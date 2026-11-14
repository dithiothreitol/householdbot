# Pack format

A household pack has the shape of the bundled packs, so every skill and
script reads it the same way. Two files in the household folder:

- `packs/<CC>.md`: the rules in words, for the model, by section.
- `packs/<CC>.json`: the data `dates.py` and `record.py` read: holidays,
  counting rules, windows, recurring dates.

`<CC>` is an ISO 3166-1 code for a country (`DE`) or an ISO 3166-2 code for a
region (`GB-SCT`, `DE-BY`).

## The JSON

Every `{…}` is replaced or the key left out; nothing here is a rule for any
country.

```json
{
  "pack": "{CC}",
  "scope": "{what the pack covers, and what it does not}",
  "schema_version": 1,
  "reviewed": "{YYYY-MM-DD}",
  "official_language": "{ISO 639-1, e.g. de}",
  "currency": "{ISO 4217}",
  "time_zone": "{IANA name}",
  "weekend": ["saturday", "sunday"],
  "holidays": {
    "law": "{act and section that sets the holidays}",
    "source": "{URL of the official text or the official list}",
    "fixed": [
      {"date": "{MM-DD}", "name": "{local name}", "name_en": "{English name}", "substitute": true}
    ],
    "easter_relative": [
      {"offset": -2, "name": "{local name}", "name_en": "Good Friday"}
    ],
    "weekday_rules": [
      {"month": 5, "weekday": "monday", "nth": 1, "name": "{local name}", "name_en": "{English name}"}
    ],
    "moved": [
      {"year": 2027, "rule": "{the name of the holiday, exactly as above}", "to": "{YYYY-MM-DD}"}
    ],
    "one_off": [
      {"date": "{YYYY-MM-DD}", "name": "{local name}", "name_en": "{English name}"}
    ]
  },
  "counting_rules": {
    "calendar": {"title": "Plain calendar arithmetic, no statutory roll", "end_roll": "none", "law": null, "met_by": null},
    "administrative": {"title": "{…}", "end_roll": "forward", "law": "{act, article}", "met_by": "{what meets the deadline: posting, receipt, online submission}"}
  },
  "deemed_delivery": [
    {"id": "{id}", "title": "{…}", "days": 14, "from": "{the day the period starts}", "law": "{act, article}", "note": "{…}"}
  ],
  "response_windows": [
    {"id": "{id}", "title": "{English, local term in brackets}", "amount": 28, "unit": "days", "from": "{the event}", "counting": "administrative", "start_inclusive": true, "law": "{act, article}"}
  ],
  "recurring": [
    {"id": "{id}", "title": "{…}", "kind": "payment", "category": "home", "dates": ["{MM-DD or MM-L}"], "window_opens": "{MM-DD}", "counting": "tax", "lead_time_days": 14, "applies_when": "{…}", "law": "{act, article}"}
  ],
  "retention": [
    {"id": "{id}", "title": "{…}", "keep_years": 6, "from": "{…}", "permanent": false, "law": "{act, article}", "suggested": false, "note": "{…}"}
  ],
  "life_events": [
    {"id": "{id}", "title": "{…}", "windows": ["{response window ids}"], "tasks": [{"title": "{…}", "law": "{…}", "note": "{…}"}]}
  ],
  "transit_buffer_days": {"instant": 0, "online-form": 0, "bank-transfer": 1, "post-domestic": 5, "post-international": 10},
  "sources": {"reviewed_with": "{which official services, read on which date}", "uncertain": ["{one line per unsure item}"]}
}
```

### What each part needs

- **Required:** `pack`, `reviewed`, `weekend`, `holidays`, `counting_rules`.
  `counting_rules` may hold only `calendar` until the others are researched;
  skills then compute no statutory windows, which is the honest result.
- **Weekend:** English weekday names in lower case.
- **Holidays:** `fixed` dates as `MM-DD`; `substitute: true` only where the
  law or the official list gives a weekday off for a holiday on a weekend
  (the next weekday that is not already a holiday, in date order);
  `easter_relative` counts from Western Easter Sunday; `weekday_rules` take
  `month` (1 to 12), `weekday` (lower-case English name) and `nth` (1 the
  first, 2 the second, -1 the last; never 0); `moved` names a holiday rule by
  its exact `name`; `from_year` and `to_year` on any rule for a holiday that
  began or ended.
- **Counting rule ids** are generic so skills work across countries:
  `administrative`, `tax`, `civil`, `court`, `calendar`. Each has `end_roll`
  (`forward` or `none`) and `law`; `start_inclusive: true` when the day of the
  event counts as day one.
