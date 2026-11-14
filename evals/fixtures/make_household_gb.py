#!/usr/bin/env python3
"""Write a synthetic household in England for tests and evals (the GB pack).

Every person, company, address, number and amount here is invented. Dates are
placed relative to --today (default: the system date):

  ob-*-0001  energy bill                 due today+6       band now
  ob-*-0002  car insurance renewal       due today+40      band coming
  ob-*-0003  MOT, Ford Focus             expires today+20  band soon
  ob-*-0004  council tax instalment      the 1st of next month
  ob-*-0005  parking PCN, discount ends  as printed on the notice: today+4
  ob-*-0006  passport expiry (child)     today+150         start now (lead 180)
  ob-*-0007  water bill                  due today-4       overdue
  ob-*-0008  boiler service              today+25          no law (owner-occupier)
  ob-*-0009  last month's energy bill    done

Usage: python3 make_household_gb.py <target folder> [--today YYYY-MM-DD]
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


def uk(d: date) -> str:
    return f"{d.day} {d.strftime('%B %Y')}"


PROFILE = """# Household profile

*Synthetic test household. Every name, place and amount is invented.*

---

## Household

- **Label:** The Carters, Testbury (test)
- **Country:** GB
- **Language:** en
- **Currency:** GBP
- **Time zone:** Europe/London
- **Set up on:** {setup}
- **Profile schema:** 1

**What takes the most time or worry:** letters from the council and renewals that roll over.

---

## Members

| Name | Role | Handles | Notes |
|---|---|---|---|
| Emma | adult | council tax, insurance, school | |
| James | adult | car, broadband, home repairs | |
| Lily | child | | birth year 2017 |

---

## Homes

| Label | Owned or rented | Town | Heating | Notes |
|---|---|---|---|---|
| House, Testbury | owned | Testbury, England | gas boiler | |

## Vehicles

| Label | Owner | Insurance term ends | Roadworthiness test due |
|---|---|---|---|
| Ford Focus | James | {ins_end} | MOT {mot} |

---

## Providers

| Category | Provider | Paid how | Notes |
|---|---|---|---|
| Energy | Example Energy Ltd | bank transfer | |
| Water | Example Water plc | bank transfer | |
| Broadband | Example Broadband Ltd | direct debit | |
| Car insurance | Example Insurance plc | annual, card | |
| Council tax | Example Borough Council | direct debit, 10 instalments | |

---

## Decision rules

- **Two-adult threshold:** GBP 500
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

- **Loaded:** GB
- **Statutory reminders accepted:** MOT, council tax instalments
"""

PCN = """# Example Borough Council — Penalty Charge Notice (synthetic test document)

Page 1

PCN number: TEST0000000
Vehicle registration mark: TE57 XXX (test)
Date of contravention and of this notice: {issued}
Location: Testbury High Street (test)
Contravention: parked in a restricted street during prescribed hours

The penalty charge is GBP 70.00. It is reduced to GBP 35.00 if paid by {discount}.
If you think the penalty charge should not be paid, you may make informal representations.
Pay or challenge online at the council's website. This is a synthetic test notice.
"""

BILL = """# Example Energy Ltd — Energy bill (synthetic test document)

Page 1

Bill date: {date}
Account: TEST-0000 (test)
Billing period: {month}

