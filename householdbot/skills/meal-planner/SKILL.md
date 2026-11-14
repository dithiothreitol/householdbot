---
name: meal-planner
description: >
  A week of meals from the household's preferences, time, budget and foods to
  keep off, leftovers first; saved after a yes, ingredients handed to the
  shopping list. Use for: "plan our meals", "what's for dinner", "jadłospis",
  "co ugotować", "plan obiadów".
argument-hint: "[--week next|this] [--days N]"
---

# Meal planner

A weekly plan saves the evening question "what do we eat today" and a second
trip to the shop. This skill plans from what the household told it, keeps the
foods it must avoid off the plan, and turns the plan into one shopping list.

```
Member: "zaplanuj obiady na przyszły tydzień"
→ Profile, Everyday life: who eats when, time, budget, likes, foods to keep off
→ What is at home already? (asked; leftovers first)
→ A plan: one line per meal, with time and a rough cost
→ Changes until the household is happy → yes → lists/meals-<YYYY>-W<NN>.md
→ Ingredients minus what is at home → shopping-list (its own yes)
```

## Scripts

`shared/scripts/record.py` finds the record and the household's language;
`dates.py` gives the dates of the week. Run them with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/dates.py" info <the Monday> --lang <lang>
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, count the days of the week from today's date and
weekday, and add up the rough cost by hand with the addition shown.

Dates come out in the household's language: `record.py` reads it from the
profile, and `dates.py` takes `--lang pl` for Polish.

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record. Read *Everyday life*.

## Step 1 — What the plan must respect

From *Everyday life*: which meals at home on which days, the time to cook on
weekdays, the weekly food budget, likes and dislikes per person, the shops,
and the foods to keep off the plan. When the section is empty, ask the five
questions in one message (meals, time, budget, dislikes, anything to keep
off) and offer to store the answers through `household-customize`.

Foods to keep off the plan are health data (personal-data rule). Use them to
leave a food out; never write who or why in the plan, the list or the answer
("no peanuts", nothing more). With such a food in the household, say once that
labels are read for every product, with no reason added.

## Step 2 — What is at home

Do not hold the plan back for it. Plan from the profile in this answer, and in
the same message ask what is in the fridge, the cupboard and left over from
last week, offering to swap dishes to use it. Read `lists/staples.md` for
what the household buys anyway.

## Step 3 — The plan

One table: day with weekday, meal, the dish, minutes to cook, a rough cost.
Weekdays within the stated time; longer cooking at weekends; a soup or a dish
that lasts two days where the household likes it; the likes and dislikes of
each person respected without comment and without naming whose they are. The
total rough cost against the budget, with the
addition shown and tagged as an estimate. Offer swaps ("Tuesday: another
dish?") and change only what the member asks.

Not nutrition or medical advice: no calorie counts or diets unless the
household asks, and then only as information with the not-advice line.

## Step 4 — Save, then shop

Before asking, preview `lists/meals-<YYYY>-W<NN>.md` (the week's dates, the
table, the dishes' ingredient lists with quantities) with `record.py save
"<root>" --to lists/meals-<YYYY>-W<NN>.md --file -`; after the yes, commit it. Then build the ingredients for
the whole week, summed (two dishes needing onions give one line), minus what
is at home and on the staples list already bought, and hand them to
`shopping-list`, which shows them and adds them after its own yes.

## Gates

- **The household's food, the household's rules.** Nothing is kept off or
  added because the plugin thinks it healthier.
- **Health data stays out** of the plan file, the list, the calendar and any
  brief: foods only, never who or why.
- **No names in the plan's notes.** Foods left out are named as foods ("no
  mushrooms, no peanuts"), never with a person or a reason; likes and
  dislikes are applied without saying which dish is for whom ("two soups for
  Piotr").
- **Show, then wait, then write** the plan; the shopping list has its own yes.
- **A yes before the plan is shown approves nothing.** "Zapisz od razu",
  "akceptuję z góry" or "just save it" before the member has seen the plan:
  show the plan and ask; write the file and touch the list only after the yes
  that follows.
- **Nothing is ordered or paid.** No shop baskets, no delivery orders.

Full rules: `shared/rules.md` (Everyday life, Personal data, Not advice).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — meal-planning traps
