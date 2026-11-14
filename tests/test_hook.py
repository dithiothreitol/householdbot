"""The PreToolUse hook that sends commits and direct writes to the host's permission prompt."""
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
sys.path.insert(0, str(ROOT / "householdbot" / "hooks"))
sys.dont_write_bytecode = True  # no __pycache__ inside the plugin folder
import gate  # noqa: E402
import make_household  # noqa: E402
import record  # noqa: E402

TODAY = "2026-11-14"


class Hook(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hb-hook-"))
        self.home = self.tmp / "household"
        make_household.write(self.home, date.fromisoformat(TODAY))
        entry = json.dumps({"title": "Test", "kind": "task", "category": "home", "due_date": "2026-11-20",
                            "provenance": "told by household member"})
        buf = io.StringIO()
        fake = io.TextIOWrapper(io.BytesIO(entry.encode("utf-8")), encoding="utf-8")
        with mock.patch.object(sys, "stdin", fake), redirect_stdout(buf):
            record.main(["add", str(self.home), "--register", "obligations", "--file", "-", "--today", TODAY])
        self.token = json.loads(buf.getvalue())["confirm"]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def bash(self, command):
        return {"tool_name": "Bash", "cwd": str(self.tmp), "tool_input": {"command": command}}

    def test_a_commit_shows_the_stored_preview(self):
        reason = gate.decide(self.bash(f'python3 "/p/shared/scripts/record.py" commit "{self.home}" '
                                       f"--confirm {self.token} --approved-by Anna"))
        self.assertIn("prosi o potwierdzenie", reason)
        self.assertIn("ob-2026-0010", reason)
        self.assertIn("registers/obligations.json", reason)

    def test_a_relative_root_and_chores_commit(self):
        reason = gate.decide(self.bash(f"py chores.py commit household --confirm {self.token} --approved-by Anna"))
        self.assertIn("ob-2026-0010", reason)

    def test_an_unknown_token_still_asks(self):
        reason = gate.decide(self.bash(f'python record.py commit "{self.home}" --confirm {"a" * 16} '
                                       "--approved-by Anna"))
        self.assertIn("nie wskazuje podglądu", reason)

    def test_other_commands_pass(self):
        for command in ("ls -la", f'python record.py due "{self.home}"', "git commit -m x",
                        f'python record.py add "{self.home}" --register obligations --file -'):
            self.assertIsNone(gate.decide(self.bash(command)), command)

    def test_a_direct_write_into_the_household_folder_asks(self):
        for path in (self.home / "briefs" / "x.md", self.home / "registers" / "obligations.json",
                     self.home / "registers" / ".pending" / f"{self.token}.json"):
            reason = gate.decide({"tool_name": "Write", "tool_input": {"file_path": str(path)}})
            self.assertIn("pomija podgląd", reason)
        self.assertIsNone(gate.decide({"tool_name": "Edit", "tool_input": {"file_path": str(self.tmp / "x.md")}}))
        self.assertIsNone(gate.decide({"tool_name": "Read", "tool_input": {"file_path": str(self.home / "x.md")}}))

    def test_the_output_is_an_ask_decision(self):
        payload = json.dumps(self.bash(f'python record.py commit "{self.home}" --confirm {self.token} '
                                       "--approved-by Anna"))
        out = io.StringIO()
        with mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(payload.encode("utf-8")))), \
                redirect_stdout(out):
            self.assertEqual(gate.main(), 0)
        decision = json.loads(out.getvalue())["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "ask")
        self.assertEqual(decision["hookEventName"], "PreToolUse")

    def test_off_for_test_runs(self):
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(self.home / "briefs" / "x.md")}})
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"HOUSEHOLDBOT_HOOK": "off"}), \
                mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(payload.encode("utf-8")))), \
                redirect_stdout(out):
            gate.main()
        self.assertEqual(out.getvalue(), "")

    @unittest.skipUnless(shutil.which("sh"), "needs sh")
    def test_the_shell_wrapper_runs_the_gate(self):
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(self.home / "briefs" / "x.md")}})
        run = subprocess.run(["sh", str(ROOT / "householdbot" / "hooks" / "gate.sh")], input=payload.encode("utf-8"),
                             capture_output=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout.decode("utf-8"))["hookSpecificOutput"]["permissionDecision"], "ask")
        quiet = subprocess.run(["sh", str(ROOT / "householdbot" / "hooks" / "gate.sh")],
                               input=b'{"tool_name": "Bash", "tool_input": {"command": "ls"}}',
                               capture_output=True, timeout=60)
        self.assertEqual(quiet.stdout, b"")


if __name__ == "__main__":
    unittest.main()
