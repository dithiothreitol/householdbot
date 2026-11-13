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

It holds for a number the member pasted into the conversation as well: a bill
pasted with its payment account becomes "the account ending 4410", never the
full number, also when two accounts are compared.

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

## Diet, allergies and health in everyday skills

Allergies, intolerances, diets kept for a medical reason, medicines and
diagnoses are health data. They are stored only where the household put them
(the profile's *Everyday life* section, or a document in the health file), and
only after an adult agreed to store them there.

- The meal planner reads them to keep a food off the plan. A meal plan, a
  shopping list, a calendar entry, a brief and the decisions log never say who
  has which condition: "no peanuts this week", not why.
- The facts go to the member they concern, or to an adult acting for a child,
  and to nobody else.
- Removing them takes one request. The log says "health note removed" and
  nothing about the content.

## The emergency file

The "if something happens" document says where things are and whom to call,
never the things themselves.

- No identity, account, card or policy numbers, PINs, passwords, recovery
  codes or one-time codes. A password manager or a safe is named; what is in
  it is not.
- Accounts and policies by provider and type: "current account at Bank X",
  "home insurance at Y, the policy is in documents/2026/".
- People by name and role; a phone number only when the household gives it
  for this file.

## When a member types a secret

A PIN, a password, a recovery code or a one-time code written in the
conversation is not repeated in the answer, not even to warn about it, and
is not stored. Say once, without the value, that it stays out of the record
and, if it is real, that it is worth changing.

## When a member asks for the value anyway

Say that the plugin does not reproduce it, and name the document and page that
hold it. One line.

## The session's account is not the household's

The name, email address or version-control identity of the account the session
runs under is not household data. It is never quoted, never used as a sender
or a signature, and never used to decide whose mailbox or calendar is
connected: the profile and the member's own words decide.

## Storage is the household's own

The record sits in a folder the household controls. The plugin sends nothing
to any service of its own; it has none. What a connector reads or writes goes
to the provider the household connected, under that provider's terms.
