# Gotchas — deadline-tracker

- **The weekday is computed, never recalled.** A model's memory of which
  weekday a date falls on is wrong often enough to matter. Take it from the
  script output; without the script, derive it step by step from a known date.
- **Holidays move.** Easter, Pentecost and Corpus Christi change every year,
  and a country can add a holiday (Poland added 24 December from 2025).
  Recompute from the pack, do not remember.
- **Two dates, two purposes.** The law may move a deadline that ends on a
  holiday forward (`due_date`); the household plans to the working day before
  the unmoved end (`do_by`). Report both, plan to one.
- **Payments count on receipt unless the pack says otherwise.** A bank
  transfer sent on the due date may arrive the next working day; the buffer
  is 1 day. For tax payments in Poland the debit of the payer's account
  counts, so the buffer can be 0.
- **An empty week is not an all-clear.** "Nothing registered" plus what the
  register covers.
- **"I paid it" for a bill not in the register.** Offer to add it as done
  only if the member wants a record; never invent a past obligation.
- **A recurring free-text schedule is not guessed.** "15 Mar, 15 May, 15 Sep,
  15 Nov" gives the next date from the list, not from adding a month.
