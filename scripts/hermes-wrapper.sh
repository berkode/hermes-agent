#!/bin/sh
# Pin Hermes CLI to the repo .venv (MacPorts CPython 3.13 via uv), not PATH python3.
HERMES_REPO="${HERMES_REPO:-$HOME/berkode/hermes-agent}"
VENV_PY="${HERMES_REPO}/.venv/bin/python3"
CLI="${HERMES_REPO}/.venv/bin/hermes"

if [ ! -x "$VENV_PY" ]; then
  echo "hermes: missing $VENV_PY — run: cd $HERMES_REPO && uv sync" >&2
  exit 1
fi

export UV_CACHE_DIR="${UV_CACHE_DIR:-$HERMES_REPO/.uv-cache}"
export VIRTUAL_ENV="${HERMES_REPO}/.venv"
export PATH="${HERMES_REPO}/.venv/bin:${PATH}"

# Never delegate to bare /opt/local/bin/python3 for the CLI itself.
exec "$CLI" "$@"
