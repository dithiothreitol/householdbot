# Changelog

## 1.0.0-rc.3

Guarantees in code, fixes from a use session, reminders on a phone (stage 5).

- **The write gate is in the scripts.** Every writing command of `record.py`,
  `chores.py` and `statement.py` only previews: it checks the change, stores
  exactly that change in `registers/.pending/` and prints the preview with a
  `confirm` token. `commit --confirm <token> --approved-by <name>` applies it
  and nothing else; a token that is unknown, older than 30 minutes, edited,
  or whose files changed since the preview is refused, and so is the old
  one-call form. Several entries of one register go into one preview (`add`
  takes a JSON list, `complete` takes `--id` more than once). `init` takes
  the approved profile (`--profile-file -`), so one yes creates the record.
- **A hook asks a person.** In Claude Code and Cowork a `PreToolUse` hook
  (`hooks/gate.py`) sends each commit, with its preview line and files, and
  each direct write into a household folder, to the host's permission prompt.
- **Files go through `record.py save`**: briefs, pages, lists, packs and
  skills, into `briefs/`, `reviews/`, `lists/`, `packs/`, `skills/`,
  `exports/`, `drafts/` or the profile, with a copy of a replaced file in
  `registers/.history/` and the log line written by the script. A page with a
  script, link, image, form or web address, and any identifier, is refused.
