# HouseholdBot

**English** · [Polski](README.pl.md)

HouseholdBot is a Claude plugin that runs a household's paperwork from a
conversation. It reads letters, bills, contracts and policies, files them into
a folder the household owns, tracks every deadline, renewal and cancel-by date
with the country's public holidays, and writes a short brief on the week
ahead. Nothing is written, sent or paid without a household member's yes.

## Skills

| Skill | Say something like |
|---|---|
| `household-onboard` | "set us up", "skonfiguruj" |
| `household-router` | "help me with our paperwork", "what can you do" |
| `file-document` | "I got a letter", "file this", "is this message real?" |
| `find-document` | "where is the car insurance?", "what did the contract say about notice?" |
| `deadline-tracker` | "what's due", "I paid it", "I got this on Tuesday, how long do I have?" |
| `weekly-brief` | "weekly brief", "what's this week" |
| `household-customize` | "we sold the car", "add a member", "use English" |
| `household-doctor` | "check my record", "Drive made a second copy of the file" |
| `inbox-triage` | "go through my email", "anything important in the mail?" |
| `bills-due` | "what do we need to pay", "I paid these" |
| `contract-check` | "check this contract before I sign" |
| `subscriptions-review` | "what subscriptions do we pay for", "Netflix went up" |
| `budget-snapshot` | sends a bank export, "where does our money go" |
| `tax-season-organizer` | "help with our tax return" |
| `reply-to-letter` | "answer this letter", "write an appeal" |
| `complaint-and-claim` | "the product broke", "insurance claim", "I want to return it" |
| `cancel-or-switch` | "cancel this", "switch provider" |
| `monthly-review` | "monthly review" |
| `home-upkeep` | "chimney check", "is the washing machine still under guarantee", "compare these quotes" |
| `vehicle-file` | "when is the car's test", "I got a speeding ticket" |
| `insurance-overview` | "what insurance do we have", "are we insured twice" |
| `identity-and-travel` | "is my ID still valid", "are we ready for the trip" |
| `school-desk` | "what does the school want", pastes an e-register message |
| `health-file` | "is the referral still valid", "when does the prescription expire" |
| `emergency-file` | "if something happens to me" |
| `family-calendar` | "what's on this week", "who picks up Zosia" |
| `meal-planner` | "plan our meals", "what's for dinner this week" |
| `shopping-list` | "add milk to the list", "what do we need from Lidl" |
| `chore-rotation` | "who does what this week", "split the chores" |
| `life-event` | "we're moving", "we had a baby", "I bought a car", "my father died" |
| `annual-review` | "annual review", "what can we shred" |
| `household-dashboard` | "dashboard", "everything at a glance" |
| `build-skill` | "make this a skill", "automate this for us" |
| `pack-builder` | "there is no pack for our country", "check our pack" |

Agents (Claude Code and Cowork): `deadline-watcher` reads the register on a
schedule and reports, with read tools only; `document-reader` reads a pile of
documents with no write tools and returns a structured extraction.

## Start

1. Install: in Claude Code, `/plugin marketplace add dithiothreitol/householdbot`
   (or the path of a local copy) then `/plugin install householdbot@householdbot`.
   In Cowork, add the marketplace under Customize > Plugins, or upload
   `householdbot.plugin` from a release. In OpenAI Codex,
   `codex plugin marketplace add dithiothreitol/householdbot` then
   `codex plugin add householdbot@householdbot`.
2. Run `/householdbot:household-onboard`. The quick setup takes about two
   minutes and ends with one real document filed.
3. From then on, send a photo or PDF of any paper, or ask "what's due".

## The household record

A folder of plain files in a place the household chooses, ideally a synced
drive so that two adults share it without any server:

```
household-profile.md      who lives here, what they own, how they decide
registers/documents.json  index of every filed document, with page and quote for each fact
registers/obligations.json every deadline, renewal and payment, with its source
registers/chores.json      chores, shares and saved chore plans (when the household uses them)
lists/                     the shopping list, regular items and the week's meals
documents/<year>/         the filed originals
briefs/, reviews/          saved briefs and pages
exports/                   the calendar file for a phone
registers/.history/        the previous version of every changed file
registers/.pending/        previews waiting for a yes (30 minutes at most)
log/decisions.md          every approved change: when, who, what
```

## What it runs, sends and fetches

- **Runs:** four Python scripts bundled in the skills (`dates.py` for
  holidays, deadlines and life events, `record.py` for the registers,
  `statement.py` for bank exports the household gives it, `chores.py` for
  fair chore plans). Standard library only. They
  read and write inside the household folder and one pointer file under
  `~/.claude/plugins/config/householdbot/`, and refuse a path that leads out of
  the household folder. Text from documents reaches them on standard input,
  never on a command line. Every write is a preview first; `commit` applies
  exactly the previewed change with the approver's name. In Claude Code and
  Cowork, the plugin's `PreToolUse` hook (`hooks/gate.py`, run through
  `hooks/gate.sh` with the Python it finds) sends each commit, and each
  direct write into the household folder, to the host's permission prompt.
  `build-skill` writes one new skill folder under
  `~/.claude/skills/` when the member approves that place. Without Python the
  skills follow the same rules by hand and mark computed dates for checking.
- **Sends:** nothing to any service of its own; HouseholdBot has none. If the
  household connects Gmail, Google Calendar or Google Drive (`.mcp.json`),
  those connectors read on request and write (a draft, a calendar entry, a
  file) only after a yes, under the provider's terms. Drafts are never sent.
  HouseholdBot never logs in to a bank and never pays.
- **Fetches:** the scripts make no web requests. `pack-builder` asks Claude
  to read official legislation and government pages with its own web tools,
  when the session has them, to build a country pack.

## Languages

English is the default and Polish is the second language. The setup asks
first, and "in Polish" or "po angielsku" switches later. Answers, briefs,
dates (`Fri 20 Nov 2026` or `pt. 20.11.2026`), amounts (`PLN 1,240.00` or
`1 240,00 zł`), the profile template and the decisions log follow the chosen
language. Documents keep theirs: a Polish letter is explained in English for
an English-speaking household, with the original quoted, and a reply to a
Polish office is drafted in Polish with an English translation.

## Countries

Country packs hold public holidays, deadline counting rules, response windows
and recurring obligations, each with its law and a review date. Included:
Poland (`PL`, reviewed 2026-11-13) and England and Wales (`GB`, reviewed
2026-11-14). For another country or region, `pack-builder` builds the
household's own pack from official sources, kept in the household folder. Without a pack, HouseholdBot works from
what documents state and what the household says.

## Privacy

[Privacy](PRIVACY.md) ([po polsku](PRIVACY.pl.md)): the household's data
stays in the household's folder and the services it chooses to connect.

## License

Apache-2.0. HouseholdBot is an independent open-source project and is not
affiliated with or endorsed by Anthropic.
