---
name: tax-season-organizer
description: >
  Gets the household ready for the annual income tax return without filing it:
  forms to collect, reliefs as questions, deadlines (Poland: PIT, Twój e-PIT).
  Use for: "help with our tax return", "PIT", "rozliczenie roczne", "jakie
  dokumenty do PIT", "ulgi".
argument-hint: "[the tax year, default the previous year]"
---

# Tax season organizer

The return itself takes an evening; collecting what goes into it takes weeks.
This skill turns the country pack's checklist into the household's own list:
what has arrived, what is missing, which reliefs to ask about, and by when.
It never fills in or files the return.

```
Member: "pomóż przygotować PIT za 2026"
→ Tax year, members, their income sources (asked, not guessed)
→ Information forms each source sends, and by when (country pack)
→ What the record already holds (record.py find), what is missing
→ Reliefs: one question each, with the proof it needs
→ Deadlines as obligations, after a yes; filing stays with the member
```

## Scripts

`shared/scripts/record.py` searches the record and writes reminders;
`shared/scripts/dates.py` gives the statutory dates. Run them with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" find "<household folder>" --query "PIT-11"
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/dates.py" recurring --country <CC> --year <year of filing> --lang <lang>
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read the registers and the pack directly, tag dates
`country pack rule — verify` and count weekdays from today's date.

The country pack is in this skill's folder:
`${CLAUDE_SKILL_DIR}/shared/locale/<CC>.md` (rules, windows, checklists) and
`<CC>.json` (the data `dates.py` reads), where `<CC>` is the profile's
Country, for example `PL`. Open it with the Read tool: it needs no shell and
no search, so read it on the no-Python path too.

Dates and amounts come out in the household's language: `record.py` reads it
from the profile, and `dates.py` takes `--lang pl` for Polish.

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record. The tax year is the previous
calendar year unless the member says otherwise.

## Step 1 — Who earned what

For each adult: employment, contract work, pension or benefit, savings and
investments, rental, income from abroad, a business. Ask; never infer from
the profile. A business, rental, foreign income, crypto-assets or a property
sale get the not-advice line in one sentence: the checklist helps, an
accountant or a tax adviser decides. For these, list only what to collect
(statements and transaction histories, contracts, records of income and
costs, invoices) and the pack's dates. Forms, rates, ways of being taxed and
elections the pack does not name are not given, not even marked to verify:
tax rules for these incomes change often, and a rule from memory may be out of
date.

## Step 2 — The forms

From the country pack's "Annual tax return" section: for each source, the
information form, who sends it and by when. Then `record.py find` for each:

| Member | Source | Form | Sent by, until | In the record |
|---|---|---|---|---|

"In the record" names the document id and date, or says *not filed yet* and
where to get it (the payer, or the online tax account that shows the forms
sent to the tax office).

## Step 3 — Reliefs, as questions

For each relief in the pack whose condition might fit the household, one
question with its law and the proof to keep ("Did you pay for internet at
home in 2026? Keep the invoices; limit and years from the pack."). Proof
already in the record is listed; proof missing is listed as missing. Never
compute the tax or the refund.

## Step 4 — Dates

The filing window and deadline, the date the pre-filled return is accepted
automatically, the date the information forms are due: from the pack, with
`dates.py recurring` (in the Polish pack: `pit-information-forms`,
`pit-twoj-e-pit-check`, `pit-annual`, `pit-1-5-pensioner-statement`). Offer
them as obligations (`record.py add … --dry-run`, show, write after a yes),
together with "collect the missing forms" tasks. When a refund is expected,
`dates.py window --id pit-refund-electronic` (or `pit-refund-paper`) from the
filing date gives the date to check for it; a correction has its own windows
in the pack.
In the GB pack: `sa-register`, `sa-paper-return`, `sa-online-return`,
`sa-january-payment`, `sa-july-payment-on-account`, `p60-arrives`,
`p11d-arrives`, `hicbc-paye-deadline` and `mtd-quarterly-update`.
Another pack has its own ids: they are in `shared/locale/<CC>.json`, and
`dates.py` lists the known ids when it is given one it does not know.

## Step 5 — One page

The checklist by member, the reliefs to decide, the missing items with who
sends them, the dates. Saved as `briefs/tax-<year>.md` after a yes. Income
figures stay out of briefs shared with children.

## Gates

- **Never fill in, sign or file** a return; never log in to a tax account.
- **No identifiers.** PESEL and NIP stay on the documents.
- **No tax advice.** Reliefs are questions with their law, and the not-advice
  line covers anything beyond the pack.
- **Every statutory date with its law and "verify".**
- **Show, then wait, then write** reminders with the approver's name.

Full rules: `shared/rules.md` (Not advice, Money, Personal data).

## Reference

- `shared/locale/<CC>.md` — the country pack (also `<CC>.json` for the scripts)
- [reference/gotchas.md](reference/gotchas.md) — tax-season mistakes seen in testing