- **Reminders without a connector**: `record.py export --ics` builds an
  RFC 5545 calendar file (stable UIDs, so a newer export updates the same
  events; closed items cancelled; neutral titles for health; `--member` for
  one person's calendar).
- **Overdue means the last day has passed.** `record.py due` no longer calls
  an item overdue when only its plan date has passed: it is `now` with
  `plan_passed` and a plan note. An entry may name the pack's counting rule
  (`"rule": "tax"`); `due` then reports `last_day`, moved past a weekend or
  holiday with the law cited. Statutory dates from `dates.py recurring` carry
  their rule.
- **Tags and law in the household's language.** Provenance tags come as
  `provenance_local` (in Polish: „reguła z pakietu krajowego, do
  sprawdzenia”); pack text that exists only in English is marked
  `text_lang: "en"` for translation; 73 law citations in the PL pack lost
  their English joiners and descriptions („w zw. z”, „i”, names of
  regulations in Polish).
- The weekly brief and the deadline list show the plan date and the last day
  in two columns; titles and notes of the Polish test household are Polish.
- **Session tests**: `scripts/session_test.py` runs 18 multi-turn sessions
  (`evals/sessions/`) with the scripts in four groups (gate, safety, dates,
  language), checked by the state of the household folder and by patterns,
  with no judge; `--check` validates and seeds them without a model.
- **Pack review**: `scripts/pack_review.py` and a monthly workflow open one
  issue per pack whose review is older than six months.
- **Pilot protocol**: `docs/pilot.md` and `docs/pilot.pl.md`, twelve
  scenarios, measures and a notes template without real data.
- 198 unit tests (49 new). The paid runs of this release (the session suite
  and the behaviour tests of the changed skills) are still to run.

## 1.0.0-rc.2

Codex and ChatGPT. The same plugin now also ships in the open Agent Plugins
format, next to the Claude one.

- `householdbot/plugin.json`: the portable manifest (Agent Plugins schema)
  with the OpenAI extension: display name, descriptions, category, privacy
  policy, sample prompts, and `household-onboard` as the onboarding skill.
- `.agents/plugins/marketplace.json` makes the repository a Codex
  marketplace: `codex plugin marketplace add dithiothreitol/householdbot`,
  then `codex plugin add householdbot@householdbot`. Checked with Codex CLI
  0.153: all 34 skills appear as `householdbot:<skill>`.
- The skills give the member the command their app uses:
  `/householdbot:<skill>` in Claude Code and Cowork, `$householdbot:<skill>`
  in Codex, the plugin picked with `@` in ChatGPT.
- `scripts/validate.py` keeps the two manifests and the two marketplaces in
  step (name, version, description, licence, links, onboarding skill).

## 1.0.0-rc.1

Reach, hardening and release (stage 4 of 4). The release candidate of 1.0;
1.0 follows the pilot in a real household.

- Skills: `household-dashboard` (one read-only page on the whole household:
  deadlines by band, this month's payments with totals per currency, what
  expires, insurance, health and school under neutral titles, chores, meals
  and shopping, the record's health and a "not tracked" line for every gap;
  saved as Markdown or one self-contained HTML page only after a yes),
  `build-skill` (a repeated household task becomes the household's own skill
  that keeps the house rules; written after a yes, never over an existing
  skill without the difference shown) and `pack-builder` (a household's own
  country pack from official sources only, checked with `dates.py
  check-pack`, kept in `packs/` in the record). 34 skills.
- Country pack **GB** (England and Wales, reviewed 2026-11-14): bank holidays
  with substitute, moved and one-off days (checked against the official list
  for 2019 to 2028), the five counting rules, deemed service and delivery,
  92 response windows (county court, HMRC, benefits, council tax, parking and
  speeding notices, consumer cancellation and rejection, complaints and
  ombudsmen, renting, life events, health), 17 yearly dates (Self Assessment,
  school admissions, childcare codes), 20 keeping periods, 6 life events,
  every rule with its act, section and source; 46 points left open are listed
  without a claim. An independent check of about forty claims against the
  primary texts led to four corrections, among them deemed service counted in
  business days (`dates.py deemed` now supports `unit` and `end_roll`). The setup asks a UK household which nation it lives in;
  Scotland and Northern Ireland start without a pack.
- `dates.py`: holiday rules for "the first Monday in May", "the last Monday in
  August", substitute days, moved and one-off days; periods "beginning with"
  the day of the event (`start_inclusive`, `deadline --inclusive`);
  `check-pack` checks a pack and lists its holidays for a year;
  `scripts/validate.py` runs the same check on the bundled packs; `windows`
  finds a pack's response windows by words (`--query defence`). Amounts in
  English use the currency symbol where there is one (`£142.60`).
- The dashboard and the payment list name the last day and the plan date
  apart ("last day Sun 17 Jan 2027, plan by Fri 15 Jan"); a payment is overdue
  only once its due date has passed. A saved dashboard page and a skill the
  household builds each leave a line in `log/decisions.md`, as register
  changes do. Around a draft in the recipient's language, everything else
  stays in the household's language. After a death, every answer opens with
  one plain sentence of sympathy, whichever skill takes the request.
- A household's own pack (`packs/<CC>.md` and `.json` in the record) is used
  where no pack is bundled, tagged `household pack — verify`; every pack
  states the part of the country it covers.
- Security review, all findings fixed: text from documents, messages, file
  names and bank exports never goes on a command line (`--query-file -`,
  `--file -`, `"original"` inside the entry, `statement.py add-rule --file -`,
  `chores.py add --file -`); writes refuse a path that leads out of the
  household folder through a link, use unique temporary files and never
  overwrite an original; the decisions log keeps one escaped line per change;
  `merge` takes only a listed conflict copy, shows every changed field and
  checks the entries it brings in; identifiers are refused at write time
  (IBANs of any country, UK sort code and account, National Insurance and NIP
  numbers, card numbers, PINs and passwords) and masked in bank exports; the
  `deadline-watcher` agent has read tools only; the release workflow builds
  with a read-only token and pinned tools and publishes from a separate job.
- `managed-agent-cookbooks/deadline-watcher`: the weekly deadline check as a
  Claude Managed Agent with three tiers (a reader with read tools, a
  calculator that runs the plugin's scripts in a sandbox with no network, a
  writer that alone can write and never sees raw data), a weekly scheduled
  deployment, an offline check and dry run; only the profile excerpt and the
  open obligations are uploaded, never the originals.
- Release packages: `scripts/package.py` builds `householdbot.plugin` (for
  Cowork's Upload plugin) and one zip per skill for claude.ai, reproducibly;
  a tag builds and publishes them (`.github/workflows/release.yml`). Behaviour
  tests with a shell run on Linux on request (`.github/workflows/evals.yml`).
- Docs: `docs/architecture.md` (the pattern and what a household changes
  about it), `docs/country-packs.md`, the quickstart for every surface and
  scheduled weekly briefs, `CONNECTORS.pl.md`; the development plan in English
  with a Polish translation.
- Tests: unit tests for the new holiday rules, inclusive periods, the pack
  check, the GB pack and the security fixes; behaviour cases for the three
  skills, the GB pack, Scotland, and a record kept behind the Google Drive
  connector.

## 0.3.0

Home, family and everyday life (stage 3 of 4).

- Skills: `home-upkeep` (statutory checks, guarantees, repair history,
  contractors' quotes), `vehicle-file`, `insurance-overview`,
  `identity-and-travel`, `school-desk`, `health-file` (stricter privacy,
  validity of prescriptions and referrals), `emergency-file` (where things
  are and whom to call, never a number or a password), `family-calendar`
  (clashes and drives, entries after a yes with neutral titles),
  `meal-planner`, `shopping-list`, `chore-rotation`, and the chains
  `life-event` (moving, a birth, buying or selling a car, a new job, a death)
  and `annual-review` (what may be shredded, renewals, tax papers, archive).
- `chores.py`: the chores register, fair and repeatable plans by share and
  age with last weeks' load carried over, saved plans, agreed swaps and the
  balance; 14 unit tests.
- `dates.py event` counts every statutory window of a life event from the
  day it happened; `record.py retention` lists papers past their keeping date
  and changes nothing; documents gain the status `disposed`.
- Shared rule `everyday` (meals, shopping, chores, the family calendar);
  personal-data rules for foods kept off the plan and for the emergency file;
  approval gates for dictated list changes, calendar entries and plans.
- The profile gains an optional *Everyday life* section, and the setup an
  optional fifth part; `registers/chores.json` and `lists/` are described in
  the registers guide.
- Every skill's description is shorter (about 300 characters, trigger
  phrases early), so 31 skills stay within the skill listing; every skill
  reads `household-profile.md` first and runs `record.py locate` only when it
  is not there.
- `--approved-by` takes a name only; a PIN, password or code a member types is
  never repeated; a yes given before a plan or list was shown approves
  nothing; `record.py complete --from-done`; `record.py find` lists a type or
  category without search words.
- An entry reaches `record.py` on standard input (read as UTF-8) or with
  `--json`; no file is written to prepare a write.
- The session's own account (name, address) is never quoted, signed with or
  used to decide whose mailbox is connected; `inbox-triage` reads the mailbox
  connected in the session and offers to note it in the profile.
- From the behaviour tests: the emergency file shows its outline from the
  record before asking; a child asking for a chore swap is answered directly;
  health papers and school letters are looked up in the record and read in
  full before anything is asked; quotes say "not stated" rather than "none";
  incomes the pack does not cover get a checklist, not rules from memory; an
  appeal's addressee block names the appeal body first; a sale or a death
  names the register entries that end with it; a fact from a filed document
  names its register id, title and page; a trip check keeps the verdict
  apart from renewal timing.
- Polish country pack: life events (buying or selling a car, moving house, a
  birth, a new job, a death), health papers, children and school, keeping and
  shredding documents, insurance a household must or may have, home upkeep
  and travel documents; 50 new windows, 6 life events, 5 recurring items and
  12 keeping periods, each with its law or marked as a suggestion. Reflects
  the 2025–2026 changes: the PLN 7,000 funeral allowance, 60 days to register
  an inherited car, the PLN 3,000 PCC exemption, central e-registration and
  smoke and CO detectors. Corrected: the lump-sum tax paid only on private
  rental does not rule out joint filing or the single-parent method (ustawa o
  PIT art. 6 ust. 8).

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
