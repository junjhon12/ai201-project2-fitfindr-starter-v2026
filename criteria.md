# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. Something about state

When the search succeeds, the item in `session["selected_item"]["id"]` is the same one passed into `suggest_outfit`, and this remains true in 5 of 5 tries.

**Why this target:**
I picked 5 of 5 here because the branch logic is the thing being tested, and the session is the single source of truth. The state bug is easy to miss because the model can still produce a believable outfit even when the wrong item reached the next tool, so the session comparison is the countable proof that the loop passed the right object through.



---

## 4. Something about the fit card

For 5 different matching items, each fit card is 2 to 4 sentences long, mentions the item title, price, and platform at least once, and is different enough from the others that the opening sentence is not the same in all 5 tries.

**Why this target:**
I am not expecting perfect model creativity, only that the card behaves like a real caption. Requiring a price and platform keeps it from becoming a template, while allowing a little variation acknowledges that model output is naturally non-deterministic.



---

## 5. Your choice

When the wardrobe is empty, the agent still completes the run and returns a fit card in at least 4 of 5 tries without crashing or leaving the session in an error state.

**Why this target:**
This matters because a new user with no saved wardrobe is a normal early-user state, and the rubric explicitly calls out the empty-wardrobe failure mode. I chose 4 of 5 instead of 5 of 5 because the model still has to invent general styling advice that fits the item, so a perfect score is stricter than the branch logic itself.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
