# Changelog

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
