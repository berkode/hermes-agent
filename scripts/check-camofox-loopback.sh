#!/usr/bin/env bash
# Fail if Hermes launch docs/config/scripts publish Camofox 9377 on all interfaces.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/check-camofox-loopback.py" "$@"
