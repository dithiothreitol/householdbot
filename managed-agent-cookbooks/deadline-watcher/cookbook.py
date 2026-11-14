#!/usr/bin/env python3
"""Helper for the deadline-watcher Claude Managed Agents cookbook.

Offline (no network, no credentials):

  python cookbook.py check                  lint: tools per tier, closed sandbox, paths, prompt drift
  python cookbook.py --dry-run              print the resolved request bodies; nothing is sent
  python cookbook.py --dry-run run --household DIR
                                            the same for one run, with this household's snapshot
  python cookbook.py snapshot --household DIR --out DIR
                                            write the exact files a run uploads, and list them
  python cookbook.py sync                   copy the plugin agent's text into the coordinator's prompt

Online (the official `anthropic` SDK; the agent and environment IDs come from
the claude-lock.json that `ant apply` writes in this folder):

  python cookbook.py run --household DIR    one session now: upload, run, check, save, delete the upload
  python cookbook.py push --household DIR [--create]
                                            give the weekly scheduled deployment a fresh snapshot
  python cookbook.py fetch --household DIR  download, check and save the newest scheduled report
  python cookbook.py forget                 pause the deployment and delete the uploaded snapshot

Every command except `snapshot` needs PyYAML. The plugin's scripts stay
standard-library only; this helper runs them as separate processes.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
AGENTS = HERE / "agents"
ORCHESTRATOR = AGENTS / "deadline-watcher" / "agent.md"
ENVIRONMENT = AGENTS / "deadline-watcher" / "environment.yaml"
WRITER = AGENTS / "report-writer" / "agent.md"
SCHEDULE = HERE / "schedule.yaml"
STEERING = HERE / "steering-examples.json"
LOCK = HERE / "claude-lock.json"
PLUGIN_AGENT = REPO / "householdbot" / "agents" / "deadline-watcher.md"
SKILL = REPO / "householdbot" / "skills" / "deadline-tracker"
SCRIPTS = SKILL / "shared" / "scripts"
STATE = Path.home() / ".claude" / "plugins" / "config" / "householdbot" / "deadline-watcher.json"

APPEND_HEADING = "## Running as a Claude Managed Agent"
TOOLSET = "agent_toolset_20260401"
BUILTIN = ("bash", "read", "write", "edit", "glob", "grep", "web_fetch", "web_search")
TIERS = ("orchestrator", "reader", "calculator", "writer")
ALLOWED = {"orchestrator": set(), "reader": {"read", "glob", "grep"},
           "calculator": {"bash", "read", "glob", "grep"}, "writer": {"write", "edit"}}
MODELS = {"claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"}
AGENT_KEYS = {"name", "description", "model", "tools", "skills", "mcp_servers", "multiagent", "metadata"}
POLICIES = {"auto", "always_ask"}
READ_ONLY_MCP = re.compile(r"^(get|list|read|search|fetch|download|find|query|describe)_[a-z0-9_]+$")
TZ_RE = re.compile(r"^(UTC|[A-Za-z]+(/[A-Za-z0-9_+\-]+)+)$")
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MONEY_RE = re.compile(r"^-?\d+(\.\d{1,2})?$")
OB_ID = re.compile(r"\bob-\d{4}-\d{4,}\b")
REPORT_RE = re.compile(r"^deadline-watch-(\d{4}-\d{2}-\d{2}|undated)\.md$")
FRONT = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
FOOTER = re.compile(r"```footer-(\w+)\n(.*?)\n```", re.S)
BETA = "managed-agents-2026-04-01"

# What leaves the household: two files, mounted read-only under
# /mnt/session/uploads/household/. Nothing else is ever read for upload.
MOUNT = "/household"
SNAPSHOT_FILES = ("household-profile.md", "registers/obligations.json")
KEEP_FIELDS = ("id", "title", "kind", "category", "owner", "due_date", "do_by",
               "transit_buffer_days", "lead_time_days", "amount", "currency",
               "auto_renews", "provenance", "law", "status")
KINDS = {"payment", "renewal", "filing", "response", "appointment", "expiry", "task"}
CATEGORIES = {"home", "vehicle", "money", "tax", "insurance", "utilities", "health",
              "children", "identity", "work", "daily", "other"}
TAGS = {"stated in document", "calculated from document", "country pack rule — verify",
        "model calculation — verify", "told by household member"}
PROFILE_LABELS = {"country": ("country", "kraj"), "language": ("language", "język"),
                  "time_zone": ("time zone", "strefa czasowa"),
                  "audience": ("who sees the weekly brief", "kto widzi przegląd tygodnia")}
PROFILE_LINE = re.compile(r"^\s*-\s*\*\*(.+?)\s*:\*\*\s*(.*?)\s*$")
EXCERPT = """# Household profile (excerpt)

Written by cookbook.py for the deadline-watcher managed agent. Only the lines
below leave this computer; the full profile stays in the household folder.

- **Country:** {country}
- **Language:** {language}
- **Time zone:** {time_zone}
- **Who sees the weekly brief:** {audience}

## Snapshot

