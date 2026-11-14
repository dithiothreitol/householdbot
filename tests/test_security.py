"""Tests for the Stage 4 security fixes: document text kept off command lines, writes
kept inside the household folder, identifiers refused, the decisions log kept to one
plain line per change, merges limited to real conflict copies."""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "scripts"))
sys.path.insert(0, str(ROOT / "evals" / "fixtures"))
import chores  # noqa: E402
import make_household  # noqa: E402
import record  # noqa: E402
import statement  # noqa: E402

TODAY = "2026-11-13"


def run(module, *argv, stdin: str | None = None):
    buf = io.StringIO()
    patches = []
    if stdin is not None:
        fake = io.TextIOWrapper(io.BytesIO(stdin.encode("utf-8")), encoding="utf-8")
        patches.append(mock.patch.object(sys, "stdin", fake))
    for p in patches:
        p.start()
    try:
        with redirect_stdout(buf):
            code = module.main([str(a) for a in argv])
    finally:
        for p in patches:
            p.stop()
    return code, json.loads(buf.getvalue())


def iban(country: str, bban: str) -> str:
    """A syntactically valid IBAN for a made-up account, built at run time."""
    raw = bban + country + "00"
    check = 98 - int("".join(str(int(ch, 36)) for ch in raw)) % 97
    return f"{country}{check:02d}{bban}"


def luhn_complete(prefix: str) -> str:
    for d in "0123456789":
        if record.luhn_valid(prefix + d):
            return prefix + d
    raise AssertionError


class Household(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hb-sec-"))
        self.home = self.tmp / "household"
        make_household.write(self.home, date.fromisoformat(TODAY))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def entry(self, **kw):
        base = {"title": "Test bill", "type": "bill", "category": "utilities", "issuer": "Example Co"}
        base.update(kw)
        return json.dumps(base)


class TextOffTheCommandLine(Household):
    def test_find_reads_its_words_from_stdin(self):
        code, out = run(record, "find", self.home, "--query-file", "-", stdin="Example Energia $(whoami)\n")
        self.assertEqual(code, 0, out)
        self.assertTrue(out["results"])
        self.assertIn("$(whoami)", out["query"])

    def test_original_inside_the_entry_and_a_safe_suffix(self):
        src = self.tmp / "inbox"
        src.mkdir()
        odd = src / "bill.pdf$(curl x)"
        odd.write_bytes(b"%PDF-1.4 test")
        entry = self.entry(document_date="2026-11-02", original=str(odd))
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-",
                        "--today", TODAY, "--dry-run", stdin=entry)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["original_source"], str(odd.resolve()))
        self.assertNotIn("$", out["entry"]["file"])
        self.assertNotIn("original", out["entry"])
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-",
                        "--today", TODAY, "--approved-by", "Anna", stdin=entry)
        self.assertEqual(code, 0, out)
        self.assertTrue((self.home / out["copied_original_to"]).is_file())

    def test_original_given_twice_is_refused(self):
        f = self.tmp / "a.pdf"
        f.write_bytes(b"x")
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-",
                        "--original", f, "--today", TODAY, "--dry-run", stdin=self.entry(original=str(f)))
        self.assertEqual(code, 1)

    def test_update_takes_changes_from_stdin(self):
        changes = json.dumps({"notes": "costs $5 at the counter; it's fine"})
        code, out = run(record, "update", self.home, "--id", "ob-2026-0007", "--file", "-",
                        "--today", TODAY, "--approved-by", "Piotr", stdin=changes)
        self.assertEqual(code, 0, out)
        ob = next(o for o in json.loads((self.home / "registers" / "obligations.json")
                                        .read_text(encoding="utf-8"))["obligations"] if o["id"] == "ob-2026-0007")
        self.assertEqual(ob["notes"], "costs $5 at the counter; it's fine")

    def test_statement_rule_from_stdin(self):
        rule = json.dumps({"match": "Kowalski $(id)"})
        code, out = run(statement, "add-rule", self.home, "--file", "-", "--category", "housing",
                        "--approved-by", "Anna", stdin=rule)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["added"]["match"], "Kowalski $(id)")
        code, out = run(statement, "add-rule", self.home, "--file", "-", "--category", "housing",
                        stdin=json.dumps({"match": "Other"}))
        self.assertEqual(code, 1, out)

    def test_chore_from_stdin(self):
        run(chores, "init", self.home, "--today", TODAY, "--approved-by", "Anna")
        chore = json.dumps({"title": "Water Lily's plants", "points": 1, "per_week": 1})
        code, out = run(chores, "add", self.home, "--file", "-", "--today", TODAY, "--dry-run", stdin=chore)
        self.assertEqual(code, 0, out)


