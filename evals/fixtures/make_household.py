#!/usr/bin/env python3
"""Write a synthetic household record for tests and evals.

Every person, company, address and amount here is invented. Dates are placed
relative to --today (default: the system date) so that urgency bands stay the
same whenever the suite runs:

  ob-*-0001  electricity bill            do_by today+5     band now
  ob-*-0002  car insurance cancel-by     do_by today+65    band coming
  ob-*-0003  property tax instalment     next statutory date after today
  ob-*-0004  internet contract cancel-by do_by today+10    band soon
  ob-*-0005  passport expiry (child)     do_by today+150   start now (lead 180)
  ob-*-0006  water bill                  do_by today-4     overdue
  ob-*-0007  chimney and gas check       do_by today+25    band soon
  ob-*-0008  roadworthiness test         no date           absent, not zero
  ob-*-0009  last month's electricity    done

Usage: python3 make_household.py <target folder> [--today YYYY-MM-DD] [--empty]
       [--conflict] [--broken] [--lang pl|en]

--lang pl (default) writes a Polish household with a Polish profile; --lang en
writes the same household speaking English, as an English-speaking family in
Poland would set it up.
"""
from __future__ import annotations

import argparse
import calendar
import json
import sys
from datetime import date, timedelta
from pathlib import Path


def add_months(d: date, n: int) -> date:
    total = d.month - 1 + n
    y, m = d.year + total // 12, total % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def back_to_weekday(d: date) -> date:
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def pl(d: date) -> str:
    return d.strftime("%d.%m.%Y")


# A Polish household keeps titles and notes in Polish (D14); company names and quotes stay as they are.
POLISH = [
    ("Example Energia: electricity bill, ", "Example Energia: rachunek za prąd, "),
    ("Example Insurance: OC policy, Skoda Octavia", "Example Insurance: polisa OC, Skoda Octavia"),
    ("Urząd Gminy Brzozowo: property tax decision ", "Urząd Gminy Brzozowo: decyzja w sprawie podatku od nieruchomości "),
    ("Example Net: internet contract, 24 months", "Example Net: umowa na internet, 24 miesiące"),
    ("Passport, Zosia: expires", "Paszport Zosi: koniec ważności"),
    ("Passport, Zosia", "Paszport, Zosia"),
    ("Electricity bill: pay Example Energia", "Rachunek za prąd: zapłata dla Example Energia"),
    ("Car insurance (OC), Skoda Octavia: last day to give notice",
     "Ubezpieczenie OC, Skoda Octavia: ostatni dzień na wypowiedzenie"),
    ("Property tax instalment", "Rata podatku od nieruchomości"),
    ("Internet contract, Example Net: last day to cancel before it continues at PLN 119.00",
     "Umowa na internet, Example Net: ostatni dzień na wypowiedzenie przed przejściem na 119,00 zł"),
    ("Water and sewage bill: pay Example Wodociągi", "Rachunek za wodę i ścieki: zapłata dla Example Wodociągi"),
    ("Chimney and gas installation check, House", "Przegląd kominiarski i instalacji gazowej, dom"),
    ("Roadworthiness test, Skoda Octavia", "Badanie techniczne, Skoda Octavia"),
    ("Example AGD: washing machine invoice and guarantee", "Example AGD: faktura i gwarancja na pralkę"),
    ("Example Assistance: home insurance policy", "Example Assistance: polisa ubezpieczenia domu"),
    ("Referral, Zosia", "Skierowanie, Zosia"),
    ("SP 1 Brzozowo: trip, consent and payment; parents' meeting",
     "SP 1 Brzozowo: wycieczka, zgoda i wpłata; zebranie rodziców"),
    ("Identity card, Anna: expires", "Dowód osobisty Anny: koniec ważności"),
    ("Identity card, Anna", "Dowód osobisty, Anna"),
    ("Washing machine guarantee ends (Example AGD)", "Koniec gwarancji na pralkę (Example AGD)"),
    ("Home insurance, Example Assistance: ends, renew or switch",
     "Ubezpieczenie domu, Example Assistance: koniec, odnowić albo zmienić"),
    ("Appointment, Zosia", "Wizyta, Zosia"),
    ("School trip: written consent and PLN 85.00", "Wycieczka szkolna: pisemna zgoda i 85,00 zł"),
    ("House, Brzozowo", "Dom, Brzozowo"),
    ("Washing machine", "Pralka"),
    ("original kept at home; a scan is not filed", "oryginał w domu; skan nie jest zapisany"),
    ("paper bill not filed yet", "papierowy rachunek jeszcze nie zapisany"),
    ("date not known yet: check the registration certificate",
     "data jeszcze nieznana: sprawdzić w dowodzie rejestracyjnym"),
    ("1 day allowed for a bank transfer", "1 dzień na przelew"),
    ("5 days allowed for a letter by post", "5 dni na doręczenie listu"),
]


