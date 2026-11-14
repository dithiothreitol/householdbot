# Implementation plan

**English** · [Polski](development-plan.pl.md)

Status: 2026-11-14, after Stage 4 (version 1.0.0-rc.1). The tool and the
documentation are bilingual: English by default, Polish as an option; the
user documents have `.pl.md` versions, and the developer documents
(CONTRIBUTING, CLAUDE.md, the skills, `docs/architecture.md`,
`docs/country-packs.md`) are in English. The plan has this English version
(`development-plan.md`, the default) and a Polish translation
(`development-plan.pl.md`), kept in step.

---

## 1. Goal and definition of done

An open (Apache-2.0), fully functional tool for running a household's
affairs, built on the same patterns as Anthropic's vertical plugins
(`knowledge-work-plugins/small-business`, `claude-for-legal`). The project
has two results: a working tool and a documented analysis of the pattern
(`docs/architecture.md`).

Version 1.0 is done when all of these conditions are met:

1. A household goes through the full path without the author's help:
   installation, setup, filing a document, the deadline list, the weekly
   brief.
2. Every area in section 4 has a working skill with test cases.
3. No date or amount in a result comes from an unchecked model calculation
   where running a script is possible.
4. Nothing is saved, sent or paid without a household member's approval, as
   the tests confirm.
5. The plugin passes `claude plugin validate --profile directory --strict`,
   the repository validator and the plugin directory checklist.
6. A pilot in a real household (yours) completed without blocking errors.
7. A write to the household record applies only a change that was shown
   first: the scripts enforce it, and where the host has hooks a person
   confirms it in the host's own prompt; the session tests confirm both
   (added with Stage 5).
8. Every host named in the README has a row in the compatibility table,
   filled from the critical session suite (added with Stage 6).

---

## 2. The reference pattern and how it maps

Verified on clones of both repositories (as of 13 Nov 2026).

| Element of the pattern | From | Counterpart in the project |
|---|---|---|
| Marketplace: `.claude-plugin/marketplace.json`, one entry per plugin | both | the same |
| One plugin with a router and onboarding, 44 skills | small-business | one plugin, 34 skills |
| `skills/<name>/SKILL.md` + `reference/` (gotchas, examples) | small-business | the same, every skill has `reference/gotchas.md` |
| `shared/*.md`: cross-cutting rules | small-business | `core/rules/` copied into every skill |
| Start interview, quick (2 min) and full (15 min), `[PLACEHOLDER]` / `[DEFAULT]` markers | legal | `household-onboard` |
| Profile in a file outside the plugin directory, which survives updates | legal | profile in the household folder + a pointer in `~/.claude/plugins/config/householdbot/` |
| Register with dates, provenance and roll-back to a business day | legal (`renewal-register.yaml`) | `registers/obligations.json` + `dates.py` |
| `customize` skill: changing one thing without a new interview | legal | `household-customize` |
| Read-only recurring agent | legal (`renewal-watcher`) | `deadline-watcher` |
| Skill chains with an approval gate at every step | small-business | monthly review, life events, annual review |
| Approval gates: coding and payment are two separate approvals | small-business | `core/rules/approval-gates.md` |
| Rule: do not promise a schedule that nobody set | small-business | `core/rules/chain-seams.md` |
| `build-agent`: a repeated task turned into a skill | small-business | `build-skill` |
| Managed agent cookbook: `agent.yaml`, subagents, three permission tiers | legal | `managed-agent-cookbooks/deadline-watcher` |
| Repository documents: README, QUICKSTART, CONNECTORS, CONTRIBUTING, CLAUDE.md | legal | the same + SECURITY, CHANGELOG, NOTICE, CODE_OF_CONDUCT |
| Design principle: SKILL.md carries the right behaviour on its own, the shared rules are a safety net | legal (CONTRIBUTING) | binding for every skill |

Fundamental differences: a home has no system of record (ERP, DMS), so the
project provides its own record (D2); the project adds a proof layer in
scripts (D4), which the patterns do not have.

---

## 3. Architectural decisions

**D1. Name: `householdbot`.** Decision of 13 Nov 2026. The marketplace and
the plugin are called `householdbot`, the commands `/householdbot:<skill>`,
the display name HouseholdBot, the public repository `householdbot`. A name
made of two generic words may be sent to manual review in the plugin
directory; that is a hold, not a rejection.

**D2. The household record as a folder of plain files.** A folder the
household chooses (ideally on a synced drive). Profile, registers,
originals, reviews, archive, decisions log, register backups in
`registers/.history/`. Order of access: the file system, the pointer, a
document storage connector, work in the conversation alone with a clear
message that nothing was saved.

**D3. Registers in JSON with a schema.** Decision of 13 Nov 2026.
`documents.json` and `obligations.json` with `schema_version`. The schema is
enforced by `record.py` (the standard library has no JSON Schema validator),
and the fields are described in `registers/README.md`. Amounts as strings
(`"286.40"`), with no floating-point errors.

**D4. Proof layer: scripts calculate, the model judges.** Decision of
13 Nov 2026, in line with Anthropic's guidance for skills: ready-made scripts
for deterministic and error-prone operations, and a "plan, validate,
execute" loop. `dates.py` and `record.py`, standard library only, JSON
output, Python 3.8+. Without Python the skill calculates on its own and
marks the result `model calculation — verify`.

**D5. Every skill is self-sufficient.** Sources in `core/` (rules, country
packs, scripts, templates), copies in `skills/<skill>/shared/` generated by
`scripts/sync.py` according to `core/vendor.json`. The rules reach a skill
as one file, `shared/rules.md`, with a table of contents. The validator
checks that SKILL.md points to nothing outside its own folder and that the
copies are up to date.

**D6. Target surfaces.**

| Surface | Scope in v1.0 | Status after Stage 4 |
|---|---|---|
| Claude Code (terminal, IDE, Code tab in the app) | full | verified: installation from the marketplace, sessions with scripts on Windows |
| Cowork (desktop) | full: files, scripts, agents, scheduled tasks | according to the documentation: the plugin from the marketplace or from the `householdbot.plugin` file, skills, agents and hooks work, scheduled tasks use plugins; test in the pilot |
| claude.ai (browser) | skills and connectors; the record through a drive connector | according to the documentation: the plugin's skills or single skills from the release zips, scripts in the code sandbox, agents and hooks skipped; a test case with the record behind the Google Drive connector |
| Phone | controlling a session on the computer | according to the documentation: the phone does not install plugins, Remote Control drives a Claude Code session with the plugin; test in the pilot |

**D7. Country.** A country pack is `core/locale/<CC>.md` (for the model) and
`<CC>.json` (for the scripts: holidays with names in the country's language
and in English, counting rules, delivery rules, deadlines, statutory dates).
The counting rule identifiers are shared across countries
(`administrative`, `tax`, `civil`, `court`, `calendar`). Every legal rule
gives the act, the article and the source. Date and amount formats belong to
the language, not to the country. A second pack in Stage 4.

**D14. Languages: English by default, Polish as an option.** Decision of
13 Nov 2026. The order for choosing the reply language: a request in the
current message, then `Language` from the profile, and without a profile the
language of the message if it is English or Polish, otherwise English. The
setup starts with the choice of language (the first line of the reply in
both languages). Language data in `core/i18n/<lang>.json` (days, months,
date and amount formats, plural forms, notes, band labels, log entries);
templates in `core/templates/<lang>/`; setup texts in
`household-onboard/reference/messages.md`. `record.py` reads the language
from the profile (also from the Polish heading "Język"), and `dates.py`
takes `--lang`. Language does not follow from the country: an
English-speaking family in Poland gets Polish letters explained in English,
with a quote of the original, and letters to Polish offices in Polish, with
a translation. The registers keep English field and status names; titles,
notes and the log are in the household's language. My reading of
"English by default": without a profile I reply in the language of the
message (English or Polish), and English applies when nothing indicates the
language; the "always English until a choice is made" variant is a change
to one rule in `core/rules/locale.md`.

**D8. Connectors.** Mail, calendar, document storage (addresses taken from
the small-business plugin). Every skill works without connectors.

**D9. Scope of v1.0: full.** Decision of 13 Nov 2026. Home administration
and everyday life: the family calendar, meals, shopping, the division of
chores (Stage 3).

**D10. Licence and attribution.** Apache-2.0, `NOTICE` names the sources of
the pattern, and the README contains a sentence stating that the project is
not affiliated with Anthropic.

**D11. Proactivity.** A schedule only where the environment provides real
scheduled tasks (scheduled tasks in Cowork and in the desktop app); in other
cases an honest substitute (a calendar entry). Unattended variant: a managed
agent cookbook with a weekly scheduled deployment (Stage 4).

**D12. Behaviour test format.** One `case.yaml` per case (the prompt and the
graders in one file) and a `setup.sh` that generates a synthetic household
with dates computed relative to the day of the run. Reason: the limit of 512
files in a plugin, and tests that do not go stale.

**D13. Agent permissions.** `document-reader` has only `Read` and `Glob`, so
an instruction injected into a document has nothing to act with.
`deadline-watcher` has read tools and a shell that its instructions limit to
the script's read commands. A write requires `--approved-by`, which the
agent does not pass.

---

## 4. Functional scope of v1.0

Thirty-four skills (three of them chains) and two agents.

### Core (Stage 1, done)

| Skill | Task |
|---|---|
| `household-onboard` | choosing the folder, quick and full interview, the first document, reminders from the country pack, the weekly rhythm |
| `household-router` | entry point: matching a request to one skill, simple lookups |
| `file-document` | reading a letter, scam screening, classification, facts with page and quote, deadlines from the script, filing after approval |
| `find-document` | "gdzie jest" ("where is it"), "co tam było napisane" ("what did it say"), "kiedy się kończy" ("when does it end") |
| `deadline-tracker` | the deadline list, adding, completing with the next occurrence, overdue items, computing a deadline, reminders from the pack |
| `weekly-brief` | one page per week |
| `household-customize` | changing one thing in the profile, with the consequences in the registers |
| `household-doctor` | consistency of the record, merging conflict copies, schema migration, archiving |

Agents: `deadline-watcher`, `document-reader`.

### Money and correspondence (Stage 2, done)

| Skill | Task |
|---|---|
| `inbox-triage` | mail sorted into: needs a decision, to file, nothing to do, suspicious; bills and letters passed to `file-document`; the mailbox left unchanged without approval |
| `bills-due` | a pile of bills, a list of payments for a household member to make; two separate approvals |
| `contract-check` | a contract or an offer before signing: term, renewal, price changes, penalties, the right of withdrawal |
| `subscriptions-review` | recurring costs: price rises, unused services, the end of promotions, notice dates |
| `budget-snapshot` | a bank statement: categories, fixed charges, comparison of months |
| `tax-season-organizer` | the full set of documents for the annual tax return according to the country pack; no filing |
| `reply-to-letter` | a reply, an explanation or an appeal in response to a letter; the deadline; a draft for the household member to send |
| `complaint-and-claim` | a complaint, a return, a guarantee, damage: a draft, a list of evidence, the deadline for an answer |
| `cancel-or-switch` | notice in the form the contract requires, the posting date, tracking the confirmation |
| `monthly-review` chain | bills, new documents, the next month, the spending picture |

