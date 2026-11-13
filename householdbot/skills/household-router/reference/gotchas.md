# Gotchas — household-router

- **An upload with no words is a filing request.** A photo or PDF sent with no
  text goes to `file-document`, not to a question about what to do with it.
- **"What do I have to pay" is a deadline question, not a budget question.**
  Route to `deadline-tracker`; the budget skills come later.
- **A forwarded payment request is screened first.** "Pay this" with a link or
  new bank details goes to `file-document`, which screens before anything
  else. Never route it straight to a payment list.
- **A specific task beats onboarding.** A first-time member who arrives with a
  letter gets the letter read; setup is offered after, in one line.
- **Language follows the profile, not the request.** A household that set
  Polish gets Polish even when a member types one English phrase. Without a
  profile, answer in the language of the message.
