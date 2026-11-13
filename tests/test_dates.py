"""Unit tests for core/scripts/dates.py (the date proof layer)."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "scripts"))
import dates  # noqa: E402

PL = dates.load_pack("PL")


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = dates.main(list(argv))
    return code, json.loads(buf.getvalue())


class EasterAndHolidays(unittest.TestCase):
    def test_easter_known_years(self):
        known = {1943: date(1943, 4, 25), 2024: date(2024, 3, 31), 2025: date(2025, 4, 20),
                 2026: date(2026, 4, 5), 2027: date(2027, 3, 28), 2038: date(2038, 4, 25),
                 2285: date(2285, 3, 22)}
        for year, expected in known.items():
            self.assertEqual(dates.easter_sunday(year), expected, year)

    def test_pl_2026_has_fourteen_holidays(self):
        hol = PL.holidays(2026)
        self.assertEqual(len(hol), 14)
        self.assertEqual(hol[date(2026, 6, 4)], "Boże Ciało")
        self.assertEqual(hol[date(2026, 5, 24)], "Zielone Świątki")
        self.assertIn(date(2026, 12, 24), hol)

    def test_christmas_eve_only_from_2025(self):
        self.assertNotIn(date(2024, 12, 24), PL.holidays(2024))
        self.assertTrue(PL.is_business_day(date(2024, 12, 24)))
        self.assertFalse(PL.is_business_day(date(2025, 12, 24)))

    def test_saturday_is_not_a_business_day(self):
        self.assertEqual(PL.non_business_reason(date(2026, 11, 14)), "Saturday")


class Deadlines(unittest.TestCase):
    def test_end_on_holiday_moves_forward_plan_moves_back(self):
        r = dates.deadline(PL, date(2026, 10, 28), 14, "days", "administrative")
        self.assertEqual(r["raw_end"]["date"], "2026-11-11")
        self.assertEqual(r["due_date"], "2026-11-12")
        self.assertEqual(r["do_by"], "2026-11-10")
        self.assertIn("Narodowe Święto Niepodległości", r["due_note"])
        self.assertIn("margin", r["do_by_note"])

    def test_end_on_saturday(self):
        r = dates.deadline(PL, date(2026, 10, 24), 14, "days", "administrative")
        self.assertEqual(r["raw_end"]["date"], "2026-11-07")
        self.assertEqual(r["due_date"], "2026-11-09")
        self.assertEqual(r["do_by"], "2026-11-06")

    def test_christmas_cluster(self):
        r = dates.deadline(PL, date(2026, 12, 10), 14, "days", "civil")
        self.assertEqual(r["raw_end"]["date"], "2026-12-24")
        self.assertEqual(r["due_date"], "2026-12-28")
        self.assertEqual(r["do_by"], "2026-12-23")

    def test_business_day_end_is_unchanged(self):
        r = dates.deadline(PL, date(2026, 11, 3), 14, "days", "administrative")
        self.assertEqual(r["due_date"], "2026-11-17")
        self.assertEqual(r["do_by"], "2026-11-17")
        self.assertEqual(r["arithmetic"], "Tue 2026-11-03 + 14 days = Tue 2026-11-17")

    def test_months_clamp_to_month_end(self):
        self.assertEqual(dates.add_period(date(2026, 1, 31), 1, "months"), date(2026, 2, 28))
        self.assertEqual(dates.add_period(date(2028, 2, 29), 1, "years"), date(2029, 2, 28))

    def test_calendar_rule_does_not_roll(self):
        r = dates.deadline(PL, date(2026, 10, 31), 14, "days", "calendar")
        self.assertEqual(r["due_date"], "2026-11-14")
        self.assertEqual(r["do_by"], "2026-11-13")

    def test_transit_and_holiday(self):
        r = dates.plan_do_by(PL, date(2026, 11, 16), 5)
        self.assertEqual(r["do_by"], "2026-11-10")
        self.assertIn("rolled back from Wed 2026-11-11", r["do_by_note"])

    def test_business_days(self):
        self.assertEqual(dates.add_period(date(2026, 11, 10), 2, "business_days", PL), date(2026, 11, 13))

    def test_unknown_rule(self):
        with self.assertRaises(dates.InputError):
            dates.deadline(PL, date(2026, 1, 1), 1, "days", "nope")


class BandsAndRecurrence(unittest.TestCase):
    def test_band_boundaries(self):
        expected = {-1: "overdue", 0: "now", 6: "now", 7: "soon", 29: "soon", 30: "coming",
                    89: "coming", 90: "later"}
        for days, name in expected.items():
            self.assertEqual(dates.band(days)["band"], name, days)

    def test_monthly_keeps_anchor(self):
        self.assertEqual(dates.next_occurrence(date(2026, 1, 31), "monthly"), date(2026, 2, 28))
        self.assertEqual(dates.next_occurrence(date(2026, 2, 28), "monthly", 31), date(2026, 3, 31))

    def test_every_n(self):
        self.assertEqual(dates.next_occurrence(date(2026, 11, 9), "every 2 months"), date(2027, 1, 9))
        self.assertEqual(dates.next_occurrence(date(2026, 11, 9), "every 5 years"), date(2031, 11, 9))
        self.assertEqual(dates.next_occurrence(date(2026, 11, 9), "weekly"), date(2026, 11, 16))

    def test_free_text_is_not_guessed(self):
        self.assertIsNone(dates.next_occurrence(date(2026, 11, 9), "15 Mar, 15 May, 15 Sep, 15 Nov"))
        self.assertIsNone(dates.next_occurrence(date(2026, 11, 9), "none"))


class Statutory(unittest.TestCase):
    def test_property_tax_2026(self):
        rows = dates.statutory_dates(PL, 2026, ["property-tax"])
        nov = [r for r in rows if r["statutory_date"] == "2026-11-15"][0]
        self.assertEqual(nov["due_date"], "2026-11-16")
        self.assertEqual(nov["do_by"], "2026-11-13")
        self.assertEqual(nov["provenance"], "country pack rule — verify")
        self.assertEqual(len(rows), 4)


class CommandLine(unittest.TestCase):
    def test_info(self):
        code, out = run("info", "2026-11-11", "--country", "PL")
        self.assertEqual(code, 0)
        self.assertFalse(out["business_day"])
        self.assertEqual(out["local"], "śr. 11.11.2026")
        self.assertEqual(out["next_business_day"]["date"], "2026-11-12")

    def test_window(self):
        code, out = run("window", "--country", "PL", "--from", "2026-11-03",
                        "--id", "appeal-administrative-decision")
        self.assertEqual(code, 0)
        self.assertEqual(out["due_date"], "2026-11-17")
        self.assertEqual(out["provenance"], "country pack rule — verify")

    def test_cancel_by(self):
        code, out = run("cancel-by", "--country", "PL", "--term-end", "2027-03-14",
                        "--notice", "1", "--unit", "months")
        self.assertEqual(out["due_date"], "2027-02-14")
        self.assertEqual(out["do_by"], "2027-02-12")

    def test_deemed(self):
        code, out = run("deemed", "--country", "PL", "--from", "2026-11-02", "--id", "registered-letter-office")
        self.assertEqual(out["deemed_delivered"]["date"], "2026-11-16")

    def test_e_delivery_is_the_day_after_fourteen_days(self):
        code, out = run("deemed", "--country", "PL", "--from", "2026-11-02", "--id", "e-delivery")
        self.assertEqual(out["deemed_delivered"]["date"], "2026-11-17")

    def test_pleas_take_one_month(self):
        code, out = run("window", "--country", "PL", "--from", "2026-10-30", "--id", "pleas-order-for-payment")
        self.assertEqual(out["raw_end"]["date"], "2026-11-30")
        self.assertEqual(out["due_date"], "2026-11-30")

    def test_withdrawal_after_home_visit_is_thirty_days(self):
        code, out = run("window", "--country", "PL", "--from", "2026-11-02", "--id", "consumer-withdrawal-home-visit")
        self.assertEqual(out["due_date"], "2026-12-02")

    def test_oc_cancel_by_one_day_before_term_end(self):
        code, out = run("cancel-by", "--country", "PL", "--term-end", "2027-03-14", "--notice", "1")
        self.assertEqual(out["due_date"], "2027-03-13")
        self.assertEqual(out["do_by"], "2027-03-12")

    def test_bad_date_is_an_error(self):
        code, out = run("info", "2026-02-30", "--country", "PL")
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])

    def test_missing_pack(self):
        code, out = run("info", "2026-02-03", "--country", "XX")
        self.assertEqual(code, 1)
        self.assertIn("model calculation", out["errors"][0])


if __name__ == "__main__":
    unittest.main()
