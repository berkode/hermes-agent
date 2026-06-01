#!/usr/bin/env bash
# Recreate .venv with MacPorts Python 3.13 and install Hermes (uv sync).
set -euo pipefail

REPO="${HERMES_REPO:-$HOME/berkode/hermes-agent}"
cd "$REPO"

export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO/.uv-cache}"

MACPORTS_PY="${HERMES_PYTHON:-/opt/local/bin/python3.13}"
if [ ! -x "$MACPORTS_PY" ]; then
  MACPORTS_PY="/opt/local/bin/python3"
fi
if [ ! -x "$MACPORTS_PY" ]; then
  echo "No MacPorts python3 found. Install: sudo port install python313" >&2
  exit 1
fi

echo "Using interpreter: $("$MACPORTS_PY" --version) ($MACPORTS_PY)"

if [ -d .venv ] && [ "${HERMES_VENV_RECREATE:-0}" = "1" ]; then
  rm -rf .venv
fi

if [ ! -d .venv ]; then
  uv venv --python "$MACPORTS_PY" .venv
fi

uv sync
echo ""
echo "Verify:"
echo "  $REPO/.venv/bin/python3 --version"
echo "  $REPO/.venv/bin/hermes --version"
echo ""
echo "Install CLI wrapper:"
echo "  ln -sf $REPO/scripts/hermes-wrapper.sh ~/.local/bin/hermes"
