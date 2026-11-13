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

Agents (Claude Code and Cowork): `deadline-watcher` reads the register on a
schedule and reports, changing nothing; `document-reader` reads a pile of
documents with no write tools and returns a structured extraction.

## Start

1. Install: in Claude Code, `/plugin marketplace add <path or repository>`
   then `/plugin install householdbot@householdbot`. In Cowork, add the
   marketplace and install the plugin.
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
documents/<year>/         the filed originals
log/decisions.md          every approved change: when, who, what
```

## What it runs, sends and fetches

- **Runs:** two Python scripts bundled in the skills (`dates.py` for holidays
  and deadlines, `record.py` for the registers). Standard library only. They
  read and write inside the household folder and one pointer file under
  `~/.claude/plugins/config/householdbot/`. Without Python the skills follow
  the same rules by hand and mark computed dates for checking.
- **Sends:** nothing to any service of its own; HouseholdBot has none. If the
  household connects Gmail, Google Calendar or Google Drive (`.mcp.json`),
  those connectors read on request and write (a draft, a calendar entry, a
  file) only after a yes, under the provider's terms.
- **Fetches:** no web requests.

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
Poland (`PL`, reviewed 2026-11-13). Without a pack, HouseholdBot works from
what documents state and what the household says.

## Privacy

[Privacy](PRIVACY.md) ([po polsku](PRIVACY.pl.md)): the household's data
stays in the household's folder and the services it chooses to connect.

## License

Apache-2.0. HouseholdBot is an independent open-source project and is not
affiliated with or endorsed by Anthropic.
