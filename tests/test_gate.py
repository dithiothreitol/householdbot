"""The write gate: a preview stores the change under a token, commit applies exactly it.

Also the files the skills keep (record.py save) and the calendar export (record.py export --ics).
"""
import io
import json
import shutil
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "scripts"))
sys.path.insert(0, str(ROOT / "evals" / "fixtures"))
import chores  # noqa: E402
import record  # noqa: E402
import make_household  # noqa: E402

TODAY = "2026-11-14"
ENTRY = {"title": "Test bill", "kind": "payment", "category": "utilities", "due_date": "2026-11-20",
         "amount": "10.00", "currency": "PLN", "provenance": "stated in document"}


def fake_iban() -> str:
    """A Polish IBAN with valid check digits, made at run time so no number sits in the repository."""
    bban = "1090" + "1014" + "0" * 16
    digits = "".join(str(int(c, 36)) for c in bban + "PL00")
    return f"PL{98 - int(digits) % 97:02d}{bban}"


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


class GateCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hb-gate-"))
        self.home = self.tmp / "household"
        make_household.write(self.home, date.fromisoformat(TODAY))
        self._config = record.CONFIG_DIR
        record.CONFIG_DIR = self.tmp / "config"

    def tearDown(self):
        record.CONFIG_DIR = self._config
        shutil.rmtree(self.tmp, ignore_errors=True)

    def reg(self, name="obligations") -> Path:
        return self.home / "registers" / f"{name}.json"

    def preview(self, entry=None, **kw):
        code, out = run(record, "add", self.home, "--register", "obligations", "--file", "-",
                        "--country", "PL", "--today", TODAY, stdin=json.dumps(entry or ENTRY))
        self.assertEqual(code, 0, out)
        return out

    def commit(self, token, who="Anna"):
        return run(record, "commit", self.home, "--confirm", token, "--approved-by", who, "--today", TODAY)


