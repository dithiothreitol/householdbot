#!/usr/bin/env python3
"""Build the release packages of HouseholdBot.

    python scripts/package.py              dist/householdbot.plugin and its SHA-256
    python scripts/package.py --skills     also dist/skills/<skill>.zip, one per skill

`householdbot.plugin` is a zip of the plugin folder with the plugin root at the
top of the archive, the format Cowork in the Claude desktop app installs
(Add > Upload plugin). Each skill zip holds one skill folder (SKILL.md,
reference/ and its generated shared/ copies) for claude.ai, which takes single
skills: its SKILL.md keeps only the frontmatter keys an upload accepts.

The build refuses to run when the generated copies are stale or the repository
checks fail (pass --skip-checks only for a quick local look). Entries are sorted
and carry a fixed timestamp, so the same tree always gives the same bytes and
the published checksum can be reproduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "householdbot"
DIST = REPO / "dist"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
SKIP_PARTS = {"__pycache__", ".DS_Store", "Thumbs.db", "desktop.ini"}


def files_under(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and not SKIP_PARTS.intersection(p.parts) and p.suffix != ".pyc")


# Frontmatter keys a single-skill upload to claude.ai accepts; any other key is an error there.
SKILL_UPLOAD_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def upload_frontmatter(text: str) -> str:
    """SKILL.md for a single-skill upload: frontmatter keys outside SKILL_UPLOAD_KEYS
    (such as argument-hint, a Claude Code prompt hint) are left out, with their lines."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    kept, keep = [], True
    for line in lines[1:end]:
        if line and not line[0].isspace():
            keep = line.split(":", 1)[0].strip() in SKILL_UPLOAD_KEYS
        if keep:
            kept.append(line)
    return "\n".join([lines[0], *kept, *lines[end:]])


def write_zip(target: Path, root: Path, prefix: str = "", for_upload: bool = False) -> int:
    """Zip every file under root; names are relative to root, under prefix."""
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files_under(root):
            name = prefix + path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(name, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if path.suffix in (".py", ".sh") else 0o644
            info.external_attr = (0o100000 | mode) << 16
            data = path.read_bytes()
            if for_upload and path.name == "SKILL.md" and path.parent == root:
                data = upload_frontmatter(data.decode("utf-8")).encode("utf-8")
            zf.writestr(info, data)
            count += 1
    return count


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_checks() -> None:
    for cmd in ([sys.executable, "scripts/sync.py", "--check"], [sys.executable, "scripts/validate.py"]):
        result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            sys.stderr.write(result.stdout[-2000:] + result.stderr[-2000:])
            raise SystemExit(f"refusing to package: {' '.join(cmd[1:])} failed")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills", action="store_true", help="also build one zip per skill")
    ap.add_argument("--out", default=str(DIST), help="output folder (default dist/)")
    ap.add_argument("--skip-checks", action="store_true", help="do not run sync --check and validate.py")
    args = ap.parse_args(argv)
    if not args.skip_checks:
        run_checks()
    out = Path(args.out)
    manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    name, version = manifest["name"], manifest["version"]

    plugin_file = out / f"{name}.plugin"
    n = write_zip(plugin_file, PLUGIN)
    digest = sha256(plugin_file)
    (out / f"{name}.plugin.sha256").write_bytes(f"{digest}  {plugin_file.name}\n".encode("utf-8"))
    report = {"name": name, "version": version,
              "plugin": {"file": plugin_file.name, "files": n, "bytes": plugin_file.stat().st_size,
                         "sha256": digest}}

    if args.skills:
        skills = []
        for skill in sorted(p for p in (PLUGIN / "skills").iterdir() if (p / "SKILL.md").exists()):
            target = out / "skills" / f"{skill.name}.zip"
            count = write_zip(target, skill, prefix=skill.name + "/", for_upload=True)
            skills.append({"skill": skill.name, "files": count, "bytes": target.stat().st_size})
        report["skills"] = skills
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
