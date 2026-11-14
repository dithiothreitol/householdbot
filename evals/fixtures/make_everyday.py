#!/usr/bin/env python3
"""Add stage-3 test data to a synthetic household made by make_household.py.

Everything is invented: the Everyday life section of the profile (one food kept
off the plan, without saying why), a chores register with one saved week, the
shopping and staples lists, and five papers with their obligations: a washing
machine invoice with its guarantee, a home insurance policy, a child's referral,
a school letter and an adult's identity card close to expiry. Dates are counted
from today, so the cases do not age.

    python make_everyday.py <household folder> [--today YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_household  # noqa: E402
from make_household import add_months, back_to_weekday, pl  # noqa: E402


def household_lang(root: Path) -> str:
    text = (root / "household-profile.md").read_text(encoding="utf-8")
    return "en" if re.search(r"\*\*Language:\*\*\s*en\b", text) else "pl"


def monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def profile_section(lang: str, today: date) -> str:
    bday = today + timedelta(days=21)
    if lang == "en":
        return f"""## Everyday life

- **Eat at home:** dinner every day, breakfast and lunch at weekends
- **Cooking time on weekdays:** 30 minutes
- **Food budget per week:** PLN 600
- **Likes and dislikes:** Zosia likes pasta and pancakes and does not eat mushrooms; Piotr likes soups; Anna eats no meat on Mondays
- **Keep off the plan:** peanuts
- **Shops:** Lidl Brzozowo, then the bakery on Rynek
- **Chores:** everyone listed under Members takes part; Zosia with a share of 0.5
- **Family calendar:** Rodzina Nowak (connected Google calendar)

| Date to remember | Whose | Day and month |
|---|---|---|
| Birthday | Zosia | {bday.day:02d}.{bday.month:02d} |
| Name day | Anna | 26.07 |
| Birthday | Piotr | 12.03 |

---

"""
    return f"""## Codzienność

- **Jemy w domu:** obiad codziennie, śniadanie i obiad w weekend
- **Czas na gotowanie w dni robocze:** 30 minut
- **Budżet na jedzenie na tydzień:** 600 zł
- **Co lubimy, czego nie:** Zosia lubi makaron i naleśniki, nie je grzybów; Piotr lubi zupy; Anna w poniedziałki nie je mięsa
- **Poza jadłospisem:** orzeszki ziemne
- **Sklepy:** Lidl Brzozowo, potem piekarnia na Rynku
- **Obowiązki:** biorą udział wszyscy domownicy; Zosia z udziałem 0,5
- **Kalendarz rodzinny:** Rodzina Nowak (podłączony kalendarz Google)

| Data do zapamiętania | Czyja | Dzień i miesiąc |
|---|---|---|
| Urodziny | Zosia | {bday.day:02d}.{bday.month:02d} |
| Imieniny | Anna | 26.07 |
| Urodziny | Piotr | 12.03 |

---

