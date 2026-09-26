"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — used for SEARCH_RESULT_LIMIT
from generate import generate
from utils.data_loader import load_listings


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _tokenize(value: str | None) -> set[str]:
    text = _normalize_text(value)
    return {token for token in text.split() if token}


def _size_matches(listing_size: str | None, requested_size: str | None) -> bool:
    if not requested_size:
        return True
    if not listing_size:
        return False

    requested_tokens = _tokenize(requested_size)
    listing_tokens = _tokenize(listing_size)

    if not requested_tokens:
        return True

    if requested_tokens & listing_tokens:
        return True

    requested_numeric = {t for t in requested_tokens if t.isdigit()}
    listing_numeric = {t for t in listing_tokens if t.isdigit()}
    if requested_numeric and requested_numeric & listing_numeric:
        return True

    requested_letters = {t for t in requested_tokens if t.isalpha()}
    listing_letters = {t for t in listing_tokens if t.isalpha()}
    if requested_letters and requested_letters & listing_letters:
        return True

    requested_full = _normalize_text(requested_size)
    listing_full = _normalize_text(listing_size)
    if requested_full in listing_full or listing_full in requested_full:
        return True

    return False


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first. Returns an empty
        list when nothing matches.
    """
    description_tokens = _tokenize(description)
    if not description_tokens:
        return []

    matches: list[tuple[int, dict]] = []
    for listing in load_listings():
        if max_price is not None and float(listing.get("price", 0.0)) > float(max_price):
            continue
        if size is not None and not _size_matches(listing.get("size"), size):
            continue

        combined_text = " ".join(
            [
                listing.get("title", ""),
                listing.get("description", ""),
                " ".join(listing.get("style_tags", []) or []),
                listing.get("category", ""),
                listing.get("brand") or "",
            ]
        )
        score = 0
        for token in description_tokens:
            if token in _tokenize(combined_text):
                score += 1
        if score == 0:
            continue
        matches.append((score, listing))

    matches.sort(key=lambda item: (-item[0], float(item[1].get("price", 0.0))))
    return [listing for _, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.
    """
    wardrobe_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []
    item_name = new_item.get("title") or "this thrifted find"
    item_category = new_item.get("category") or "piece"
    item_price = new_item.get("price")
    item_platform = new_item.get("platform") or "the marketplace"

    if not wardrobe_items:
        prompt = (
            f"I found {item_name} for ${item_price} on {item_platform}. "
            f"Give me 2 outfit ideas for styling this {item_category}. "
            "Keep the advice practical, concise, and wearable for everyday life."
        )
        system = (
            "You are a helpful vintage fashion stylist. Suggest outfits using "
            "common wardrobe staples and describe how to wear the item in a way "
            "that feels realistic and flattering."
        )
        return generate(prompt, system=system).strip() or (
            f"Style {item_name} with a relaxed denim layer, simple basics, and a pair of "
            "clean sneakers or boots for an easy everyday outfit."
        )

    wardrobe_summary = "; ".join(
        f"{item.get('name', 'item')} ({item.get('category', 'piece')})"
        for item in wardrobe_items[:10]
    )
    prompt = (
        f"New item: {item_name} ({item_category}) — ${item_price} on {item_platform}. "
        f"User wardrobe: {wardrobe_summary}. "
        "Suggest exactly 2 outfit combinations that use pieces from the wardrobe "
        "and explain which existing items pair best with the new item."
    )
    system = (
        "You are a fashion stylist. Respond with concise outfit ideas that name "
        "specific wardrobe pieces and how they work together."
    )
    return generate(prompt, system=system).strip() or (
        f"Pair {item_name} with the most versatile pieces in the wardrobe for a clean "
        "look that balances texture and silhouette."
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.
    """
    outfit_text = (outfit or "").strip()
    if not outfit_text:
        return (
            f"Found {new_item.get('title', 'this piece')} for ${new_item.get('price', 0)} on "
            f"{new_item.get('platform', 'the marketplace')} and I already know it is going to be a good one."
        )

    item_title = new_item.get("title") or "this piece"
    item_price = new_item.get("price")
    item_platform = new_item.get("platform") or "the marketplace"
    item_tags = ", ".join(new_item.get("style_tags", [])[:3]) or "vintage"

    prompt = (
        f"Write a 2-to-4 sentence social caption about this thrift find: "
        f"{item_title}, priced at ${item_price}, sold on {item_platform}. "
        f"The suggested outfit is: {outfit_text}. "
        f"Make it sound like a real thrift post, not a product listing. "
        f"Mention the vibe as '{item_tags}' and keep it punchy, specific, and easy to read."
    )
    system = (
        "You write short, authentic social captions for thrift finds. Keep it to 2-4 sentences, "
        "include price and platform once each, and sound like a person sharing a great score."
    )
    return generate(prompt, system=system).strip() or (
        f"Found {item_title} for ${item_price} on {item_platform} and I am already imagining the outfit: "
        f"{outfit_text}. This is exactly the kind of vintage score I wanted."
    )