- **Taken:** {taken}
- **Open obligations:** {open}
- **Record check on this computer:** {check}
"""


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def _yaml():
    try:
        import yaml
    except ImportError:
        sys.exit("this command needs PyYAML: pip install pyyaml")
    return yaml


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def split_front(path: Path) -> tuple:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = FRONT.match(text)
    if not m:
        raise ValueError(f"{rel(path)}: no YAML frontmatter")
    return m.group(1), m.group(2)


def read_agent(path: Path) -> tuple:
    front, body = split_front(path)
    fm = _yaml().safe_load(front) or {}
    if not isinstance(fm, dict):
        raise ValueError(f"{rel(path)}: the frontmatter is not a mapping")
    return fm, body.strip()


def plugin_body() -> str:
    return split_front(PLUGIN_AGENT)[1].strip()


def agent_files() -> list:
    files = sorted(AGENTS.glob("*/agent.md"))
    return [p for p in files if p != ORCHESTRATOR] + [p for p in files if p == ORCHESTRATOR]


def footers(writer_body: str | None = None) -> dict:
    body = writer_body if writer_body is not None else split_front(WRITER)[1]
    return {lang: text.strip() for lang, text in FOOTER.findall(body)}


def load_schedule() -> dict:
    return _yaml().safe_load(SCHEDULE.read_text(encoding="utf-8")) or {}


def enabled_tools(toolset: dict) -> set:
    default = (toolset.get("default_config") or {}).get("enabled", True)
    on = {name for name in BUILTIN if default}
    for cfg in toolset.get("configs") or []:
        if isinstance(cfg, dict) and cfg.get("name") in BUILTIN:
            if cfg.get("enabled", default):
                on.add(cfg["name"])
            else:
                on.discard(cfg["name"])
    return on


# --------------------------------------------------------------------------
# check: the offline lint
# --------------------------------------------------------------------------

def lint() -> list:
    yaml = _yaml()
    errors: list = []
    agents, enabled = {}, {}
    for path in agent_files():
        try:
            agents[path] = read_agent(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(str(exc))
    tiers: dict = {t: [] for t in TIERS}
    names: set = set()
    reader_servers = False
    for path, (fm, body) in agents.items():
        where = rel(path)
        tier = (fm.get("metadata") or {}).get("householdbot_tier")
        if tier not in TIERS:
            errors.append(f"{where}: metadata.householdbot_tier must be one of {', '.join(TIERS)}")
            continue
        tiers[tier].append(path)
        extra = set(fm) - AGENT_KEYS
        if extra:
            errors.append(f"{where}: fields the agents API does not take: {sorted(extra)}")
        name = fm.get("name")
        if not isinstance(name, str) or not name or name == "self" or name in names:
            errors.append(f"{where}: needs a unique name other than 'self'")
        names.add(name)
        model = fm.get("model")
        model_id = model.get("id") if isinstance(model, dict) else model
        if model_id not in MODELS:
            errors.append(f"{where}: model {model_id!r} is not one of {sorted(MODELS)}")
        elif tier == "orchestrator" and model_id != "claude-opus-5-5":
            errors.append(f"{where}: the coordinator runs on claude-opus-5-5")
        if not body:
            errors.append(f"{where}: empty system prompt")

        on, mcp = set(), []
        for i, tool in enumerate(fm.get("tools") or []):
            kind = tool.get("type") if isinstance(tool, dict) else None
            if kind == TOOLSET:
                default = tool.get("default_config") or {}
                if default.get("enabled", True) is not False:
                    errors.append(f"{where}: tools[{i}] must set default_config.enabled: false "
                                  "and enable tools one by one")
                if (default.get("permission_policy") or {}).get("type") not in POLICIES:
                    errors.append(f"{where}: tools[{i}] needs permission_policy auto or always_ask")
                for cfg in tool.get("configs") or []:
                    if not isinstance(cfg, dict) or cfg.get("name") not in BUILTIN:
                        errors.append(f"{where}: tools[{i}] names an unknown tool: {cfg!r}")
                    elif "permission_policy" in cfg and \
                            (cfg["permission_policy"] or {}).get("type") not in POLICIES:
                        errors.append(f"{where}: {cfg['name']} needs permission_policy auto or always_ask")
                on |= enabled_tools(tool)
            elif kind == "mcp_toolset":
                mcp.append(tool)
            else:
                errors.append(f"{where}: tools[{i}] of type {kind!r} is not allowed (no custom tools)")
        enabled[path] = on
        for tool_name in sorted(on - ALLOWED[tier]):
            errors.append(f"{where}: a {tier} must not have '{tool_name}'")

        servers = {s.get("name"): s for s in fm.get("mcp_servers") or [] if isinstance(s, dict)}
        if (servers or mcp) and tier != "reader":
            errors.append(f"{where}: only a reader may use an MCP server, and only to read")
        for tool in mcp:
            if tool.get("mcp_server_name") not in servers:
                errors.append(f"{where}: mcp_toolset names a server the agent does not declare")
            if (tool.get("default_config") or {}).get("enabled", True) is not False:
                errors.append(f"{where}: an MCP toolset must be off by default")
            for cfg in tool.get("configs") or []:
                if isinstance(cfg, dict) and cfg.get("enabled") \
                        and not READ_ONLY_MCP.match(str(cfg.get("name"))):
                    errors.append(f"{where}: MCP tool {cfg.get('name')!r} does not look read-only")
        for server in servers.values():
            if not str(server.get("url", "")).startswith("https://"):
                errors.append(f"{where}: MCP server {server.get('name')!r} needs an https URL")
        reader_servers = reader_servers or bool(servers)

        skills = fm.get("skills") or []
        for skill in skills:
            if not isinstance(skill, str) or not (path.parent / skill / "SKILL.md").is_file():
                errors.append(f"{where}: skill {skill!r} is not a folder with a SKILL.md")
        if skills and "read" not in on:
            errors.append(f"{where}: an agent with skills needs the read tool")
        if tier != "orchestrator" and fm.get("multiagent") is not None:
            errors.append(f"{where}: a worker must not delegate (one level of delegation)")

    for tier in TIERS:
        if not tiers[tier]:
            errors.append(f"no {tier} agent under {rel(AGENTS)}")
    for tier in ("orchestrator", "writer"):
        if len(tiers[tier]) > 1:
            errors.append(f"more than one {tier}: {[rel(p) for p in tiers[tier]]}")
    workers = {p.resolve() for t in ("reader", "calculator", "writer") for p in tiers[t]}

    for path in tiers["orchestrator"]:
        fm, body = agents[path]
        where = rel(path)
        block = fm.get("multiagent") or {}
        sub = block.get("subagents") or {}
        if block.get("type") != "multiagent_20261001" or sub.get("type") != "enabled":
            errors.append(f"{where}: needs multiagent_20261001 with subagents enabled")
        if (sub.get("inline_agents") or {}).get("type") != "disabled":
            errors.append(f"{where}: subagents.inline_agents must be disabled (listed workers only)")
        roster = set()
        for entry in sub.get("predefined_agents") or []:
            target = (path.parent / entry).resolve() if isinstance(entry, str) else None
            if target is None or not target.is_file():
                errors.append(f"{where}: roster entry {entry!r} is not an agent file")
            else:
                roster.add(target)
        if roster != workers:
            errors.append(f"{where}: the roster must list exactly the worker agent files")
        flows = block.get("workflows") or {}
        if flows.get("type") == "enabled":
            listed = {(path.parent / e).resolve() for e in flows.get("predefined_agents") or []
                      if isinstance(e, str)}
            if (flows.get("inline_agents") or {}).get("type") != "disabled" or not listed \
                    or not listed <= workers:
                errors.append(f"{where}: workflow runs may use the listed workers only")
        elif flows.get("type") != "disabled":
            errors.append(f"{where}: write workflows out as {{type: disabled}}; they default to enabled")
        if (block.get("advisor") or {}).get("type", "disabled") != "disabled":
            errors.append(f"{where}: no advisor in this cookbook")
        if not body.startswith(plugin_body() + "\n\n" + APPEND_HEADING):
            errors.append(f"{where}: the prompt must be {rel(PLUGIN_AGENT)} followed by "
                          f"'{APPEND_HEADING}'; run: python cookbook.py sync")

    for path in tiers["calculator"]:
        fm, body = agents[path]
        for skill in fm.get("skills") or []:
            for script in ("record.py", "dates.py"):
                if not (path.parent / skill / "shared" / "scripts" / script).is_file():
                    errors.append(f"{rel(path)}: skill {skill} has no shared/scripts/{script}")
        if "record.py" not in body or "<<'PY'" not in body:
            errors.append(f"{rel(path)}: the prompt must carry the program that runs record.py due")

    for path in tiers["writer"]:
        if "write" not in enabled.get(path, set()):
            errors.append(f"{rel(path)}: the writer needs the write tool")
        if set(footers(agents[path][1])) != {"en", "pl"}:
            errors.append(f"{rel(path)}: needs the footer blocks footer-en and footer-pl")

    try:
        env = yaml.safe_load(ENVIRONMENT.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{rel(ENVIRONMENT)}: {exc}")
        env = {}
    config = env.get("config") or {}
    net = config.get("networking") or {}
    if config.get("type") != "cloud":
        errors.append(f"{rel(ENVIRONMENT)}: config.type must be cloud")
    if net.get("type") != "limited":
        errors.append(f"{rel(ENVIRONMENT)}: networking must be limited (API environments default to unrestricted)")
    if net.get("allowed_hosts"):
        errors.append(f"{rel(ENVIRONMENT)}: no allowed_hosts: nothing in this job needs the network")
    if net.get("allow_package_managers"):
        errors.append(f"{rel(ENVIRONMENT)}: allow_package_managers must be false")
    if net.get("allow_mcp_servers") and not reader_servers:
        errors.append(f"{rel(ENVIRONMENT)}: allow_mcp_servers is on but no reader declares a server")
    if config.get("packages"):
        errors.append(f"{rel(ENVIRONMENT)}: no packages: the plugin's scripts use the standard library")

    try:
        schedule = load_schedule()
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{rel(SCHEDULE)}: {exc}")
        schedule = {}
    cron = schedule.get("schedule") or {}
    fields = str(cron.get("expression", "")).split()
    if cron.get("type") != "cron" or len(fields) != 5 or fields[4].lower() not in ("1", "mon"):
        errors.append(f"{rel(SCHEDULE)}: the schedule must be a cron that runs on Mondays")
    elif fields[1].isdigit() and 1 <= int(fields[1]) <= 3:
        errors.append(f"{rel(SCHEDULE)}: keep the hour out of the 01:00-03:00 DST window")
    zone = cron.get("timezone")
    if zone != "from-profile" and not TZ_RE.match(str(zone)):
        errors.append(f"{rel(SCHEDULE)}: timezone must be from-profile or an IANA name")
    budget = schedule.get("budget") or {}
    cap = budget.get("max_list_cost") or {}
    if budget.get("type") != "limit" or not re.fullmatch(r"[1-9]\d*", str(cap.get("amount", ""))) \
            or cap.get("currency") != "USD":
        errors.append(f"{rel(SCHEDULE)}: budget must be a limit in USD cents, e.g. amount: \"300\"")
    events = schedule.get("initial_events") or []
    outcome = events[0] if len(events) == 1 and isinstance(events[0], dict) else {}
    rubric = outcome.get("rubric") or {}
    if outcome.get("type") != "user.define_outcome" or not str(outcome.get("description", "")).strip() \
            or rubric.get("type") != "text" or not str(rubric.get("content", "")).strip():
        errors.append(f"{rel(SCHEDULE)}: initial_events must be one user.define_outcome with a text rubric")
    elif type(outcome.get("max_iterations")) is not int or not 1 <= outcome["max_iterations"] <= 3:
        errors.append(f"{rel(SCHEDULE)}: keep max_iterations between 1 and 3")

    try:
        steering = json.loads(STEERING.read_text(encoding="utf-8"))
        valid = isinstance(steering, list) and bool(steering) and all(
            isinstance(e, dict) and isinstance(e.get("event"), str) and isinstance(e.get("description"), str)
            for e in steering)
    except (OSError, ValueError):
        valid = False
    if not valid:
        errors.append(f"{rel(STEERING)}: must be a list of {{event, description}} objects")
    if not (HERE / "README.md").is_file():
        errors.append(f"{rel(HERE)}/README.md is missing")
    return errors


def cmd_check(args) -> int:
    errors = lint()
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print("deadline-watcher: tools per tier, sandbox, paths, prompt and schedule in order")
    print(f"{len(errors)} error(s)")
    return 1 if errors else 0


def cmd_sync(args) -> int:
    front, body = split_front(ORCHESTRATOR)
    at = body.find(APPEND_HEADING)
    if at < 0:
        sys.exit(f"{rel(ORCHESTRATOR)}: no '{APPEND_HEADING}' section to keep")
    text = f"---\n{front}\n---\n\n{plugin_body()}\n\n{body[at:].strip()}\n"
    if text == ORCHESTRATOR.read_text(encoding="utf-8").replace("\r\n", "\n"):
        print("already in sync")
    else:
        _write(ORCHESTRATOR, text)
        print(f"updated {rel(ORCHESTRATOR)} from {rel(PLUGIN_AGENT)}")
    return 0


# --------------------------------------------------------------------------
# The request bodies (also printed by --dry-run)
# --------------------------------------------------------------------------

def _agent_ref(path: Path) -> str:
    try:
        name = read_agent(path)[0].get("name")
    except (OSError, ValueError):
        name = rel(path)
    return f"<agent id from ant apply: {name}>"


def resolve_agent(path: Path, fm: dict, body: str) -> dict:
    out = {key: copy.deepcopy(fm[key]) for key in ("name", "description", "model") if key in fm}
    out["system"] = body
    for key in ("tools", "mcp_servers"):
        if fm.get(key):
            out[key] = copy.deepcopy(fm[key])
    if fm.get("skills"):
        out["skills"] = [{"type": "custom", "version": "latest",
                          "skill_id": f"<skill id from ant apply: {rel(path.parent / s)}>"}
                         for s in fm["skills"]]
    if fm.get("multiagent"):
        block = copy.deepcopy(fm["multiagent"])
        for member in ("subagents", "workflows"):
            part = block.get(member) or {}
            if part.get("predefined_agents"):
                part["predefined_agents"] = [_agent_ref(path.parent / e) if isinstance(e, str) else e
                                             for e in part["predefined_agents"]]
        out["multiagent"] = block
    if fm.get("metadata"):
        out["metadata"] = dict(fm["metadata"])
    return out


def resources(file_ids: dict | None = None) -> list:
    ids = file_ids or {}
    return [{"type": "file", "file_id": ids.get(name, f"<file id of the uploaded {name}>"),
             "mount_path": f"{MOUNT}/{name}"} for name in SNAPSHOT_FILES]


def session_request(settings: dict, today: str, zone: str | None) -> tuple:
    body = {
        "agent": "<agent id of deadline-watcher, from claude-lock.json>",
        "environment_id": "<environment id, from claude-lock.json>",
        "title": f"deadline-watch {today}",
        "resources": resources(),
        "budget": copy.deepcopy(settings["budget"]),
        "metadata": {"householdbot_cookbook": "deadline-watcher"},
    }
    when = f"Today is {today}" + (f" ({zone})." if zone else ".")
    events = [{"type": "user.message", "content": [{"type": "text", "text": when}]}]
    return body, events + copy.deepcopy(settings["initial_events"])


def deployment_request(settings: dict, zone: str | None) -> dict:
    schedule = dict(settings["schedule"])
    schedule["timezone"] = zone or "<the profile's Time zone>"
    return {
        "name": settings["name"],
        "agent": "<agent id of deadline-watcher, from claude-lock.json>",
        "environment_id": "<environment id, from claude-lock.json>",
        "resources": resources(),
        "initial_events": copy.deepcopy(settings["initial_events"]),
        "schedule": schedule,
        "budget": copy.deepcopy(settings["budget"]),
    }


def plan(household: str | None = None) -> dict:
    yaml = _yaml()
    settings = load_schedule()
    requests, seen = [], set()
    agents = [(p, *read_agent(p)) for p in agent_files()]
    for path, fm, _ in agents:
        for skill in fm.get("skills") or []:
            folder = (path.parent / skill).resolve()
            if folder not in seen:
                seen.add(folder)
                count = sum(1 for f in folder.rglob("*") if f.is_file() and "__pycache__" not in f.parts)
                requests.append({"method": "POST", "path": "/v1/skills", "by": "ant apply",
                                 "skill_folder": rel(folder), "files": count})
    for path, fm, body in agents:
        requests.append({"method": "POST", "path": "/v1/agents", "by": "ant apply",
                         "file": rel(path), "body": resolve_agent(path, fm, body)})
    requests.append({"method": "POST", "path": "/v1/environments", "by": "ant apply",
                     "file": rel(ENVIRONMENT),
                     "body": yaml.safe_load(ENVIRONMENT.read_text(encoding="utf-8"))})
    zone, uploads = None, [{"file": n, "mount": f"/mnt/session/uploads{MOUNT}/{n}"} for n in SNAPSHOT_FILES]
    if household:
        with tempfile.TemporaryDirectory(prefix="deadline-watch-") as tmp:
            snap = build_snapshot(Path(household), Path(tmp))
        zone, uploads = snap["profile"]["time_zone"], snap["files"]
    requests.append({"method": "POST", "path": "/v1/files", "by": "cookbook.py run and push",
                     "uploads": uploads})
    body, events = session_request(settings, date.today().isoformat(), zone)
    requests.append({"method": "POST", "path": "/v1/sessions", "by": "cookbook.py run", "body": body})
    requests.append({"method": "POST", "path": "/v1/sessions/<session id>/events",
                     "by": "cookbook.py run, after it opens the event stream", "body": {"events": events}})
    requests.append({"method": "POST", "path": "/v1/deployments", "by": "cookbook.py push --create, then pause",
                     "body": deployment_request(settings, zone)})
    requests.append({"method": "POST", "path": "/v1/deployments/<deployment id>", "by": "cookbook.py push",
                     "body": {"agent": "<agent id of deadline-watcher>", "resources": resources()}})
    return {"dry_run": True,
            "note": "Resolved request bodies. Nothing was sent; IDs that ant apply or the API "
                    "assign are shown in angle brackets.",
            "requests": requests}


# --------------------------------------------------------------------------
# snapshot: the only data that leaves the household
# --------------------------------------------------------------------------

def _value(raw: str | None) -> str | None:
    if raw is None or raw.strip().startswith("[PLACEHOLDER"):
        return None
    m = re.match(r"^\[DEFAULT\b\W*(.*?)\]$", raw.strip())
    return (m.group(1) if m else raw).strip() or None


def parse_profile(text: str) -> dict:
    found: dict = {}
    for line in text.replace("\r\n", "\n").splitlines():
        m = PROFILE_LINE.match(line)
        if not m:
            continue
        label = m.group(1).strip().lower()
        for key, labels in PROFILE_LABELS.items():
            if label in labels and key not in found:
                found[key] = _value(m.group(2))
    country = (found.get("country") or "").upper()
    language = (found.get("language") or "").lower()
    zone = found.get("time_zone") or ""
    seen_by = (found.get("audience") or "").lower()
    if any(w in seen_by for w in ("child", "dzie", "everyone", "wszyscy")):
        audience = "everyone, children included"
    elif any(w in seen_by for w in ("adult", "doros")):
        audience = "adults only"
    else:
        audience = "not set"
    return {"country": country if re.fullmatch(r"[A-Z]{2}", country) else None,
            "language": "pl" if language in ("pl", "polski", "polish", "po polsku") else "en",
            "time_zone": zone if TZ_RE.match(zone) else None,
            "audience": audience}


def _line(value: str, cap: int) -> str:
    text = " ".join(value.split())
    return "".join(ch for ch in text if ch.isprintable())[:cap]


def _money(value) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float)) or (isinstance(value, str) and bool(MONEY_RE.match(value)))


def trim_obligations(data: dict) -> tuple:
    """Open obligations only, the KEEP_FIELDS only, each value checked."""
    kept, closed = [], 0
    for entry in data.get("obligations") or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != "open":
            closed += 1
            continue
        e = {k: entry[k] for k in KEEP_FIELDS if entry.get(k) not in (None, "")}
        for key, cap in (("id", 40), ("title", 200), ("owner", 60), ("law", 200)):
            if key in e:
                if isinstance(e[key], str):
                    e[key] = _line(e[key], cap)
                else:
                    del e[key]
        for key in ("due_date", "do_by"):
            if key in e and not (isinstance(e[key], str) and DAY_RE.match(e[key])):
                del e[key]
        for key in ("transit_buffer_days", "lead_time_days"):
            if key in e and not (type(e[key]) is int and 0 <= e[key] <= 3650):
                del e[key]
        if "amount" in e and not _money(e["amount"]):
            del e["amount"]
        if "currency" in e and not (isinstance(e["currency"], str) and re.fullmatch(r"[A-Z]{3}", e["currency"])):
            del e["currency"]
        if "auto_renews" in e and not isinstance(e["auto_renews"], bool):
            del e["auto_renews"]
        for key, allowed in (("kind", KINDS), ("category", CATEGORIES), ("provenance", TAGS)):
            if key in e and e[key] not in allowed:
                del e[key]
        kept.append(e)
    return {"schema_version": data.get("schema_version", 1), "obligations": kept}, closed


def _plugin(*argv: str) -> dict:
    """Run the deadline-tracker skill's record.py locally and return its JSON."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    run = subprocess.run([sys.executable, "-B", str(SCRIPTS / "record.py"), *argv],
                         capture_output=True, text=True, encoding="utf-8", env=env)
    try:
        return json.loads(run.stdout)
    except ValueError:
        return {"ok": False, "errors": [f"record.py exited with {run.returncode}"]}