"""


def chores_register(today: date) -> dict:
    last = monday(today) - timedelta(weeks=1)
    y, w, _ = last.isocalendar()
    return {
        "schema_version": 1,
        "people": [{"name": "Anna", "share": 1.0}, {"name": "Piotr", "share": 1.0},
                   {"name": "Zosia", "share": 0.5, "birth_year": 2016}],
        "chores": [
            {"id": "ch-001", "title": "Zmywanie i zmywarka", "per_week": 7, "every_weeks": 1, "effort": 1,
             "min_age": 8, "who": [], "fixed": None, "first_week": None, "active": True, "notes": ""},
            {"id": "ch-002", "title": "Odkurzanie", "per_week": 1, "every_weeks": 1, "effort": 3,
             "min_age": 10, "who": [], "fixed": None, "first_week": None, "active": True, "notes": ""},
            {"id": "ch-003", "title": "Wyniesienie śmieci", "per_week": 2, "every_weeks": 1, "effort": 1,
             "min_age": 8, "who": [], "fixed": None, "first_week": None, "active": True, "notes": ""},
            {"id": "ch-004", "title": "Łazienka", "per_week": 1, "every_weeks": 1, "effort": 3,
             "min_age": 14, "who": [], "fixed": None, "first_week": None, "active": True, "notes": ""},
            {"id": "ch-005", "title": "Pranie i rozwieszanie", "per_week": 2, "every_weeks": 1, "effort": 2,
             "min_age": 12, "who": [], "fixed": None, "first_week": None, "active": True, "notes": ""},
            {"id": "ch-006", "title": "Koszenie trawy", "per_week": 1, "every_weeks": 2, "effort": 3,
             "min_age": 16, "who": [], "fixed": "Piotr", "first_week": None, "active": False,
             "notes": "sezonowo, od kwietnia"},
        ],
        "plans": [{"week": f"{y}-W{w:02d}", "start": last.isoformat(), "approved_by": "Anna",
                   "saved": last.isoformat(), "assignments": [
                       {"chore": "ch-001", "title": "Zmywanie i zmywarka", "person": "Anna", "count": 5, "effort": 5},
                       {"chore": "ch-001", "title": "Zmywanie i zmywarka", "person": "Zosia", "count": 2, "effort": 2},
                       {"chore": "ch-002", "title": "Odkurzanie", "person": "Anna", "count": 1, "effort": 3},
                       {"chore": "ch-003", "title": "Wyniesienie śmieci", "person": "Piotr", "count": 2, "effort": 2},
                       {"chore": "ch-004", "title": "Łazienka", "person": "Anna", "count": 1, "effort": 3},
                       {"chore": "ch-005", "title": "Pranie i rozwieszanie", "person": "Piotr", "count": 2, "effort": 4}]}],
    }


LISTS = {
    "pl": {
        "shopping.md": "# Lista zakupów\n\n## Lidl Brzozowo\n\n- [ ] papier toaletowy\n- [ ] masło 2 szt. (Piotr)\n\n"
                       "## Piekarnia na Rynku\n\n- [ ] chleb razowy\n",
        "staples.md": "# Kupujemy prawie co tydzień\n\n- mleko 3 l\n- jajka 10 szt.\n- chleb\n- jabłka 1 kg\n"
                      "- kawa 500 g\n- makaron 1 kg\n",
    },
    "en": {
        "shopping.md": "# Shopping list\n\n## Lidl Brzozowo\n\n- [ ] toilet paper\n- [ ] butter 2 pcs (Piotr)\n\n"
                       "## Bakery on Rynek\n\n- [ ] wholemeal bread\n",
        "staples.md": "# Bought most weeks\n\n- milk 3 l\n- eggs 10 pcs\n- bread\n- apples 1 kg\n"
                      "- coffee 500 g\n- pasta 1 kg\n",
    },
}

ORIGINALS = {
    "washer": """# Example AGD Sp. z o.o. — Faktura (synthetic test document)

Data sprzedaży: {bought}. Pralka Example WM-7, 1 999,00 zł brutto, zapłacono kartą.
Karta gwarancyjna producenta: gwarancja 24 miesiące od daty zakupu, naprawa w serwisie Example Serwis.
""",
    "home": """# Example Assistance S.A. — Polisa ubezpieczenia domu (synthetic test document)

Przedmiot ubezpieczenia: dom jednorodzinny, Brzozowo. Okres ubezpieczenia: {start} – {end}.
Zakres: mury i stałe elementy, ruchomości domowe, OC w życiu prywatnym. Składka roczna 1 240,00 zł, zapłacona.
Umowa nie przedłuża się automatycznie; o wznowieniu informujemy na 30 dni przed końcem okresu.
""",
    "referral": """# e-skierowanie (synthetic test document)

Pacjent: Zosia Nowak (dane syntetyczne). Skierowanie do poradni alergologicznej dla dzieci.
Data wystawienia: {issued}. Kod skierowania: patrz wydruk, strona 1.
""",
    "school": """# Szkoła Podstawowa nr 1 w Brzozowie — informacja dla rodziców klasy 4b (synthetic test document)

Wycieczka do Muzeum Wsi: {trip}. Prosimy o pisemną zgodę i wpłatę 85 zł do {due}.
Zebranie z rodzicami: {meeting}, godz. 17:00, sala 12.
""",
    "oldbill": """# Example Energia S.A. — Faktura VAT za 01/{year} (synthetic test document)

Do zapłaty 241,80 zł, zapłacono {paid}.
""",
    "idcard": """# Dowód osobisty (synthetic test document)

