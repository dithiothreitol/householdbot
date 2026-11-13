---
name: life-event
description: >
  A big change step by step: moving, a birth, buying or selling a car, a new
  job, a death; every statutory deadline counted from the day it happened. Use
  for: "we're moving", "we had a baby", "I bought a car", "przeprowadzka",
  "kupiłem auto", "zmarł tata", "zmieniam pracę".
argument-hint: "[event] [--date YYYY-MM-DD]"
---

# Life event

A big change brings a dozen deadlines at once, each from a different office.
This chain reads the event's checklist from the country pack, counts every
date from the day it happened, and lets the household take it one step at a
time.

```
Member: "kupiłem używane auto od sąsiada 10 listopada"
→ Which event, which day, whom it concerns (asked, not guessed)
→ dates.py event: every statutory step with its date, weekday and law
→ Steps that do not apply are dropped with the member
→ The chosen ones become reminders (one batch, shown first, yes, written)
→ Hand-offs: the profile, documents, letters, policies, contracts
```

## Scripts

`shared/scripts/dates.py` counts the event's windows; `record.py` writes the
reminders. Run them with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/dates.py" events --country PL --lang pl
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/dates.py" event --country PL --id vehicle-purchase --from <the day it happened> --lang pl
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read the event in `shared/locale/<CC>.md` and
`<CC>.json`, count each window by hand with every step shown, the weekday
counted from today's date, tagged `model calculation — verify`.

The country pack is in this skill's folder:
`${CLAUDE_SKILL_DIR}/shared/locale/<CC>.md` (rules, windows, checklists) and
`<CC>.json` (the data `dates.py` reads), where `<CC>` is the profile's
Country, for example `PL`. Open it with the Read tool: it needs no shell and
no search, so read it on the no-Python path too. The section "Life events"
and the JSON `life_events` hold the checklists; the ids are listed by
`dates.py events`.

Dates come out in the household's language: `record.py` reads it from the
profile, and `dates.py` takes `--lang pl` for Polish.

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record. With no record, the dates are
still counted and nothing is saved.

## Step 1 — The event

Ask what happened, on which day, and whom it concerns, in one message. A
planned event (a move next month) uses the planned day and says the dates
move with it. An event the pack has no checklist for (a wedding, a divorce, a
retirement, a child starting school): say so, offer to build a checklist with
the member from what they know and from the household's documents, and mark
every date in it as the member's, not the law's.

Death of someone close: the answer's first sentence is one plain sentence of
sympathy in the household's language ("Bardzo mi przykro z powodu śmierci
Twojego taty."), with nothing before it, no remark about language or tools.
Then the next two or three steps only, and the offer to continue later. The
not-advice line comes before anything about inheritance.

## Step 2 — The dates

`dates.py event --id <event> --from <day>`: each `step` has its due date,
`do_by`, weekday, what meets it and the law; each `task` has no statutory
date. Show one table, earliest first: what, by when (weekday), how it is done
(the pack's channel), the law, tagged `country pack rule — verify`. Steps
already done are asked about and dropped.

Ask the questions that change the list (bought from a dealer or a person?
the car registered in Poland already? the child born abroad?) and drop the
steps that do not apply, saying why.

## Step 3 — Reminders

The chosen steps as obligations: title, kind (`filing`, `payment`, `task`),
`due_date` and `do_by` from the script, `law`, provenance `country pack rule —
verify`. Each `record.py add --dry-run`; show the whole batch; the member may
remove items; write after a yes with `--approved-by` (approval gates, gates 4
and 5). Tasks without a date are written only if the member gives one.

When something ends (a car sold, a home left, a person who died), the first
answer also names what in the record ends with it: the open entries about it
(by `subject` or `counterparty` in `registers/obligations.json`, such as the
car's OC renewal and its roadworthiness test) to close, and the profile line
to change. Both are proposals in the same answer, written after a yes
(closing with `record.py complete --status cancelled --no-next`; the profile
through `household-customize`).

## Step 4 — Hand-offs

- The profile changes (a new member, an address, a vehicle bought or sold, a
  member who died): `household-customize`.
- Papers from the event (a sales contract, a birth certificate, a death
  certificate): `file-document`.
- Letters to offices and companies: `reply-to-letter`; contracts at the old
  address or of the person who died: `cancel-or-switch`.
- A new car: `vehicle-file`; policies: `insurance-overview`; documents for a
  newborn or after a move: `identity-and-travel`; final bills: `bills-due`.

Each hand-off keeps its own approval (chain seams).

## Gates

- **One step at a time, each with its own yes.**
- **Every date from the script or tagged**, with its law and "verify".
- **Never contact an office, sign or pay.** The plugin prepares; the member
  goes, signs and pays.
- **No legal advice.** Inheritance, tax and benefit choices get the not-advice
  line and the professional to ask.
- **Gentle with loss.** No platitudes, no long lists, the member sets the pace.

Full rules: `shared/rules.md` (Chain seams, Dates and deadlines, Not advice,
Approval gates).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — life-event traps
