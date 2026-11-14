# Deadline watcher on Claude Managed Agents

The plugin's [`deadline-watcher`](../../householdbot/agents/deadline-watcher.md)
agent reads the household's obligations register and reports what is overdue,
due soon or inside its lead time. This cookbook runs the same check unattended
on [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview):
every Monday morning a session reads a trimmed snapshot of the register and
writes one short report, which a helper script downloads, checks and saves in
the household folder.

It is a cookbook: a working setup to read, adjust and deploy under your own
Anthropic account. The coordinator's system prompt is the plugin's own agent
file plus a section for unattended runs, and the date arithmetic comes from the
plugin's `deadline-tracker` skill, so a change in the plugin reaches this
deployment through `python cookbook.py sync` and the next `ant apply`.

## What it does

- Reads a read-only snapshot: a short excerpt of `household-profile.md` and
  the open obligations from `registers/obligations.json`.
- Computes urgency bands and do-by dates with the skill's `record.py due`
  (which calls `dates.py`), with the country's public holidays when the plugin
  has a country pack for it.
- Writes `deadline-watch-<YYYY-MM-DD>.md` in the household's language
  (English or Polish): overdue, this week, the next 30 days, start now, date
  unknown and waiting for a yes, each line with its obligation id. A quiet week
  gets a two-line all-clear that says how many open obligations the snapshot
  holds. Every report ends with a fixed verification footer.
