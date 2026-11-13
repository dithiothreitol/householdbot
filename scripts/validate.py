#!/usr/bin/env python3
"""Repository checks for HouseholdBot that `claude plugin validate` does not make.

  python scripts/validate.py          print findings; exit 1 on any error

Checks: manifests, skill frontmatter and size, self-sufficient skills (every
path a SKILL.md names exists inside its own folder), generated copies up to
date, plugin directory limits, agents' tool limits, eval suite shape and
coverage, country packs, and identifiers or secrets in committed files.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "core" / "scripts"))
sys.dont_write_bytecode = True
import record  # noqa: E402

PLUGIN = REPO / "householdbot"
SKILLS = PLUGIN / "skills"
MAX_FILES, WARN_FILES, MAX_BYTES = 512, 450, 256 * 1024
ALLOWED_EXT = {".md", ".json", ".py", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".txt",
               ".yaml", ".yml", ".sh", ".jsonl", ""}
FORBIDDEN_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED = ("anthropic", "claude")
MIN_CASES_PER_SKILL = 3
SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "Anthropic API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
]
TEXT_EXT = {".md", ".json", ".py", ".txt", ".yaml", ".yml", ".sh", ".jsonl", ".toml", ".cfg", ""}

errors: list[str] = []
warnings: list[str] = []


def rel(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm, body, key = {}, m.group(2), None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            key = km.group(1)
            val = km.group(2).strip()
            fm[key] = "" if val in (">", "|", ">-", "|-") else val.strip('"')
        elif key and line.startswith(" "):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm, body


def committed_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                             cwd=REPO, capture_output=True, text=True, check=True).stdout
        return [REPO / line for line in out.splitlines() if line and (REPO / line).is_file()]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts]


def check_manifests() -> None:
    try:
        market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifest unreadable: {exc}")
        return
    entry = next((p for p in market.get("plugins", []) if p.get("name") == plugin.get("name")), None)
    if not entry:
        errors.append("marketplace.json has no entry for plugin " + str(plugin.get("name")))
    elif (REPO / entry.get("source", "")).resolve() != PLUGIN.resolve():
        errors.append(f"marketplace source {entry.get('source')} does not point to {rel(PLUGIN)}")
    if not re.match(r"^\d+\.\d+\.\d+$", plugin.get("version", "")):
        errors.append("plugin.json version must be semver")
    for name in (".mcp.json", "hooks/hooks.json"):
        p = PLUGIN / name
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{rel(p)} is not valid JSON: {exc}")
                continue
            for srv, spec in (data.get("mcpServers") or {}).items():
                if not str(spec.get("url", "")).startswith("https://"):
                    errors.append(f"{rel(p)}: server {srv} must use an https URL")
    changelog = REPO / "CHANGELOG.md"
    if changelog.exists() and f"## {plugin.get('version')}" not in changelog.read_text(encoding="utf-8"):
        warnings.append(f"CHANGELOG.md has no section for version {plugin.get('version')}")


def check_skills() -> set[str]:
    names = set()
    for sdir in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        skill_md = sdir / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{rel(sdir)}: no SKILL.md")
            continue
        names.add(sdir.name)
        fm, body = frontmatter(skill_md)
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != sdir.name:
            errors.append(f"{rel(skill_md)}: name '{name}' must match folder '{sdir.name}'")
        if not NAME_RE.match(name) or len(name) > 64 or any(r in name for r in RESERVED):
            errors.append(f"{rel(skill_md)}: invalid skill name '{name}'")
        if not desc:
            errors.append(f"{rel(skill_md)}: empty description")
        elif len(desc) > 1024:
            errors.append(f"{rel(skill_md)}: description is {len(desc)} characters (max 1024)")
        if re.search(r"<[A-Za-z/][^>]*>", desc):
            errors.append(f"{rel(skill_md)}: description contains an XML-like tag")
        lines = skill_md.read_text(encoding="utf-8").count("\n") + 1
        if lines >= 500:
            errors.append(f"{rel(skill_md)}: {lines} lines (keep under 500)")
        if not (sdir / "reference" / "gotchas.md").exists():
            errors.append(f"{rel(sdir)}: missing reference/gotchas.md")
        for md in sdir.rglob("*.md"):
            if "shared" in md.relative_to(sdir).parts:
                continue
            text = md.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)#\s]+)\)", text):
                if re.match(r"^[a-z]+://", target):
                    continue
                resolved = (md.parent / target).resolve()
                if not str(resolved).startswith(str(sdir.resolve())):
                    errors.append(f"{rel(md)}: link {target} leaves the skill folder")
                elif not resolved.exists():
                    errors.append(f"{rel(md)}: link {target} does not exist")
            if "../../shared" in text or "${CLAUDE_PLUGIN_ROOT}" in text:
                errors.append(f"{rel(md)}: refers outside the skill folder; use the skill's shared/ copy")
            if re.search(r"/household:[a-z]", text):
                errors.append(f"{rel(md)}: old command prefix /household:")
            for path in re.findall(r"`((?:shared|reference)/[A-Za-z0-9_./<>-]+)`", text):
                if "<" in path:
                    continue
                if not (sdir / path).exists():
                    errors.append(f"{rel(md)}: names `{path}`, which is not in the skill folder")
    return names


def check_cross_refs(skills: set[str]) -> None:
    agents = {p.stem for p in (PLUGIN / "agents").glob("*.md")}
    for md in [*PLUGIN.rglob("*.md"), REPO / "README.md", REPO / "QUICKSTART.md"]:
        if not md.exists() or "shared" in md.parts:
            continue
        for ref in re.findall(r"/householdbot:([a-z0-9-]+)", md.read_text(encoding="utf-8")):
            if ref not in skills:
                errors.append(f"{rel(md)}: /householdbot:{ref} is not a skill")
    manifest = json.loads((REPO / "core" / "vendor.json").read_text(encoding="utf-8"))
    for s in manifest["skills"]:
        if s not in skills:
            errors.append(f"core/vendor.json lists unknown skill {s}")
    for s in skills:
        if s not in manifest["skills"]:
            errors.append(f"skill {s} is missing from core/vendor.json")
    for a in agents:
        fm, _ = frontmatter(PLUGIN / "agents" / f"{a}.md")
        if fm.get("name") != a or not fm.get("description"):
            errors.append(f"agents/{a}.md: needs name '{a}' and a description")
        tools = {t.strip() for t in fm.get("tools", "").split(",") if t.strip()}
        if a == "document-reader" and tools - {"Read", "Glob", "Grep"}:
            errors.append(f"agents/{a}.md: a reader of untrusted documents gets read tools only, has {sorted(tools)}")
        if a == "deadline-watcher" and tools & {"Write", "Edit", "NotebookEdit", "WebFetch"}:
            errors.append(f"agents/{a}.md: the watcher is read-only, has {sorted(tools)}")


def check_sync() -> None:
    res = subprocess.run([sys.executable, str(REPO / "scripts" / "sync.py"), "--check"],
                         capture_output=True, text=True)
    if res.returncode:
        report = json.loads(res.stdout)
        errors.append("generated copies are stale; run python scripts/sync.py: "
                      + ", ".join(report["stale"] + report["removed_or_extra"]))


def check_directory_limits() -> None:
    files = [p for p in PLUGIN.rglob("*") if p.is_file() and "results" not in p.relative_to(PLUGIN).parts]
    if len(files) > MAX_FILES:
        errors.append(f"plugin has {len(files)} files (directory limit {MAX_FILES})")
    elif len(files) > WARN_FILES:
        warnings.append(f"plugin has {len(files)} files, close to the directory limit {MAX_FILES}")
    for p in files:
        if p.name in FORBIDDEN_NAMES or p.suffix in (".pyc",) or "__pycache__" in p.parts:
            errors.append(f"{rel(p)}: system or cache file in the plugin")
        elif p.suffix.lower() not in ALLOWED_EXT:
            errors.append(f"{rel(p)}: file type {p.suffix} is not accepted by the plugin directory")
        if p.stat().st_size >= MAX_BYTES and p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
            errors.append(f"{rel(p)}: {p.stat().st_size} bytes (limit 256 KiB)")
    readme = PLUGIN / "README.md"
    if not readme.exists() or len(readme.read_text(encoding="utf-8").split()) < 40:
        errors.append("householdbot/README.md missing or under 40 words")
    if not (PLUGIN / "LICENSE").exists():
        errors.append("householdbot/LICENSE missing")
    ga = REPO / ".gitattributes"
    if ga.exists() and re.search(r"export-ignore|filter=|\bident\b", ga.read_text(encoding="utf-8")):
        errors.append(".gitattributes uses an attribute the plugin directory refuses")
    print(f"plugin files: {len(files)} of {MAX_FILES}")


def check_evals(skills: set[str]) -> None:
    if (PLUGIN / "evals").exists():
        errors.append("householdbot/evals/ exists: behaviour tests live in evals/ at the repository root, "
                      "outside the plugin package (run them with python scripts/eval.py)")
    root = REPO / "evals"
    counts = {s: 0 for s in skills}
    cases = {p.parent for p in [*root.rglob("prompt.md"), *root.rglob("case.yaml")]}
    for case in sorted(cases):
        if "results" in case.relative_to(root).parts:
            continue
        cy = case / "case.yaml"
        ytext = cy.read_text(encoding="utf-8") if cy.exists() else ""
        has_graders = list((case / "graders").glob("*.md")) or re.search(r"^graders:\s*$", ytext, re.M)
        if not has_graders:
            errors.append(f"{rel(case)}: eval case without graders")
        prompt = case / "prompt.md"
        body = frontmatter(prompt)[1] if prompt.exists() else ""
        if not body.strip() and not re.search(r"^\s+prompt:\s*\S", ytext, re.M):
            errors.append(f"{rel(case)}: empty prompt")
        if ytext and 'schema_version: "1.1"' not in ytext:
            errors.append(f"{rel(cy)}: needs schema_version \"1.1\"")
        for llm_block in re.findall(r"type: llm\n(\s+)criteria: \|\n((?:\1  .*\n|\n)+)", ytext):
            crit = llm_block[1]
            if "PASS" not in crit or "FAIL" not in crit:
                errors.append(f"{rel(cy)}: llm criteria need PASS and FAIL conditions")
        group = case.relative_to(root).parts[0]
        if group in counts:
            counts[group] += 1
        sm = re.search(r"scaffold_script:\s*(\S+)", ytext)
        if sm and not (case / sm.group(1)).exists():
            errors.append(f"{rel(cy)}: scaffold script {sm.group(1)} not found")
    for s, n in sorted(counts.items()):
        if n < MIN_CASES_PER_SKILL:
            errors.append(f"evals: skill {s} has {n} case(s), needs at least {MIN_CASES_PER_SKILL}")
    print("eval cases per skill: " + ", ".join(f"{s} {n}" for s, n in sorted(counts.items())))


def check_packs() -> None:
    for js in sorted((REPO / "core" / "locale").glob("*.json")):
        data = json.loads(js.read_text(encoding="utf-8"))
        for key in ("pack", "reviewed", "weekend", "holidays", "counting_rules"):
            if key not in data:
                errors.append(f"{rel(js)}: missing '{key}'")
        for rid, rule in (data.get("counting_rules") or {}).items():
            if rule.get("end_roll") not in ("forward", "none"):
                errors.append(f"{rel(js)}: rule {rid} needs end_roll forward or none")
        for section in ("response_windows", "recurring", "deemed_delivery"):
            for item in data.get(section, []):
                if section != "deemed_delivery" and item.get("counting") not in data.get("counting_rules", {}):
                    errors.append(f"{rel(js)}: {section} {item.get('id')} uses unknown rule {item.get('counting')}")
                if not item.get("law"):
                    errors.append(f"{rel(js)}: {section} {item.get('id')} names no law")
        windows = {w.get("id") for w in data.get("response_windows", [])}
        for ev in data.get("life_events", []):
            for wid in ev.get("windows", []):
                if wid not in windows:
                    errors.append(f"{rel(js)}: life event {ev.get('id')} names unknown window {wid}")
            if not ev.get("title"):
                errors.append(f"{rel(js)}: life event {ev.get('id')} has no title")
        for item in data.get("retention", []):
            if not item.get("law") and not item.get("suggested"):
                errors.append(f"{rel(js)}: retention {item.get('id')} needs a law or \"suggested\": true")
        md = js.with_suffix(".md")
        if not md.exists():
            errors.append(f"{rel(js)}: no matching {md.name}")
            continue
        text = md.read_text(encoding="utf-8")
        for heading in ("Public holidays", "How deadlines are counted", "Scam patterns", "Sources"):
            if f"## {heading}" not in text:
                errors.append(f"{rel(md)}: missing section '## {heading}'")
        if f"Reviewed:** {data.get('reviewed')}" not in text:
            warnings.append(f"{rel(md)}: review date differs from {js.name} ({data.get('reviewed')})")


TRANSLATED_DOCS = ["README.md", "QUICKSTART.md", "householdbot/README.md", "householdbot/PRIVACY.md"]


def check_languages() -> None:
    i18n = REPO / "core" / "i18n"

    def keys(d: dict, prefix: str = "") -> set:
        out = set()
        for k, v in d.items():
            out.add(prefix + k)
            if isinstance(v, dict) and k != "currency_symbols":
                out |= keys(v, prefix + k + ".")
        return out

    base = json.loads((i18n / "en.json").read_text(encoding="utf-8"))
    if not base.get("default"):
        errors.append("core/i18n/en.json must be the default language")
    langs = []
    for f in sorted(i18n.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        langs.append(f.stem)
        if data.get("lang") != f.stem:
            errors.append(f"{rel(f)}: 'lang' must be '{f.stem}'")
        if f.stem != "en" and data.get("default"):
            errors.append(f"{rel(f)}: only English is the default")
        missing, extra = keys(base) - keys(data), keys(data) - keys(base)
        if missing or extra:
            errors.append(f"{rel(f)}: keys differ from en.json (missing {sorted(missing)}, extra {sorted(extra)})")
        for unit, forms in (data.get("units") or {}).items():
            if not isinstance(forms, list) or not forms:
                errors.append(f"{rel(f)}: units.{unit} must be a list of plural forms")
    for lang in langs:
        for name in ("household-profile.md", "registers-README.md"):
            p = REPO / "core" / "templates" / lang / name
            if not p.exists():
                errors.append(f"core/templates/{lang}/{name} missing")
            elif name == "household-profile.md":
                text = p.read_text(encoding="utf-8")
                if "[PLACEHOLDER" not in text or "[DEFAULT" not in text:
                    errors.append(f"{rel(p)}: keep the [PLACEHOLDER] and [DEFAULT] markers")
    messages = SKILLS / "household-onboard" / "reference" / "messages.md"
    if messages.exists():
        text = messages.read_text(encoding="utf-8")
        if text.count("**English**") != text.count("**Polski**"):
            errors.append(f"{rel(messages)}: every setup text needs an English and a Polish version")
    for doc in TRANSLATED_DOCS:
        en = REPO / doc
        pl = en.with_name(en.stem + ".pl.md")
        if not pl.exists():
            errors.append(f"{doc}: Polish translation {rel(pl)} missing")
            continue
        if f"]({pl.name})" not in en.read_text(encoding="utf-8")[:400]:
            errors.append(f"{doc}: first lines must link to {pl.name}")
        if f"]({en.name})" not in pl.read_text(encoding="utf-8")[:400]:
            errors.append(f"{rel(pl)}: first lines must link to {en.name}")


def check_identifiers() -> None:
    for p in committed_files():
        if p.suffix.lower() not in TEXT_EXT or p.stat().st_size > 2_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for rx, label in SECRET_PATTERNS:
            if rx.search(text):
                errors.append(f"{rel(p)}: contains what looks like a {label}")
        if p.suffix in (".md", ".json", ".txt", ".jsonl"):
            found = [w.split(": ", 1)[1] for w in record.identifier_warnings(text, "x")
                     if "password" not in w]
            for f in sorted(set(found)):
                errors.append(f"{rel(p)}: {f}; test data must be synthetic")


def main() -> int:
    check_manifests()
    skills = check_skills()
    check_cross_refs(skills)
    check_sync()
    check_directory_limits()
    check_evals(skills)
    check_packs()
    check_languages()
    check_identifiers()
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
