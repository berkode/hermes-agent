"""Hermes tool: Bejcapital agency agent runtime and monitor APIs."""

from __future__ import annotations

import json
from typing import Any, Dict

from tools.registry import registry, tool_error


def bejcapital_platform_tool(args: Dict[str, Any], **_kw: Any) -> str:
    action = str(args.get("action") or "").strip()
    if not action:
        return tool_error("action is required")

    from hermes_cli import bejcapital_agency as agency

    if action == "agent_status":
        return json.dumps(agency.get_agent_status(), indent=2)
    if action == "capabilities":
        return json.dumps(agency.get_capabilities(), indent=2)
    if action == "list_runs":
        limit = int(args.get("limit") or 20)
        status = args.get("status")
        return json.dumps(agency.list_runs(limit=limit, status=str(status) if status else None), indent=2)
    if action == "get_run":
        run_id = str(args.get("run_id") or "").strip()
        if not run_id:
            return tool_error("run_id is required for get_run")
        return json.dumps(agency.get_run(run_id), indent=2)
    if action == "create_run":
        payload = args.get("payload")
        if not isinstance(payload, dict):
            return tool_error("payload object is required for create_run")
        return json.dumps(agency.create_run(payload), indent=2)
    if action == "approve_run":
        run_id = str(args.get("run_id") or "").strip()
        payload = args.get("payload")
        if not run_id or not isinstance(payload, dict):
            return tool_error("run_id and payload are required for approve_run")
        return json.dumps(agency.approve_run(run_id, payload), indent=2)

    return tool_error(f"unknown action: {action}")


BEJCAPITAL_PLATFORM_SCHEMA = {
    "type": "function",
    "function": {
        "name": "bejcapital_platform",
        "description": (
            "Bejcapital agency backend (not execution): agent runs, capabilities, approvals. "
            "Fleet start/stop uses Hermes Services tab — do not submit orders via this tool."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "agent_status",
                        "capabilities",
                        "list_runs",
                        "get_run",
                        "create_run",
                        "approve_run",
                    ],
                    "description": "Agency API operation",
                },
                "run_id": {"type": "string", "description": "Agent run UUID"},
                "limit": {"type": "integer", "description": "Max runs for list_runs"},
                "status": {
                    "type": "string",
                    "description": "Filter list_runs by run status",
                },
                "payload": {
                    "type": "object",
                    "description": "JSON body for create_run or approve_run",
                },
            },
            "required": ["action"],
        },
    },
}


registry.register(
    name="bejcapital_platform",
    toolset="bejcapital",
    schema=BEJCAPITAL_PLATFORM_SCHEMA,
    handler=bejcapital_platform_tool,
    emoji="🏦",
)
