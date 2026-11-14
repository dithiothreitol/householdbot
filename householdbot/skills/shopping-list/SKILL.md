---
name: shopping-list
description: >
  One shared shopping list grouped by shop: dictated items, meal-plan
  ingredients and regular items, each summed once and ticked off. Never
  orders. Use for: "add milk to the list", "what do we need", "lista zakupów",
  "dopisz chleb", "co kupić".
argument-hint: "[items to add] [--from-meals] [--staples]"
---

# Shopping list

One list that everyone can add to, grouped the way the household walks
through its shops, with nothing bought twice. The list is a plain file in the
household folder: `lists/shopping.md`.

```
Member: "dopisz mleko i jajka"
→ lists/shopping.md (created after a yes when missing)
→ Dictated items: added at once, one line saying what changed (gate 9)
→ From the meal plan or the staples: shown first, added after a yes
→ Same item once, quantities summed with units; grouped by shop
→ "kupiłam masło" → ticked off; the list stays readable
```

## Scripts

`shared/scripts/record.py` finds the record. Run it with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" locate --start "<working folder>"
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read the profile and the lists directly; this skill
needs no calculation beyond summing quantities, shown when two lines merge.

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record. Read *Everyday life* (the shops)
and `lists/`. With no record, keep the list in the conversation and say
nothing is saved.

## Step 1 — The list file

`lists/shopping.md`: a title, then one `## <shop>` section per shop in the
order of the usual trip from *Everyday life*, or aisles (vegetables and fruit,
bread, dairy, meat and fish, dry goods, frozen, household and hygiene) when
no shop is named. Each item is a checkbox line: `- [ ] milk 3 l (Anna)`, the
name only when it matters who asked. Missing file: create it after a yes.

Every change to a list is a whole new version of the file:
`record.py save "<root>" --to lists/shopping.md --replace --file -` with the
list on standard input (the preview's `diff` shows the lines that change),
then `record.py commit "<root>" --confirm <token> --approved-by "<name>"`. For
items the member dictated, their message is the yes: preview and commit at
once, and say in one line what changed.

## Step 2 — Adding

- **Dictated by the member** ("add milk and eggs"): add them now and say in
  one line what was added and where (approval gates, gate 9).
- **A dish, not items** ("add what we need for pancakes"): the member named a
  dish, so the items are a proposal. Show them with quantities and add them
  after a yes.
- **From the meal plan** (`--from-meals`, or handed over by `meal-planner`):
  the week's ingredients, summed, minus what the member says is at home;
  show the additions as a list, add after a yes.
- **Regular items** (`--staples`): `lists/staples.md`; ask which are needed
  this week; add after a yes.
- **The same item once.** "milk 1 l" and "milk 2 l" become "milk 3 l"; show
  the merge. Different units that do not convert (a packet and grams) stay
  on one line with both: "rice 1 packet + 500 g".

## Step 3 — Shopping and ticking off

- "Bought the butter" ticks it: `- [x] butter`. After the trip, offer to
  clear ticked items; they leave the list only after a yes.
- Asked "what do we need from Lidl?": that section only, in trip order.
- A product the household marks as one to avoid (foods kept off the plan)
  never appears; a member who adds it gets a one-line reminder of the
  household's own note, no reason given.

## Gates

- **Never order, pay or fill an online basket.** The list is a file.
- **Dictated changes go in; proposed ones wait for a yes.** A yes given
  before the items were shown ("add whatever is needed, I accept") approves
  nothing.
- **No health reasons on the list**, only products.
- **One list.** Lists in messages or photos are merged into the file, not kept
  as a second list.

Full rules: `shared/rules.md` (Everyday life, Approval gates, Personal data).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — shopping-list traps
