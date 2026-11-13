# Absent is not zero

The most common way a household tool gives a confident wrong answer. A record
is complete only for what was filed into it, and a search sees only what it
was pointed at. A gap reads as good news unless the skill says otherwise.

---

## The shape of it

| What the data did | What a careless answer says | What may be true |
|---|---|---|
| The register has no obligations next week | "Nothing is due next week." | Nothing was registered; the bills are still in the post box |
| A search for "notary deed" finds nothing | "You do not have a notary deed." | It was never filed |
| An obligation has no date | It is left out of the list | It is the one most likely to be missed |
| The mailbox search for an insurer returns nothing | "No letters from the insurer." | The query used the wrong sender address or label |
| The e-delivery box was not checked | "No official letters." | A letter has been sitting there for twelve days, and deemed delivery is near |
| The profile says `Vehicles: none` with a `[DEFAULT]` marker | No car reminders | The quick setup skipped the question |

## The rule

Before reporting an absence or a zero, ask whether the record or the search
could see the thing at all. If it could not, say what was searched and what
was not.

1. **"Not in the record" is the answer, never "does not exist".** Name what
   was searched (`registers/documents.json`, the mailbox for the last 30
   days) and offer the next step: file it, or search further.
2. **An open obligation without a date is listed, not dropped.** It goes in
   its own line, *date unknown*, above the dated items of the same urgency,
   with the question that would give it a date.
3. **An empty week is reported with its coverage.** "Nothing registered for
   next week. The record holds 14 obligations; mail is not connected, so
   anything that arrived by post since Monday is not in it."
4. **A failed read is not an empty read.** A tool error, a file that did not
   parse, a connector that timed out: say so, and do not summarise as if the
   result were empty.
5. **A placeholder is not an answer.** `[PLACEHOLDER]` means unknown and
   `[DEFAULT]` means assumed. Neither is a fact about the household.

## Saying it well

> *"I found no notary deed in the register. If you have one, it was not filed
> yet: send a photo of the first page and I will file it."*

One sentence, and the household knows how far to trust the answer. A named
gap is useful. A fabricated "nothing due" is worse than silence, because the
household acts on it.
