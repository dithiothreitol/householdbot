---
name: annual-review
description: >
  The yearly round: papers that may be shredded (it never deletes anything),
  renewals, subscriptions, tax papers, the archive, the record's health, the
  emergency file. Use for: "annual review", "what can we shred", "przegląd
  roczny", "co można wyrzucić", "usuń stare rachunki".
argument-hint: "[--year YYYY]"
---

# Annual review

Once a year the household's papers need pruning and its contracts a look.
This chain does it in the order that saves the most work, keeps every step's
approval separate, and never deletes, sends or cancels anything itself.

```
Member: "zróbmy przegląd roczny"
→ 1 Papers: record.py retention → may go / no keeping date / kept for good
→ 2 Policies and 3 subscriptions: renewals and overlaps (their skills)
→ 4 Tax papers for the year (tax-season-organizer)
→ 5 Closed reminders to archive (record.py archive)
→ 6 The country pack's review date; 7 the record's health; 8 the emergency file
→ One page at the end, saved after a yes
```

## Scripts

`shared/scripts/record.py` reports and archives; `dates.py` dates the year.
Run them with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" retention "<household folder>" --today <today>
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" archive "<household folder>" --before <YYYY-01-01> --dry-run
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" validate "<household folder>"
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read `registers/documents.json` and compare each
`keep_until` with today's date, showing the comparison.

The country pack is in this skill's folder:
`${CLAUDE_SKILL_DIR}/shared/locale/<CC>.md` (rules, windows, checklists) and
`<CC>.json` (the data `dates.py` reads, including `retention`), where `<CC>`
is the profile's Country, for example `PL`. Open it with the Read tool: it
needs no shell and no search, so read it on the no-Python path too. The
section "Keeping and shredding documents" says how long each kind of paper is
kept and on what basis.

Dates come out in the household's language: `record.py` reads it from the
profile, and `dates.py` takes `--lang pl` for Polish.

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record. Say the eight steps in one line
and which ones will be skipped.

## Step 1 — Papers to keep, papers that may go

`record.py retention`:

- **May go** (`may_go`): the keeping date has passed. List them with their
  dates and where the file and paper are. The household shreds the paper and
  deletes the file; the plugin never does. After the member says it is done,
  offer `record.py update --id <id> --set status=disposed` for each (preview,
  yes, commit).
- **No keeping date** (`no_keeping_date`): propose one per paper from the
  pack's table (the period, what starts it, the basis, or "suggested" where no
  statute sets it), and the profile's *Documents kept for*. One batch of
  `update --set keep_until=...`, previewed, yes, committed.
- **Kept for good** (`permanent`): counted, not listed.

## Steps 2 and 3 — Policies and subscriptions

Follow `insurance-overview` for renewals in the next 90 days, overlaps and
gaps, and `subscriptions-review` for recurring costs (a bank export when the
member gives one). Their approvals are their own.

## Step 4 — Tax papers

Follow `tax-season-organizer` for the tax year that has just ended: which
information forms will arrive and when. Reminders after its own yes.

## Step 5 — Closed reminders

`record.py archive --before <1 January of this year>`: a preview of how many
closed obligations move to `archive/`. Commit its token after a yes.

## Step 6 — The rules' age

The country pack's review date (the first lines of `<CC>.md`). Older than
twelve months: say that rules may have changed and that a plugin update may
carry a newer pack.

## Step 7 — The record's health

`record.py validate`: errors, warnings, conflict copies. Anything found goes
to `household-doctor`.

## Step 8 — The emergency file

Is there one (`briefs/emergency-file.md`), and when was it last written?
Offer `emergency-file --refresh`.

## Step 9 — One page

What may go and what went, keeping dates set, renewals coming, subscriptions
kept or to cancel, tax papers expected, archived reminders, the pack's age,
the record's state. Saved as `briefs/annual-review-<year>.md` (`record.py save`, then
`record.py commit` after the yes).

## Scheduled runs

A run with nobody in the loop does steps 1 (report only), 6 and 7 and lists
what waits for a yes. It disposes, archives and updates nothing.

## Gates

- **Never delete, shred or move a document.** The household does; the
  register only records it, after a yes. "Delete the old bills" gets the list
  of what may go and this sentence; the plugin never offers to delete files or
  register entries, with or without a shell.
- **Each step keeps its own approval**; nothing approved in one step counts in
  another.
- **Keeping periods come with their basis**: the law, or "suggested".
- **Absent is not zero.** Skipped steps are reported as skipped.

Full rules: `shared/rules.md` (Chain seams, Household record, Approval gates).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — annual-review traps
