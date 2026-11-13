# Language, country and currency — nothing is assumed

HouseholdBot speaks English (the default) and Polish, and it is not tied to a
country. Nothing it emits assumes a language, a currency, a tax system or a
holiday calendar that the household profile did not state.

---

## Where the values come from

Four fields in `household-profile.md`, captured by `household-onboard`:

```
- **Language:** <en (default) or pl>
- **Country:** <ISO 3166 two-letter code, e.g. PL, DE, GB, US>
- **Currency:** <ISO 4217 code, e.g. PLN, EUR, GBP, USD>
- **Time zone:** <IANA name, e.g. Europe/Warsaw>
```

A Polish profile uses the Polish labels (`Język`, `Kraj`, `Waluta`, `Strefa
czasowa`). If a value is missing when a skill runs, ask once, in one question,
and offer to store the answer. Never infer the country from a language, a
provider's name or an email address, and never infer the language from the
country: an English-speaking household can live in Poland.

## Which language to answer in

In this order:

1. **A request in the current message** ("in English", "po polsku") applies to
   this answer. When it differs from the profile, offer to store it
   (`household-customize`).
2. **The profile's `Language`.**
3. **No profile yet:** the language the member writes in, when it is English
   or Polish; English otherwise. Say once, in one line, that the other
   language is available.

Other languages work in conversation, but the curated texts, templates and
date formats exist for English and Polish only. Say so once when a member
writes in a third language.

## What stays in which language

- **Answers, questions, summaries and briefs:** the household's language.
- **Quotes from documents:** the document's own language, in quotation marks.
  When it differs from the household's language, add a translation after the
  quote.
- **Drafts to an office, a court, a company or a school:** the recipient's
  language and conventions (a Polish office gets formal Polish). When that
  differs from the household's language, add a translation for the member and
  mark it as a translation, not the text to send.
- **Registers:** field names, status values, kinds, categories and ids stay in
  English so that every skill reads them the same way. Titles and notes are
  written in the household's language.
- **The decisions log:** written by `record.py` in the household's language.

## Dates and amounts

The scripts format both in the household's language (`dates.py --lang`;
`record.py` reads the profile) from `shared/i18n/<lang>.json`:

| | English | Polish |
|---|---|---|
| Date in prose | `Fri 20 Nov 2026` | `pt. 20.11.2026` |
| Amount | `PLN 1,240.00` | `1 240,00 zł` |

- Registers keep ISO dates (`2026-11-20`) and amounts as strings with a dot
  (`"1240.00"`) plus the currency code.
- An amount in another currency is shown in that currency and named as such.
  It is never silently converted.
- An amount or a date that cannot be read is reported as unreadable.

## Country packs

Each skill that needs them carries the pack in `shared/locale/<CC>.md`
(reminders and rules for the model) and `shared/locale/<CC>.json` (holidays,
counting rules and statutory dates for `dates.py`).

- When the pack for the household's `Country` exists, skills read it before
  computing or proposing any statutory date.
- When it does not exist, skills work from what documents state and what the
  household says, and say once that no country pack is loaded, so statutory
  reminders are not offered.
- **A legal rule names its law.** Every statutory window, date or threshold in
  a pack cites the act and article, carries the pack's review date, and
  reaches the household tagged `country pack rule — verify`.
- A pack is a reminder list, not legal advice.

Packs and languages are contributed separately; `CONTRIBUTING.md` at the
repository root describes both.
