# HouseholdBot

**English** · [Polski](README.pl.md)

HouseholdBot is an open-source Claude plugin that runs a household's
paperwork from a conversation. It reads letters, bills, contracts and
policies, files them into a folder the household owns, tracks every deadline,
renewal and cancel-by date with the country's public holidays, and writes a
short brief on the week ahead. Nothing is written, sent or paid without a
household member's yes.

The project applies the structure of Anthropic's open-source vertical plugins
([knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins),
small-business in particular, and
[claude-for-legal](https://github.com/anthropics/claude-for-legal)) to
household administration: a router and a setup interview, shared rules every
skill carries, a profile file, registers with provenance on every date,
approval gates, and a read-only watcher agent. It adds a proof layer: small
scripts count dates and check the registers, so the model judges and the
scripts prove.

## Languages

HouseholdBot speaks **English** (the default) and **Polish**. The setup asks
first; afterwards "in Polish" or "po angielsku" switches at any time. The
language decides the answers, the weekly brief, the date and amount formats
(`Fri 20 Nov 2026`, `PLN 1,240.00` or `pt. 20.11.2026`, `1 240,00 zł`), the
profile template and the decisions log. Documents keep their own language:
an English-speaking family in Poland gets Polish letters explained in English,
with the original quoted, and drafts to Polish offices in Polish with an
English translation. New languages are added as files in `core/i18n/` and
`core/templates/<lang>/`.

## What is in this repository

```
.claude-plugin/marketplace.json   the marketplace (one plugin)
householdbot/                     the plugin
  skills/<skill>/SKILL.md         thirty-four skills, each self-sufficient
  skills/<skill>/shared/          generated copies of rules, country packs, scripts, templates
  agents/                         deadline-watcher and document-reader, read tools only
managed-agent-cookbooks/          deadline-watcher as a Claude Managed Agent (three tiers, weekly)
evals/                            behaviour tests for `claude plugin eval`, synthetic household;
                                  kept outside the plugin package, run by scripts/eval.py
core/                             sources of everything under skills/*/shared/
  rules/                          the rules every skill follows
  locale/PL.*, GB.*               country packs: Poland; England and Wales
  i18n/en.json, pl.json           languages: date and amount formats, notes, log lines
  scripts/dates.py, record.py,    the proof layer (Python standard library)
    statement.py, chores.py
  money/categories.json           spending categories for bank exports
  templates/en/, templates/pl/    household profile and register guide per language
scripts/sync.py                   copies core/ into the skills
scripts/validate.py               repository checks
scripts/package.py                release packages: householdbot.plugin and one zip per skill
tests/                            unit tests for the scripts
docs/architecture.md              the pattern and what a household changes about it
docs/country-packs.md             how a country pack is built and checked
docs/development-plan.md          the staged plan (Polish version: development-plan.pl.md)
```

Each skill carries its own copy of what it needs because on claude.ai and in
the mobile apps only a skill's own folder reaches the sandbox.

## Use it

See [QUICKSTART.md](QUICKSTART.md). In Claude Code:

```
/plugin marketplace add dithiothreitol/householdbot
/plugin install householdbot@householdbot
/householdbot:household-onboard
```

Cowork, claude.ai and the phone are covered in the quickstart.

## Develop it

```
python scripts/sync.py                       # after editing anything in core/
python scripts/validate.py                   # repository checks
python -m unittest discover -s tests         # proof-layer tests
claude plugin validate ./householdbot --profile directory --strict
python scripts/eval.py --scaffold --allow-tools Write Edit --no-publish   # tests run on a staged copy in build/
```

[CONTRIBUTING.md](CONTRIBUTING.md) covers new skills and country packs.
[CLAUDE.md](CLAUDE.md) is the guide for working on the repository with
Claude Code.

## Status

Version 1.0.0-rc.1, the release candidate of 1.0, in English and Polish:
setup, filing, search, deadlines, the weekly brief, profile changes and record
repair; the mailbox, bills, contracts, subscriptions, bank statements, the
tax-return checklist, replies, complaints, cancellations and the monthly
review; the house, the car, insurance, identity documents and travel, school,
health papers, the emergency file, life events, the family calendar, meals,
shopping, chores and the annual review; a dashboard, the household's own
skills and country packs; country packs for Poland and for England and Wales;
an unattended weekly deadline check as a Claude Managed Agent. Version 1.0
follows the pilot in a real household. See [CHANGELOG.md](CHANGELOG.md), and
[docs/architecture.md](docs/architecture.md) for what building it showed.

## License

Apache License 2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
HouseholdBot is an independent project and is not affiliated with or endorsed
by Anthropic.
