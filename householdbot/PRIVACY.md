# Privacy

**English** · [Polski](PRIVACY.pl.md)

HouseholdBot is a set of instructions, two local scripts and a connector list.
It has no server, no account and no analytics.

## Where household data goes

- **The household folder.** Profile, registers, filed originals, briefs and
  the decisions log live in a folder the household chooses. HouseholdBot reads
  and writes there and nowhere else, apart from one pointer file
  (`~/.claude/plugins/config/householdbot/location.md`) that stores the
  folder's path.
- **Claude.** Documents and questions are processed by Claude in the
  household's own Claude account, under that account's terms.
- **Connected services.** Gmail, Google Calendar and Google Drive are used only
  if the household connects them, under Google's terms. HouseholdBot reads
  through them on request and writes through them only after a yes.

## What HouseholdBot keeps out of its own files

National identity and tax numbers, account and card numbers, document numbers,
passwords and codes are never copied into the registers; an entry points to
the page of the original instead. Health details stay out of briefs and
calendar entries.

## Removing data

Delete the household folder and the pointer file. Nothing else holds a copy
made by HouseholdBot.
