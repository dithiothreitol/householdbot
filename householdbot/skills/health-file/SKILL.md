---
name: health-file
description: >
  Health papers per person with strict privacy: referrals and prescriptions
  with their validity, appointments, results; neutral titles, no medical
  advice. Use for: "is the referral still valid", "prescription expiry",
  "skierowanie", "recepta ważna do", "wyniki".
argument-hint: "[person] [--appointments]"
---

# Health file

Health papers are the ones a household looks for in a hurry. This skill
indexes them per person, counts how long each stays valid, and keeps their
content away from everything shared: briefs, family calendars, logs.

```
Member: "do kiedy jest ważne skierowanie Zosi?"
→ Whose papers? The person concerned, or an adult acting for a child
→ The record: documents in category health (neutral titles)
→ Validity from the country pack's "Health papers" (dates.py window)
→ Reminders and appointments after a yes, with neutral titles
→ Where the official copies are (the pack names the patient account)
```

## Scripts

`shared/scripts/record.py` finds health papers and writes reminders;
`dates.py` counts validity windows. Run them with Python 3:

```
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/record.py" find "<household folder>" --query "<person>" --category health
python3 "${CLAUDE_SKILL_DIR}/shared/scripts/dates.py" window --country PL --from <date issued> --id <window id from the pack> --lang pl
```

Window ids in the Polish pack: `prescription-paper`, `e-prescription`,
`e-prescription-365`, `e-prescription-365-full-quantity`,
`prescription-antibiotic`, `prescription-imported-or-immunological`,
`prescription-narcotic`, `referral-original-delivery`,
`waiting-list-reinstatement`, `physiotherapy-referral-registration`,
`spa-referral-paper-sending`, `spa-referral-nfz-decision`,
`sick-leave-address-change`, `sickness-benefit-claim`.

`${CLAUDE_SKILL_DIR}` is this skill's folder; where it was not substituted,
use the folder this SKILL.md was read from. Use `python` or `py -3` where
`python3` is not found or is only a placeholder that prints "Python was not
found". Without Python, read `registers/documents.json`, count by hand with
every step shown, the weekday counted from today's date, tagged
`model calculation — verify`.

The country pack is in this skill's folder:
`${CLAUDE_SKILL_DIR}/shared/locale/<CC>.md` (rules, windows, checklists) and
`<CC>.json` (the data `dates.py` reads), where `<CC>` is the profile's
Country, for example `PL`. Open it with the Read tool: it needs no shell and
no search, so read it on the no-Python path too. The section "Health papers"
names the validity of prescriptions and referrals and the window ids.

Dates come out in the household's language: `record.py` reads it from the
profile, and `dates.py` takes `--lang pl` for Polish.

## Step 0 — Find the record, and whose file it is

Read `household-profile.md` in the working folder (or an attached folder, or a
direct subfolder) with the Read tool. When it is not there, run
`record.py locate --start "<working folder>"` by its full path from the
session's working folder (never after `cd` into the skill's folder), then
check the pointer `~/.claude/plugins/config/householdbot/location.md`. A
missing shell never means a missing record.

Ask whose papers, when it is not clear. An adult sees their own and a child's
they care for; another adult's health papers only with that adult's word in
the conversation. A child asking gets their own appointments, not results.

## Step 1 — The index

`record.py find --category health` for the person (without Python, read
`registers/documents.json`). One table: the paper with its neutral title, the
date, valid until (when it expires), where the original is (the file, or "in
the patient account"). Register titles stay neutral: "Referral, Zosia",
"Prescription, Anna", "Results, Piotr"; the specialty, the medicine and the
result stay in the document.

A request to save or register a paper starts here too. A paper already in the
register (same person, same kind, about the same date) is named with its id
and its neutral title, and only what is missing is offered, such as the
reminder with its date counted from the date of issue in the register. Ask for
the paper itself only when the register does not have it.

New papers go through `file-document`; tell it this is a health paper, so the
title and key facts stay neutral and the quote holds only the date and
validity.

## Step 2 — Validity

For a referral or a prescription: `dates.py window --id <the pack's window>`
from the date of issue (or the "valid from" date the paper names). Show the
last day with its weekday and the law, tagged `country pack rule — verify`.
When the pack has no window for that paper, say what the paper itself states
and that nothing else is known.

Offer one reminder per paper, kind `expiry`, title neutral ("Prescription,
Anna: last day"), `lead_time_days` 7; dry run, yes, write.

## Step 3 — Appointments

An appointment the member mentions becomes an obligation of kind
`appointment` with the time in `notes` and a neutral title ("Appointment,
Zosia"). A calendar entry goes through `family-calendar`, same title.

## Step 4 — Official records

The official copy of e-prescriptions, e-referrals, sick-leave papers and
vaccinations is in the patient account the pack names under "Where things are
done". Point there; never log in, never ask for a login.

## Gates

- **Health details stay with the person.** Never in a brief, a shared
  calendar, the decisions log, a list or a title. A title naming a specialty
  or a condition is not written even when the member asks for one: keep the
  neutral title and say the detail stays in the document, where it is when
  they open it. Propose one reminder with its date, not a menu.
- **No medical advice.** What a result means, whether to take a medicine,
  which doctor to see: the not-advice line, and the doctor or the pharmacist.
- **No identifiers.** Prescription and referral codes, PESEL and insurance
  numbers stay on the paper: "code: see page 1".
- **Show, then wait, then write** reminders with the approver's name.
- **Removing is one request.** A member who wants a health paper out of the
  record gets it out (the entry and, after a yes, the file).

Full rules: `shared/rules.md` (Personal data, Not advice, Approval gates).

## Reference

- [reference/gotchas.md](reference/gotchas.md) — health-file traps
