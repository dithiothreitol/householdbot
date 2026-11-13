# Personal data — the register points, it does not copy

Household papers carry more about a person than any output needs. The rule is
the same in every skill: use a field to do the work, and leave the value in
the document it came from.

---

## Never reproduced, in any output or register

Not in chat, not in a brief, not in an artifact, not in `documents.json` or
`obligations.json`, not in a draft, not in a calendar entry:

- National identity and tax numbers (for example PESEL, NIP, SSN, NINO).
- Identity card, passport and driving licence numbers, and images of them.
- Full bank account and card numbers, security codes and expiry dates. The
  last four digits identify an account or card; nothing more is needed.
- Passwords, PINs, one-time codes, recovery phrases, login links.
- Full dates of birth. The profile stores `adult` or `child` and, where the
  household wants age-based reminders, a birth year.

When a document carries one of these, the register entry says where it is:
`"policy number: see page 1"`. The value is read for the step that needs it
and then dropped. It is not echoed back to confirm. `record.py validate` warns
when a register value looks like an identifier, without printing it.

This holds when reporting a problem too. When a register, a profile or a
draft holds an identifier where it should not, name the entry and the field
("the notes of doc-2026-0002 hold a PESEL number"), never the value.

## Kept to the output that needs it

- **Health details** (diagnoses, medication, test results, reasons for leave)
  appear only in an answer to the person concerned or an adult acting for a
  child, and never in a weekly brief, a shared calendar entry or a posted
  message. A brief says "appointment, Thu 10:30", not what it is for.
- **Children.** Store the minimum: a first name or label, `child`, and the
  school or clinic only where a deadline depends on it.
- **Income, debt and benefit amounts** appear in the skill that works on them
  and not in a brief shared with the whole household unless the profile says
  briefs are for adults only.
- **Other people.** Landlords, neighbours, employers and relatives outside the
  household appear by name and role only.

## When a member asks for the value anyway

Say that the plugin does not reproduce it, and name the document and page that
hold it. One line.

## Storage is the household's own

The record sits in a folder the household controls. The plugin sends nothing
to any service of its own; it has none. What a connector reads or writes goes
to the provider the household connected, under that provider's terms.
