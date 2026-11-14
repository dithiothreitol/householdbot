# Architecture: the plugin pattern applied to a household

HouseholdBot has two results: a plugin a household can run its paperwork
with, and an analysis of how the structure of Anthropic's open-source vertical
plugins carries over to a domain that has no system of record, no staff and
no lawyer on call. This document is the analysis. It describes what was taken
from the pattern, what a household changes about it, and what four stages of
building and testing showed.

## 1. The reference pattern

Two Anthropic repositories, both Apache-2.0, were read in full before the
first line was written:

- **knowledge-work-plugins/small-business**: one plugin with a router and an
  onboarding interview, about forty skills, shared rules that every skill
  carries, chains of skills with an approval gate at each step, and a
  `build-agent` skill that turns a repeated task into a new skill.
- **claude-for-legal**: a practice profile stored outside the plugin so it
  survives updates, a quick and a full interview with `[PLACEHOLDER]` and
  `[DEFAULT]` markers, a renewal register with provenance on every date, a
  `customize` skill that changes one setting without a new interview, a
  read-only watcher agent, and managed-agent cookbooks that split work into
  readers, analysers and a single writer.

What the two share, and what HouseholdBot treats as binding: **each SKILL.md
carries the right behaviour on its own; the shared rules are a safety net, not
the place where behaviour lives.** Nothing leaves the conversation without a
person's yes.

## 2. How the pattern maps

| Element of the pattern | From | In HouseholdBot |
|---|---|---|
| Marketplace with one entry per plugin | both | `.claude-plugin/marketplace.json`, one plugin |
| One plugin, router, onboarding | small-business | `household-router`, `household-onboard`, 34 skills |
| `skills/<name>/SKILL.md` with `reference/` | small-business | the same; every skill has `reference/gotchas.md` |
| Shared rules | small-business | `core/rules/*.md`, bundled into one `shared/rules.md` per skill |
| Quick and full interview with markers | legal | `household-onboard`, two minutes or fifteen |
| Profile outside the plugin | legal | `household-profile.md` in the household's own folder |
| Register with provenance and business-day roll-back | legal | `registers/obligations.json` and `dates.py` |
| `customize` | legal | `household-customize` |
| Read-only watcher agent | legal | `deadline-watcher` |
| Chains with a gate at each step | small-business | `monthly-review`, `life-event`, `annual-review` |
| Coding and paying as two approvals | small-business | the money rule: a payment list, then a separate yes per payment |
| "Do not promise a schedule nobody set" | small-business | `chain-seams` rule |
| `build-agent` | small-business | `build-skill` |
| Managed-agent cookbook with three tiers | legal | `managed-agent-cookbooks/deadline-watcher` |

## 3. What a household changes

### 3.1 There is no system of record

A firm has an ERP, a contract repository or a document management system, and
its plugin reads from it. A household has a drawer, a mailbox and two phones.
HouseholdBot therefore brings its own record: a folder of plain files the
household chooses and owns, ideally inside a synced drive so two adults share
it.

```
household-profile.md       who lives here, homes, vehicles, providers, decision rules
registers/documents.json   one entry per filed paper: facts with page and quote
registers/obligations.json one entry per thing to do by a date
registers/chores.json      chores, shares and saved plans (optional)
registers/.history/        a copy of each register before every write
documents/<year>/          the originals, renamed by date and issuer
lists/                     shopping list, staples, meal plans (optional)
log/decisions.md           one line per approved change, with the approver's name
```

JSON was chosen over YAML or a database because the standard library reads it
everywhere, a person can open it, and a synced drive merges nothing silently:
a conflict copy (`obligations (1).json`) stops all writes until
`household-doctor` merges it. Amounts are strings (`"286.40"`), never floats.
The schema is enforced by `record.py` rather than by JSON Schema files, because
the standard library has no validator and the skills must run without
installing anything.

