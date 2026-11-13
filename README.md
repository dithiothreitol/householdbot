# HouseholdBot

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

## What is in this repository

```
.claude-plugin/marketplace.json   the marketplace (one plugin)
householdbot/                     the plugin
  skills/<skill>/SKILL.md         eight skills, each self-sufficient
  skills/<skill>/shared/          generated copies of rules, country packs, scripts, templates
  agents/                         deadline-watcher (read-only), document-reader (no write tools)
  evals/                          behaviour tests for `claude plugin eval`, synthetic household
core/                             sources of everything under skills/*/shared/
  rules/                          the rules every skill follows
  locale/PL.md, PL.json           the Polish country pack
  scripts/dates.py, record.py     the proof layer (Python standard library)
  templates/                      household profile and register guide
scripts/sync.py                   copies core/ into the skills
scripts/validate.py               repository checks
tests/                            unit tests for the scripts
docs/development-plan.md          the staged plan (Polish)
```

Each skill carries its own copy of what it needs because on claude.ai and in
the mobile apps only a skill's own folder reaches the sandbox.

## Use it

See [QUICKSTART.md](QUICKSTART.md). In Claude Code:

```
/plugin marketplace add <path to this repository>
/plugin install householdbot@householdbot
/householdbot:household-onboard
```

## Develop it

```
python scripts/sync.py                       # after editing anything in core/
python scripts/validate.py                   # repository checks
python -m unittest discover -s tests         # proof-layer tests
claude plugin validate ./householdbot --profile directory --strict
cd householdbot && claude plugin eval . --scaffold --allow-tools Write Edit --no-publish
```

[CONTRIBUTING.md](CONTRIBUTING.md) covers new skills and country packs.
[CLAUDE.md](CLAUDE.md) is the guide for working on the repository with
Claude Code.

## Status

Version 0.1: the core. Setup, filing, search, deadlines, the weekly brief,
profile changes and record repair, with the Polish country pack. Next stages
add money and correspondence (bills, contracts, subscriptions, bank
statements, replies to offices, complaints, cancellations), then home, family
and daily life (vehicles, health, school, insurance overview, identity
documents, life events, meals, shopping and chores), then more countries and
a hosted watcher. See [CHANGELOG.md](CHANGELOG.md).

## License

Apache License 2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE).
HouseholdBot is an independent project and is not affiliated with or endorsed
by Anthropic.
