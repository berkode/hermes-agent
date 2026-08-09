"""Proxy Bejcapital agency agent APIs for the Hermes dashboard."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def agency_base_url() -> str:
    raw = os.environ.get("BEJCAPITAL_AGENCY_URL", "http://127.0.0.1:8088").strip()
    return raw.rstrip("/")


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    api_key = os.environ.get("AGENCY_API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


def _request(method: str, path: str, body: dict[str, Any] | None = None, *, timeout: float = 30.0) -> dict[str, Any]:
    url = f"{agency_base_url()}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
        except json.JSONDecodeError:
            parsed = {"detail": detail or exc.reason}
        return {"ok": False, "error": parsed.get("detail") or str(exc), "status": exc.code}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "available": False}


def get_agent_status() -> dict[str, Any]:
    out = _request("GET", "/api/agents/status")
    if "available" not in out:
        out["available"] = "error" not in out
    return out


def get_capabilities() -> dict[str, Any]:
    return _request("GET", "/api/agents/capabilities")


def list_runs(limit: int = 50, status: str | None = None) -> dict[str, Any]:
    qs = f"?limit={max(1, min(limit, 200))}"
    if status:
        qs += f"&status={urllib.parse.quote(status)}"
    return _request("GET", f"/api/agents/runs{qs}")


def get_run(run_id: str) -> dict[str, Any]:
    return _request("GET", f"/api/agents/runs/{urllib.parse.quote(run_id)}")


def create_run(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/api/agents/runs", payload)


def approve_run(run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", f"/api/agents/runs/{urllib.parse.quote(run_id)}/approve", payload)
