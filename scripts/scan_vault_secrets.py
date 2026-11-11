#!/usr/bin/env python3
"""Scan vault draft notes under ~/Master/05-HERMES for key-like patterns.

Outputs one line per match: ``filepath:linenumber:pattern_name``.
Never prints the matched value. Master or the operator reviews false positives.

Patterns mirror agent/redact.py:
  - API key prefixes (sk-, ghp_, xox, AWS, Stripe, etc.)
  - Private key PEM blocks
  - JWTs
  - High-entropy hex/base64 adjacent to secret keywords
"""

from __future__ import annotations

import os
import re
import sys

# --- Patterns (mirrored from agent/redact.py) ---
_PREFIX_PATTERNS = [
    r"sk-[A-Za-z0-9_-](?:\.?[A-Za-z0-9_-]){9,}",
    r"ctx7sk-[A-Za-z0-9_-]{10,}",
    r"ghp_[A-Za-z0-9]{10,}",
    r"github_pat_[A-Za-z0-9_]{10,}",
    r"gho_[A-Za-z0-9]{10,}",
    r"ghu_[A-Za-z0-9]{10,}",
    r"ghs_[A-Za-z0-9]{10,}",
    r"ghr_[A-Za-z0-9]{10,}",
    r"xapp-\d+-[A-Za-z0-9-]{10,}",
    r"xox[baprs]-[A-Za-z0-9-]{10,}",
    r"AIza[A-Za-z0-9_-]{30,}",
    r"pplx-[A-Za-z0-9]{10,}",
    r"fal_[A-Za-z0-9_-]{10,}",
    r"fc-[A-Za-z0-9]{10,}",
    r"bb_live_[A-Za-z0-9_-]{10,}",
    r"gAAAA[A-Za-z0-9_=-]{20,}",
    r"AKIA[A-Z0-9]{16}",
    r"sk_live_[A-Za-z0-9]{10,}",
    r"sk_test_[A-Za-z0-9]{10,}",
    r"rk_live_[A-Za-z0-9]{10,}",
    r"SG\.[A-Za-z0-9_-]{10,}",
    r"hf_[A-Za-z0-9]{10,}",
    r"r8_[A-Za-z0-9]{10,}",
    r"npm_[A-Za-z0-9]{10,}",
    r"pypi-[A-Za-z0-9_-]{10,}",
    r"dop_v1_[A-Za-z0-9]{10,}",
    r"doo_v1_[A-Za-z0-9]{10,}",
    r"am_(?:org_)?[A-Za-z0-9]{20,}",
    r"sk_[A-Za-z0-9_]{10,}",
    r"tvly-[A-Za-z0-9]{10,}",
    r"exa_[A-Za-z0-9]{10,}",
    r"gsk_[A-Za-z0-9]{10,}",
    r"syt_[A-Za-z0-9]{10,}",
    r"retaindb_[A-Za-z0-9]{10,}",
    r"hsk-[A-Za-z0-9]{10,}",
    r"mem0_[A-Za-z0-9]{10,}",
    r"brv_[A-Za-z0-9]{10,}",
    r"xai-[A-Za-z0-9]{30,}",
    r"ntn_[A-Za-z0-9]{10,}",
    r"fw-[A-Za-z0-9]{30,}",
    r"fw_[A-Za-z0-9]{30,}",
    r"fpk_[A-Za-z0-9]{30,}",
    r"glpat-[A-Za-z0-9_\-]{10,}",
    r"gloas-[A-Za-z0-9_\-]{10,}",
    r"gldt-[A-Za-z0-9_\-]{10,}",
    r"glrt-[A-Za-z0-9_.\-]{10,}",
    r"glrtr-[A-Za-z0-9_.\-]{10,}",
    r"glcbt-[A-Za-z0-9_\-]{10,}",
    r"glptt-[A-Za-z0-9_\-]{10,}",
    r"glft-[A-Za-z0-9_\-]{10,}",
    r"glimt-[A-Za-z0-9_\-]{10,}",
    r"glagent-[A-Za-z0-9_\-]{10,}",
    r"glsoat-[A-Za-z0-9_\-]{10,}",
    r"glffct-[A-Za-z0-9_\-]{10,}",
    r"glwt-[A-Za-z0-9_\-]{10,}",
    r"GR1348941[A-Za-z0-9_\-]{10,}",
    r"pk-lf-[A-Za-z0-9\-]{8,}",
]
_PREFIX_RE = re.compile(r"(?<![A-Za-z0-9_-])(" + "|".join(_PREFIX_PATTERNS) + r")(?![A-Za-z0-9_-])")

_PRIVATE_KEY_RE = re.compile(r"-----BEGIN[A-Z ]*PRIVATE KEY-----[\s\S]*?-----END[A-Z ]*PRIVATE KEY-----")
_JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]{10,}(?:\.[A-Za-z0-9_=-]{4,}){0,2}")

_SECRET_ADJACENT_KEYWORDS = frozenset({
    "secret", "token", "key", "password", "passwd", "pass", "pw",
    "credential", "apikey", "api_key", "auth", "private", "signing",
})
_HEX_RE = re.compile(r"\b[0-9a-fA-F]{40,}\b")
_BASE64_RE = re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")

# Pattern name -> compiled regex (in scan order)
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("vendor_api_key", _PREFIX_RE),
    ("private_key_pem", _PRIVATE_KEY_RE),
    ("jwt", _JWT_RE),
]

VAULT_DIR = os.path.expanduser("~/Master/05-HERMES")


def _is_high_entropy_secret_adjacent(text: str, start: int, end: int) -> bool:
    window = 80
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    ctx = text[lo:hi].lower()
    return any(kw in ctx for kw in _SECRET_ADJACENT_KEYWORDS)


def scan_line(line: str, lineno: int, path: str) -> list[tuple[int, str]]:
    """Return [(lineno, pattern_name)] for matches in this line. Never the matched value."""
    hits: list[tuple[int, str]] = []
    for name, rx in PATTERNS:
        for m in rx.finditer(line):
            hits.append((lineno, name))
    # High-entropy hex/base64 adjacent to a secret keyword.
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
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    for lineno, line in enumerate(fh, start=1):
                        for lineno_hit, pattern_name in scan_line(line, lineno, path):
                            print(f"{path}:{lineno_hit}:{pattern_name}")
                            count += 1
            except OSError as exc:
                print(f"# skip {path}: {exc}", file=sys.stderr)
    print(f"# scanned {count} pattern matches", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
