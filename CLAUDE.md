# Working on HouseholdBot with Claude Code

## Layout

- `householdbot/` is the plugin. `skills/<skill>/SKILL.md` and
  `skills/<skill>/reference/` are written by hand.
- `householdbot/skills/<skill>/shared/` is **generated** by `scripts/sync.py`
  from `core/`. Never edit it; edit `core/` and run the sync.
- `core/vendor.json` says which skill gets which bundle.
- `householdbot/evals/<skill>/<case>/case.yaml` are behaviour tests; the
  synthetic household comes from `householdbot/evals/fixtures/make_household.py`.
- `docs/development-plan.md` is the staged plan (in Polish). Read the current
  stage before starting work, and update it when a stage closes.

## After every change

```
python scripts/sync.py
python scripts/validate.py
python -m unittest discover -s tests
```

Before a stage closes, also run
`claude plugin validate ./householdbot --profile directory --strict` and the
eval suite (`cd householdbot && claude plugin eval . --scaffold --allow-tools Write Edit --no-publish`).
On Windows, eval runs cannot grant Bash (no OS sandbox), so they exercise the
skills' no-Python path; the scripts are covered by the unit tests.

## Rules for changes

- A skill names only files inside its own folder.
- SKILL.md stays under 500 lines; detail goes to `reference/`.
- Every write a skill makes is shown first and runs with `--approved-by`.
- Test data is synthetic. No real document, name, address or identifier ever
  enters the repository.
- Country-pack facts cite an act, an article and an official source.
