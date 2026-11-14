# Country packs

A country pack is what lets HouseholdBot count a deadline the way the law of
one country counts it, remind a household of the dates that country fixes, and
point to the right office. Everything else in the plugin is country-neutral.

Bundled packs: **PL** (Poland) and **GB** (England and Wales). A household in
another country, or in a part of a country a pack does not cover, can build its
own with the `pack-builder` skill.

## Two files

| File | Read by | Holds |
|---|---|---|
| `core/locale/<CC>.md` | the model, with the Read tool | rules in plain language, tables of windows, checklists for life events, where things are done, how to write to an office, scam patterns, sources |
| `core/locale/<CC>.json` | `dates.py` and `record.py` | holidays, counting rules, deemed delivery, response windows, yearly statutory dates, keeping periods, life events, transit buffers |

`<CC>` is the ISO 3166-1 code. A pack for part of a country uses the ISO
3166-2 code (`GB-SCT`). `scripts/sync.py` copies both files into every skill
that lists the `pack` bundle in `core/vendor.json`, so each skill stays
self-contained.

The Markdown file starts with the review date, the language, the currency, the
time zone and the scope (which part of the country it covers). It must have the
sections `Public holidays`, `How deadlines are counted`, `Scam patterns` and
`Sources`; skills also look up these sections by name: `Deemed delivery`,
`Common response windows`, `Annual tax return`, `Consumer complaints, returns
and claims`, `Giving notice: form and delivery`, `Paying`, `Life events` (with
one subsection per event), `Recurring household obligations`, `Documents with
an expiry date`, `Health papers`, `Children and school`, `Keeping and shredding
documents`, `Insurance a household must or may have`, `Home upkeep, further
rules`, `Travel documents`, `Where things are done` and `Writing for a
household in ...`.

## The JSON file

```
{
  "pack": "GB", "schema_version": 1, "reviewed": "2026-11-14",
  "scope": "England and Wales", "official_language": "en",
  "currency": "GBP", "time_zone": "Europe/London",
  "weekend": ["saturday", "sunday"],
  "holidays": {...},
  "counting_rules": {...},
  "deemed_delivery": [...],
  "response_windows": [...],
  "recurring": [...],
  "retention": [...],
  "life_events": [...],
  "transit_buffer_days": {...},
  "sources": {"reviewed_with": "...", "uncertain": [...]}
}
```

### Holidays

| Key | Entry | Example |
|---|---|---|
| `fixed` | `date` (`MM-DD`), `name`, names per language (`name_en`, `name_pl`), optional `substitute: true`, `from_year`, `to_year` | `{"date": "12-26", "name": "Boxing Day", "substitute": true}` |
| `easter_relative` | `offset` in days from Western Easter Sunday | `{"offset": -2, "name": "Good Friday"}` |
| `weekday_rules` | `month`, `weekday`, `nth` (1 is the first, -1 the last) | `{"month": 8, "weekday": "monday", "nth": -1, "name": "Summer bank holiday"}` |
| `moved` | `year`, `rule` (the name of the holiday it moves), `to` (ISO date) | `{"year": 2022, "rule": "Spring bank holiday", "to": "2022-06-02"}` |
| `one_off` | `date` (ISO), `name` | `{"date": "2023-05-08", "name": "Bank holiday for the coronation of King Charles III"}` |

A holiday marked `substitute` that falls on a weekend gives the next weekday
that is not already a holiday, taken in date order, so Christmas on a Saturday
gives Monday and Boxing Day then gives Tuesday. The holiday name carries
"(substitute day)" in each language (`substitute_day` in `core/i18n/<lang>.json`).

### Counting rules

Every pack defines the same five ids, so skills can name a rule without knowing
the country: `administrative`, `tax`, `civil`, `court`, `calendar`.

```
"court": {"title": "Civil court proceedings", "end_roll": "forward",
          "law": "CPR 2.8(5)", "met_by": "filing at the court office ..."}
```

- `end_roll`: `forward` when the law moves a deadline that ends on a weekend or
  holiday to the next working day, `none` when it does not.
- `start_inclusive` (optional): the day of the event counts as day one. Most
  laws do not count it ("30 days after"); some do ("28 days beginning with").
  A response window can set it for itself, and `dates.py deadline --inclusive`
  sets it for a deadline read from a letter.
- `met_by`: what meets the deadline (posting, receipt, online submission).