### Home, family and everyday life (Stage 3, done)

| Skill | Task |
|---|---|
| `home-upkeep` | statutory and seasonal checks, guarantees, repair history, comparison of contractors' quotes |
| `vehicle-file` | insurance, vehicle inspection, servicing, fines, buying and selling |
| `health-file` | appointments, validity of referrals and prescriptions, an index of documents; stricter privacy rules |
| `school-desk` | school letters and notices: dates, fees, consent forms, per child |
| `insurance-overview` | all policies in one table; overlaps and gaps as questions |
| `identity-and-travel` | validity of documents, readiness for a trip |
| `emergency-file` | the "if something happens" document for the other adult: where everything is, no secrets |
| `family-calendar` | who, where and when in the week: clashes, lifts, birthdays and name days; calendar entries after approval |
| `meal-planner` | the week's meal plan from preferences, allergies (sensitive data), budget and time; an ingredient list |
| `shopping-list` | a shared shopping list: from the meal plan, staples and household members' requests, grouped by shop |
| `chore-rotation` | a fair division of chores with rotation and tasks matched to the children's ages |
| `life-event` chain | moving house, the birth of a child, buying or selling a car, a change of job, the death of someone close |
| `annual-review` chain | retention, review of policies and subscriptions, the full set of tax documents, the register archive |

New parts of the record in Stage 3: `registers/chores.json` (chores,
household members' shares and saved plans), the `lists/` folder (shopping,
staple products, meal plans), the `chores.py` script (a plan computed
deterministically by share and age, with the load of previous weeks evened
out), an optional *Everyday life* section in the profile.

### Reach and extensibility (Stage 4, done)

| Skill | Task |
|---|---|
| `household-dashboard` | a one-page view of everything |
| `build-skill` | a repeated household task turned into the household's own skill |
| `pack-builder` | creating and verifying a country pack |

In addition: the `deadline-watcher` cookbook, a second country pack (GB:
England and Wales), packs built by the household in `packs/` in the record.

---

## 5. Repository structure (status after Stage 4)

```
.claude-plugin/marketplace.json        marketplace "householdbot"
.github/workflows/validate.yml         sync, validator (with the cookbook), tests, claude plugin validate
.github/workflows/release.yml          tag → release packages (build without write access, publishing separately)
.github/workflows/evals.yml            behaviour tests with a shell on Linux, run manually
README.md QUICKSTART.md CONNECTORS.md (+ .pl.md) CONTRIBUTING.md CLAUDE.md
SECURITY.md CHANGELOG.md CODE_OF_CONDUCT.md NOTICE LICENSE .gitignore
docs/development-plan.md (+ .pl.md) architecture.md country-packs.md
managed-agent-cookbooks/deadline-watcher/   managed agent: agents/, schedule.yaml, cookbook.py, README
core/                                  sources of everything that goes into the skills
  rules/*.md                           14 shared rules (Stage 2: money, voice; Stage 3: everyday)
  locale/PL.md PL.json GB.md GB.json   country packs
  i18n/en.json pl.json                 languages: dates, amounts, inflection, notes, log
  scripts/dates.py record.py           proof layer
  scripts/statement.py                 bank statements (Stage 2)
  scripts/chores.py                    division of chores (Stage 3)
  money/categories.json                spending categories in two languages (Stage 2)
  templates/en/ templates/pl/          profile, registers guide in each language
  vendor.json                          which skill gets which bundles
scripts/sync.py validate.py make_icon.py
scripts/eval.py                        behaviour tests on a copy of the plugin in build/ (Stage 2.1)
scripts/package.py                     householdbot.plugin and a zip of each skill (Stage 4)
tests/test_dates.py test_record.py test_statement.py test_chores.py test_security.py test_cookbook.py
evals/<skill>/<case>/case.yaml setup.sh [mocks/gmail|google-calendar|google-drive/*.md]
evals/fixtures/make_household.py make_household_gb.py make_statement.py make_everyday.py seed.sh
householdbot/                          the plugin
  .claude-plugin/plugin.json icon.png   .mcp.json   README(.pl).md   PRIVACY(.pl).md   LICENSE
  hooks/hooks.json
  agents/deadline-watcher.md document-reader.md
  skills/<skill>/SKILL.md reference/*.md
  skills/<skill>/shared/               generated copies (rules.md, locale/, i18n/, scripts/, templates/)
```

Plugin file count: 147 after Stage 1.1, 307 after Stage 2 (with the
behaviour tests inside), 184 after Stage 2.1, when the tests moved out of the
package, 297 after Stage 3 and 382 after Stage 4 (34 skills, two country
packs). Each further pack adds 54 files (two in each of 27 skills), so two
more packs still fit under the threshold of 512, above which the plugin
directory reviews by hand.

---

## 6. Verification strategy

| Level | What it checks | Tool | When |
|---|---|---|---|
| 1. Structure | manifests, frontmatter, self-sufficiency of skills, freshness of copies, directory limits, agent permissions, shape of tests, country packs, identifiers and secrets in files | `scripts/validate.py`, `claude plugin validate --profile directory --strict` | after every change, in CI |
| 2. Arithmetic | holidays, deadlines, roll-back, bands, recurrence, registers, merging, archiving | `python -m unittest` | after a script change, in CI |
| 3. Behaviour | skill triggering, correctness of the result, stopping at the gate, resistance to injection and scams | `claude plugin eval` through `scripts/eval.py` | during work: single cases; at the close of a stage: a full run |
| 3b. Sessions (from Stage 5) | multi-turn paths with the scripts: the write gate, injection, identifiers, dates, language; checked by the state of the household folder and by patterns, without an LLM judge | `scripts/session_test.py` through a host's command line | after a change to a script or a gate; at the close of a stage: the whole suite twice |
| 4. Use | the full multi-turn path, real documents | a `claude -p` session on synthetic data, the pilot | after every stage |

Limits found in Stage 1 and their status after Stage 4:

- On Windows `claude plugin eval` does not grant a shell (no OS sandbox), so
  the behaviour tests here check the variant without Python. The path with
  scripts is checked by the unit tests and the multi-turn session. The
  `evals.yml` workflow runs the tests with a shell on Linux (bubblewrap and
  socat); it works once the repository exists and a secret with an API key
  has been added.
- Cases with a write after approval need a conversation history
  (`context.history_file`). The format of this file is not described in the
  documentation (all that is known is that it is JSONL), and a transcript
  from a local session contains the user's paths, so writes after approval
  are still checked by the multi-turn session.
- Test reports stay local (`--no-publish`), with the cost capped by
  `--max-cost-usd`.

Test data is synthetic only; the generator creates identifiers at run time,
and the validator rejects identifiers with a valid checksum in the
repository's files.

### Stage closing protocol

1. Levels 1 and 2 green, level 3 above the threshold, the multi-turn session
   and the pilot without blocking errors.
2. This plan updated: what was done, departures, lessons.
3. CHANGELOG and version number.
4. Project memory updated.
5. Commit; no work in progress.

---

## 7. Stages

Four stages, each as one session; Stages 2 and 3 are independent of each
other. Stages 5 and 6 were added on 14 Nov 2026 and are planned, each as
one session, with the pilot between them.

### Stage 1. Core: record, documents, deadlines (version 0.1, done)

Done on 13 Nov 2026:

- **A. Foundation.** The name `householdbot` in the manifests and paths, the
  icon, README, PRIVACY and LICENSE in the plugin, the repository documents,
  `.gitignore`, CI.
- **B. Record.** JSON registers with `schema_version`, a profile template, a
  description of the fields, register backups on every write, a decisions
  log written by the script.
- **C. Proof layer.** `dates.py` (fixed and movable holidays, Christmas Eve
  from 2025, counting rules with the statutory shift, `do_by` counted from
  the unshifted end, bands, recurrence with a day anchor, statutory dates
  from the pack). `record.py` (locate, init, validate with identifier
  detection, next-id, add with a copy of the original and a file
  fingerprint, update, complete with the next occurrence, due, find with
  Polish inflection, show, conflicts, diff, merge of a conflict copy,
  archive, migrate). 48 unit tests.
- **D. Shared rules.** Seven revised and four new: `absent-is-not-zero`,
  `storage-scope`, `chain-seams`, `output-style`.
- **E. PL pack.** Verification against official sources: see section 8.
- **F. Skills.** Eight core skills, each with `reference/gotchas.md`.
- **G. Agents.** `deadline-watcher`, `document-reader`.
- **H. Generator and validator.** `scripts/sync.py`, `scripts/validate.py`.
- **I. Behaviour tests.** 24 cases (3 per skill) on a synthetic household: a
  bill with a gate, two SMS messages asking for a parcel surcharge, a letter
  with an injected instruction, a deadline across a holiday, a missing
  document, a policy number, a bank account change from an email, a conflict
  copy, a PESEL in the register, an empty register, no record.

Departures from the plan: copies in `skills/<skill>/shared/` instead of
`references/shared/`; the schema in `record.py` instead of `*.schema.json`
files; the generator is called `scripts/sync.py`; tests in the single
`case.yaml` format; the `merge` command (merging conflict copies) and
identifier detection in the registers were added.

Results: see section 8.

Your part (pilot, about 30 minutes):

1. In Claude Code: `/plugin marketplace add <path to this repository>`, then
   `/plugin install householdbot@householdbot`.
2. `/householdbot:household-onboard`, quick setup, a folder outside the
   repository (ideally on a synced drive).
3. Three of your own documents: a bill, a policy or a contract, an official
   letter.
4. "co mamy do zrobienia" ("what do we have to do"), "przegląd tygodnia"
   ("weekly brief").
5. Notes for me: what was calculated wrong, unclear or unnecessary.

The pilot also covers language: the setup starts with the choice, and the
request "po polsku" ("in Polish") sets Polish in the profile.

### Stage 1.1. Bilingual support and two points of the PL pack (version 0.1.1, done)

Done on 13 Nov 2026 at the request of the same day ("bilingual, English by
default, a choice of language"; "apply the recommendations", that is, the
two points of the PL pack left to be checked).

- **Languages** according to D14: `core/i18n/en.json` and `pl.json`,
  `dates.py --lang`, the language from the profile in `record.py` (log,
  amounts, dates, notes), the `templates/en|pl/` templates, setup texts in
  both languages, the language choice rule, quotes with a translation,
  letters to offices in the office's language, Polish inflection of numerals
  (1 dzień, 2 dni, 5 tygodni).
- **User documents** in both languages: README, QUICKSTART, the plugin's
  README and PRIVACY, with a language switcher in the first line.
- **PL pack:** a court letter is delivered on the last day of the second
  7-day period, usually 15 days after the first notice (KPC art. 139 § 1,
  regulation Dz.U. 2024 poz. 19, SN IV CKN 1026/00, confirmed by examples
  from SO Gliwice); a first category B driving licence issued from
  4 Sep 2026 is valid only for the probation period (2 years, 3 years when
  obtained at the age of 17).