### 3.2 Scripts prove, the model judges

A firm's plugin can lean on its systems for arithmetic. A household's
deadlines are where language models fail quietly: a fourteen-day appeal that
ends on a public holiday, a contract that renews unless cancelled thirty days
before a date in a scanned PDF, a bank export in a legacy encoding. HouseholdBot
adds a proof layer of four standard-library scripts that print one JSON object
each:

| Script | Proves |
|---|---|
| `dates.py` | holidays per country (fixed, Easter-based, "first Monday in May", substitute days, one-off days), deadlines under the country's counting rule, deemed delivery, the safe `do_by` date, urgency bands, recurrence, statutory dates, life events, a pack check |
| `record.py` | register reads and writes, schema, identifiers caught before they are stored, conflict copies, merges, archive, migration, keeping periods |
| `statement.py` | a bank export to the cent: encodings, layouts, masked account numbers, running-balance check, missing months reported as missing, price rises |
| `chores.py` | a chore plan that is the same every time for the same inputs, with shares, age limits and last weeks' load carried over |

Every write is a preview first: the script stores the change under a confirm
token, and only `commit --confirm <token> --approved-by <name>` applies it
(section 4). Without Python (a sandbox with no shell), each
skill follows the same rules by hand and tags every computed date
`model calculation — verify`.

### 3.3 Every skill stands alone

On claude.ai a skill is uploaded on its own, and only its folder reaches the
sandbox. Each skill therefore carries copies of what it needs in
`skills/<skill>/shared/`: the rules as one file with a table of contents, the
country packs, the scripts, the language files and the templates.
`scripts/sync.py` generates the copies from `core/` according to
`core/vendor.json`, and `scripts/validate.py` fails when a copy is stale or a
SKILL.md names a path outside its own folder.

### 3.4 Law is data

A business plugin can assume one jurisdiction or leave law to its users. A
household meets statutory windows weekly: an appeal against a tax decision, a
consumer's withdrawal, a registration after buying a car. Country knowledge
sits in two files per country (`docs/country-packs.md`): Markdown for the
model and JSON for the scripts. The counting-rule vocabulary (`administrative`,
`tax`, `civil`, `court`, `calendar`) is shared, so a skill names a rule without
knowing the country. Every rule cites an act, an article and an official
source; unsettled points are listed as uncertain and never stated. Two packs
are bundled (Poland, and England and Wales); a household elsewhere can build
its own with `pack-builder`, and the same check (`dates.py check-pack`) runs on
both kinds.

### 3.5 Language is not country

An English-speaking family in Poland needs Polish letters explained in
English and replies to Polish offices written in Polish. Language therefore
lives in `core/i18n/<lang>.json` (weekday and month names, date and amount
formats, plural forms, notes, log lines) and `core/templates/<lang>/`, apart
from the country pack. The setup's first line is in both languages and asks.

### 3.6 Household data needs stricter rules than business data

- Identifiers (national ID numbers, account and card numbers, policy numbers)
  are never copied into the record; the register points to the page. The one
  exception is the last four digits of an account to pay into, kept to notice
  when a bill asks for payment to a new account.
- Health and allergies stay out of titles, because a calendar entry or a
  reminder is read by people outside the matter.
- The account a session runs on is not the household's data: its name and
  email address never sign a letter or decide whose mailbox is connected.
- Every document is untrusted. The `document-reader` agent has only `Read` and
  `Glob`, so a sentence planted in a scanned letter has nothing to act with,
  and every skill screens for the country's scam patterns before filing.

## 4. Approval gates in practice

The pattern says "nothing without a yes". In a household the gate has to be
concrete enough for a model to follow under pressure:

1. The skill shows the exact entry, list or draft, then asks.
2. The script previews every write and stores exactly that change under a
   confirm token; only `commit --confirm <token> --approved-by <name>`
   applies it, after the yes, and the decisions log keeps the name. A token
   older than 30 minutes, or one whose files changed since the preview, is
   refused; several entries of one register go into one preview, so one yes
   is one commit per register. In Claude Code and Cowork a `PreToolUse` hook
   sends the commit to the host's own permission prompt, which shows the
   preview line, so the yes reaches the record through a person and not
   only through the model's account of it.
3. Preparing a file is already a write. Entries reach `record.py` on standard
   input (`--file -` with a here-document) or as `--json`; files the skills
   keep (briefs, pages, lists, packs) go through `record.py save` under the
   same gate; without a shell the skill only shows them.
4. Money takes two approvals: one for the payment list, one per payment the
   member reports as made. HouseholdBot never pays.
5. A draft is never sent. A draft in a connected mailbox is created only after
   the household approved its text.
6. A chain (`monthly-review`, `life-event`, `annual-review`) stops at every
   seam for its own yes, and a step that depends on an earlier one says so
   when the earlier one was skipped.

## 5. Verification

| Level | What | Tool |
|---|---|---|
| 1. Structure | manifests, frontmatter, self-sufficient skills, fresh copies, directory limits, agents' tools, packs, identifiers and secrets in committed files | `scripts/validate.py`, `claude plugin validate --profile directory --strict` |
| 2. Arithmetic | holidays (England and Wales checked against the official list for 2019 to 2028), deadlines, deemed delivery, registers, merges, bank exports, chore plans | `python -m unittest` |
| 3. Behaviour | skill triggering, correct answers on a synthetic household, gates held, injection and scams resisted | `claude plugin eval` through `scripts/eval.py`, with an LLM judge |
| 4. Use | multi-turn sessions with the scripts on synthetic data; the pilot on a real household | `claude -p`, the household |

The behaviour tests live outside the plugin package (`evals/`), so the
published plugin carries no test files. `claude plugin eval` reads cases only
inside a plugin, so `scripts/eval.py` stages a copy in `build/`. Each stage
closed with a full run; the numbers are in the development plan.

The Stage 4 run compared the plugin with the same model and no plugin on the
same 115 cases. With the plugin 98 cases passed in full, without it 19 (mean
score 0.95 against 0.64), at about twice the cost per answer. The cases that
pass without the plugin are mostly gates the model keeps on its own (it does
not delete papers on request, recognises a parcel scam, does not pretend to
read a mailbox that is not connected) and simple file tasks. The difference
lies where the answer depends on the record and the country pack: dates with
their weekdays and law, amounts from the registers, documents the record
does not hold, a yes before a write. After the fixes that run led to, the
final run passed 103 of the 115 cases (mean score 0.97).

## 6. What building it showed

These findings are about the pattern, not about households alone.

1. **Every step that calls a script needs a path without one**, including the
   step that finds the record. Without it a skill correctly refuses to work
   and gives the user nothing.
2. **No shell does not mean no record.** Step 0 of every skill reads the
   profile with the Read tool first and runs the locator script only when no
   profile is found.
3. **Scripts run from the session's folder, not the skill's.** Run from the
   skill folder, a script does not see the user's files.
4. **A skill names every file it needs.** Without a shell a model does not
   search; a pack it was not pointed to does not exist for it, and it quotes
   law from memory instead.
5. **The skill listing has a budget.** With thirty-one skills the
   descriptions had to fall to about 300 characters, trigger phrases first.
   Shortening them lost the phrases for requests that do not sound like tasks
   ("from now on in Polish", "until when can I appeal"), and those requests
   were answered without any skill.
6. **"Do not repeat an identifier" must cover error reports**: a model quotes
   the bad value to show what is wrong.
7. **A window the other side must meet needs its own fields**: what meets it
   (`met_by`) and what silence means (`silence`). The rule for the household's
   own statements was misleading there.
8. **The session account leaks.** A model sees the account owner's name and
   the git identity; it signed letters with them until the rule said the
   signature comes from the profile or stays a field to fill in.