def record_check(household: Path) -> dict | None:
    result = _plugin("validate", str(household), "--no-files")
    if not isinstance(result.get("warnings"), list):
        return None
    return {"errors": len(result.get("errors") or []), "warnings": len(result["warnings"]),
            "conflict_copies": len(result.get("conflicts") or [])}


def build_snapshot(household: Path, out: Path, taken: datetime | None = None) -> dict:
    household = household.expanduser().resolve()
    profile_path = household / "household-profile.md"
    register_path = household / "registers" / "obligations.json"
    if not profile_path.is_file() or not register_path.is_file():
        sys.exit(f"{household} has no household-profile.md and registers/obligations.json: "
                 "point --household at the household folder")
    profile = parse_profile(profile_path.read_text(encoding="utf-8"))
    try:
        register, closed = trim_obligations(json.loads(register_path.read_text(encoding="utf-8")))
    except (ValueError, AttributeError):
        sys.exit(f"{register_path} is not a readable register: in Claude Code, say "
                 "'check my household record'")
    taken = taken or datetime.now().astimezone()
    check = record_check(household)
    _write(out / "household-profile.md", EXCERPT.format(
        country=profile["country"] or "not set", language=profile["language"],
        time_zone=profile["time_zone"] or "not set", audience=profile["audience"],
        taken=taken.strftime("%Y-%m-%d %H:%M %z").strip(), open=len(register["obligations"]),
        check="could not run" if check is None else
        f"{check['errors']} errors, {check['warnings']} warnings, {check['conflict_copies']} conflict copies"))
    _write(out / "registers" / "obligations.json", json.dumps(register, ensure_ascii=False, indent=2) + "\n")
    files = [{"file": n, "bytes": (out / n).stat().st_size, "mount": f"/mnt/session/uploads{MOUNT}/{n}"}
             for n in SNAPSHOT_FILES]
    return {"folder": str(out), "files": files, "profile": profile, "taken": taken.date().isoformat(),
            "open_obligations": len(register["obligations"]), "closed_left_out": closed,
            "fields_kept": list(KEEP_FIELDS), "record_check": check}