- **Response windows:** `unit` is one of `days`, `weeks`, `months`, `years`,
  `business_days`; `amount` a whole number from 1; `counting` names a rule in
  `counting_rules`; `law` always; `start_inclusive` as above; `met_by` when
  something other than the general rule meets it.
- **Recurring:** `dates` as `MM-DD`, or `MM-L` for the last day of the month;
  `window_opens` the same; `counting` a known rule; `law` always;
  `applies_when` in words the profile can answer.
- **Deemed delivery:** `days` a whole number; `law` always.
- **Retention:** `law`, or `"suggested": true` with the reasoning in `note`.
- **Life events:** every id in `windows` exists in `response_windows`; a
  `title` always.
- **Ids:** lower case with hyphens, unique within their section.
- **Titles:** English with the local term in brackets
  ("Objection (*Widerspruch*)"); a `title_pl` may follow for a Polish
  household.
- **`transit_buffer_days`** are planning margins for the household, not law;
  set the post values to what the country's post really takes.

## The Markdown's first lines

```
# Country pack — {country or region} ({CC})

**Reviewed:** {YYYY-MM-DD}. **Language:** {…}. **Currency:** {…}. **Time zone:** {…}.
**Scope:** {what it covers and what it does not}.

A household pack, built with pack-builder from official sources. Each line
below is a reminder of a rule as understood at the review date. Dates,
amounts and procedures change; the letter in hand and the official source
control. Everything taken from this file reaches the household tagged
`household pack — verify`.
```

The `Reviewed:` date is the same as the JSON's. Then the sections in the
order SKILL.md lists them, each as a table (`| Topic | Rule | Law |`, or
`| Document | Window | Law |` for windows), like the bundled packs. A section
not researched yet keeps its heading and the line "To be researched." The
*Sources* section lists each official text with its URL and the date it was
read, then *Uncertain*, one line per item.

## The check by hand

The same checks `check-pack` makes, for a session without Python:

1. The keys `pack`, `reviewed`, `weekend`, `holidays` and `counting_rules`
   are there.
2. Every weekend day is a lower-case English weekday name.
3. Every counting rule has `end_roll` `forward` or `none`.
4. Every entry of `response_windows`, `recurring`, `deemed_delivery`,
   `retention` and `life_events` has an `id`, unique in its section.
5. Every response window and recurring entry names a counting rule that
   exists; every response window, recurring entry and deemed delivery names
   its law.
6. Response windows: `unit` from the list above, `amount` a whole number from
   1.
7. Recurring: `dates` present, each `MM-DD` or `MM-L` and a real day.
8. Deemed delivery: `days` a whole number; `unit`, when present, `days` or
   `business_days`; `end_roll`, when present, `forward` or `none`.
9. Life events: every window id exists; a `title`.
10. Retention: a `law`, or `"suggested": true`.
11. Holidays: every `moved.rule` is the name of a fixed, Easter-relative or
    weekday rule; no `nth` of 0; the year's list can be computed.
12. The Markdown has *Public holidays*, *How deadlines are counted*, *Scam
    patterns* and *Sources*, and its `Reviewed:` date equals the JSON's.
13. `sources` is there, with `reviewed_with` and `uncertain`.

## The year's holidays by hand

- **Fixed:** the date in that year.
- **Substitute days:** in date order, a holiday marked `substitute: true` that
  falls on a weekend day gives the next weekday that is not a holiday or
  another substitute (25 Dec on a Saturday gives Monday 27 Dec; 26 Dec on the
  Sunday then gives Tuesday 28 Dec).
- **Easter Sunday** (Western), every step written down, for the year Y
  (div is whole division, mod the remainder):
  a = Y mod 19; b = Y div 100; c = Y mod 100; d = b div 4; e = b mod 4;
  f = (b + 8) div 25; g = (b − f + 1) div 3;
  h = (19a + b − d − g + 15) mod 30; i = c div 4; k = c mod 4;
  l = (32 + 2e + 2i − h − k) mod 7; m = (a + 11h + 22l) div 451;
  month = (h + l − 7m + 114) div 31; day = ((h + l − 7m + 114) mod 31) + 1.
  For 2030: a 16, b 20, c 30, d 5, e 0, f 1, g 6, h 28, i 7, k 2, l 2, m 0,
  so month 4 and day 21: Sunday 21 April 2030.
- **Easter-relative:** Easter Sunday plus the offset in days.
- **Weekday rules:** the nth such weekday of the month; -1 is the last.
- **Moved and one-off:** as listed for that year.
- Each date with its weekday counted from a known date, and the whole list
  tagged `model calculation — verify`.
