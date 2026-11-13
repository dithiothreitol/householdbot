"""Unit tests for core/scripts/record.py on the synthetic household."""
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "scripts"))
sys.path.insert(0, str(ROOT / "householdbot" / "evals" / "fixtures"))
import record  # noqa: E402
import make_household  # noqa: E402
from datetime import date  # noqa: E402

TODAY = "2026-11-13"


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = record.main([str(a) for a in argv])
    return code, json.loads(buf.getvalue())


def fake_pesel() -> str:
    """A string with a valid PESEL checksum, generated so no number sits in the repo."""
    body = "9" + "0" * 5 + "1234"
    w = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    check = (10 - sum(int(a) * b for a, b in zip(body, w)) % 10) % 10
    return body + str(check)


class RecordTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hb-test-"))
        self.home = self.tmp / "household"
        make_household.write(self.home, date.fromisoformat(TODAY))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def obligations(self):
        return json.loads((self.home / "registers" / "obligations.json").read_text(encoding="utf-8"))["obligations"]

    def log_lines(self):
        return [ln for ln in (self.home / "log" / "decisions.md").read_text(encoding="utf-8").splitlines()
                if ln.startswith("- ")]


class Validate(RecordTestCase):
    def test_fixture_is_valid(self):
        code, out = run("validate", self.home)
        self.assertEqual(code, 0, out["errors"])
        self.assertEqual(out["stats"]["documents"], 5)
        self.assertEqual(out["stats"]["obligations"], 9)
        self.assertTrue(any("without any date" in w for w in out["warnings"]))

    def test_schema_errors_are_reported(self):
        path = self.home / "registers" / "obligations.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["obligations"][0]["due_date"] = "15.11.2026"
        data["obligations"][1]["kind"] = "bill"
        data["obligations"][2]["id"] = data["obligations"][3]["id"]
        path.write_text(json.dumps(data), encoding="utf-8")
        code, out = run("validate", self.home)
        self.assertEqual(code, 1)
        text = " ".join(out["errors"])
        self.assertIn("due_date", text)
        self.assertIn("kind", text)
        self.assertIn("duplicate id", text)

    def test_newer_schema_is_refused(self):
        path = self.home / "registers" / "documents.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["schema_version"] = 99
        path.write_text(json.dumps(data), encoding="utf-8")
        code, out = run("validate", self.home)
        self.assertIn("update the plugin", " ".join(out["errors"]))

    def test_identifier_is_flagged_without_echo(self):
        path = self.home / "registers" / "documents.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        pesel = fake_pesel()
        data["documents"][0]["notes"] = f"PESEL {pesel}"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, out = run("validate", self.home)
        joined = " ".join(out["warnings"])
        self.assertIn("looks like a PESEL", joined)
        self.assertNotIn(pesel, joined)


class Due(RecordTestCase):
    def test_bands_and_order(self):
        code, out = run("due", self.home, "--today", TODAY, "--country", "PL")
        self.assertEqual(code, 0)
        items = out["items"]
        self.assertEqual(items[0]["band"], "overdue")
        self.assertIn("Water", items[0]["title"])
        bands = {i["id"]: i["band"] for i in items}
        self.assertEqual(bands["ob-2026-0001"], "now")
        self.assertEqual(bands["ob-2026-0004"], "now")  # cancel-by today+10 minus 5 days post
        self.assertEqual(bands["ob-2026-0002"], "coming")
        passport = [i for i in items if i["id"] == "ob-2026-0005"][0]
        self.assertTrue(passport["start_now"])
        self.assertEqual(out["no_date"][0]["id"], "ob-2026-0008")
        self.assertNotIn("ob-2026-0009", bands)  # done
        dos = [i["do_by"] for i in items]
        self.assertEqual(dos, sorted(dos))

    def test_horizon(self):
        code, out = run("due", self.home, "--today", TODAY, "--horizon", "7")
        ids = {i["id"] for i in out["items"]}
        self.assertNotIn("ob-2026-0002", ids)
        self.assertIn("ob-2026-0005", ids)  # lead time keeps it in view


