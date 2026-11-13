#!/usr/bin/env python3
"""Date arithmetic for HouseholdBot.

Public holidays, business days, deadlines counted from an event, the safe
"do by" date, urgency bands, recurrence and statutory dates from a country
pack. Standard library only. Every command prints one JSON object.

Country data is read from ../locale/<CC>.json relative to this file, or from
the path given with --pack. Language data (weekday and month names, date and
amount formats, notes) is read from ../i18n/<lang>.json. English is the
default language; pass --lang pl for Polish.

Examples:
  python3 dates.py info 2026-11-11 --country PL --lang pl
  python3 dates.py deadline --country PL --from 2026-10-28 --amount 14 --unit days --rule administrative
  python3 dates.py window --country PL --from 2026-11-03 --id appeal-administrative-decision
  python3 dates.py do-by --country PL --due 2026-11-16 --transit 1
  python3 dates.py band --today 2026-11-13 --date 2026-11-20
  python3 dates.py next --due 2026-01-31 --recurrence monthly
  python3 dates.py recurring --country PL --year 2027
  python3 dates.py amount --value 1240.00 --currency PLN --lang pl
"""
from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "1.1.0"
HERE = Path(__file__).resolve().parent
LOCALE_DIR = HERE.parent / "locale"
I18N_DIR = HERE.parent / "i18n"
DEFAULT_LANG = "en"

WEEKDAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_INDEX = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EVERY_RE = re.compile(r"^every\s+(\d+)\s+(day|week|month|year)s?$")

BANDS = [
    # (name, lower bound inclusive, upper bound exclusive)
    ("overdue", None, 0),
    ("now", 0, 7),
    ("soon", 7, 30),
    ("coming", 30, 90),
    ("later", 90, None),
]


class InputError(Exception):
    """Bad input from the caller: an unreadable date, an unknown rule."""


# --------------------------------------------------------------------------
# Parsing and language
# --------------------------------------------------------------------------

def parse_date(value: str) -> date:
    if not isinstance(value, str) or not ISO_RE.match(value):
        raise InputError(f"not an ISO date (YYYY-MM-DD): {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError(f"not a real calendar date: {value!r}") from exc


def text_en(d: date) -> str:
    """Weekday and ISO date, the stable form used in notes for the model."""
    return f"{WEEKDAYS_EN[d.weekday()]} {d.isoformat()}"


class Lang:
    """Formats for one language: dates, amounts, notes, statuses, log lines."""

    def __init__(self, data: dict, requested: str):
        self.data = data
        self.code = data.get("lang", DEFAULT_LANG)
        self.requested = requested

    def date(self, d: date) -> str:
        return self.data["date_format"].format(
            wd=self.data["weekdays_short"][d.weekday()],
            wdl=self.data["weekdays_long"][d.weekday()],
            d=d.day, dd=f"{d.day:02d}", mm=f"{d.month:02d}",
            mon=self.data["months_short"][d.month - 1], yyyy=f"{d.year:04d}")

    def weekday_long(self, d: date) -> str:
        return self.data["weekdays_long"][d.weekday()]

    def number(self, value) -> str:
        try:
            q = Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError) as exc:
            raise InputError(f"not an amount: {value!r}") from exc
        sign = "-" if q < 0 else ""
        whole, frac = f"{abs(q):.2f}".split(".")
        groups = []
        while len(whole) > 3:
            groups.insert(0, whole[-3:])
            whole = whole[:-3]
        groups.insert(0, whole)
        return sign + self.data["thousands_separator"].join(groups) + self.data["decimal_separator"] + frac

    def amount(self, value, currency: str | None) -> str | None:
        if value is None:
            return None
        code = currency or ""
        symbol = self.data.get("currency_symbols", {}).get(code, code)
        return self.data["amount_format"].format(code=code, symbol=symbol, number=self.number(value)).strip()

    def plural_index(self, n: int) -> int:
        n = abs(int(n))
        if self.code == "pl":
            if n == 1:
                return 0
            if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
                return 1
            return 2
        return 0 if n == 1 else 1

    def unit(self, unit: str, n: int | None = None) -> str:
        """The unit word for n (\"1 day\", \"5 days\", \"2 dni\", \"5 dni\", \"1 dzień\")."""
        forms = self.data.get("units", {}).get(unit, unit)
        if isinstance(forms, str):
            return forms
        word = forms[min(self.plural_index(2 if n is None else n), len(forms) - 1)]
        return word if n is None else f"{n} {word}"

    def note(self, key: str, **kw) -> str:
        return self.data["notes"][key].format(**kw)

    def status(self, status: str) -> str:
        return self.data.get("statuses", {}).get(status, status)

    def band_label(self, band_name: str) -> str:
        return self.data.get("bands", {}).get(band_name, band_name)

    def log(self, key: str, **kw) -> str:
        return self.data["log"][key].format(**kw)

    def quote(self, text: str) -> str:
        left, right = self.data.get("quotes", ['"', '"'])
        return f"{left}{text}{right}"