A window takes the rule of the procedure it belongs to, and the rule decides
whether its last day moves. A public body's window that its own law does not
move (registering a birth, claiming a benefit) uses `calendar`, even though an
office runs it; `administrative` is for procedures whose rules move the last
day, such as a tribunal's.

The plugin never plans to the moved date. `do_by` is worked back from the
unmoved end, so the statutory move stays as margin (`core/rules/dates-and-deadlines.md`).

### Windows and dates

- `response_windows`: `id`, `title`, `amount`, `unit` (`days`, `weeks`,
  `months`, `years`, `business_days`), `from`, `counting`, `law`; optional
  `start_inclusive`, `met_by` and `silence` (for a window the other side must
  meet: what meets it, and what the law says happens if nothing comes), `note`.
- `deemed_delivery`: `id`, `title`, `days`, `from`, `law`, `note`; optional
  `unit` (`days` or `business_days`) and `end_roll: forward` for a rule such as
  "the second day after posting if that is a business day, otherwise the next
  business day" (CPR 6.26).
- `recurring`: `id`, `title`, `kind`, `category`, `dates` (`MM-DD`, or `MM-L`
  for the last day of a month), optional `window_opens`, `counting`,
  `lead_time_days`, `applies_when`, `law`.
- `retention`: `id`, `title`, `title_<lang>`, `keep_years`, `from`,
  `permanent`, `law` or `suggested: true` with the reason in `note`.
- `life_events`: `id`, `title`, `title_<lang>`, `windows` (ids of response
  windows counted from the day of the event), `tasks` (steps with no statutory
  date: `title`, `title_<lang>`, `law`, `note`).
- `transit_buffer_days`: days to allow per channel (`instant`, `online-form`,
  `bank-transfer`, `post-domestic`, `post-international`).

## The verification standard

1. **Every rule names its law**: the act or regulation, the article or section,
   and an official source in the `Sources` section. Official means the
   legislation database and government portals of that country; a law firm's
   article or a news report can lead to the source but is never the citation.
2. **As in force on the review date.** Read the consolidated text and the list
   of amendments not yet applied. A change announced but not in force is
   described as such.
3. **No claim without a source.** A point that two sources contradict, or that
   only case law settles and the text does not, goes to `sources.uncertain`
   and is written in the Markdown without a claim.
4. **Amounts with their date.** Fees, penalties and thresholds carry the date
   they apply from.
5. **The household sees the tag.** Everything taken from a pack reaches the
   household as `country pack rule — verify`, with the law named; the letter
   in hand and the official source control.

## Checking a pack

```
python core/scripts/dates.py check-pack --country GB --year 2027
python core/scripts/dates.py check-pack --pack path/to/XX.json
```

The check reports errors (a missing law, a window with an unknown counting
rule, a life event naming a window that does not exist, a keeping period with
neither a law nor `suggested`, a holiday rule that cannot be computed, a missing
required section) and lists the holidays of the year for a person to compare
with the official calendar. `scripts/validate.py` runs the same check on every
bundled pack, and `tests/test_dates.py` compares the England and Wales rules
with the official list for 2019 to 2028.

To see which windows a pack holds for a matter, search them by words, then
count one:

```
python core/scripts/dates.py windows --country GB --query defence
python core/scripts/dates.py window --country GB --id county-court-defence-after-acknowledgment --from 2026-12-14
```

## A household's own pack

`pack-builder` writes `packs/<CC>.md` and `packs/<CC>.json` into the household
record. Skills use it only where no pack is bundled for that code: the scripts
get `--pack <record>/packs/<CC>.json` instead of `--country`, and everything
from it is tagged `household pack — verify`. A bundled pack always wins.

## Contributing a pack

1. Build it with `pack-builder`, or by hand from the two GB files.
2. Run `dates.py check-pack` until it reports no errors, and compare the
   holiday list with the official calendar for two years.
3. Add both files to `core/locale/`, run `python scripts/sync.py` and
   `python scripts/validate.py`.
4. Add at least three behaviour cases in `evals/` for the country (a deadline
   that crosses a holiday, a life event, a letter in the country's language).
5. In the pull request, list the sources you read and the points left in
   `uncertain`.

Each pack adds two files to every skill that carries packs (27 skills, so 54
files), and the plugin directory reviews plugins above 512 files by hand. With
the PL and GB packs the plugin has 382 files, which leaves room for two more
packs; beyond that, packs should move to a plugin of their own that the skills
read through a shared path.