9. **Each new skill takes requests from older ones**, so the graders that
   check which skill fired must widen with every skill added.
10. **Judges need rubrics written for judges**: one sentence saying the
    record is synthetic, numbered checks, and a list of what is not an error,
    including country-pack rules the judge cannot see. With that, the same
    answer stopped swinging between 0/3 and 3/3. A small judge model gave false
    failures on long answers in Polish; a mid-size judge did not. A judge
    with `focus: last_message` sees the final reply only, not the request, the
    record or the pack, so a rubric names the facts of the request it relies
    on (a decision quoted in the message), and a condition that may not apply
    ("inheritance behind the not-advice line") says when it does not.
11. **Test data from several generators must agree** (providers, amounts,
    keeping periods), because the model rightly reports the disagreement.
12. **A deterministic plan moves the argument.** Once a script computes the
    chore plan the same way every time, a family's dispute moves to the
    shares and age limits an adult sets, where it belongs.
13. **The model's own abilities compete with the skills.** Asked to "turn
    that into a skill and install it", Claude wrote a skill file itself,
    without the draft and the yes that `build-skill` would have asked for.
    Asked "what are our deadlines" about a court claim, it answered from
    memory and missed that the last day was a substitute bank holiday. A
    plugin's rules apply only once one of its skills runs, so the trigger
    phrases must cover how people actually ask, including requests that do
    not sound like a task for a plugin.
14. **The model writes shell commands, so outside text must never be part of
    one.** A sender's name or an attachment's file name in double quotes on a
    command line runs `$(...)`; an apostrophe ends single quotes. Every script
    takes such text on standard input, and the rule says so in every skill.
15. **A detector must match the real format.** An IBAN check that allowed
    spaces anywhere and tried every length flagged ordinary prose that passed
    the checksum by chance. Country lengths and groups of four fixed it; the
    same check now refuses identifiers at write time instead of warning.
16. **Legal research parallelises, verification does not.** Three agents
    researched the GB pack against one written standard (official sources
    only, act and section for every rule, the unsure listed without a claim);
    a separate agent then checked about forty claims against the primary
    texts and found four errors: a weekend roll the law does not give, two
    outdated citations, and deemed service counted in calendar days where the
    rule says business days. A sample check is cheap next to a wrong date in a
    household's hands.
17. **"Not in the pack" needs a search that could have found it.** A broad
    search of the pack returned a long result that the model read in part,
    and it reported a court rule as missing that the pack holds. A script that
    finds windows by words (`dates.py windows --query defence`) answers in a
    few lines.
18. **The last day and the plan date need different names everywhere.** A
    dashboard that called the plan date "the last day" took two days from the
    household.
19. **Rules in one skill must not compete.** "No platitudes" crowded out "one
    plain sentence of sympathy" after a death; the first-sentence rule now
    sits among the gates.
20. **Every write into the household folder is logged, not only register
    writes.** The scripts log register changes themselves; a skill that writes
    a page or a file with the Write tool needs the log line in its own steps.
21. **Examples in a skill are copied verbatim.** Labels the skill quotes in
    English ("not tracked", "not set up") appeared word for word on a Polish
    page until the skill said that every label is in the household's
    language and gave the translation.
22. **The path without Python is the weak point of a test environment
    without a shell.** On a long page, weekdays counted by hand went wrong
    (three of thirty-one in one run), and a pack checked by hand missed an
    undefined counting rule that `check-pack` always reports. The same steps
    with the scripts are deterministic and covered by unit tests; the
    behaviour tests on Windows measure the fallback.
23. **A guarantee belongs in the script, not in the prompt.** Until rc.2 the
    gate rested on the model: it typed `--approved-by` itself, and nothing
    but its instructions kept it from typing the name before the yes. Next
    to agent platforms whose agents act without asking, that is a promise a
    weaker or a misled model can break. In rc.3 the scripts enforce two
    phases and the hook asks a person; the skills only describe the flow.
