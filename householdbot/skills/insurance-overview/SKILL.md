---
name: insurance-overview
description: >
  Every policy in one table: cover, insurer, term, premium, renewal,
  cancel-by, compulsory or not; overlaps and gaps as questions, no buying
  advice. Use for: "what insurance do we have", "what insurance is
  compulsory", "jakie mamy ubezpieczenia", "jakie ubezpieczenia musimy mieć".
argument-hint: "[--member NAME]"
---

# Insurance overview

Policies arrive one at a time, from different insurers, banks and schools,
and renew on different days. This skill puts them in one table, says which
ones the law requires as the country pack states it, and asks about what
looks doubled or missing. Choosing cover stays with the household.

```
Member: "jakie mamy ubezpieczenia?"
→ Policies: documents of type insurance-policy; renewals in the register
→ One table: cover, for whom, insurer, term, premium, renews how, last day to cancel
→ Compulsory or voluntary: the country pack, with its law
→ Premium against last year's policy; overlaps and gaps as questions
→ Renew or switch → cancel-or-switch; offers → contract-check; claims → complaint-and-claim
```

## Scripts

`shared/scripts/record.py` finds the policies and their renewal entries and
writes missing reminders; `shared/scripts/dates.py` counts a last day to
cancel the register does not hold yet. Run them with Python 3 and today's
date:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" find "<household folder>" --query "policy polisa insurance ubezpieczenie" --register documents
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" due "<household folder>" --kind renewal,payment --category insurance,vehicle --horizon 400 --today <today> --country <CC>
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/dates.py" cancel-by --country <CC> --term-end <term end> --notice <n> --unit days --transit <days>
```

Window ids in the Polish pack: `compulsory-policy-renewal-document`,
`insurance-claim-limitation`, `farm-holder-change-notice`,
`insurer-claim-acknowledgement`, `insurer-claim-payment`.

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read `registers/documents.json` and
`registers/obligations.json` directly, add up by hand with the addition
shown, count dates with every step and the weekday counted from today's
date, and tag the results `model calculation — verify`.

This skill does not read bank exports. For payments to insurers, ask the
member what they see, or hand the export to `subscriptions-review`, which
lists repeating payments, and compare its payees with the table.

The country pack is in this skill's folder:
`${CLAUDE_SKILL_DIR}/shared/locale/<CC>.md` (rules, windows, checklists) and
`<CC>.json` (the data `dates.py` reads), where `<CC>` is the profile's
Country, for example `PL`. Open it with the Read tool: it needs no shell and
no search, so read it on the no-Python path too.

Dates and amounts come out in the household's language: `record.py` reads it
from the profile, and `dates.py` takes `--lang pl` for Polish (English is the
default).

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record. Read the profile for the language,
the country, the members, the *Homes* and the *Vehicles*. With no record, work
from the policies the member shows and say nothing is saved.

## Step 1 — Collect the policies

- Documents of type `insurance-policy` under any category (a vehicle policy
  is often filed under `vehicle`), and their renewal and premium entries: the
  ids in each policy's `obligations` field (`record.py show --id ob-…`), or
  entries matched by insurer.
- Cover mentioned in other papers (an account or card package, a mortgage's
  required cover, school accident cover in a school letter) is listed as
  "mentioned, not filed", with the document it came from.
- A policy whose term has ended with no newer one filed: "ended on <date>;
  was it renewed?" (absent is not zero).

## Step 2 — One table

| Cover | For whom or what | Insurer | Term | Premium | Renews | Last day to cancel | Compulsory? | Source |
|---|---|---|---|---|---|---|---|---|

- *Cover*: what the policy says it covers, with the page; quotes stay in the
  policy's language, with a translation when the household reads another.
- *Premium*: per year, with the currency; instalments named.
- *Renews*: "by itself", "does not renew" or "not stated", from the policy's
  own words, never assumed.
- *Last day to cancel*: from the register; otherwise `dates.py cancel-by`
  from the term end and the notice the policy or the pack gives; "unknown"
  when neither does. A policy that does not renew shows its end date and
  "nothing to cancel".
- *Compulsory?*: as the pack's "Insurance a household must or may have" says,
  with the law and "verify". A kind the pack does not list is "not in the
  pack", never "voluntary" by assumption.
- Totals per currency, from the script or added by hand with the addition
  shown, each naming what it covers ("PLN 3,150.00 a year for the 3 policies
  in the record").

## Step 3 — Premium against last year

The previous policy for the same cover: the document the new one
`supersedes`, or the earlier entry in the same `series`. Show both amounts
and the change with the arithmetic, tagged `model calculation — verify`; ask
about any rise above 10%. No earlier policy in the record means no
comparison, never "unchanged".

## Step 4 — Overlaps and gaps, as questions

- **Overlaps:** the same risk for the same person or thing in two policies:
  two home policies for one home, private liability in a home policy and
  again in a bank or card package, school accident cover and a child's own
  accident policy, assistance in two places. Ask what each covers (sums, who,
  where, the excess) before anyone calls it a duplicate.
- **Gaps:** what the profile shows and the record holds no policy for: a
  home, a vehicle beyond its compulsory cover, a child at school, a trip.
  Ask: "The record has no policy for X. Is there one that was not filed, or
  none?" Never "you should buy".
- **Compulsory cover missing:** when the pack makes a cover compulsory and
  the record holds none for that home or vehicle, say so plainly, with the
  law, and ask whether the policy is filed elsewhere.

## Step 5 — Hand on

- Renew, switch or cancel: `cancel-or-switch`.
- A new offer or the terms of a package: `contract-check`.
- Damage, a claim or a refused claim: `complaint-and-claim`.
- A policy paid for but not filed: `file-document`.
- A reminder the register lacks (a last day to cancel, an end date with lead
  time to compare offers): build it, `record.py add "<root>" --register
  obligations --file - --country <CC> --today <today> --dry-run`,
  show it, ask one question, and write with `--approved-by "<name>"` after
  the yes.

## Step 6 — Which cover to buy

Which cover to buy, how much, from whom, or which of two overlapping covers
to keep is advice. Say so once, in one line, naming who gives it (an
independent adviser or a broker) and the date that matters (the next last day
to cancel), then keep to the facts in the table.

## Gates

- **Never buy, renew, cancel or claim**, and never log in to an insurer's
  portal.
- **Questions, not advice.** Overlaps and gaps are asked about; which cover
  to buy gets the not-advice line once.
- **Compulsory only as the pack says**, with its law and "verify".
- **Show, then wait, then write** with the approver's name.
- **No policy numbers**; the register points to the page.
- **Totals per currency**, each with what it covers.

Full rules: `shared/rules.md` (Not advice, Money, Absent is not zero).

## Reference

- `shared/locale/<CC>.md` — the country pack (also `<CC>.json` for the scripts)
- [reference/gotchas.md](reference/gotchas.md) — insurance overview traps