_LANG_CACHE: dict[str, Lang] = {}


def load_lang(code: str | None = None) -> Lang:
    """The language file for code; English when the code is missing or unknown."""
    requested = (code or DEFAULT_LANG).strip().lower()[:2] or DEFAULT_LANG
    if requested in _LANG_CACHE:
        return _LANG_CACHE[requested]
    path = I18N_DIR / f"{requested}.json"
    if not path.exists():
        path = I18N_DIR / f"{DEFAULT_LANG}.json"
    with path.open(encoding="utf-8") as fh:
        lang = Lang(json.load(fh), requested)
    _LANG_CACHE[requested] = lang
    return lang


def describe(d: date, lang: Lang) -> dict:
    return {"date": d.isoformat(), "text": text_en(d), "local": lang.date(d)}


# --------------------------------------------------------------------------
# Country packs
# --------------------------------------------------------------------------

class Pack:
    """A country pack: holidays, weekend, counting rules and statutory dates."""

    def __init__(self, data: dict, source: str):
        self.data = data
        self.source = source
        self.code = data.get("pack", "??")
        self.reviewed = data.get("reviewed", "unknown")
        self.weekend = {WEEKDAY_INDEX[d] for d in data.get("weekend", ["saturday", "sunday"])}
        self._holiday_cache: dict[int, dict[date, dict]] = {}

    def label(self) -> str:
        return f"{self.code} pack, reviewed {self.reviewed}"

    def holidays(self, year: int) -> dict[date, dict]:
        """Every public holiday of the year, mapped to its entry (names per language)."""
        if year in self._holiday_cache:
            return self._holiday_cache[year]
        out: dict[date, dict] = {}
        spec = self.data.get("holidays", {})
        for h in spec.get("fixed", []):
            if h.get("from_year") and year < h["from_year"]:
                continue
            if h.get("to_year") and year > h["to_year"]:
                continue
            month, day = (int(x) for x in h["date"].split("-"))
            out[date(year, month, day)] = h
        if spec.get("easter_relative"):
            base = easter_sunday(year)
            for h in spec["easter_relative"]:
                if h.get("from_year") and year < h["from_year"]:
                    continue
                out[base + timedelta(days=int(h["offset"]))] = h
        self._holiday_cache[year] = out
        return out

    def holiday_name(self, d: date, lang: Lang | None = None) -> str | None:
        h = self.holidays(d.year).get(d)
        if not h:
            return None
        if lang is not None and h.get(f"name_{lang.code}"):
            return h[f"name_{lang.code}"]
        return h["name"]

    def non_business_reason(self, d: date, lang: Lang | None = None) -> str | None:
        lang = lang or load_lang(DEFAULT_LANG)
        name = self.holiday_name(d, lang)
        if name:
            return lang.note("holiday", name=name)
        if d.weekday() in self.weekend:
            return lang.weekday_long(d)
        return None

    def is_business_day(self, d: date) -> bool:
        return d.weekday() not in self.weekend and d not in self.holidays(d.year)

    def roll_forward(self, d: date) -> date:
        while not self.is_business_day(d):
            d += timedelta(days=1)
        return d

    def roll_back(self, d: date) -> date:
        while not self.is_business_day(d):
            d -= timedelta(days=1)
        return d

    def add_business_days(self, d: date, n: int) -> date:
        step = 1 if n >= 0 else -1
        remaining = abs(n)
        while remaining:
            d += timedelta(days=step)
            if self.is_business_day(d):
                remaining -= 1
        return d

    def rule(self, rule_id: str) -> dict:
        rules = self.data.get("counting_rules", {})
        if rule_id not in rules:
            raise InputError(f"unknown counting rule {rule_id!r}; known: {sorted(rules)}")
        return rules[rule_id]

    def entry(self, section: str, entry_id: str) -> dict:
        for item in self.data.get(section, []):
            if item.get("id") == entry_id:
                return item
        known = [i.get("id") for i in self.data.get(section, [])]
        raise InputError(f"unknown {section} id {entry_id!r}; known: {known}")


