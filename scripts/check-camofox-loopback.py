#!/usr/bin/env python3
"""Fail if first-party launch configs publish Camofox 9377 on all interfaces."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORT = "9377"

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "__pycache__",
    "external",
    "_retired",
}
SKIP_SUFFIXES = {".lock", ".png", ".jpg", ".webp", ".woff", ".woff2"}
SELF_NAMES = {"check-camofox-loopback.py", "check-camofox-loopback.sh"}

SCAN_SUFFIXES = {
    ".sh",
    ".bash",
    ".service",
    ".timer",
    ".yml",
    ".yaml",
    ".cjs",
    ".js",
    ".py",
    ".env",
    ".example",
    ".md",
    ".toml",
    ".json",
}

# Host-port publish of 9377 without a loopback bind address.
UNSAFE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "docker -p 9377:9377 (all interfaces)",
        re.compile(r"""(?x)
            -p(?:\s+|=)
            ["']?
            (?:0\.0\.0\.0:|\[::\]:|\*:)?
            9377:9377
        """),
    ),
    (
        "compose ports 9377:9377 (all interfaces)",
        re.compile(r"""(?x)
            (?:
                ports:\s*\[?\s*["']9377:9377["']
                |
                ["']9377:9377["']
                |
                -\s+9377:9377\b
            )
        """),
    ),
    (
        "explicit 0.0.0.0:9377",
        re.compile(r"0\.0\.0\.0:9377\b"),
    ),
    (
        "IPv6 all-iface [::]:9377",
        re.compile(r"\[::\]:9377\b"),
    ),
    (
        "systemd ListenStream=9377 without loopback",
        re.compile(r"ListenStream=(?:0\.0\.0\.0:)?9377\b"),
    ),
)

SAFE_DOCKER_PUBLISH = re.compile(
    r"""-p(?:\s+|=)["']?127\.0\.0\.1:\d+:9377"""
)


def iter_scan_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES or part.endswith("_retired") for part in path.parts):
            continue
        if path.name in SELF_NAMES:
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        if path.suffix not in SCAN_SUFFIXES and path.name not in {
            "Dockerfile",
            "docker-compose.yml",
            "compose.yml",
        }:
            continue
        files.append(path)
    return files


def line_is_comment(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("#") or stripped.startswith("//")


def findings_for_text(rel: str, text: str) -> list[str]:
    hits: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line_is_comment(line):
            continue
        if SAFE_DOCKER_PUBLISH.search(line) and "0.0.0.0:9377" not in line:
            # Loopback docker publish still contains the substring 9377:9377.
            continue
        for label, pattern in UNSAFE_PATTERNS:
            if pattern.search(line):
                hits.append(f"{rel}:{lineno}: {label}: {line.strip()}")
    return hits


def run_self_test() -> None:
    unsafe_samples = [
        'docker run -p 9377:9377 -e CAMOFOX_PORT=9377 img',
        'docker run -p 0.0.0.0:9377:9377 img',
        'ports: ["9377:9377"]',
        '- "9377:9377"',
        "ListenStream=9377",
        "app.listen on 0.0.0.0:9377",
    ]
    safe_samples = [
        'docker run -p 127.0.0.1:9377:9377 -e CAMOFOX_PORT=9377 img',
        '-p "${BIND}:${PORT}:9377"',
        "CAMOFOX_URL=http://127.0.0.1:9377",
        "Environment=CAMOFOX_URL=http://127.0.0.1:9377",
        "curl -sf http://127.0.0.1:9377/health",
        'ListenStream=127.0.0.1:9377',
    ]
    for sample in unsafe_samples:
        hits = findings_for_text("self-test", sample)
        if not hits:
            raise SystemExit(f"self-test missed unsafe sample: {sample!r}")
    for sample in safe_samples:
        hits = findings_for_text("self-test", sample)
        if hits:
            raise SystemExit(f"self-test false positive on {sample!r}: {hits}")


def main() -> int:
    run_self_test()
    all_hits: list[str] = []
    for path in iter_scan_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(ROOT).as_posix()
        all_hits.extend(findings_for_text(rel, text))
    if all_hits:
        print("Camofox 9377 published on all interfaces:", file=sys.stderr)
        for hit in all_hits:
            print(f"  {hit}", file=sys.stderr)
        print(
            "Bind loopback only, e.g. -p 127.0.0.1:9377:9377 or --host 127.0.0.1.",
            file=sys.stderr,
        )
        return 1
    print(f"ok: no all-iface {PORT} publish in Hermes launch/docs/config")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
