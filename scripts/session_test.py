#!/usr/bin/env python3
"""Session tests: multi-turn conversations with the plugin and its scripts, checked
by the state of the household folder and by patterns, without an LLM judge.

Each session in evals/sessions/<name>.json seeds a synthetic household in a
temporary folder, may prepare it further with the plugin's own scripts, then
sends its turns through a host's command line in that folder. After every turn
the checks look at the reply and at the folder: registers unchanged, an entry
with given fields, the number of new log lines, a file present or absent, text
that must not appear anywhere. The host is an adapter: `claude` runs
`claude -p --plugin-dir householdbot --resume`; Stage 6 adds others.

Runs cost money (one model session per run). `--check` costs nothing: it
validates every session file, seeds every household, runs the preparations
and the date computations, and prints what each session would send.

    python scripts/session_test.py --check
    python scripts/session_test.py --session "gate-*" --runs 2 --max-cost-usd 10
    python scripts/session_test.py --list

Placeholders: <<name>> in a turn, a file or a check stands for a value worked
out at run time (a date relative to today, a deadline from the country pack),
so the sessions do not age. In a pattern the value is escaped.
Standard library only. Reports go to evals/results/sessions/<time>/.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "householdbot"
SESSIONS = REPO / "evals" / "sessions"
FIXTURES = REPO / "evals" / "fixtures"
SCRIPTS = REPO / "core" / "scripts"
RESULTS = REPO / "evals" / "results" / "sessions"
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True
import dates  # noqa: E402

GROUPS = ("gate", "safety", "dates", "language")
SEED_MODES = {
    "full": ["make_household.py", "."],
    "full-en": ["make_household.py", ".", "--lang", "en"],
    "gb": ["make_household_gb.py", "."],
    "everyday": ["make_everyday.py", "."],
    "conflict": ["make_household.py", ".", "--conflict"],
    "statement": ["make_statement.py", "inbox/wyciag.csv", "--format", "a"],
    "statement-en": ["make_statement.py", "inbox/statement.csv", "--format", "c"],
}
CHECK_KEYS = {"reply_matches", "reply_not_matches", "unchanged", "record_unchanged", "log_lines_added",
              "entry", "no_entry", "files_exist", "files_absent", "file_matches", "file_not_matches",
              "nothing_matches", "glob_exists"}
PL_MONTHS = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września",
             "października", "listopada", "grudnia"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
             "October", "November", "December"]


class SessionError(Exception):
    """A session file that cannot run as written."""


# --------------------------------------------------------------------------
# Values worked out at run time
# --------------------------------------------------------------------------

def date_vars(name: str, d: date) -> dict:
    pl, en = dates.load_lang("pl"), dates.load_lang("en")
    return {name: d.isoformat(), f"{name}_pl": f"{d.day} {PL_MONTHS[d.month - 1]} {d.year}",
            f"{name}_en": f"{d.day} {EN_MONTHS[d.month - 1]} {d.year}", f"{name}_local_pl": pl.date(d),
            f"{name}_local_en": en.date(d), f"{name}_dm": f"{d.day:02d}.{d.month:02d}",
            f"{name}_weekday_pl": pl.weekday_long(d), f"{name}_d_mon_en": f"{d.day} {EN_MONTHS[d.month - 1][:3]}"}


def resolve_date(spec, today: date, known: dict) -> date:
    """An offset in days ("-2", 14), "next MM-DD" (that day this year or next), or a known name."""
    if isinstance(spec, int) or re.fullmatch(r"[+-]?\d+", str(spec)):
        return today + timedelta(days=int(spec))
    m = re.fullmatch(r"next (mon|tue|wed|thu|fri|sat|sun)", str(spec))
    if m:
        target = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"].index(m.group(1))
        return today + timedelta(days=(target - today.weekday() - 1) % 7 + 1)
    m = re.fullmatch(r"next (\d{2})-(\d{2})", str(spec))
    if m:
        d = date(today.year, int(m.group(1)), int(m.group(2)))
        return d if d >= today else date(today.year + 1, d.month, d.day)
    if spec in known:
        return date.fromisoformat(known[spec])
    raise SessionError(f"cannot read the date {spec!r}")


def fake_identifiers() -> dict:
    """A PESEL and an IBAN with valid checksums, made at run time: the repository never holds one."""
    body = "8" + "0" * 5 + "4321"
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    pesel = body + str((10 - sum(int(a) * b for a, b in zip(body, weights)) % 10) % 10)
    bban = "1090" + "1014" + "0" * 12 + "4321"
    check = 98 - int("".join(str(int(c, 36)) for c in bban + "PL00")) % 97
    iban = f"PL{check:02d}{bban}"
    spaced = iban[:4] + " " + " ".join(iban[i:i + 4] for i in range(4, len(iban), 4))
    return {"fake_pesel": pesel, "fake_iban": iban, "fake_iban_spaced": spaced,
            "fake_iban_digits": iban[2:]}


def compute_vars(session: dict, today: date) -> dict:
    values = date_vars("today", today)
    values.update(fake_identifiers())
    for name, spec in (session.get("dates") or {}).items():
        values.update(date_vars(name, resolve_date(spec, today, values)))
    for name, spec in (session.get("windows") or {}).items():
        pack = dates.load_pack(spec.get("country", "PL"))
        lang = dates.load_lang(spec.get("lang", "pl"))
        start = resolve_date(spec["from"], today, values)
        res = dates.window_result(pack, lang, pack.entry("response_windows", spec["window"]), start)
        values.update(date_vars(f"{name}_due", date.fromisoformat(res["due_date"])))
        values.update(date_vars(f"{name}_do_by", date.fromisoformat(res["do_by"])))
        values[f"{name}_law"] = res.get("law") or ""
    return values


def fill(text: str, values: dict, pattern: bool = False) -> str:
    def sub(m):
        key = m.group(1)
        if key not in values:
            raise SessionError(f"unknown placeholder <<{key}>>")
        return re.escape(values[key]) if pattern else values[key]
    return re.sub(r"<<([a-z0-9_]+)>>", sub, text)


# --------------------------------------------------------------------------
# The household folder
# --------------------------------------------------------------------------

def run_fixture(args: list[str], cwd: Path, today: date) -> None:
    cmd = [sys.executable, str(FIXTURES / args[0]), *args[1:]]
    if args[0] != "make_everyday.py" and args[0] != "make_statement.py":
        cmd += ["--today", today.isoformat()]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env)
    if done.returncode:
        raise SessionError(f"seeding {' '.join(args)} failed: {done.stderr.strip()[:300]}")


def call_script(script: str, argv: list[str], cwd: Path, stdin: str | None = None) -> dict:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    done = subprocess.run([sys.executable, str(SCRIPTS / script), *argv], cwd=cwd, input=stdin,
                          capture_output=True, text=True, encoding="utf-8", env=env)
    try:
        return json.loads(done.stdout)
    except ValueError:
        raise SessionError(f"{script} {' '.join(argv)}: {done.stderr.strip()[:300]}")


def prepare(session: dict, home: Path, values: dict) -> None:
    """Writes made before the conversation, through the scripts' own two phases."""
    for step in session.get("prepare") or []:
        argv = [fill(str(a), values) for a in step["args"]]
        stdin = step.get("stdin")
        if stdin is not None and not isinstance(stdin, str):
            stdin = json.dumps(stdin, ensure_ascii=False)
        out = call_script(step.get("script", "record.py"), argv, home, fill(stdin, values) if stdin else None)
        if not out.get("confirm"):
            raise SessionError(f"prepare {argv[:2]} gave no preview: {out.get('errors')}")
        done = call_script(step.get("script", "record.py"),
                           ["commit", str(home), "--confirm", out["confirm"], "--approved-by",
                            step.get("approver", "Anna")], home)
        if not done.get("ok", True) or "committed" not in done:
            raise SessionError(f"prepare commit failed: {done.get('errors')}")