def cmd_snapshot(args) -> int:
    summary = build_snapshot(Path(args.household), Path(args.out).expanduser().resolve())
    _print(summary)
    print(f"Read these files before the first upload: {summary['folder']}")
    return 0


# --------------------------------------------------------------------------
# The report check, run on this computer before a report is saved
# --------------------------------------------------------------------------

def identifier_findings(text: str) -> list | None:
    """The plugin's own identifier detector (record.identifier_warnings); None if it cannot run."""
    code = ("import json, sys; sys.path.insert(0, sys.argv[1]); import record; "
            "print(json.dumps(record.identifier_warnings(sys.stdin.read(), 'report')))")
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    run = subprocess.run([sys.executable, "-B", "-c", code, str(SCRIPTS)], input=text,
                         capture_output=True, text=True, encoding="utf-8", env=env)
    try:
        return [str(w) for w in json.loads(run.stdout)]
    except ValueError:
        return None


def report_problems(text: str, expected: list | None = None, feet: dict | None = None) -> tuple:
    """Problems stop the report from being saved; notes are saved next to it."""
    feet = feet or footers()
    body = text.replace("\r\n", "\n").rstrip()
    problems, notes = [], []
    flat = " ".join(body.split())
    if not any(flat.endswith(" ".join(f.split())) for f in feet.values()):
        problems.append("the verification footer is missing or was changed")
    plain = re.sub(r"`[^`\n]*`", "", body)
    if re.search(r"<\s*[A-Za-z!/?]", plain):
        problems.append("it contains HTML or an autolink")
    if re.search(r"(?<!\\)\]\s*\(|^\s{0,3}\[[^\]\n]+\]:\s*\S", plain, re.M):
        problems.append("it contains a Markdown link or image")
    if re.search(r"(?i)\b(?:https?://|www\.)|\b(?:javascript|vbscript):|\bdata:[a-z]+/", plain):
        problems.append("it contains a web address outside a code span")
    findings = identifier_findings(body)
    if findings is None:
        notes.append("the identifier check could not run")
    for finding in findings or []:
        (notes if "password" in finding else problems).append(finding)
    if expected is not None:
        missing = sorted(set(expected) - set(OB_ID.findall(body)))
        if missing:
            notes.append("record.py due lists these, but the report does not: " + ", ".join(missing))
    return problems, notes