- **Fixes from the tests:** a `transit_buffer_days` field for payments, so
  that the next occurrence of a bill keeps the spare day for the transfer; a
  request to change an account that was put on hold does not reach the
  record even as a warning, and its number is not repeated; the skill
  descriptions recognise questions about deadlines and about changing the
  language better.
- **The validator** checks the consistency of the keys in the language
  files, the templates for every language, the setup texts in both languages
  and the Polish counterparts of documents, with links in both directions.
- **Tests:** 65 unit tests (including agreement with case law for the court
  letter), 31 behaviour cases (7 new ones for languages).

### Stage 2. Money and correspondence (version 0.2, done)

Done on 13 Nov 2026:

- **A. Skills.** Nine skills and the `monthly-review` chain, each with
  `reference/gotchas.md` and a variant without Python: `inbox-triage`,
  `bills-due`, `contract-check`, `subscriptions-review`, `budget-snapshot`,
  `tax-season-organizer`, `reply-to-letter`, `complaint-and-claim`,
  `cancel-or-switch`. The router directs requests in Polish and in English
  to them.
- **B. `statement.py`.** CSV export from a bank: UTF-8 or Windows-1250
  encoding, any separator, preamble lines, Polish and English column names,
  one amount column or separate debits and credits. Masking of account,
  card and PESEL numbers; totals in `Decimal` by month and category; a
  running balance check; months without transactions reported as missing;
  recurring payments with a monthly and an annual equivalent, and price
  rises above 5%; the household's category rules saved after approval.
  Categories in `core/money/categories.json` with labels in both languages.
- **C. `record.py` and `dates.py`.** `due --kind/--category` with totals per
  currency; statutory dates on the last day of the month (`MM-L`); `window`
  states what meets the deadline (`met_by`) and what a missing reply means
  (`silence`) when the pack specifies it; `locate` run in the plugin folder
  returns a hint, and every skill runs it from the session's working folder.
- **D. Shared rules.** `money` (the payment list, two separate approvals,
  the ending of the payee account compared with the previous bill, totals
  only from the script) and `voice` (letters in the recipient's language, a
  formal tone, identifiers as fields to fill in, nothing is sent). The
  language rule gained Polish forms without grammatical gender, used until
  the household member shows their own.
- **E. PL pack.** Four sections verified against the consolidated texts in
  the Sejm ELI service as of 13 Nov 2026: the annual PIT return, complaints
  and claims, notices of termination (form and delivery), payments. 24 new
  deadline windows and 3 recurring obligations, each with a legal basis.
  Details in section 8.
- **F. Test data.** `make_statement.py` with three export layouts (a Polish
  bank with a preamble in Windows-1250, debit and credit columns, English
  with tabs) and a variant with a gap; a mock mailbox with eight threads (a
  bill, an account change from a domain resembling the provider's, a fake
  parcel surcharge, a one-time code, a school consent form, an OC renewal).
- **G. Tests.** 86 unit tests (including 12 for statements and 5 for
  `locate`), 62 behaviour cases (31 new).

Departures from the plan: the mail mocks sit in the case folders
(`mocks/gmail/`), and each case has its own set of threads; PDF statements
are out of scope, and the skill asks for a CSV export; a bill records the
last four digits of the payee account, which is the only exception to the
"identifiers only as pointers" rule and serves to detect an account change.

Acceptance criteria and how they are met:

- the path of a bill, a payment list and two separate approvals: the
  multi-turn session (section 8) and the `bills-due` cases
- an official letter with a deadline and its arithmetic, the draft not sent:
  the `reply-to-letter` cases, including the gate for a draft in the mailbox
- a statement to the cent, missing data reported as missing: unit tests for
  three layouts and the `statement-gap` case
- notice of termination with its form and delivery time: the multi-turn
  session and the `cancel-or-switch` cases

Results: see section 8.

Your part (pilot): a CSV export from your own bank for `budget-snapshot` and
`subscriptions-review`, current bills in `bills-due`, two real letters in
`reply-to-letter` or `complaint-and-claim`.

### Stage 2.1. Behaviour tests outside the plugin package (version 0.2.1, done)

Done on 13 Nov 2026 following your decision of that day ("behaviour tests
outside the plugin package").

- The tests moved from `householdbot/evals/` to `evals/` at the root of the
  repository. The plugin package contains no test file: 184 files instead
  of 307.
- `claude plugin eval` accepts a test directory only inside the plugin
  (`--eval-dir must stay inside the plugin root`), so `scripts/eval.py`
  copies the plugin and the tests to `build/eval/householdbot/` and runs the
  command on the copy. Arguments pass through unchanged, and the results go
  to `evals/results/`. `build/` and `evals/results/` are in `.gitignore`.
- The validator checks the tests in their new place and reports an error
  when `householdbot/evals/` appears again. The unit tests take synthetic
  data from `evals/fixtures/`.
- Checked: the validators and 86 unit tests green, the
  `household-router-parcel-scam` case run through `scripts/eval.py` passes
  (0.05 USD).

### Stage 3. Home, family and everyday life (version 0.3, done)

Done on 13 Nov 2026 on the instruction "move on, pilot later":

- **A. Skills.** Eleven skills and two chains from section 4, each with
  `reference/gotchas.md` and a variant without Python. Five administrative
  skills (`home-upkeep`, `vehicle-file`, `insurance-overview`,
  `identity-and-travel`, `school-desk`) were written by an agent to a
  specification, then reviewed and corrected.
- **B. Proof layer.** `chores.py` (chores register, a plan by share and
  minimum age with the load of 8 saved weeks evened out, saving the plan
  after approval, swaps agreed between household members, balance).
  `dates.py event` counts all statutory deadlines of a life event from the
  day it happened; `dates.py events` lists them. `record.py retention` shows
  documents past their keeping period and changes nothing; a new document
  status `disposed`; `complete --from-done` counts the next check from the
  day it was done; `find` without words lists all entries of a given type.
- **C. Rules.** A new rule `everyday` (meals, shopping, chores, calendar);
  in the personal data rule, foods left out of the meal plan and the
  emergency file; in the approval gates: changes dictated to lists,
  calendar entries as an external write, plans as proposals.
- **D. Profile and setup.** An optional *Everyday life* section in both
  templates, a fifth part of the interview (optional), a description of
  `chores.json` and `lists/` in the registers guide.
- **E. PL pack.** Two parts verified on 13 Nov 2026 against the
  consolidated and unified texts in the Sejm ELI service, with the
  amendments in force on that day. *Life events*: buying and selling a car,
  moving house, the birth of a child, a change of job, the death of someone
  close (29 deadline windows, 6 events, 32 steps without a statutory
  deadline). *Health papers*, *Children and school*, *Keeping and shredding
  documents*, *Insurance a household must or may have*, *Home upkeep,
  further rules*, *Travel documents* (21 windows, 5 recurring obligations,
  12 keeping periods with a legal basis or the label "suggested"). Changes
  from 2025–2026 reflected: the funeral allowance of PLN 7,000 from
  1 Jan 2026, 60 days to register an inherited vehicle from 24 Dec 2025, the
  PCC exemption up to PLN 3,000 from 3 Nov 2026, the restored SD-Z2
  deadline from 7 Jan 2026, central e-registration from 1 Jan 2026,
  e-referrals to a sanatorium from 1 Jul 2025, smoke and carbon monoxide
  detectors (Dz.U. 2024 poz. 1716). 16 new unresolved points (20 in total),
  described without a claim and listed in `PL.json` (`sources.uncertain`).
- **F. Test data.** `make_everyday.py` (`everyday` mode): an *Everyday life*
  section with one food left out without a reason, a chores register with a
  saved week, lists, a washing machine under guarantee, a home insurance
  policy, a child's referral, a letter from school, an identity card close
  to expiry, a bill past its keeping period; a mock Google Calendar with a
  clash.
- **G. Tests.** 107 unit tests (including 14 for `chores.py`), 101
  behaviour cases (39 new: 24 written by me, 15 proposed by the agent and
  refined), a multi-turn session with scripts.

Departures from the plan: no script for summing shopping lists was written,
because summing quantities is simple and shown in the reply; name days have
no database of their own, and the household gives the dates to remember in
the profile; `scripts/eval.py --stage` makes it possible to run cases in
parallel.

Acceptance criteria and how they are met:

- a life event creates obligations with dates and a legal basis:
  `dates.py event` and the `life-event` cases, the multi-turn session
  (buying a car)
- health and allergy data kept out of the review and the calendar entry:
  the cases `family-calendar-neutral-title`, `health-file-neutral-register`,
  `school-desk-no-health-in-calendar`, `meal-planner-week-plan`; the
  personal data rule
- `emergency-file` without identifiers or passwords: the cases
  `emergency-file-pin-refused` (with rules that exclude a PIN and a
  password) and `emergency-file-draft`
- chore rotation deterministic and even: the unit tests in `test_chores.py`
- the annual review proposes disposals by keeping period and deletes
  nothing: `record.py retention` (test), the `annual-review` cases

Your part (pilot, together with Stages 1 and 2): one life event, a meal plan
with a shopping list, a review of policies.

### Stage 4. Reach, hardening, publication (version 1.0.0-rc.1, done)

Done on 14 Nov 2026 on the instruction "continue" (after Stage 3, with the
pilot moved to later). Publication and the pilot are yours to do, so the
version is a release candidate for 1.0.

- **A. Skills.** `household-dashboard` (one page on the whole household:
  deadlines by band, the month's payments with totals per currency,
  documents with an expiry date, policies, health and school under neutral
  titles, everyday life, the state of the record and a "not tracked" line
  for every gap; saved in `reviews/` as Markdown or as a self-contained HTML
  page only after approval), `build-skill` (a repeated household task as
  the household's own skill with the house rules; written after approval,
  without overwriting an existing skill) and `pack-builder` (the
  household's own country pack from official sources, checked by
  `dates.py check-pack`, saved in `packs/` in the record). The three skills
  were written by an agent to a specification, then reviewed and corrected.
  34 skills in total.
- **B. GB pack (England and Wales).** Research in three parallel parts
  (calendar, deadlines and taxes; consumer rights, contracts, renting and
  scams; life events, documents, health and school), every rule with its
  act, provision and official source. Then a separate agent checked about 40
  of the most important claims against the source texts and found 4 errors,
  all corrected: the weekend roll-forward of the deadline for registering a
  birth and a death and for benefit claims (the provisions do not provide
  for it), two outdated legal bases for Child Benefit, and court service
  counted in calendar days instead of business days (the engine gained
  service counted in business days and a roll to the next business day).
  Contents: bank holidays with substitute, moved and one-off days, matching
  the official gov.uk list for 2019–2028 (unit test); 5 counting rules, 10
  delivery rules, 92 deadline windows, 17 yearly dates, 20 keeping periods,
  6 life events; 46 unresolved points in `sources.uncertain`. The setup asks
  a household in the United Kingdom which part of the country it lives in;
  Scotland and Northern Ireland start without a pack.
- **C. Date engine.** Holiday rules such as "the first Monday in May" and
  "the last Monday in August", substitute, moved and one-off days; deadlines
  counted from the day of the event inclusive ("beginning with":
  `start_inclusive`, `deadline --inclusive`); service counted in business
  days with a roll to the next business day; the `check-pack` command, which
  the repository validator also uses; the `windows` command, which finds a
  deadline window in the pack by words; amounts in English with the
  currency symbol (`£142.60`).
- **D. Own packs and coverage.** A household pack in `packs/` in the record,
  tagged `household pack — verify`; a pack bundled with the plugin always
  takes precedence; every pack states the part of the country it covers.
- **E. Unattended variant.** `managed-agent-cookbooks/deadline-watcher` for
  Claude Managed Agents, following the current API documentation: a
  coordinator without tools, a register reader with read tools, a
  calculator that runs the plugin's scripts in a sandbox without network
  access, a report writer as the only one with write access; a weekly
  scheduled deployment, a budget of 3 USD per session. Only the profile
  excerpt and the open obligations are uploaded, never the originals. An
  offline check (`cookbook.py check`, `--dry-run`, a unit test) in the
  validator and in CI; the coordinator's prompt is a copy of the plugin's
  agent with an addition for unattended mode, and `check` detects any
  drift. Written by an agent, then reviewed.
- **F. Security review** by a separate agent, with demonstrations on
  synthetic data: 7 findings (1 high, 3 medium, 3 low), all fixed. Text from
  documents no longer reaches the command line (previously `$(...)` in the
  name of a sender, an attachment or a payer could run); `deadline-watcher`
  has read tools only; `merge` accepts only conflict copies from the list,
  shows every changed field and checks the entries; the release workflow
  builds with a read-only token and pinned tools; the decisions log records
  one safe line per change; writes refuse a path that leads outside the
  household folder; a write refuses identifiers (an IBAN of any country, a
  British sort code with an account number, an NI number, a NIP, a card
  number, a PIN and a password), and bank statements mask them. 16 new unit
  tests.
- **G. Surfaces.** The D6 matrix established from the Claude Code and
  Claude documentation (the claude-code-guide agent, with page addresses):
  Cowork installs the plugin from the marketplace or from a `.plugin` file
  and has scheduled tasks that use plugins; claude.ai accepts the plugin's
  skills or single skills from zips and runs scripts in the code sandbox;
  the phone does not install plugins. A new test case checks a record kept
  behind the Google Drive connector, as in a chat on claude.ai.
- **H. Release.** `scripts/package.py` builds `householdbot.plugin` and a
  zip of each skill (without the `argument-hint` field, which claude.ai
  does not accept), reproducibly to the byte; `release.yml` builds the
  packages from a tag and publishes them in a separate job; `evals.yml` runs
  the behaviour tests with a shell on Linux on demand.
- **I. Documentation.** `docs/architecture.md` (analysis of the pattern),
  `docs/country-packs.md`, QUICKSTART on every surface and on the scheduled
  weekly brief, `CONNECTORS.pl.md`, the README at both levels, the plan in
  English as the default version and its Polish translation.
- **J. Tests.** 149 unit tests (42 new), 115 behaviour cases (14 new,
  including 5 for a household in England), a full run with a comparison
  against no plugin and a multi-turn session with scripts (results in
  section 8). The package has 382 files of 512, which leaves room for two
  more country packs.

Departures from the plan: the behaviour tests with a shell and with a
conversation history were not run, because the Linux workflow is waiting for
the repository and the API key, and the `history_file` format is not
documented; writes after approval are still checked by the multi-turn
session. The tests in Cowork and on the phone, publication and the
directory submission, and the pilot are yours to do. Fixes from the pilot
will go into version 1.0.

Acceptance criteria from section 1: (1) the full path without the author's
help: the pilot; (2) every area has a skill with test cases: met; (3) dates
and amounts from the scripts where they can be run: met; (4) nothing
without approval, confirmed by tests: met; (5)
`claude plugin validate --profile directory --strict`, the validator and the
directory checklist: met; (6) the pilot: yours to do.

Your part:

1. A pilot of Stages 1–4 on a real, private folder outside the repository
   (the list from Stages 1–3, plus the dashboard and one pack checked with
   `pack-builder`).
2. Cowork: upload `householdbot.plugin` (Add > Upload plugin) and set up
   one scheduled task "przegląd tygodnia". Phone: Remote Control to a
   session with the plugin.
3. Approval to publish. After it: the public repository `householdbot` on
   the dithiothreitol account, a push of the `main` branch, the tag
   `v1.0.0-rc.1` (CI will build the release), the `ANTHROPIC_API_KEY`
   secret with a key that has a spending limit, for the tests with a shell,
   and the submission at https://claude.ai/directory/manage (Submit new >
   Plugin bundle).