def seed(session: dict, folder: Path, today: date, values: dict) -> Path:
    home = folder / "household"
    home.mkdir(parents=True)
    for mode in session.get("household", ["full"]):
        if mode not in SEED_MODES:
            raise SessionError(f"unknown household mode {mode!r}")
        run_fixture(SEED_MODES[mode], home, today)
    for rel, text in (session.get("files") or {}).items():
        p = home / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(fill(text, values).encode("utf-8"))
    prepare(session, home, values)
    return home


def snapshot(home: Path) -> dict:
    files = {}
    for p in sorted(home.rglob("*")):
        if p.is_file() and ".pending" not in p.parts and ".history" not in p.parts:
            files[p.relative_to(home).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    log = home / "log" / "decisions.md"
    lines = [ln for ln in log.read_text(encoding="utf-8").splitlines() if ln.startswith("- ")] if log.exists() else []
    return {"files": files, "log_lines": len(lines)}


def entries(home: Path, register: str) -> list[dict]:
    p = home / "registers" / f"{register}.json"
    return json.loads(p.read_text(encoding="utf-8")).get(register, []) if p.exists() else []


def entry_matches(entry: dict, where: dict, values: dict) -> bool:
    for field, want in where.items():
        have = entry.get(field)
        if isinstance(want, str) and want.startswith("~"):
            if have is None or not re.search(fill(want[1:], values, pattern=True), str(have), re.I):
                return False
        elif have != (fill(want, values) if isinstance(want, str) else want):
            return False
    return True


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def check_turn(expect: dict, reply: str, before: dict, after: dict, home: Path, values: dict) -> list[str]:
    """Failures for one turn; an empty list means the turn passed."""
    fails = []
    for rx in expect.get("reply_matches", []):
        if not re.search(fill(rx, values, pattern=True), reply, re.I | re.S):
            fails.append(f"reply lacks /{rx}/")
    for rx in expect.get("reply_not_matches", []):
        m = re.search(fill(rx, values, pattern=True), reply, re.I | re.S)
        if m:
            fails.append(f"reply holds /{rx}/: {m.group(0)[:80]!r}")
    if expect.get("record_unchanged"):
        changed = sorted(k for k in set(before["files"]) | set(after["files"])
                         if (k.startswith("registers/") or k.startswith("log/") or k == "household-profile.md")
                         and before["files"].get(k) != after["files"].get(k))
        if changed:
            fails.append(f"record changed: {', '.join(changed)}")
    for rel in expect.get("unchanged", []):
        if before["files"].get(rel) != after["files"].get(rel):
            fails.append(f"{rel} changed")
    want = expect.get("log_lines_added")
    if want is not None:
        added = after["log_lines"] - before["log_lines"]
        lo, hi = (want, want) if isinstance(want, int) else (want.get("min", 0), want.get("max", 10 ** 6))
        if not lo <= added <= hi:
            fails.append(f"log lines added: {added}, expected {want}")
    for spec in ([expect["entry"]] if isinstance(expect.get("entry"), dict) else expect.get("entry", [])):
        if not any(entry_matches(e, spec["where"], values) for e in entries(home, spec["register"])):
            fails.append(f"no {spec['register']} entry with {spec['where']}")
    for spec in ([expect["no_entry"]] if isinstance(expect.get("no_entry"), dict) else expect.get("no_entry", [])):
        if any(entry_matches(e, spec["where"], values) for e in entries(home, spec["register"])):
            fails.append(f"a {spec['register']} entry with {spec['where']} exists")
    for rel in expect.get("files_exist", []):
        if not (home / fill(rel, values)).exists():
            fails.append(f"{rel} is missing")
    for rel in expect.get("files_absent", []):
        if (home / fill(rel, values)).exists() or (home.parent / fill(rel, values)).exists():
            fails.append(f"{rel} exists")
    for pattern in expect.get("glob_exists", []):
        if not list(home.glob(fill(pattern, values))):
            fails.append(f"no file matches {pattern}")
    for rel, rx in (expect.get("file_matches") or {}).items():
        found = list(home.glob(fill(rel, values)))
        if not found or not any(re.search(fill(rx, values, pattern=True), p.read_text(encoding="utf-8", errors="replace"), re.I)
                                for p in found):
            fails.append(f"{rel} lacks /{rx}/")
    for rel, rx in (expect.get("file_not_matches") or {}).items():
        for p in home.glob(fill(rel, values)):
            m = re.search(fill(rx, values, pattern=True), p.read_text(encoding="utf-8", errors="replace"), re.I)
            if m:
                fails.append(f"{p.relative_to(home).as_posix()} holds /{rx}/: {m.group(0)[:60]!r}")
    for rx in expect.get("nothing_matches", []):
        # Text that must appear nowhere: not in the reply, not in the registers, not in the log.
        compiled = re.compile(fill(rx, values, pattern=True), re.I)
        places = {"reply": reply}
        for p in list((home / "registers").glob("*.json")) + [home / "log" / "decisions.md"]:
            if p.exists():
                places[p.relative_to(home).as_posix()] = p.read_text(encoding="utf-8", errors="replace")
        for where, text in places.items():
            if compiled.search(text):
                fails.append(f"/{rx}/ found in {where}")
    return fails


# --------------------------------------------------------------------------
# Hosts
# --------------------------------------------------------------------------

class ClaudeHost:
    """claude -p with the plugin from this repository; the session continues with --resume."""
    name = "claude"
    tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Skill"]

    def __init__(self, model: str):
        self.exe = shutil.which("claude")
        if not self.exe:
            raise SessionError("claude is not on PATH")
        self.model = model

    def send(self, text: str, cwd: Path, session_id: str | None) -> tuple[str, str | None, float]:
        cmd = [self.exe, "-p", text, "--plugin-dir", str(PLUGIN), "--model", self.model,
               "--allowedTools", *self.tools, "--output-format", "json"]
        if session_id:
            cmd += ["--resume", session_id]
        # No person answers the write gate's prompt in a test run; the scripts still demand a token.
        env = dict(os.environ, HOUSEHOLDBOT_HOOK="off", PYTHONIOENCODING="utf-8")
        done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=env, timeout=1200)
        try:
            out = json.loads(done.stdout)
        except ValueError:
            raise SessionError(f"claude gave no JSON: {done.stderr.strip()[:300]}")
        return str(out.get("result") or ""), out.get("session_id"), float(out.get("total_cost_usd") or 0.0)