- `cookbook.py` saves the report in `<household folder>/out/` after checking
  it on your computer (see [The checks on your computer](#the-checks-on-your-computer)).

## What it does not do

- It sends, pays, files, signs and cancels nothing, and it contacts nobody.
- It does not write to the household's record. The snapshot is mounted
  read-only; the one file the agents write is the report, inside the sandbox.
  On your computer, `cookbook.py` writes the report into `out/`, its own
  state file and temporary files outside the household folder.
- It does not deliver the report. There is no e-mail and no notification:
  forwarding the report from `out/` (a mail rule, a phone shortcut, a webhook
  in the Console) is a step you wire up yourself.
- It does not read the originals in `documents/`, the inbox, mail, calendars
  or anything online. No MCP server is configured, the web tools are off and
  the sandbox has no network.
- It does not replace the paper. Dates come from the register, and the
  register comes from documents a person or the plugin read once.

## What leaves your computer

Per run, two files, mounted under `/mnt/session/uploads/household/`:

| File | What it holds |
|---|---|
| `household-profile.md` | An excerpt written by `cookbook.py`: Country, Language, Time zone and who sees the weekly brief, plus when the snapshot was taken, the number of open obligations and the counts of a record check run on your computer. Members, homes, vehicles, providers, everyday life and dates to remember stay home. |
| `registers/obligations.json` | Open obligations only, with fifteen fields: `id`, `title`, `kind`, `category`, `owner`, `due_date`, `do_by`, `transit_buffer_days`, `lead_time_days`, `amount`, `currency`, `auto_renews`, `provenance`, `law`, `status`. Closed obligations, `notes`, `source` (document, page and quote), `counterparty`, `subject`, `notice`, `recurrence` and `series` stay home. |

Never uploaded: `documents/` (the originals), `inbox/`, `registers/documents.json`,
`registers/.history/`, `log/`, `briefs/`, `archive/` and the full profile.
`registers/documents.json` is not needed, because expiry dates live in
`obligations.json` as `kind: expiry` entries.

To read the exact files before the first upload:

```sh
python cookbook.py snapshot --household "/path/to/household" --out /tmp/deadline-watch-snapshot
```

The files are stored in your Anthropic account's file storage and read by the
agents in a sandbox on Anthropic's infrastructure. Anthropic processes them,
the agents' messages and the report under your account's data-retention
settings. Managed Agents sessions are not covered by zero data retention: a
session's transcript, which holds the reader's short titles and the report,
stays in the account until you delete the session. `run` deletes the uploaded
files when the session ends, and `--delete-session` also deletes the session
and its output. With the scheduled deployment, the last snapshot you pushed
stays in file storage until the next push or `forget`.

**Running without uploading anything.** Use the plugin's own
`deadline-watcher` agent in Claude Code on your computer: ask "check our
deadlines in the background", or start it from your own scheduler with
`claude -p "Use the deadline-watcher agent to check our deadlines"` in the
household folder. The record stays in your folder; Claude Code sends the model
only what the agent reads during that conversation, and nothing is stored as
a file or runs in a sandbox on Anthropic's side.

## How the work is split

Text in the register is untrusted: titles and laws were often copied from
letters that people outside the household wrote. Each agent gets only the tools
its step needs.

| Agent | Tier | Model | Tools | Sees register text | Network |
|---|---|---|---|---|---|
| `deadline-watcher` | coordinator | `claude-opus-5-5` | none: it hands tasks to the three workers | only the reader's capped JSON | none |
| `register-reader` | reader | `claude-sonnet-5-5` | `read`, `glob`, `grep` | yes, as data | none |
| `deadline-calculator` | analyser | `claude-haiku-5-5` | `bash`, `read`, the `deadline-tracker` skill | not on its normal path: its program returns ids, dates, bands and amounts | none |
| **`report-writer`** | writer | `claude-sonnet-5-5` | `write`, nothing else | only the capped JSON it is handed | none |

- **The reader** returns JSON with capped fields. It removes links, phone
  numbers and anything that looks like an identifier, replaces text that
  gives an instruction with a flag, and turns health items into a neutral
  "appointment". It cannot write, run a command or reach a connector.
- **The calculator** runs one fixed program, written out in its prompt, that
  calls `record.py due` with a 30-day horizon and passes on only computed
  fields, each checked against a pattern. Titles, owners and laws never enter
  its context on that path, so the one agent with a shell does not read the
  register's words. Its prompt forbids opening the snapshot; a shell that
  ignored it could, but with no network, no write tool and no MCP, what it
  read could leave the sandbox only through its reply to the coordinator.
- **The writer** is the only agent with `write`, and it cannot read: it
  formats the merged JSON, escapes every register-derived string (one line;
  `|`, `[` and `]` escaped; `<` and `>` as entities; web addresses as inert
  code; a leading `=`, `+`, `-` or `@` prefixed with `'`), never makes a link
  or an image, and ends with the footer.
- **The coordinator** has no file, shell or connector tool. It merges the two
  results by id without changing a date, band or amount, so the list of items
  comes from the script, not from the agent that read the text. Dynamic
  workflows and inline agents are off: it delegates to these three only.

All tools run under the `auto` permission policy. In an unattended run a call
the server cannot decide waits for an answer: `run` denies it, and with the
scheduled deployment it waits until you answer it (see Option A below).

**Why the calculator has a shell.** The plugin's rule is that the script counts
and the model judges: weekdays, public holidays and do-by dates come from
`dates.py`, and a date the model works out by hand carries the tag
`model calculation — verify`. A shell is what runs the script. The environment
([`environment.yaml`](agents/deadline-watcher/environment.yaml)) is `limited`
with no allowed hosts, no package registries and no MCP servers, so nothing the
shell runs can reach a network, and the snapshot is mounted read-only.

## The checks on your computer

Before `run` or `fetch` saves a report, `cookbook.py` checks it:

- the verification footer is there, word for word;
- there is no HTML, no Markdown link or image, and no web address outside a
  code span;
- the plugin's own detector (`record.py`'s `identifier_warnings`) finds no
  national ID, account or card number;
- every obligation id that `record.py due` lists on your computer for the
  report's date appears in the report (`run` compares with the snapshot it
  uploaded, `fetch` with the register as it is now).

A report that fails one of the first three is not saved: `out/` gets
`deadline-watch-<date>.check-failed.txt` with the reason and the session ID.
Missing ids go into `deadline-watch-<date>.check-notes.txt` next to the saved
report.

## Prerequisites

- A Claude Console organization with access to Managed Agents (beta) and
  billing set up.
