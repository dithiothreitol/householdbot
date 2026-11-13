# Gotchas — household-onboard

- **Language is not country.** A member writing Polish may live in Germany,
  and an English-speaking family may live in Poland. Ask for the country;
  propose currency and time zone from it.
- **English is the default, not a guess.** Without a request or a Polish
  opening message, set up in English and offer Polish in the first line. Once
  chosen, the language goes into the profile and every skill follows it.
- **The folder is created after the yes, not before.** Choosing a location in
  Step 2 creates nothing. `record.py init` runs only after the profile is
  approved.
- **An existing record is never re-initialised.** `record.py init` refuses
  when registers exist; that refusal is correct. Offer `household-customize`
  or `household-doctor` instead.
- **One paper beats ten questions.** When a member is unsure of a provider or
  a date, ask for the document rather than guessing a default.
- **A child's birth year only on purpose.** Store it only when a reminder
  depends on age (an identity card for a child, school enrolment). Never a
  full date of birth.
- **"Weekly" stored is not "weekly" scheduled.** Writing the preference into
  *Rhythm* schedules nothing. Say which one happened.
- **A connector listed is not a connector working.** Mark ✓ only after a call
  succeeded in this session.