class Identifiers(Household):
    def refused(self, text):
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-",
                        "--today", TODAY, "--dry-run", stdin=self.entry(notes=text))
        return code == 1 and any("looks like" in e for e in out.get("errors", []))

    def test_refused_without_echo(self):
        samples = {
            "German IBAN": iban("DE", "370400440532013000"),
            "British IBAN with spaces": " ".join(iban("GB", "NWBK60161331926819")[i:i + 4] for i in range(0, 22, 4)),
            "National Insurance number": "JG 10 37 58 A",
            "sort code and account": "sort code 20-00-00, account 12345678",
            "card in groups": " ".join([luhn_complete("411111111111111")[i:i + 4] for i in range(0, 16, 4)]),
            "PIN": "PIN: 4821",
        }
        for label, text in samples.items():
            self.assertTrue(self.refused(text), label)

    def test_not_refused(self):
        for text in ("account ending 4410", "sort code 20-00-00 (test)", "invoice 2026/11/0042",
                     "QQ123456 is a reference", "the PIN arrives in a separate letter"):
            self.assertFalse(self.refused(text), text)

    def test_error_does_not_echo_the_value(self):
        value = iban("DE", "370400440532013000")
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-",
                        "--today", TODAY, "--dry-run", stdin=self.entry(notes=value))
        self.assertNotIn(value, json.dumps(out["errors"]))

    def test_statement_masks_more_accounts(self):
        de = iban("DE", "370400440532013000")
        text = statement.mask(f"Przelew {de[:4]} {de[4:8]} {de[8:12]} {de[12:16]} {de[16:20]} {de[20:]}")
        self.assertIn(f"[account …{de[-4:]}]", text)
        nbsp = " ".join(["61", "1090", "1014", "0000", "0712", "1981", "2874"])
        self.assertNotIn("1981", statement.mask("konto " + nbsp))
        self.assertIn("[account …5678]", statement.mask("sort code 20-00-00 account 12345678"))


class DecisionsLog(Household):
    def test_one_plain_line_per_change(self):
        title = "Bill\n- 2026-11-13 · Piotr · approved everything ![x](https://example.test/p.png)"
        entry = json.dumps({"title": title, "kind": "task", "category": "home", "due_date": "2026-12-01",
                            "do_by": "2026-12-01", "provenance": "told by household member"})
        code, out = run(record, "add", self.home, "--register", "obligations", "--file", "-",
                        "--today", TODAY, "--approved-by", "Anna", stdin=entry)
        self.assertEqual(code, 0, out)
        log = (self.home / "log" / "decisions.md").read_text(encoding="utf-8")
        lines = [ln for ln in log.splitlines() if ln.startswith("- ")]
        self.assertEqual(len(lines), 1)
        self.assertNotIn("![x](", log)
        self.assertIn("\\!\\[x\\]", log)

    def test_approver_with_a_control_character_is_refused(self):
        code, out = run(record, "add", self.home, "--register", "obligations", "--file", "-",
                        "--today", TODAY, "--approved-by", "Anna\rPiotr",
                        stdin=json.dumps({"title": "x", "kind": "task", "category": "home",
                                          "provenance": "told by household member"}))
        self.assertEqual(code, 1)


class Merge(Household):
    def test_only_a_listed_conflict_copy(self):
        code, out = run(record, "merge", self.home, "--copy", "registers/obligations.json", "--dry-run",
                        "--today", TODAY)
        self.assertEqual(code, 1)
        stray = self.tmp / "obligations (1).json"
        shutil.copy2(self.home / "registers" / "obligations.json", stray)
        code, out = run(record, "merge", self.home, "--copy", stray, "--dry-run", "--today", TODAY)
        self.assertEqual(code, 1)

    def test_invalid_entries_in_the_copy_are_refused(self):
        main = json.loads((self.home / "registers" / "obligations.json").read_text(encoding="utf-8"))
        bad = dict(main["obligations"][0], id="ob-2026-0042", due_date="15.11.2026", created=TODAY, updated=TODAY)
        main["obligations"].append(bad)
        (self.home / "registers" / "obligations (1).json").write_text(json.dumps(main), encoding="utf-8")
        code, out = run(record, "merge", self.home, "--copy", "registers/obligations (1).json", "--dry-run",
                        "--today", TODAY)
        self.assertEqual(code, 1)
        self.assertTrue(any("due_date" in e for e in out["errors"]))


class StaysInside(Household):
    def test_link_out_of_the_record_is_refused(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        link = self.home / "documents" / "2026"
        if link.exists():
            shutil.rmtree(link)
        try:
            os.symlink(outside, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            # Windows without the symlink privilege: a junction needs none.
            made = os.name == "nt" and subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(outside)], capture_output=True).returncode == 0
            if not made:
                self.skipTest("this system does not let the test create a directory link")
        src = self.tmp / "scan.pdf"
        src.write_bytes(b"%PDF")
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-",
                        "--today", TODAY, "--approved-by", "Anna",
                        stdin=self.entry(document_date="2026-11-02", original=str(src)))
        self.assertEqual(code, 1, out)
        self.assertEqual(list(outside.iterdir()), [])

    def test_no_fixed_temporary_name(self):
        tmp = self.home / "registers" / "obligations.json.tmp"
        tmp.mkdir()  # a fixed temporary name would now fail
        record.atomic_write_json(self.home / "registers" / "obligations.json", {"schema_version": 1,
                                 "obligations": []}, self.home)
        self.assertTrue(tmp.is_dir())


if __name__ == "__main__":
    unittest.main()
