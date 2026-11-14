#!/usr/bin/env python3
"""The household record for HouseholdBot.

Reads, checks and writes the two registers of a household folder:
registers/documents.json and registers/obligations.json. Standard library
only. Every command prints one JSON object.

Every write has two steps. A writing command (init, add, update, complete,
merge, archive, migrate, save, export, set-pointer) only previews: it checks
the change, stores exactly that change in registers/.pending/ and prints the
preview with a confirm token. After the household member says yes,
`commit <folder> --confirm TOKEN --approved-by NAME` applies the stored change
and nothing else; it refuses a token that is unknown, older than 30 minutes,
or whose files changed since the preview. The name is recorded in
log/decisions.md as the member gave it; the script cannot verify who is
typing. Every write keeps a copy of the previous file in registers/.history/
and refuses to run while sync-conflict copies of a register exist.

Dates, amounts and log lines follow the household's language: the
`Language` line of household-profile.md (English or Polish), English when it
is not set, or --lang to override.

Examples:
  python3 record.py locate
  python3 record.py init ./household --lang pl --profile-file - < profile.md
  python3 record.py commit ./household --confirm 3f9a1c0d2b7e4a65 --approved-by Anna
  python3 record.py validate ./household
  python3 record.py due ./household --today 2026-11-13 --country PL
  python3 record.py find ./household --query "polisa OC"
  python3 record.py add ./household --register obligations --file - --country PL < entry
  python3 record.py save ./household --to briefs/2026-W46.md --file - < brief.md
  python3 record.py export ./household --ics --country PL
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True  # leave no __pycache__ inside the plugin folder
import dates  # noqa: E402

VERSION = "1.2.1"
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
CONFIG_DIR = POINTER.parent
HISTORY_KEEP = 20
PENDING = Path("registers/.pending")
PENDING_TTL_SECONDS = 30 * 60
TOKEN_RE = re.compile(r"^[0-9a-f]{16}$")
# Stands for the approver's name inside a previewed register (chores plans keep it);
# commit puts the name in its place.
APPROVER = "⁣approver⁣"
SAVE_FOLDERS = ("briefs", "reviews", "lists", "packs", "skills", "exports", "drafts")
SAVE_SUFFIXES = (".md", ".html", ".ics", ".json", ".txt", ".csv")
HTML_FORBIDDEN = re.compile(
    r"<\s*(script|iframe|object|embed|form|link|img|base|svg)\b|@import|url\s*\(|"
    r"\bon[a-z]+\s*=|javascript:|https?://|www\.", re.I)
# A saved page declares its encoding and a viewport (the dashboard template has both);
# any other <meta>, such as http-equiv="refresh", is refused.
META_TAG = re.compile(r"<\s*meta\b[^>]*>", re.I)
META_ALLOWED = re.compile(
    r"<\s*meta\s+(?:charset\s*=\s*[\"']?[\w-]+[\"']?"
    r"|name\s*=\s*[\"']viewport[\"']\s+content\s*=\s*[\"'][\w\s=.,-]*[\"']"
    r"|content\s*=\s*[\"'][\w\s=.,-]*[\"']\s+name\s*=\s*[\"']viewport[\"'])\s*/?\s*>", re.I)

CATEGORIES = ["home", "vehicle", "money", "tax", "insurance", "utilities", "health",
              "children", "identity", "work", "daily", "other"]
KINDS = ["payment", "renewal", "filing", "response", "appointment", "expiry", "task"]
OB_STATUS = ["open", "done", "cancelled", "lapsed"]
DOC_STATUS = ["filed", "action-needed", "superseded", "disposed"]
PROVENANCE = ["stated in document", "calculated from document", "country pack rule — verify",
              "household pack — verify", "model calculation — verify", "told by household member"]
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
    "notice": "obj?", "transit_buffer_days": "int?", "source": "obj?", "provenance": "provenance",
    "law": "str?", "rule": "str?", "status": "ob_status", "done_date": "date?", "notes": "str",
    "created": "date!", "updated": "date!",
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
                    "currency": None, "auto_renews": None, "notice": None,
                    "transit_buffer_days": None, "source": None,
                    "law": None, "rule": None, "status": "open", "done_date": None, "notes": ""},
}
CONFLICT_PATTERNS = [
    re.compile(r"conflict", re.I),                                   # Dropbox, Nextcloud, Syncthing
    re.compile(r"^(documents|obligations|chores|household-profile) \(\d+\)\.(json|md)$"),   # Google Drive
    re.compile(r"^(documents|obligations|chores|household-profile) \d+\.(json|md)$"),       # iCloud
    re.compile(r"^(documents|obligations|chores|household-profile)-[A-Za-z0-9][A-Za-z0-9-]*\.(json|md)$"),  # OneDrive
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


LANG_LINE = re.compile(r"^\s*-\s*\*\*(?:Language|Język)\s*:\*\*\s*(.+?)\s*$", re.I | re.M)
LANG_WORDS = {"pl": ("pl", "polski", "polish", "po polsku"), "en": ("en", "english", "angielski")}


def household_language(root: Path | None) -> str:
    """The household's language from its profile; English when unset or unknown."""
    if root is None or not (root / PROFILE).exists():
        return dates.DEFAULT_LANG
    m = LANG_LINE.search((root / PROFILE).read_text(encoding="utf-8"))
    if not m:
        return dates.DEFAULT_LANG
    value = m.group(1).strip().lower()
    marked = re.match(r"\[default\s*[—–-]\s*([a-z]{2})\b", value)
    if marked:
        return marked.group(1)
    if value.startswith("[placeholder"):
        return dates.DEFAULT_LANG
    for code, words in LANG_WORDS.items():
        if any(re.search(rf"(?<![a-ząćęłńóśźż]){re.escape(w)}(?![a-ząćęłńóśźż])", value) for w in words):
            return code
    return dates.DEFAULT_LANG


def lang_for(args, root: Path | None) -> "dates.Lang":
    """--lang when given, otherwise the profile's language, otherwise English."""
    code = getattr(args, "lang", None) or household_language(root)
    return dates.load_lang(code)


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


CONTROL_RE = re.compile(r"[\x00-\x1f\x7f\u2028\u2029]")
MD_SPECIAL_RE = re.compile(r"([\\`*_\[\]<>!|])")


def md_safe(text) -> str:
    """One line of plain text for a Markdown file: control characters become spaces and
    Markdown syntax is escaped, so a title cannot add a line, a link, an image or HTML."""
    return MD_SPECIAL_RE.sub(r"\\\1", CONTROL_RE.sub(" ", str(text)))


def ensure_inside(root: Path, path: Path) -> Path:
    """Refuse a path that, followed through links and junctions, leaves the household folder."""
    real_root = root.resolve()
    real = path.resolve()
    if real != real_root and real_root not in real.parents:
        raise RecordError(f"{path.name}: the path leads outside the household folder "
                          "(a link or junction?); nothing was written")
    return path


def read_text_input(value: str) -> str:
    """Text from a file, or from standard input for '-', decoded as UTF-8.
    Text taken from documents reaches the scripts this way, never on a command line."""
    if value == "-":
        # Bytes, decoded as UTF-8: a pipe on Windows would otherwise use the ANSI code page.
        stream = getattr(sys.stdin, "buffer", None)
        return stream.read().decode("utf-8-sig") if stream is not None else sys.stdin.read()
    return Path(value).read_text(encoding="utf-8-sig")


def json_text(data: dict) -> str:
    """A register as stored: UTF-8 JSON, two-space indent, one final newline."""
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def atomic_write_json(path: Path, data: dict, root: Path | None = None) -> None:
    atomic_write_bytes(path, json_text(data).encode("utf-8"), root)


