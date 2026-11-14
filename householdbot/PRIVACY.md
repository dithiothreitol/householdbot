# Privacy

**English** · [Polski](PRIVACY.pl.md)

HouseholdBot is a set of instructions, four local scripts and a connector list.
It has no server, no account and no analytics.

## Where household data goes

- **The household folder.** Profile, registers, filed originals, briefs and
  the decisions log live in a folder the household chooses. HouseholdBot reads
  and writes there and nowhere else, apart from one pointer file
  (`~/.claude/plugins/config/householdbot/location.md`) that stores the
  folder's path. A change waiting for a yes is kept in
  `registers/.pending/` for at most 30 minutes and holds only what the write
  would hold; a change made before a record exists (setup) waits next to the
  pointer file. The calendar file in `exports/` is shared only by the member
  who imports it.
- **Claude.** Documents and questions are processed by Claude in the
  household's own Claude account, under that account's terms.
- **Connected services.** Gmail, Google Calendar and Google Drive are used only
  if the household connects them, under Google's terms. HouseholdBot reads
  through them on request and writes through them only after a yes.

## What HouseholdBot keeps out of its own files

National identity and tax numbers, account and card numbers, document numbers,
passwords and codes are never copied into the registers; an entry points to
the page of the original instead. Health details stay out of briefs and
calendar entries. Foods the household keeps off its meal plan are stored only
with an adult's consent, without the reason, and never appear in lists,
calendar entries or briefs. The emergency file says where things are and whom
to call, never a number or a password.

## Removing data

Delete the household folder and the pointer file. Nothing else holds a copy
made by HouseholdBot.