Posiadacz: Anna Nowak (dane syntetyczne). Numer dokumentu: patrz strona 1. Data ważności: {expiry}.
""",
}


def add(root: Path, today: date) -> dict:
    lang = household_lang(root)
    y = today.year
    prof = root / "household-profile.md"
    text = prof.read_text(encoding="utf-8")
    head = "## Rhythm" if lang == "en" else "## Rytm"
    if "## Everyday life" not in text and "## Codzienność" not in text:
        text = text.replace(head, profile_section(lang, today) + head, 1)
        text = text.replace("| Calendar | ✗ |", "| Calendar | ✓ (Anna, Piotr, Rodzina Nowak) |")
        text = text.replace("| Kalendarz | ✗ |", "| Kalendarz | ✓ (Anna, Piotr, Rodzina Nowak) |")
        prof.write_text(text, encoding="utf-8")

    reg = root / "registers"
    (reg / "chores.json").write_text(json.dumps(chores_register(today), ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")
    lists = root / "lists"
    lists.mkdir(exist_ok=True)
    for name, body in LISTS[lang].items():
        (lists / name).write_text(body, encoding="utf-8")

    bought = today - timedelta(days=400)
    guarantee_end = add_months(bought, 24)
    home_start = today - timedelta(days=60)
    home_end = add_months(home_start, 12) - timedelta(days=1)
    issued = today - timedelta(days=9)
    trip, due, meeting = today + timedelta(days=14), today + timedelta(days=7), today + timedelta(days=12)
    id_expiry = today + timedelta(days=45)
    old_bill = date(today.year - 8, 1, 20)

    docs = json.loads((reg / "documents.json").read_text(encoding="utf-8"))
    obs = json.loads((reg / "obligations.json").read_text(encoding="utf-8"))
    dn = max(int(d["id"].split("-")[-1]) for d in docs["documents"]) + 1
    on = max(int(o["id"].split("-")[-1]) for o in obs["obligations"]) + 1
    stamp = today.isoformat()

    def doc(n, **kw):
        base = {"id": f"doc-{y}-{n:04d}", "issuer": None, "concerns": [], "document_date": None,
                "received_date": None, "file": None, "sha256": None, "language": "pl", "key_facts": [],
                "obligations": [], "supersedes": None, "keep_until": None, "status": "filed", "notes": "",
                "created": stamp, "updated": stamp}
        base.update(kw)
        return base

    def ob(n, **kw):
        base = {"id": f"ob-{y}-{n:04d}", "series": None, "owner": None, "subject": None, "counterparty": None,
                "due_date": None, "do_by": None, "do_by_note": "", "lead_time_days": None, "recurrence": "none",
                "recurrence_day": None, "amount": None, "currency": None, "auto_renews": None, "notice": None,
                "transit_buffer_days": None, "source": None, "law": None, "status": "open", "done_date": None,
                "notes": "", "created": stamp, "updated": stamp}
        base.update(kw)
        return base

    files = {
        f"documents/{bought.year}/{bought.isoformat()}_example-agd_invoice.md": ORIGINALS["washer"].format(bought=pl(bought)),
        f"documents/{home_start.year}/{home_start.isoformat()}_example-assistance_insurance-policy.md":
            ORIGINALS["home"].format(start=pl(home_start), end=pl(home_end)),
        f"documents/{issued.year}/{issued.isoformat()}_referral.md": ORIGINALS["referral"].format(issued=pl(issued)),
        f"documents/{y}/{(today - timedelta(days=2)).isoformat()}_sp1-brzozowo_school-letter.md":
            ORIGINALS["school"].format(trip=pl(trip), due=pl(due), meeting=pl(meeting)),
        f"documents/{y}/{(today - timedelta(days=30)).isoformat()}_identity-card.md":
            ORIGINALS["idcard"].format(expiry=pl(id_expiry)),
        f"documents/{old_bill.year}/{old_bill.isoformat()}_example-energia_bill.md":
            ORIGINALS["oldbill"].format(year=old_bill.year, paid=pl(old_bill + timedelta(days=10))),
    }
    paths = list(files)
    new_docs = [
        doc(dn, title="Example AGD: washing machine invoice and guarantee", type="warranty-receipt", category="home",
            issuer="Example AGD Sp. z o.o.", concerns=["House, Brzozowo"], document_date=bought.isoformat(),
            file=paths[0], obligations=[f"ob-{y}-{on:04d}"], keep_until=add_months(guarantee_end, 1).isoformat(),
            key_facts=[{"fact": "price", "value": "1999.00 PLN", "page": 1, "quote": "1 999,00 zł brutto"},
                       {"fact": "guarantee", "value": "24 months from purchase", "page": 1,
                        "quote": "gwarancja 24 miesiące od daty zakupu"}]),
        doc(dn + 1, title="Example Assistance: home insurance policy", type="insurance-policy", category="insurance",
            issuer="Example Assistance S.A.", concerns=["House, Brzozowo"], document_date=home_start.isoformat(),
            file=paths[1], obligations=[f"ob-{y}-{on + 1:04d}"],
            key_facts=[{"fact": "insurance period", "value": f"{home_start.isoformat()} to {home_end.isoformat()}",
                        "page": 1, "quote": f"Okres ubezpieczenia: {pl(home_start)} – {pl(home_end)}"},
                       {"fact": "premium", "value": "1240.00 PLN", "page": 1, "quote": "Składka roczna 1 240,00 zł"},
                       {"fact": "renewal", "value": "does not renew automatically", "page": 1,
                        "quote": "Umowa nie przedłuża się automatycznie"}]),
        doc(dn + 2, title="Referral, Zosia", type="medical", category="health", issuer="Przychodnia (test)",
            concerns=["Zosia"], document_date=issued.isoformat(), file=paths[2], obligations=[f"ob-{y}-{on + 2:04d}"],
            key_facts=[{"fact": "kind", "value": "specialist referral", "page": 1},
                       {"fact": "referral code", "value": "see page 1"}]),
        doc(dn + 3, title="SP 1 Brzozowo: trip, consent and payment; parents' meeting", type="school-notice",
            category="children", issuer="Szkoła Podstawowa nr 1 w Brzozowie", concerns=["Zosia"],
            document_date=(today - timedelta(days=2)).isoformat(), file=paths[3], status="action-needed",
            obligations=[f"ob-{y}-{on + 3:04d}"],
            key_facts=[{"fact": "trip", "value": trip.isoformat(), "page": 1},
                       {"fact": "consent and payment due", "value": due.isoformat(), "page": 1,
                        "quote": f"zgodę i wpłatę 85 zł do {pl(due)}"},
                       {"fact": "parents' meeting", "value": f"{meeting.isoformat()} 17:00", "page": 1}]),
        doc(dn + 4, title="Identity card, Anna", type="identity-document", category="identity", issuer="Wójt (test)",
            concerns=["Anna"], file=paths[4], obligations=[f"ob-{y}-{on + 4:04d}"], keep_until="permanent",
            key_facts=[{"fact": "expiry date", "value": id_expiry.isoformat(), "page": 1,
                        "quote": f"Data ważności: {pl(id_expiry)}"},
                       {"fact": "document number", "value": "see page 1"}]),
        doc(dn + 5, title=f"Example Energia: electricity bill, 01/{old_bill.year}", type="bill",
            category="utilities", issuer="Example Energia S.A.", concerns=["House, Brzozowo"],
            document_date=old_bill.isoformat(), file=paths[5], keep_until=date(old_bill.year + 6, 12, 31).isoformat(),
            key_facts=[{"fact": "amount", "value": "241.80 PLN", "page": 1, "quote": "Do zapłaty 241,80 zł"}]),
    ]
    new_obs = [
        ob(on, title="Washing machine guarantee ends (Example AGD)", kind="expiry", category="home",
           owner="Piotr", subject="Washing machine", counterparty="Example AGD Sp. z o.o.",
           due_date=guarantee_end.isoformat(), do_by=back_to_weekday(guarantee_end - timedelta(days=30)).isoformat(),
           lead_time_days=30, provenance="calculated from document",
           source={"document": f"doc-{y}-{dn:04d}", "page": 1, "quote": "gwarancja 24 miesiące od daty zakupu"}),
        ob(on + 1, title="Home insurance, Example Assistance: ends, renew or switch", kind="renewal",
           category="insurance", owner="Anna", counterparty="Example Assistance S.A.", due_date=home_end.isoformat(),
           do_by=back_to_weekday(home_end - timedelta(days=30)).isoformat(), lead_time_days=45,
           amount="1240.00", currency="PLN", auto_renews=False, provenance="stated in document",
           source={"document": f"doc-{y}-{dn + 1:04d}", "page": 1}),
        ob(on + 2, title="Appointment, Zosia", kind="appointment", category="health", owner="Anna", subject="Zosia",
           due_date=(today + timedelta(days=20)).isoformat(), do_by=(today + timedelta(days=20)).isoformat(),
           provenance="told by household member", notes="10:30"),
        ob(on + 3, title="School trip: written consent and PLN 85.00", kind="payment",
           category="children", owner="Anna", subject="Zosia", counterparty="Szkoła Podstawowa nr 1 w Brzozowie",
           due_date=due.isoformat(), do_by=back_to_weekday(due - timedelta(days=1)).isoformat(),
           amount="85.00", currency="PLN", transit_buffer_days=1, provenance="stated in document",
           source={"document": f"doc-{y}-{dn + 3:04d}", "page": 1, "quote": f"zgodę i wpłatę 85 zł do {pl(due)}"}),
        ob(on + 4, title="Identity card, Anna: expires", kind="expiry", category="identity", owner="Anna",
           subject="Anna", due_date=id_expiry.isoformat(), do_by=back_to_weekday(id_expiry).isoformat(),
           lead_time_days=60, provenance="stated in document",
           source={"document": f"doc-{y}-{dn + 4:04d}", "page": 1, "quote": f"Data ważności: {pl(id_expiry)}"}),
    ]
    if lang == "pl":
        make_household.polish(new_docs)
        make_household.polish(new_obs)
    docs["documents"].extend(new_docs)
    obs["obligations"].extend(new_obs)
    for name, data in (("documents", docs), ("obligations", obs)):
        (reg / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return {"documents": [d["id"] for d in new_docs], "obligations": [o["id"] for o in new_obs], "lang": lang}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--today")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    root = Path(a.target)
    if not (root / "household-profile.md").exists():
        print(json.dumps({"ok": False, "error": "run make_household.py first"}))
        return 1
    print(json.dumps({"ok": True, **add(root, today)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
