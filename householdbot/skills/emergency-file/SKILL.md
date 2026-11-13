---
name: emergency-file
description: >
  The "if something happens" file for the other adult: whom to call, where the
  papers are, providers and regular payments, never a number or a password.
  Use for: "if something happens to me", "emergency file", "plik awaryjny",
  "gdzie co jest".
argument-hint: "[--refresh]"
---

# Emergency file

When an adult is suddenly in hospital or gone, the other one has to find
papers, pay bills and call the right people while upset. This file tells them
where everything is and whom to call. It never holds the things themselves:
numbers, codes and passwords stay where they are.

```
Member: "przygotuj plik na wypadek, gdyby coś mi się stało"
→ From the record: providers, policies, regular payments, deadlines, files
→ Shown at once as the outline of the file, gaps marked
→ The questions only the member can answer, in one short list
→ A draft with no identifiers or secrets → yes → briefs/emergency-file.md
→ A reminder to refresh it once a year (annual-review)
```

## Scripts

`shared/scripts/record.py` lists what the household has and pays. Run it with
Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" due "<household folder>" --kind payment,renewal --horizon 366 --today <today> --country <CC>
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" find "<household folder>" --query "<insurer or bank>"
```

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read `registers/documents.json` and
`registers/obligations.json` directly.

The country pack is in this skill's folder:
`${CLAUDE_SKILL_DIR}/shared/locale/<CC>.md` (rules, windows, checklists) and
`<CC>.json`, where `<CC>` is the profile's Country, for example `PL`. Open it
with the Read tool. "Where things are done" names the official services; the
life events section names the first statutory steps after a death.

## Step 0 — Find the record

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record.

The member has usually said for whom the file is ("for Piotr", "for Anna's
sister"); take that and go on. Where it will be kept is one of the questions
in Step 2, not a reason to stop here.

## Step 1 — From the record, shown at once

- **Providers and contracts:** from the profile's *Providers* and the
  documents: who supplies electricity, water, internet, insurance; type and
  provider only.
- **Policies:** insurer, what it covers, where the policy is (`documents/…`
  or the paper folder), the renewal date. No policy numbers.
- **Regular payments:** payee, about how much, how often, how it is paid
  (transfer, direct debit). No account numbers.
- **Deadlines in the next months:** the few that must not be missed.

Show this in the first answer as the outline of the file, under the section
names of Step 3, with what the record knows filled in and each gap marked
"to fill in". The member sees what the file will look like before answering
anything.

## Step 2 — From the member, in one list

Under the outline, one short numbered list of what only the member knows; they
may answer some now and the rest later:

- Where the file will be kept (the household folder is fine; a printed copy in
  a known place is better for some households), and for whom, if not said.
- Where the originals are kept (identity papers, deeds, policies, the will if
  there is one: only that it exists and where).
- Banks: which banks and account types, and that the bank's own helpline on
  the card is the way to block cards. Nothing else about the accounts.
- Whom to call: by name and role (a relative, the employer's HR, a notary, a
  friend with a key); a phone number only when the member gives it for this
  file.
- The home: where the main water valve, the fuse box and the gas valve are;
  who has a spare key.
- Children: school or nursery, who may collect them, the after-school
  arrangements. Health facts only when an adult asks for them to be here,
  written as what to do ("the medicine is in the kitchen drawer"), never as a
  list of conditions.
- Digital life: which password manager or safe holds the access, and who knows
  how to open it. Never the password itself.

## Step 3 — The draft

Sections: *Call first*, *Where things are*, *Money and regular payments*,
*Insurance*, *Home*, *Children*, *First steps* (for a death: the pack's
statutory steps through `life-event`, one line each; for a hospital stay:
the employer, the payments due in the next 30 days). Plain words, short lines,
readable on paper.

Before showing it, check it line by line for identifiers and secrets
(personal-data rule): identity, account, card or policy numbers, PINs,
passwords, codes. Any found is replaced by where it is ("policy number: on the
policy, page 1").

## Step 4 — Save and keep fresh

After a yes, write `briefs/emergency-file.md` (or the place the member
chose). Offer a yearly reminder to refresh it (kind `task`), which
`annual-review` also checks.

## Gates

- **No identifiers, no secrets.** Not one number or password, in the file or
  in the answer. A PIN, password or code the member typed is never quoted
  back, not even to warn them; say once, without the value, that it does not
  go into any file and, if it is real, that it is worth changing.
- **Where, not what.** Originals, codes and access are located, never copied.
- **The member decides what goes in**, especially anything about health.
- **Show, then wait, then write.**

Full rules: `shared/rules.md` (Personal data, Approval gates).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — emergency-file traps
