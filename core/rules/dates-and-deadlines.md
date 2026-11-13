# Dates and deadlines — plan to the safe date, show the arithmetic

A household misses a deadline in one of four ways: the date was read wrong, it
fell on a weekend, the letter took five days in the post, or the renewal rolled
over and nobody updated the note. Every skill that reads, computes or reports a
date follows these rules.

---

## The script counts, the model judges

`dates.py` (in the skill's `shared/scripts/`) knows the country's public
holidays and counting rules. Use it for every date that is computed rather
than read: a deadline from a delivery date, a cancel-by date, the safe
`do_by`, an urgency band, the next occurrence of a recurring payment, a
weekday. Pass today's date from the session with `--today`.

When Python is not available, compute by hand following the same rules, show
every step, and tag the result `model calculation — verify`.

## Today

Take today's date from the session. If it cannot be determined, ask. Never
compute urgency from an assumed date.

## How a date is written

- In registers: ISO `YYYY-MM-DD`.
- In prose: the weekday with the date, in the household's language and the
  country pack's local format (`pt. 20.11.2026` for Poland, `Fri 2026-11-20`
  in English). A date printed without its weekday hides the weekend problem
  this file exists to catch.
- A date that cannot be read is reported as unreadable, with the document and
  page. It is never guessed and never left blank as if there were none.

## Two dates per obligation

| Field | Meaning |
|---|---|
| `due_date` | The deadline as the source states it or as the rule gives it. |
| `do_by` | The date the household plans to. Alerts and urgency use this one. |

Computing `do_by`:

1. **Subtract transit time** when the action is not instant:
   `transit_buffer_days` is `0` for an online form or instant payment, `1`
   for an ordinary bank transfer, `5` for domestic post, `10` for
   international post, or what the document itself specifies. The country
   pack's `met_by` says whether posting or receipt counts; when receipt
   counts, the buffer is never zero for a letter.
2. **Roll back to a business day.** If the result is a Saturday, a Sunday or a
   public holiday, move to the previous business day. Roll back, never
   forward.
3. **Record the difference.** When `do_by` differs from `due_date`, write why
   in `do_by_note`: `"rolled back from Sun 2026-11-15"`.

Many legal systems move a deadline that ends on a holiday forward to the next
working day. The country pack records that rule and its law, and `dates.py`
reports it in `due_date`. The plan is still worked back from the unmoved end:
the forward move is margin, never the plan.

## Deadlines counted from delivery

"Within 14 days of receiving this letter" needs the delivery date.

- **Ask for it.** The date printed on the letter is not the date it arrived.
- If the household does not know, use the document date as the conservative
  start and say so.
- Apply the country pack's counting rule (`dates.py deadline` or `window`) and
  **show the arithmetic**: `delivered Tue 2026-11-03 + 14 days = Tue 2026-11-17`.
- Deemed delivery (a registered letter left at the post office, an electronic
  delivery box) follows the country pack (`dates.py deemed`) and is named when
  it applies.

## Provenance: every date says where it came from

One tag per date, stored in `provenance` and carried into every report:

| Tag | When |
|---|---|
| `stated in document` | the date is printed in the source; `source` holds page and quote |
| `calculated from document` | `dates.py` computed it from dates and periods the document states |
| `country pack rule — verify` | the rule comes from the country pack; the law is named |
| `model calculation — verify` | the model did the arithmetic without the script |
| `told by household member` | a member said so |

A statutory date never appears without its law and the word *verify*. The
letter in hand and the official source control; the pack is a reminder.

## Urgency bands

Computed on `do_by` by `dates.py band` or `record.py due`, as half-open
intervals so each obligation lands in exactly one band:

| Band | Days until `do_by` |
|---|---|
| ⚫ overdue | fewer than 0, status still `open` |
| 🔴 now | 0 to 6 |
| 🟠 soon | 7 to 29 |
| 🟡 coming | 30 to 89 |

Day 0 is today. Days 7, 30 and 90 belong to the later band. Obligations 90 or
more days away are not shown unless asked for.

**Lead time.** An obligation with `lead_time_days` also appears, marked
*start now*, from `do_by` minus that many days, whatever band it is in. Use it
for anything that needs comparing, booking or gathering first.

## Renewals and cancel-by dates

For a contract that renews by itself, the obligation is the last day to give
notice, not the renewal day: `due_date` = end of the current term minus the
notice period (`dates.py cancel-by`).

Store the notice period, the required method (email, form, written letter) and
the transit buffer in `notice`. Compute from the **current** term end, which
moves every time the contract renews.

## Recurrence

When a recurring obligation is completed, `record.py complete` sets it to
`done` with `done_date` and appends the next occurrence with the same
`series`, a new id and fresh dates. Both changes go through one approval.

A recurrence written as free text ("15 Mar, 15 May, 15 Sep, 15 Nov") is not
guessed: take the next date from the source or the country pack
(`dates.py recurring`) and add it as a new entry. If an auto-renewing contract
passed its cancel-by date with no notice recorded, close it as `lapsed`, say
that it renewed, and offer the next occurrence.