class Writes(RecordTestCase):
    ENTRY = {"title": "Boiler service", "kind": "task", "category": "home", "due_date": "2026-12-15",
             "provenance": "told by household member", "amount": 250, "currency": "PLN"}

    def entry_file(self, entry):
        p = self.tmp / "entry.json"
        p.write_text(json.dumps(entry), encoding="utf-8")
        return p

    def test_write_needs_approval(self):
        before = (self.home / "registers" / "obligations.json").read_text(encoding="utf-8")
        code, out = run("add", self.home, "--register", "obligations", "--file", self.entry_file(self.ENTRY))
        self.assertEqual(code, 1)
        self.assertIn("--approved-by", out["errors"][0])
        self.assertEqual(before, (self.home / "registers" / "obligations.json").read_text(encoding="utf-8"))

    def test_dry_run_writes_nothing(self):
        code, out = run("add", self.home, "--register", "obligations", "--file", self.entry_file(self.ENTRY),
                        "--dry-run", "--today", TODAY, "--country", "PL")
        self.assertEqual(code, 0)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["entry"]["id"], "ob-2026-0010")
        self.assertEqual(out["entry"]["amount"], "250.00")
        self.assertEqual(out["entry"]["do_by"], "2026-12-15")
        self.assertEqual(len(self.obligations()), 9)
        self.assertEqual(self.log_lines(), [])

    def test_add_writes_logs_and_backs_up(self):
        code, out = run("add", self.home, "--register", "obligations", "--file", self.entry_file(self.ENTRY),
                        "--approved-by", "Anna", "--today", TODAY, "--country", "PL")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.obligations()), 10)
        self.assertIn("approved by Anna", self.log_lines()[0])
        self.assertTrue((self.home / out["backup"]).exists())

    def test_merge_conflict_copy(self):
        main = self.home / "registers" / "obligations.json"
        copy = self.home / "registers" / "obligations (1).json"
        data = json.loads(main.read_text(encoding="utf-8"))
        data["obligations"][0]["amount"] = "290.00"          # edited later on the other device
        data["obligations"][0]["updated"] = "2026-11-14"
        data["obligations"].append(dict(data["obligations"][6], id="ob-2026-0010", title="Gutter cleaning",
                                        created="2026-11-14"))  # added on the other device
        data["obligations"].append(dict(data["obligations"][6], id="ob-2026-0009", title="Something else",
                                        created="2026-11-14"))  # same id as a different local entry
        copy.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, out = run("merge", self.home, "--copy", "registers/obligations (1).json", "--dry-run", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["added_from_copy"], ["ob-2026-0010"])
        self.assertEqual(out["replaced_by_newer_copy"], ["ob-2026-0001"])
        self.assertEqual(out["id_collisions"][0]["copy_entry_renumbered_to"], "ob-2026-0011")
        code, out = run("merge", self.home, "--copy", "registers/obligations (1).json",
                        "--approved-by", "Anna", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertFalse(copy.exists())
        obs = {o["id"]: o for o in self.obligations()}
        self.assertEqual(obs["ob-2026-0001"]["amount"], "290.00")
        self.assertEqual(obs["ob-2026-0011"]["title"], "Something else")
        code, out = run("validate", self.home)
        self.assertEqual(out["conflicts"], [])

    def test_merge_same_day_edits_need_a_decision(self):
        main = self.home / "registers" / "obligations.json"
        copy = self.home / "registers" / "obligations (1).json"
        data = json.loads(main.read_text(encoding="utf-8"))
        data["obligations"][0]["amount"] = "290.00"
        copy.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, out = run("merge", self.home, "--copy", "registers/obligations (1).json", "--dry-run")
        self.assertEqual(code, 1)
        self.assertEqual(out["unresolved"][0]["id"], "ob-2026-0001")
        code, out = run("merge", self.home, "--copy", "registers/obligations (1).json", "--dry-run",
                        "--resolve", "ob-2026-0001=copy")
        self.assertEqual(code, 0, out)

    def test_conflict_copy_blocks_writes(self):
        shutil.copy(self.home / "registers" / "obligations.json", self.home / "registers" / "obligations (1).json")
        code, out = run("add", self.home, "--register", "obligations", "--file", self.entry_file(self.ENTRY),
                        "--approved-by", "Anna", "--today", TODAY)
        self.assertEqual(code, 1)
        self.assertIn("sync-conflict", out["errors"][0])
        code, out = run("conflicts", self.home)
        self.assertEqual(out["conflicts"], ["registers/obligations (1).json"])

    def test_original_is_copied_and_duplicates_refused(self):
        scan = self.tmp / "scan.txt"
        scan.write_text("synthetic scan", encoding="utf-8")
        doc = {"title": "Example Bank: account agreement", "type": "contract", "category": "money",
               "issuer": "Example Bank", "document_date": "2026-11-02"}
        code, out = run("add", self.home, "--register", "documents", "--file", self.entry_file(doc),
                        "--original", scan, "--approved-by", "Piotr", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["entry"]["file"], "documents/2026/2026-11-02_example-bank_contract.txt")
        self.assertTrue((self.home / out["entry"]["file"]).exists())
        code, out = run("add", self.home, "--register", "documents", "--file", self.entry_file(doc),
                        "--original", scan, "--approved-by", "Piotr", "--today", TODAY)
        self.assertEqual(code, 1)
        self.assertIn("already filed", out["errors"][0])

    def test_update_touches_one_entry(self):
        code, out = run("update", self.home, "--id", "ob-2026-0007", "--set", "due_date=2026-12-12",
                        "--approved-by", "Piotr", "--today", TODAY, "--country", "PL")
        self.assertEqual(code, 0, out)
        obs = {o["id"]: o for o in self.obligations()}
        self.assertEqual(obs["ob-2026-0007"]["due_date"], "2026-12-12")
        self.assertEqual(obs["ob-2026-0007"]["do_by"], "2026-12-11")  # Saturday rolled back
        self.assertEqual(obs["ob-2026-0001"]["updated"], TODAY)

    def test_update_keeps_amount_as_text(self):
        code, out = run("update", self.home, "--id", "ob-2026-0001", "--set", "amount=290.10",
                        "--approved-by", "Anna", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertEqual({o["id"]: o for o in self.obligations()}["ob-2026-0001"]["amount"], "290.10")

    def test_complete_monthly_adds_next(self):
        code, out = run("complete", self.home, "--id", "ob-2026-0001", "--approved-by", "Anna",
                        "--today", TODAY, "--country", "PL")
        self.assertEqual(code, 0, out)
        nxt = out["next_occurrence"]
        self.assertEqual(nxt["id"], "ob-2026-0010")
        self.assertEqual(nxt["series"], "electricity-bill")
        self.assertEqual(nxt["due_date"], "2026-12-18")
        self.assertEqual(nxt["status"], "open")
        obs = {o["id"]: o for o in self.obligations()}
        self.assertEqual(obs["ob-2026-0001"]["status"], "done")
        self.assertEqual(len(self.log_lines()), 2)

    def test_complete_free_text_recurrence_warns(self):
        code, out = run("complete", self.home, "--id", "ob-2026-0003", "--approved-by", "Anna",
                        "--today", TODAY)
        self.assertEqual(code, 0)
        self.assertIsNone(out["next_occurrence"])
        self.assertIn("cannot be computed", out["warnings"][0])

    def test_archive_moves_closed_only(self):
        code, out = run("archive", self.home, "--before", "2026-11-01", "--approved-by", "Anna", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertEqual(out["count"], 1)
        self.assertNotIn("ob-2026-0009", {o["id"] for o in self.obligations()})
        self.assertTrue((self.home / "archive" / "obligations-2026.json").exists())
        code, out = run("validate", self.home)
        self.assertEqual(code, 0, out["errors"])

    def test_init_refuses_existing_record(self):
        code, out = run("init", self.home, "--approved-by", "Anna")
        self.assertEqual(code, 1)
        fresh = self.tmp / "fresh"
        code, out = run("init", fresh, "--approved-by", "Anna", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertTrue((fresh / "registers" / "documents.json").exists())
        self.assertTrue((fresh / "log" / "decisions.md").exists())

    def test_migrate_adds_schema_version(self):
        path = self.home / "registers" / "documents.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        del data["schema_version"]
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, out = run("migrate", self.home, "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("added schema_version 1", out["summary"])
        code, out = run("migrate", self.home, "--approved-by", "Anna", "--today", TODAY)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"], 1)


class Search(RecordTestCase):
    def test_polish_and_english_queries(self):
        code, out = run("find", self.home, "--query", "ubezpieczenia samochodu OC")
        self.assertEqual(out["results"][0]["id"], "doc-2026-0002")
        code, out = run("find", self.home, "--query", "where is the internet contract")
        self.assertEqual(out["results"][0]["id"], "doc-2026-0004")

    def test_by_id(self):
        code, out = run("find", self.home, "--query", "co jest w doc-2026-0003?")
        self.assertEqual(out["results"][0]["id"], "doc-2026-0003")

    def test_no_match_says_so(self):
        code, out = run("find", self.home, "--query", "akt notarialny")
        self.assertEqual(out["results"], [])
        self.assertIn("never have been filed", out["note"])

    def test_diff(self):
        a = self.home / "registers" / "obligations.json"
        b = self.tmp / "other.json"
        data = json.loads(a.read_text(encoding="utf-8"))
        data["obligations"][0]["amount"] = "999.00"
        data["obligations"].pop()
        b.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, out = run("diff", a, b)
        self.assertEqual(out["only_in_a"], ["ob-2026-0009"])
        self.assertEqual(out["differing"][0]["id"], "ob-2026-0001")


if __name__ == "__main__":
    unittest.main()
