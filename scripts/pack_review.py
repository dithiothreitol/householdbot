#!/usr/bin/env python3
"""Which country packs are due for a review, on the repository's side.

A pack records the day it was last checked against its official sources
(`reviewed`) and the points it could not settle (`sources.uncertain`). This
script reports every pack in core/locale/ with its age, and marks a pack due
when the review is older than --months (default 6). The monthly workflow
pack-review.yml opens or updates one issue per due pack with the body from
--issue-body; the procedure is in docs/country-packs.md, "Reviewing a pack".

    python scripts/pack_review.py
    python scripts/pack_review.py --today 2027-06-01 --months 6
    python scripts/pack_review.py --issue-body PL

Standard library only; prints one JSON object (or the issue body as Markdown).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOCALE = REPO / "core" / "locale"


def months_between(a: date, b: date) -> float:
    return (b - a).days / 30.44


def packs(today: date, months: int) -> list[dict]:
    out = []
    for path in sorted(LOCALE.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        reviewed = data.get("reviewed")
        try:
            when = date.fromisoformat(str(reviewed))
        except ValueError:
            when = None
        uncertain = (data.get("sources") or {}).get("uncertain") or []
        age = round(months_between(when, today), 1) if when else None
        out.append({"pack": data.get("pack", path.stem), "file": path.relative_to(REPO).as_posix(),
                    "reviewed": reviewed, "age_months": age,
                    "due": when is None or age >= months, "uncertain": len(uncertain),
                    "windows": len(data.get("response_windows") or []),
                    "scope": data.get("scope")})
    return out


def issue_body(pack: dict, months: int) -> str:
    return "\n".join([
        f"The {pack['pack']} country pack was last reviewed on {pack['reviewed']} "
        f"({pack['age_months']} months ago; the review is due after {months}).",
        "",
        f"- File: `{pack['file']}` and its `.md` companion",
        f"- Response windows: {pack['windows']}",
        f"- Points left uncertain at the last review (`sources.uncertain`): {pack['uncertain']}",
        "",
        "Steps (docs/country-packs.md, \"Reviewing a pack\"):",
        "",
        "1. Open every source the pack cites and check each rule against the act in force today.",
        "2. Settle the uncertain points you can; leave the rest listed with what would settle them.",
        "3. Run `python core/scripts/dates.py check-pack --pack <file> --year <next year>` and the unit tests.",
        "4. Set `reviewed` to the day of the review, note who reviewed it in the commit message, and "
        "add a CHANGELOG line.",
        "",
        "This issue is opened and updated by the pack-review workflow; close it with the commit "
        "that records the review.",
    ])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today", help="ISO date; default the system date")
    ap.add_argument("--months", type=int, default=6, help="age that makes a review due")
    ap.add_argument("--issue-body", metavar="PACK", help="print the issue body for this pack")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    today = date.fromisoformat(args.today) if args.today else date.today()
    found = packs(today, args.months)
    if args.issue_body:
        pack = next((p for p in found if p["pack"] == args.issue_body), None)
        if pack is None:
            print(f"no pack {args.issue_body}", file=sys.stderr)
            return 1
        print(issue_body(pack, args.months))
        return 0
    print(json.dumps({"today": today.isoformat(), "months": args.months, "packs": found,
                      "due": [p["pack"] for p in found if p["due"]]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
