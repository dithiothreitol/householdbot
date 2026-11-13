# Gotchas — budget-snapshot

- **Exports list newest first.** The balance check tries both orders; totals
  do not depend on it.
- **One export, several layouts.** Polish banks use semicolons or commas,
  Windows-1250 or UTF-8, a preamble before the header, one amount column or
  separate debit and credit columns. The reader detects them; when it cannot,
  ask for the CSV with column names.
- **A refund is income only on paper.** An Allegro refund lowers shopping, it
  is not earnings; the categories keep it where it belongs.
- **Own transfers are not spending.** Moving money to savings is its own
  category; leave it out of "spent" when the member asks what they spent.
- **The last days of the month may be missing.** An export made on the 28th
  does not show the 30th.
- **Account numbers hide in titles.** Transfer titles carry account and card
  numbers; the reader masks them, and so must every answer.
- **Name the largest category in words.** A table alone left it to the
  reader; one sentence with the category and its share settles it.
