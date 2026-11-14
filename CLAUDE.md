# Working on HouseholdBot with Claude Code

## Layout

- `householdbot/` is the plugin. `skills/<skill>/SKILL.md` and
  `skills/<skill>/reference/` are written by hand.
- Two manifests, one plugin: `householdbot/.claude-plugin/plugin.json` for
  Claude and the portable `householdbot/plugin.json` for Codex and ChatGPT,
  with the same name, version and description; `.agents/plugins/marketplace.json`
  mirrors `.claude-plugin/marketplace.json`. A version bump changes both;
  `scripts/validate.py` checks they agree.
- `householdbot/skills/<skill>/shared/` is **generated** by `scripts/sync.py`
  from `core/`. Never edit it; edit `core/` and run the sync.
- `core/vendor.json` says which skill gets which bundle.
- Languages: English is the default, Polish the second. Formats, notes and
  log lines live in `core/i18n/<lang>.json`; templates in
  `core/templates/<lang>/`; setup texts in
  `householdbot/skills/household-onboard/reference/messages.md`. A change to
  a user-facing document (`README`, `QUICKSTART`, the plugin `README` and
  `PRIVACY`) goes into both the English file and its `.pl.md` translation.
- `evals/<skill>/<case>/case.yaml` are behaviour tests, kept at the
  repository root so the plugin package carries no test files. The
  synthetic household and bank exports come from `evals/fixtures/`.
  `claude plugin eval` reads cases only inside a plugin, so
  `python scripts/eval.py` copies the plugin and the tests into `build/`
  and runs there; arguments pass through, results go to `evals/results/`.
- `docs/development-plan.md` is the staged plan (English; Polish translation
  in `development-plan.pl.md`, kept in step). Read the current stage before
  starting work, and update it when a stage closes.
- `docs/architecture.md` is the analysis of the pattern; `docs/country-packs.md`
  describes the packs. `managed-agent-cookbooks/deadline-watcher/` is the
  unattended variant; `python managed-agent-cookbooks/deadline-watcher/cookbook.py sync`
  after editing `householdbot/agents/deadline-watcher.md`.

## After every change

```
python scripts/sync.py
python scripts/validate.py
python -m unittest discover -s tests
```

Before a stage closes, also run
`claude plugin validate ./householdbot --profile directory --strict`, the
eval suite (`python scripts/eval.py --scaffold --allow-tools Write Edit --no-publish`),
the session tests (`python scripts/session_test.py`; `--check` checks the
session files without a model) and `python scripts/package.py --skills`
(release packages in `dist/`). On Windows, eval runs cannot grant Bash (no OS
sandbox), so they exercise the skills' no-Python path; the scripts are
covered by the unit tests and the session tests.

## Rules for changes

- A skill names only files inside its own folder.
- SKILL.md stays under 500 lines; detail goes to `reference/`.
- Every write a skill makes is a preview first; only
  `commit --confirm <token> --approved-by <name>` applies it, after the
  member's yes. `scripts/validate.py` refuses a write in one call.
- Text from documents, messages, file names or bank exports never goes on a
  command line: scripts take it on standard input (`--file -`,
  `--query-file -`), as `core/rules/untrusted-content.md` says.
- On Windows, write files with LF line endings (`write_bytes`, or
  `newline="\n"`); Python's text mode would write CRLF.
- Test data is synthetic. No real document, name, address or identifier ever
  enters the repository.
- Country-pack facts cite an act, an article and an official source.
