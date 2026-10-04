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

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. matching query completes | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. impossible query stops early | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. selected item persists in session | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. fit card meets caption requirements | 5 of 5 | FAIL | FAIL | FAIL | PASS | FAIL | MISSED (1/5) |
| 5. empty wardrobe | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Run details:** `python run_eval.py --label before`; 9 scenarios ran five
times apiece, with caching off and temperature 0.9 (80 model calls). Criterion 4 uses five
different matched items. For each Try column, I checked the corresponding
attempt for all five items as one batch; a batch passes only if all five cards
meet the sentence, item-name, price, and platform requirements and all five
opening sentences differ. This also repeats each item five times to check
variation. The generated run log is
[`results/run_2026-10-04_0425_before.md`](results/run_2026-10-04_0425_before.md),
produced by `run_eval.py::write_report` from records captured by
`run_eval.py::run_once` and `agent.py::run_agent`.

### Criterion 1 — matching query completes

Source: [`results/run_2026-10-04_0425_before.md`](results/run_2026-10-04_0425_before.md),
`agent.py::run_agent`, matching-query Try 1:

```
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
search_results: 10

Fit card:
Found the ultimate Y2K baby tee with the cutest butterfly print, and I am obsessed. Style it baggy with dark denim and combat boots for that effortless grunge look, or tuck it into wide-leg khakis with fresh sneakers. Grab this vintage graphic tee on Depop right now for just $18!
```

### Criterion 2 — impossible query stops early

Source: [`results/run_2026-10-04_0425_before.md`](results/run_2026-10-04_0425_before.md),
`agent.py::run_agent`, impossible-query Try 1:

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
      →    query parsed into description, size, and max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] empty_search_branch
      in:  dict with keys: search_results
      out: No listings matched that search. Try changing the keywords, size, or price ceiling to make the item easier to …
      →    branch: empty list, stop before suggest_outfit
```

### Criterion 3 — selected item persists in session

The evaluation report records the selected track jacket in the returned
session. I also instrumented `suggest_outfit` in memory (leaving search and
`agent.py::run_agent` unchanged) to print both IDs on five additional
state-only checks:

```
Try 1: session selected_item.id=lst_004; suggest_outfit new_item.id=lst_004; PASS
Try 2: session selected_item.id=lst_004; suggest_outfit new_item.id=lst_004; PASS
Try 3: session selected_item.id=lst_004; suggest_outfit new_item.id=lst_004; PASS
Try 4: session selected_item.id=lst_004; suggest_outfit new_item.id=lst_004; PASS
Try 5: session selected_item.id=lst_004; suggest_outfit new_item.id=lst_004; PASS
```

The five model-backed evaluation runs are in
[`results/run_2026-10-04_0425_before.md`](results/run_2026-10-04_0425_before.md),
under `agent.py::run_agent`, “selected item persists in session.”

### Criterion 4 — fit card meets caption requirements

Source for all five outputs: [`results/run_2026-10-04_0425_before.md`](results/run_2026-10-04_0425_before.md),
`agent.py::run_agent`, Try 4 across the five criterion-4 scenarios. This was
the one batch in which all five cards passed; their opening sentences differ.

```
90s Silk Slip Dress — Floral, Midi Length ($30.0, depop)
Just scored the ultimate 90s floral silk slip dress and I'm obsessed with this vintage vibe. Throw an oversized grey crewneck and combat boots over it for a grunge look, or style it with a cropped zip hoodie and chunky sneakers for pure 90s street style. Grab this dreamy piece now on Depop for just $30 before I keep it for myself!

Platform Mary Janes — Black Patent ($55.0, depop)
Obsessed with these glossy black platform Mary Janes—such a good y2k, goth, platform score. Style them with baggy denim and a cropped zip hoodie for a street look, or lean into prep-punk contrast with khaki trousers and a vintage jacket. Grab them on Depop for $55 before I change my mind and keep them.

Corduroy Wide-Leg Pants — Rust ($32.0, depop)
Nothing beats finding the ultimate pair of 70s-vibed corduroy pants while sifting through the racks. This vintage rust pair gives off major cottagecore energy and looks so good styled with an oversized grey sweatshirt or a cropped hoodie. Grab them on Depop for just $32.0 before someone else snags your new go-to fall bottoms!

Leather Belt — Brown, Braided ($12.0, thredUp)
Found this gorgeous brown braided leather belt on thredUp for just $12.00, and it’s giving major vintage, western, classic vibes. It adds the absolute best texture whether I'm styling it with baggy jeans or wide-leg khakis. Such an easy little detail that pulls every look together!

