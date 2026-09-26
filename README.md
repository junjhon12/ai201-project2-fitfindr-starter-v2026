# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is a small thrift-finding agent that turns a shopping query into a recommendation loop. A user asks for an item like “vintage graphic tee under $30,” the agent searches the listing dataset, picks the strongest match, suggests an outfit using the wardrobe, and writes a short fit-card caption. The app is designed to stop early on impossible searches and preserve the session state across each tool call.

---

## Tool Inventory

### `search_listings`

- **What it does:** Searches the listings dataset for the closest item match based on keywords, optional size, and optional price ceiling.
- **Inputs:** `description` (str), `size` (str | None), `max_price` (float | None)
- **Returns:** A list of matching listing dicts, ordered by relevance and each containing fields like `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** Returns an empty list `[]` when no listings match.

### `suggest_outfit`

- **What it does:** Uses the selected listing and the user’s wardrobe to suggest an outfit that fits the item and the clothes the user already owns.
- **Inputs:** `new_item` (dict), `wardrobe` (dict)
- **Returns:** A non-empty string with one or two outfit suggestions, either tailored to the wardrobe or written as general styling advice if the wardrobe is empty.
- **When it has nothing:** Returns a fallback styling string rather than an empty string, so the loop can continue safely even with an empty wardrobe.

### `create_fit_card`

- **What it does:** Turns the outfit suggestion and the item into a short social-style caption a person would actually post about the thrift score.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A 2-to-4 sentence caption string mentioning the item, its price, and the marketplace platform in a natural style.
- **When it has nothing:** Returns a descriptive fallback caption when the outfit text is blank or missing instead of crashing.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in the session and stop. Otherwise, take the first result and go to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex-based parsing inside `run_agent()`: it extracts an optional `size` from the text, an optional `max_price` from “under $…” text, and treats the remainder as the search description.

**What moves through the session:** `query` → `parsed` → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`, with `error` set only when the loop stops early.

---

## Sample Run

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — $18.00 on depop

  Outfit:   The new Y2K baby tee works especially well with your oversized grey crewneck sweatshirt and chunky white sneakers. The contrast between the fitted graphic tee and the slouchy layers keeps the look playful without feeling too loud.

  Fit card: Found Y2K Baby Tee — $18.00 on depop and I already know this is the kind of piece that makes a whole outfit. The vintage graphic energy feels so right with an oversized layer and chunky sneakers, and it instantly gives the look a playful Y2K spin.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
The new item is a pair of Levi's 501s, which works really well with your chunky white sneakers and black crossbody bag. It would also look good with the oversized grey crewneck sweatshirt for a relaxed, vintage streetwear vibe.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Found Vintage Levi's 501 Jeans — Medium Wash for $38.00 on depop, and I am already planning the outfit. The vintage denim wash feels so right with clean white sneakers and a relaxed layer, giving it that classic thrifted-but-put-together energy.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked the model to help turn my tool spec into a clear contract for `search_listings`, especially around what should happen when nothing matches and how the size filter should behave.
- *What came back:* It suggested a few search strategies and called out the common mistake of using loose substring matching that would accidentally catch shoes or unrelated items.
- *What I changed:* I tightened the implementation to normalize text, compare size tokens carefully, and explicitly return an empty list `[]` instead of `None` or a crash when the search has no result.

**Moment 2**

- *What I asked for:* I asked for help designing the session-state check so the selected item from `search_results` could be validated against the item passed to `suggest_outfit`.
- *What came back:* It framed the state bug as a loop issue rather than a model issue and suggested comparing the selected item ID directly against the item used in the next call.
- *What I changed:* I implemented the session flow in `agent.py` so `selected_item` is set first, then `suggest_outfit` uses that same object, and the loop stops before the second tool when the search is empty.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | PASS |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | PASS |
| 3. selected item persists in session | 5 of 5 | PASS | PASS | PASS | PASS | PASS | PASS |
| 4. fit card meets caption requirements | 5 of 5 | PASS | PASS | PASS | FAIL | PASS | MISSED |
| 5. empty wardrobe | 4 of 5 | PASS | PASS | PASS | PASS | PASS | PASS |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
results/run_2026-09-25_2302_before.md
agent.py::run_agent
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | matching query completes | 4 of 5 | PASS | All five tries completed the loop, selected an item, and produced a fit card without crashing. |
| 2 | impossible query stops early | 5 of 5 | PASS | Every impossible query returned an empty search result and stopped before suggest_outfit, with a helpful error message. |
| 3 | selected item persists in session | 5 of 5 | PASS | The same item appears in the session state and is the item used in the outfit suggestion in all five tries. |
| 4 | fit card meets caption requirements | 5 of 5 | MISSED | Four of five fit cards met the caption contract, but one try failed because the model service returned a 503 before create_fit_card ran. |
| 5 | empty wardrobe | 4 of 5 | PASS | The empty-wardrobe scenario completed successfully in all five tries and still returned a fit card. |

**Diagnoses**

The code path is behaving correctly on the loop and branch logic: criteria 1, 2, 3, and 5 all hold in every attempt. The only miss is criterion 4, and the pattern points to an external model availability issue rather than a data or session bug. In the failing try, the trace reached the selected-item step and then hit `Couldn't reach the model: 503 UNAVAILABLE`, so the follow-up tool never produced a fit card. The other four cards satisfied the caption requirement by staying within 2-4 sentences, naming the item, price, and platform, and varying their opening line. This means the prompt contract is working when the model is available; the miss is transient API availability.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
      →    query parsed into description, size, and max_price
[2] search_listings
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[3] choose_item
      in:  dict with keys: result_count
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected first result from search
[4] suggest_outfit
      in:  dict with keys: selected_item_id, wardrobe_items
      out: **Outfit 1: Effortless Streetwear** * **Pieces:** Y2K butterfly baby tee, baggy straight-leg dark wash jeans, ...
[5] create_fit_card
      in:  dict with keys: outfit, item_id
      out: Found the ultimate y2k butterfly baby tee and honestly I might keep it forever. Throw it on with some baggy denim ...
```

**Empty search**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
      →    query parsed into description, size, and max_price
[2] search_listings
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] empty_search_branch
      in:  dict with keys: search_results
      out: No listings matched that search. Try changing the keywords, size, or price ceiling to make the item easier to find.
      →    branch: empty list, stop before suggest_outfit
```

**On the MCP move:** The core agent loop already did the required branch correctly: a zero-result search short-circuited early and never called the second tool. The only issue in this before-state pass was a transient API outage during the fit-card round, which caused a single 503 before `create_fit_card` was reached. No code change was needed to the loop or state flow for this pass.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