def load_pack(country: str | None = None, path: str | None = None) -> Pack:
    if path:
        p = Path(path)
    elif country:
        p = LOCALE_DIR / f"{country.upper()}.json"
    else:
        raise InputError("give --country <CC> or --pack <path>")
    if not p.exists():
        raise InputError(
            f"no country pack at {p}. Work from dates stated in documents and tag "
            "computed dates 'model calculation — verify'."
        )
    with p.open(encoding="utf-8") as fh:
        return Pack(json.load(fh), str(p))


# --------------------------------------------------------------------------
# Pure date arithmetic
# --------------------------------------------------------------------------

def easter_sunday(year: int) -> date:
    """Western (Gregorian) Easter Sunday, anonymous Gregorian algorithm."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    month = (h + el - 7 * m + 114) // 31
    day = (h + el - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def add_months(d: date, n: int, anchor_day: int | None = None) -> date:
    """Add calendar months; a day missing in the target month becomes its last day."""
    total = d.month - 1 + n
    year = d.year + total // 12
    month = total % 12 + 1
    day = anchor_day or d.day
    return date(year, month, min(day, calendar.monthrange(year, month)[1]))


def add_period(start: date, amount: int, unit: str, pack: Pack | None = None) -> date:
    unit = unit.rstrip("s") if unit != "business_days" else unit
    if unit == "day":
        return start + timedelta(days=amount)
    if unit == "week":
        return start + timedelta(weeks=amount)
    if unit == "month":
        return add_months(start, amount)
    if unit == "year":
        return add_months(start, 12 * amount)
    if unit == "business_days":
        if pack is None:
            raise InputError("business days need a country pack")
        return pack.add_business_days(start, amount)
    raise InputError(f"unknown unit {unit!r}; use days, weeks, months, years or business_days")


def band(days: int, lang: Lang | None = None) -> dict:
    lang = lang or load_lang(DEFAULT_LANG)
    for name, lo, hi in BANDS:
        if (lo is None or days >= lo) and (hi is None or days < hi):
            return {"band": name, "label": lang.band_label(name)}
    raise AssertionError("unreachable")


def next_occurrence(prev: date, recurrence: str, anchor_day: int | None = None) -> date | None:
    """Next due date of a recurring obligation, or None when the rule is free text."""
    r = (recurrence or "").strip().lower()
    if r in ("", "none"):
        return None
    if r == "weekly":
        return prev + timedelta(weeks=1)
    if r in ("fortnightly", "biweekly"):
        return prev + timedelta(weeks=2)
    if r == "monthly":
        return add_months(prev, 1, anchor_day)
    if r == "quarterly":
        return add_months(prev, 3, anchor_day)
    if r in ("half-yearly", "semiannual"):
        return add_months(prev, 6, anchor_day)
    if r in ("yearly", "annual", "annually"):
        return add_months(prev, 12, anchor_day)
    m = EVERY_RE.match(r)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "day":
            return prev + timedelta(days=n)
        if unit == "week":
            return prev + timedelta(weeks=n)
        if unit == "month":
            return add_months(prev, n, anchor_day)
        return add_months(prev, 12 * n, anchor_day)
    return None


# --------------------------------------------------------------------------
# Composite calculations used by the skills
# --------------------------------------------------------------------------

def plan_do_by(pack: Pack, due: date, transit_days: int = 0, lang: Lang | None = None) -> dict:
    """The date the household plans to: transit subtracted, rolled back to a business day."""
    lang = lang or load_lang(DEFAULT_LANG)
    notes = []
    d = due - timedelta(days=transit_days)
    if transit_days:
        notes.append(lang.note("transit", days=lang.unit("days", transit_days), date=lang.date(due)))
    reason = pack.non_business_reason(d, lang)
    if reason:
        rolled = pack.roll_back(d)
        notes.append(lang.note("rolled_back", date=lang.date(d), reason=reason))
        d = rolled
    return {
        "do_by": d.isoformat(),
        "do_by_text": text_en(d),
        "do_by_local": lang.date(d),
        "do_by_note": "; ".join(notes),
    }


def deadline(pack: Pack, start: date, amount: int, unit: str, rule_id: str,
             transit_days: int = 0, lang: Lang | None = None) -> dict:
    lang = lang or load_lang(DEFAULT_LANG)
    rule = pack.rule(rule_id)
    raw_end = add_period(start, amount, unit, pack)
    due = raw_end
    due_note = ""
    if rule.get("end_roll") == "forward":
        reason = pack.non_business_reason(raw_end, lang)
        if reason:
            due = pack.roll_forward(raw_end)
            due_note = lang.note("moved_forward", date=lang.date(raw_end), reason=reason,
                                 new_date=lang.date(due), law=rule.get("law", rule_id))
    result = {
        "start": describe(start, lang),
        "amount": amount,
        "unit": unit,
        "rule": rule_id,
        "law": rule.get("law"),
        "arithmetic": f"{lang.date(start)} + {lang.unit(unit, amount)} = {lang.date(raw_end)}",
        "raw_end": describe(raw_end, lang),
        "due_date": due.isoformat(),
        "due_date_text": text_en(due),
        "due_date_local": lang.date(due),
        "due_note": due_note,
        "met_by": rule.get("met_by"),
        "lang": lang.code,
    }
    # The plan never relies on the statutory forward roll: do_by is worked
    # back from the raw end of the period, so the forward roll stays margin.
    result.update(plan_do_by(pack, raw_end, transit_days, lang))
    if due != raw_end:
        result["do_by_note"] = "; ".join(n for n in (result["do_by_note"], lang.note("margin")) if n)
    return result


def statutory_dates(pack: Pack, year: int, ids: list[str] | None = None,
                    transit_days: int = 0, lang: Lang | None = None) -> list[dict]:
    lang = lang or load_lang(DEFAULT_LANG)
    out = []
    for item in pack.data.get("recurring", []):
        if ids and item["id"] not in ids:
            continue
        rule = pack.data.get("counting_rules", {}).get(item.get("counting", ""), {})
        for md in item.get("dates", []):
            m_txt, d_txt = md.split("-")
            month = int(m_txt)
            day = calendar.monthrange(year, month)[1] if d_txt.upper() == "L" else int(d_txt)
            raw = date(year, month, day)
            due = raw
            due_note = ""
            if rule.get("end_roll") == "forward" and not pack.is_business_day(raw):
                due = pack.roll_forward(raw)
                due_note = lang.note("moved_forward", date=lang.date(raw),
                                     reason=pack.non_business_reason(raw, lang),
                                     new_date=lang.date(due), law=rule.get("law", item.get("counting")))
            row = {
                "id": item["id"],
                "title": item.get(f"title_{lang.code}") or item.get("title"),
                "kind": item.get("kind"),
                "category": item.get("category"),
                "applies_when": item.get("applies_when"),
                "statutory_date": raw.isoformat(),
                "due_date": due.isoformat(),
                "due_date_text": text_en(due),
                "due_date_local": lang.date(due),
                "due_note": due_note,
                "lead_time_days": item.get("lead_time_days"),
                "law": item.get("law"),
                "provenance": "country pack rule — verify",
            }
            if item.get("window_opens"):
                om, od = (int(x) for x in item["window_opens"].split("-"))
                row["window_opens"] = date(year, om, od).isoformat()
            row.update(plan_do_by(pack, raw, transit_days, lang))
            if due != raw:
                row["do_by_note"] = "; ".join(n for n in (row["do_by_note"], lang.note("margin")) if n)
            out.append(row)
    out.sort(key=lambda r: (r["due_date"], r["id"]))
    return out


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def _pack(args) -> Pack:
    return load_pack(getattr(args, "country", None), getattr(args, "pack", None))


def _lang(args) -> Lang:
    return load_lang(getattr(args, "lang", None))


def cmd_holidays(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    hol = pack.holidays(args.year)
    return {
        "year": args.year,
        "pack": pack.label(),
        "lang": lang.code,
        "holidays": [
            {"date": d.isoformat(), "text": text_en(d), "local": lang.date(d),
             "name": pack.holiday_name(d, lang)}
            for d in sorted(hol)
        ],
        "law": pack.data.get("holidays", {}).get("law"),
    }


def cmd_info(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    d = parse_date(args.date)
    reason = pack.non_business_reason(d, lang)
    return {
        **describe(d, lang),
        "business_day": reason is None,
        "reason": reason,
        "previous_business_day": describe(pack.roll_back(d), lang) if reason else None,
        "next_business_day": describe(pack.roll_forward(d), lang) if reason else None,
        "pack": pack.label(),
        "lang": lang.code,
    }


def cmd_deadline(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    res = deadline(pack, parse_date(args.start), args.amount, args.unit, args.rule, args.transit, lang)
    res["pack"] = pack.label()
    return res


def cmd_window(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    w = pack.entry("response_windows", args.id)
    res = deadline(pack, parse_date(args.start), int(w["amount"]), w["unit"], w["counting"],
                   args.transit, lang)
    res.update({"window": w["id"], "title": w.get(f"title_{lang.code}") or w.get("title"),
                "counted_from": w.get("from"), "law": w.get("law"), "pack": pack.label(),
                "provenance": "country pack rule — verify"})
    if w.get("met_by"):
        # A window for the other side (a firm's reply, an insurer's payment) says what
        # meets it; the general rule describes the household's own statements.
        res["met_by"] = w["met_by"]
    if w.get("silence"):
        res["silence"] = w["silence"]
    return res


def cmd_deemed(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    rule = pack.entry("deemed_delivery", args.id)
    start = parse_date(args.start)
    deemed = start + timedelta(days=int(rule["days"]))
    return {
        "rule": rule["id"],
        "title": rule.get("title"),
        "counted_from": rule.get("from"),
        "start": describe(start, lang),
        "deemed_delivered": describe(deemed, lang),
        "arithmetic": f"{lang.date(start)} + {lang.unit('days', int(rule['days']))} = {lang.date(deemed)}",
        "law": rule.get("law"),
        "note": rule.get("note"),
        "pack": pack.label(),
        "lang": lang.code,
        "provenance": "country pack rule — verify",
    }


def cmd_do_by(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    due = parse_date(args.due)
    res = {"due_date": due.isoformat(), "due_date_text": text_en(due),
           "due_date_local": lang.date(due), "pack": pack.label(), "lang": lang.code}
    res.update(plan_do_by(pack, due, args.transit, lang))
    return res


def cmd_band(args) -> dict:
    lang = _lang(args)
    today = parse_date(args.today) if args.today else date.today()
    d = parse_date(args.date)
    days = (d - today).days
    return {"today": today.isoformat(), "today_source": "argument" if args.today else "system clock",
            "date": d.isoformat(), "text": text_en(d), "local": lang.date(d), "days": days,
            "lang": lang.code, **band(days, lang)}


def cmd_next(args) -> dict:
    lang = _lang(args)
    prev = parse_date(args.due)
    nxt = next_occurrence(prev, args.recurrence, args.anchor_day)
    if nxt is None:
        return {"ok": False, "errors": [
            f"recurrence {args.recurrence!r} cannot be computed; ask the household for the next date"]}
    res = {"previous": prev.isoformat(), "recurrence": args.recurrence,
           "next_due_date": nxt.isoformat(), "next_due_text": text_en(nxt),
           "next_due_local": lang.date(nxt), "lang": lang.code}
    if args.country or args.pack:
        res.update(plan_do_by(_pack(args), nxt, args.transit, lang))
    return res


def cmd_cancel_by(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    term_end = parse_date(args.term_end)
    due = add_period(term_end, -args.notice, args.unit, pack)
    res = {
        "term_end": describe(term_end, lang),
        "notice": lang.unit(args.unit, args.notice),
        "arithmetic": f"{lang.date(term_end)} - {lang.unit(args.unit, args.notice)} = {lang.date(due)}",
        "due_date": due.isoformat(),
        "due_date_text": text_en(due),
        "due_date_local": lang.date(due),
        "pack": pack.label(),
        "lang": lang.code,
    }
    res.update(plan_do_by(pack, due, args.transit, lang))
    return res


def cmd_recurring(args) -> dict:
    pack, lang = _pack(args), _lang(args)
    ids = [i.strip() for i in args.ids.split(",")] if args.ids else None
    return {"year": args.year, "pack": pack.label(), "lang": lang.code,
            "dates": statutory_dates(pack, args.year, ids, args.transit, lang)}


def cmd_amount(args) -> dict:
    lang = _lang(args)
    return {"value": args.value, "currency": args.currency, "lang": lang.code,
            "text": lang.amount(args.value, args.currency)}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dates.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="command", required=True)

    def with_lang(sp):
        sp.add_argument("--lang", default=DEFAULT_LANG,
                        help="language of the dates and notes in the output: en (default) or pl")
        return sp

    def with_pack(sp):
        sp.add_argument("--country", help="ISO country code of the pack, e.g. PL")
        sp.add_argument("--pack", help="path to a country pack JSON file")
        return with_lang(sp)

    s = with_pack(sub.add_parser("holidays", help="public holidays in a year"))
    s.add_argument("--year", type=int, required=True)
    s.set_defaults(func=cmd_holidays)

    s = with_pack(sub.add_parser("info", help="weekday, business day or not"))
    s.add_argument("date")
    s.set_defaults(func=cmd_info)

    s = with_pack(sub.add_parser("deadline", help="deadline counted from an event"))
    s.add_argument("--from", dest="start", required=True)
    s.add_argument("--amount", type=int, required=True)
    s.add_argument("--unit", default="days",
                   choices=["days", "weeks", "months", "years", "business_days"])
    s.add_argument("--rule", required=True, help="counting rule id from the pack")
    s.add_argument("--transit", type=int, default=0, help="days allowed for delivery")
    s.set_defaults(func=cmd_deadline)

    s = with_pack(sub.add_parser("window", help="a named response window from the pack"))
    s.add_argument("--from", dest="start", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--transit", type=int, default=0)
    s.set_defaults(func=cmd_window)

    s = with_pack(sub.add_parser("deemed", help="deemed delivery date"))
    s.add_argument("--from", dest="start", required=True,
                   help="the date the deemed-delivery period starts, as the pack rule names it")
    s.add_argument("--id", required=True)
    s.set_defaults(func=cmd_deemed)

    s = with_pack(sub.add_parser("do-by", help="safe planning date for a due date"))
    s.add_argument("--due", required=True)
    s.add_argument("--transit", type=int, default=0)
    s.set_defaults(func=cmd_do_by)

    s = with_lang(sub.add_parser("band", help="urgency band of a date"))
    s.add_argument("--date", required=True)
    s.add_argument("--today")
    s.set_defaults(func=cmd_band)

    s = with_pack(sub.add_parser("next", help="next occurrence of a recurring obligation"))
    s.add_argument("--due", required=True)
    s.add_argument("--recurrence", required=True)
    s.add_argument("--anchor-day", type=int)
    s.add_argument("--transit", type=int, default=0)
    s.set_defaults(func=cmd_next)

    s = with_pack(sub.add_parser("cancel-by", help="last day to give notice before a term ends"))
    s.add_argument("--term-end", required=True)
    s.add_argument("--notice", type=int, required=True)
    s.add_argument("--unit", default="days", choices=["days", "weeks", "months"])
    s.add_argument("--transit", type=int, default=0)
    s.set_defaults(func=cmd_cancel_by)

    s = with_pack(sub.add_parser("recurring", help="statutory dates from the pack for a year"))
    s.add_argument("--year", type=int, required=True)
    s.add_argument("--ids", help="comma-separated ids; default all")
    s.add_argument("--transit", type=int, default=0)
    s.set_defaults(func=cmd_recurring)

    s = with_lang(sub.add_parser("amount", help="an amount written the household's way"))
    s.add_argument("--value", required=True, help='the amount as in the register, e.g. "1240.00"')
    s.add_argument("--currency", required=True, help="ISO 4217 code, e.g. PLN")
    s.set_defaults(func=cmd_amount)
    return p


def emit(obj: dict, code: int = 0) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    obj.setdefault("ok", code == 0)
    obj.setdefault("calculated_by", f"dates.py {VERSION}")
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    return code


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = args.func(args)
    except InputError as exc:
        return emit({"ok": False, "errors": [str(exc)]}, 1)
    return emit(result, 0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    sys.exit(main())