24. **A use session finds what the behaviour tests cannot.** Six turns with
    the scripts on a Polish household (0.81 USD) found a band computed from
    the plan date ("overdue" for an instalment whose last day was two days
    ahead), provenance tags and law citations in English inside Polish
    answers, and a table that called the safe date the last day. None of
    them shows in the 115 cases, because on Windows they run without a
    shell; the session tests now cover that path with deterministic checks.

## 7. Surfaces

| Surface | How it is installed | What works |
|---|---|---|
| Claude Code (terminal, IDE) | `/plugin marketplace add` and `/plugin install` | everything: skills, agents, scripts, local record |
| Claude desktop, Code tab | **+ > Add plugins** in a local session | skills, agents, scripts, local record |
| Cowork (Claude desktop) | **Customize > Plugins**, or **Upload plugin** with `householdbot.plugin` from a release | skills, agents and hooks; local files when the session runs on the computer; scheduled tasks can use the plugin |
| claude.ai (web) | the plugin, or single skills uploaded as zips from a release | skills; scripts in the code sandbox; the record through the Google Drive connector; agents and hooks are ignored |
| Mobile apps | no plugin install; Remote Control drives a session on the computer | as the session it drives |
| OpenAI Codex CLI | `codex plugin marketplace add`, then `codex plugin add` | skills and scripts in the Codex sandbox; the agents and the bundled connector settings are Claude features |
| ChatGPT desktop app (Codex, Work) | the Plugins Directory, from the repository's marketplace | skills; scripts where the session can run them |

The same plugin folder serves both ecosystems: `.claude-plugin/plugin.json`
for Claude, and the portable `plugin.json` (Agent Plugins format, with the
OpenAI extension) for Codex and ChatGPT. The skills follow the open Agent
Skills standard, so one `SKILL.md` works in both; only the command a member
types differs (`/householdbot:<skill>` against `$householdbot:<skill>`).

Proactivity follows the surface: a weekly brief can be a Cowork scheduled
task or a desktop scheduled task while the app is open, and the unattended
variant is the managed-agent cookbook. Where nothing is scheduled, the skills
say so instead of promising a reminder.

## 8. The unattended variant

`managed-agent-cookbooks/deadline-watcher` deploys the weekly deadline check
as a Claude Managed Agent, following the legal cookbooks' three tiers: a reader
that touches the register snapshot with read-only tools, a calculator that
runs the plugin's scripts in a sandbox with no network and returns only
checked ids, dates and bands, and a writer, the only worker that writes, which
never sees raw data and produces one report. The coordinator holds no tools;
its prompt is the plugin's own agent with a section for unattended runs, and
the offline check fails when the two drift apart.
Only the profile and the registers are uploaded for a run; the originals never
leave the household. Nothing is sent: delivery of the report is wired by the
household.

## 9. Limits and open questions

- **Files.** The plugin directory reviews plugins of more than 512 files by
  hand. Each country pack adds two files to each of the 27 skills that carry
  packs; with two packs the plugin has 382 files, so two more packs fit before
  packs need a plugin of their own.
- **The script path in behaviour tests.** On Windows the eval sandbox cannot
  grant a shell, so local runs test the path without Python; the script path is
  covered by unit tests, multi-turn sessions, and a Linux workflow
  (`.github/workflows/evals.yml`).
- **Writes after a yes in behaviour tests.** A case that resumes a
  conversation needs a transcript file whose format is not documented, and a
  local transcript carries the user's paths. Writes after approval are
  therefore checked in multi-turn sessions on synthetic data.
- **Law drifts.** Packs carry a review date, `annual-review` reminds the
  household of it, and every statutory date reaches the household with the word
  *verify*.
- **The pilot.** The last acceptance condition for 1.0 is a real household
  using it without blocking errors.
