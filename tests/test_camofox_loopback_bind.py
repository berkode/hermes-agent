"""Camofox control API must not be published on all interfaces."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_camofox_launch_configs_bind_loopback() -> None:
    script = ROOT / "scripts" / "check-camofox-loopback.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "ok:" in proc.stdout
