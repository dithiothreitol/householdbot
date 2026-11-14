#!/usr/bin/env bash
# Synthetic data for this case; see ../../fixtures/seed.sh
. "$(dirname "${BASH_SOURCE[0]}")/../../fixtures/seed.sh" full
# A synthetic household pack with three planted defects: a response window naming a
# counting rule the pack does not define, a recurring entry with no law, and no Sources
# section in the Markdown.
mkdir -p packs
cat > packs/DE.json <<'EOF'
{
  "pack": "DE",
  "scope": "Germany: the public holidays observed in every state. The states add holidays of their own, which this pack does not list.",
  "schema_version": 1,
  "reviewed": "2026-10-02",
  "official_language": "de",
  "currency": "EUR",
  "time_zone": "Europe/Berlin",
  "weekend": ["saturday", "sunday"],
  "holidays": {
    "law": "Einigungsvertrag Art. 2 Abs. 2 (3 October); the other holidays by state law",
    "source": "",
    "fixed": [
      {"date": "01-01", "name": "Neujahr", "name_en": "New Year's Day"},
      {"date": "05-01", "name": "Tag der Arbeit", "name_en": "Labour Day"},
      {"date": "10-03", "name": "Tag der Deutschen Einheit", "name_en": "German Unity Day"},
      {"date": "12-25", "name": "1. Weihnachtstag", "name_en": "Christmas Day"},
      {"date": "12-26", "name": "2. Weihnachtstag", "name_en": "Second Day of Christmas"}
    ],
    "easter_relative": [
      {"offset": -2, "name": "Karfreitag", "name_en": "Good Friday"},
      {"offset": 1, "name": "Ostermontag", "name_en": "Easter Monday"},
      {"offset": 39, "name": "Christi Himmelfahrt", "name_en": "Ascension Day"},
      {"offset": 50, "name": "Pfingstmontag", "name_en": "Whit Monday"}
    ]
  },
  "counting_rules": {
    "calendar": {"title": "Plain calendar arithmetic, no statutory roll", "end_roll": "none", "law": null, "met_by": null}
  },
  "deemed_delivery": [],
  "response_windows": [
    {"id": "objection-administrative-act", "title": "Objection to an administrative act (Widerspruch)", "amount": 1, "unit": "months", "from": "notification of the act", "counting": "administrative", "law": "VwGO § 70 Abs. 1"}
  ],
  "recurring": [
    {"id": "broadcast-fee", "title": "Broadcast fee (Rundfunkbeitrag), paid for three months at a time", "kind": "payment", "category": "home", "dates": ["02-15", "05-15", "08-15", "11-15"], "counting": "calendar", "lead_time_days": 7, "applies_when": "every household", "law": ""}
  ],
  "sources": {
    "reviewed_with": "synthetic test pack for the HouseholdBot behaviour tests, not a real pack",
    "uncertain": ["the holidays of the household's own state"]
  }
}
EOF
cat > packs/DE.md <<'EOF'
# Country pack — Germany (DE)

**Reviewed:** 2026-10-02. **Language:** de. **Currency:** EUR. **Time zone:** Europe/Berlin.
**Scope:** the public holidays observed in every state; the states add their own.

Synthetic test pack for the HouseholdBot behaviour tests, not a real pack.
Everything taken from this file reaches the household tagged
`household pack — verify`.

---

## Public holidays

Fixed: 1 Jan, 1 May, 3 Oct, 25 Dec, 26 Dec. Movable: Good Friday, Easter
Monday, Ascension Day (39 days after Easter Sunday), Whit Monday (50 days
after Easter Sunday). The states add holidays of their own.

## How deadlines are counted

To be researched.

## Common response windows

| Document | Window | Law |
|---|---|---|
| Objection (*Widerspruch*) to an administrative act | 1 month from notification | VwGO § 70 Abs. 1 |

## Recurring household obligations

| Applies when | Obligation | When | Law or source |
|---|---|---|---|
| Every household | Broadcast fee (*Rundfunkbeitrag*) for three months at a time | 15 Feb, 15 May, 15 Aug, 15 Nov | |

## Scam patterns

To be researched.
EOF