Vintage Windbreaker — Color Block Purple/Teal ($40.0, thredUp)
I am obsessed with the purple and teal color-blocking on this vintage windbreaker—total '90s athletic energy. I threw it on with baggy denim and chunky sneakers for the ultimate retro streetwear vibe. Snagged this gem on thredUp for just $40!
```

### Criterion 5 — empty wardrobe

Source: [`results/run_2026-10-04_0425_before.md`](results/run_2026-10-04_0425_before.md),
`agent.py::run_agent`, empty-wardrobe Try 1:

```
selected_item: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
stopped early: no

Fit card:
The ultimate transitional piece has officially entered the chat! This cropped light wash denim jacket adds instant vintage charm and looks so good thrown over a slip dress or paired with stripes. Grab it over on my Poshmark closet for just $42.00.

Vibe: denim, vintage, classic.
```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | matching query completes | 4 of 5 | MET (5/5) | Every try selected a listing and completed both later tools with a non-empty fit card. |
| 2 | impossible query stops early | 5 of 5 | MET (5/5) | Every try returned no search results, a message about changing the query, and no outfit/card step. |
| 3 | selected item persists in session | 5 of 5 | MET (5/5) | The five evaluation runs completed; a separate five-run state probe recorded matching `lst_004` IDs in session and the outfit-tool argument. |
| 4 | fit card meets caption requirements | 5 of 5 | MISSED (1/5) | Only batch 4 of 5 passed across the five distinct items. Sentence counts and opening variation passed, but some cards in the other batches missed an item-identifying phrase or the item's price. |
| 5 | empty wardrobe | 4 of 5 | MET (5/5) | Each empty-wardrobe run completed without error and returned a fit card. |

**Diagnoses**

The loop, empty-search branch, state handoff, and empty-wardrobe path all met
their targets. The only miss was in model-generated fit-card content, not
availability: all 45 agent runs completed or took the expected empty-search
branch, with no crashes. Across criterion 4, every caption had 2–4 sentences,
the platform was named, and the five openings differed in every batch.
However, at least one caption in four of the five batches omitted either a
clear item-identifying phrase or the matching numeric price. The
`create_fit_card` prompt in `tools.py` supplies the title and price, but it
asks for a punchy post “not a product listing” and does not explicitly require
the item title in the system instruction. The model sometimes prioritizes
that style direction and leaves out identifying words or the price; this is
an output-contract weakness, not a search or loop failure.

---

## Milestone 2 Failure Runs

**Empty search** — `python app.py ask 'nonexistent moon colony artifact' --trace`

```
No listings matched that search. Try changing the keywords, size, or price ceiling to make the item easier to find.
```

**Empty wardrobe** — `python app.py ask 'vintage graphic tee under $30' --empty-wardrobe`

The agent completed instead of crashing or returning blank advice:

```
What a fun find! At $18, that butterfly baby tee is peak 2000s nostalgia. Since the top is fitted and cropped, the key to making it look modern and wearable for everyday life is balancing proportions and keeping the rest of the outfit grounded.

Here are two easy, practical ways to style it using common wardrobe staples:
```

The response continued with two practical outfit ideas and ended: “Stylist Tip: Don't stress about over-accessorizing. Let the butterfly print be the star of the show by keeping your other pieces solid-colored and classic!” The run also returned a non-empty fit-card caption.

**Model unavailable** — changed one character of the `.env` key for a fresh query with the cache disabled; the original `.env` was restored afterward.

```
The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.
```

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

Command: `python app.py ask 'vintage graphic tee under $30' --trace`

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
      →    query parsed into description, size, and max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[3] choose_item
      in:  dict with keys: result_count
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    selected first result from search
[4] suggest_outfit
      in:  dict with keys: selected_item_id, wardrobe_items
      out: **Outfit 1: Effortless Streetwear** *   **Pieces:** Y2K butterfly baby tee, baggy straight-leg dark wash jeans…
[5] create_fit_card
      in:  dict with keys: outfit, item_id
      out: Found the ultimate y2k butterfly baby tee and I am never taking it off. It’s giving major vintage graphic tee …
```

**Empty search**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
      →    query parsed into description, size, and max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] empty_search_branch
      in:  dict with keys: search_results
      out: No listings matched that search. Try changing the keywords, size, or price ceiling to make the item easier to find.
      →    branch: empty list, stop before suggest_outfit
```

**On the MCP move:** `mcp_server.py::search_listings` now registers the existing search implementation with typed `description`, `size`, and `max_price` inputs. `agent.py::run_agent` calls it through `mcp_client.call_tool`; the MCP client unwraps the result back into a list of listing dictionaries, so the existing empty-search branch and the rest of the loop keep the same result shape. `python mcp_client.py` lists the registered tool, and a direct-vs-MCP comparison returned equal lists. A traced `vintage graphic tee under $30` query completed with Y2K Baby Tee selected, and the impossible-search query still stopped before `suggest_outfit`. The loop trace labels the MCP call `search_listings (via MCP)`.

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
