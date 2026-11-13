# Setup interview

Ask in the user's language. One question at a time; wait for the answer. One
follow-up is fine when an answer is vague; do not drill further. Any question
can be skipped: the field keeps its `[DEFAULT]` or `[PLACEHOLDER]` value. A
question the member already answered is not asked again: confirm the answer
instead.

**Prefer a document to a typed answer.** "Send a photo of a recent
electricity bill, or just tell me the provider" is the default ask for
anything that is written down somewhere.

The answers fill the sections of `shared/templates/household-profile.md`,
under the same headings.

---

## Part 0 — The essentials (quick and full)

1. **Country and language.** "Which country do you live in, and which language
   should I use with you?" Then propose the currency and time zone that follow
   from the country and ask for a yes. Never infer the country from the
   language.
2. **Who lives here.** "Who is in the household? First names are enough; tell
   me who is an adult and who is a child." Store a birth year for a child only
   if the household wants reminders that depend on age.
3. **What takes the most time or worry.** "What part of the household
   paperwork costs you the most time or worry?" Record the answer in their own
   words. It decides which next steps are offered at the end.
4. **A label.** Propose a short label for the household from what was said
   (surname or first names, and town) and ask for a yes.

The quick path stops here.

---

## Part 1 — What the household owns and uses (full)

5. **Homes.** "Tell me about your home: owned or rented, which town, and how
   it is heated." A second home or a plot of land is a second row.
6. **Vehicles.** "Any cars or other registered vehicles? For each one: what it
   is, who owns it, and, if you know them, when the insurance term ends and
   when the next roadworthiness test is due." Offer to read the dates from the
   policy or the registration document instead.
7. **Providers.** Go through the categories in the profile table by category,
   never by suggesting a company: bank, electricity, gas or heating, water and
   waste, internet and TV, mobile, home insurance, health, school or
   childcare. For each: who it is and how it is paid (direct debit, standing
   order, manual transfer, cash). Skip a category the household does not have.

## Part 2 — How the household decides (full)

8. **Who handles what.** "Who usually deals with which papers?" Fill the
   *Handles* column for each adult.
9. **Two-adult threshold.** "Is there an amount above which you both want to
   agree before anything is paid or signed?"
10. **Who sees the weekly brief.** Adults only, or everyone.
11. **Keeping documents.** Offer the default retention and ask whether to
    change it.

## Part 3 — Tools and rhythm (full)

12. **Connected tools.** Check which of mail, calendar and document storage
    are connected, and whose account each one is. This is a read-only
    inventory: do not pull any household data during it. For a missing
    category, say in one line what connecting it would add, and move on. Never
    recommend one provider over another.
13. **Rhythm.** Which day for the weekly brief, and how it is triggered. Apply
    the scheduling rule in the skill's Step 7.
14. **Output preference.** Short answer in chat with the brief saved as a
    file, or the brief as a rendered page where the environment supports it.

---

## Pacing

- If the user is short on time in the full path, compress to questions 5, 6
  and 9. Those three feed the most reminders and gates.
- Do not read out the whole list of what HouseholdBot can do. Name the two or
  three things that match question 3.
- Repeat back what was understood at the end of each part in one or two
  lines, and correct before moving on.
