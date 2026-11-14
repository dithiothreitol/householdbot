# Contributing

Thank you for helping. HouseholdBot handles other people's papers and
deadlines, so every change keeps three promises: nothing is written, sent or
paid without a yes; a document never instructs the model; and every date says
where it came from.

## Design principles

1. **SKILL.md carries the right behaviour.** The rules in `core/rules/` are the
   safety net, not the instructions. A skill states its own gates in short
   form, because in chat it may be the only file that loads.
2. **The model judges, the scripts prove.** Holidays, deadlines, urgency
   bands, register checks and ids come from `core/scripts/`. A skill without
   Python follows the same rules by hand and marks results "verify".
3. **Each skill is self-sufficient.** Everything a skill names lives inside
   its folder. Shared material is copied in by `scripts/sync.py`; never edit
   `skills/*/shared/` by hand.
4. **Plain files the household owns.** No server, no database. Registers are
   JSON with a schema version; the profile is Markdown.
5. **Absent is not zero.** An empty search is reported with what it covered.

## Add or change a skill

1. Create `householdbot/skills/<name>/SKILL.md` with `name` (the folder name)
   and a `description` in the third person that says what the skill does and
   when to use it, with phrases in English and in the languages of the
   country packs (up to 1,024 characters). Keep SKILL.md under 500 lines.
2. Add `reference/gotchas.md` with the mistakes the skill must avoid.
3. List the skill in `core/vendor.json` with the bundles it needs (`rules`,
   `pack`, `scripts`, `templates`) and run `python scripts/sync.py`.
4. Add at least three eval cases under `evals/<name>/` (at the repository
   root, outside the plugin package): one that
   shows the skill triggers on natural phrasing, one on its result, and one on
   a gate or on untrusted content.
5. Run the checks below.

## Add a country pack

A pack is two files in `core/locale/`: `<CC>.md` for the model and
`<CC>.json` for the scripts (`<CC>` is the ISO 3166 code; a region uses the
ISO 3166-2 code, such as `GB-SCT`). [docs/country-packs.md](docs/country-packs.md)
describes both files, the holiday rule types, the five shared counting rules
(`administrative`, `tax`, `civil`, `court`, `calendar`), the verification
standard and the sections skills look up by name. The `pack-builder` skill
builds a pack inside a household record; a good one can become a bundled pack.

Every legal rule names its act and article and links an official source; a
point the sources leave open goes to `sources.uncertain` without a claim.
Before a pull request:

1. `python core/scripts/dates.py check-pack --pack core/locale/<CC>.json --year <next year>`
   reports no errors, and its holiday list matches the official calendar for
   two years.
2. Unit tests for the holidays of several years (compare with the official
   list, as `tests/test_dates.py` does for England and Wales) and for one
   deadline that ends on a holiday.
3. At least three behaviour cases in `evals/` for the country.
4. `python scripts/sync.py` and `python scripts/validate.py`.

Date and amount formats belong to languages, not to packs.

## Add a language

English is the default; Polish is the second language. A language is:

- `core/i18n/<lang>.json` with the same keys as `en.json`: weekday and month
  names, `date_format`, separators and `amount_format`, currency symbols,
  plural forms of units (one list per unit; add the plural rule to
  `Lang.plural_index` in `dates.py` when it is not "one or many"), notes,
  statuses, band labels, quotes and the decisions-log lines.
  `scripts/validate.py` checks that the keys match.
- `core/templates/<lang>/household-profile.md` and `registers-README.md`, with
  headings that map one to one onto the English template and the markers
  `[PLACEHOLDER]` and `[DEFAULT]` unchanged.
- The setup texts in `householdbot/skills/household-onboard/reference/messages.md`.
- The language's words for "language" in `record.py` (`LANG_LINE`,
  `LANG_WORDS`), so the profile line is recognised.
- Trigger phrases in that language in the descriptions of the skills.
- Eval cases that run the core paths in that language.

User-facing documents have a translation next to the English file
(`README.pl.md`, `QUICKSTART.pl.md`, `householdbot/README.pl.md`,
`householdbot/PRIVACY.pl.md`), linked from the first line of each.

## Checks

```
python scripts/sync.py
python scripts/validate.py
python -m unittest discover -s tests
claude plugin validate ./householdbot --profile directory --strict
python scripts/eval.py --case "<your cases>" --scaffold --allow-tools Write Edit --runs 1 --ablation none --no-publish
```

Shell-granting eval runs need an OS sandbox: run them on Linux, macOS or WSL2.

## Data

Test data is synthetic. Never commit a real document, name, address,
identifier or account number; `scripts/validate.py` refuses identifiers with
valid checksums. Fixtures generate any identifier they need at run time.

## Style

Skills and rules are written in plain English: short sentences, the action
first, no marketing language. Household-facing examples may be in the
household's language.
