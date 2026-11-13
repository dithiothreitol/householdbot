#!/usr/bin/env python3
"""The household record for HouseholdBot.

Reads, checks and writes the two registers of a household folder:
registers/documents.json and registers/obligations.json. Standard library
only. Every command prints one JSON object.

Writes need --approved-by NAME. The name is recorded in log/decisions.md as
the household member gave it; the script cannot verify who is typing. Every
write keeps a copy of the previous file in registers/.history/ and refuses
to run while sync-conflict copies of a register exist.

Examples:
  python3 record.py locate
  python3 record.py init ./household --approved-by Anna
  python3 record.py validate ./household
  python3 record.py due ./household --today 2026-11-13 --country PL
  python3 record.py find ./household --query "polisa OC"
  python3 record.py add ./household --register obligations --file entry.json --dry-run
  python3 record.py add ./household --register documents --file doc.json --original scan.pdf --approved-by Anna
  python3 record.py complete ./household --id ob-2026-0003 --approved-by Anna --country PL
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True  # leave no __pycache__ inside the plugin folder
import dates  # noqa: E402

VERSION = "1.0.0"
SCHEMA_VERSION = 1
PROFILE = "household-profile.md"
REGISTERS = {"documents": Path("registers/documents.json"),
             "obligations": Path("registers/obligations.json")}
PREFIX = {"documents": "doc", "obligations": "ob"}
ID_RE = {"documents": re.compile(r"^doc-(\d{4})-(\d{4,})$"),
         "obligations": re.compile(r"^ob-(\d{4})-(\d{4,})$")}
MONEY_RE = re.compile(r"^-?\d+(\.\d{1,2})?$")
CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
POINTER = Path.home() / ".claude" / "plugins" / "config" / "householdbot" / "location.md"
HISTORY_KEEP = 20

CATEGORIES = ["home", "vehicle", "money", "tax", "insurance", "utilities", "health",
              "children", "identity", "work", "daily", "other"]
KINDS = ["payment", "renewal", "filing", "response", "appointment", "expiry", "task"]
OB_STATUS = ["open", "done", "cancelled", "lapsed"]
DOC_STATUS = ["filed", "action-needed", "superseded"]
PROVENANCE = ["stated in document", "calculated from document", "country pack rule — verify",
              "model calculation — verify", "told by household member"]
CLOSED = {"done", "cancelled", "lapsed"}

DOC_FIELDS = {
    "id": "id", "title": "str!", "type": "str!", "category": "category", "issuer": "str?",
    "concerns": "list[str]", "document_date": "date?", "received_date": "date?", "file": "str?",
    "sha256": "str?", "language": "str?", "key_facts": "facts", "obligations": "list[str]",
    "supersedes": "str?", "keep_until": "keep", "status": "doc_status", "notes": "str",
    "created": "date!", "updated": "date!",
}
OB_FIELDS = {
    "id": "id", "series": "str?", "title": "str!", "kind": "kind", "category": "category",
    "owner": "str?", "subject": "str?", "counterparty": "str?", "due_date": "date?",
    "do_by": "date?", "do_by_note": "str", "lead_time_days": "int?", "recurrence": "str?",
    "recurrence_day": "int?", "amount": "money?", "currency": "currency?", "auto_renews": "bool?",
    "notice": "obj?", "source": "obj?", "provenance": "provenance", "law": "str?",
    "status": "ob_status", "done_date": "date?", "notes": "str", "created": "date!",
    "updated": "date!",
}
FIELDS = {"documents": DOC_FIELDS, "obligations": OB_FIELDS}
REQUIRED = {
    "documents": ["id", "title", "type", "category", "status", "created", "updated"],
    "obligations": ["id", "title", "kind", "category", "status", "provenance", "created", "updated"],
}
DEFAULTS = {
    "documents": {"issuer": None, "concerns": [], "document_date": None, "received_date": None,
                  "file": None, "sha256": None, "language": None, "key_facts": [],
                  "obligations": [], "supersedes": None, "keep_until": None,
                  "status": "filed", "notes": ""},
    "obligations": {"series": None, "owner": None, "subject": None, "counterparty": None,
                    "due_date": None, "do_by": None, "do_by_note": "", "lead_time_days": None,
                    "recurrence": "none", "recurrence_day": None, "amount": None,
                    "currency": None, "auto_renews": None, "notice": None, "source": None,
                    "law": None, "status": "open", "done_date": None, "notes": ""},
}
CONFLICT_PATTERNS = [
    re.compile(r"conflict", re.I),                                   # Dropbox, Nextcloud, Syncthing
    re.compile(r"^(documents|obligations|household-profile) \(\d+\)\.(json|md)$"),   # Google Drive
    re.compile(r"^(documents|obligations|household-profile) \d+\.(json|md)$"),       # iCloud
    re.compile(r"^(documents|obligations|household-profile)-[A-Za-z0-9][A-Za-z0-9-]*\.(json|md)$"),  # OneDrive
]
STOPWORDS = set("""
a i w z na do od po o u we ze sie się jest są jak gdzie kiedy co czy mi mnie mój moja moje
nasz nasza nasze ten ta to tam tu dla przez oraz lub albo jaki jaka jakie który która które
the a an of to in on for at by is are was my our where when what which how do does find show
""".split())


class RecordError(Exception):
    """A problem the household or the calling skill must resolve."""


# --------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------

def today_from(args) -> date:
    return dates.parse_date(args.today) if getattr(args, "today", None) else date.today()


def root_of(path: str) -> Path:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise RecordError(f"no such folder: {root}")
    return root


def empty_register(name: str) -> dict:
    return {"schema_version": SCHEMA_VERSION, name: []}


def load(root: Path, name: str, required: bool = True) -> dict:
    p = root / REGISTERS[name]
    if not p.exists():
        if required:
            raise RecordError(f"{REGISTERS[name].as_posix()} not found in {root}; "
                              "run household-onboard, or record.py init")
        return empty_register(name)
    try:
        with p.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise RecordError(f"{REGISTERS[name].as_posix()} is not valid JSON "
                          f"(line {exc.lineno}, column {exc.colno}); household-doctor can help")
    if not isinstance(data, dict) or not isinstance(data.get(name), list):
        raise RecordError(f"{REGISTERS[name].as_posix()} must be an object with a '{name}' list")
    return data


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    for attempt in range(4):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 3:
                raise
            time.sleep(0.3)


def backup(root: Path, name: str) -> str | None:
    src = root / REGISTERS[name]
    if not src.exists():
        return None
    hist = root / "registers" / ".history"
    hist.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    dst = hist / f"{name}-{stamp}.json"
    shutil.copy2(src, dst)
    olds = sorted(hist.glob(f"{name}-*.json"))
    for old in olds[:-HISTORY_KEEP]:
        old.unlink()
    return dst.relative_to(root).as_posix()


def append_log(root: Path, when: date, approved_by: str, lines: list[str]) -> None:
    log = root / "log" / "decisions.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        log.write_text(LOG_HEADER, encoding="utf-8")
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        for line in lines:
            fh.write(f"- {when.isoformat()} · approved by {approved_by} · {line}\n")


LOG_HEADER = """# Decisions log

