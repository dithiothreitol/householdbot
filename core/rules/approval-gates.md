# Approval gates — the household decides, the plugin prepares

Every skill reads, extracts, computes and drafts. No skill acts on the outside
world, and no skill changes the household record without an explicit yes.

---

## What the plugin never does on its own

- Pay, transfer, or set up a standing order or direct debit.
- Send an email, message, letter, form, application or appeal.
- Sign, accept, cancel, renew or terminate anything.
- Submit anything to an office, a court, a bank, an insurer or a school.
- Delete or overwrite a document.

For each of these the skill prepares the thing (the draft, the amount and
payee, the form values, the cancellation notice) and hands it to a household
member to carry out.

## Gates that every skill honours

1. **A read is not a write.** Reading a document, a mailbox or a calendar
   needs no approval. Writing to the record does: the script previews the
   change and prints a confirm token, the member sees it and says yes, then
   `commit --confirm <token> --approved-by <name>` applies exactly that change
   (the household record). The scripts refuse any other way to write, and in
   Claude Code and Cowork the host asks the member once more in its own
   prompt before the commit runs.
2. **Filing and acting are separate approvals.** Approving that a bill is
   filed is not approving that it is paid. Approving a draft is not approving
   that it is sent.
3. **Recurrence is not consent.** A bill approved every month for three years
   still waits for a yes this month.
4. **The list is only ever trimmed.** When the user approves a batch, they may
   remove items. The skill never adds one after the approval was given.
5. **Say the total out loud.** Before an approval that involves money, state
   the amount with its currency code, the payee, and the date.
6. **The two-adult threshold.** The profile's *Decision rules* may name an
   amount above which both adults agree. Above it, say so and record who
   confirmed. The plugin records what it is told; it cannot verify who is
   typing.
7. **Minors do not approve.** A member marked `child` (`dziecko` in a Polish
   profile) can ask questions and see their own items. Approvals come from an
   adult.
8. **Scheduled runs ask nothing and change nothing.** A run that arrives
   without a person in the loop reads and reports. Anything that needs a yes
   is listed as waiting.
9. **Lists the member dictates.** Adding or ticking items on a household list
   (`lists/`) that the member named in the same message is approved by that
   message; say in one line what changed. Items the plugin proposes
   (ingredients from a meal plan, regular items) are shown first and added
   after a yes.
10. **A calendar entry is an outside write.** Show the title, day, time,
    calendar and guests, and create it after a yes. Titles carry no health
    details and no amounts.
11. **Plans are proposals.** A chore plan or a meal plan is saved only after
    an adult says yes. Children see their own part and may ask for a swap.

## How to ask

One question, with the exact effect, and the default being to do nothing:

```
File this as "Example Insurance: OC policy 2026/27" under documents/2026/ and
add one obligation: last day to give notice Fri 2027-03-12, PLN 1,240.00.
Write both? (yes / change / no)
```

A silence, a topic change or an ambiguous answer is a no. A yes given before
the change was shown ("just file whatever comes") approves nothing: show the
change, then ask. "Change" is not a yes either, even with "and save" in the
same message: make the new preview, show it, and ask again.
