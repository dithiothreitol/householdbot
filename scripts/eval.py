#!/usr/bin/env python3
"""Run the behaviour tests against a staged copy of the plugin.

The tests live in evals/ at the repository root, outside the plugin package,
so the published plugin carries no test files. `claude plugin eval` reads cases
only from a folder inside the plugin, so this script copies householdbot/ and
evals/ into build/eval/householdbot/ and runs the command there. Every argument
goes to `claude plugin eval` unchanged; results land in evals/results/<time>/
unless --output-dir is given.

    python scripts/eval.py --scaffold --allow-tools Write Edit --no-publish
    python scripts/eval.py --case "bills-due-*" --runs 1 --scaffold --allow-tools Write Edit --no-publish
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "householdbot"
EVALS = REPO / "evals"
STAGE = REPO / "build" / "eval" / "householdbot"
SKIP = shutil.ignore_patterns("results", "__pycache__", "*.pyc", ".replay")


def stage() -> None:
    """A fresh copy of the plugin with the tests inside it, where the command looks for them."""
    if STAGE.exists():
        shutil.rmtree(STAGE)
    shutil.copytree(PLUGIN, STAGE, ignore=SKIP)
    shutil.copytree(EVALS, STAGE / "evals", ignore=SKIP)


def main(argv: list[str]) -> int:
    claude = shutil.which("claude")
    if not claude:
        print("claude is not on PATH; install Claude Code first", file=sys.stderr)
        return 2
    stage()
    args = list(argv)
    if "--eval-dir" in args:
        print("--eval-dir is set by this script (evals inside the staged copy)", file=sys.stderr)
        return 2
    if "--output-dir" not in args:
        args += ["--output-dir", str(EVALS / "results" / time.strftime("%Y-%m-%dT%H-%M-%S"))]
    cmd = [claude, "plugin", "eval", str(STAGE), "--eval-dir", "evals", *args]
    print("staged:", STAGE, flush=True)
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
