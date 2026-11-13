# Changelog

## 0.1.1

English and Polish (stage 1.1).

- English is the default language and Polish the second: the setup asks
  first, "in Polish" or "po angielsku" switches later, and the choice is
  stored in the profile.
- Languages live in `core/i18n/` (`en.json`, `pl.json`): weekday and month
  names, date and amount formats, plural forms, notes, band labels and the
  decisions-log lines. `dates.py --lang` and `record.py` (from the profile)
  write dates, amounts, notes and log lines in the household's language.
- Profile and register templates in English and Polish
  (`templates/en/`, `templates/pl/`); setup texts in both languages.
- Documents keep their language: quotes in the original with a translation,
  drafts to offices in the office's language with a translation for the
  member.
- Polish versions of the README, QUICKSTART, plugin README and privacy note.
- Polish country pack: court letters count as delivered on the last day of
  the second 7-day collection period (usually 15 days after the first
  notice); a first category B driving licence issued from 4 Sep 2026 is valid
  only for the probation period. Both checked against case law and acts.
- Seven new eval cases for languages (31 in total).

## 0.1.0

The core of HouseholdBot (stage 1 of 4).

- Skills: `household-onboard`, `household-router`, `file-document`,
  `find-document`, `deadline-tracker`, `weekly-brief`,
  `household-customize`, `household-doctor`.
- Agents: `deadline-watcher` (read-only), `document-reader` (no write tools).
- The household record: profile, JSON registers with `schema_version`,
  filed originals, decisions log, backups of every register write.
- Proof layer: `dates.py` (holidays, counting rules, safe dates, bands,
  recurrence, statutory dates) and `record.py` (locate, init, validate, add,
  update, complete, due, find, merge of sync-conflict copies, archive,
  migrate), with unit tests.
- Shared rules: approval gates, untrusted content, personal data, the
  household record, dates and deadlines, absent is not zero, locale, storage
  scope, chain seams, output style, not advice.
- Country pack: Poland (`PL`), every legal rule checked against the
  consolidated texts in the Sejm ELI service on 2026-11-13, with sources.
- Behaviour tests: 24 eval cases on a synthetic household.