Append-only. One line per approved change to the record: the date, who
approved it as they stated it, and what changed. Written by record.py.

"""


def conflicts(root: Path) -> list[str]:
    found = []
    for folder in (root, root / "registers"):
        if not folder.is_dir():
            continue
        for p in folder.iterdir():
            if not p.is_file() or p.name.endswith(".tmp"):
                continue
            if p.name in (PROFILE, "documents.json", "obligations.json"):
                continue
            stem_ok = p.name.startswith(("documents", "obligations", "household-profile"))
            if stem_ok and any(rx.search(p.name) for rx in CONFLICT_PATTERNS):
                found.append(p.relative_to(root).as_posix())
    return sorted(found)


def require_writable(root: Path, args) -> None:
    if not getattr(args, "dry_run", False):
        who = (getattr(args, "approved_by", None) or "").strip()
        if not who:
            raise RecordError("a write needs --approved-by NAME: show the change, get a yes, "
                              "then run again with the name of the person who approved")
    if not getattr(args, "ignore_conflicts", False):
        found = conflicts(root)
        if found:
            raise RecordError("sync-conflict copies exist, so writing now could lose an edit: "
                              + ", ".join(found) + ". Run household-doctor first.")


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def is_date(v) -> bool:
    if not isinstance(v, str) or not dates.ISO_RE.match(v):
        return False
    try:
        date.fromisoformat(v)
        return True
    except ValueError:
        return False


def check_field(kind: str, v) -> str | None:
    """Return an error message, or None when the value fits."""
    if kind == "id":
        return None if isinstance(v, str) else "must be a string id"
    if kind == "str!":
        return None if isinstance(v, str) and v.strip() else "must be a non-empty string"
    if kind == "str":
        return None if isinstance(v, str) else "must be a string"
    if kind == "str?":
        return None if v is None or isinstance(v, str) else "must be a string or null"
    if kind == "date!":
        return None if is_date(v) else "must be an ISO date YYYY-MM-DD"
    if kind == "date?":
        return None if v is None or is_date(v) else "must be an ISO date YYYY-MM-DD or null"
    if kind == "int?":
        ok = v is None or (isinstance(v, int) and not isinstance(v, bool) and v >= 0)
        return None if ok else "must be a whole number or null"
    if kind == "bool?":
        return None if v is None or isinstance(v, bool) else "must be true, false or null"
    if kind == "money?":
        if v is None:
            return None
        if isinstance(v, str) and MONEY_RE.match(v):
            return None
        return 'must be an amount written as a string, e.g. "1240.00", or null'
    if kind == "currency?":
        return None if v is None or (isinstance(v, str) and CURRENCY_RE.match(v)) \
            else "must be an ISO 4217 code such as PLN or EUR, or null"
    if kind == "list[str]":
        return None if isinstance(v, list) and all(isinstance(x, str) for x in v) \
            else "must be a list of strings"
    if kind == "facts":
        if not isinstance(v, list):
            return "must be a list"
        for f in v:
            if not isinstance(f, dict) or not f.get("fact") or "value" not in f:
                return "each key fact needs 'fact' and 'value'"
        return None
    if kind == "obj?":
        return None if v is None or isinstance(v, dict) else "must be an object or null"
    if kind == "keep":
        return None if v is None or v == "permanent" or is_date(v) \
            else 'must be an ISO date, "permanent" or null'
    if kind == "category":
        return None if isinstance(v, str) and v else "must be a category"
    if kind == "kind":
        return None if v in KINDS else f"must be one of {KINDS}"
    if kind == "ob_status":
        return None if v in OB_STATUS else f"must be one of {OB_STATUS}"
    if kind == "doc_status":
        return None if v in DOC_STATUS else f"must be one of {DOC_STATUS}"
    if kind == "provenance":
        return None if v in PROVENANCE else f"must be one of {PROVENANCE}"
    return f"unknown field kind {kind}"


def pesel_valid(s: str) -> bool:
    w = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    return (10 - sum(int(a) * b for a, b in zip(s[:10], w)) % 10) % 10 == int(s[10])


def nrb_valid(digits: str) -> bool:
    # Polish account number (26 digits) as an IBAN with country code PL.
    rearranged = digits[2:] + "2521" + digits[:2]  # P=25, L=21
    return int(rearranged) % 97 == 1


def luhn_valid(s: str) -> bool:
    total, alt = 0, False
    for ch in reversed(s):
        n = int(ch)
        if alt:
            n = n * 2 - 9 if n > 4 else n * 2
        total += n
        alt = not alt
    return total % 10 == 0


SECRET_WORDS = re.compile(r"(hasł|haslo|password|passcode|\bpin\b|\bcvv\b|\bcvc\b|kod blik|seed phrase)", re.I)


def identifier_warnings(obj, path: str = "") -> list[str]:
    """Flag values that look like personal identifiers, without echoing them."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += identifier_warnings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += identifier_warnings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        compact = re.sub(r"[\s-]", "", obj)
        for m in re.finditer(r"(?<!\d)\d{11}(?!\d)", obj):
            if pesel_valid(m.group()):
                out.append(f"{path}: looks like a PESEL number")
        for m in re.finditer(r"(?<!\d)\d{26}(?!\d)", compact):
            if nrb_valid(m.group()):
                out.append(f"{path}: looks like a full bank account number")
        for m in re.finditer(r"(?<!\d)\d{13,19}(?!\d)", compact):
            if luhn_valid(m.group()) and len(m.group()) in (15, 16):
                out.append(f"{path}: looks like a payment card number")
        if SECRET_WORDS.search(obj) and re.search(r"[:=]\s*\S", obj):
            out.append(f"{path}: looks like a password, PIN or code")
    return out


