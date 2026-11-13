# Gotchas — tax-season-organizer

- **The pre-filled return is not always complete.** It knows the forms the
  payers sent; it does not know reliefs the household has not claimed.
- **Joint filing is a choice, not a default.** Ask; the pack names the
  condition and the article.
- **Two jobs, two forms.** Each payer sends its own information form; a
  missing one is the most common cause of a correction later.
- **The tax year is last year.** "PIT for 2026" is filed in 2027.
- **A relief needs proof the household keeps,** not the tax office: invoices,
  receipts, confirmations. List where each one is.
- **Refund amounts are not promised.** HouseholdBot does not compute tax.
- **The pack is a file, not a search.** In testing, with no shell and no
  search tool, an answer said it could not find the pack and named no
  forms. The pack is at `shared/locale/<CC>.md` in this skill's folder;
  open it with Read.