def polish(items: list[dict]) -> list[dict]:
    """Titles, notes, subjects and the places an entry concerns, in Polish."""
    def tr(text):
        if not isinstance(text, str):
            return text
        for en, pl_text in POLISH:
            text = text.replace(en, pl_text)
        return text
    for item in items:
        for key in ("title", "notes", "do_by_note", "subject"):
            item[key] = tr(item.get(key))
        if isinstance(item.get("concerns"), list):
            item["concerns"] = [tr(c) for c in item["concerns"]]
    return items


def next_property_tax(today: date) -> date:
    for year in (today.year, today.year + 1):
        for m, dd in ((3, 15), (5, 15), (9, 15), (11, 15)):
            d = date(year, m, dd)
            if d > today:
                return d
    raise AssertionError


PROFILE_EN = """# Household profile

*Synthetic test household. Every name, place and amount is invented.*

---

## Household

- **Label:** The Nowaks, Brzozowo (test)
- **Country:** PL
- **Language:** en
- **Currency:** PLN
- **Time zone:** Europe/Warsaw
- **Set up on:** {setup}
- **Profile schema:** 1

**What takes the most time or worry:** bills arrive by post and email, and renewals slip.

---

## Members

| Name | Role | Handles | Notes |
|---|---|---|---|
| Anna | adult | taxes, insurance, school | |
| Piotr | adult | car, internet, home repairs | |
| Zosia | child | | birth year 2016 |

---

## Homes

| Label | Owned or rented | Town | Heating | Notes |
|---|---|---|---|---|
| House, Brzozowo | owned | Brzozowo | gas boiler | |

## Vehicles

| Label | Owner | Insurance term ends | Roadworthiness test due |
|---|---|---|---|
| Skoda Octavia | Piotr | {oc_end} | unknown |

---

## Providers

| Category | Provider | Paid how | Notes |
|---|---|---|---|
| Electricity | Example Energia S.A. | bank transfer | |
| Water / waste | Example Wodociągi Sp. z o.o. | bank transfer | |
| Internet / TV | Example Net Sp. z o.o. | direct debit | |
| Car insurance | Example Insurance S.A. | bank transfer | |

---

## Decision rules

- **Two-adult threshold:** PLN 2000
- **Never without asking:** paying, sending, signing, cancelling, submitting
- **Who sees the weekly brief:** adults only
- **Documents kept for:** [DEFAULT — 6 years unless the document type says longer; identity, property, court and tax-decision papers permanently]

---

## Connected tools

| Category | Status | Without it |
|---|---|---|
| Mail | ✗ | Documents arrive as uploads, photos or pasted text |
| Calendar | ✗ | Deadlines are reported in the brief; no calendar entries are proposed |
| Document storage | ✗ | The household folder is a local or synced folder |

---

## Rhythm

- **Weekly brief:** [DEFAULT — on request; say "weekly brief"]
- **Scheduled:** [DEFAULT — no; nothing runs unless a household member asks]

---

## Country pack

- **Loaded:** PL
- **Statutory reminders accepted:** {accepted}
"""