def validate_entries(name: str, entries: list, errors: list, warnings: list) -> None:
    spec = FIELDS[name]
    seen = set()
    for idx, e in enumerate(entries):
        where = f"{name}[{idx}]"
        if not isinstance(e, dict):
            errors.append(f"{where}: must be an object")
            continue
        eid = e.get("id")
        if isinstance(eid, str):
            where = eid
            if not ID_RE[name].match(eid):
                errors.append(f"{where}: id must look like {PREFIX[name]}-YYYY-NNNN")
            if eid in seen:
                errors.append(f"{where}: duplicate id")
            seen.add(eid)
        for field in REQUIRED[name]:
            if field not in e:
                errors.append(f"{where}: missing required field '{field}'")
        for field, value in e.items():
            if field not in spec:
                warnings.append(f"{where}: unknown field '{field}' kept as is")
                continue
            msg = check_field(spec[field], value)
            if msg:
                errors.append(f"{where}.{field}: {msg}")
        cat = e.get("category")
        if isinstance(cat, str) and cat and cat not in CATEGORIES:
            warnings.append(f"{where}.category: '{cat}' is not a standard category {CATEGORIES}")
        if name == "obligations":
            status = e.get("status")
            if status == "done" and not e.get("done_date"):
                warnings.append(f"{where}: status done without done_date")
            if status == "open" and not e.get("due_date") and not e.get("do_by"):
                warnings.append(f"{where}: open obligation without any date; ask for it "
                                "(absent is not zero)")
            if is_date(e.get("do_by")) and is_date(e.get("due_date")) and e["do_by"] > e["due_date"]:
                warnings.append(f"{where}: do_by is after due_date")
            if (e.get("amount") is None) != (e.get("currency") is None):
                warnings.append(f"{where}: amount and currency should be given together")


def validate_record(root: Path, check_files: bool = True) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    data = {}
    for name in REGISTERS:
        try:
            data[name] = load(root, name)
        except RecordError as exc:
            errors.append(str(exc))
            continue
        sv = data[name].get("schema_version")
        if sv is None:
            errors.append(f"{REGISTERS[name].as_posix()}: no schema_version; run migrate")
        elif not isinstance(sv, int) or sv > SCHEMA_VERSION:
            errors.append(f"{REGISTERS[name].as_posix()}: schema_version {sv} is newer than "
                          f"this plugin understands ({SCHEMA_VERSION}); update the plugin")
        elif sv < SCHEMA_VERSION:
            errors.append(f"{REGISTERS[name].as_posix()}: schema_version {sv}; run migrate")
        validate_entries(name, data[name][name], errors, warnings)
        warnings += [f"{REGISTERS[name].as_posix()} {w}" for w in identifier_warnings(data[name][name])]
    if "documents" in data and "obligations" in data:
        doc_ids = {d.get("id") for d in data["documents"]["documents"] if isinstance(d, dict)}
        ob_ids = {o.get("id") for o in data["obligations"]["obligations"] if isinstance(o, dict)}
        archived = archived_ids(root)
        for d in data["documents"]["documents"]:
            if not isinstance(d, dict):
                continue
            for oid in d.get("obligations") or []:
                if oid not in ob_ids and oid not in archived:
                    warnings.append(f"{d.get('id')}: lists obligation {oid}, which is not in the register")
            sup = d.get("supersedes")
            if sup and sup not in doc_ids:
                warnings.append(f"{d.get('id')}: supersedes {sup}, which is not in the register")
            f = d.get("file")
            if check_files and isinstance(f, str) and f and not (root / f).exists():
                warnings.append(f"{d.get('id')}: file {f} not found in the household folder")
        series_open: dict[str, list[str]] = {}
        for o in data["obligations"]["obligations"]:
            if not isinstance(o, dict):
                continue
            src = o.get("source") or {}
            if isinstance(src, dict) and src.get("document") and src["document"] not in doc_ids:
                warnings.append(f"{o.get('id')}: source document {src['document']} is not in the register")
            if o.get("series") and o.get("status") == "open":
                series_open.setdefault(o["series"], []).append(o.get("id"))
        for s, ids in series_open.items():
            if len(ids) > 1:
                warnings.append(f"series '{s}' has {len(ids)} open occurrences: {', '.join(ids)}; a series "
                                "holds one recurring obligation, so give different obligations their own series "
                                "or close the earlier occurrence")
    if not (root / PROFILE).exists():
        warnings.append(f"{PROFILE} not found; household-onboard writes it")
    indexed = set()
    if "documents" in data:
        indexed = {d.get("file") for d in data["documents"]["documents"] if isinstance(d, dict)}
    unindexed = sorted(p.relative_to(root).as_posix() for p in (root / "documents").rglob("*")
                       if p.is_file() and p.relative_to(root).as_posix() not in indexed) \
        if (root / "documents").is_dir() else []
    inbox = sorted(p.relative_to(root).as_posix() for p in (root / "inbox").iterdir()
                   if p.is_file()) if (root / "inbox").is_dir() else []
    found = conflicts(root)
    stats = {}
    if "documents" in data:
        stats["documents"] = len(data["documents"]["documents"])
    if "obligations" in data:
        obs = [o for o in data["obligations"]["obligations"] if isinstance(o, dict)]
        stats["obligations"] = len(obs)
        stats["open_obligations"] = sum(1 for o in obs if o.get("status") == "open")
    return {"ok": not errors, "root": str(root), "errors": errors, "warnings": warnings,
            "conflicts": found, "unindexed_files": unindexed, "inbox": inbox, "stats": stats}


def archived_ids(root: Path) -> set:
    ids = set()
    arch = root / "archive"
    if arch.is_dir():
        for p in arch.glob("obligations-*.json"):
            try:
                with p.open(encoding="utf-8") as fh:
                    ids |= {o.get("id") for o in json.load(fh).get("obligations", [])}
            except (OSError, json.JSONDecodeError):
                continue
    return ids


# --------------------------------------------------------------------------
# Helpers for entries
# --------------------------------------------------------------------------

def next_id(entries: list, name: str, year: int, extra_taken: set | None = None) -> str:
    rx = ID_RE[name]
    top = 0
    for e in entries:
        m = rx.match(str(e.get("id", ""))) if isinstance(e, dict) else None
        if m and int(m.group(1)) == year:
            top = max(top, int(m.group(2)))
    for taken in extra_taken or ():
        m = rx.match(taken)
        if m and int(m.group(1)) == year:
            top = max(top, int(m.group(2)))
    return f"{PREFIX[name]}-{year}-{top + 1:04d}"


def fold(text: str) -> str:
    text = text.replace("ł", "l").replace("Ł", "L")
    norm = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in norm if not unicodedata.combining(ch)).lower()