- The `ant` CLI, version 1.40.0 or later (the coordinator lists its workers by
  file path), logged in with `ant auth login`. `ant auth status` should show
  the workspace you mean.
- Python 3.9 or later with `pyyaml` and, for the online commands, the official
  `anthropic` package: `python -m venv .venv`, then `pip install anthropic pyyaml`.
- A household record set up by the plugin (`/householdbot:household-onboard`)
  with Country, Language and Time zone filled in.

## Deploy

From this folder:

```sh
python cookbook.py check        # lint: tools per tier, closed sandbox, paths, prompt drift
python cookbook.py --dry-run    # every request body; nothing is sent
ant apply --dry-run -v agents/deadline-watcher/agent.md agents/deadline-watcher/environment.yaml
ant apply agents/deadline-watcher/agent.md agents/deadline-watcher/environment.yaml
```

`ant apply` follows the coordinator's references. It uploads the plugin's
`deadline-tracker` folder as a custom skill, creates the three workers and the
coordinator, creates the environment, and records the IDs in
`claude-lock.json` here. That file is ignored by git in this folder because the
IDs belong to your workspace; keep it, since without it the next `ant apply`
creates duplicates. After a change to the plugin's agent file, run
`python cookbook.py sync`, then `ant apply` again.

Then compare the deployed settings with Anthropic's security guide: in Claude
Code, run `/claude-api managed-agents-secure <agent id>` with the coordinator's
ID from `claude-lock.json`.

## Run it once

```sh
python cookbook.py run --household "/path/to/household"
```

`run` builds the snapshot, uploads the two files, creates a session with the
budget from [`schedule.yaml`](schedule.yaml), opens the event stream, sends
today's date and the outcome, denies any call that waits for approval,
downloads the report, checks it, saves it in `<household>/out/` and deletes
the uploaded files. It prints the session's link in the Console and its list
cost. `--dry-run` prints the upload list and the session body instead;
`--delete-session` deletes the session and its output after saving.

## Schedule it weekly

### Option A: a scheduled deployment

The deployment fires on Anthropic's side every Monday at 07:00 in the
profile's time zone, whether or not your computer is on. Its snapshot files are
replaced on every push, so `cookbook.py` creates and updates the deployment
rather than `ant apply`, and keeps its ID in
`~/.claude/plugins/config/householdbot/deadline-watcher.json`.

```sh
python cookbook.py push --household "/path/to/household" --create   # upload, create, pause
ant beta:deployments run --deployment-id <depl_id>                    # a manual test run
python cookbook.py fetch --household "/path/to/household"             # download, check, save
ant beta:deployments unpause --deployment-id <depl_id>
```

Each week, run `push` after the register changes (or from your own scheduler
on Sunday evening) and `fetch` on Monday. The report states when its snapshot
was taken, so a stale push shows. Firing times can be up to nine minutes late,
and 07:00 stays clear of the hours that daylight-saving changes skip or
repeat. No client is attached to a scheduled session, so a call that waits for
approval holds the run: list runs with
`ant beta:deployment-runs list --deployment-id <depl_id>` and open a session
with `ant beta:sessions connect <session id>` to answer it (deny when in
doubt), or register a `session.status_idled` webhook in the Console.

### Option B: your own scheduler

`run` every Monday from cron, a systemd timer, launchd or Windows Task
Scheduler. The snapshot exists on Anthropic's side only while the session
runs, and the computer has to be on.

```sh
0 7 * * 1  cd /path/to/householdbot/managed-agent-cookbooks/deadline-watcher && /path/to/.venv/bin/python cookbook.py run --household /path/to/household
```

```bat
schtasks /Create /SC WEEKLY /D MON /ST 07:00 /TN "HouseholdBot deadline watch" /TR "C:\path\to\.venv\Scripts\python.exe C:\path\to\householdbot\managed-agent-cookbooks\deadline-watcher\cookbook.py run --household C:\path\to\household"
```

## Cost

