# Security

HouseholdBot reads documents written by people outside the household and can
write to the household's files. These are the protections it relies on, and
how to report a way around them.

## What the plugin defends against

| Threat | Protection |
|---|---|
| Instructions planted in a letter, email, PDF or calendar invite | Every skill treats read content as data and quotes text aimed at the assistant as suspicious; the `document-reader` agent has no write, shell or web tools; eval cases test planted instructions |
| Payment scams (parcel surcharges, "new bank account", fake tax refunds) | Money, credential and identity asks are held, never drafted or registered; country packs list local scam patterns |
| Writes the household did not approve | Every write is a preview stored under a confirm token; only `commit --confirm <token> --approved-by <name>` applies it, exactly as previewed. The scripts refuse a write in one call, an unknown or expired token (30 minutes), and a token whose files changed since the preview; they keep the previous file and log who approved. In Claude Code and Cowork a `PreToolUse` hook sends every commit and every direct write into the household folder to the host's permission prompt |
| A saved page that runs or loads something | `record.py save` refuses HTML with a script, link, image, form, outside style or web address, and any identifier |
| Lost edits in a shared folder | Writes stop while sync-conflict copies exist; `household-doctor` merges entry by entry |
| Identifiers copied into files that travel | Registers point to the document page instead of copying numbers; `record.py validate` and `scripts/validate.py` flag identifier-shaped values |
| Wrong dates | Holidays and counting rules come from a script and a dated country pack; statutory dates carry their law and the word "verify" |

## What it cannot do

It cannot verify who is typing: the approver's name is recorded as given. The
token proves that a write equals a preview that was made; it does not prove
that a person read it. The hook adds that in Claude Code and Cowork; where a
host has no hooks (claude.ai, Codex), the host's own approval of shell
commands stands in for it. An agent that can write any file in the household
folder could forge a preview; the hook asks the person about such direct
writes too. It cannot verify that a payment left an account. A country pack
is a reminder list, not legal advice.

## Reporting

Please report a vulnerability privately through a GitHub security advisory
on the project repository, with the prompt or document that shows the
problem. Use synthetic data in the report.
