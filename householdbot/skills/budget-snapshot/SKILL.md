---
name: budget-snapshot
description: >
  Turns a bank statement export (CSV) into a one-page picture of the
  household's money: income and spending by month and category to the grosz,
  regular payments and price rises, the biggest changes against the previous
  month, and what the file does not cover. Learns the household's own
  categories with its approval. Use when someone sends a bank export or asks
  "where does our money go", "how much did we spend", "summarise my
  statement", "podsumuj wydatki", "na co idą pieniądze", "budżet", "wyciąg z
  banku".
argument-hint: "[the CSV export] [--months N]"
---

# Budget snapshot

A statement is hundreds of lines; the household needs one page. Every number
on that page comes from `statement.py`, which adds up with exact decimals, and
the page says first what the file covers and what it does not.

```
Member sends wyciag.csv
→ statement.py summary: coverage, gaps, balance check, totals by month and category
→ Read the warnings first: missing months, missing rows, partial months
→ One page: income, spending, net; categories; regular payments; changes
→ Unknown payees: offer category rules, written after a yes
→ No advice, no judgement; the member decides what to change
```

## Scripts

`shared/scripts/statement.py` reads the export (encoding, delimiter, header,
Polish and English column names), masks account and card numbers, and sums.
Run it with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/statement.py" summary "<export.csv>" --household "<household folder>"
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/statement.py" recurring "<export.csv>" --household "<household folder>"
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read the CSV, add up month by month with the
additions shown, tag every total `model calculation — verify`, and keep
account and card numbers out of the answer.

Amounts come out in the household's language: `statement.py` reads it from
the profile given with `--household`, or takes `--lang pl`.

## Step 0 — The record and the file

Find the record with `record.py locate --start "<working folder>"`, run by its
full path from the session's working folder (never after `cd` into the skill's
folder), or read `household-profile.md` in the working folder; `statement.py`
uses its category rules and language. If `locate` finds nothing, read
`household-profile.md` in the working folder yourself before saying the
household is not set up. The export is a CSV from the bank's website or app
(usually under the account history, "export" or "download", format CSV). A PDF
statement: ask for the CSV export instead; reading PDF statements is not
supported yet. Never log in to a bank, never fetch a statement yourself.

## Step 1 — Coverage before totals

Run `summary` and read, before any number:

- `period`: the first and last date in the file;
- `months_without_transactions`: months inside the period with no rows are
  missing, not zero;
- `balance_check.breaks`: a break in the running balance means rows are
  missing between those lines;
- `partial_months`: the file may start late or end early in these;
- `currencies`: one total per currency, never mixed;
- `skipped_lines`: summary or note lines the reader left out.

Say what the file covers in the first line of the answer.

## Step 2 — One page

1. Per month: income, spending, net (the script's `*_text` values).
2. Spending by category for the latest complete month, largest first, with
   one sentence naming the largest category and its share of spending.
3. Regular payments from `recurring`: payee, period, last amount, monthly and
   yearly equivalent, and price rises above 5% (`price_rise`).
4. The biggest changes against the previous month (`changes_last_month`):
   spending up or down by category.
5. Uncategorised payments (`uncategorised`): the three largest payees.

No judgement words ("too much", "wasteful"); the member decides.

## Step 3 — Teach a category, after a yes

For a payee that lands in "other" or in the wrong category, propose a rule:
`statement.py add-rule "<root>" --match "<payee>" --category <category>
--dry-run`, show it, and on a yes run it with `--approved-by "<name>"`. The
rule lives in `registers/category-rules.json` and is used from then on.

## Step 4 — Keep it

Offer to save the page as `briefs/budget-<YYYY-MM>.md`, and the export itself
through `file-document` (type `bank-statement`). Income and debt figures go
into a brief only when the profile says briefs are for adults only.

## Gates

- **Numbers from the script**, one total per currency, coverage stated first.
- **Missing is not zero.** Gaps and balance breaks are named before totals.
- **No full account or card numbers**; the script masks them, and so does
  every answer.
- **No advice** on saving, investing or borrowing; one line naming who gives
  it, when asked.
- **Show, then wait, then write** for category rules and saved pages.

Full rules: `shared/rules.md` (Money, Absent is not zero).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — statement traps seen in testing
