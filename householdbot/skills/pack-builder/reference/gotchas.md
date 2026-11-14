# Gotchas — pack-builder

- **A rule remembered is not a rule found.** Without the official text in
  hand it goes to "to be researched", however sure it feels. A pack that
  states a deadline from memory is worse than one that says it does not know.
- **A bundled pack wins.** A household pack with a bundled code is never
  read. A mistake in a bundled pack is a correction for the plugin; local
  dates are obligations for `deadline-tracker`.
- **Regions differ.** German states, Spanish communities, Swiss cantons, US
  states and the UK's nations have holidays of their own and often their own
  procedure. One pack per region where it matters, with the scope saying so,
  and the region code in the profile's Country.
- **Scotland is not England.** Its bank holidays, courts and deadlines differ,
  so a pack for England and Wales does not cover a Scottish household.
- **Bank holidays are not always public holidays.** The days that move a
  legal deadline can be a different list from the days offices close. Take
  the list the counting law refers to, and note the difference.
- **Orthodox and lunar holidays.** `dates.py` computes Western Easter only.
  Orthodox Easter, Eid, the Lunar New Year and the like go in as `one_off`
  dates, year by year, from the official announcement.
- **Substitute days follow the law, not habit.** `substitute: true` only where
  the law or the official list gives a weekday off for a holiday on a weekend.
- **"Beginning with" counts the first day.** "Within 28 days beginning with
  the date of the notice" gets `start_inclusive: true`; "28 days after" does
  not.
- **The forward roll is the law's margin.** `end_roll: forward` only where
  the law moves an end that falls on a weekend or holiday; the household still
  plans to the day before.
- **Name the version read.** Rules change: the consolidated text, its date,
  and any amendment that takes effect later.
- **The pack is not the household's.** No names, addresses, providers or
  amounts of the household in it, so it can be shared as it is.
- **A clean check is not a verified pack.** `check-pack` proves the shape and
  computes the holidays; a person still compares the holiday list with the
  official one, and every rule still needs its source.
- **A written pack is in use.** The other skills read it as soon as it is in
  `packs/`; a draft with uncertain holidays says so in `sources.uncertain`,
  and everything from it reaches the household marked "verify".