Each run is one session, billed to your API account: the tokens of every agent
at its model's list price (the coordinator on Claude Opus 5.5, the reader and
the writer on Claude Sonnet 5.5, the calculator on Claude Haiku 5.5, and the
outcome grader) plus the session's running time. The web tools are off, so
there are no search charges. Current rates are on the
[pricing page](https://platform.claude.com/docs/en/about-claude/pricing).
`run` and `fetch` print each session's list cost, and the Console shows it per
session.

To keep it small:

- The snapshot is small by design: open obligations only, fifteen fields.
- Workflows, inline agents and an advisor are off; each run is four agents
  and one grader.
- Effort is `medium` for the coordinator, reader and writer and `low` for the
  calculator; lower it in the agent files if your reports stay right.
- The outcome loop stops after two iterations. To drop the grader, replace the
  `user.define_outcome` in `schedule.yaml` with a `user.message` that has the
  same text; you lose the independent check.
- Keep it weekly: a daily schedule runs seven sessions a week instead of one.
- `schedule.yaml` caps each session at USD 3.00 (`amount: "300"`, in cents).
  That is a ceiling, not an estimate: a session that reaches it pauses instead
  of spending more. Set it a little above what your first runs cost.

## Turn it off

- Option B: remove the cron line or the scheduled task.
- Option A: `ant beta:deployments pause --deployment-id <depl_id>` stops the
  schedule and can be undone with `unpause`. `python cookbook.py forget`
  pauses it and deletes the uploaded snapshot.
  `ant beta:deployments archive --deployment-id <depl_id>` ends the deployment
  for good.
- Sessions: `ant beta:sessions list`, then
  `ant beta:sessions delete --session-id <id>` for each one you want gone.
- Charges come from sessions. The agent and environment definitions run
  nothing by themselves; archive the agents only if you will never use them
  again, because archiving cannot be undone.

## Files

| Path | What it is |
|---|---|
| `agents/deadline-watcher/agent.md` | The coordinator: the plugin agent's text, then "Running as a Claude Managed Agent". Kept in step by `cookbook.py sync`. |
| `agents/deadline-watcher/environment.yaml` | The sandbox: cloud, `limited` networking, nothing allowed. |
| `agents/register-reader/agent.md` | The reader. |
| `agents/deadline-calculator/agent.md` | The calculator, with the program it runs and a path to the plugin's skill. |
| `agents/report-writer/agent.md` | The writer, with the report layout and both footers. |
| `schedule.yaml` | The weekly schedule, the per-session budget and the kickoff outcome with its starter rubric. Not an `ant apply` file. |
| `steering-examples.json` | Kickoff messages for the scheduled run, a manual run and a smoke test. |
| `cookbook.py` | Offline `check`, `--dry-run`, `snapshot` and `sync`; online `run`, `push`, `fetch` and `forget` with the official `anthropic` SDK. |

## Adapting it

- **Language and country.** The writer has English and Polish labels and
  footers, matching the plugin. For a country without a pack in the plugin, the
  calculator leaves `--country` out: dates already in the register are used,
  holidays are not counted, and the report says so.
- **Models.** Keep the coordinator on Claude Opus 5.5. The reader can move to
  Claude Haiku 5.5 for less cost, or any worker to Claude Opus 5.5 for more
  care; `cookbook.py check` accepts the three.
- **Workflows.** They are off because one register is small work. To turn
  them on, set `workflows: {type: enabled, predefined_agents: [the three
  worker files], inline_agents: {type: disabled}}` in the coordinator, and add
  a sentence to its section saying when a run is worth starting. Every agent
  in a run uses tokens.
- **A record kept on a drive.** A folder synced by Google Drive, OneDrive or
  Dropbox is already a local folder for `cookbook.py`, so no connector is
  needed. If you add a read-only MCP server anyway, put it on the reader
  only, off by default with each read tool named, set
  `allow_mcp_servers: true` in the environment, and keep its credential in a
  vault; `cookbook.py check` enforces the first three. The reader could then
  open anything that connection reaches, originals included.