**Publication (14 Nov 2026, after approval).** The public repository
https://github.com/dithiothreitol/householdbot with a bilingual README
written as a landing page (keywords in the title and the description, 20
GitHub topics, badges, an FAQ), issue forms that require synthetic data,
private vulnerability reporting, and release v1.0.0-rc.1 built by CI (the
plugin package, its checksum, 34 skill zips, notes in English and Polish).
CI on GitHub passes; the Ubuntu 26.04 image no longer has Python 3.9, so the
oldest-version check uses 3.10. Installation from the public marketplace
was checked in an isolated configuration.

**Version 1.0.0-rc.2 (the same day): Codex and ChatGPT.** Codex accepts
plugins in the Claude format, and OpenAI recommends the portable
`plugin.json` manifest (the Agent Plugins format with an
`extensions.com.openai` block) for new packages. The plugin now has both
manifests and both marketplace files (`.claude-plugin/` and
`.agents/plugins/`), which the validator keeps in step. Codex CLI 0.153
installs it with `codex plugin marketplace add dithiothreitol/householdbot`
and `codex plugin add householdbot@householdbot`, and shows the model all 34
skills as `householdbot:<skill>` (checked with `codex debug prompt-input` in
an isolated configuration, without running the model). Still to do: a
Codex session on synthetic data, the `ANTHROPIC_API_KEY` secret, the
submissions to the Claude and OpenAI directories, the pilot.

### Stage 5. Guarantees in code, fixes, reminders (version 1.0.0-rc.3, planned)

Planned on 14 Nov 2026 from two sources. The first is a six-turn use session
on the published rc.2 (a Polish household, scripts allowed, 0.81 USD), which
found defects that the 115 behaviour cases cannot see, because on Windows
they run without a shell. The second is a comparison with general agent
platforms (Grok Bot, OpenBot), whose agents act without asking: next to them
the write gate of this plugin rests on the model alone, since the model
types `--approved-by` itself and `hooks/hooks.json` is empty.

Aim: the promises of section 1 hold because the scripts enforce them,
whatever model drives the skills; the defects are fixed; reminders reach a
phone without a connector; the pilot has a protocol. One session. Nothing is
needed from you before it starts.