Amount due: GBP 142.60
Pay by: {due}
Pay to: sort code 00-00-00, account ending 4410 (test)
"""


def build(today: date) -> dict:
    y = today.year
    bill_date = today - timedelta(days=10)
    bill_due = today + timedelta(days=6)
    ins_end = today + timedelta(days=40)
    mot_end = today + timedelta(days=20)
    first_next = add_months(date(today.year, today.month, 1), 1)
    pcn_issued = today - timedelta(days=9)
    pcn_discount = today + timedelta(days=4)
    passport_exp = today + timedelta(days=150)
    water_due = today - timedelta(days=4)
    boiler_due = back_to_weekday(today + timedelta(days=25))
    last_bill_due = add_months(bill_due, -1)

    def doc(n, **kw):
        base = {"id": f"doc-{y}-{n:04d}", "issuer": None, "concerns": [], "document_date": None,
                "received_date": None, "file": None, "sha256": None, "language": "en",
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
                "transit_buffer_days": None, "source": None, "law": None, "status": "open",
                "done_date": None, "notes": "", "created": today.isoformat(), "updated": today.isoformat()}
        base.update(kw)
        return base

    f_bill = f"documents/{bill_date.year}/{bill_date.isoformat()}_example-energy_bill.md"
    f_pcn = f"documents/{pcn_issued.year}/{pcn_issued.isoformat()}_example-borough-council_pcn.md"
    documents = [
        doc(1, title=f"Example Energy: energy bill, {bill_date.strftime('%m/%Y')}", type="bill",
            category="utilities", issuer="Example Energy Ltd", concerns=["House, Testbury"],
            document_date=bill_date.isoformat(), received_date=(bill_date + timedelta(days=2)).isoformat(),
            file=f_bill,
            key_facts=[
                {"fact": "amount due", "value": "GBP 142.60", "page": 1, "quote": "Amount due: GBP 142.60"},
                {"fact": "payment deadline", "value": bill_due.isoformat(), "page": 1,
                 "quote": f"Pay by: {uk(bill_due)}"},
                {"fact": "payment account", "value": "ending 4410", "page": 1,
                 "quote": "account ending 4410 (test)"}],
            obligations=[f"ob-{y}-0001"], keep_until=f"{y + 6}-12-31"),
        doc(2, title="Example Insurance: motor policy, Ford Focus", type="insurance-policy",
            category="vehicle", issuer="Example Insurance plc", concerns=["James", "Ford Focus"],
            document_date=(ins_end - timedelta(days=368)).isoformat(),
            key_facts=[
                {"fact": "period of cover", "value": f"to {ins_end.isoformat()}", "page": 1,
                 "quote": f"Period of cover ends: {uk(ins_end)}"},
                {"fact": "annual premium", "value": "GBP 612.00", "page": 1, "quote": "Total premium: GBP 612.00"},
                {"fact": "policy number", "value": "see page 1"}],
            obligations=[f"ob-{y}-0002"]),
        doc(3, title=f"Example Borough Council: council tax bill {y}/{(y + 1) % 100:02d}", type="tax-document",
            category="home", issuer="Example Borough Council", concerns=["House, Testbury"],
            document_date=f"{y}-03-10",
            key_facts=[
                {"fact": "yearly council tax", "value": "GBP 1980.00", "page": 1,
                 "quote": "Council tax for the year: GBP 1,980.00"},
                {"fact": "instalments", "value": "10 monthly instalments of GBP 198.00 on the 1st, April to January",
                 "page": 1, "quote": "10 instalments of GBP 198.00 on the 1st of each month from April"}],
            obligations=[f"ob-{y}-0004"]),
        doc(4, title="Example Borough Council: Penalty Charge Notice, Ford Focus", type="fine",
            category="vehicle", issuer="Example Borough Council", concerns=["James", "Ford Focus"],
            document_date=pcn_issued.isoformat(), received_date=pcn_issued.isoformat(), file=f_pcn,
            key_facts=[
                {"fact": "penalty charge", "value": "GBP 70.00", "page": 1, "quote": "The penalty charge is GBP 70.00."},
                {"fact": "discounted charge", "value": f"GBP 35.00 if paid by {pcn_discount.isoformat()}", "page": 1,
                 "quote": f"It is reduced to GBP 35.00 if paid by {uk(pcn_discount)}."},
                {"fact": "PCN number", "value": "see page 1"}],
            obligations=[f"ob-{y}-0005"]),
        doc(5, title="Passport, Lily", type="identity-document", category="identity",
            issuer="HM Passport Office", concerns=["Lily"],
            key_facts=[{"fact": "expiry date", "value": passport_exp.isoformat(), "page": 2,
                        "quote": f"Date of expiry: {uk(passport_exp)}"},
                       {"fact": "passport number", "value": "see page 2"}],
            obligations=[f"ob-{y}-0006"], keep_until="permanent", notes="original kept at home"),
    ]
    obligations = [
        ob(1, series="energy-bill", title="Energy bill: pay Example Energy", kind="payment",
           category="utilities", owner="Emma", counterparty="Example Energy Ltd",
           due_date=bill_due.isoformat(), do_by=back_to_weekday(bill_due - timedelta(days=1)).isoformat(),
           do_by_note="1 day allowed for a bank transfer", transit_buffer_days=1, recurrence="monthly",
           amount="142.60", currency="GBP",
           source={"document": f"doc-{y}-0001", "page": 1, "quote": f"Pay by: {uk(bill_due)}"},
           provenance="stated in document"),
        ob(2, series="motor-insurance", title="Car insurance, Ford Focus: renews; compare or stop the renewal",
           kind="renewal", category="vehicle", owner="James", subject="Ford Focus",
           counterparty="Example Insurance plc", due_date=ins_end.isoformat(),
           do_by=back_to_weekday(ins_end - timedelta(days=7)).isoformat(), lead_time_days=30,
           recurrence="yearly", amount="612.00", currency="GBP", auto_renews=True,
           source={"document": f"doc-{y}-0002", "page": 1, "quote": f"Period of cover ends: {uk(ins_end)}"},
           provenance="stated in document"),
        ob(3, series="mot-focus", title="MOT, Ford Focus: certificate expires", kind="expiry",
           category="vehicle", owner="James", subject="Ford Focus", due_date=mot_end.isoformat(),
           do_by=back_to_weekday(mot_end - timedelta(days=3)).isoformat(), lead_time_days=30,
           recurrence="yearly", provenance="told by household member",
           law="Road Traffic Act 1988 s.47"),
        ob(4, series="council-tax", title="Council tax instalment, Example Borough Council", kind="payment",
           category="home", owner="Emma", counterparty="Example Borough Council",
           due_date=first_next.isoformat(), do_by=first_next.isoformat(),
           do_by_note="paid by direct debit", recurrence="monthly", amount="198.00", currency="GBP",
           source={"document": f"doc-{y}-0003", "page": 1,
                   "quote": "10 instalments of GBP 198.00 on the 1st of each month from April"},
           provenance="stated in document"),
        ob(5, title="Parking PCN, Ford Focus: discounted payment ends", kind="payment", category="vehicle",
           owner="James", subject="Ford Focus", counterparty="Example Borough Council",
           due_date=pcn_discount.isoformat(), do_by=back_to_weekday(pcn_discount - timedelta(days=1)).isoformat(),
           amount="35.00", currency="GBP",
           source={"document": f"doc-{y}-0004", "page": 1,
                   "quote": f"It is reduced to GBP 35.00 if paid by {uk(pcn_discount)}."},
           provenance="stated in document", notes="pay the discounted charge or challenge it; not both"),
        ob(6, title="Passport, Lily: expires", kind="expiry", category="identity", owner="Emma",
           subject="Lily", due_date=passport_exp.isoformat(), do_by=back_to_weekday(passport_exp).isoformat(),
           lead_time_days=180,
           source={"document": f"doc-{y}-0005", "page": 2, "quote": f"Date of expiry: {uk(passport_exp)}"},
           provenance="stated in document"),
        ob(7, series="water-bill", title="Water bill: pay Example Water", kind="payment", category="utilities",
           owner="Emma", counterparty="Example Water plc", due_date=water_due.isoformat(),
           do_by=back_to_weekday(water_due).isoformat(), recurrence="every 6 months", amount="48.20",
           currency="GBP", provenance="told by household member", notes="paper bill not filed yet"),
        ob(8, series="boiler-service", title="Boiler service, House", kind="task", category="home",
           owner="James", subject="House, Testbury", due_date=boiler_due.isoformat(),
           do_by=boiler_due.isoformat(), lead_time_days=21, recurrence="yearly",
           provenance="told by household member",
           notes="no legal duty for an owner-occupier; the household keeps it yearly"),
        ob(9, series="energy-bill", title="Energy bill: pay Example Energy", kind="payment",
           category="utilities", owner="Emma", counterparty="Example Energy Ltd",
           due_date=last_bill_due.isoformat(), do_by=back_to_weekday(last_bill_due - timedelta(days=1)).isoformat(),
           recurrence="monthly", amount="151.30", currency="GBP", status="done",
           done_date=(last_bill_due - timedelta(days=2)).isoformat(), provenance="stated in document"),
    ]
    originals = {
        f_bill: BILL.format(date=uk(bill_date), due=uk(bill_due), month=bill_date.strftime("%B %Y")),
        f_pcn: PCN.format(issued=uk(pcn_issued), discount=uk(pcn_discount)),
    }
    profile = PROFILE.format(setup=today.isoformat(), ins_end=ins_end.isoformat(), mot=mot_end.isoformat())
    return {"documents": documents, "obligations": obligations, "originals": originals, "profile": profile}


def write(target: Path, today: date) -> None:
    data = build(today)
    for sub in ("registers", "documents", "briefs", "inbox", "log"):
        (target / sub).mkdir(parents=True, exist_ok=True)
    for name in ("documents", "obligations"):
        with (target / "registers" / f"{name}.json").open("w", encoding="utf-8", newline="\n") as fh:
            json.dump({"schema_version": 1, name: data[name]}, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    (target / "household-profile.md").write_bytes(data["profile"].encode("utf-8"))
    (target / "log" / "decisions.md").write_bytes(
        b"# Decisions log\n\nAppend-only. One line per approved change to the record.\n\n")
    for rel, text in data["originals"].items():
        p = target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--today")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    write(Path(a.target), today)
    print(json.dumps({"ok": True, "target": a.target, "today": today.isoformat()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