def expected_ids(root: Path, today: str, country: str | None) -> list | None:
    argv = ["due", str(root), "--today", today, "--horizon", "30"]
    if country and (SKILL / "shared" / "locale" / f"{country}.json").is_file():
        argv += ["--country", country]
    result = _plugin(*argv)
    if not isinstance(result.get("items"), list):
        return None
    ids = [i.get("id") for i in result["items"]] + [n.get("id") for n in result.get("no_date") or []]
    return [i for i in ids if isinstance(i, str) and OB_ID.fullmatch(i)]


def save_report(out_dir: Path, name: str, text: str, expected: list | None, session_id: str) -> int:
    problems, notes = report_problems(text, expected)
    stem = name[:-3]
    if problems:
        target = out_dir / f"{stem}.check-failed.txt"
        _write(target, "The report was not saved: " + "; ".join(problems) + ".\n"
               f"Session {session_id}: open it in the Console or with "
               f"`ant beta:sessions connect {session_id}`.\n")
        print(f"report NOT saved: {'; '.join(problems)} (see {target})")
        return 3
    _write(out_dir / name, text if text.endswith("\n") else text + "\n")
    print(f"saved {out_dir / name}")
    if notes:
        _write(out_dir / f"{stem}.check-notes.txt", "\n".join(notes) + "\n")
        print("check notes: " + "; ".join(notes))
    return 0


