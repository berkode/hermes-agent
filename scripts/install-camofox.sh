#!/usr/bin/env bash
# Wrapper — canonical script lives in bejcapital (deploy with the monorepo).
set -euo pipefail
BEJ="${BEJCAPITAL_ROOT:-$HOME/berkode/bejcapital}"
SCRIPT="$BEJ/app/scripts/install-camofox.sh"
if [[ ! -f "$SCRIPT" ]]; then
  echo "Missing $SCRIPT — git pull bejcapital first." >&2
  exit 1
fi
exec bash "$SCRIPT" "$@"
