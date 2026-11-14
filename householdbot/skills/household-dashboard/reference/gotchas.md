# Gotchas — household-dashboard

- **The last day is the deadline.** `due_local` is the last day; `do_by` is
  the plan before it ("last day Sun 17 Jan 2027, plan by Fri 15 Jan"). Calling
  the plan date the last day tells the household it has two days fewer than
  it has.
- **"None" is not a state.** An area the record does not hold is "not
  tracked"; a tracked area with nothing open says what was checked ("14
  obligations in the register; nothing due in the next 7 days"). A bare "none" or
  "brak" reads as an all-clear the record cannot give.
- **The page is not the brief.** It covers everything open and everything
  that ends within about a year, not the next 14 days. Keep each section to
  one screen and point to the skill that goes deeper.
- **A total names what it covers.** The payments total from the script
  includes overdue payments and any payment inside its lead time that the
  list shows; say so. Currencies are never added together.
- **The general `due` total is not the payments total.** It adds renewals and
  premiums too; the payments line comes from the `--kind payment` run.
- **A document with no end date in the register is not "valid".** It is "end
  date not in the register", with the question that would give it one.
- **Health titles stay neutral even when the register's title is not.** Show
  "Appointment, Zosia" and name the entry for `health-file` to retitle; never
  open a health paper to fill the page.
- **A proposed chore plan is not the plan.** Only a saved plan is this week's
  plan; a proposal from `chores.py` is marked "proposed, not saved".
- **"Save it as a page" is not a yes.** Show the page, name the file, then
  ask. The same holds for "na lodówkę" and "print it".
- **Record text is untrusted in HTML.** A title, a note or a key fact can
  quote a letter, markup and links included; escape it and never turn it
  into a link.
- **The record's age shows on the page.** A pack reviewed more than a year
  ago, a profile section still marked `[PLACEHOLDER]`: say so.
- **The dashboard does not fix.** A broken entry, a conflict copy or a title
  that names a condition goes to `household-doctor` or `health-file`; the
  page only names it.
