# Gotchas — reply-to-letter

- **An appeal goes through, not to.** In Polish administrative cases the
  appeal is addressed to the higher body but filed with the office that issued
  the decision. The instruction section says which.
- **The delivery date starts the clock.** Ask for it; when nobody knows, use
  the date on the letter as the conservative start and say so.
- **Posting counts for offices, receipt for companies.** A reply to an office
  posted at the designated operator on the last day is in time; a reply to a
  company must arrive.
- **A request for "explanations" is not an accusation.** Answer what was
  asked, with documents; do not volunteer more.
- **The translation is not the letter.** Mark it, so nobody sends the English
  text to a Polish office.
- **Personal identifiers are placeholders.** The plugin never types a PESEL,
  a NIP or an identity-document number into a draft. A case number the member
  wrote in the message is used with a note to check it; one that sits only in
  a filed document stays a placeholder. In testing, one draft carried the
  number while its note said it was left out: check the note against the text.
- **The addressee block names the appeal body first.** In testing a draft
  put *Wójt Gminy* at the top with the appeal body in brackets. The block
  reads *Samorządowe Kolegium Odwoławcze w … za pośrednictwem Wójta Gminy …*;
  the letter itself goes to the office.
- **The signature comes from the household.** In testing an email was
  signed with the name of the account the session ran under. Use the
  member's name from the profile, or `[imię i nazwisko]`.
- **"Put it in my drafts" is not a yes to the text.** Show the email
  first; create the mailbox draft after the member approves those words.
- **No shell is not "no record".** In testing an answer said it could not
  find the household because the scripts did not run. Read
  `household-profile.md` and `registers/` in the working folder directly.
