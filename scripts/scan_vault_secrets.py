#!/usr/bin/env python3
"""Scan vault draft notes under ~/Master/05-HERMES for key-like patterns.

Outputs one line per match: ``filepath:linenumber:pattern_name``.
Never prints the matched value. Master or the operator reviews false positives.

Patterns are imported from ``agent.redact`` (shared), not copied. PEM blocks are
scanned across lines. This script is NOT run in CI.
"""

from __future__ import annotations

import os
import sys

from agent.redact import (
    _BASE64_RE,
    _HEX_RE,
    _PREFIX_RE,
    _PRIVATE_KEY_RE,
    _JWT_RE,
    _is_high_entropy_secret_adjacent,
)

VAULT_DIR = os.path.expanduser("~/Master/05-HERMES")

# Pattern name -> compiled regex (in scan order)
PATTERNS = [
    ("vendor_api_key", _PREFIX_RE),
    ("private_key_pem", _PRIVATE_KEY_RE),
    ("jwt", _JWT_RE),
]


def _iter_lines(path: str):
    """Yield (lineno, line) for the file, grouping PEM blocks across lines."""
    try:
        fh = open(path, "r", encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"# skip {path}: {exc}", file=sys.stderr)
        return
    with fh:
        buf = []
        start_lineno = None
        for lineno, line in enumerate(fh, start=1):
            if "-----BEGIN" in line and "PRIVATE KEY" in line:
                start_lineno = lineno
                buf = [line]
                continue
            if buf:
                buf.append(line)
                if "-----END" in line and "PRIVATE KEY" in line:
                    yield start_lineno, "".join(buf)
                    buf = []
                    start_lineno = None
                continue
            yield lineno, line


def scan_line(line: str, lineno: int, path: str) -> list[tuple[int, str]]:
    """Return [(lineno, pattern_name)] for matches in this line. Never the matched value."""
    hits: list[tuple[int, str]] = []
    for name, rx in PATTERNS:
        for _m in rx.finditer(line):
            hits.append((lineno, name))
    # High-entropy hex/base64 adjacent to a secret keyword (whole-word keyword match).
    for rx, label in ((_HEX_RE, "high_entropy_hex"), (_BASE64_RE, "high_entropy_base64")):
        for m in rx.finditer(line):
            if _is_high_entropy_secret_adjacent(line, m.start(), m.end()):
                hits.append((lineno, label))
    return hits


def main() -> int:
    if not os.path.isdir(VAULT_DIR):
        print(f"vault dir not found: {VAULT_DIR}", file=sys.stderr)
        return 1

    count = 0
    for root, _dirs, files in os.walk(VAULT_DIR):
        for fname in sorted(files):
            path = os.path.join(root, fname)
            try:
                for lineno, line in _iter_lines(path):
                    for lineno_hit, pattern_name in scan_line(line, lineno, path):
                        print(f"{path}:{lineno_hit}:{pattern_name}")
                        count += 1
            except OSError as exc:
                print(f"# skip {path}: {exc}", file=sys.stderr)
    print(f"# scanned {count} pattern matches", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