# --------------------------------------------------------------------------
# Online commands (official anthropic SDK). Documented, not run in tests.
# --------------------------------------------------------------------------

def _client():
    try:
        import anthropic
    except ImportError:
        sys.exit("the online commands need the official SDK: pip install anthropic")
    return anthropic.Anthropic()


def _lock_ids(path: Path) -> tuple:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        sys.exit(f"no readable {path}: run ant apply in {HERE} first (README, Deploy)")
    wanted = ("agents/deadline-watcher/agent.md", "agents/deadline-watcher/environment.yaml")
    found = {}
    for key, value in (data.get("resources") or {}).items():
        for suffix in wanted:
            if key.replace("\\", "/").endswith(suffix) and isinstance(value, dict) and value.get("id"):
                found[suffix] = value["id"]
    if len(found) != 2:
        sys.exit(f"{path} has no IDs for the coordinator and its environment: run ant apply first")
    return found[wanted[0]], found[wanted[1]]


def _load_state(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _delete_files(client, file_ids) -> None:
    for file_id in list(file_ids):
        try:
            client.beta.files.delete(file_id)
        except Exception as exc:  # keep going; the Console lists what is left
            print(f"could not delete uploaded file {file_id}: {exc}")


def _upload(client, folder: Path) -> dict:
    ids: dict = {}
    try:
        for name in SNAPSHOT_FILES:
            with open(folder / name, "rb") as fh:
                ids[name] = client.beta.files.upload(file=fh).id
    except Exception:
        _delete_files(client, ids.values())
        raise
    return ids


def _drive(client, session_id: str, events: list) -> str:
    """Open the stream first, then send the kickoff; deny any call that waits for approval."""
    with client.beta.sessions.events.stream(session_id=session_id) as stream:
        client.beta.sessions.events.send(session_id=session_id, events=events)
        for event in stream:
            kind = getattr(event, "type", "")
            if kind in ("agent.tool_use", "agent.mcp_tool_use") \
                    and getattr(event, "evaluated_permission", None) == "ask":
                client.beta.sessions.events.send(session_id=session_id, events=[{
                    "type": "user.tool_confirmation", "tool_use_id": event.id, "result": "deny",
                    "deny_message": "Unattended run: nobody is here to approve this call."}])
                print(f"denied a call that waited for approval: {getattr(event, 'name', 'tool')}")
            elif kind == "span.outcome_evaluation_end":
                print(f"grader: {getattr(event, 'result', '?')}")
            elif kind == "session.error":
                print(f"session error: {getattr(getattr(event, 'error', None), 'message', 'see the Console')}")
            elif kind == "session.status_idle":
                reason = getattr(getattr(event, "stop_reason", None), "type", None)
                if reason != "requires_action":
                    return str(reason)
            elif kind == "session.status_terminated":
                return "terminated"
    return "stream closed"


def _cost(client, session_id: str) -> None:
    session = client.beta.sessions.retrieve(session_id=session_id)
    cost = getattr(getattr(session, "usage", None), "list_cost", None)
    amount = getattr(cost, "amount", None)
    if amount is not None:
        print(f"list cost of this session: {int(amount) / 100:.2f} {getattr(cost, 'currency', 'USD')}")


def _fetch_report(client, session_id: str, scratch: Path) -> tuple | None:
    files: list = []
    for _ in range(5):  # outputs are indexed a few seconds after the session goes idle
        files = list(client.beta.files.list(scope_id=session_id, betas=[BETA]).data)
        if files:
            break
        time.sleep(2)
    reports = [f for f in files if REPORT_RE.match(Path(str(f.filename)).name)]
    others = [str(f.filename) for f in files if f.id not in {r.id for r in reports}]
    if others:
        print("the session also wrote, not downloaded: " + ", ".join(others))
    if len(reports) != 1:
        print(f"expected one deadline-watch-<date>.md among the session's outputs, found {len(reports)}")
        return None
    target = scratch / "report.download"
    client.beta.files.download(reports[0].id).write_to_file(target)
    return Path(str(reports[0].filename)).name, target.read_text(encoding="utf-8"), reports[0].id


def _report_day(name: str, fallback: str) -> str:
    m = REPORT_RE.match(name)
    return m.group(1) if m and m.group(1) != "undated" else fallback


def cmd_run(args) -> int:
    settings = load_schedule()
    household = Path(args.household).expanduser().resolve()
    today = args.today or date.today().isoformat()
    out_dir = Path(args.out).expanduser() if args.out else household / "out"
    with tempfile.TemporaryDirectory(prefix="deadline-watch-") as tmp:
        folder = Path(tmp) / "snapshot"
        snap = build_snapshot(household, folder)
        body, events = session_request(settings, today, snap["profile"]["time_zone"])
        if args.dry_run:
            _print({"dry_run": True, "uploads": snap["files"], "session": body, "events": events})
            return 0
        client = _client()
        agent_id, environment_id = _lock_ids(Path(args.lock))
        ids = _upload(client, folder)
        try:
            body.update(agent=agent_id, environment_id=environment_id, resources=resources(ids))
            session = client.beta.sessions.create(**body)
            print(f"session {session.id}: https://platform.claude.com/workspaces/default/sessions/"
                  f"{session.id} (put your workspace ID in place of 'default' if the key is not in "
                  "the Default workspace)")
            print(f"session stopped: {_drive(client, session.id, events)}")
            _cost(client, session.id)
            got = _fetch_report(client, session.id, Path(tmp))
            if got is None:
                return 2
            name, text, output_id = got
            day = _report_day(name, today)
            code = save_report(out_dir, name, text,
                               expected_ids(folder, day, snap["profile"]["country"]), session.id)
            if args.delete_session:
                _delete_files(client, [output_id])
                client.beta.sessions.delete(session_id=session.id)
                print("deleted the session and its output file")
            return code
        finally:
            _delete_files(client, ids.values())
            print("deleted the uploaded snapshot")


def cmd_push(args) -> int:
    settings = load_schedule()
    household = Path(args.household).expanduser().resolve()
    state_path = Path(args.state)
    state = _load_state(state_path)
    if args.create and state.get("deployment_id"):
        sys.exit(f"{state_path} already names deployment {state['deployment_id']}: push without "
                 "--create, or archive that deployment and remove the file first")
    create = args.create or not state.get("deployment_id")
    with tempfile.TemporaryDirectory(prefix="deadline-watch-") as tmp:
        folder = Path(tmp) / "snapshot"
        snap = build_snapshot(household, folder)
        zone = args.timezone or snap["profile"]["time_zone"]
        if create and not zone:
            sys.exit("the profile has no Time zone: pass --timezone, for example Europe/Warsaw")
        if args.dry_run:
            change = deployment_request(settings, zone) if create else \
                {"agent": "<agent id of deadline-watcher>", "resources": resources()}
            _print({"dry_run": True, "uploads": snap["files"], "create" if create else "update": change})
            return 0
        client = _client()
        agent_id, environment_id = _lock_ids(Path(args.lock))
        ids = _upload(client, folder)
        try:
            if create:
                body = deployment_request(settings, zone)
                body.update(agent=agent_id, environment_id=environment_id, resources=resources(ids))
                deployment = client.beta.deployments.create(**body)
                client.beta.deployments.pause(deployment.id)
                state["deployment_id"] = deployment.id
                upcoming = getattr(getattr(deployment, "schedule", None), "upcoming_runs_at", None)
                print(f"created deployment {deployment.id} and paused it; next runs: {upcoming}")
            else:
                client.beta.deployments.update(state["deployment_id"], agent=agent_id,
                                               resources=resources(ids))
                print(f"deployment {state['deployment_id']} now mounts the snapshot of {snap['taken']}")
        except Exception:
            _delete_files(client, ids.values())
            raise
    previous = state.get("snapshot_file_ids") or []
    state.update(snapshot_file_ids=list(ids.values()), snapshot_taken=snap["taken"])
    _write(state_path, json.dumps(state, indent=2) + "\n")
    _delete_files(client, previous)
    return 0


def cmd_fetch(args) -> int:
    state = _load_state(Path(args.state))
    deployment_id = state.get("deployment_id")
    if not deployment_id:
        sys.exit("no deployment yet: run push --create first")
    household = Path(args.household).expanduser().resolve()
    out_dir = Path(args.out).expanduser() if args.out else household / "out"
    client = _client()
    runs = list(client.beta.deployment_runs.list(deployment_id=deployment_id))
    if not runs:
        print("the deployment has not run yet")
        return 0
    newest = max(runs, key=lambda r: str(getattr(r, "created_at", "")))
    if not getattr(newest, "session_id", None):
        error = getattr(newest, "error", None)
        print(f"the newest run started no session: {getattr(error, 'type', '?')}: "
              f"{getattr(error, 'message', '')}")
        return 1
    session = client.beta.sessions.retrieve(session_id=newest.session_id)
    if session.status in ("running", "rescheduling"):
        print(f"session {session.id} is still running; fetch again later")
        return 0
    _cost(client, session.id)
    with tempfile.TemporaryDirectory(prefix="deadline-watch-") as tmp:
        got = _fetch_report(client, session.id, Path(tmp))
    if got is None:
        print(f"open the session to see why: ant beta:sessions connect {session.id}")
        return 2
    name, text, output_id = got
    profile = parse_profile((household / "household-profile.md").read_text(encoding="utf-8"))
    # Computed from the register as it is now; it may have changed since the push.
    expected = expected_ids(household, _report_day(name, date.today().isoformat()), profile["country"])
    code = save_report(out_dir, name, text, expected, session.id)
    if args.delete_session:
        _delete_files(client, [output_id])
        client.beta.sessions.delete(session_id=session.id)
        print("deleted the session and its output file")
    return code


def cmd_forget(args) -> int:
    state_path = Path(args.state)
    state = _load_state(state_path)
    client = _client()
    if state.get("deployment_id"):
        client.beta.deployments.pause(state["deployment_id"])
        print(f"paused deployment {state['deployment_id']}")
    _delete_files(client, state.get("snapshot_file_ids") or [])
    state["snapshot_file_ids"] = []
    _write(state_path, json.dumps(state, indent=2) + "\n")
    print("deleted the uploaded snapshot; push and unpause to start again")
    return 0


# --------------------------------------------------------------------------

def main(argv: list | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="cookbook.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="print the request bodies and stop; no network, no credentials")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("check", help="offline lint of the agent files")
    sub.add_parser("sync", help="copy the plugin agent's text into the coordinator's prompt")
    p = sub.add_parser("snapshot", help="write the files a run would upload (offline)")
    p.add_argument("--household", required=True, help="the household folder")
    p.add_argument("--out", required=True, help="an empty folder for the snapshot")
    for name, text in (("run", "one session now"), ("push", "fresh snapshot for the deployment"),
                       ("fetch", "newest scheduled report"), ("forget", "pause and delete the snapshot")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--state", default=str(STATE), help="where push keeps the deployment and file IDs")
        if name == "forget":
            continue
        p.add_argument("--household", required=True, help="the household folder")
        if name in ("run", "push"):
            p.add_argument("--lock", default=str(LOCK), help="the claude-lock.json written by ant apply")
            p.add_argument("--dry-run", dest="sub_dry_run", action="store_true", help=argparse.SUPPRESS)
        if name in ("run", "fetch"):
            p.add_argument("--out", help="where to save the report; default <household>/out")
            p.add_argument("--delete-session", action="store_true",
                           help="after saving, delete the session and its output file")
        if name == "run":
            p.add_argument("--today", help="the report date, YYYY-MM-DD; default today on this computer")
        if name == "push":
            p.add_argument("--create", action="store_true", help="create the deployment (paused)")
            p.add_argument("--timezone", help="IANA time zone when the profile has none")
    args = parser.parse_args(argv)
    args.dry_run = args.dry_run or getattr(args, "sub_dry_run", False)
    if args.cmd is None:
        if args.dry_run:
            _print(plan())
            return 0
        parser.print_help()
        return 0
    commands = {"check": cmd_check, "sync": cmd_sync, "snapshot": cmd_snapshot, "run": cmd_run,
                "push": cmd_push, "fetch": cmd_fetch, "forget": cmd_forget}
    if args.dry_run and args.cmd not in ("run", "push"):
        parser.error("--dry-run goes alone or with run or push")
    return commands[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
