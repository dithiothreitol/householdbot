# Pilot protocol

**English** · [Polski](pilot.pl.md)

The pilot is the last condition of version 1.0 (definition of done in
`development-plan.md`, conditions 1 and 6): a real household goes through the
full path without the author's help, and no blocking error is left open. It
runs on version 1.0.0-rc.4, between Stages 5 and 6.

## Before the first session

- **A private folder outside this repository**, for example
  `Documents/Household`. Real documents never enter the repository; the
  `.gitignore` catches some folder names, not all.
- **HouseholdBot 1.0.0-rc.4** installed from the marketplace
  (`/plugin marketplace update householdbot`, then `/plugin install
  householdbot@householdbot`). `/plugin` shows the version.
- **Python 3.8 or newer** on the PATH. On Windows, `python3` can be a Microsoft
  Store placeholder that runs nothing; `python --version` must answer.
- **A copy of the folder** (a zip) before each session, so any session can be
  undone.
- **This file and a notes file** next to each other. The notes hold no real
  data (see the template below).

## Twelve scenarios

| # | Scenario | What to ask | What to check |
|---|---|---|---|
| 1 | Setup | "set up HouseholdBot", quick setup | the record is created by one commit after one yes; the host's prompt shows the change |
| 2 | Three documents filed | a bill, an insurance policy, an official letter | each one previewed and filed after a yes; obligations with dates; originals in `documents/<year>/` |
| 3 | The deadline list | "what's due?" | bands, the plan date and the last day, tags in your language |
| 4 | An official letter with a deadline | the letter, "until when?" | the last day with its article and the plan date, each checked against `dates.py window` or the act |
| 5 | A bank export | a CSV from your bank | account numbers masked; totals match the statement |
| 6 | A cancellation drafted | "cancel the internet contract" | a draft only; nothing sent |
| 7 | The weekly brief | "weekly brief" | two date columns; saved through `record.py save` only after a yes |
| 8 | The dashboard | "a page for the fridge" | nothing on it you would not hang there; the HTML prints on A4 |
| 9 | Reminders on a phone | "make a calendar file" | the `.ics` imports; after a change and a new export the events update instead of doubling |
| 10 | A life event | a move, a car, a birth, a new job, if one is due | the steps with dates and laws; nothing written without a yes; skip with a note when none applies |
| 11 | Cowork with a scheduled brief | a weekly scheduled task | the run reads and reports; the record is unchanged |
| 12 | A phone through Remote Control | "what's due today" from the phone | the answer comes from the record on the computer |

## Measures

| Measure | Target | How |
|---|---|---|
| Writes without consent | 0 | every line in `log/decisions.md` matches a yes you gave; `registers/.history/` holds nothing unexpected |
| Wrong dates | 0 | every computed date checked with `dates.py` or the source act |
| Minutes to the first weekly brief | recorded | from installation to the first brief |
| Corrections per scenario | recorded | how many times you corrected the answer |
| Host prompts that showed the right change | all | the prompt before each commit matches what you approved |

## Errors

**Blocking:** a write without consent, a wrong last day, an identifier
stored, a document lost or overwritten, a failure that stops a scenario.
Each one is reproduced on synthetic data and fixed before 1.0 (Stage 6,
part A).

**Not blocking:** wording, an extra question, slowness, formatting. Each is
recorded and fixed when it is cheap.

## Notes template

Notes describe what happened in your own words. They never hold a name, an
address, a number, an amount or a case reference from a real document, and a
screenshot shows synthetic data only.

```
Scenario: 4 · an official letter with a deadline
Date: <day> · Host: Claude Code <version> · Model: <model>
What I asked (my own words, no real data):
What happened:
What I expected:
Blocking: yes / no
Corrections I made:
```

## Done when

All twelve scenarios have run (a scenario that does not apply is skipped with
a note), no blocking error is left open, and the measures are recorded. The
notes go to the author in the template's form, as a private message or an
issue; they start Stage 6.