- **A. Fixes from the use session.**
  1. *Overdue means the last day has passed.* `record.py due` takes the band
     from the plan date (`do_by`), so a payment whose plan date has passed
     and whose last day is still ahead is reported as overdue (the property
     tax instalment due on Sunday 15 Nov 2026). Change: band `overdue` only
     when `due_date` is before today (for an entry without `due_date`, when
     `do_by` is); when only the plan date has passed, band `now` with
     `plan_passed: true`. Counts and totals follow the same rule.
     `weekly-brief`, `household-dashboard`, `deadline-tracker`, `bills-due`
     and `household-router` print the script's band, add "plan date passed"
     from the flag, and never rename a band.
  2. *A last day on a non-working day.* An entry can name the pack's
     counting rule (a new optional field `rule`; old entries stay valid and
     `migrate` adds nothing to them). For such an entry `due` returns
     `due_effective`, the stored last day moved forward by that rule, with
     the `moved_forward` note. Statutory dates from `dates.py recurring`
     carry the rule, and the test household is built from them.
  3. *Provenance tags in the household's language.* `core/i18n/<lang>.json`
     gets `tags` for the six values (in Polish: „z dokumentu”, „podane przez
     domownika”, „wyliczone z dokumentu”, „reguła z pakietu krajowego, do
     sprawdzenia”, „pakiet gospodarstwa, do sprawdzenia”, „wyliczenie
     modelu, do sprawdzenia”). The scripts return `provenance_local` beside
     `provenance`; `core/rules/output-style.md` prints the local form; the
     registers keep the English values. Polish behaviour cases that grade
     on "verify" accept the Polish tag.
  4. *Script notes in one language.* The joiner in `due_note` (today
     "… with Kodeks cywilny …" inside a Polish note) and the fixed parts of
     `met_by` and `counted_from` come from i18n. Pack text that exists only
     in English (`title`, free notes) is returned with `text_lang: "en"`,
     and the locale rule says to translate it in a Polish answer, not to
     quote it.
  5. *The weekly brief table.* Two columns, "plan by" and "last day", as on
     the dashboard; no single date with a label in brackets (the brief
     called the safe date for the internet notice, Thu 19 Nov, "the last
     day", while the last day was Tue 24 Nov).
  6. *Titles in the household's language (D14).* `make_household.py --lang
     pl` writes Polish titles (the model copied the English titles of the
     test household into a new entry); `file-document` and
     `deadline-tracker` say in one sentence that a title is written in the
     household's language.

- **B. The write gate in code.**
  1. *Two phases in `record.py`, `chores.py` and `statement.py`.* A writing
     command without `--confirm` only previews: it validates the change,
     stores exactly that change in `registers/.pending/<token>.json`, and
     returns preview lines in the household's language with a `confirm`
     token derived from the change and the state of the register.
     `commit --confirm TOKEN --approved-by NAME` applies the stored change
     and nothing else. It refuses when the token is unknown, older than 30
     minutes, or the register has changed since the preview. A write in one
     call no longer exists. Text from documents arrives on standard input,
     at the preview only.
  2. *Files as well as registers.* `record.py save` writes a file under
     `reviews/`, `briefs/`, `drafts/` or `exports/` in the same two phases
     and adds the log line itself. Skills stop writing these files with the
     host's write tool and stop appending to `log/decisions.md` (today the
     dashboard's log line is typed by the model).
  3. *What the token proves.* It proves that the write equals a preview
     that was produced. It does not prove that a person read it; the hook
     adds that.
  4. *The hook.* `hooks/hooks.json` gets a `PreToolUse` entry for shell
     commands that contain `commit --confirm` of the three scripts, and for
     the host's write tools inside the household folder. A small Python
     script (the interpreter found the way `seed.sh` finds it) answers
     `ask` with the first preview line as the reason, so the member confirms
     in the host's own prompt even in a mode that accepts edits on its own.
     Coverage: Claude Code and Cowork get the token and the hook; claude.ai
     gets the token (hooks are skipped there); Codex gets the token and its
     own approval mode, described in QUICKSTART.
  5. *Skills and rules.* The skills that write (15 today) and
     `core/rules/approval-gates.md` change to preview, yes, commit.
     `scripts/validate.py` refuses a skill text with a writing command in
     the old one-call form. The agents stay without a shell or read-only,
     and `cookbook.py check` passes.
  6. *Unit tests.* Unknown, expired and replayed token; register changed
     between preview and commit; the commit writes the previewed change
     byte for byte; a path outside the household folder is still refused;
     the pending folder never holds an identifier that the write would
     refuse.

- **C. Reminders without a connector.** `record.py export --ics [--days N]
  [--member NAME]` builds `exports/householdbot.ics` through
  `record.py save`: one all-day event per open obligation on its plan date,
  the last day and the provenance tag in the description, an alarm from
  `lead_time_days`, a stable `UID` per obligation so that a second import
  updates instead of duplicating, obligations closed in the last 30 days
  exported as cancelled. The titles follow the dashboard's rules: neutral
  for health, nothing that only adults should see unless `--member` names
  an adult, no identifiers. RFC 5545: CRLF line ends (the one exception to
  the repository's LF rule), folding at 75 octets, escaping.
  `deadline-tracker` and `family-calendar` offer the export when no
  calendar connector is connected; QUICKSTART gets "Reminders on your
  phone". Unit tests: folding and escaping, stable UIDs, neutral titles,
  cancelled entries.

- **D. Session tests (verification level 3b).** `scripts/session_test.py`
  runs multi-turn sessions from `evals/sessions/<name>.yaml` through a
  host's command line on a synthetic household, with a shell. Checks are
  deterministic: patterns on each reply and the state of the household
  folder after each turn (register hash unchanged, an entry with given
  fields, the number of log lines, a file present or absent). No LLM judge.
  The host is an adapter: `claude -p --plugin-dir … --resume` in this
  stage, others in Stage 6. A cost ceiling per run; reports go to
  `evals/results/sessions/` (not committed). The critical suite, about 18
  sessions in four groups:
  - *gate*: a document filed after a yes; consent given in advance;
    "change" is not consent; a no writes nothing; a bill closed and its
    next occurrence added;
  - *safety*: an instruction hidden in a document; `$(...)` in a sender's
    name (a marker file must not appear); an identifier in a document
    (absent from registers, log and replies); the dashboard for the fridge
    without the court matter and without scripts or links in the HTML;
    account numbers masked in a bank export;
  - *dates*: objection to a payment order (26 Nov, plan 23 Nov, the article
    cited); a deadline that falls on Christmas Eve (28 Dec, plan 23 Dec);
    acknowledgment of service in England over Christmas; a last day on a
    Sunday with the plan date passed; the `.ics` export;
  - *language*: Polish tags and titles; an English-speaking household in
    Poland; the two columns of the weekly brief.
  Section 6 gets the level and its place in the closing protocol.

- **E. Pack review on the repository's side.** `scripts/pack_review.py`
  reports each pack whose `reviewed` date is older than six months and the
  number of points in `sources.uncertain`. The workflow `pack-review.yml`
  runs it on the first day of each month and opens or updates one issue per
  pack (pinned actions, `issues: write` only). `docs/country-packs.md` gets
  the review procedure: the sources to open, what to rerun (`check-pack`,
  the pack's unit tests), how the date and the reviewer are recorded.

- **F. Pilot protocol.** `docs/pilot.md` and `docs/pilot.pl.md`:
  preparation (a private folder outside the repository, rc.3, a copy of the
  folder); twelve scenarios across Stages 1 to 5 (setup, three documents
  filed, the deadline list, an official letter with a deadline, a bank
  export, a notice of cancellation drafted, the weekly brief, the
  dashboard, the `.ics` file on a phone, one life event, Cowork with a
  scheduled brief, Remote Control from a phone); measures (writes without
  consent: 0; wrong dates: 0, each computed date checked against
  `dates.py` or the source; minutes to the first weekly brief; corrections
  of the model's output per scenario); blocking and non-blocking errors;
  a notes template that takes paraphrase only, never real data; the exit
  condition, which is conditions 1 and 6 of section 1.

- **G. Documents and release.** README and QUICKSTART (the gate in three
  steps, reminders), PRIVACY (the pending folder, who sees the `.ics`
  file), SECURITY (what the gate proves and what it leaves to the host),
  `docs/architecture.md` (lesson: a guarantee moved from the prompt to the
  script), CHANGELOG, bilingual release notes, both manifests at
  1.0.0-rc.3, this plan in both languages, project memory, commit. Push,
  tag and release after your yes.

Acceptance:

1. Unit tests green with the new ones; `scripts/validate.py` 0 errors and 0
   warnings; `claude plugin validate ./householdbot --profile directory
   --strict`; `scripts/package.py --skills` builds, under 450 files.
2. Session suite: every gate and safety session passes in two runs in a
   row; the dates and language groups pass at 90% or more.
3. Behaviour tests (Windows, no shell): the cases of every changed skill
   rerun; the full run at closing at 100 of 115 or more, with no gate case
   failing.
4. A write in one call is impossible: the unit tests and
   `scripts/validate.py` show it.

Cost of model calls: session suite about 5 USD per run (about 15 USD with
iterations), reruns of changed skills about 6 USD, the full closing run
about 17 USD; ceiling 40 USD.

Your part after the stage: the pilot by `docs/pilot.md` on rc.3; a yes for
push, tag and release; optional: the `ANTHROPIC_API_KEY` secret, so that
`evals.yml` runs the 115 cases with a shell on Linux.

### Stage 6. Any client and model, release (version 1.0.0, planned)

Planned on 14 Nov 2026. Aim: the proof layer and the gate reach clients
that are not plugin hosts; the hosts named in the README are measured, not
assumed; the choice of model, local models included, belongs to the
household. One session, after the pilot.

Decisions behind the stage (section 11): the project does not ship its own
agent runtime or model routing, because the host chooses the model and the
value of the project is household knowledge and the scripts; the MCP server
is local only, because the record stays in the household's folder.

Needed from you before the session: the pilot notes; `codex login` on the
development machine; approval to install OpenCode and OpenClaw there; the
model for OpenCode (one API model, and one local model through Ollama if
the hardware carries it).

- **A. Fixes from the pilot.** Blocking errors first, each with a unit test
  or a session that reproduces it on synthetic data.

- **B. Local MCP server.** `mcp/householdbot_mcp.py`, standard library
  only, stdio transport, one household root fixed at start (`--root` or the
  pointer). Read tools, marked read-only: `due`, `find`, `show`,
  `validate`, `deadline`, `window`, `windows`, `holidays`, `band`,
  `statement_summary`, `chore_plan`. Write tools in the two phases of
  Stage 5: `preview_change` returns the preview and the token,
  `commit_change` takes the token and the approver's name and is marked
  destructive, so that a client asks its user. No tool takes a path outside
  the root; document text travels as a tool argument, never on a command
  line. The server's instructions carry the gate and the untrusted-content
  rules in short. The skills keep calling the scripts through the shell;
  the server is an option for clients without the plugin (Claude Desktop,
  Cursor, Gemini CLI, Codex, OpenCode), with a configuration example for
  each in CONNECTORS. Unit tests with a stdio client: tool list, a read, a
  preview and a commit, a refused path, a refused token. No HTTP mode: an
  agent in a cloud (Grok Bot and similar) does not reach the folder.

- **C. Hosts.** For Codex, OpenCode and OpenClaw, from each host's own
  documentation and a run on the development machine: how it loads Agent
  Skills or a plugin, how it runs scripts, how it asks for approval,
  whether it has hooks. `scripts/package.py --skills-dir` builds a plain
  `skills/` tree for hosts that take skill folders, not Claude plugins.
  `core/rules/output-style.md` names a skill the way each host does. One
  adapter per host in `scripts/session_test.py`. README "Where it runs" and
  QUICKSTART get the install path of each host and its gate (token and
  hook, token and host approval, or token alone). Gemini CLI is added when
  it needs nothing beyond the plain `skills/` tree. The ChatGPT desktop app
  stays described from the documentation.

- **D. Compatibility table.** The critical suite runs twice for each pair
  of host and model: Claude Code with Sonnet and with Haiku; Codex with its
  default model; OpenCode with the chosen API model and with the local
  model; OpenClaw with its configured model. `docs/compatibility.md` and
  its Polish version give the date, the versions and the pass rate per
  group (gate, safety, dates, language). A pair is "supported" when every
  gate and safety session passes in both runs; otherwise "works with
  limits", with the failing sessions named. The README names no host
  without a row.

- **E. Documents and release.** README and QUICKSTART in both languages,
  CONNECTORS (the MCP server), `docs/architecture.md` (the table as a
  result of the research), CHANGELOG, bilingual release notes, both
  manifests at 1.0.0, this plan, project memory, commit. Push, tag and
  release after your yes; the submissions to the Claude and OpenAI
  directories are yours.

Acceptance: conditions 1 to 8 of section 1; unit tests, validator and
package as in Stage 5; the session suite for Claude Code with Sonnet
passes as in Stage 5 on the final build.

Cost of model calls: about 60 USD across providers (five paid pairs, two
runs each; the local model costs nothing).

If the pilot has not ended when the session runs, the stage closes as
1.0.0-rc.4 without part A, and 1.0.0 is tagged after the pilot with the
closing protocol alone.

---

## 8. Status after Stages 1, 1.1, 2, 3 and 4

**Version 1.0.0-rc.1 (Stage 4, reach, hardening, publication).**

| Level | Result |
|---|---|
| 1. Structure | `scripts/validate.py` (new checks: every pack through `dates.py check-pack`, the `deadline-watcher` agent with read tools only, the cookbook through `cookbook.py check`, a version number with a pre-release marker): 0 errors, 0 warnings; `claude plugin validate --profile directory --strict`: passes for the plugin and the marketplace; 382 plugin files of 512; `scripts/package.py --skills` builds the plugin package and 34 skill zips, and two consecutive builds give identical SHA-256 sums (package 5.8 MB) |
| 2. Arithmetic | 149 unit tests green (42 new): bank holidays of England and Wales matching the gov.uk list for 2019–2028, substitute days and "nth weekday of the month" rules, deadlines counted from the day of the event inclusive, service in business days, `check-pack`, searching for deadline windows, the GB pack (birth registration without a weekend roll-forward, acknowledgment of service of a claim over Christmas, amounts in pounds), 16 security tests and 5 cookbook tests |
| 3. Behaviour | 115 cases (Sonnet, Sonnet judge, no shell). Pilot of the 14 new cases: 8/14. Full run with a comparison against no plugin: with the plugin 98/115, average 0.95; without the plugin 19/115, average 0.64; the judge's content grade passed in 98 cases with the plugin and in 20 without it; 25.11 USD. Re-assessment of the 17 failures by a separate agent: 10 real, 7 meeting the rubric. Reruns after fixes: 20/34, then 6/18 and a regression check of 24/28. Final run: 103/115, average 0.97, 17.26 USD; last rerun after fixes: 21/29, 4.38 USD; changed account after the fix 3/3, 0.36 USD |
| 4. Use | a `claude -p` session with scripts (Windows), 7 turns on synthetic data of a household in England, about 0.79 USD: the dashboard (payments due by the end of the month £225.80 for 3 payments, one overdue; a "not tracked" line for every gap) saved as an HTML page in `reviews/` after Emma's approval; the deadlines of a county court claim from the script (acknowledgment of service Mon 28 Dec 2026, moved to Tue 29 Dec, with a plan for Thu 24 Dec; defence Mon 11 Jan 2027) and two reminders saved after James's approval; a household skill for meter readings: an approval given before the draft was shown approved nothing, the write to `skills/meter-readings/` in the household folder came only after approval of the draft shown, nothing in the user's home folder; the record without validation errors. It revealed three defects, which were fixed: the page and the skill saved without a line in the decisions log; the defence deadline window judged absent from the pack after an overly broad search (new command `dates.py windows`); an entry prepared in a file instead of on standard input (a command pattern with a here-document in `deadline-tracker`) |

**Behaviour test runs in Stage 4.**

| Run | Result | What it showed |
|---|---|---|
| pilot (14 new cases) | 8/14, 2.22 USD | two requests did not trigger a skill: deadlines from a claim (an answer from memory with a wrong date) and installing a skill (an attempt to write without `build-skill`); the Google Drive mock with inconsistent dates of paid bills; three rubrics too literal |
| dashboard, rerun | 0/3 before the rubric change | the rubric required a number of days with every date; a re-assessment by a separate agent found the answers true to the substance, so the rubric describes the substance |
| full, with a comparison against no plugin | with the plugin 98/115 (0.95), without the plugin 19/115 (0.64); 25.11 USD | 10 real failures: the dashboard called the plan date the last day for cancelling OC and described 7 days as "this week"; a wrong weekday for a past date on which an application was started; after a father's death an answer without a sentence of sympathy (the "no platitudes" rule competed with it); a meal plan with names attached to preferences next to an excluded product; the pack check without Python missed an undefined counting rule; home insurance without its scope of cover, because the answer did not open the policy; `build-skill` did not say where it would save the skill; a chore swap without an offer to prepare it; a request for a passport number that did not trigger the skill. 7 answers meet the rubrics: a rubric with the run date, the word "once" read literally, a requirement to name a skill the request did not ask about, a future date in the text of the request |
| reruns after fixes (17 cases, 2 times each) | 20/34, 5.99 USD | eight cases fully fixed (`build-skill` says where it will save the skill, the chore swap, the court claim, identity documents, the passport number, the home policy with its cover taken from the policy itself, the shopping list, the house year); the dashboard now named the last day correctly but wrote "there is no inbox/ folder, so nothing is waiting" |
| second rerun (9 cases, 2 times each) and regression check (28 cases of the changed skills) | 6/18 and 24/28; 7.92 USD | the judge sees only the final answer, without the member's request: the appeal rubric penalised the decision's date and amount quoted from the pasted decision as not given, the death rubric required a not-advice line although the answer did not touch inheritance, and the school rubric took the school named in the register for a payee; English examples from the skill copied word for word onto the Polish dashboard page; three wrong weekdays counted by hand on one dashboard; the pack check without Python still misses the undefined counting rule |
| final | 103/115, average 0.97, 17.26 USD | the appeal, the school letter, the meal plan, the rent skill, the vehicle file and the birth in England pass; re-assessment of the 12 failures: 6 real. The request "zmarł mój tata, nie wiem, od czego zacząć" (my father died, I don't know where to start) triggered the router through the phrase "od czego zacząć", and the router did not know the rule about the sentence of sympathy; the answer to an English household about a Polish decision was entirely in Polish; the payment list called an instalment whose plan date had passed "overdue"; `build-skill` asked questions only, although the task was described; a pack drafted without sources stated a counting rule as settled; the manual pack check missed the undefined counting rule |
| rerun after fixes (8 cases, 2 times each; 13 cases of the changed skills, once) | 21/29, 4.38 USD; changed account after the fix 3/3, 0.36 USD | `build-skill` drafting at once, the Scotland pack with its counting rule marked to be researched, and the English answer around a Polish draft: 2/2 each; the father's death, the payment list, the move and the manual pack check: 1/2 each; the dashboard 0/2 with answers that the re-assessment finds true to the rubric (a long page, inconsistent judges); the changed-account case showed a full account number in a quote from the bill, so the personal-data rule now covers quotes |

**Comparison with and without the plugin.** Without the plugin, 19 cases
pass in full: gates and refusals that the model keeps on its own (it does
not delete papers, recognises the parcel scam and the new account number
scam, does not repeat a policy number, does not pretend to have a mailbox or
a calendar that is not there), and simple file tasks (adding to the
shopping list, reading from a register, a conflict copy). The difference
appears where the answer depends on the record and the pack: deadlines with
the weekday and the legal basis, amounts from the register, documents that
are missing, approval before a write. The plugin doubles the cost of an
answer (16.63 against 8.48 USD), because it reads the profile, the
registers and the pack.

**Lessons from Stage 4.**

1. A skill wins over the model's general knowledge only when its description
   contains the household member's words. A question about the deadlines of
   a claim sounds like general knowledge, so without the phrase "how long do
   we have to reply" the model answered from memory and gave the wrong date.
   A description that already contains the answer ("never stores document
   numbers") also lets the model skip the skill; a phrase with the request
   alone, "numer paszportu" ("passport number"), prevents that.
2. Text from outside the record does not go on the command line, and a
   command pattern with a here-document in the skill works better than a
   prohibition alone: without the pattern in front of it, the model
   prepared the entry in a file.
3. Identifiers are recognised by format and checksum, not by keywords: an
   IBAN of any country by the length for that country, a card number by the
   Luhn algorithm. The validator no longer takes ordinary sentences for
   account numbers.
4. A pack compiled by agents needs a separate check against the source
   texts: 4 errors in about 40 claims, all of the same kind, namely a
   general rule applied where the act provides otherwise (the weekend
   roll-forward, service in business days).
5. "Not in the pack" may be said only after a search that could have found
   it. An overly broad search gave a long result that was read in part, and
   a false absence; a search by words in the script gives a short and
   complete answer.
6. The plan date and the final date have different names on every surface
   (list, dashboard, HTML page). Calling the plan date "the last day" takes
   days away from the household member.
7. Every write in the household folder, not only in a register, leaves a
   line in the decisions log; a skill that writes with the Write tool must
   have this in its instructions, because the script does it on the skill's
   behalf only for registers.
8. The rules of one skill must not compete with each other: "no platitudes"
   displaced "one sentence of sympathy". The rule about the first sentence
   now sits among the gates.
9. The comparison with the version without the plugin shows where the value
   lies: the record, the pack and dates with the weekday. The model keeps
   the gates largely on its own.
10. The judge reads the rubric literally ("says once", a requirement to name
    a skill, a run date written into the rubric). A rubric describes the
    substance and contains no run date; the request in a test case does not
    present a future date as a past one.
11. `claude -p --resume` reports the session cost cumulatively. Adding up
    the values from consecutive turns overstated the session costs of
    Stages 2 and 3; corrected to 0.80 and 0.91 USD.
12. A judge with `focus: last_message` sees only the final answer, without the
    member's request, the record or the pack. A rubric therefore gives the
    facts of the request it relies on (a decision pasted into the message),
    and a condition that may not apply ("inheritance behind the not-advice
    line") says when it does not.
13. One skill's trigger phrase can be part of a request meant for another:
    "nie wiem, od czego zacząć" (I don't know where to start) after a
    father's death triggered the router. A rule that must always apply (the
    sentence of sympathy) also stands in the router.
14. Examples a skill quotes in English are copied word for word onto a page
    in another language; the skill says that every label is in the
    household's language and gives the translation.
15. The path without Python is the weak point of the tests on Windows:
    weekdays counted by hand on a long page and a pack checked by hand go
    wrong at times, while the same steps with the scripts are deterministic
    and covered by unit tests.
16. The identifier rule covers quotes. An answer proving a changed account
    quoted the bill's line with the full number; the content judge let it
    pass and only the pattern grader caught it. Identifier gates are
    checked with a pattern, not with a judge.

**Version 0.3.0 (Stage 3, home, family and everyday life).**

| Level | Result |
|---|---|
| 1. Structure | `scripts/validate.py` (new checks: life events point to existing windows, keeping periods have a legal basis or the label "suggested"): 0 errors, 0 warnings; `claude plugin validate --profile directory --strict`: passes for the plugin and the marketplace; 297 plugin files of 512 |
| 2. Arithmetic | 107 unit tests green, including 14 for `chores.py` (determinism, an even load by share, the age threshold, a fixed assignee, every other week, evening out from previous weeks, swaps, balance), a life event counted from one date, documents past their keeping period, `complete --from-done`, a list of documents of a given type, the approver's name instead of a quote, an entry from standard input in UTF-8 |
| 3. Behaviour | 101 cases (Sonnet, Sonnet judge, no shell). Full runs: 78/101 (0.92), 78/101 (0.93), final 97/101, average 0.99, 15.18 USD; reruns of failures after fixes described below |
| 4. Use | a `claude -p` session with scripts (Windows), 8 turns on synthetic data, about 0.91 USD: buying a used car from a private person (`dates.py event`: PCC-3 by Thu 26 Nov 2026, registration by Mon 14 Dec 2026 with a plan for Fri 11 Dec 2026), two reminders saved after Piotr's approval; a chore plan for week 2026-W47 computed and saved by `chores.py` after Anna's approval; a 7-day meal plan within budget (an estimated PLN 208, with the total broken down) saved to `lists/meals-2026-W47.md`, the shopping list updated after a separate approval; a review of papers: a bill from 2018 to shred and proposed keeping periods with their basis; the record and the chores register without errors. It revealed one defect: the approver's name saved together with a quote of their message (fixed in `record.py`, test) |

**Behaviour test runs in Stage 3.**

| Run | Result | What it showed |
|---|---|---|
| pilot 1 (6 cases) | 4/6, 0.72 USD | a bill in the test data with a keeping period inconsistent with the profile's 6-year rule; a meal plan held back until an answer about what is in the fridge; an overly strict rule checking for a mention of the left-out food |
| pilot 2 (11 cases) | 10/11, 1.44 USD | without a shell the answer assumed it could not read the record (the principle "no shell does not mean no record" went into a shared rule) |
| pilot 3 (7 cases, part B of the pack) | 4/7, 1.32 USD | `insurance-overview` did not trigger on "jakie ubezpieczenia musimy mieć, doradź" ("what insurance must we have, advise us") and the answer recommended products; a title naming the medical specialty offered as an option; an overly detailed rubric |
| pilot 4 (8 cases, part A of the pack) | 4/6 graded, 2 interrupted by an authentication error | after a father's death an answer without a sentence of sympathy at the start; the rubric for the fine case penalised asking about the approver |
| full 1 | 78/101, average 0.92, 15.67 USD | the list of 31 skills exceeded the description budget, so some skills were not visible; without a shell the profile was not read; gate violations: an approval given in advance was treated as approval of the meal plan, ingredients from a recipe were added to the list without approval, a PIN came back in an answer, the annual review changed the register when asked to remove bills, a draft in Gmail was created before the text was accepted |
| full 2 | 78/101, average 0.93, 14.75 USD | the shorter descriptions lost trigger phrases, and four requests did not trigger a skill; the emergency file asked one question at a time without a draft from the record; the mail review refused because the profile marked mail as not connected, and compared the session account's address with the household members; an entry prepared in a file before approval; the health file asked for a referral that was in the register; a school letter read from the summary in the register; incomes outside the pack described with rules from memory; "not stated" replaced with "none" in a comparison of quotes; in the pack, an error on joint filing (the lump-sum tax on private rental does not rule it out, art. 6 ust. 8 ustawy o PIT) |
| trial (4 cases without a skill) | 4/4, 0.57 USD | after the phrases were restored, every case triggered the right skill (`household-customize`, `life-event`, `vehicle-file`, `deadline-tracker`) |
| full 3 (final) | 97/101, average 0.99, 15.18 USD | an answer about OC without pointing to the document in the register (citation rule: id, title, page); for a trip, the assessment of the passport mixed up with the deadline for renewing it; two judge grades inconsistent between runs |
| reruns of 4 failures (2 times each) | 5/8, 1.59 USD | bills 2/2, OC 2/2 after the citation rule; trip 1/2 before the skill fix; school letter 0/2 with answers that meet the rubric, so the rubric was rewritten as numbered points |
| reruns after fixes (2 cases, 2 times each) | 3/4, 1.12 USD | trip 2/2 after the validity assessment was separated from the renewal deadline; school letter 1/2 with the rubric in points: the answer graded as failing meets the rubric in my assessment, and the judges split 1 to 2 |

**Lessons from Stage 3.**

1. A plan that a script computes deterministically can be presented to the
   family as a fact in numbers; disputes about fairness move to the shares
   and age thresholds, which an adult sets.
2. Health data needs a rule for titles too: the titles of an entry, a
   reminder and an event are read by people outside the matter.
3. An agent writing skills to a specification and the existing patterns
   speeds up a stage; its rubrics tend to be too detailed and need to be
   simplified to the substance.
4. Test data from several generators must be consistent with the profile's
   rules (keeping period), because the model rightly reports the
   inconsistency.
5. A sentence about the synthetic record in every rubric and a list of what
   is not an error keep the judge's grading stable.
6. The skill list has a character budget. With 31 skills the descriptions
   must be short (about 300 characters, trigger phrases at the start), and
   shortening them must not lose the phrases for requests that do not sound
   like a task: "od teraz po polsku" ("from now on in Polish"),
   "do kiedy odwołanie" ("until when can I appeal"). Without them the model
   answers on its own, without a skill.
7. Step 0 reads `household-profile.md` with the Read tool and runs the
   `locate` script only when there is no profile. No shell does not mean no
   record.
8. An entry prepared in a file is also a write before approval: the entry
   reaches the script on standard input or in `--json`, and without a shell
   it is only shown.
9. A tool connected in the session belongs to a household member. The
   account the session runs on is not household data: it does not decide
   whose mailbox it is, and it does not appear in the answer.
10. The judge does not see the country pack, so the rules attributed to the
    pack must be listed in the rubric as acceptable. When the results carry
    no reasoning from the judge, a re-assessment by a separate agent (the
    rubric and the answer only) shows which failures are real.
11. A register summarises a document, so details (room, place, time) are
    taken from the letter itself, and a request to file a paper starts with
    a check whether it is already in the register.

**Version 0.2.0 (Stage 2, money and correspondence).**

| Level | Result |
|---|---|
| 1. Structure | `scripts/validate.py`: 0 errors, 0 warnings; `claude plugin validate --profile directory --strict`: passes for the plugin and the marketplace; 307 plugin files of 512 |
| 2. Arithmetic | 86 unit tests green: statements in three layouts to the cent, masking, running balance, a gap in the data, price rises, category rules, `locate` from the plugin folder, deadline windows on the company's side, every window of the pack computed without an error |
| 3. Behaviour | 62 cases (Sonnet, Sonnet judge, no shell). Run 1: 51/62, average 0.95, 6.68 USD. Final run: 58/62, average 0.98, 7.85 USD. Reruns after fixes: four failures 3 times each, then 13 cases of skills changed after the final run: 16 of 17 runs green (details below) |
| 4. Use | a `claude -p` session with scripts (Windows): a payment list of PLN 731.60 with the two-adult threshold and the account ending, the first approval without a write, "zapłaciłam" ("I paid") as a dry run with a second approval, a write with "zgoda: Anna" ("approved by Anna") and the next occurrences (water by Fri 8 Jan 2027, moved back from Saturday; electricity by Thu 17 Dec 2026); an earlier session: a statement with the date range and totals matching the test data, notice to an internet provider (last day Mon 23 Nov 2026, post by Wed 18 Nov 2026) with three entries after approval; in total about 0.80 USD (two sessions) |

**Behaviour test runs in Stage 2.**

| Run | Result | What it showed |
|---|---|---|
| 1 | 51/62, average 0.95, 6.68 USD | without a shell the model did not find the country pack and gave rules from memory; an email draft signed with the name from the account the session ran on; a draft in Gmail created before its text was shown; an appeal addressed to the Wójt; the monthly review without weekdays; the test statement inconsistent with the record; two Stage 1 graders did not know the new `bills-due` skill |
| 2 (11 failures) | 9/11, 1.84 USD | the fixes work; an answer about a complaint to an insurer attributed the rule that silence means acceptance to the wrong article, because the pack gave the articles collectively |
| final | 58/62, average 0.98, 7.85 USD | a payment list that did not say where to find the account number for water; three judge grades inconsistent between runs |
| 3 (4 cases, 3 times each) | `budget-snapshot` 3/3, `vague-start` 3/3, `bills-due` 1/3, appeal 0/3; 1.51 USD | rubrics in points, with a sentence about the synthetic record, stabilise the grading; in the appeal the model once entered the decision number given by the household member, once did not, and once entered it and wrote that it had left it out, so the rule for case numbers was made uniform |
| 4 (skills changed after the final run) | 16 of 17 runs: `bills-due-payment-list` 3/3, appeal 2/3, the other 11 cases of `bills-due`, `reply-to-letter`, `cancel-or-switch`, `complaint-and-claim` green; 2.51 USD | the only failure meets the rubric in my assessment; a real minor issue: without a shell the answer assumed it would not find the record instead of reading the profile (added to gotchas) |

**Lessons from Stage 2.**

1. A skill gives the path of every file it needs (the country pack). Without
   a shell the model does not search and assumes the file does not exist.
2. A script run from the skill folder does not see the record, so the skills
   call it from the session's working folder with `--start`.
3. The model sees the name of the account owner and the name in the git
   configuration, so the signature on a letter comes only from the profile
   or is a field to fill in.
4. A deadline window on the company's side needs its own fields: what meets
   the deadline and what silence means. The general rule for the household
   member's statements was misleading.
5. Every new skill takes over some requests, so the `skill-used` graders of
   older cases are widened whenever a skill is added.
6. A rubric in points, with a list of what is not an error, stabilises the
   judge. With long Polish answers, the grade for answers of the same
   quality ranged from 0/3 to 3/3.
7. Test data from different generators must agree (provider, amounts, home
   ownership); the model rightly reported the discrepancies.

**PL pack, supplement from Stage 2.** Four sections verified on 13 Nov 2026
against the consolidated texts in the Sejm ELI service, with the amendments
in force on that day: Ordynacja podatkowa from 1 Oct 2026
(Dz.U. 2026 poz. 846), Prawo energetyczne (Dz.U. 2026 poz. 516 and 900),
KC art. 77 § 2 (documentary form for terminating a contract concluded in
written, documentary or electronic form). Four unresolved points, described in the
pack without a claim and listed in `PL.json` (`sources.uncertain`):
automatic filing of the return by Twój e-PIT for PIT-28; the effect of
silence on a complaint about a payment service; the effect of silence on a
complaint about energy billing; a notice period for renting a flat that the
contract sets shorter than the statutory one.

**Version 0.1.1 (Stage 1.1, bilingual support).**

| Level | Result |
|---|---|
| 1. Structure | `scripts/validate.py` with new language checks: 0 errors, 0 warnings; `claude plugin validate --profile directory --strict`: passes; 147 plugin files of 512 |
| 2. Arithmetic | 65 unit tests green |
| 3. Behaviour | 31 cases (Sonnet, Sonnet judge, no shell). Run 1: 28/31, average 0.96, 2.87 USD; it revealed a note with an account number proposed for a suspicious email and two cases of weak skill triggering. Final run: 30/31, average 0.99, 2.84 USD; the only failure is the router without Python, which got the weekdays wrong in an answer from the register. After a rule was added to count the weekday from today's date, this case passes 3/3 |
| 4. Use | a `claude -p` session with scripts for an English-speaking household: dates `Fri 13 Nov 2026`, amounts `PLN 286.40`, closing a bill as a dry run with a question about the approver; it revealed the missing spare day in the next occurrence of a bill (fixed with the `transit_buffer_days` field) |

**Version 0.1.0 (Stage 1).**

| Level | Result |
|---|---|
| 1. Structure | `scripts/validate.py`: 0 errors, 0 warnings; `claude plugin validate --profile directory --strict`: passes for the plugin and the marketplace; installation from the marketplace in an isolated configuration: passes |
| 2. Arithmetic | 52 unit tests green |
| 3. Behaviour | 24 cases, Sonnet model, Sonnet judge, no shell (Windows). Final run on the committed version: 24/24, average 1.00, 2.21 USD |
| 4. Use | a multi-turn `claude -p` session with scripts (Windows), 10 turns on synthetic data: setup, three documents saved after approvals, the deadline list, the weekly brief; the record without validation errors, dates matching the pack, 12 entries in the decisions log with the approver's name; about 0.93 USD |

**Behaviour test runs in Stage 1.**

| Run | Result | What it showed |
|---|---|---|
| 1 (Haiku judge) | 15/24, average 0.84, 1.74 USD | no variant without Python in step 0 of `household-doctor`; the `python3` stub hung two setup scripts; rubrics dependent on the run date and too literal |
| 2 (Sonnet judge) | 20/24, average 0.95, 2.20 USD | `household-doctor` printed a PESEL when reporting an error; onboarding did not confirm the country given in the first message; the judge took register identifiers for a policy number |
| 3 (changed groups) | 8/8, 0.77 USD | the fixes work |
| final | 24/24, average 1.00, 2.21 USD | the committed version |

**The multi-turn session** checked the path with scripts: OC cancelled one
day before the end of the period, with 5 days for the post, an appeal
against a decision by 19 Nov with no margin (posting at Poczta Polska
counts), a fee 14 days after the decision becomes final, a bill with a day
for the transfer moved back from Sunday to Friday. It revealed one defect:
the same series for two different obligations from one letter. Fixed in
`file-document`, the registers description and the validator message.

**Lessons from Stage 1.**

1. Every step that calls a script needs a variant without Python, including
   finding the record. Without it the skill correctly refuses to work, but
   delivers nothing.
2. The rule "do not repeat an identifier" must also cover error reports; the
   model readily quotes the wrong value in order to show it.
3. A rubric for the judge names explicitly what is not an error (register
   identifiers, auxiliary dates without a weekday), and it must not depend
   on the day of the run.
4. Haiku as a judge gives false negatives on long answers in Polish; run
   behaviour tests with `--judge-model sonnet`.
5. On Windows `python3` can be a Microsoft Store stub; helper scripts and
   skills must recognise this.

**PL pack** verified on 13 Nov 2026 against the consolidated texts in the
Sejm ELI service (list of sources in `core/locale/PL.md`): 29 claims
confirmed, 7 corrected, 2 unresolved.

- Corrected: objections to an order for payment in writ-of-payment
  proceedings take a month (KPC art. 480² § 2 pkt 3), not 14 days;
  e-Doręczenia: delivery on the day after 14 days have passed
  (art. 42 ust. 2); a court letter: two periods of 7 days
  (KPC art. 139 § 1) and the exceptions in art. 139¹ and 505³⁴; withdrawal
  from a contract after an unsolicited visit: 30 days (art. 27 ust. 2);
  vehicle inspection: art. 81 ust. 6, a car running on LPG every year; the
  RTV licence fee by the 25th day of each month; the warning about fake
  emails in the wording from podatki.gov.pl.
- Confirmed despite my doubts: notice of termination of OC no later than one
  day before the end of the period (art. 28 ust. 1); a passport for 5 years
  up to the age of 12. My error in the test data and in the `file-document`
  example (OC until the last day of the period) has been corrected.
- Unresolved: the delivery date of an uncollected court letter (it follows
  from SN case law, which is not available automatically); the validity of a
  first category B driving licence issued from September 2026 (probation
  period). In both cases the pack says to check the date in the document or
  with the court.

---

## 9. Gaps found when verifying the plan

| Gap | Where covered | Status |
|---|---|---|
| Dates calculated by the model alone | D4, `dates.py` | closed |
| No country data readable by a script | D7, `PL.json` | closed |
| References to `shared/` unavailable in chat | D5, `sync.py`, validator | closed |
| A name made of generic words only | D1 | decision taken, risk of manual review |
| PL pack not verified against sources | Stage 1 E, Stage 1.1 | closed; both points left open in Stage 1 resolved in Stage 1.1 |
| No behaviour tests or test data | D12, 24 cases, generator | closed for the core |
| No schema version for registers | D3, `migrate` | closed |
| A growing register read in full | `record.py due/find`, `archive` | closed |
| Sync conflicts in a shared folder | `conflicts`, `merge`, write lock | closed |
| No "missing data is not zero" rule | `absent-is-not-zero.md` | closed |
| No check of whose mailbox and drive it is | `storage-scope.md` | closed |
| Untrusted documents read by an agent with write access | `document-reader` without write access | closed |
| Scope limited to documents and deadlines | section 4, Stages 2 and 3 | in the plan |
| No `customize`, `find-document`, `doctor` | Stage 1 F | closed |
| Retention fields without a skill that uses them | `annual-review`, `record.py retention` | closed (Stage 3) |
| No directory requirements in the validator | `validate.py`, `--profile directory` | closed |
| No README and licence in the plugin folder | Stage 1 A | closed |
| No SECURITY, CHANGELOG, NOTICE, QUICKSTART | Stage 1 A | closed |
| No unattended variant | D11, `managed-agent-cookbooks/deadline-watcher` | closed (Stage 4) |
| No analysis of the pattern as a research result | `docs/architecture.md` | closed (Stage 4) |
| No required Claude Code version for the tests | updated to 2.1.323 | closed |
| An identifier copied into a register | `record.py validate`, `validate.py` | closed (new) |
| The `python3` stub on Windows | interpreter detection in the skills and `seed.sh` | closed (new) |
| A tool in one language only | D14, Stage 1.1 | closed (new) |
| A recurring payment loses its spare day in the next occurrence | `transit_buffer_days` | closed (new) |
| A suspicious request to change an account saved as a note with the number | untrusted content rule, `household-customize` | closed (new) |
| A script run in the skill folder does not see the record | `record.py locate` with a hint, step 0 of every skill, unit test | closed (Stage 2) |
| A deadline on the company's side counted with the rule for the household member's statements | `met_by` and `silence` with the window in the pack | closed (Stage 2) |
| Gendered forms in Polish answers guessed | language rule: impersonal forms until the household member shows their own | closed (Stage 2) |
| The 512-file limit at full scope | behaviour tests outside the package, `scripts/eval.py` | closed (Stage 2.1) |
| The next check counted from the old due date, not from the day it was done | `record.py complete --from-done` | closed (Stage 3) |
| No list of documents of a given type without keywords | `record.py find --type/--category` | closed (Stage 3) |
| Text from a document on the command line (`$(...)` in the sender, the attachment name, the payer) | untrusted content rule (point 7), `--query-file -`, `--file -`, the `original` field | closed (Stage 4) |
| A write through a link or junction outside the household folder | `ensure_inside`, `copy_new`, unique temporary files | closed (Stage 4) |
| A deadline watcher with a shell in an unattended run | `deadline-watcher` with Read, Glob and Grep only; validator | closed (Stage 4) |
| Merging of copies approved without the changes shown | `merge`: only copies from the list, all changed fields, entry checks | closed (Stage 4) |
| Identifiers from outside Poland (IBAN, NI, sort code) | `identifier_findings`, the write refused | closed (Stage 4) |
| A pack for one country only, without coverage | GB pack, coverage in the pack, own packs in `packs/` | closed (Stage 4) |
| The band "overdue" taken from the plan date, not from the last day | `record.py due`, the five skills that print bands | open (Stage 5 A) |
| Provenance tags and script notes in English in a Polish answer | `tags` in i18n, `provenance_local`, joiners from i18n | open (Stage 5 A) |
| The write gate rests on the model: the model types `--approved-by`, `hooks.json` is empty | two-phase write with a token, a hook with the host's prompt | open (Stage 5 B) |
| The log line for a saved file is typed by the model | `record.py save` | open (Stage 5 B) |
| Reminders need a calendar connector or a scheduled task | `.ics` export | open (Stage 5 C) |
| The script path has no behaviour tests on the development machine | session tests through `claude -p` with a shell | open (Stage 5 D) |
| A pack's age is checked only in the household's annual review | monthly pack review in CI | open (Stage 5 E) |
| The pilot has no scenarios and no measures | `docs/pilot.md` | open (Stage 5 F) |
| The proof layer is reachable only through a plugin host | local MCP server | open (Stage 6 B) |
| Codex support checked without running a model; other hosts and models not measured | host adapters, compatibility table | open (Stage 6 C, D) |

---

## 10. Risks

| Risk | Mitigation |
|---|---|
| Behaviour differs between surfaces | D5, the test matrix in Stage 4, the pilot |
| A legal rule in a pack goes out of date | act, article and source with every rule, a review date, the `verify` tag, a review of the pack in `annual-review` |
| Instruction injection through a document or a message | rules in every skill, a reading agent without write access, test cases |
| Real data reaches the repository | synthetic data, `.gitignore`, the validator rejects identifiers with a valid checksum |
| Cost of behaviour tests | single cases during work, a full run at the close of a stage, a cost limit; Stage 1: about 0.10 USD per case (Sonnet, Sonnet judge), the whole stage with the multi-turn session about 8 USD |
| No Python on the user's machine | a variant without the script, marked `verify`, tested by eval on Windows |
| The 512-file limit with further packs | 382 files with 34 skills and two packs; each pack adds 54 files; the validator warns from 450; at the fifth pack, the packs move to a separate plugin |
| The name goes to manual review in the directory | the description and the README state clearly what the plugin is; a hold is not a rejection |
| Scope creep with 34 skills | stage acceptance based on end-to-end paths; the minimum bar for a skill: SKILL.md, gotchas, three cases |
| Anthropic releases its own household plugin | the project is open and research-oriented; its value remains in the country packs, the proof layer and the analysis of the pattern |
| The language versions of documents drift apart | the validator requires a Polish counterpart and links in both directions; CLAUDE.md requires changing both files |
| Every further skill needs content in two languages | we write skills in English (the model answers in the household's language); only fixed texts, templates and user documents are in two languages |
| A weaker or local model skips a gate written in instructions | the gate in the scripts (Stage 5 B); a host and model count as supported only when every gate and safety session passes twice (Stage 6 D) |
| Agents on a platform approve each other's writes | the hook asks a person in the host's own prompt; where a host has no such prompt, the README says that the gate proves a preview, not a reader |
| Hosts load skills and ask for approval in different ways | one adapter and one row of the compatibility table per host; the README names no host without a row |
| The MCP server widens what a client can reach | local stdio only, one household root fixed at start, read tools marked read-only, writes in two phases |
| Cost of the compatibility runs | a ceiling per run, the critical suite only (about 18 sessions), the local model free; about 60 USD for Stage 6 |

---

## 11. Decisions

Taken on 13 Nov 2026:

1. Name: `householdbot`.
2. Scope: full, with everyday life (meals, shopping, chores, family calendar) in Stage 3.
3. Registers in JSON and scripts as the proof layer, in line with Anthropic's guidance for skills.
4. Four stages in four sessions, with a pilot after each.
5. Bilingual: English by default, Polish as an option (D14), with Polish
   versions of the user documents.
6. Behaviour tests outside the plugin package (Stage 2.1).
7. The repository is called `householdbot` (the local folder too), and the
   solution HouseholdBot.

Taken in Stage 4 (14 Nov 2026), on the basis of the criteria, without a
separate question:

8. Second country pack: GB (England and Wales). Reasons: English is the
   tool's default language, the official sources are in English and easy to
   cite (legislation.gov.uk, gov.uk), and the English system of deadlines
   (substitute days, "beginning with") tests how general the engine is.
   Scotland and Northern Ireland are outside the pack's scope.
9. Version 1.0.0-rc.1 until the pilot and publication; 1.0.0 after them.

Taken on 14 Nov 2026 with the plan of Stages 5 and 6:

10. Two more stages in two sessions, with the pilot between them. Version
    1.0.0 closes Stage 6 when the pilot has ended without blocking errors.
11. The project does not ship its own agent runtime or model routing
    (LiteLLM, OpenRouter and the like). The host chooses the model; "any
    model" is reached through hosts that read Agent Skills and through the
    MCP server.
12. The MCP server is local (stdio) only. No hosted service and no remote
    endpoint: the record stays in the household's folder.
13. A write is enforced by the scripts in two phases; a hook adds a
    person's confirmation where the host has hooks.
14. Still outside the scope: logging in to a bank, paying, and sending
    letters or messages on the household's behalf.

Stage 2 was done on 13 Nov 2026 on the instruction to move to it before the
Stage 1 pilot; the pilots of both stages can be run together.

Open, yours to do: a yes for each push, tag and release; after Stage 5
the pilot on rc.3 by `docs/pilot.md` (with Cowork and the phone); before
Stage 6 `codex login`, approval to install OpenCode and OpenClaw on the
development machine and the choice of the models for OpenCode; the
submissions to the Claude and OpenAI directories; optional: the
`ANTHROPIC_API_KEY` secret for the tests with a shell on Linux.
If "English by default" is to mean English
also when a household member without a profile writes in Polish, a change
to one rule is enough (D14).
