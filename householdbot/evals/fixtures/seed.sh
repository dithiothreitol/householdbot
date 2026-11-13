#!/usr/bin/env bash
# Seed the synthetic household into the eval workspace (the current folder).
# Sourced by each case's setup.sh:
#   . "$(dirname "${BASH_SOURCE[0]}")/../../fixtures/seed.sh" <full|empty|conflict|broken|none>
# Everything it writes is invented; see make_household.py.
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
case "${1:-full}" in
  full)     "$HB_PY" "$HB_FIXTURES/make_household.py" . >/dev/null ;;
  empty)    "$HB_PY" "$HB_FIXTURES/make_household.py" . --empty >/dev/null ;;
  conflict) "$HB_PY" "$HB_FIXTURES/make_household.py" . --conflict >/dev/null ;;
  broken)   "$HB_PY" "$HB_FIXTURES/make_household.py" . --broken >/dev/null ;;
  none)     : ;;
  *) echo "seed.sh: unknown mode $1" >&2; exit 1 ;;
esac