def atomic_write_bytes(path: Path, payload: bytes, root: Path | None = None) -> None:
    """Write the bytes as given (no newline translation) through a temporary file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if root is not None:
        ensure_inside(root, path)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
        for attempt in range(4):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if attempt == 3:
                    raise
                time.sleep(0.3)
    finally:
        if tmp.exists():
            tmp.unlink()


def backup_file(root: Path, rel: str) -> str | None:
    """Keep a copy of a file before it is replaced: registers/.history/<stem>-<time><suffix>,
    the newest HISTORY_KEEP per file name."""
    src = root / rel
    if not src.is_file():
        return None
    hist = root / "registers" / ".history"
    hist.mkdir(parents=True, exist_ok=True)
    ensure_inside(root, hist)
    p = Path(rel)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    dst = hist / f"{p.stem}-{stamp}{p.suffix}"
    shutil.copy2(src, dst)
    olds = sorted(hist.glob(f"{p.stem}-[0-9]*{p.suffix}"))
    for old in olds[:-HISTORY_KEEP]:
        old.unlink()
    return dst.relative_to(root).as_posix()


def backup(root: Path, name: str) -> str | None:
    return backup_file(root, REGISTERS[name].as_posix())


def append_log(root: Path, when: date, approved_by: str, lines: list[str],
               lang: "dates.Lang | None" = None) -> None:
    lang = lang or dates.load_lang(household_language(root))
    log = root / "log" / "decisions.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    ensure_inside(root, log)
    if not log.exists():
        log.write_text(lang.log("header"), encoding="utf-8")
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        for line in lines:
            fh.write(lang.log("line", date=when.isoformat(), who=md_safe(approved_by),
                              what=md_safe(line)) + "\n")


def conflicts(root: Path) -> list[str]:
    found = []
    for folder in (root, root / "registers"):
        if not folder.is_dir():
            continue
        for p in folder.iterdir():
            if not p.is_file() or p.name.endswith(".tmp"):
                continue
            if p.name in (PROFILE, "documents.json", "obligations.json", "chores.json"):
                continue
            stem_ok = p.name.startswith(("documents", "obligations", "chores", "household-profile"))
            if stem_ok and any(rx.search(p.name) for rx in CONFLICT_PATTERNS):
                found.append(p.relative_to(root).as_posix())
    return sorted(found)


ONE_CALL = ("a write has two steps: run the same command without --approved-by to get a preview "
            "and a confirm token, show the preview, and after a yes run: "
            "commit <household folder> --confirm <token> --approved-by <name>")


def check_approver(name) -> str:
    who = (name or "").strip()
    if not who:
        raise RecordError("commit needs --approved-by NAME: the person who said yes to the preview")
    if (len(who) > 40 or CONTROL_RE.search(who) or "⁣" in who
            or any(ch in who for ch in (":", '"', "„", "”"))):
        raise RecordError("--approved-by takes the approver's name only, for example --approved-by Anna; "
                          "their words stay in the conversation")
    return who


def require_writable(root: Path, args) -> None:
    """Checks before a preview: the one-call form is refused, and so is a write while
    sync-conflict copies exist."""
    if (getattr(args, "approved_by", None) or "").strip():
        raise RecordError(ONE_CALL)
    if not getattr(args, "ignore_conflicts", False):
        found = conflicts(root)
        if found:
            raise RecordError("sync-conflict copies exist, so writing now could lose an edit: "
                              + ", ".join(found) + ". Run household-doctor first.")


# --------------------------------------------------------------------------
# Two-phase writes: a preview stores the change, commit applies exactly it
# --------------------------------------------------------------------------

class Change:
    """Every write one command would make. The preview stores it under a confirm token;
    commit applies these writes and nothing else."""

    def __init__(self, root: Path, lang: "dates.Lang", command: str, ignore_conflicts: bool = False):
        self.root = root.resolve()
        self.lang = lang
        self.command = command
        self.ignore_conflicts = ignore_conflicts
        self.ops: list[dict] = []
        self.lines: list[str] = []     # log lines, also the preview
        self.notes: list[str] = []     # preview lines that are not logged

    def _rel(self, rel) -> str:
        rel = Path(str(rel).replace("\\", "/")).as_posix()
        ensure_inside(self.root, self.root / rel)
        return rel

    def write_text(self, rel, text: str, backup: bool = False, new: bool = False) -> None:
        rel = self._rel(rel)
        p = self.root / rel
        if new and p.exists():
            raise RecordError(f"{rel} already exists")
        self.ops.append({"op": "write", "path": rel, "text": text,
                         "before": sha256_of(p) if p.is_file() else None,
                         "backup": bool(backup) and p.is_file()})

    def write_json(self, rel, data: dict, backup: bool = True) -> None:
        self.write_text(rel, json_text(data), backup=backup)

    def copy(self, src: Path, rel) -> None:
        rel = self._rel(rel)
        if (self.root / rel).exists():
            raise RecordError(f"{rel} already exists")
        self.ops.append({"op": "copy", "src": str(src), "src_sha256": sha256_of(src), "path": rel,
                         "before": None})

    def move(self, rel, to) -> None:
        rel, to = self._rel(rel), self._rel(to)
        self.ops.append({"op": "move", "path": rel, "to": to, "before": sha256_of(self.root / rel)})

    def mkdir(self, rel) -> None:
        self.ops.append({"op": "mkdir", "path": self._rel(rel)})

    def pointer(self) -> None:
        self.ops.append({"op": "pointer", "text": str(self.root) + "\n"})

    def log(self, *lines: str) -> None:
        self.lines.extend(line for line in lines if line)

    def files(self) -> list[str]:
        out = []
        for op in self.ops:
            if op["op"] in ("write", "copy"):
                out.append(op["path"])
            elif op["op"] == "move":
                out.append(f"{op['path']} → {op['to']}")
            elif op["op"] == "pointer":
                out.append(str(POINTER))
        if self.lines:
            out.append("log/decisions.md")
        return out


def pending_dir(root: Path) -> Path:
    """Previews wait in the record's registers/.pending/; before a record exists (init),
    in the plugin's configuration folder on this machine."""
    if (root / "registers").is_dir():
        return root / PENDING
    return CONFIG_DIR / "pending"