class ScriptedHost:
    """For the runner's own tests: canned replies, optional actions on the folder."""
    name = "scripted"

    def __init__(self, replies: list):
        self.replies = list(replies)

    def send(self, text: str, cwd: Path, session_id: str | None) -> tuple[str, str | None, float]:
        reply = self.replies.pop(0)
        if callable(reply):
            reply = reply(cwd)
        return reply, "scripted", 0.0


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------

def load_session(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    problems = []
    if data.get("group") not in GROUPS:
        problems.append(f"group must be one of {GROUPS}")
    if not data.get("turns"):
        problems.append("no turns")
    for i, turn in enumerate(data.get("turns", []), 1):
        if not turn.get("say"):
            problems.append(f"turn {i} says nothing")
        unknown = set(turn.get("expect", {})) - CHECK_KEYS
        if unknown:
            problems.append(f"turn {i}: unknown checks {sorted(unknown)}")
        if not turn.get("expect"):
            problems.append(f"turn {i} checks nothing")
    if problems:
        raise SessionError(f"{path.name}: " + "; ".join(problems))
    data.setdefault("name", path.stem)
    return data


def run_session(session: dict, host, today: date | None = None, keep: Path | None = None) -> dict:
    today = today or date.today()
    folder = Path(tempfile.mkdtemp(prefix="hb-session-"))
    result = {"name": session["name"], "group": session["group"], "turns": [], "cost_usd": 0.0}
    try:
        values = compute_vars(session, today)
        home = seed(session, folder, today, values)
        session_id = None
        for i, turn in enumerate(session["turns"], 1):
            before = snapshot(home)
            text = fill(turn["say"], values)
            started = time.time()
            reply, session_id, cost = host.send(text, home, session_id)
            after = snapshot(home)
            fails = check_turn(turn.get("expect", {}), reply, before, after, home, values)
            result["turns"].append({"turn": i, "say": text, "reply": reply, "fails": fails,
                                    "seconds": round(time.time() - started, 1)})
            result["cost_usd"] = cost
        result["passed"] = all(not t["fails"] for t in result["turns"])
    except SessionError as exc:
        result.update({"passed": False, "error": str(exc)})
    finally:
        if keep is not None:
            target = keep / session["name"]
            shutil.copytree(folder, target, dirs_exist_ok=True)
        shutil.rmtree(folder, ignore_errors=True)
    return result


def check_only(sessions: list[dict]) -> int:
    """No model: every file loads, every household seeds, every placeholder resolves."""
    bad = 0
    for s in sessions:
        folder = Path(tempfile.mkdtemp(prefix="hb-session-check-"))
        try:
            values = compute_vars(s, date.today())
            seed(s, folder, date.today(), values)
            for turn in s["turns"]:
                fill(turn["say"], values)
                for key, spec in turn["expect"].items():
                    text = json.dumps(spec, ensure_ascii=False)
                    for m in re.finditer(r"<<([a-z0-9_]+)>>", text):
                        if m.group(1) not in values:
                            raise SessionError(f"{key}: unknown placeholder <<{m.group(1)}>>")
                    for rx in (spec if isinstance(spec, list) else []):
                        if isinstance(rx, str) and key.startswith(("reply", "nothing")):
                            re.compile(fill(rx, values, pattern=True))
            print(f"ok    {s['group']:<9} {s['name']}: {len(s['turns'])} turns; first: {fill(s['turns'][0]['say'], values)[:90]}")
        except (SessionError, re.error, KeyError) as exc:
            bad += 1
            print(f"FAIL  {s.get('name')}: {exc}")
        finally:
            shutil.rmtree(folder, ignore_errors=True)
    print(f"{len(sessions) - bad} of {len(sessions)} sessions ready")
    return 1 if bad else 0


def write_report(results: list[dict], host: str, model: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = RESULTS / stamp
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_bytes(json.dumps({"host": host, "model": model, "results": results},
                                                  ensure_ascii=False, indent=2).encode("utf-8"))
    lines = [f"# Session tests {stamp}", "", f"Host: {host}, model: {model}", "",
             "| Group | Passed | Runs |", "|---|---|---|"]
    for g in GROUPS:
        runs = [r for r in results if r["group"] == g]
        if runs:
            lines.append(f"| {g} | {sum(r['passed'] for r in runs)} | {len(runs)} |")
    lines += ["", f"Cost: USD {sum(r['cost_usd'] for r in results):.2f}", ""]
    for r in results:
        lines.append(f"## {'PASS' if r['passed'] else 'FAIL'} {r['name']} ({r['group']}, USD {r['cost_usd']:.2f})")
        if r.get("error"):
            lines.append(f"- error: {r['error']}")
        for t in r["turns"]:
            for f in t["fails"]:
                lines.append(f"- turn {t['turn']}: {f}")
        lines.append("")
    (out / "report.md").write_bytes("\n".join(lines).encode("utf-8"))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", default="*", help="name glob, e.g. gate-*")
    ap.add_argument("--group", choices=GROUPS)
    ap.add_argument("--host", default="claude", choices=["claude"])
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--max-cost-usd", type=float, default=10.0, help="stop starting sessions above this total")
    ap.add_argument("--check", action="store_true", help="validate and seed every session; no model, no cost")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--keep", action="store_true", help="keep each household folder in the report")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    paths = sorted(p for p in SESSIONS.glob("*.json") if fnmatch.fnmatch(p.stem, args.session))
    sessions = [load_session(p) for p in paths]
    if args.group:
        sessions = [s for s in sessions if s["group"] == args.group]
    if args.list:
        for s in sessions:
            print(f"{s['group']:<9} {s['name']:<40} {len(s['turns'])} turns  {s.get('about', '')}")
        return 0
    if args.check:
        return check_only(sessions)
    host = ClaudeHost(args.model)
    results, spent = [], 0.0
    keep = (RESULTS / "households" / datetime.now().strftime("%Y%m%d-%H%M%S")) if args.keep else None
    for run in range(args.runs):
        for s in sessions:
            if spent >= args.max_cost_usd:
                print(f"stopped: USD {spent:.2f} reached the ceiling of {args.max_cost_usd}")
                break
            r = run_session(s, host, keep=keep)
            r["run"] = run + 1
            spent += r["cost_usd"]
            results.append(r)
            print(f"{'PASS' if r['passed'] else 'FAIL'}  {s['group']:<9} {s['name']} (run {run + 1}, USD {r['cost_usd']:.2f})")
    out = write_report(results, host.name, args.model)
    print(f"{sum(r['passed'] for r in results)} of {len(results)} passed; USD {spent:.2f}; report {out}")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
