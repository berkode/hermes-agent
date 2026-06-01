#!/usr/bin/env bash
# Create or refresh the MASTER Obsidian vault layout (default: ~/Master).
# Prefer: hermes master init

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VAULT="${MASTER_VAULT_PATH:-$HOME/Master}"

if [[ $# -ge 1 && "${1}" != --* ]]; then
  VAULT="$1"
  shift
fi

exec python3 "${REPO_ROOT}/optional-skills/productivity/master-second-brain/scripts/master_scaffold.py" \
  --vault-path "${VAULT}" \
  --source "${SCRIPT_DIR}" \
  "$@"
