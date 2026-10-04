"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from mcp_client import call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    session = new_session(query, wardrobe)
    trace.start_trace()

    for count in range(1, config.MAX_ITERATIONS + 2):
        trace.check_iterations(count)

        parsed = {"description": query, "size": None, "max_price": None}

        price_match = re.search(r"under\s*\$?\s*(\d+(?:\.\d+)?)", query, flags=re.I)
        if price_match:
            parsed["max_price"] = float(price_match.group(1))

        size_match = re.search(r"\bsize\s+([A-Za-z0-9/\s-]+?)(?=\s*(?:under|$))", query, flags=re.I)
        if size_match:
            parsed["size"] = size_match.group(1).strip()

        description = query
        if parsed["max_price"] is not None:
            description = re.sub(r"\s*under\s*\$?\s*\d+(?:\.\d+)?", "", description, flags=re.I)
        if parsed["size"]:
            description = re.sub(r"\s*size\s*" + re.escape(parsed["size"]), "", description, flags=re.I)
        description = " ".join(description.split())
        parsed["description"] = description or query.strip()
        session["parsed"] = parsed

        trace.step(
            "parse_query",
            inputs={"query": query},
            returned=parsed,
            note="query parsed into description, size, and max_price",
        )

        results = call_tool(
            "search_listings",
            {
                "description": parsed["description"],
                "size": parsed["size"],
                "max_price": parsed["max_price"],
            },
        )
        session["search_results"] = results
        trace.step(
            "search_listings (via MCP)",
            inputs={"description": parsed["description"], "size": parsed["size"], "max_price": parsed["max_price"]},
            returned=results,
        )

        if not results:
            session["error"] = (
                "No listings matched that search. Try changing the keywords, size, or price ceiling "
                "to make the item easier to find."
            )
            trace.step(
                "empty_search_branch",
                inputs={"search_results": results},
                returned=session["error"],
                note="branch: empty list, stop before suggest_outfit",
            )
            return session

        selected_item = results[0]
        session["selected_item"] = selected_item
        trace.step(
            "choose_item",
            inputs={"result_count": len(results)},
            returned=selected_item,
            note="selected first result from search",
        )

        try:
            outfit = suggest_outfit(selected_item, wardrobe)
        except ModelUnavailable as exc:
            session["error"] = str(exc)
            return session
        session["outfit_suggestion"] = outfit
        trace.step(
            "suggest_outfit",
            inputs={"selected_item_id": selected_item.get("id"), "wardrobe_items": len(wardrobe.get("items", []))},
            returned=outfit,
        )

        try:
            card = create_fit_card(outfit, selected_item)
        except ModelUnavailable as exc:
            session["error"] = str(exc)
            return session
        session["fit_card"] = card
        trace.step(
            "create_fit_card",
            inputs={"outfit": outfit, "item_id": selected_item.get("id")},
            returned=card,
        )
        return session

    session["error"] = "The loop exceeded the allowed number of iterations. Check the branch conditions."
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
