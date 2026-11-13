# Gotchas — bills-due

- **A direct debit paid twice.** A bill marked "paid by direct debit" is not
  put on the list; paying it by transfer as well pays it twice.
- **The new account number in a reminder.** Fraudsters send "updated" bills
  with their own account. The ending is compared with the last bill, every
  time.
- **"Paid" is what the member said.** HouseholdBot cannot check the bank. Mark
  the date the member gives, not today by assumption.
- **Overdue first, even when small.** A late fee on a forgotten PLN 40 bill is
  avoidable today.
- **A total without its scope misleads.** "PLN 731.60 for three payments due
  by Fri 27 Nov" is a fact; "you owe PLN 731.60" is not.
- **Tax payments count when the payer's account is debited** in Poland, so a
  transfer on the due date is in time; other payments count when the money
  arrives, so keep the one-day margin.