PROFILE_PL = """# Profil gospodarstwa

*Syntetyczne gospodarstwo testowe. Wszystkie imiona, miejsca i kwoty są zmyślone.*

---

## Gospodarstwo

- **Nazwa:** Nowakowie, Brzozowo (test)
- **Kraj:** PL
- **Język:** pl
- **Waluta:** PLN
- **Strefa czasowa:** Europe/Warsaw
- **Data konfiguracji:** {setup}
- **Wersja profilu:** 1

**Co zabiera najwięcej czasu lub nerwów:** rachunki przychodzą pocztą i mailem, a odnowienia umów umykają.

---

## Domownicy

| Imię | Rola | Zajmuje się | Uwagi |
|---|---|---|---|
| Anna | dorosły | podatki, ubezpieczenia, szkoła | |
| Piotr | dorosły | samochód, internet, naprawy w domu | |
| Zosia | dziecko | | rok urodzenia 2016 |

---

## Domy

| Nazwa | Własność czy najem | Miejscowość | Ogrzewanie | Uwagi |
|---|---|---|---|---|
| Dom, Brzozowo | własność | Brzozowo | kocioł gazowy | |

## Pojazdy

| Pojazd | Właściciel | Koniec okresu ubezpieczenia | Termin badania technicznego |
|---|---|---|---|
| Skoda Octavia | Piotr | {oc_end} | nieznany |

---

## Dostawcy

| Kategoria | Dostawca | Sposób płatności | Uwagi |
|---|---|---|---|
| Prąd | Example Energia S.A. | przelew | |
| Woda / odpady | Example Wodociągi Sp. z o.o. | przelew | |
| Internet / telewizja | Example Net Sp. z o.o. | polecenie zapłaty | |
| Ubezpieczenie samochodu | Example Insurance S.A. | przelew | |

---

## Zasady decyzji

- **Próg zgody dwojga dorosłych:** 2000 zł
- **Nigdy bez pytania:** płacenie, wysyłanie, podpisywanie, wypowiadanie, składanie pism
- **Kto widzi przegląd tygodnia:** tylko dorośli
- **Jak długo trzymamy dokumenty:** [DEFAULT — 6 lat, chyba że rodzaj dokumentu wymaga dłużej; dokumenty tożsamości, nieruchomości, sądowe i decyzje podatkowe bezterminowo]

---

## Podłączone narzędzia

| Kategoria | Stan | Czyje konto | Bez tego |
|---|---|---|---|
| Poczta | ✗ | | Dokumenty przychodzą jako pliki, zdjęcia lub wklejony tekst |
| Kalendarz | ✗ | | Terminy są w przeglądzie; bez propozycji wpisów w kalendarzu |
| Magazyn dokumentów | ✗ | | Folder gospodarstwa jest lokalny lub na dysku synchronizowanym |

---

## Rytm

- **Przegląd tygodnia:** [DEFAULT — na żądanie; wystarczy napisać „przegląd tygodnia”]
- **Harmonogram:** [DEFAULT — brak; nic nie uruchamia się bez prośby domownika]

---

## Pakiet krajowy

- **Wczytany:** PL
- **Przyjęte przypomnienia ustawowe:** {accepted}
"""


