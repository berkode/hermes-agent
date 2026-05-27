"""Dashboard control of ``~/.hermes/scripts/hermes-services.sh`` (manual stack only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from hermes_constants import get_hermes_home

try:
    from hermes_cli.bejcapital_fleet import KNOWN_SERVICES, SERVICE_ORDER
except ImportError:
    KNOWN_SERVICES = frozenset(
        {"pimono", "pimono-proxy", "bejmind", "hermes-gateway"}
    )
    SERVICE_ORDER = list(KNOWN_SERVICES)
_BULK_ACTIONS = frozenset({"start-llm", "start-all", "stop-all"})
_PER_SERVICE_ACTIONS = frozenset({"start", "stop", "toggle"})


def _fleet_python() -> Path:
    agent_root = Path(
        os.environ.get(
            "HERMES_AGENT_ROOT",
            Path(__file__).resolve().parents[1],
        )
    ).expanduser()
    for candidate in (
        agent_root / "venv" / "bin" / "python",
        agent_root / ".venv" / "bin" / "python",
    ):
        if candidate.is_file():
            return candidate
    return Path(sys.executable)


def _run(argv: list[str], timeout: int = 300) -> tuple[int, str]:
    import os
    import sys

    proc = subprocess.run(
        [str(_fleet_python()), "-m", "hermes_cli.bejcapital_fleet", *argv],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(Path(__file__).resolve().parents[1].parent),
        env={
            **os.environ,
            "PYTHONPATH": str(Path(__file__).resolve().parents[1].parent),
        },
    )
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode, out


def get_status_json() -> dict[str, Any]:
    """Return ``{"services": {name: bool}}`` or an error payload."""
    code, out = _run(["status-json"])
    if code != 0:
        return {"available": True, "error": out, "services": {}}
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        return {"available": True, "error": out, "services": {}}
    body["available"] = True
    return body


def run_services_action(action: str, service: Optional[str] = None) -> dict[str, Any]:
    """Run fleet control; always attach fresh status when possible."""
    action = (action or "").strip()
    if action in _BULK_ACTIONS:
        argv = [action]
    elif action in _PER_SERVICE_ACTIONS:
        name = (service or "").strip()
        if name not in KNOWN_SERVICES:
            return {
                "ok": False,
                "message": f"Unknown service: {name!r}",
                "status": get_status_json(),
            }
        argv = [action, name]
    else:
        return {
            "ok": False,
            "message": f"Unknown action: {action!r}",
            "status": get_status_json(),
        }

    code, message = _run(argv)
    status = get_status_json()
    return {"ok": code == 0, "message": message, "status": status}