def pending_digest(body: dict) -> str:
    canonical = json.dumps({k: v for k, v in body.items() if k != "token"},
                           sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def sweep_pending(folder: Path) -> None:
    """Remove previews older than the time a confirm token lives."""
    now = time.time()
    for p in folder.glob("*.json"):
        try:
            created = float(json.loads(p.read_text(encoding="utf-8")).get("created") or 0)
        except (OSError, ValueError, AttributeError):
            created = 0.0
        if now - created > PENDING_TTL_SECONDS:
            try:
                p.unlink()
            except OSError:
                pass


def inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def store_pending(change: Change, result: dict) -> tuple[str, str]:
    folder = pending_dir(change.root)
    folder.mkdir(parents=True, exist_ok=True)
    in_record = inside(change.root, folder)
    if in_record:
        ensure_inside(change.root, folder)
    sweep_pending(folder)
    created = time.time()
    body = {"version": 1, "command": change.command, "root": str(change.root),
            "lang": change.lang.code, "created": created,
            "ignore_conflicts": change.ignore_conflicts, "ops": change.ops,
            "lines": change.lines, "result": result}
    token = pending_digest(body)
    body["token"] = token
    atomic_write_bytes(folder / f"{token}.json", json_text(body).encode("utf-8"),
                       change.root if in_record else None)
    expires = datetime.fromtimestamp(created + PENDING_TTL_SECONDS).isoformat(timespec="minutes")
    return token, expires


def finish(change: Change, args, result: dict) -> dict:
    """End a writing command: store the change under a confirm token and return the
    preview; with --dry-run only show it."""
    if (getattr(args, "approved_by", None) or "").strip():
        raise RecordError(ONE_CALL)
    result["preview"] = list(change.lines) + list(change.notes)
    result["files"] = change.files()
    if getattr(args, "dry_run", False):
        result["dry_run"] = True
        result["note"] = ("nothing written and no token issued; run without --dry-run for a preview "
                          "the household can approve")
        return result
    stored = {k: v for k, v in result.items() if k not in ("preview", "files")}
    token, expires = store_pending(change, stored)
    result.update({
        "confirm": token,
        "expires": expires,
        "next": (f"show the preview; after a yes: commit \"{change.root}\" --confirm {token} "
                 "--approved-by <name>"),
        "note": "nothing written yet",
    })
    return result


def find_pending(root: Path, token: str) -> Path:
    for folder in (root / PENDING, CONFIG_DIR / "pending"):
        p = folder / f"{token}.json"
        if p.is_file():
            return p
    raise RecordError("unknown confirm token: its preview was committed, expired or never made; run the "
                      "command again without --approved-by and show the new preview")


def verify_ops(root: Path, ops: list) -> list[str]:
    """Paths whose state differs from the preview."""
    stale = []
    for op in ops:
        kind = op.get("op")
        if kind in ("write", "move"):
            p = root / op["path"]
            now = sha256_of(p) if p.is_file() else None
            if now != op.get("before"):
                stale.append(op["path"])
        if kind == "move" and (root / op["to"]).exists():
            stale.append(op["to"])
        if kind == "copy":
            src = Path(op["src"])
            if not src.is_file() or sha256_of(src) != op.get("src_sha256"):
                stale.append(src.name)
            if (root / op["path"]).exists():
                stale.append(op["path"])
    return stale


def apply_ops(root: Path, ops: list, who: str) -> tuple[list[str], list[str]]:
    written, backups = [], []
    marker = json.dumps(APPROVER, ensure_ascii=False)
    name = json.dumps(who, ensure_ascii=False)
    for op in ops:
        kind = op.get("op")
        if kind == "mkdir":
            target = root / op["path"]
            target.mkdir(parents=True, exist_ok=True)
            ensure_inside(root, target)
        elif kind == "write":
            if op.get("backup"):
                saved = backup_file(root, op["path"])
                if saved:
                    backups.append(saved)
            atomic_write_bytes(root / op["path"], op["text"].replace(marker, name).encode("utf-8"), root)
            written.append(op["path"])
        elif kind == "copy":
            target = root / op["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            ensure_inside(root, target.parent)
            with open(op["src"], "rb") as fin, open(target, "xb") as fout:
                shutil.copyfileobj(fin, fout)
            shutil.copystat(op["src"], target)
            written.append(op["path"])
        elif kind == "move":
            dest = root / op["to"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            ensure_inside(root, dest.parent)
            shutil.move(str(root / op["path"]), str(dest))
            written.append(op["to"])
        elif kind == "pointer":
            POINTER.parent.mkdir(parents=True, exist_ok=True)
            POINTER.write_text(op["text"], encoding="utf-8")
            written.append(str(POINTER))
        else:
            raise RecordError(f"the stored preview holds an unknown step {kind!r}; nothing was written")
    return written, backups


def cmd_commit(args) -> dict:
    """Apply a previewed change after the household member said yes."""
    root = Path(args.root).expanduser().resolve()
    token = (args.confirm or "").strip().lower()
    if not TOKEN_RE.match(token):
        raise RecordError("--confirm takes the 16-character token from the preview")
    who = check_approver(args.approved_by)
    path = find_pending(root, token)
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise RecordError("the stored preview cannot be read; run the command again for a new preview")
    if body.get("token") != token or pending_digest(body) != token:
        raise RecordError("the stored preview does not match its token; run the command again "
                          "and show the new preview")
    if Path(body.get("root", "")).resolve() != root:
        raise RecordError("this token belongs to another household folder")
    age = time.time() - float(body.get("created") or 0)
    if age > PENDING_TTL_SECONDS or age < -300:
        path.unlink()
        raise RecordError("the preview expired (a token lives 30 minutes); run the command again "
                          "and show the new preview")
    if not body.get("ignore_conflicts") and root.is_dir():
        found = conflicts(root)
        if found:
            raise RecordError("sync-conflict copies exist, so writing now could lose an edit: "
                              + ", ".join(found) + ". Run household-doctor first.")
    ops = body.get("ops") or []
    stale = verify_ops(root, ops)
    if stale:
        raise RecordError("the record changed since the preview (" + ", ".join(stale) + "); run the "
                          "command again and show the new preview")
    written, backups = apply_ops(root, ops, who)
    lines = body.get("lines") or []
    if lines:
        append_log(root, today_from(args), who, lines, dates.load_lang(body.get("lang")))
    path.unlink()
    out = dict(body.get("result") or {})
    out.update({"committed": token, "command": body.get("command"), "approved_by": who,
                "written": written, "backups": backups, "log": lines})
    return out


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


def iban_valid(s: str) -> bool:
    s = s.upper()
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", s):
        return False
    return int("".join(str(int(ch, 36)) for ch in s[4:] + s[:4])) % 97 == 1


def nip_valid(digits: str) -> bool:
    w = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    total = sum(int(a) * b for a, b in zip(digits[:9], w)) % 11
    return total != 10 and total == int(digits[9])


NI_RE = re.compile(r"(?<![A-Z0-9])([A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D](?![A-Z0-9])")
NI_NOT_ISSUED = {"BG", "GB", "KN", "NK", "NT", "TN", "ZZ"}
SORT_ACCOUNT_RE = re.compile(r"(?<!\d)\d{2}[-\s]\d{2}[-\s]\d{2}(?!\d)\D{0,30}?(?<!\d)\d{8}(?!\d)")
# IBAN lengths by country (ISO 13616 registry), so prose that happens to pass mod 97 is not flagged.
IBAN_LENGTHS = {"AD": 24, "AT": 20, "BE": 16, "BG": 22, "CH": 21, "CY": 28, "CZ": 24, "DE": 22, "DK": 18,
                "EE": 20, "ES": 24, "FI": 18, "FR": 27, "GB": 22, "GI": 23, "GR": 27, "HR": 21, "HU": 28,
                "IE": 22, "IS": 26, "IT": 27, "LI": 21, "LT": 20, "LU": 20, "LV": 21, "MC": 27, "MT": 31,
                "NL": 18, "NO": 15, "PL": 28, "PT": 25, "RO": 24, "SE": 24, "SI": 19, "SK": 24, "SM": 27,
                "UA": 29}
# Electronic form (no spaces) or print form (groups of four separated by one space).
IBAN_FORM_RE = re.compile(r"(?<![A-Za-z0-9])([A-Z]{2}\d{2}(?:[A-Z0-9]{11,30}|(?: [A-Z0-9]{4}){2,7}(?: [A-Z0-9]{1,4})?))"
                          r"(?![A-Za-z0-9])")


def find_ibans(text: str) -> list[tuple[int, int, str]]:
    """(start, end, compact) of every valid IBAN written in electronic or print form."""
    out = []
    for m in IBAN_FORM_RE.finditer(text or ""):
        compact = m.group(1).replace(" ", "")
        if IBAN_LENGTHS.get(compact[:2]) == len(compact) and iban_valid(compact):
            out.append((m.start(1), m.end(1), compact))
    return out
CARD_RE = re.compile(r"(?<!\d)(?:\d{4}[ -]){3}\d{1,7}(?!\d)|(?<!\d)\d{13,19}(?!\d)")


def identifier_findings(obj, path: str = "") -> list[tuple[str, str]]:
    """(field path, kind) for every value that looks like a personal identifier or a secret."""
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += identifier_findings(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += identifier_findings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        compact = re.sub(r"[\s-]", "", obj)
        if any(pesel_valid(m.group()) for m in re.finditer(r"(?<!\d)\d{11}(?!\d)", obj)):
            out.append((path, "a PESEL number"))
        account = any(nrb_valid(m.group()) for m in re.finditer(r"(?<!\d)\d{26}(?!\d)", compact))
        account = account or bool(find_ibans(obj))
        if account:
            out.append((path, "a full bank account number"))
        if SORT_ACCOUNT_RE.search(obj):
            out.append((path, "a sort code with an account number"))
        if any(m.group(1) not in NI_NOT_ISSUED for m in NI_RE.finditer(obj.upper())):
            out.append((path, "a National Insurance number"))
        for m in re.finditer(r"NIP\W{0,3}((?:\d[\s-]?){9}\d)", obj, re.I):
            if nip_valid(re.sub(r"\D", "", m.group(1))):
                out.append((path, "a NIP tax number"))
                break
        for m in CARD_RE.finditer(obj):
            digits = re.sub(r"\D", "", m.group())
            if 13 <= len(digits) <= 19 and digits[0] in "23456" and luhn_valid(digits):
                out.append((path, "a payment card number"))
                break
        if SECRET_WORDS.search(obj) and re.search(r"[:=]\s*\S", obj):
            out.append((path, "a password, PIN or code"))
    return out


def identifier_warnings(obj, path: str = "") -> list[str]:
    """Flag stored values that look like personal identifiers, without echoing them."""
    return [f"{p}: looks like {kind}" for p, kind in identifier_findings(obj, path)]


def identifier_errors(obj, path: str = "") -> list[str]:
    """Refuse to write a value that looks like an identifier or a secret, without echoing it."""
    return [f"{p}: looks like {kind}; the record keeps only where it is (\"see page 2\") "
            "or, for an account to pay into, its last four digits" for p, kind in identifier_findings(obj, path)]


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


def describe_entry(name: str, e: dict, lang: "dates.Lang | None" = None) -> str:
    lang = lang or dates.load_lang(dates.DEFAULT_LANG)
    title = lang.quote(e.get("title") or "")
    if name == "documents":
        return f"{e['id']} {title}"
    when = e.get("do_by") or e.get("due_date")
    when_txt = lang.date(date.fromisoformat(when)) if is_date(when) else lang.log("no_date")
    money = ""
    if e.get("amount") and e.get("currency"):
        try:
            money = ", " + lang.amount(e["amount"], e["currency"])
        except dates.InputError:
            money = f", {e['currency']} {e['amount']}"
    return f"{e['id']} {title} ({lang.log('do_by')} {when_txt}{money})"


def register_label(name: str, lang: "dates.Lang") -> str:
    return lang.log(f"register_{name}")


def transit_of(entry: dict) -> int:
    """Days allowed for delivery: the obligation's own value, else its notice's, else none."""
    for value in (entry.get("transit_buffer_days"), (entry.get("notice") or {}).get("transit_buffer_days")):
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value
    return 0


def pack_or_none(args):
    if getattr(args, "country", None) or getattr(args, "pack", None):
        return dates.load_pack(getattr(args, "country", None), getattr(args, "pack", None))
    return None


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def plugin_root() -> Path | None:
    """The plugin folder this script belongs to, when it runs from a skill's copy."""
    for p in HERE.parents:
        if (p / ".claude-plugin" / "plugin.json").exists():
            return p
    return None


def inside_plugin(path: Path) -> bool:
    """True when a search would start in the plugin's own folders, not the household's."""
    root = plugin_root()
    if root is None:
        return False
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def cmd_locate(args) -> dict:
    start = Path(args.start or os.getcwd()).expanduser().resolve()
    starts = [start]
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project and Path(project).resolve() != start:
        starts.append(Path(project).resolve())
    for s in starts:
        candidates = [s] + ([p for p in sorted(s.iterdir()) if p.is_dir()] if s.is_dir() else [])
        for c in candidates:
            if (c / PROFILE).exists():
                return {"found": True, "root": str(c), "how": "working folder"}
    result = {"found": False, "searched": str(start), "pointer": str(POINTER)}
    if POINTER.exists():
        lines = POINTER.read_text(encoding="utf-8").strip().splitlines()
        target = Path(lines[0].strip()).expanduser() if lines else None
        if target is not None and (target / PROFILE).exists():
            return {"found": True, "root": str(target), "how": f"pointer {POINTER}"}
        result.update({"pointer_target": str(target) if target else "",
                       "note": "the pointer names a folder without household-profile.md"})
    if inside_plugin(start):
        result["hint"] = ("the search started inside the plugin's own folder; run locate with "
                          "--start <the session's working folder> before deciding the household "
                          "is not set up")
    return result


def cmd_set_pointer(args) -> dict:
    root = root_of(args.root)
    if not (root / PROFILE).exists():
        raise RecordError(f"{root} has no {PROFILE}")
    if (args.approved_by or "").strip():
        raise RecordError(ONE_CALL)
    lang = lang_for(args, root)
    change = Change(root, lang, "set-pointer", ignore_conflicts=True)
    change.pointer()
    change.notes.append(f"{POINTER} → {root}")
    return finish(change, args, {"would_write": str(POINTER), "content": str(root)})


def cmd_init(args) -> dict:
    root = Path(args.root).expanduser().resolve()
    existing = [str(REGISTERS[n].as_posix()) for n in REGISTERS if (root / REGISTERS[n]).exists()]
    if existing:
        raise RecordError(f"a record already exists here ({', '.join(existing)}); "
                          "nothing was changed. Use validate or household-doctor.")
    require_writable(root, args)
    plan = [p.as_posix() for p in REGISTERS.values()] + [
        "registers/README.md", "log/decisions.md", "documents/", "briefs/", "inbox/"]
    lang = lang_for(args, root)
    change = Change(root, lang, "init")
    change.mkdir(".")
    for name in REGISTERS:
        change.write_json(REGISTERS[name], empty_register(name), backup=False)
    readme_src = HERE.parent / "templates" / lang.code / "registers-README.md"
    if not readme_src.exists():
        readme_src = HERE.parent / "templates" / dates.DEFAULT_LANG / "registers-README.md"
    readme = readme_src.read_text(encoding="utf-8") if readme_src.exists() else REGISTERS_README
    change.write_text("registers/README.md", readme)
    for d in ("documents", "briefs", "inbox"):
        change.mkdir(d)
    if getattr(args, "profile_file", None):
        # The approved profile goes in the same change, so one yes creates the whole record.
        profile = read_text_input(args.profile_file)
        if (root / PROFILE).exists():
            raise RecordError(f"{PROFILE} already exists here; household-customize changes it")
        problems = identifier_errors({"profile": profile})
        if problems:
            return {"ok": False, "errors": problems}
        change.write_text(PROFILE, profile, new=True)
        plan.append(PROFILE)
    change.log(lang.log("created_record"))
    return finish(change, args, {"root": str(root), "would_create": plan, "lang": lang.code})


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


def read_entries(args) -> list[dict]:
    """One entry as a JSON object, or several entries of one register as a list."""
    if getattr(args, "json", None):
        raw = args.json
    elif getattr(args, "file", None):
        raw = read_text_input(args.file)
    else:
        raise RecordError("give the entry with --json '<object>' or --file <path> (or --file - for stdin)")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RecordError(f"entry is not valid JSON: {exc}")
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
        return value
    raise RecordError("entry must be a JSON object, or a list of objects for one register")


def prepare_entry(root: Path, name: str, raw_entry: dict, entries: list, today: date, lang, pack,
                  given_original, warnings: list, taken_files: set) -> tuple[dict, Path | None]:
    # The path of a file a document arrived in is document-derived text: it travels inside
    # the entry on standard input ("original"), never on the command line.
    source = raw_entry.pop("original", None)
    if source and given_original:
        raise RecordError("give the original once: in the entry as \"original\" or with --original")
    source = source or given_original
    entry = fill_defaults(name, raw_entry)
    normalise_amount(entry, warnings)
    original = None
    if source and name != "documents":
        raise RecordError("an original belongs to the documents register")
    if source:
        original = Path(str(source)).expanduser().resolve()
        if not original.is_file():
            raise RecordError(f"original not found: {original}")
        entry["sha256"] = sha256_of(original)
    if not entry.get("id"):
        entry["id"] = next_id(entries, name, today.year, archived_ids(root))
    entry["created"] = entry.get("created") or today.isoformat()
    entry["updated"] = today.isoformat()
    if name == "obligations" and entry.get("due_date") and not entry.get("do_by"):
        if pack:
            transit = transit_of(entry)
            planned = dates.plan_do_by(pack, dates.parse_date(entry["due_date"]), transit, lang)
            entry["do_by"], entry["do_by_note"] = planned["do_by"], planned["do_by_note"]
        else:
            warnings.append(f"{entry['id']}: do_by not given and no --country: do_by left empty")
    if name == "documents" and original is not None:
        stamp = entry.get("document_date") or entry.get("received_date") or today.isoformat()
        base = "_".join(x for x in (stamp, slug(entry.get("issuer") or "unknown"),
                                    slug(entry.get("type") or "document")) if x)
        dest_dir = root / "documents" / stamp[:4]
        suffix = original.suffix.lower()
        if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
            suffix = ""
        dest, n = dest_dir / f"{base}{suffix}", 2
        while dest.exists() or dest.relative_to(root).as_posix() in taken_files:
            dest = dest_dir / f"{base}-{n}{suffix}"
            n += 1
        entry["file"] = dest.relative_to(root).as_posix()
        taken_files.add(entry["file"])
    return entry, original


def cmd_add(args) -> dict:
    """Add one entry, or several entries of one register in one change (a JSON list)."""
    root = root_of(args.root)
    name = args.register
    require_writable(root, args)
    today = today_from(args)
    data = load(root, name)
    entries = data[name]
    raw_entries = read_entries(args)
    if args.original and len(raw_entries) > 1:
        raise RecordError("--original takes one entry; give each entry of a list its own \"original\"")
    lang = lang_for(args, root)
    pack = pack_or_none(args) if name == "obligations" else None
    change = Change(root, lang, "add", getattr(args, "ignore_conflicts", False))
    warnings: list[str] = []
    errs: list[str] = []
    added: list[dict] = []
    originals: dict[str, str] = {}
    taken_files: set = set()
    for raw in raw_entries:
        entry, original = prepare_entry(root, name, raw, entries, today, lang, pack, args.original,
                                        warnings, taken_files)
        entry_errs: list[str] = []
        validate_entries(name, [entry], entry_errs, warnings)
        if any(e.get("id") == entry["id"] for e in entries if isinstance(e, dict)):
            entry_errs.append(f"id {entry['id']} already exists")
        dup_errs, dup_warns = duplicate_warnings(name, entry, entries)
        entry_errs += dup_errs
        warnings += dup_warns
        entry_errs += identifier_errors(entry)
        added.append(entry)
        if entry_errs:
            errs += entry_errs if len(raw_entries) == 1 else [f"{entry['id']}: {m}" for m in entry_errs]
            continue
        if original is not None:
            change.copy(original, entry["file"])
            originals[entry["file"]] = str(original)
        entries.append(entry)
        change.log(lang.log("add", entry=describe_entry(name, entry, lang), register=register_label(name, lang)))
    if errs:
        out = {"ok": False, "errors": errs, "warnings": warnings}
        if len(added) == 1:
            out["entry"] = added[0]
        else:
            out["entries"] = added
        return out
    change.write_json(REGISTERS[name], data)
    result = {"register": REGISTERS[name].as_posix(), "warnings": warnings, "lang": lang.code,
              "summary": "; ".join(change.lines)}
    if len(added) == 1:
        result["entry"] = added[0]
        if originals:
            result["original_to"], result["original_source"] = next(iter(originals.items()))
    else:
        result["entries"] = added
        if originals:
            result["originals"] = originals
    return finish(change, args, result)


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
    if getattr(args, "file", None):
        try:
            given = json.loads(read_text_input(args.file))
        except json.JSONDecodeError as exc:
            raise RecordError(f"the changes are not valid JSON: {exc}")
        if not isinstance(given, dict):
            raise RecordError("the changes must be a JSON object of field: value")
        changes.update(given)
    for item in args.set or []:
        if "=" not in item:
            raise RecordError(f"--set needs field=value, got {item!r}")
        field, raw = item.split("=", 1)
        changes[field.strip()] = parse_value(raw, FIELDS[name].get(field.strip()))
    for field in changes:
        if field in ("id", "created"):
            raise RecordError(f"'{field}' cannot be changed")
    if not changes:
        raise RecordError("nothing to change; give --file - with a JSON object, or --set field=value")
    entry.update(changes)
    warnings: list[str] = []
    lang = lang_for(args, root)
    if name == "obligations" and "due_date" in changes and "do_by" not in changes:
        pack = pack_or_none(args)
        if pack and entry.get("due_date"):
            transit = transit_of(entry)
            planned = dates.plan_do_by(pack, dates.parse_date(entry["due_date"]), transit, lang)
            entry["do_by"], entry["do_by_note"] = planned["do_by"], planned["do_by_note"]
            changes["do_by"] = entry["do_by"]
        else:
            warnings.append("due_date changed but do_by was not recomputed; give --country or set do_by")
    entry["updated"] = today.isoformat()
    errs: list[str] = []
    validate_entries(name, [entry], errs, warnings)
    identifier_errs = identifier_errors(changes)
    if identifier_errs:
        return {"ok": False, "errors": identifier_errs, "warnings": warnings}
    diff = {k: {"from": before.get(k), "to": entry.get(k)} for k in changes}
    summary = lang.log("update", id=args.id, changes=", ".join(
        f"{k} → {json.dumps(entry.get(k), ensure_ascii=False)}" for k in changes))
    if errs:
        entry.clear()
        entry.update(before)
        return {"ok": False, "errors": errs, "warnings": warnings, "changes": diff}
    result = {"register": REGISTERS[name].as_posix(), "id": args.id, "changes": diff,
              "warnings": warnings, "summary": summary}
    change = Change(root, lang, "update", getattr(args, "ignore_conflicts", False))
    change.write_json(REGISTERS[name], data)
    change.log(summary)
    return finish(change, args, result)


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
    """Close one or more open obligations (--id, repeated) and add their next occurrences,
    as one change."""
    root = root_of(args.root)
    require_writable(root, args)
    today = today_from(args)
    data = load(root, "obligations")
    entries = data["obligations"]
    done_date = args.done_date or today.isoformat()
    if not is_date(done_date):
        raise RecordError(f"--done-date must be YYYY-MM-DD, got {done_date!r}")
    lang = lang_for(args, root)
    pack = pack_or_none(args)
    ids = list(dict.fromkeys(args.id))
    lines: list[str] = []
    warnings: list[str] = []
    completed = []
    for oid in ids:
        entry = find_entry(entries, oid)
        if entry.get("status") != "open":
            raise RecordError(f"{oid} is {entry.get('status')}, not open")
        changes = {"status": args.status, "done_date": done_date if args.status == "done" else None,
                   "updated": today.isoformat()}
        new_entry = None
        recurrence = entry.get("recurrence") or "none"
        if recurrence != "none" and not args.no_next:
            if not is_date(entry.get("due_date")):
                warnings.append(f"{oid}: no due_date to compute the next occurrence from")
            else:
                # --from-done: checks and services count the next one from the day they were done
                base = dates.parse_date(done_date) if args.from_done else dates.parse_date(entry["due_date"])
                anchor = None if args.from_done else series_anchor_day(entries, entry)
                nxt = dates.next_occurrence(base, recurrence, anchor)
                if nxt is None:
                    warnings.append(f"{oid}: recurrence '{recurrence}' cannot be computed; ask for the next "
                                    "date and add it with add")
                else:
                    new_entry = {k: v for k, v in entry.items()}
                    new_entry.update({
                        "id": next_id(entries, "obligations", today.year, archived_ids(root)),
                        "due_date": nxt.isoformat(), "do_by": None, "do_by_note": "",
                        "status": "open", "done_date": None,
                        "created": today.isoformat(), "updated": today.isoformat(),
                        "series": entry.get("series") or slug(entry.get("title", "series")),
                        "notes": f"next occurrence after {entry['id']}, computed from recurrence '{recurrence}'"
                                 + (" counted from the day it was done" if args.from_done else ""),
                    })
                    if entry.get("source") and (entry["source"] or {}).get("document"):
                        new_entry["provenance"] = "calculated from document"
                    if pack:
                        planned = dates.plan_do_by(pack, nxt, transit_of(entry), lang)
                        new_entry["do_by"], new_entry["do_by_note"] = planned["do_by"], planned["do_by_note"]
                    else:
                        new_entry["do_by"] = nxt.isoformat()
                        warnings.append(f"{oid}: no --country: do_by of the next occurrence equals its due_date")
                    if not entry.get("series"):
                        changes["series"] = new_entry["series"]
        if args.status == "done":
            lines.append(lang.log("complete_on", id=oid, status=lang.status(args.status),
                                  date=lang.date(dates.parse_date(done_date))))
        else:
            lines.append(lang.log("complete", id=oid, status=lang.status(args.status)))
        if new_entry:
            lines.append(lang.log("next", entry=describe_entry("obligations", new_entry, lang)))
        entry.update(changes)
        if new_entry:
            entries.append(new_entry)
        completed.append({"id": oid, "changes": changes, "next_occurrence": new_entry})
    result = {"register": REGISTERS["obligations"].as_posix(), "warnings": warnings, "summary": "; ".join(lines)}
    if len(completed) == 1:
        result.update(completed[0])
    else:
        result["completed"] = completed
    change = Change(root, lang, "complete", getattr(args, "ignore_conflicts", False))
    change.write_json(REGISTERS["obligations"], data)
    change.log(*lines)
    return finish(change, args, result)

def effective_last_day(o: dict, pack, lang: "dates.Lang", warnings: list) -> tuple[date | None, str]:
    """The last day the law gives: the stored due date, moved past a weekend or holiday when the
    entry names the pack's counting rule ("rule": "tax") and that rule moves a deadline forward."""
    due = o.get("due_date")
    if not is_date(due):
        return None, ""
    d = date.fromisoformat(due)
    rule_id = o.get("rule")
    if not rule_id:
        return d, ""
    if pack is None:
        warnings.append(f"{o.get('id')}: names the counting rule {rule_id!r}; give --country to apply it")
        return d, ""
    try:
        rule = pack.rule(rule_id)
    except dates.InputError:
        warnings.append(f"{o.get('id')}: the {pack.code} pack has no counting rule {rule_id!r}")
        return d, ""
    if rule.get("end_roll") != "forward":
        return d, ""
    reason = pack.non_business_reason(d, lang)
    if not reason:
        return d, ""
    moved = pack.roll_forward(d)
    return moved, lang.note("moved_forward", date=lang.date(d), reason=reason, new_date=lang.date(moved),
                            law=rule.get("law", rule_id))


def cmd_due(args) -> dict:
    root = root_of(args.root)
    today = today_from(args)
    pack = pack_or_none(args)
    lang = lang_for(args, root)
    data = load(root, "obligations")
    items, no_date, beyond = [], [], 0
    counts = {b[0]: 0 for b in dates.BANDS}
    warnings = []
    kinds = set(args.kind.split(",")) if getattr(args, "kind", None) else None
    categories = set(args.category.split(",")) if getattr(args, "category", None) else None
    for o in data["obligations"]:
        if not isinstance(o, dict) or o.get("status") != "open":
            continue
        if kinds and o.get("kind") not in kinds:
            continue
        if categories and o.get("category") not in categories:
            continue
        plan = o.get("do_by") or o.get("due_date")
        if not is_date(plan):
            no_date.append({"id": o.get("id"), "title": o.get("title"),
                            "note": "no usable date; ask for it"})
            continue
        computed_note = ""
        if not o.get("do_by") and pack:
            transit = transit_of(o)
            planned = dates.plan_do_by(pack, dates.parse_date(plan), transit, lang)
            plan, computed_note = planned["do_by"], "do_by computed now; not stored"
        d = date.fromisoformat(plan)
        days = (d - today).days
        due = o.get("due_date")
        last, last_note = effective_last_day(o, pack, lang, warnings)
        # "Overdue" means the last day has passed. A plan date that has passed while the
        # last day is still ahead is "now", flagged plan_passed.
        plan_passed = days < 0 and last is not None and last >= today
        b = ({"band": "now", "label": lang.band_label("now")} if plan_passed else dates.band(days, lang))
        lead = o.get("lead_time_days")
        start_now = bool(lead) and days >= 0 and days <= int(lead)
        if days >= args.horizon and not start_now:
            beyond += 1
            continue
        counts[b["band"]] += 1
        try:
            amount_text = lang.amount(o["amount"], o.get("currency")) if o.get("amount") else None
        except dates.InputError:
            amount_text = None
        row = {
            "id": o.get("id"), "title": o.get("title"), "kind": o.get("kind"),
            "category": o.get("category"), "owner": o.get("owner"),
            "counterparty": o.get("counterparty"), "amount": o.get("amount"),
            "currency": o.get("currency"), "amount_text": amount_text,
            "due_date": due, "due_text": dates.text_en(date.fromisoformat(due)) if is_date(due) else None,
            "due_local": lang.date(date.fromisoformat(due)) if is_date(due) else None,
            "do_by": plan, "do_by_text": dates.text_en(d), "do_by_local": lang.date(d),
            "days": days, "band": b["band"], "band_label": b["label"], "plan_passed": plan_passed,
            "start_now": start_now, "lead_time_days": lead,
            "recurrence": o.get("recurrence"), "series": o.get("series"),
            "provenance": o.get("provenance"), "provenance_local": lang.tag(o.get("provenance")),
            "law": o.get("law"),
            "source_document": (o.get("source") or {}).get("document"),
            "notice": o.get("notice"), "auto_renews": o.get("auto_renews"),
        }
        if last is not None:
            row["days_to_last_day"] = (last - today).days
        if last is not None and last.isoformat() != due:
            row.update({"last_day": last.isoformat(), "last_day_text": dates.text_en(last),
                        "last_day_local": lang.date(last), "last_day_note": last_note})
        if plan_passed:
            row["plan_note"] = lang.note("plan_passed", date=lang.date(d), last=lang.date(last))
        if computed_note:
            row["note"] = computed_note
        items.append(row)
    items.sort(key=lambda r: (r["do_by"], r["due_date"] or "", r["id"] or ""))
    totals: dict = {}
    for r in items:
        if r.get("amount") and r.get("currency") and MONEY_RE.match(str(r["amount"])):
            totals[r["currency"]] = totals.get(r["currency"], Decimal("0")) + Decimal(r["amount"])
    if not pack:
        warnings.append("no --country: missing do_by dates are not computed")
    return {"today": today.isoformat(), "today_source": "argument" if args.today else "system clock",
            "today_local": lang.date(today), "lang": lang.code,
            "horizon_days": args.horizon, "items": items, "no_date": no_date,
            "totals": {c: f"{v:.2f}" for c, v in sorted(totals.items())},
            "totals_text": {c: lang.amount(v, c) for c, v in sorted(totals.items())},
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
    if getattr(args, "query_file", None):
        args.query = " ".join(read_text_input(args.query_file).split())
    root = root_of(args.root)
    for name in REGISTERS:
        m = re.search(rf"\b{PREFIX[name]}-\d{{4}}-\d{{4,}}\b", args.query or "")
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
    q = [t for t in tokens(args.query or "") if t not in STOPWORDS]
    if not q and not (args.type or args.category):
        raise RecordError("give --query, or --type / --category to list every entry of that kind")
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
            if not q:
                results.append({
                    "register": name, "id": e.get("id"), "title": e.get("title"),
                    "status": e.get("status"), "score": 0, "matched": [], "file": e.get("file"),
                    "date": e.get("document_date") or e.get("do_by") or e.get("due_date"),
                    "key_facts": e.get("key_facts") if name == "documents" else None,
                })
                continue
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
    return {"query": args.query or "", "words": q, "results": results[: args.limit],
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
    listed = {(root / c).resolve() for c in conflicts(root)}
    if copy.resolve() not in listed:
        raise RecordError(f"{copy.name} is not a sync-conflict copy of a register in this household "
                          "folder; merge takes only the copies that household-doctor lists")
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
    changes: dict[str, dict] = {}
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
            changes[eid] = {f: {"main": mine.get(f), "copy": e.get(f)}
                            for f in sorted(set(mine) | set(e)) if mine.get(f) != e.get(f)}
    try:
        copy_label = copy.resolve().relative_to(root).as_posix()
    except ValueError:
        copy_label = str(copy)
    lang = lang_for(args, root)
    renumbered = {c["copy_entry_renumbered_to"] for c in collisions}
    incoming = [e for e in merged if isinstance(e, dict)
                and (e.get("id") in set(added) | set(replaced) | renumbered)]
    entry_errors: list[str] = []
    entry_warnings: list[str] = []
    validate_entries(name, incoming, entry_errors, entry_warnings)
    entry_errors += identifier_errors(incoming, "copy")
    result = {"register": name, "copy": copy_label,
              "added_from_copy": [{"id": e.get("id"), "title": e.get("title")} for e in incoming
                                  if e.get("id") in added],
              "replaced_by_newer_copy": replaced, "changes_from_copy": changes,
              "id_collisions": collisions, "unresolved": unresolved,
              "summary": lang.log("merge", copy=copy.name, register=register_label(name, lang),
                                  added=len(added), updated=len(replaced), renumbered=len(collisions))}
    if collisions:
        result["note"] = ("renumbered entries may be referenced by the other register; "
                          "check document 'obligations' lists and obligation 'source' fields")
    if entry_warnings:
        result["warnings"] = entry_warnings
    if entry_errors:
        result["ok"] = False
        result["errors"] = entry_errors
        return result
    if unresolved:
        result["ok"] = False
        result["errors"] = ["entries changed on both sides on the same day; ask which version to keep "
                            "and pass --resolve <id>=main or --resolve <id>=copy"]
        return result
    main[name] = merged
    change = Change(root, lang, "merge", ignore_conflicts=True)
    change.write_json(REGISTERS[name], main)
    parked = f"registers/.history/conflict-{datetime.now().strftime('%Y%m%dT%H%M%S')}-{copy.name}"
    change.move(copy_label, parked)
    result["conflict_copy_moves_to"] = parked
    change.log(result["summary"])
    return finish(change, args, result)


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
    lang = lang_for(args, root)
    detail = "; ".join(f"{y}: {', '.join(ids)}" for y, ids in plan.items())
    result = {"before": before, "move": plan, "count": total,
              "summary": lang.log("archive", count=total, before=lang.date(dates.parse_date(before)),
                                  detail=detail)}
    if not total:
        result["note"] = "nothing to archive"
        return result
    change = Change(root, lang, "archive", getattr(args, "ignore_conflicts", False))
    for year, items in sorted(move.items()):
        rel = f"archive/obligations-{year}.json"
        arch = empty_register("obligations")
        if (root / rel).exists():
            with (root / rel).open(encoding="utf-8") as fh:
                arch = json.load(fh)
        arch["obligations"].extend(items)
        change.write_json(rel, arch, backup=False)
    data["obligations"] = keep
    change.write_json(REGISTERS["obligations"], data)
    change.log(result["summary"])
    return finish(change, args, result)


# --------------------------------------------------------------------------
# Files the skills keep in the record: briefs, pages, lists, packs, exports
# --------------------------------------------------------------------------

MEMBERS_HEAD = re.compile(r"^##\s+(Members|Domownicy)\s*$", re.M)
LABEL_LINE = re.compile(r"^\s*-\s*\*\*(?:Label|Nazwa)\s*:\*\*\s*(.+?)\s*$", re.I | re.M)


def profile_members(root: Path) -> dict[str, str]:
    """Member name -> "adult" or "child", from the profile's members table."""
    p = root / PROFILE
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    m = MEMBERS_HEAD.search(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in text[m.end():].splitlines():
        if line.startswith("## ") or line.strip() == "---":
            if out:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not line.lstrip().startswith("|") or set(cells[0]) <= set("-: "):
            continue
        name, role = cells[0], cells[1].lower()
        if name.lower() in ("name", "imię", "imie") or name.startswith("["):
            continue
        out[name] = "child" if role.startswith(("child", "dziecko")) else "adult"
    return out


def household_label(root: Path) -> str:
    p = root / PROFILE
    m = LABEL_LINE.search(p.read_text(encoding="utf-8")) if p.exists() else None
    return m.group(1).strip() if m else root.name


def save_target(to: str) -> str:
    rel = Path((to or "").replace("\\", "/"))
    parts = rel.parts
    if not parts or rel.is_absolute() or ".." in parts or any(p.startswith(".") for p in parts):
        raise RecordError("--to takes a path inside the household folder, for example briefs/2026-W46.md")
    if rel.as_posix() != PROFILE and (parts[0] not in SAVE_FOLDERS or len(parts) < 2):
        raise RecordError("save writes into " + ", ".join(f"{f}/" for f in SAVE_FOLDERS) + f" or {PROFILE}; "
                          "registers change through add, update and complete")
    if rel.suffix.lower() not in SAVE_SUFFIXES:
        raise RecordError("save keeps " + ", ".join(SAVE_SUFFIXES) + " files")
    return rel.as_posix()


def free_name(root: Path, rel: str) -> str:
    p, n = Path(rel), 1
    target = p
    while (root / target).exists():
        n += 1
        target = p.with_name(f"{p.stem}-{n}{p.suffix}")
    return target.as_posix()


def content_problems(rel: str, text: str) -> list[str]:
    problems = identifier_errors({"text": text})
    if rel.lower().endswith(".html"):
        m = HTML_FORBIDDEN.search(text)
        if m:
            problems.append(f"the page holds {m.group(0)!r}: a saved page has no scripts, links, images, "
                            "forms, styles from outside or web addresses")
        meta = next((t for t in META_TAG.findall(text) if not META_ALLOWED.fullmatch(t)), None)
        if meta:
            problems.append(f"the page holds {meta[:60]!r}: <meta> may only declare the charset "
                            "(<meta charset=\"utf-8\">) and the viewport line")
    if rel.lower().endswith(".json"):
        try:
            json.loads(text)
        except ValueError as exc:
            problems.append(f"not valid JSON: {exc}")
    return problems


def short_diff(old: str, new: str, limit: int = 60) -> list[str]:
    lines = [ln.rstrip("\n") for ln in difflib.unified_diff(
        old.splitlines(), new.splitlines(), "before", "after", n=0, lineterm="")][2:]
    return lines[:limit] + ([f"... {len(lines) - limit} more lines"] if len(lines) > limit else [])


def cmd_save(args) -> dict:
    """Keep a file the household approved: a brief, a page, a list, a pack, a skill, an export."""
    root = root_of(args.root)
    if not (root / "registers").is_dir():
        raise RecordError("no record here: save writes into a household folder made by init")
    require_writable(root, args)
    rel = save_target(args.to)
    text = read_text_input(args.file)
    lang = lang_for(args, root)
    replaces = (root / rel).exists() and bool(args.replace)
    if (root / rel).exists() and not args.replace:
        rel = free_name(root, rel)
    problems = content_problems(rel, text)
    if problems:
        return {"ok": False, "errors": problems, "file": rel}
    change = Change(root, lang, "save", getattr(args, "ignore_conflicts", False))
    change.write_text(rel, text, backup=replaces and not rel.startswith("exports/"))
    summary = lang.log("replaced" if replaces else "saved", file=rel)
    change.log(summary)
    result = {"file": rel, "replaces": replaces, "bytes": len(text.encode("utf-8")), "summary": summary}
    if replaces:
        result["diff"] = short_diff((root / rel).read_text(encoding="utf-8", errors="replace"), text)
    return finish(change, args, result)


def ics_escape(text: str) -> str:
    return (str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n"))


def ics_fold(line: str) -> list[str]:
    """RFC 5545 3.1: lines longer than 75 octets continue on lines that start with a space;
    a UTF-8 character is never split."""
    out, current, size = [], "", 0
    for ch in line:
        width = len(ch.encode("utf-8"))
        limit = 75 if not out else 74
        if size + width > limit:
            out.append(current)
            current, size = "", 0
        current += ch
        size += width
    out.append(current)
    return [out[0]] + [" " + part for part in out[1:]]


def ics_date(iso: str) -> str:
    return iso.replace("-", "")


def ics_event(o: dict, key: str, lang: "dates.Lang", root: Path, pack, cancelled: bool,
              warnings: list) -> list[str]:
    plan = o.get("do_by") or o.get("due_date")
    start = date.fromisoformat(plan)
    updated = o.get("updated") if is_date(o.get("updated")) else plan
    if o.get("category") == "health":
        summary = lang.log("ics_appointment") + (f", {o['owner']}" if o.get("owner") else "")
    else:
        summary = o.get("title") or o.get("id")
    details = []
    last, _ = effective_last_day(o, pack, lang, warnings)
    if last is not None:
        details.append(lang.log("ics_last_day", date=lang.date(last)))
    if o.get("amount") and o.get("currency"):
        try:
            details.append(lang.amount(o["amount"], o["currency"]))
        except dates.InputError:
            pass
    if o.get("owner"):
        details.append(lang.log("ics_who", name=o["owner"]))
    if o.get("provenance") and o["provenance"] != "stated in document":
        details.append(f"({lang.tag(o['provenance'])})")
    if o.get("law") and o.get("category") != "health":
        details.append(o["law"])
    lines = [
        "BEGIN:VEVENT",
        f"UID:{o['id']}-{key}@householdbot",
        f"DTSTAMP:{ics_date(updated)}T000000Z",
        f"SEQUENCE:{int(ics_date(updated))}",
        f"DTSTART;VALUE=DATE:{ics_date(plan)}",
        f"DTEND;VALUE=DATE:{ics_date((start + timedelta(days=1)).isoformat())}",
        f"SUMMARY:{ics_escape(summary)}",
        f"DESCRIPTION:{ics_escape(' · '.join(details))}",
        "TRANSP:TRANSPARENT",
        f"STATUS:{'CANCELLED' if cancelled else 'CONFIRMED'}",
    ]
    if not cancelled:
        lead = o.get("lead_time_days")
        days = lead if isinstance(lead, int) and not isinstance(lead, bool) and lead > 0 else 1
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{ics_escape(summary)}",
                  f"TRIGGER:-P{days}D", "END:VALARM"]
    lines.append("END:VEVENT")
    return lines


def cmd_export(args) -> dict:
    """Open obligations as a calendar file any phone or calendar imports (RFC 5545)."""
    root = root_of(args.root)
    require_writable(root, args)
    today = today_from(args)
    lang = lang_for(args, root)
    pack = pack_or_none(args)
    members = profile_members(root)
    member = (args.member or "").strip() or None
    if member and member not in members:
        raise RecordError(f"{member!r} is not in the profile's members table")
    data = load(root, "obligations")
    key = hashlib.sha256(household_label(root).encode("utf-8")).hexdigest()[:8]
    horizon = today + timedelta(days=args.days)
    events, warnings, skipped, cancelled = [], [], [], 0
    for o in data["obligations"]:
        if not isinstance(o, dict) or not o.get("id"):
            continue
        if member and (o.get("owner") or "") != member:
            continue
        plan = o.get("do_by") or o.get("due_date")
        if o.get("status") == "open":
            if not is_date(plan):
                skipped.append(o["id"])
                continue
            if date.fromisoformat(plan) > horizon:
                continue
            events.append(ics_event(o, key, lang, root, pack, False, warnings))
        elif (o.get("status") in CLOSED and is_date(plan) and is_date(o.get("updated"))
              and (today - date.fromisoformat(o["updated"])).days <= 30):
            events.append(ics_event(o, key, lang, root, pack, True, warnings))
            cancelled += 1
    name = household_label(root)
    head = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//HouseholdBot//record.py {VERSION}//EN",
            "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
            f"X-WR-CALNAME:{ics_escape('HouseholdBot · ' + name + (' · ' + member if member else ''))}"]
    out_lines = head + [line for ev in events for line in ev] + ["END:VCALENDAR"]
    text = "".join(part + "\r\n" for line in out_lines for part in ics_fold(line))
    rel = f"exports/householdbot{'-' + slug(member) if member else ''}.ics"
    change = Change(root, lang, "export", getattr(args, "ignore_conflicts", False))
    change.write_text(rel, text, backup=False)
    summary = lang.log("exported", count=len(events) - cancelled, file=rel)
    change.log(summary)
    result = {"file": rel, "events": len(events) - cancelled, "cancelled": cancelled,
              "no_date": skipped, "days": args.days, "member": member, "summary": summary,
              "warnings": warnings,
              "note": "import the file into a calendar; importing a newer export updates the same events"}
    if member and members.get(member) == "child":
        result["note"] += "; a child's export holds only that child's own entries"
    return finish(change, args, result)


def cmd_retention(args) -> dict:
    """Which papers may go, which have no keeping date, which stay for good. Changes nothing."""
    root = root_of(args.root)
    today = today_from(args).isoformat()
    lang = lang_for(args, root)
    data = load(root, "documents")
    may_go, no_date, permanent, kept = [], [], [], 0
    for d in data["documents"]:
        if not isinstance(d, dict) or d.get("status") == "disposed":
            continue
        row = {k: d.get(k) for k in ("id", "title", "type", "category", "document_date", "file",
                                     "keep_until", "status")}
        ku = d.get("keep_until")
        if ku == "permanent":
            permanent.append(row)
        elif not is_date(ku):
            no_date.append(row)
        elif ku <= today:
            row["keep_until_text"] = lang.date(dates.parse_date(ku))
            may_go.append(row)
        else:
            kept += 1
    may_go.sort(key=lambda r: (r["keep_until"], r["id"]))
    return {"today": today, "may_go": may_go, "no_keeping_date": no_date,
            "permanent": len(permanent), "kept_for_now": kept,
            "note": "the plugin never deletes anything: the household shreds the paper and deletes "
                    "the file, then the entry is marked status=disposed with record.py update, after a yes"}


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
    lang = lang_for(args, root)
    result = {"changes": [{"register": r["register"], "steps": r["steps"]} for r in report],
              "summary": "; ".join(lang.log("migrate", register=register_label(r["register"], lang),
                                            steps=", ".join(r["steps"])) for r in changed)
              or "already at the current schema"}
    if not changed:
        return result
    change = Change(root, lang, "migrate", getattr(args, "ignore_conflicts", False))
    for r in changed:
        change.write_json(REGISTERS[r["register"]], r["data"])
    change.log(result["summary"])
    return finish(change, args, result)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="record.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp, root=True, write=False, pack=False):
        if root:
            sp.add_argument("root", help="the household folder")
        sp.add_argument("--today", help="today's date from the session, YYYY-MM-DD")
        sp.add_argument("--lang", help="en or pl; default: the profile's Language, else English")
        if write:
            # Accepted only to refuse it with the two-step instruction (ONE_CALL); not shown in --help,
            # so that the help of a writing command teaches the preview, not a write in one call.
            sp.add_argument("--approved-by", help=argparse.SUPPRESS)
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
    s.add_argument("--profile-file", help="the approved household-profile.md, or - for stdin; "
                                          "written in the same change")
    s.set_defaults(func=cmd_init)

    s = common(sub.add_parser("commit", help="apply a previewed change after a yes"))
    s.add_argument("--confirm", required=True, help="the token printed with the preview")
    s.add_argument("--approved-by", required=True, help="the name of the person who said yes")
    s.set_defaults(func=cmd_commit)

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
    s.add_argument("--original", help="documents only: the original file to copy into documents/YYYY/; "
                                      "a path that came with a document goes inside the entry as \"original\"")
    s.set_defaults(func=cmd_add)

    s = common(sub.add_parser("update", help="change fields of one entry"), write=True, pack=True)
    s.add_argument("--id", required=True)
    s.add_argument("--set", action="append", help="field=value; value is JSON when it parses")
    s.add_argument("--file", help="the changes as a JSON object of field: value, or - for stdin")
    s.set_defaults(func=cmd_update)

    s = common(sub.add_parser("complete", help="close obligations and add their next occurrences"),
               write=True, pack=True)
    s.add_argument("--id", required=True, action="append",
                   help="the obligation to close; repeat for several in one change")
    s.add_argument("--done-date")
    s.add_argument("--status", choices=["done", "lapsed", "cancelled"], default="done")
    s.add_argument("--no-next", action="store_true", help="do not add the next occurrence")
    s.add_argument("--from-done", action="store_true",
                   help="count the next occurrence from the done date, not the old due date "
                        "(checks and services)")
    s.set_defaults(func=cmd_complete)

    s = common(sub.add_parser("due", help="open obligations by urgency"), pack=True)
    s.add_argument("--horizon", type=int, default=90, help="days ahead to list; default 90")
    s.add_argument("--kind", help="only these kinds, comma-separated (payment, renewal, ...)")
    s.add_argument("--category", help="only these categories, comma-separated")
    s.set_defaults(func=cmd_due)

    s = common(sub.add_parser("find", help="search documents and obligations"))
    s.add_argument("--query", help="words to search; leave out with --type or --category to list them all")
    s.add_argument("--query-file", help="the words to search, from a file or - for stdin "
                                        "(text taken from a document goes this way)")
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

    s = common(sub.add_parser("retention", help="papers whose keeping period has ended; changes nothing"))
    s.set_defaults(func=cmd_retention)

    s = common(sub.add_parser("archive", help="move closed obligations to archive/"), write=True)
    s.add_argument("--before", required=True, help="archive closed entries dated before this day")
    s.set_defaults(func=cmd_archive)

    s = common(sub.add_parser("migrate", help="bring registers to the current schema"), write=True)
    s.set_defaults(func=cmd_migrate)

    s = common(sub.add_parser("save", help="keep an approved file: a brief, page, list, pack, skill"),
               write=True)
    s.add_argument("--to", required=True, help="path inside the household folder, e.g. briefs/2026-W46.md")
    s.add_argument("--file", required=True, help="the content, from a file or - for stdin")
    s.add_argument("--replace", action="store_true",
                   help="replace the file when it exists (a copy goes to registers/.history/); "
                        "without it a taken name gets -2, -3")
    s.set_defaults(func=cmd_save)

    s = common(sub.add_parser("export", help="open obligations as a calendar file (.ics)"),
               write=True, pack=True)
    s.add_argument("--ics", action="store_true", required=True, help="iCalendar format (RFC 5545)")
    s.add_argument("--days", type=int, default=400, help="plan dates up to this many days ahead")
    s.add_argument("--member", help="only this member's entries, for their own calendar")
    s.set_defaults(func=cmd_export)
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
