# Changelog

## 0.2.1

Behaviour tests outside the plugin package (stage 2.1).

- The eval suite moved from `householdbot/evals/` to `evals/` at the
  repository root, so the plugin package carries no test files (184 files
  instead of 307).
- `scripts/eval.py` runs `claude plugin eval` on a staged copy of the plugin
  with the tests in `build/`; arguments pass through and results go to
  `evals/results/`.
- The validator checks the suite in its new place and refuses a test folder
  inside the plugin.

## 0.2.0

Money and correspondence (stage 2 of 4).

- Skills: `inbox-triage` (the mailbox sorted into decide, file, nothing and
  suspicious, nothing changed in it), `bills-due` (payment list with totals,
  payee account endings compared with the last bill, two separate approvals),
  `contract-check`, `subscriptions-review`, `budget-snapshot`,
  `tax-season-organizer`, `reply-to-letter`, `complaint-and-claim`,
  `cancel-or-switch`, and the `monthly-review` chain.
- `statement.py`: reads bank CSV exports (UTF-8 or Windows-1250, any
  delimiter, preamble lines, Polish and English column names, one amount
  column or debit and credit columns), masks account, card and PESEL numbers,
  sums with exact decimals by month and category, checks the running balance
  and missing months, finds recurring payments and price rises, learns the
  household's own category rules after a yes.
- `record.py due --kind/--category` with totals per currency;
  `dates.py` statutory dates on the last day of a month (`MM-L`).
- Shared rules `money` (payment lists, two approvals, account checks, totals
  from the script) and `voice` (drafts in the recipient's language, formal,
  identifiers as placeholders, the sender's name from the profile or a
  placeholder, a mailbox draft only after the member approves its text,
  never sent). A case or customer number the member wrote is used with a
  note to check it; one that sits only in a filed document stays a
  placeholder.
- Polish answers use forms that mark no grammatical gender until the member's
  own words show theirs; nothing is inferred from a name.
- Every skill that reads the country pack names its path, so the pack is
  read without a shell or a search tool.
- Bills record the last four digits of the payment account, so a changed
  account is caught.
- Polish country pack: the annual tax return (information forms, Twój e-PIT,
  joint filing, reliefs and the proof each needs, corrections and refunds
  after the 1 Oct 2026 amendment), consumer complaints and claims (goods,
  digital content, insurers, banks, payment services, telecom, energy),
  giving notice (form, delivery, OC, energy, telecom, renting, payment
  accounts) and paying (when a transfer counts, statutory interest);
  24 new response windows and 3 recurring tax items, each with its law.
- `dates.py window` reports what meets a window (`met_by`, such as sending in
  time) and what a missing reply means (`silence`) when the pack states it.
- `record.py locate` started inside the plugin's own folder says so instead
  of reporting a household that is not set up; every skill runs it from the
  session's working folder.
- Eval cases: 31 new (62 in total), with a mocked mailbox for the mail cases.

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
