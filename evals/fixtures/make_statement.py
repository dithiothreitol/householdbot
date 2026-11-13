#!/usr/bin/env python3
"""Write a synthetic bank statement export for tests and evals.

Every payee, amount and number is invented. The three full months before
--today are covered. Three layouts exercise the reader:

  a  Polish, semicolons, Windows-1250, preamble lines, newest first, one signed
     amount column, running balance, account numbers in a column of their own
  b  Polish, commas, UTF-8 with BOM, oldest first, DD.MM.YYYY, separate debit and
     credit columns, quoted decimal commas
  c  English, tabs, UTF-8, ISO dates, signed amounts with a decimal point, no balance

--expected writes the totals the reader must reproduce, computed from the source
list here, not by reading the file back. --gap leaves out the middle month.

Usage: python3 make_statement.py <out.csv> [--format a|b|c] [--today YYYY-MM-DD]
       [--gap] [--expected expected.json]
"""
from __future__ import annotations

import argparse
import calendar
import json
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

D = Decimal

# (day, payee, description_pl, description_en, amount, category); month-specific rows below
MONTHLY = [
    (1, "ACME Sp. z o.o.", "Wynagrodzenie za {mm}/{yyyy}", "Salary {mm}/{yyyy}", D("7450.00"), "income"),
    (2, "Example Bank S.A.", "Rata kredytu hipotecznego {mm}/{yyyy}", "Mortgage instalment {mm}/{yyyy}", D("-2200.00"), "housing"),
    (3, "ZUS", "Swiadczenie wychowawcze 800+", "ZUS child benefit 800+", D("800.00"), "income"),
    (5, "Biedronka 1234 Brzozowo", "Zakupy", "Groceries", D("-186.45"), "food"),
    (16, "Example Energia S.A.", "Faktura FE/{mm}/{yyyy}", "Invoice FE/{mm}/{yyyy}", None, "utilities"),
    (10, "NETFLIX.COM", "Netflix subskrypcja", "Netflix subscription", None, "subscriptions"),
    (12, "ORLEN Stacja nr 123", "Paliwo", "Fuel", D("-250.00"), "transport"),
    (15, "Spotify AB", "Spotify Premium", "Spotify Premium", D("-23.99"), "subscriptions"),
    (17, "Lidl Brzozowo", "Zakupy", "Groceries", D("-142.30"), "food"),
    (20, "Orange Polska S.A.", "Abonament telefon", "Phone plan", D("-79.00"), "utilities"),
    (22, "Apteka Pod Lipami", "Leki", "Medicines", D("-64.20"), "health"),
    (25, "Allegro.pl", "Zakup Allegro", "Allegro purchase", D("-129.99"), "shopping"),
    (27, "", "Przelew wlasny na oszczednosci", "Own transfer to savings", D("-500.00"), "transfers"),
    (28, "", "Wyplata z bankomatu", "ATM withdrawal", D("-200.00"), "cash"),
]
ELECTRICITY = [D("-278.90"), D("-294.35"), D("-301.15")]
NETFLIX = [D("-49.00"), D("-49.00"), D("-55.00")]


def three_months(today: date) -> list[tuple[int, int]]:
    y, m = today.year, today.month
    out = []
    for _ in range(3):
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
        out.insert(0, (y, m))
    return out


def fake_account(seed: int) -> str:
    """26 digits whose IBAN checksum is deliberately wrong, so no real account is written."""
    base = f"{(seed * 7919) % 10**8:08d}" + "1020" + "0000" + f"{seed:010d}"
    digits = base[:26]
    rearranged = int(digits[2:] + "2521" + digits[:2])
    if rearranged % 97 == 1:
        digits = digits[:-1] + str((int(digits[-1]) + 1) % 10)
    return f"{digits[:2]} {digits[2:6]} {digits[6:10]} {digits[10:14]} {digits[14:18]} {digits[18:22]} {digits[22:26]}"


