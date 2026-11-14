---
name: chore-rotation
description: >
  Fair chores by share and age, planned by a script, saved after an adult's
  yes, with agreed swaps and the balance. Use for: "who does what this week",
  "split the chores", "podział obowiązków", "kto dziś zmywa", "grafik
  sprzątania".
argument-hint: "[--weeks N, default 1] [--from DATE]"
---

# Chore rotation

Housework feels fairer when it is written down and counted the same way every
week. This skill keeps the household's chores in `registers/chores.json`, lets
`chores.py` assign them, and leaves every decision with the adults.

```
Member: "rozpisz obowiązki na przyszły tydzień"
→ The register: chores, who takes part, shares (chores.py validate)
→ None yet? Build it from the household's own words, then a yes
→ chores.py plan for the coming week(s): who does what, the load per person
→ Shown per person; children see their own part
→ An adult says yes → chores.py save-plan, then chores.py commit
→ Later: agreed swaps (chores.py swap) and the balance (chores.py balance)
```

## Scripts

`shared/scripts/chores.py` assigns chores and keeps the register;
`record.py` finds the record. Run them with Python 3 and today's date:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/chores.py" plan "<household folder>" --from <next Monday> --weeks 1 --today <today>
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/chores.py" save-plan "<household folder>" --from <next Monday> --weeks 1 --today <today>
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/chores.py" commit "<household folder>" --confirm <token> --approved-by "<name>"
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/chores.py" balance "<household folder>" --weeks 8 --today <today>
```

Other commands: `init`, `add --json`, `update --id --set field=value`,
`retire --id`, `person --name --share --birth-year`, `swap --week --chore
--from --to`, `validate`. Every write previews first and prints a `confirm`
token; `chores.py commit` applies it after a yes.

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read `registers/chores.json`, assign by the same rule
(the lowest load divided by share takes the next chore, the heaviest chores
first, ties to whoever did not do it last week), show the arithmetic, tag the
plan `model calculation — verify`, and edit the JSON by hand only after a yes
(household-record rule, *Without Python*).

Dates come out in the household's language: `chores.py` reads it from the
profile, like `record.py`.

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record. Read the profile's members and
*Everyday life*, then `chores.py validate`.

## Step 1 — Start or change the register

- No `registers/chores.json`: `chores.py init` previews the members.
  Adults get a share of 1, children 0.5 with their birth year. Show who takes
  part, ask whether anyone should have another share, write after a yes.
- Chores come from the household's own words, one line each: what, how many
  times a week (`per_week`), every how many weeks (`every_weeks`), effort from
  1 to 5 (1 a few minutes, 3 about an hour, 5 half a day), the minimum age,
  only certain people (`who`), always the same person (`fixed`). Ask for the
  minimum age as a question ("from what age should someone clean the
  bathroom?"); never decide it.
- Add with `chores.py add --file -` and the chore as JSON on
  standard input (a here-document ending in `HB_END`), show the whole list,
  write after a yes. Change with `update`, stop planning with `retire` (the
  history stays).

## Step 2 — Plan

`chores.py plan --from <the Monday of the week> --weeks N`. Read before
showing:

- `unassigned`: a chore nobody may do (age or `who`); say why and ask.
- `carried_over`: who did more in the saved weeks; they get less now, and say
  so in one line.
- `normalized_load` and `spread`: the load divided by the share.

Show it per person, chores with how many times, then the week's points. One
line on fairness in numbers ("everyone within 1 point of their share"). No
rankings, no blame words, no "lazy" or "always".

## Step 3 — Save, after a yes

An adult says yes: `chores.py commit "<root>" --confirm <token> --approved-by
"<name>"` for the `save-plan` preview. Offer to
add the plan to the family calendar through `family-calendar` (one weekly
note, not an event per chore) and to print it as a list in `lists/`.

A swap both people agreed to: `chores.py swap --week <week> --chore <id>
--from <name> --to <name>`, then its commit with the adult's name after a yes.
The balance stays true only when swaps are recorded.

## Step 4 — How it went

`chores.py balance --weeks 8`: points per person, divided by share, and the
weeks it covers. Weeks with no saved plan are missing, not zero.

## Children

Minors see their own part and may ask for a swap; adults approve. A chore with
a minimum age above a child's age never reaches them.

When a child writes (they say who they are, or the profile marks them a
child), answer the child: by name, in short, kind sentences and a child's
words. No script names, options, week numbers, rule quotes or notes about the
shell. Say what happens next in their terms: a swap needs the other person to
agree (for a swap with Dad, Dad says yes) and an adult to approve it before it
is saved; offer to prepare it so that an adult can say yes ("I can get the
swap ready now; when Dad says yes, it goes in"). When this week's
plan is not saved yet, say so simply ("this week's plan isn't written down
yet; once Mum or Dad approves it, the swap goes in"). Never a scolding, never
"you have to". The tone is encouraging: what is done, what is next.

## Gates

- **The script assigns.** No reshuffling by hand to please someone; change the
  register (share, `who`, `fixed`) and plan again.
- **An adult's yes** before any commit, with `--approved-by`; children do not
  approve.
- **Numbers, not judgements.** No rankings, no blame.
- **Absent is not zero.** Unsaved weeks are reported as missing.

Full rules: `shared/rules.md` (Everyday life, Approval gates, Absent is not
zero).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — chore-rota traps