def build(today: date, lang: str = "pl") -> dict:
    y = today.year
    bill_date = today - timedelta(days=12)
    bill_due = back_to_weekday(today + timedelta(days=5))
    oc_start = today - timedelta(days=299)
    oc_end = add_months(oc_start, 12) - timedelta(days=1)
    tax_raw = next_property_tax(today)
    net_end = today + timedelta(days=40)
    net_cancel = net_end - timedelta(days=30)
    passport_exp = today + timedelta(days=150)
    water_due = today - timedelta(days=4)
    chimney_due = back_to_weekday(today + timedelta(days=25))
    last_bill_due = add_months(bill_due, -1)

    def doc(n, **kw):
        base = {"id": f"doc-{y}-{n:04d}", "issuer": None, "concerns": [], "document_date": None,
                "received_date": None, "file": None, "sha256": None, "language": "pl",
                "key_facts": [], "obligations": [], "supersedes": None, "keep_until": None,
                "status": "filed", "notes": "", "created": today.isoformat(),
                "updated": today.isoformat()}
        base.update(kw)
        return base

    def ob(n, **kw):
        base = {"id": f"ob-{y}-{n:04d}", "series": None, "owner": None, "subject": None,
                "counterparty": None, "due_date": None, "do_by": None, "do_by_note": "",
                "lead_time_days": None, "recurrence": "none", "recurrence_day": None,
                "amount": None, "currency": None, "auto_renews": None, "notice": None,
                "transit_buffer_days": None, "source": None, "law": None, "rule": None, "status": "open",
                "done_date": None, "notes": "",
                "created": today.isoformat(), "updated": today.isoformat()}
        base.update(kw)
        return base

    f_bill = f"documents/{bill_date.year}/{bill_date.isoformat()}_example-energia_bill.md"
    f_oc = f"documents/{oc_start.year}/{oc_start.isoformat()}_example-insurance_insurance-policy.md"
    f_net = f"documents/{y}/{(net_end - timedelta(days=730)).isoformat()}_example-net_contract.md"
    documents = [
        doc(1, title=f"Example Energia: electricity bill, {bill_date.strftime('%m/%Y')}",
            type="bill", category="utilities", issuer="Example Energia S.A.",
            concerns=["House, Brzozowo"], document_date=bill_date.isoformat(),
            received_date=(bill_date + timedelta(days=3)).isoformat(), file=f_bill,
            key_facts=[
                {"fact": "amount due", "value": "PLN 286.40", "page": 1, "quote": "Do zapłaty: 286,40 zł"},
                {"fact": "payment deadline", "value": bill_due.isoformat(), "page": 1,
                 "quote": f"Termin płatności: {pl(bill_due)}"},
                {"fact": "customer number", "value": "see page 1"},
                {"fact": "payment account", "value": "ending 7781", "page": 1,
                 "quote": "Rachunek do wpłat: ... 7781"}],
            obligations=[f"ob-{y}-0001"], keep_until=f"{y + 5}-12-31"),
        doc(2, title="Example Insurance: OC policy, Skoda Octavia", type="insurance-policy",
            category="vehicle", issuer="Example Insurance S.A.", concerns=["Piotr", "Skoda Octavia"],
            document_date=(oc_start - timedelta(days=3)).isoformat(), file=f_oc,
            key_facts=[
                {"fact": "insurance term", "value": f"{oc_start.isoformat()} to {oc_end.isoformat()}",
                 "page": 1, "quote": f"Okres ubezpieczenia: {pl(oc_start)} - {pl(oc_end)}"},
                {"fact": "annual premium", "value": "PLN 1240.00", "page": 1,
                 "quote": "Składka łączna: 1 240,00 zł"},
                {"fact": "policy number", "value": "see page 1"}],
            obligations=[f"ob-{y}-0002"], keep_until=f"{oc_end.year + 6}-12-31"),
        doc(3, title=f"Urząd Gminy Brzozowo: property tax decision {y}", type="tax-document",
            category="home", issuer="Urząd Gminy Brzozowo", concerns=["House, Brzozowo"],
            document_date=f"{y}-02-10", received_date=f"{y}-02-17",
            key_facts=[
                {"fact": "yearly tax", "value": "PLN 1124.00", "page": 1,
                 "quote": "Podatek od nieruchomości: 1 124,00 zł"},
                {"fact": "instalment", "value": "PLN 281.00 by 15 Mar, 15 May, 15 Sep, 15 Nov",
                 "page": 2, "quote": "raty: 15 marca, 15 maja, 15 września, 15 listopada"}],
            obligations=[f"ob-{y}-0003"], keep_until="permanent"),
        doc(4, title="Example Net: internet contract, 24 months", type="contract",
            category="utilities", issuer="Example Net Sp. z o.o.", concerns=["House, Brzozowo"],
            document_date=(net_end - timedelta(days=730)).isoformat(), file=f_net,
            key_facts=[
                {"fact": "fixed term ends", "value": net_end.isoformat(), "page": 1,
                 "quote": f"Umowa zawarta na czas określony do dnia {pl(net_end)}"},
                {"fact": "monthly fee", "value": "PLN 79.00", "page": 1, "quote": "Abonament: 79,00 zł/mies."},
                {"fact": "after the term", "value": "continues for an indefinite period at PLN 119.00 unless cancelled 30 days before the end",
                 "page": 2, "quote": "przechodzi w umowę na czas nieokreślony, chyba że Abonent złoży oświadczenie najpóźniej na 30 dni przed upływem"}],
            obligations=[f"ob-{y}-0004"]),
        doc(5, title="Passport, Zosia", type="identity-document", category="identity",
            issuer="Wojewoda", concerns=["Zosia"],
            key_facts=[{"fact": "expiry date", "value": passport_exp.isoformat(), "page": 2,
                        "quote": f"Data ważności: {pl(passport_exp)}"},
                       {"fact": "passport number", "value": "see page 2"}],
            obligations=[f"ob-{y}-0005"], keep_until="permanent",
            notes="original kept at home; a scan is not filed"),
    ]
    obligations = [
        ob(1, series="electricity-bill", title="Electricity bill: pay Example Energia",
           kind="payment", category="utilities", owner="Anna", counterparty="Example Energia S.A.",
           due_date=bill_due.isoformat(), do_by=back_to_weekday(bill_due - timedelta(days=1)).isoformat(),
           do_by_note="1 day allowed for a bank transfer", transit_buffer_days=1, recurrence="monthly",
           amount="286.40",
           currency="PLN", source={"document": f"doc-{y}-0001", "page": 1,
                                   "quote": f"Termin płatności: {pl(bill_due)}"},
           provenance="stated in document"),
        ob(2, series="oc-skoda", title="Car insurance (OC), Skoda Octavia: last day to give notice",
           kind="renewal", category="vehicle", owner="Piotr", subject="Skoda Octavia",
           counterparty="Example Insurance S.A.", due_date=(oc_end - timedelta(days=1)).isoformat(),
           do_by=back_to_weekday(oc_end - timedelta(days=1)).isoformat(), lead_time_days=45,
           recurrence="yearly", amount="1240.00", currency="PLN", auto_renews=True,
           notice={"period": "written notice no later than one day before the term ends",
                   "method": "written notice", "transit_buffer_days": 0},
           source={"document": f"doc-{y}-0002", "page": 1,
                   "quote": f"Okres ubezpieczenia: {pl(oc_start)} - {pl(oc_end)}"},
           provenance="country pack rule — verify",
           law="ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 28"),
        # The decision states the raw date; the tax counting rule moves a last day off a weekend
        # (Ordynacja podatkowa art. 12 § 5), so the entry names the rule and record.py due
        # reports the moved last day. The plan date is worked back from the raw date.
        ob(3, series="property-tax", title="Property tax instalment", kind="payment",
           category="home", owner="Anna", counterparty="Urząd Gminy Brzozowo",
           due_date=tax_raw.isoformat(), do_by=back_to_weekday(tax_raw).isoformat(), rule="tax",
           recurrence="15 Mar, 15 May, 15 Sep, 15 Nov", amount="281.00", currency="PLN",
           source={"document": f"doc-{y}-0003", "page": 2,
                   "quote": "raty: 15 marca, 15 maja, 15 września, 15 listopada"},
           provenance="stated in document", law="ustawa o podatkach i opłatach lokalnych art. 6"),
        ob(4, title="Internet contract, Example Net: last day to cancel before it continues at PLN 119.00",
           kind="renewal", category="utilities", owner="Piotr", counterparty="Example Net Sp. z o.o.",
           due_date=net_cancel.isoformat(),
           do_by=back_to_weekday(net_cancel - timedelta(days=5)).isoformat(),
           do_by_note="5 days allowed for a letter by post", auto_renews=True,
           notice={"period": "30 days before the end of the term", "method": "written statement",
                   "transit_buffer_days": 5},
           source={"document": f"doc-{y}-0004", "page": 2,
                   "quote": "najpóźniej na 30 dni przed upływem"},
           provenance="calculated from document"),
        ob(5, title="Passport, Zosia: expires", kind="expiry", category="identity", owner="Anna",
           subject="Zosia", due_date=passport_exp.isoformat(),
           do_by=back_to_weekday(passport_exp).isoformat(), lead_time_days=180,
           source={"document": f"doc-{y}-0005", "page": 2,
                   "quote": f"Data ważności: {pl(passport_exp)}"},
           provenance="stated in document"),
        ob(6, series="water-bill", title="Water and sewage bill: pay Example Wodociągi",
           kind="payment", category="utilities", owner="Anna",
           counterparty="Example Wodociągi Sp. z o.o.", due_date=water_due.isoformat(),
           do_by=back_to_weekday(water_due).isoformat(), recurrence="every 2 months",
           amount="164.20", currency="PLN", provenance="told by household member",
           notes="paper bill not filed yet"),
        ob(7, series="chimney-check", title="Chimney and gas installation check, House",
           kind="task", category="home", owner="Piotr", subject="House, Brzozowo",
           due_date=chimney_due.isoformat(), do_by=chimney_due.isoformat(), lead_time_days=21,
           recurrence="yearly", provenance="told by household member",
           law="Prawo budowlane art. 62"),
        ob(8, title="Roadworthiness test, Skoda Octavia", kind="expiry", category="vehicle",
           owner="Piotr", subject="Skoda Octavia", provenance="told by household member",
           notes="date not known yet: check the registration certificate"),
        ob(9, series="electricity-bill", title="Electricity bill: pay Example Energia",
           kind="payment", category="utilities", owner="Anna", counterparty="Example Energia S.A.",
           due_date=last_bill_due.isoformat(), do_by=back_to_weekday(last_bill_due - timedelta(days=1)).isoformat(),
           recurrence="monthly", amount="301.15", currency="PLN", status="done",
           done_date=(last_bill_due - timedelta(days=2)).isoformat(), provenance="stated in document"),
    ]
    if lang == "en":
        profile_tpl, accepted, unknown, none_yet = PROFILE_EN, "property tax instalments", "unknown", "none yet"
    else:
        profile_tpl, accepted, unknown, none_yet = PROFILE_PL, "raty podatku od nieruchomości", "nieznany", "na razie brak"
        polish(documents)
        polish(obligations)
    originals = {
        f_bill: BILL.format(date=pl(bill_date), due=pl(bill_due), month=bill_date.strftime("%m/%Y")),
        f_oc: OC.format(start=pl(oc_start), end=pl(oc_end)),
        f_net: NET.format(end=pl(net_end)),
    }
    return {"documents": documents, "obligations": obligations, "originals": originals,
            "profile": profile_tpl.format(setup=today.isoformat(), oc_end=oc_end.isoformat(),
                                          accepted=accepted),
            "profile_empty": profile_tpl.format(setup=today.isoformat(), oc_end=unknown, accepted=none_yet)}