def transactions(today: date, gap: bool = False) -> list[dict]:
    rows = []
    for idx, (y, m) in enumerate(three_months(today)):
        if gap and idx == 1:
            continue
        for day, payee, pl, en, amount, cat in MONTHLY:
            if amount is None:
                amount = ELECTRICITY[idx] if cat == "utilities" else NETFLIX[idx]
            fmt = {"mm": f"{m:02d}", "yyyy": f"{y}"}
            rows.append({"date": date(y, m, day), "payee": payee, "pl": pl.format(**fmt),
                         "en": en.format(**fmt), "amount": amount, "category": cat})
        if idx == 1:
            rows.append({"date": date(y, m, 18), "payee": "Example Assistance S.A.", "pl": "Skladka ubezpieczenie domu",
                         "en": "Home insurance premium", "amount": D("-1240.00"), "category": "insurance"})
            rows.append({"date": date(y, m, 19), "payee": "Jan Kowalski",
                         "pl": f"Zwrot pozyczki, rachunek {fake_account(y * 100 + m)}",
                         "en": f"Loan repayment, account {fake_account(y * 100 + m)}",
                         "amount": D("-60.00"), "category": "other"})
        if idx == 2:
            rows.append({"date": date(y, m, 26), "payee": "Allegro.pl", "pl": "Zwrot Allegro",
                         "en": "Allegro refund", "amount": D("59.99"), "category": "shopping"})
            rows.append({"date": date(y, m, 9), "payee": "Sklep Internetowy",
                         "pl": "Platnosc karta 4111 1111 1111 1111", "en": "Card payment 4111 1111 1111 1111",
                         "amount": D("-35.50"), "category": "other"})
    rows.sort(key=lambda r: (r["date"], r["payee"]))
    balance = D("5000.00")
    for r in rows:
        balance += r["amount"]
        r["balance"] = balance
    return rows


def pl_num(v: Decimal) -> str:
    sign = "-" if v < 0 else ""
    whole, frac = f"{abs(v):.2f}".split(".")
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    return sign + " ".join(groups) + "," + frac


def write_a(rows, path: Path, today: date) -> None:
    first, last = rows[0]["date"], rows[-1]["date"]
    lines = ["#Klient;Anna Nowak (dane testowe)", f"#Okres;{first.isoformat()};{last.isoformat()}",
             "#Waluta;PLN", "",
             "#Data operacji;#Data księgowania;#Opis operacji;#Tytuł;#Nadawca/Odbiorca;#Numer konta;#Kwota;#Saldo po operacji;"]
    for i, r in enumerate(reversed(rows)):
        acct = fake_account(i + 1) if r["payee"] else ""
        lines.append(f"{r['date'].isoformat()};{r['date'].isoformat()};{'PRZELEW' if r['payee'] else 'OPERACJA'};"
                     f"{r['pl']};{r['payee']};{acct};{pl_num(r['amount'])};{pl_num(r['balance'])};")
    lines += ["", f"#Saldo końcowe;{pl_num(rows[-1]['balance'])}"]
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("cp1250"))


def write_b(rows, path: Path, today: date) -> None:
    out = ['"Data transakcji","Opis","Kontrahent","Obciążenia","Uznania","Saldo","Waluta"']
    for r in rows:
        debit = pl_num(-r["amount"]) if r["amount"] < 0 else ""
        credit = pl_num(r["amount"]) if r["amount"] > 0 else ""
        out.append(f'"{r["date"].strftime("%d.%m.%Y")}","{r["pl"]}","{r["payee"]}","{debit}","{credit}",'
                   f'"{pl_num(r["balance"])}","PLN"')
    path.write_text("\n".join(out) + "\n", encoding="utf-8-sig", newline="\n")


def write_c(rows, path: Path, today: date) -> None:
    out = ["Booking date\tDescription\tPayee\tAmount\tCurrency"]
    for r in rows:
        out.append(f"{r['date'].isoformat()}\t{r['en']}\t{r['payee']}\t{r['amount']:.2f}\tPLN")
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def expected(rows) -> dict:
    months = defaultdict(lambda: {"income": D(0), "spending": D(0), "by_category": defaultdict(D)})
    for r in rows:
        m = months[r["date"].strftime("%Y-%m")]
        if r["amount"] > 0:
            m["income"] += r["amount"]
        else:
            m["spending"] += -r["amount"]
        m["by_category"][r["category"]] += r["amount"]
    return {mon: {"income": f"{v['income']:.2f}", "spending": f"{v['spending']:.2f}",
                  "by_category": {c: f"{t:.2f}" for c, t in sorted(v["by_category"].items())}}
            for mon, v in sorted(months.items())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--format", choices=["a", "b", "c"], default="a")
    ap.add_argument("--today")
    ap.add_argument("--gap", action="store_true")
    ap.add_argument("--expected")
    a = ap.parse_args(argv)
    today = date.fromisoformat(a.today) if a.today else date.today()
    rows = transactions(today, a.gap)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    {"a": write_a, "b": write_b, "c": write_c}[a.format](rows, out, today)
    if a.expected:
        Path(a.expected).write_text(json.dumps(expected(rows), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "rows": len(rows), "format": a.format}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
