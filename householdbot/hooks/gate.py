#!/usr/bin/env python3
"""HouseholdBot write gate for Claude Code and Cowork: a PreToolUse hook.

It sends two kinds of tool call to the host's own permission prompt, so that a
person answers and not the model:

- `commit --confirm TOKEN` of record.py, chores.py or statement.py. The prompt
  shows what the stored preview writes: its log lines and its files.
- A host write tool (Write, Edit, MultiEdit, NotebookEdit) aimed at a file in a
  household folder, which would skip the preview.

Every other call passes without output. Standard library only; the hook input
arrives as JSON on standard input. HOUSEHOLDBOT_HOOK=off in the host's
environment turns the prompt off for test runs with no person to answer
(`claude -p`); the scripts still refuse a write without a previewed token.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from pathlib import Path

COMMIT_RE = re.compile(r"(?:record|chores|statement)\.py['\"]?\s+commit\b")
TOKEN_RE = re.compile(r"--confirm(?:=|\s+)['\"]?([0-9a-f]{16})\b")
SCRIPT_RE = re.compile(r"(?:record|chores|statement)\.py$")
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
PROFILE = "household-profile.md"
CONFIG_PENDING = Path.home() / ".claude" / "plugins" / "config" / "householdbot" / "pending"
LANG_LINE = re.compile(r"^\s*-\s*\*\*(?:Language|Język)\s*:\*\*\s*(.+?)\s*$", re.I | re.M)
TEXT = {
    "en": {
        "commit": "HouseholdBot asks you to confirm this change to the household record",
        "files": "files",
        "unknown": "HouseholdBot: this commit names no preview the gate can show; confirm only if you "
                   "saw the change in the conversation",
        "direct": "HouseholdBot: {path} is in the household folder and this writes it without a preview "
                  "(record.py save shows the change first)",
    },
    "pl": {
        "commit": "HouseholdBot prosi o potwierdzenie tej zmiany w rekordzie gospodarstwa",
        "files": "pliki",
        "unknown": "HouseholdBot: ten zapis nie wskazuje podglądu, który bramka może pokazać; potwierdź "
                   "tylko wtedy, gdy zmiana była pokazana w rozmowie",
        "direct": "HouseholdBot: {path} leży w folderze gospodarstwa, a ten zapis pomija podgląd "
                  "(record.py save najpierw pokazuje zmianę)",
    },
}


def household_root(start: Path) -> Path | None:
    for p in [start] + list(start.parents):
        if (p / PROFILE).is_file() and (p / "registers").is_dir():
            return p
    return None


def household_lang(root: Path | None) -> str:
    try:
        m = LANG_LINE.search((root / PROFILE).read_text(encoding="utf-8")) if root else None
    except OSError:
        m = None
    value = (m.group(1).lower() if m else "")
    return "pl" if re.search(r"\b(pl|polski|polish)\b", value) else "en"


def root_from_command(command: str, cwd: Path) -> Path | None:
    try:
        parts = shlex.split(command, posix=True)
    except ValueError:
        return None
    for i, part in enumerate(parts[:-2]):
        if SCRIPT_RE.search(part) and parts[i + 1] == "commit":
            root = Path(parts[i + 2]).expanduser()
            return root if root.is_absolute() else cwd / root
    return None


def load_pending(root: Path | None, token: str) -> dict | None:
    folders = ([root / "registers" / ".pending"] if root else []) + [CONFIG_PENDING]
    for folder in folders:
        p = folder / f"{token}.json"
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return None
    return None


def ask(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                             "permissionDecisionReason": reason[:1000]}},
                     ensure_ascii=False))


def commit_reason(body: dict | None, lang: str) -> str:
    t = TEXT.get(lang, TEXT["en"])
    if not body:
        return t["unknown"]
    lines = [str(x) for x in body.get("lines") or []]
    files = []
    for op in body.get("ops") or []:
        if op.get("op") in ("write", "copy"):
            files.append(str(op.get("path")))
        elif op.get("op") == "move":
            files.append(f"{op.get('path')} → {op.get('to')}")
        elif op.get("op") == "pointer":
            files.append("location.md")
    shown = "; ".join(lines[:4]) + (f" (+{len(lines) - 4})" if len(lines) > 4 else "")
    return f"{t['commit']}: {shown or body.get('command', '')} [{t['files']}: {', '.join(files)}]"


def decide(data: dict) -> str | None:
    """The reason to ask, or None to let the call through."""
    tool = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    cwd = Path(data.get("cwd") or os.getcwd())
    if tool == "Bash":
        command = str(tool_input.get("command") or "")
        if not COMMIT_RE.search(command):
            return None
        token = TOKEN_RE.search(command)
        root = root_from_command(command, cwd)
        body = load_pending(root, token.group(1)) if token else None
        lang = (body or {}).get("lang") or household_lang(root)
        return commit_reason(body, lang)
    if tool in WRITE_TOOLS:
        raw = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not raw:
            return None
        path = Path(str(raw)).expanduser()
        path = path if path.is_absolute() else cwd / path
        root = household_root(path.resolve().parent)
        if root is None:
            return None
        try:
            rel = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = path.name
        return TEXT[household_lang(root)]["direct"].format(path=rel)
    return None


def main() -> int:
    if os.environ.get("HOUSEHOLDBOT_HOOK", "").strip().lower() == "off":
        return 0
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        stream = getattr(sys.stdin, "buffer", None)
        raw = stream.read().decode("utf-8-sig") if stream is not None else sys.stdin.read()
        data = json.loads(raw or "{}")
    except (OSError, ValueError):
        return 0
    reason = decide(data if isinstance(data, dict) else {})
    if reason:
        ask(reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
