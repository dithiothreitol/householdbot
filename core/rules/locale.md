# Country, language and currency — nothing is assumed

HouseholdBot is not tied to a country. Nothing it emits assumes a language, a
currency, a tax system or a holiday calendar that the household profile did
not state.

---

## Where the values come from

Four fields in `household-profile.md`, captured by `household-onboard`:

```
- **Country:** <ISO 3166 two-letter code, e.g. PL, DE, GB, US>
- **Language:** <language the household reads, e.g. pl, de, en>
- **Currency:** <ISO 4217 code, e.g. PLN, EUR, GBP, USD>
- **Time zone:** <IANA name, e.g. Europe/Warsaw>
```

If one is missing when a skill runs, ask once, in one question, and offer to
store the answer. Never infer the country from a language, a provider's name
or an email address.

## Language

Speak and write to the household in its `Language`: questions, summaries,
briefs, drafts. Register field names and status values stay in English so
that files remain readable by every skill. Quotes from documents stay in the
document's own language.

## Amounts

- ISO code with the number: `PLN 1,240.00` in English, `1 240,00 PLN` or
  `1 240,00 zł` in Polish prose. Never a bare number.
- In registers: `amount` as a string with a dot and two decimals (`"1240.00"`)
  and `currency` as the ISO code.
- An amount in another currency is shown in that currency and named as such.
  It is never silently converted.
- An amount that cannot be read is reported as unreadable.

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

Packs are contributed per country; `CONTRIBUTING.md` at the repository root
describes the required sections and checks.
