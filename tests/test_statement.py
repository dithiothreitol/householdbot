"""Unit tests for core/scripts/statement.py on synthetic bank exports."""
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "scripts"))
sys.path.insert(0, str(ROOT / "evals" / "fixtures"))
import statement  # noqa: E402
import make_statement  # noqa: E402
import make_household  # noqa: E402

TODAY = "2026-11-13"


def gen(*argv):
    with redirect_stdout(io.StringIO()):
        make_statement.main([str(a) for a in argv])


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = statement.main([str(a) for a in argv])
    return code, json.loads(buf.getvalue())


class StatementTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hb-stmt-"))
        self.expected = self.tmp / "expected.json"
        for fmt in "abc":
            gen(self.tmp / f"{fmt}.csv", "--format", fmt, "--today", TODAY, "--expected", self.expected)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class Totals(StatementTestCase):
    def test_every_format_sums_to_the_grosz(self):
        exp = json.loads(self.expected.read_text(encoding="utf-8"))
        for fmt in "abc":
            code, out = run("summary", self.tmp / f"{fmt}.csv")
            self.assertEqual(code, 0, out)
            self.assertEqual([m["month"] for m in out["months"]], sorted(exp), fmt)
            for m in out["months"]:
                e = exp[m["month"]]
                self.assertEqual(m["income"], e["income"], (fmt, m["month"]))
                self.assertEqual(m["spending"], e["spending"], (fmt, m["month"]))
                self.assertEqual({c["category"]: c["total"] for c in m["by_category"]}, e["by_category"],
                                 (fmt, m["month"]))

    def test_encodings_and_layouts_are_detected(self):
        code, a = run("parse", self.tmp / "a.csv")
        self.assertEqual(a["encoding"], "cp1250")
        self.assertEqual(a["delimiter"], ";")
        self.assertGreater(a["header_line"], 1)  # preamble before the header
        code, b = run("parse", self.tmp / "b.csv")
        self.assertEqual(b["encoding"], "utf-8-sig")
        self.assertIn("debit", b["columns"])
        code, c = run("parse", self.tmp / "c.csv")
        self.assertEqual(c["delimiter"], "\t")

    def test_amounts_are_texts_in_the_household_language(self):
        code, out = run("summary", self.tmp / "a.csv", "--lang", "pl")
        self.assertEqual(out["months"][0]["income_text"], "8 250,00 zł")
        code, out = run("summary", self.tmp / "a.csv", "--lang", "en")
        self.assertEqual(out["months"][0]["income_text"], "PLN 8,250.00")


class Safety(StatementTestCase):
    def test_account_card_numbers_are_masked(self):
        code, out = run("parse", self.tmp / "a.csv")
        text = json.dumps(out["rows"], ensure_ascii=False)
        self.assertIn("[card …1111]", text)
        self.assertRegex(text, r"\[account …\d{4}\]")
        self.assertIsNone(re.search(r"(?:\d[ -]?){16,}", text))

    def test_missing_rows_break_the_balance(self):
        lines = (self.tmp / "a.csv").read_bytes().decode("cp1250").splitlines()
        tx = [i for i, ln in enumerate(lines) if re.match(r"^\d{4}-\d{2}-\d{2};", ln)]
        del lines[tx[10]]
        (self.tmp / "holed.csv").write_bytes("\r\n".join(lines).encode("cp1250"))
        code, out = run("summary", self.tmp / "holed.csv")
        self.assertEqual(len(out["balance_check"]["breaks"]), 1)
        self.assertTrue(any("missing" in w for w in out["warnings"]))

    def test_a_missing_month_is_missing_not_zero(self):
        gen(self.tmp / "gap.csv", "--format", "b", "--today", TODAY, "--gap")
        code, out = run("summary", self.tmp / "gap.csv")
        self.assertEqual(out["months_without_transactions"], ["2026-09"])
        self.assertTrue(any("missing, not zero" in w for w in out["warnings"]))

    def test_unreadable_file(self):
        bad = self.tmp / "bad.csv"
        bad.write_text("just some text\nwithout columns\n", encoding="utf-8")
        code, out = run("parse", bad)
        self.assertEqual(code, 1)
        self.assertIn("no header row", out["errors"][0])


class Recurring(StatementTestCase):
    def test_price_rise_and_periods(self):
        code, out = run("recurring", self.tmp / "b.csv")
        by_party = {r["counterparty"]: r for r in out["recurring"]}
        self.assertTrue(by_party["NETFLIX.COM"]["price_rise"])
        self.assertEqual(by_party["NETFLIX.COM"]["change_percent"], "12.2")
        self.assertEqual(by_party["Example Energia S.A."]["period"], "monthly")
        self.assertFalse(by_party["Spotify AB"]["price_rise"])


class Parsing(unittest.TestCase):
    def test_amount_formats(self):
        cases = {"1 234,56": "1234.56", "-1.234,56": "-1234.56", "1,234.56": "1234.56",
                 "(12,30)": "-12.30", "12,3 zł": "12.3", "7450.00": "7450.00", "+59,99": "59.99",
                 "1 240,00 PLN": "1240.00"}
        for raw, exp in cases.items():
            self.assertEqual(statement.parse_amount(raw), Decimal(exp), raw)
        self.assertIsNone(statement.parse_amount(""))
        self.assertIsNone(statement.parse_amount("—"))

    def test_dates(self):
        for raw in ("2026-11-13", "13.11.2026", "13-11-2026", "13/11/2026", "2026.11.13", "2026-11-13 10:15"):
            self.assertEqual(statement.parse_day(raw), date(2026, 11, 13), raw)

    def test_longest_rule_wins(self):
        cats = statement.load_categories()
        rows = [{"counterparty": "RTV EURO AGD", "description": "", "amount": "-99.00"},
                {"counterparty": "Google Play", "description": "", "amount": "-9.99"},
                {"counterparty": "Play", "description": "abonament", "amount": "-45.00"}]
        statement.categorise(rows, cats, [])
        self.assertEqual([r["category"] for r in rows], ["shopping", "subscriptions", "utilities"])


class HouseholdRules(StatementTestCase):
    def test_add_rule_needs_approval_and_is_used(self):
        home = self.tmp / "household"
        make_household.write(home, date.fromisoformat(TODAY))
        code, out = run("add-rule", home, "--match", "Jan Kowalski", "--category", "transfers")
        self.assertEqual(code, 1)
        code, out = run("add-rule", home, "--match", "Jan Kowalski", "--category", "transfers",
                        "--approved-by", "Anna", "--today", TODAY)
        self.assertEqual(code, 0, out)
        log = (home / "log" / "decisions.md").read_text(encoding="utf-8")
        self.assertIn("zgoda: Anna · dodano regułę kategorii Jan Kowalski → transfers", log)
        code, out = run("summary", self.tmp / "a.csv", "--household", home)
        self.assertEqual(out["uncategorised"], 1)  # only the card payment is left


if __name__ == "__main__":
    unittest.main()