BILL = """# Example Energia S.A. — Faktura VAT (synthetic test document)

Strona 1

Data wystawienia: {date}
Okres rozliczeniowy: {month}
Nabywca: Anna Nowak, ul. Testowa 1, 00-000 Brzozowo
Numer klienta: 0000-TEST-0000

Energia elektryczna czynna: 214 kWh
Opłata dystrybucyjna i sprzedaż energii

Do zapłaty: 286,40 zł
Termin płatności: {due}
Rachunek do wpłat: PL 00 0000 0000 0000 0000 0000 7781 (numer testowy)
"""

OC = """# Example Insurance S.A. — Polisa OC posiadacza pojazdu (synthetic test document)

Strona 1

Ubezpieczający: Piotr Nowak
Pojazd: Skoda Octavia, nr rej. TEST 0000
Okres ubezpieczenia: {start} - {end}
Składka łączna: 1 240,00 zł, płatna jednorazowo

Umowa ulega przedłużeniu na kolejne 12 miesięcy, jeżeli nie zostanie wypowiedziana
zgodnie z art. 28 ustawy o ubezpieczeniach obowiązkowych.
"""

NET = """# Example Net Sp. z o.o. — Umowa o świadczenie usług (synthetic test document)

Strona 1

Abonent: Piotr Nowak
Umowa zawarta na czas określony do dnia {end}
Abonament: 79,00 zł/mies.

Strona 2

Po upływie okresu określonego umowa przechodzi w umowę na czas nieokreślony, chyba że Abonent
złoży oświadczenie najpóźniej na 30 dni przed upływem tego okresu. Opłata po tym okresie: 119,00 zł/mies.
"""


