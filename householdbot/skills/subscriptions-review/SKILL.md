---
name: subscriptions-review
description: >
  Recurring costs from the register and bank exports: monthly and yearly cost,
  price rises, promotions ending, cancel-by dates. Use for: "what
  subscriptions do we pay for", "Netflix went up", "jakie mamy abonamenty",
  "stałe opłaty".
argument-hint: "[a bank export, optional]"
---

# Subscriptions review

Small monthly payments are easy to forget and easy to raise. This skill puts
them in one table with their yearly cost, spots what changed, and leaves the
decision to keep or cancel with the household.

```
Member: "jakie mamy abonamenty?"
→ The register: recurring payments and contracts with a monthly fee
→ A bank export, if given: statement.py recurring
→ One table: service, period, last amount, monthly and yearly cost, change, cancel by
→ Flags: price rise, promotion ending, overlap, renewal soon
→ The member picks what to cancel → cancel-or-switch
```

## Scripts

`shared/scripts/statement.py` finds repeating payments in a bank export, with
monthly and yearly equivalents and price changes; `shared/scripts/record.py`
reads the register and writes new reminders. Run them with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/statement.py" recurring "<export.csv>" --household "<household folder>"
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" due "<household folder>" --kind payment,renewal --horizon 365 --today <today> --country <CC>
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read both by hand, show each multiplication, and tag
the totals `model calculation — verify`.

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
missing shell never means a missing record.

## Step 1 — Collect

- **Register:** open obligations with a recurrence and kind `payment` or
  `renewal`, and contracts in `documents.json` with a monthly fee in their key
  facts.
- **Bank export**, when the member gives one: `statement.py recurring`. Keep
  the categories that are commitments (subscriptions, utilities, insurance,
  housing); groceries and fuel repeat but are not subscriptions.
- No export: work from the register, say that bank payments were not checked,
  and offer to look at an export.

A payee in both sources is confirmed; a payee only in the bank is a
commitment the register does not know about yet.

## Step 2 — One table

| Service | Payee | Period | Last amount | Monthly | Yearly | Change | Cancel by |
|---|---|---|---|---|---|---|---|

Monthly and yearly figures come from the script; the totals per currency
from `monthly_total_text` and `yearly_total_text` (for the rows shown). The
*Cancel by* date comes from the register, or is marked unknown.

## Step 3 — Flags, as questions

- price rise above 5% since the previous payment (`price_rise`);
- a promotion ending or a fixed term ending within 60 days;
- two services of the same kind (two video services, two cloud plans);
- a yearly renewal within 60 days;
- "Is this still used?" for each service, asked, never assumed.

## Step 4 — Act, after the member chooses

- To cancel: hand each one to `cancel-or-switch`.
- To remember a promotion end or a cancel-by date the register lacks: build
  the obligation, `record.py add …` (a preview), show it, commit after a yes.

## Gates

- **The household decides** what is used and what is cancelled.
- **Never cancel, never log in** to a service or a bank.
- **Show, then wait, then write** new reminders with the approver's name.
- **Totals per currency, from the script**, with what they cover.
- **No full account or card numbers.**

Full rules: `shared/rules.md` (Money, Approval gates).

## Reference

- `shared/locale/<CC>.md` — the country pack (also `<CC>.json` for the scripts)
- [reference/gotchas.md](reference/gotchas.md) — subscription traps seen in testing
