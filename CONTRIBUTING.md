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
4. Add at least three eval cases under `householdbot/evals/<name>/`: one that
   shows the skill triggers on natural phrasing, one on its result, and one on
   a gate or on untrusted content.
5. Run the checks below.

## Add a country pack

A pack is two files in `core/locale/`:

- `<CC>.md` for the model, with these sections: *Public holidays*, *How
  deadlines are counted*, *Deemed delivery*, *Common response windows*,
  *Recurring household obligations*, *Documents with an expiry date*, *Where
  things are done*, *Writing for a <country> household*, *Scam patterns*,
  *Sources*, and a `Reviewed:` line.
- `<CC>.json` for `dates.py`: `weekend`, `holidays` (fixed and
  Easter-relative), `counting_rules` (each with `end_roll` and `law`),
  `deemed_delivery`, `response_windows`, `recurring`, `weekday_names`,
  `date_format_local`, `reviewed`.

Every legal rule names its act and article and links an official source.
Add unit tests for the holidays of the current and next year and for one
deadline that ends on a holiday. Use the generic counting rule ids
(`administrative`, `tax`, `civil`, `court`, `calendar`) so skills work across
countries.

## Checks

```
python scripts/sync.py
python scripts/validate.py
python -m unittest discover -s tests
claude plugin validate ./householdbot --profile directory --strict
cd householdbot && claude plugin eval . --case "<your cases>" --scaffold --allow-tools Write Edit --runs 1 --ablation none --no-publish
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