class TwoPhases(GateCase):
    def test_preview_writes_nothing_and_commit_writes_the_preview_byte_for_byte(self):
        before = self.reg().read_bytes()
        out = self.preview()
        self.assertEqual(before, self.reg().read_bytes())
        pending = json.loads((self.home / record.PENDING / f"{out['confirm']}.json").read_text(encoding="utf-8"))
        stored = next(op["text"] for op in pending["ops"] if op["path"] == "registers/obligations.json")
        code, done = self.commit(out["confirm"])
        self.assertEqual(code, 0, done)
        self.assertEqual(self.reg().read_bytes(), stored.encode("utf-8"))
        self.assertEqual(done["approved_by"], "Anna")
        self.assertTrue((self.home / done["backups"][0]).is_file())
        log = (self.home / "log" / "decisions.md").read_text(encoding="utf-8").splitlines()
        self.assertTrue(log[-1].startswith("- 2026-11-14 · zgoda: Anna · dodano ob-2026-0010"))
        self.assertFalse((self.home / record.PENDING / f"{out['confirm']}.json").exists())

    def test_replayed_and_unknown_tokens_are_refused(self):
        out = self.preview()
        self.assertEqual(self.commit(out["confirm"])[0], 0)
        after = self.reg().read_bytes()
        code, again = self.commit(out["confirm"])
        self.assertEqual(code, 1)
        self.assertIn("unknown confirm token", again["errors"][0])
        code, bad = self.commit("0" * 16)
        self.assertEqual(code, 1)
        code, bad = self.commit("not-a-token")
        self.assertIn("16-character", bad["errors"][0])
        self.assertEqual(after, self.reg().read_bytes())

    def test_an_expired_token_is_refused(self):
        out = self.preview()
        later = time.time() + record.PENDING_TTL_SECONDS + 60
        with mock.patch.object(record.time, "time", return_value=later):
            code, res = self.commit(out["confirm"])
        self.assertEqual(code, 1)
        self.assertIn("expired", res["errors"][0])
        self.assertFalse((self.home / record.PENDING / f"{out['confirm']}.json").exists())

    def test_a_register_changed_after_the_preview_is_not_overwritten(self):
        first, second = self.preview(), self.preview(dict(ENTRY, title="Another bill"))
        self.assertEqual(self.commit(first["confirm"])[0], 0)
        after_first = self.reg().read_bytes()
        code, res = self.commit(second["confirm"])
        self.assertEqual(code, 1)
        self.assertIn("changed since the preview", res["errors"][0])
        self.assertEqual(after_first, self.reg().read_bytes())

    def test_an_edited_preview_is_refused(self):
        out = self.preview()
        path = self.home / record.PENDING / f"{out['confirm']}.json"
        body = json.loads(path.read_text(encoding="utf-8"))
        body["ops"][0]["text"] = body["ops"][0]["text"].replace("Test bill", "Something else")
        path.write_text(json.dumps(body), encoding="utf-8")
        code, res = self.commit(out["confirm"])
        self.assertEqual(code, 1)
        self.assertIn("does not match its token", res["errors"][0])

    def test_the_approver_is_checked_at_commit_and_the_preview_waits(self):
        out = self.preview()
        code, res = self.commit(out["confirm"], who="Anna: tak, zapisz")
        self.assertEqual(code, 1)
        self.assertIn("name only", res["errors"][0])
        self.assertEqual(self.commit(out["confirm"], who="Anna")[0], 0)

    def test_the_one_call_form_is_refused_everywhere(self):
        for module, argv in ((record, ["add", self.home, "--register", "obligations", "--json", json.dumps(ENTRY)]),
                             (record, ["save", self.home, "--to", "briefs/x.md", "--file", "-"]),
                             (chores, ["init", self.home])):
            code, out = run(module, *argv, "--approved-by", "Anna", stdin="text")
            self.assertEqual(code, 1, (module.__name__, out))
            self.assertIn("two steps", out["errors"][0])

    def test_a_refused_entry_leaves_no_pending_change(self):
        iban = fake_iban()
        code, out = run(record, "add", self.home, "--register", "obligations", "--file", "-", "--today", TODAY,
                        stdin=json.dumps(dict(ENTRY, notes=f"pay to {iban}")))
        self.assertEqual(code, 1)
        pending = self.home / record.PENDING
        self.assertFalse(pending.exists() and any(pending.iterdir()))

    def test_a_document_original_is_copied_at_commit_only(self):
        scan = self.tmp / "scan.pdf"
        scan.write_bytes(b"%PDF-1.4 synthetic")
        entry = {"title": "Rachunek", "type": "bill", "category": "utilities", "document_date": "2026-11-10",
                 "issuer": "Example Energia S.A.", "original": str(scan)}
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-", "--today", TODAY,
                        stdin=json.dumps(entry))
        self.assertEqual(code, 0, out)
        target = self.home / out["original_to"]
        self.assertFalse(target.exists())
        self.assertEqual(self.commit(out["confirm"])[0], 0)
        self.assertEqual(target.read_bytes(), scan.read_bytes())

    def test_a_changed_original_is_refused(self):
        scan = self.tmp / "scan.pdf"
        scan.write_bytes(b"%PDF-1.4 synthetic")
        entry = {"title": "Rachunek", "type": "bill", "category": "utilities", "original": str(scan)}
        code, out = run(record, "add", self.home, "--register", "documents", "--file", "-", "--today", TODAY,
                        stdin=json.dumps(entry))
        scan.write_bytes(b"%PDF-1.4 something else")
        code, res = self.commit(out["confirm"])
        self.assertEqual(code, 1)
        self.assertIn("scan.pdf", res["errors"][0])

    def test_init_with_the_profile_is_one_change(self):
        fresh = self.tmp / "new"
        profile = (self.home / record.PROFILE).read_text(encoding="utf-8")
        code, out = run(record, "init", fresh, "--lang", "pl", "--profile-file", "-", "--today", TODAY, stdin=profile)
        self.assertEqual(code, 0, out)
        self.assertFalse(fresh.exists())
        self.assertTrue((record.CONFIG_DIR / "pending" / f"{out['confirm']}.json").exists())
        code, done = run(record, "commit", fresh, "--confirm", out["confirm"], "--approved-by", "Anna",
                         "--today", TODAY)
        self.assertEqual(code, 0, done)
        self.assertEqual((fresh / record.PROFILE).read_text(encoding="utf-8"), profile)
        self.assertTrue((fresh / "registers" / "obligations.json").is_file())
        self.assertIn("zgoda: Anna · utworzono rekord", (fresh / "log" / "decisions.md").read_text(encoding="utf-8"))

    def test_several_entries_of_one_register_are_one_change(self):
        batch = [ENTRY, dict(ENTRY, title="Second bill", due_date="2026-11-27")]
        code, out = run(record, "add", self.home, "--register", "obligations", "--file", "-", "--country", "PL",
                        "--today", TODAY, stdin=json.dumps(batch))
        self.assertEqual(code, 0, out)
        self.assertEqual([e["id"] for e in out["entries"]], ["ob-2026-0010", "ob-2026-0011"])
        self.assertEqual(len(out["preview"]), 2)
        code, done = self.commit(out["confirm"])
        self.assertEqual(code, 0, done)
        ids = {o["id"] for o in json.loads(self.reg().read_text(encoding="utf-8"))["obligations"]}
        self.assertTrue({"ob-2026-0010", "ob-2026-0011"} <= ids)
        log = (self.home / "log" / "decisions.md").read_text(encoding="utf-8")
        self.assertEqual(log.count("zgoda: Anna · dodano ob-2026-001"), 2)

    def test_a_bad_entry_in_a_batch_stops_the_whole_batch(self):
        batch = [ENTRY, {"title": "no kind"}]
        code, out = run(record, "add", self.home, "--register", "obligations", "--file", "-", "--today", TODAY,
                        stdin=json.dumps(batch))
        self.assertEqual(code, 1)
        self.assertTrue(any(e.startswith("ob-2026-0011:") for e in out["errors"]))
        self.assertNotIn("confirm", out)

    def test_several_bills_paid_in_one_change(self):
        code, out = run(record, "complete", self.home, "--id", "ob-2026-0001", "--id", "ob-2026-0006",
                        "--country", "PL", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertEqual([c["id"] for c in out["completed"]], ["ob-2026-0001", "ob-2026-0006"])
        self.assertEqual(self.commit(out["confirm"])[0], 0)
        obs = {o["id"]: o for o in json.loads(self.reg().read_text(encoding="utf-8"))["obligations"]}
        self.assertEqual(obs["ob-2026-0001"]["status"], "done")
        self.assertEqual(obs["ob-2026-0006"]["status"], "done")
        self.assertEqual(sum(1 for o in obs.values() if o.get("series") == "electricity-bill"
                             and o["status"] == "open"), 1)

    def test_chores_plan_keeps_the_approver_from_commit(self):
        code, out = run(chores, "init", self.home, "--today", TODAY)
        self.assertEqual(run(chores, "commit", self.home, "--confirm", out["confirm"], "--approved-by", "Anna")[0], 0)
        code, out = run(chores, "add", self.home, "--json", json.dumps({"title": "Dishes", "per_week": 3}),
                        "--today", TODAY)
        self.assertEqual(run(chores, "commit", self.home, "--confirm", out["confirm"], "--approved-by", "Anna")[0], 0)
        code, out = run(chores, "save-plan", self.home, "--from", "2026-11-16", "--today", TODAY)
        self.assertEqual(code, 0, out)
        self.assertEqual(run(chores, "commit", self.home, "--confirm", out["confirm"], "--approved-by", "Piotr")[0], 0)
        data = json.loads(self.reg("chores").read_text(encoding="utf-8"))
        self.assertEqual(data["plans"][-1]["approved_by"], "Piotr")
        self.assertNotIn("\u2063", self.reg("chores").read_text(encoding="utf-8"))


class SaveFiles(GateCase):
    def save(self, to, text, *extra):
        return run(record, "save", self.home, "--to", to, "--file", "-", "--today", TODAY, *extra, stdin=text)

    def test_a_brief_is_saved_after_commit_and_a_taken_name_gets_a_number(self):
        code, out = self.save("briefs/2026-W46.md", "# Przegląd\n")
        self.assertEqual(code, 0, out)
        self.assertFalse((self.home / "briefs" / "2026-W46.md").exists())
        self.assertEqual(run(record, "commit", self.home, "--confirm", out["confirm"], "--approved-by", "Anna")[0], 0)
        self.assertEqual((self.home / "briefs" / "2026-W46.md").read_text(encoding="utf-8"), "# Przegląd\n")
        code, out = self.save("briefs/2026-W46.md", "# Drugi\n")
        self.assertEqual(out["file"], "briefs/2026-W46-2.md")
        log = (self.home / "log" / "decisions.md").read_text(encoding="utf-8")
        self.assertIn("zgoda: Anna · zapisano briefs/2026-W46.md", log)

    def test_replace_keeps_a_copy_and_shows_the_difference(self):
        (self.home / "lists").mkdir(exist_ok=True)
        (self.home / "lists" / "shopping.md").write_text("- mleko\n", encoding="utf-8")
        code, out = self.save("lists/shopping.md", "- mleko\n- chleb\n", "--replace")
        self.assertEqual(code, 0, out)
        self.assertIn("+- chleb", out["diff"])
        code, done = run(record, "commit", self.home, "--confirm", out["confirm"], "--approved-by", "Piotr")
        self.assertEqual(code, 0, done)
        self.assertTrue(done["backups"][0].startswith("registers/.history/shopping-"))

    def test_paths_outside_the_allowed_folders_are_refused(self):
        for to in ("../outside.md", "registers/obligations.json", "briefs/../x.md", "notes.md",
                   "briefs/.hidden.md", "briefs/run.sh", "C:/x/briefs/a.md"):
            code, out = self.save(to, "x")
            self.assertEqual(code, 1, to)

    def test_a_page_with_a_script_or_a_link_is_refused(self):
        for bad in ("<script>alert(1)</script>", '<a href="https://example.com">x</a>', "<img src=x>",
                    '<p onclick="x()">', "<style>@import 'x.css';</style>"):
            code, out = self.save("reviews/dashboard-2026-11-14.html", f"<!doctype html><p>{bad}</p>")
            self.assertEqual(code, 1, bad)
        code, out = self.save("reviews/dashboard-2026-11-14.html", "<!doctype html><p>Stan na sobotę</p>")
        self.assertEqual(code, 0, out)

    def test_an_identifier_in_a_file_is_refused(self):
        code, out = self.save("briefs/x.md", f"Konto: {fake_iban()}\n")
        self.assertEqual(code, 1)
        self.assertFalse((self.home / record.PENDING).exists() and any((self.home / record.PENDING).iterdir()))


class IcsExport(GateCase):
    def export(self, *extra):
        code, out = run(record, "export", self.home, "--ics", "--country", "PL", "--today", TODAY, *extra)
        self.assertEqual(code, 0, out)
        code, done = run(record, "commit", self.home, "--confirm", out["confirm"], "--approved-by", "Anna")
        self.assertEqual(code, 0, done)
        return out, (self.home / out["file"]).read_bytes().decode("utf-8")

    def test_rfc_5545_shape(self):
        out, text = self.export()
        self.assertTrue(text.startswith("BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"))
        self.assertTrue(text.endswith("END:VCALENDAR\r\n"))
        self.assertNotIn("\n", text.replace("\r\n", ""))
        for line in text.split("\r\n"):
            self.assertLessEqual(len(line.encode("utf-8")), 75, line)
        self.assertEqual(text.count("BEGIN:VEVENT"), out["events"] + out["cancelled"])
        self.assertIn("DTSTART;VALUE=DATE:20261118", text)

    def test_folding_and_escaping(self):
        line = "SUMMARY:" + record.ics_escape("Zażółć gęślą jaźń; przecinek, " * 4)
        folded = record.ics_fold(line)
        self.assertTrue(all(len(part.encode("utf-8")) <= 75 for part in folded))
        self.assertTrue(all(part.startswith(" ") for part in folded[1:]))
        self.assertEqual("".join(p[1:] if i else p for i, p in enumerate(folded)), line)
        self.assertIn("\\;", line)
        self.assertIn("\\,", line)

    def test_uids_are_stable_between_exports(self):
        _, first = self.export()
        _, second = self.export()
        uid = [ln for ln in first.split("\r\n") if ln.startswith("UID:")]
        self.assertEqual(uid, [ln for ln in second.split("\r\n") if ln.startswith("UID:")])
        self.assertEqual(len(uid), len(set(uid)))

    def test_health_titles_are_neutral_and_closed_entries_are_cancelled(self):
        obs = json.loads(self.reg().read_text(encoding="utf-8"))
        obs["obligations"].append({**record.DEFAULTS["obligations"], "id": "ob-2026-0050",
                                   "title": "Appointment, Zosia", "kind": "appointment", "category": "health",
                                   "owner": "Zosia", "due_date": "2026-12-04", "do_by": "2026-12-04",
                                   "provenance": "told by household member", "created": TODAY, "updated": TODAY})
        self.reg().write_text(json.dumps(obs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        out, text = self.export()
        self.assertIn("SUMMARY:Wizyta\\, Zosia", text)
        self.assertEqual(out["cancelled"], 1)          # last month's electricity bill, done
        self.assertIn("STATUS:CANCELLED", text)

    def test_a_member_export_holds_only_their_entries(self):
        out, text = self.export("--member", "Piotr")
        self.assertEqual(out["file"], "exports/householdbot-piotr.ics")
        self.assertNotIn("Example Energia", text)


if __name__ == "__main__":
    unittest.main()