def write(target: Path, today: date, empty: bool = False, lang: str = "pl") -> None:
    target.mkdir(parents=True, exist_ok=True)
    data = build(today, lang)
    for sub in ("registers", "documents", "briefs", "inbox", "log"):
        (target / sub).mkdir(parents=True, exist_ok=True)
    docs = [] if empty else data["documents"]
    obs = [] if empty else data["obligations"]
    for name, items in (("documents", docs), ("obligations", obs)):
        with (target / "registers" / f"{name}.json").open("w", encoding="utf-8", newline="\n") as fh:
            json.dump({"schema_version": 1, name: items}, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    (target / "household-profile.md").write_text(data["profile_empty" if empty else "profile"], encoding="utf-8")
    header = ("# Dziennik decyzji\n\nTylko dopisywanie. Jedna linia na każdą zatwierdzoną zmianę w rekordzie.\n\n"
              if lang == "pl" else
              "# Decisions log\n\nAppend-only. One line per approved change to the record.\n\n")
    (target / "log" / "decisions.md").write_text(header, encoding="utf-8")
    if not empty:
        for rel, text in data["originals"].items():
            p = target / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")


def fake_pesel() -> str:
    """Eleven digits with a valid checksum, made at run time so none is committed."""
    body = "9" + "0" * 5 + "1234"
    w = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    return body + str((10 - sum(int(a) * b for a, b in zip(body, w)) % 10) % 10)


def add_conflict_copy(target: Path, today: date) -> None:
    """A Google Drive style conflict copy: one entry added, one amount changed on the other device."""
    main = json.loads((target / "registers" / "obligations.json").read_text(encoding="utf-8"))
    later = (today + timedelta(days=1)).isoformat()
    main["obligations"][0] = dict(main["obligations"][0], amount="291.70", updated=later)
    main["obligations"].append(dict(main["obligations"][6], id=f"ob-{today.year}-0010",
                                    series="gutters", title="Gutter cleaning, House",
                                    due_date=(today + timedelta(days=20)).isoformat(),
                                    do_by=back_to_weekday(today + timedelta(days=20)).isoformat(),
                                    recurrence="yearly", created=later, updated=later))
    with (target / "registers" / "obligations (1).json").open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(main, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def break_registers(target: Path) -> None:
    """A malformed date and an identifier copied into a register, as a careless hand edit leaves them."""
    p = target / "registers" / "obligations.json"
    obs = json.loads(p.read_text(encoding="utf-8"))
    obs["obligations"][0]["due_date"] = "15.11.2026"
    p.write_text(json.dumps(obs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    p = target / "registers" / "documents.json"
    docs = json.loads(p.read_text(encoding="utf-8"))
    docs["documents"][1]["notes"] = f"PESEL ubezpieczającego {fake_pesel()}"
    p.write_text(json.dumps(docs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--today")
    ap.add_argument("--empty", action="store_true", help="profile and empty registers only")
    ap.add_argument("--conflict", action="store_true", help="also write a sync-conflict copy")
    ap.add_argument("--broken", action="store_true", help="also break the registers the way a hand edit can")
    ap.add_argument("--lang", choices=["pl", "en"], default="pl",
                    help="pl: Polish household (Polish profile); en: English-speaking household in Poland")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    write(Path(a.target), today, a.empty, a.lang)
    if a.conflict:
        add_conflict_copy(Path(a.target), today)
    if a.broken:
        break_registers(Path(a.target))
    print(json.dumps({"ok": True, "target": str(Path(a.target).resolve()), "today": today.isoformat()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
