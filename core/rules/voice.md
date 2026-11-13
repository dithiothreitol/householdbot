# Voice — letters a member signs and sends

Replies to offices, complaints, cancellations and appeals are drafts. A member
reads, signs and sends them. Every skill that drafts follows these rules.

---

## Language and register

- **The recipient's language.** A Polish office, court, bank or company gets
  Polish. When the household reads another language, give a translation
  after the draft, marked as a translation and not the text to send.
- **The recipient's register.** Formal and plain: in Polish *Szanowni
  Państwo* or *Szanowna Pani / Szanowny Panie*, and *Z poważaniem*; in English
  "Dear Sir or Madam" and "Yours faithfully". No jokes, no emotion, no
  threats, no admissions the member did not make.

## Structure

1. Sender: the member's name and address as the member gives them or as the
   profile lists them, otherwise placeholders (`[imię i nazwisko]`,
   `[adres]`); place and date. Never a name taken from the computer, the
   account, the mail client or version-control settings: the person at the
   keyboard is not necessarily the one who signs.
2. Recipient: name and address from the document being answered. An appeal
   is addressed to the body that decides it and lodged through the office
   that issued the decision, as the instruction section says; the country
   pack shows the form of the addressee block.
3. Reference: the case, decision or customer number the recipient needs.
   When the member wrote it in the conversation, use it as written and add a
   note to check it against the original. A number that sits only in a filed
   document stays a placeholder that says where it is: `[numer sprawy, str. 1
   pisma]`. The identifiers of the personal-data rule (PESEL, NIP,
   identity-document numbers, full account numbers) are always placeholders,
   never typed in by the plugin, whoever wrote them.
4. Subject line: what the letter is (*Odwołanie od decyzji nr …*,
   *Reklamacja*, *Wypowiedzenie umowy*).
5. The request in the first sentence: what the member wants.
6. The facts with dates, from the record, each one the member can confirm.
7. The legal basis only where the country pack names it, with the article,
   and only as far as the pack goes.
8. Attachments, listed.
9. Signature line: the same name as the sender, or `[podpis]`.

## Marked as a draft

Every draft starts with a line saying it is a draft to check, sign and send
("Projekt do sprawdzenia, podpisania i wysłania", "Draft for you to check,
sign and send"), is shown as a quote block or plain text rather than a code
block, and states:

- the **form** the recipient needs (signed letter, email, online form, in
  person) and whether the plugin's draft meets it;
- the **deadline** and what counts for it: posting at the post office of the
  designated operator, or receipt by the other side (the country pack's
  `met_by`), and the date to send by (`do_by`);
- the **proof to keep**: the registered-mail receipt, the confirmation email,
  a copy of the signed letter.

## Never

- Never send, submit or sign. A draft created in a connected mailbox is a
  draft, and is never sent by the plugin. It is created only after the member
  has seen its full text in the conversation and said yes to that text: a
  request such as "put it in my drafts" chooses the place, it does not
  approve words the member has not read yet.
- Never invent a fact, a date, a case number or a legal ground.
- Never let the notes around a draft contradict it: before showing it, check
  that what the notes say was left out is not in the text, and the reverse.
- Never write on behalf of someone outside the household.
- Court papers, tax assessments, enforcement and debt collection get the
  not-advice line before the draft, with the date by which to reach a
  professional.
