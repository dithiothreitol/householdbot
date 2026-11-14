#!/usr/bin/env bash
# Seed the synthetic household into the eval workspace (the current folder).
# Sourced by each case's setup.sh with one or more modes:
#   . "$(dirname "${BASH_SOURCE[0]}")/../../fixtures/seed.sh" full statement
# Household modes: full | full-en | gb | empty | conflict | broken | none
#   everyday (after full or full-en): profile Everyday life, chores, lists, five more papers
#   (full, empty, conflict and broken write a Polish household; full-en writes it in English)
#   gb writes a household in England (GB pack, GBP), see make_household_gb.py
# Statement modes, written to inbox/wyciag.csv:
#   statement (Polish layout, Windows-1250) | statement-gap (middle month missing) | statement-en (English layout)
# Everything it writes is invented; see make_household.py and make_statement.py.
set -e
HB_FIXTURES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HB_PY=""
for c in python3 python py; do
  where="$(command -v "$c" 2>/dev/null || true)"
  # On Windows, python3 can be a Microsoft Store placeholder that never runs Python; skip it.
  case "$where" in ""|*WindowsApps*) continue ;; esac
  if "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
    HB_PY="$c"
    break
  fi
done
if [ -z "$HB_PY" ]; then
  echo "seed.sh: no Python 3.8+ found on PATH" >&2
  exit 1
fi
[ "$#" -eq 0 ] && set -- full
for mode in "$@"; do
  case "$mode" in
    full)          "$HB_PY" "$HB_FIXTURES/make_household.py" . >/dev/null ;;
    full-en)       "$HB_PY" "$HB_FIXTURES/make_household.py" . --lang en >/dev/null ;;
    gb)            "$HB_PY" "$HB_FIXTURES/make_household_gb.py" . >/dev/null ;;
    empty)         "$HB_PY" "$HB_FIXTURES/make_household.py" . --empty >/dev/null ;;
    conflict)      "$HB_PY" "$HB_FIXTURES/make_household.py" . --conflict >/dev/null ;;
    broken)        "$HB_PY" "$HB_FIXTURES/make_household.py" . --broken >/dev/null ;;
    statement)     "$HB_PY" "$HB_FIXTURES/make_statement.py" inbox/wyciag.csv --format a >/dev/null ;;
    statement-gap) "$HB_PY" "$HB_FIXTURES/make_statement.py" inbox/wyciag.csv --format b --gap >/dev/null ;;
    statement-en)  "$HB_PY" "$HB_FIXTURES/make_statement.py" inbox/statement.csv --format c >/dev/null ;;
    everyday)      "$HB_PY" "$HB_FIXTURES/make_everyday.py" . >/dev/null ;;
    none)          : ;;
    *) echo "seed.sh: unknown mode $mode" >&2; exit 1 ;;
  esac
done
