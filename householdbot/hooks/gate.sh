#!/bin/sh
# HouseholdBot write gate (PreToolUse). Reads the hook input on standard input, skips calls
# that cannot concern the gate, finds Python 3.8+ and runs gate.py. python3 can be a
# Microsoft Store placeholder on Windows, so each candidate is tried. Without Python the
# hook says nothing and the host's own permission flow applies; the scripts still refuse
# a write without a previewed token.
input=$(cat)
case "$input" in
  *commit*--confirm*|*'"file_path"'*|*'"notebook_path"'*) ;;
  *) exit 0 ;;
esac
here=$(dirname "$0")
for c in python3 python py; do
  where=$(command -v "$c" 2>/dev/null) || continue
  case "$where" in *WindowsApps*) continue ;; esac
  if "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
    printf '%s' "$input" | "$c" "$here/gate.py"
    exit 0
  fi
done
exit 0