def slug(text: str, limit: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", fold(text or "")).strip("-")
    return s[:limit].strip("-") or "x"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_entry(args) -> dict:
    if getattr(args, "json", None):
        raw = args.json
    elif getattr(args, "file", None):
        raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    else:
        raise RecordError("give the entry with --json '<object>' or --file <path> (or --file - for stdin)")
    try:
        entry = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RecordError(f"entry is not valid JSON: {exc}")
    if not isinstance(entry, dict):
        raise RecordError("entry must be a JSON object")
    return entry


def fill_defaults(name: str, entry: dict) -> dict:
    out = dict(DEFAULTS[name])
    out.update(entry)
    return out


def duplicate_warnings(name: str, entry: dict, entries: list) -> tuple[list, list]:
    errs, warns = [], []
    for e in entries:
        if not isinstance(e, dict):
            continue
        if name == "documents":
            if entry.get("sha256") and entry.get("sha256") == e.get("sha256"):
                errs.append(f"the same file is already filed as {e.get('id')} ({e.get('title')})")
            elif (entry.get("issuer") and fold(entry.get("issuer", "")) == fold(e.get("issuer") or "")
                  and entry.get("type") == e.get("type")
                  and entry.get("document_date") and entry.get("document_date") == e.get("document_date")):
                warns.append(f"possible duplicate of {e.get('id')} ({e.get('title')}): same issuer, "
                             "type and document date")
        else:
            if e.get("status") != "open":
                continue
            same_series = entry.get("series") and entry.get("series") == e.get("series")
            same_title = fold(entry.get("title", "")) == fold(e.get("title") or "")
            if (same_series or same_title) and entry.get("due_date") == e.get("due_date"):
                warns.append(f"possible duplicate of {e.get('id')} ({e.get('title')}), "
                             f"due {e.get('due_date')}")
            elif same_series:
                warns.append(f"series '{entry['series']}' already has an open occurrence "
                             f"{e.get('id')} due {e.get('due_date')}")
    return errs, warns


def describe_entry(name: str, e: dict) -> str:
    if name == "documents":
        return f"{e['id']} \"{e.get('title')}\""
    when = e.get("do_by") or e.get("due_date")
    when_txt = dates.text_en(date.fromisoformat(when)) if is_date(when) else "no date"
    money = f", {e['currency']} {e['amount']}" if e.get("amount") and e.get("currency") else ""
    return f"{e['id']} \"{e.get('title')}\" (do by {when_txt}{money})"


def pack_or_none(args):
    if getattr(args, "country", None) or getattr(args, "pack", None):
        return dates.load_pack(getattr(args, "country", None), getattr(args, "pack", None))
    return None


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_locate(args) -> dict:
    start = Path(args.start or os.getcwd()).expanduser().resolve()
    candidates = [start] + ([p for p in sorted(start.iterdir()) if p.is_dir()] if start.is_dir() else [])
    for c in candidates:
        if (c / PROFILE).exists():
            return {"found": True, "root": str(c), "how": "working folder"}
    if POINTER.exists():
        target = Path(POINTER.read_text(encoding="utf-8").strip().splitlines()[0].strip()).expanduser()
        if (target / PROFILE).exists():
            return {"found": True, "root": str(target), "how": f"pointer {POINTER}"}
        return {"found": False, "pointer": str(POINTER), "pointer_target": str(target),
                "note": "the pointer names a folder without household-profile.md"}
    return {"found": False, "searched": str(start), "pointer": str(POINTER)}


def cmd_set_pointer(args) -> dict:
    root = root_of(args.root)
    if not (root / PROFILE).exists():
        raise RecordError(f"{root} has no {PROFILE}")
    if args.dry_run:
        return {"dry_run": True, "would_write": str(POINTER), "content": str(root)}
    if not (args.approved_by or "").strip():
        raise RecordError("a write needs --approved-by NAME")
    POINTER.parent.mkdir(parents=True, exist_ok=True)
    POINTER.write_text(str(root) + "\n", encoding="utf-8")
    return {"written": str(POINTER), "root": str(root)}


def cmd_init(args) -> dict:
    root = Path(args.root).expanduser().resolve()
    existing = [str(REGISTERS[n].as_posix()) for n in REGISTERS if (root / REGISTERS[n]).exists()]
    if existing:
        raise RecordError(f"a record already exists here ({', '.join(existing)}); "
                          "nothing was changed. Use validate or household-doctor.")
    plan = [p.as_posix() for p in REGISTERS.values()] + [
        "registers/README.md", "log/decisions.md", "documents/", "briefs/", "inbox/"]
    if args.dry_run:
        return {"dry_run": True, "root": str(root), "would_create": plan}
    if not (args.approved_by or "").strip():
        raise RecordError("a write needs --approved-by NAME")
    root.mkdir(parents=True, exist_ok=True)
    for name in REGISTERS:
        atomic_write_json(root / REGISTERS[name], empty_register(name))
    readme_src = HERE.parent / "templates" / "registers-README.md"
    readme = readme_src.read_text(encoding="utf-8") if readme_src.exists() else REGISTERS_README
    (root / "registers" / "README.md").write_text(readme, encoding="utf-8")
    for d in ("documents", "briefs", "inbox"):
        (root / d).mkdir(exist_ok=True)
    append_log(root, today_from(args), args.approved_by.strip(), ["created the household record"])
    return {"root": str(root), "created": plan}


REGISTERS_README = """# Registers

documents.json lists every filed document; obligations.json lists every
deadline, renewal, payment and dated task. Both are written by HouseholdBot
through record.py, which checks them before every write. Field reference:
the HouseholdBot README, section "The household record".
"""


def cmd_validate(args) -> dict:
    root = root_of(args.root)
    return validate_record(root, check_files=not args.no_files)


def cmd_next_id(args) -> dict:
    root = root_of(args.root)
    name = "documents" if args.kind == "doc" else "obligations"
    data = load(root, name)
    year = args.year or today_from(args).year
    return {"next_id": next_id(data[name], name, year, archived_ids(root))}


def cmd_add(args) -> dict:
    root = root_of(args.root)
    name = args.register
    require_writable(root, args)
    today = today_from(args)
    data = load(root, name)
    entries = data[name]
    entry = fill_defaults(name, read_entry(args))
    warnings: list[str] = []
    normalise_amount(entry, warnings)
    original = None
    if name == "documents" and args.original:
        original = Path(args.original).expanduser().resolve()
        if not original.is_file():
            raise RecordError(f"original not found: {original}")
        entry["sha256"] = sha256_of(original)
    if not entry.get("id"):
        entry["id"] = next_id(entries, name, today.year, archived_ids(root))
    entry.setdefault("created", today.isoformat())
    entry["created"] = entry.get("created") or today.isoformat()
    entry["updated"] = today.isoformat()
    if name == "obligations" and entry.get("due_date") and not entry.get("do_by"):
        pack = pack_or_none(args)
        if pack:
            transit = int(((entry.get("notice") or {}).get("transit_buffer_days")) or 0)
            planned = dates.plan_do_by(pack, dates.parse_date(entry["due_date"]), transit)
            entry["do_by"], entry["do_by_note"] = planned["do_by"], planned["do_by_note"]
        else:
            warnings.append("do_by not given and no --country: do_by left empty")
    if name == "documents" and original is not None:
        stamp = entry.get("document_date") or entry.get("received_date") or today.isoformat()
        year = stamp[:4]
        base = "_".join(x for x in (stamp, slug(entry.get("issuer") or "unknown"),
                                    slug(entry.get("type") or "document")) if x)
        dest_dir = root / "documents" / year
        dest = dest_dir / f"{base}{original.suffix.lower()}"
        n = 2
        while dest.exists():
            dest = dest_dir / f"{base}-{n}{original.suffix.lower()}"
            n += 1
        entry["file"] = dest.relative_to(root).as_posix()
    errs: list[str] = []
    validate_entries(name, [entry], errs, warnings)
    if any(e.get("id") == entry["id"] for e in entries if isinstance(e, dict)):
        errs.append(f"id {entry['id']} already exists")
    dup_errs, dup_warns = duplicate_warnings(name, entry, entries)
    errs += dup_errs
    warnings += dup_warns
    warnings += identifier_warnings(entry)
    if errs:
        return {"ok": False, "errors": errs, "warnings": warnings, "entry": entry}
    result = {"register": REGISTERS[name].as_posix(), "entry": entry, "warnings": warnings,
              "summary": f"add {describe_entry(name, entry)} to {name}"}
    if args.dry_run:
        result["dry_run"] = True
        result["note"] = "nothing written; show this to the household and wait for a yes"
        return result
    if original is not None:
        dest = root / entry["file"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, dest)
        result["copied_original_to"] = entry["file"]
    result["backup"] = backup(root, name)
    entries.append(entry)
    atomic_write_json(root / REGISTERS[name], data)
    append_log(root, today, args.approved_by.strip(), [result["summary"]])
    return result


TEXT_KINDS = {"str!", "str", "str?", "date!", "date?", "money?", "currency?", "category", "kind",
              "ob_status", "doc_status", "provenance", "keep", "id"}


def parse_value(raw: str, kind: str | None = None):
    """Text fields keep the raw text; structured fields are read as JSON."""
    if raw.strip() == "null":
        return None
    if kind in TEXT_KINDS:
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def normalise_amount(entry: dict, warnings: list) -> None:
    v = entry.get("amount")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        entry["amount"] = f"{v:.2f}"
        warnings.append(f'amount stored as the string "{entry["amount"]}"')


def find_entry(entries: list, eid: str) -> dict:
    for e in entries:
        if isinstance(e, dict) and e.get("id") == eid:
            return e
    raise RecordError(f"{eid} not found")


def register_of(eid: str) -> str:
    if eid.startswith("doc-"):
        return "documents"
    if eid.startswith("ob-"):
        return "obligations"
    raise RecordError(f"{eid} is neither a doc- nor an ob- id")


def cmd_update(args) -> dict:
    root = root_of(args.root)
    require_writable(root, args)
    name = register_of(args.id)
    today = today_from(args)
    data = load(root, name)
    entry = find_entry(data[name], args.id)
    before = dict(entry)
    changes = {}
    for item in args.set or []:
        if "=" not in item:
            raise RecordError(f"--set needs field=value, got {item!r}")
        field, raw = item.split("=", 1)
        field = field.strip()
        if field in ("id", "created"):
            raise RecordError(f"'{field}' cannot be changed")
        changes[field] = parse_value(raw, FIELDS[name].get(field))
    if not changes:
        raise RecordError("nothing to change; give one or more --set field=value")
    entry.update(changes)
    warnings: list[str] = []
    if name == "obligations" and "due_date" in changes and "do_by" not in changes:
        pack = pack_or_none(args)
        if pack and entry.get("due_date"):
            transit = int(((entry.get("notice") or {}).get("transit_buffer_days")) or 0)
            planned = dates.plan_do_by(pack, dates.parse_date(entry["due_date"]), transit)
            entry["do_by"], entry["do_by_note"] = planned["do_by"], planned["do_by_note"]
            changes["do_by"] = entry["do_by"]
        else:
            warnings.append("due_date changed but do_by was not recomputed; give --country or set do_by")
    entry["updated"] = today.isoformat()
    errs: list[str] = []
    validate_entries(name, [entry], errs, warnings)
    warnings += identifier_warnings(changes)
    diff = {k: {"from": before.get(k), "to": entry.get(k)} for k in changes}
    summary = f"update {args.id}: " + ", ".join(f"{k} → {json.dumps(entry.get(k), ensure_ascii=False)}"
                                                 for k in changes)
    if errs:
        entry.clear()
        entry.update(before)
        return {"ok": False, "errors": errs, "warnings": warnings, "changes": diff}
    result = {"register": REGISTERS[name].as_posix(), "id": args.id, "changes": diff,
              "warnings": warnings, "summary": summary}
    if args.dry_run:
        result["dry_run"] = True
        result["note"] = "nothing written; show this to the household and wait for a yes"
        return result
    result["backup"] = backup(root, name)
    atomic_write_json(root / REGISTERS[name], data)
    append_log(root, today, args.approved_by.strip(), [summary])
    return result


def series_anchor_day(entries: list, entry: dict) -> int | None:
    if entry.get("recurrence_day"):
        return int(entry["recurrence_day"])
    series = entry.get("series")
    if not series:
        return None
    firsts = sorted(e["due_date"] for e in entries
                    if isinstance(e, dict) and e.get("series") == series and is_date(e.get("due_date")))
    return int(firsts[0][8:10]) if firsts else None


def cmd_complete(args) -> dict:
    root = root_of(args.root)
    require_writable(root, args)
    today = today_from(args)
    data = load(root, "obligations")
    entries = data["obligations"]
    entry = find_entry(entries, args.id)
    if entry.get("status") != "open":
        raise RecordError(f"{args.id} is {entry.get('status')}, not open")
    done_date = args.done_date or today.isoformat()
    if not is_date(done_date):
        raise RecordError(f"--done-date must be YYYY-MM-DD, got {done_date!r}")
    lines = []
    changes = {"status": args.status, "done_date": done_date if args.status == "done" else None,
               "updated": today.isoformat()}
    new_entry = None
    warnings: list[str] = []
    recurrence = entry.get("recurrence") or "none"
    if recurrence != "none" and not args.no_next:
        if not is_date(entry.get("due_date")):
            warnings.append("no due_date to compute the next occurrence from")
        else:
            nxt = dates.next_occurrence(dates.parse_date(entry["due_date"]), recurrence,
                                        series_anchor_day(entries, entry))
            if nxt is None:
                warnings.append(f"recurrence '{recurrence}' cannot be computed; ask for the next date "
                                "and add it with add")
            else:
                new_entry = {k: v for k, v in entry.items()}
                new_entry.update({
                    "id": next_id(entries, "obligations", today.year, archived_ids(root)),
                    "due_date": nxt.isoformat(), "do_by": None, "do_by_note": "",
                    "status": "open", "done_date": None,
                    "created": today.isoformat(), "updated": today.isoformat(),
                    "series": entry.get("series") or slug(entry.get("title", "series")),
                    "notes": f"next occurrence after {entry['id']}, computed from recurrence '{recurrence}'",
                })
                if entry.get("source") and (entry["source"] or {}).get("document"):
                    new_entry["provenance"] = "calculated from document"
                pack = pack_or_none(args)
                if pack:
                    transit = int(((entry.get("notice") or {}).get("transit_buffer_days")) or 0)
                    planned = dates.plan_do_by(pack, nxt, transit)
                    new_entry["do_by"], new_entry["do_by_note"] = planned["do_by"], planned["do_by_note"]
                else:
                    new_entry["do_by"] = nxt.isoformat()
                    warnings.append("no --country: do_by of the next occurrence equals its due_date")
                if not entry.get("series"):
                    changes["series"] = new_entry["series"]
    lines.append(f"mark {args.id} {args.status}" + (f" on {done_date}" if args.status == "done" else ""))
    if new_entry:
        lines.append(f"add next occurrence {describe_entry('obligations', new_entry)}")
    result = {"register": REGISTERS["obligations"].as_posix(), "id": args.id, "changes": changes,
              "next_occurrence": new_entry, "warnings": warnings, "summary": "; ".join(lines)}
    if args.dry_run:
        result["dry_run"] = True
        result["note"] = "nothing written; show this to the household and wait for a yes"
        return result
    entry.update(changes)
    if new_entry:
        entries.append(new_entry)
    result["backup"] = backup(root, "obligations")
    atomic_write_json(root / REGISTERS["obligations"], data)
    append_log(root, today, args.approved_by.strip(), lines)
    return result


def cmd_due(args) -> dict:
    root = root_of(args.root)
    today = today_from(args)
    pack = pack_or_none(args)
    data = load(root, "obligations")
    items, no_date, beyond = [], [], 0
    counts = {b[0]: 0 for b in dates.BANDS}
    warnings = []
    for o in data["obligations"]:
        if not isinstance(o, dict) or o.get("status") != "open":
            continue
        plan = o.get("do_by") or o.get("due_date")
        if not is_date(plan):
            no_date.append({"id": o.get("id"), "title": o.get("title"),
                            "note": "no usable date; ask for it"})
            continue
        computed_note = ""
        if not o.get("do_by") and pack:
            transit = int(((o.get("notice") or {}).get("transit_buffer_days")) or 0)
            planned = dates.plan_do_by(pack, dates.parse_date(plan), transit)
            plan, computed_note = planned["do_by"], "do_by computed now; not stored"
        d = date.fromisoformat(plan)
        days = (d - today).days
        b = dates.band(days)
        lead = o.get("lead_time_days")
        start_now = bool(lead) and days >= 0 and days <= int(lead)
        if days >= args.horizon and not start_now:
            beyond += 1
            continue
        counts[b["band"]] += 1
        due = o.get("due_date")
        row = {
            "id": o.get("id"), "title": o.get("title"), "kind": o.get("kind"),
            "category": o.get("category"), "owner": o.get("owner"),
            "counterparty": o.get("counterparty"), "amount": o.get("amount"),
            "currency": o.get("currency"),
            "due_date": due, "due_text": dates.text_en(date.fromisoformat(due)) if is_date(due) else None,
            "do_by": plan, "do_by_text": dates.text_en(d),
            "do_by_local": pack.text_local(d) if pack else None,
            "days": days, "band": b["band"], "band_label": b["label"],
            "start_now": start_now, "lead_time_days": lead,
            "recurrence": o.get("recurrence"), "series": o.get("series"),
            "provenance": o.get("provenance"), "law": o.get("law"),
            "source_document": (o.get("source") or {}).get("document"),
            "notice": o.get("notice"), "auto_renews": o.get("auto_renews"),
        }
        if computed_note:
            row["note"] = computed_note
        items.append(row)
    items.sort(key=lambda r: (r["do_by"], r["due_date"] or "", r["id"] or ""))
    if not pack:
        warnings.append("no --country: weekdays are English and do_by is not recomputed")
    return {"today": today.isoformat(), "today_source": "argument" if args.today else "system clock",
            "horizon_days": args.horizon, "items": items, "no_date": no_date,
            "counts": counts, "beyond_horizon": beyond, "warnings": warnings}


def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", fold(text)) if len(t) >= 2]


def stem(t: str) -> str:
    if len(t) <= 4:
        return t
    return t[:-1] if len(t) <= 6 else t[:-2]


def entry_text(name: str, e: dict) -> list[tuple[str, int]]:
    parts: list[tuple[str, int]] = [(e.get("title") or "", 3)]
    if name == "documents":
        parts += [(e.get("issuer") or "", 2), (e.get("type") or "", 2), (e.get("category") or "", 2),
                  (" ".join(e.get("concerns") or []), 1), (e.get("notes") or "", 1)]
        for f in e.get("key_facts") or []:
            if isinstance(f, dict):
                parts.append((f"{f.get('fact', '')} {f.get('value', '')} {f.get('quote', '')}", 1))
    else:
        parts += [(e.get("counterparty") or "", 2), (e.get("subject") or "", 2),
                  (e.get("kind") or "", 1), (e.get("category") or "", 2), (e.get("notes") or "", 1),
                  (e.get("owner") or "", 1)]
    return parts


def cmd_find(args) -> dict:
    root = root_of(args.root)
    for name in REGISTERS:
        m = re.search(rf"\b{PREFIX[name]}-\d{{4}}-\d{{4,}}\b", args.query)
        if m:
            data = load(root, name)
            try:
                e = find_entry(data[name], m.group())
            except RecordError:
                return {"query": args.query, "results": [], "total_matches": 0,
                        "note": f"{m.group()} is not in the register"}
            return {"query": args.query, "results": [{"register": name, "id": e.get("id"),
                    "title": e.get("title"), "status": e.get("status"), "score": 100,
                    "matched": [m.group()], "file": e.get("file"), "entry": e}], "total_matches": 1}
    q = [t for t in tokens(args.query) if t not in STOPWORDS]
    if not q:
        raise RecordError("the query has no searchable words")
    stems = [stem(t) for t in q]
    results = []
    for name in REGISTERS:
        if args.register and args.register != name:
            continue
        data = load(root, name)
        for e in data[name]:
            if not isinstance(e, dict):
                continue
            if args.type and e.get("type") != args.type:
                continue
            if args.category and e.get("category") != args.category:
                continue
            score, matched = 0, set()
            for text, weight in entry_text(name, e):
                toks = tokens(text)
                for qs, qt in zip(stems, q):
                    if any(t.startswith(qs) for t in toks):
                        score += weight
                        matched.add(qt)
            if matched:
                coverage = len(matched) / len(q)
                results.append({
                    "register": name, "id": e.get("id"), "title": e.get("title"),
                    "status": e.get("status"), "score": round(score * coverage, 2),
                    "matched": sorted(matched), "file": e.get("file"),
                    "date": e.get("document_date") or e.get("do_by") or e.get("due_date"),
                    "key_facts": e.get("key_facts") if name == "documents" else None,
                })
    results.sort(key=lambda r: (-r["score"], r["id"] or ""))
    return {"query": args.query, "words": q, "results": results[: args.limit],
            "total_matches": len(results),
            "note": "no match in the registers is not proof the document does not exist; "
                    "it may never have been filed" if not results else ""}


def cmd_show(args) -> dict:
    root = root_of(args.root)
    name = register_of(args.id)
    data = load(root, name)
    return {"register": REGISTERS[name].as_posix(), "entry": find_entry(data[name], args.id)}


def cmd_conflicts(args) -> dict:
    root = root_of(args.root)
    found = conflicts(root)
    return {"conflicts": found, "count": len(found),
            "next_step": "compare each copy with diff, merge with the household's approval, "
                         "then move the copy into registers/.history/" if found else ""}


def cmd_diff(args) -> dict:
    def read(p):
        with Path(p).open(encoding="utf-8") as fh:
            data = json.load(fh)
        for name in REGISTERS:
            if isinstance(data.get(name), list):
                return name, {e.get("id"): e for e in data[name] if isinstance(e, dict)}
        raise RecordError(f"{p} is not a register file")
    na, a = read(args.a)
    nb, b = read(args.b)
    if na != nb:
        raise RecordError(f"{args.a} is a {na} register and {args.b} is a {nb} register")
    only_a = sorted(k for k in a if k not in b)
    only_b = sorted(k for k in b if k not in a)
    differing = []
    for k in sorted(set(a) & set(b)):
        if a[k] != b[k]:
            fields = sorted(f for f in set(a[k]) | set(b[k]) if a[k].get(f) != b[k].get(f))
            differing.append({"id": k, "fields": {f: {"a": a[k].get(f), "b": b[k].get(f)} for f in fields}})
    return {"register": na, "a": args.a, "b": args.b, "only_in_a": only_a, "only_in_b": only_b,
            "differing": differing, "identical": not (only_a or only_b or differing)}


def cmd_merge(args) -> dict:
    """Fold a sync-conflict copy of a register back into the main file."""
    root = root_of(args.root)
    require_writable(root, argparse.Namespace(dry_run=args.dry_run, approved_by=args.approved_by,
                                              ignore_conflicts=True))
    today = today_from(args)
    copy = Path(args.copy)
    copy = copy if copy.is_absolute() else root / copy
    if not copy.is_file():
        raise RecordError(f"conflict copy not found: {copy}")
    with copy.open(encoding="utf-8") as fh:
        other = json.load(fh)
    name = next((n for n in REGISTERS if isinstance(other.get(n), list)), None)
    if not name:
        raise RecordError(f"{copy.name} is not a register file")
    main = load(root, name)
    by_id = {e.get("id"): i for i, e in enumerate(main[name]) if isinstance(e, dict)}
    taken = set(by_id) | {e.get("id") for e in other[name] if isinstance(e, dict)} | archived_ids(root)
    resolve = {}
    for item in args.resolve or []:
        eid, _, side = item.partition("=")
        if side not in ("main", "copy"):
            raise RecordError(f"--resolve needs id=main or id=copy, got {item!r}")
        resolve[eid] = side
    added, replaced, collisions, unresolved = [], [], [], []
    merged = list(main[name])
    for e in other[name]:
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        if eid not in by_id:
            merged.append(e)
            added.append(eid)
            continue
        mine = main[name][by_id[eid]]
        if mine == e:
            continue
        if mine.get("created") != e.get("created"):
            year = int(str(e.get("created") or today.isoformat())[:4])
            new_id = next_id([{"id": t} for t in taken if t], name, year)
            taken.add(new_id)
            moved = dict(e, id=new_id, notes=(e.get("notes") or "") + f" (renumbered from {eid} when merging {copy.name})")
            merged.append(moved)
            collisions.append({"id": eid, "copy_entry_renumbered_to": new_id, "title": e.get("title")})
            continue
        side = resolve.get(eid)
        if side is None:
            if (e.get("updated") or "") > (mine.get("updated") or ""):
                side = "copy"
            elif (e.get("updated") or "") < (mine.get("updated") or ""):
                side = "main"
        if side is None:
            fields = sorted(f for f in set(mine) | set(e) if mine.get(f) != e.get(f))
            unresolved.append({"id": eid, "fields": {f: {"main": mine.get(f), "copy": e.get(f)} for f in fields}})
            continue
        if side == "copy":
            merged[by_id[eid]] = e
            replaced.append(eid)
    try:
        copy_label = copy.resolve().relative_to(root).as_posix()
    except ValueError:
        copy_label = str(copy)
    result = {"register": name, "copy": copy_label,
              "added_from_copy": added, "replaced_by_newer_copy": replaced,
              "id_collisions": collisions, "unresolved": unresolved,
              "summary": f"merge {copy.name} into {REGISTERS[name].as_posix()}: {len(added)} added, "
                         f"{len(replaced)} updated, {len(collisions)} renumbered"}
    if collisions:
        result["note"] = ("renumbered entries may be referenced by the other register; "
                          "check document 'obligations' lists and obligation 'source' fields")
    if unresolved:
        result["ok"] = False
        result["errors"] = ["entries changed on both sides on the same day; ask which version to keep "
                            "and pass --resolve <id>=main or --resolve <id>=copy"]
        return result
    if args.dry_run:
        result["dry_run"] = True
        result["note"] = (result.get("note", "") + " nothing written; show this and wait for a yes").strip()
        return result
    result["backup"] = backup(root, name)
    main[name] = merged
    atomic_write_json(root / REGISTERS[name], main)
    hist = root / "registers" / ".history"
    hist.mkdir(parents=True, exist_ok=True)
    parked = hist / f"conflict-{datetime.now().strftime('%Y%m%dT%H%M%S')}-{copy.name}"
    shutil.move(str(copy), parked)
    result["conflict_copy_moved_to"] = parked.relative_to(root).as_posix()
    append_log(root, today, args.approved_by.strip(), [result["summary"]])
    return result


def cmd_archive(args) -> dict:
    root = root_of(args.root)
    require_writable(root, args)
    today = today_from(args)
    before = dates.parse_date(args.before).isoformat()
    data = load(root, "obligations")
    keep, move = [], {}
    for o in data["obligations"]:
        when = isinstance(o, dict) and (o.get("done_date") or o.get("do_by") or o.get("due_date"))
        if isinstance(o, dict) and o.get("status") in CLOSED and is_date(when) and when < before:
            move.setdefault(when[:4], []).append(o)
        else:
            keep.append(o)
    total = sum(len(v) for v in move.values())
    plan = {y: [o["id"] for o in v] for y, v in sorted(move.items())}
    result = {"before": before, "move": plan, "count": total,
              "summary": f"archive {total} closed obligation(s) dated before {before}"}
    if args.dry_run or not total:
        result["dry_run"] = bool(args.dry_run)
        if not total:
            result["note"] = "nothing to archive"
        return result
    result["backup"] = backup(root, "obligations")
    for year, items in move.items():
        path = root / "archive" / f"obligations-{year}.json"
        arch = empty_register("obligations")
        if path.exists():
            with path.open(encoding="utf-8") as fh:
                arch = json.load(fh)
        arch["obligations"].extend(items)
        atomic_write_json(path, arch)
    data["obligations"] = keep
    atomic_write_json(root / REGISTERS["obligations"], data)
    append_log(root, today, args.approved_by.strip(),
               [f"{result['summary']} into archive/: " + "; ".join(f"{y}: {', '.join(ids)}" for y, ids in plan.items())])
    return result


MIGRATIONS: dict[int, callable] = {
    # schema_version N -> function(data, name) returning data at version N + 1
}


def cmd_migrate(args) -> dict:
    root = root_of(args.root)
    require_writable(root, args)
    today = today_from(args)
    report = []
    for name in REGISTERS:
        data = load(root, name)
        sv = data.get("schema_version")
        if isinstance(sv, int) and sv > SCHEMA_VERSION:
            raise RecordError(f"{name} is at schema {sv}, newer than this plugin ({SCHEMA_VERSION}); "
                              "update the plugin instead")
        steps = []
        if sv is None:
            data = {"schema_version": 1, **{k: v for k, v in data.items() if k != "schema_version"}}
            steps.append("added schema_version 1")
            sv = 1
        while sv < SCHEMA_VERSION:
            data = MIGRATIONS[sv](data, name)
            steps.append(f"{sv} → {sv + 1}")
            sv += 1
            data["schema_version"] = sv
        report.append({"register": name, "steps": steps, "data": data})
    changed = [r for r in report if r["steps"]]
    result = {"changes": [{"register": r["register"], "steps": r["steps"]} for r in report],
              "summary": "; ".join(f"migrate {r['register']}: {', '.join(r['steps'])}" for r in changed)
              or "already at the current schema"}
    if args.dry_run or not changed:
        result["dry_run"] = bool(args.dry_run)
        return result
    for r in changed:
        backup(root, r["register"])
        atomic_write_json(root / REGISTERS[r["register"]], r["data"])
    append_log(root, today, args.approved_by.strip(), [result["summary"]])
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="record.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp, root=True, write=False, pack=False):
        if root:
            sp.add_argument("root", help="the household folder")
        sp.add_argument("--today", help="today's date from the session, YYYY-MM-DD")
        if write:
            sp.add_argument("--approved-by", help="who approved this change, as they said it")
            sp.add_argument("--dry-run", action="store_true", help="show what would be written")
            sp.add_argument("--ignore-conflicts", action="store_true", help=argparse.SUPPRESS)
        if pack:
            sp.add_argument("--country", help="country pack code, e.g. PL")
            sp.add_argument("--pack", help="path to a country pack JSON file")
        return sp

    s = sub.add_parser("locate", help="find the household folder")
    s.add_argument("--start", help="folder to start from; default the current folder")
    s.set_defaults(func=cmd_locate)

    s = common(sub.add_parser("set-pointer", help="remember the household folder on this machine"), write=True)
    s.set_defaults(func=cmd_set_pointer)

    s = common(sub.add_parser("init", help="create an empty record"), write=True)
    s.set_defaults(func=cmd_init)

    s = common(sub.add_parser("validate", help="check both registers"))
    s.add_argument("--no-files", action="store_true", help="skip checking that filed originals exist")
    s.set_defaults(func=cmd_validate)

    s = common(sub.add_parser("next-id", help="next free id"))
    s.add_argument("--kind", choices=["doc", "ob"], required=True)
    s.add_argument("--year", type=int)
    s.set_defaults(func=cmd_next_id)

    s = common(sub.add_parser("add", help="add one entry"), write=True, pack=True)
    s.add_argument("--register", choices=list(REGISTERS), required=True)
    s.add_argument("--json", help="the entry as a JSON object")
    s.add_argument("--file", help="a file holding the entry as JSON, or - for stdin")
    s.add_argument("--original", help="documents only: the original file to copy into documents/YYYY/")
    s.set_defaults(func=cmd_add)

    s = common(sub.add_parser("update", help="change fields of one entry"), write=True, pack=True)
    s.add_argument("--id", required=True)
    s.add_argument("--set", action="append", help="field=value; value is JSON when it parses")
    s.set_defaults(func=cmd_update)

    s = common(sub.add_parser("complete", help="close an obligation and add its next occurrence"),
               write=True, pack=True)
    s.add_argument("--id", required=True)
    s.add_argument("--done-date")
    s.add_argument("--status", choices=["done", "lapsed", "cancelled"], default="done")
    s.add_argument("--no-next", action="store_true", help="do not add the next occurrence")
    s.set_defaults(func=cmd_complete)

    s = common(sub.add_parser("due", help="open obligations by urgency"), pack=True)
    s.add_argument("--horizon", type=int, default=90, help="days ahead to list; default 90")
    s.set_defaults(func=cmd_due)

    s = common(sub.add_parser("find", help="search documents and obligations"))
    s.add_argument("--query", required=True)
    s.add_argument("--register", choices=list(REGISTERS))
    s.add_argument("--type")
    s.add_argument("--category")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_find)

    s = common(sub.add_parser("show", help="one entry by id"))
    s.add_argument("--id", required=True)
    s.set_defaults(func=cmd_show)

    s = common(sub.add_parser("conflicts", help="list sync-conflict copies"))
    s.set_defaults(func=cmd_conflicts)

    s = sub.add_parser("diff", help="compare two register files by id")
    s.add_argument("a")
    s.add_argument("b")
    s.set_defaults(func=cmd_diff)

    s = common(sub.add_parser("merge", help="fold a sync-conflict copy back into its register"), write=True)
    s.add_argument("--copy", required=True, help="the conflict copy, relative to the household folder")
    s.add_argument("--resolve", action="append", help="id=main or id=copy for an entry changed on both sides")
    s.set_defaults(func=cmd_merge)

    s = common(sub.add_parser("archive", help="move closed obligations to archive/"), write=True)
    s.add_argument("--before", required=True, help="archive closed entries dated before this day")
    s.set_defaults(func=cmd_archive)

    s = common(sub.add_parser("migrate", help="bring registers to the current schema"), write=True)
    s.set_defaults(func=cmd_migrate)
    return p


def emit(obj: dict, code: int = 0) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    obj.setdefault("ok", code == 0)
    obj.setdefault("calculated_by", f"record.py {VERSION}")
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    return code


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = args.func(args)
    except (RecordError, dates.InputError) as exc:
        return emit({"ok": False, "errors": [str(exc)]}, 1)
    return emit(result, 0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    sys.exit(main())
