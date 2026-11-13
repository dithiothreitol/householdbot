# Everyday life — meals, shopping, chores and the family calendar

The everyday skills plan and keep lists; the household cooks, shops, cleans
and drives. They follow the same gates as the rest of the plugin, with the
lighter rule for dictated list changes (approval gates, gate 9).

---

## Where things live

| What | File |
|---|---|
| Preferences, budget, shops, who takes part | `household-profile.md`, section *Everyday life* |
| Chores, shares and saved chore plans | `registers/chores.json` (written by `chores.py`) |
| The shopping list | `lists/shopping.md`, one section per shop or aisle |
| Regular items bought most weeks | `lists/staples.md` |
| The week's meals | `lists/meals-<YYYY>-W<NN>.md` |

A missing file is created after a yes, from the household's answers, never
filled with invented preferences.

## Meals

- The plan follows the profile: who eats at home on which days, the time to
  cook on weekdays, the weekly budget, likes and dislikes, and the foods to
  keep off the plan (personal-data rule: never why).
- It is not nutrition or medical advice. With an allergy in the household,
  say once that labels are read for every product, because recipes and
  products change.
- Leftovers and what is already at home come first; nothing is wasted on
  purpose. No brands unless the household names them.

## Shopping

- One list, grouped by the household's shops, or by aisle when no shop is
  named. Quantities with units, the same item summed once ("milk 3 l", not
  three lines), and who asked for it when that matters.
- Nothing is ordered, paid for or added to an online basket. A shop's app is
  the member's to use.

## Chores

- The plan comes from `chores.py`: the same register and dates always give
  the same plan, and each person's load divided by their share stays as even
  as the chores allow. Report it in numbers; no blame, no rankings.
- A chore has a minimum age, so a child gets only what fits their age. A
  child's share is smaller by default (0.5) until the household changes it.
- Swaps between people are fine when both agree; record the result, not the
  argument.

## The family calendar

- Reading the household's calendars needs no approval; writing to them does
  (approval gates, gate 10).
- Collisions are stated as facts: two events at once, two places too far apart
  in the time between them, a child to drive with no adult free.
- Birthdays and name days come from the profile, as the household gave them
  (day and month; personal-data rule: no full dates of birth).
