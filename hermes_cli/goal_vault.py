"""Obsidian vault checkpoints for /goal state.

Persists standing goals to the MASTER vault so quota/API/model failures do
not strand progress. Checkpoints live under::

    <vault>/05-HERMES/control-room/active-goals/LATEST.md
    <vault>/05-HERMES/control-room/goal-history/<timestamp>-<slug>.md

The obsidian skill and master-second-brain skill both reference this layout.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hermes_cli.goals import GoalState

logger = logging.getLogger(__name__)

_ACTIVE_DIR = Path("05-HERMES") / "control-room" / "active-goals"
_HISTORY_DIR = Path("05-HERMES") / "control-room" / "goal-history"
_LATEST_NAME = "LATEST.md"


def resolve_vault_path() -> Optional[Path]:
    """Return the Obsidian vault path from env or config, or None."""
    raw = (os.environ.get("OBSIDIAN_VAULT_PATH") or "").strip()
    if not raw:
        try:
            from hermes_cli.config import load_config

            cfg = load_config() or {}
            raw = (
                (cfg.get("skills") or {}).get("obsidian_vault_path")
                or (cfg.get("obsidian") or {}).get("vault_path")
                or ""
            ).strip()
        except Exception:
            raw = ""
    if not raw:
        fallback = Path.home() / "Master"
        if fallback.is_dir():
            return fallback
        return None
    path = Path(raw).expanduser()
    return path if path.is_dir() else None


def _slug(text: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").strip().lower()).strip("-")
    return (slug[:limit] or "goal")


def _format_checkpoint(
    state: "GoalState",
    *,
    session_id: str,
    event: str,
    error: Optional[str] = None,
    transcript_tail: Optional[str] = None,
) -> str:
    now = datetime.now(tz=timezone.utc).astimezone()
    subgoals_block = ""
    if state.subgoals:
        lines = "\n".join(f"- {i}. {s}" for i, s in enumerate(state.subgoals, start=1))
        subgoals_block = f"\n## Subgoals\n{lines}\n"
    err_block = f"\n## Last error\n{error}\n" if error else ""
    tail_block = ""
    if transcript_tail and transcript_tail.strip():
        tail_block = f"\n## Transcript tail\n```\n{transcript_tail.strip()}\n```\n"
    paused = f"\nPaused reason: {state.paused_reason}" if state.paused_reason else ""
    return f"""---
hermes_goal: true
session_id: {session_id}
status: {state.status}
turns_used: {state.turns_used}
max_turns: {state.max_turns}
event: {event}
updated_at: {now.isoformat()}
---

# Standing goal

{state.goal}
{subgoals_block}
## Progress

- Turns: {state.turns_used}/{state.max_turns}
- Last verdict: {state.last_verdict or "(none)"}
- Last reason: {state.last_reason or "(none)"}{paused}
{err_block}{tail_block}
## Resume

In Hermes: `/goal resume` (re-queues the next continuation step).

Session id: `{session_id}`
"""


def write_goal_checkpoint(
    state: "GoalState",
    session_id: str,
    *,
    event: str = "update",
    error: Optional[str] = None,
    transcript_tail: Optional[str] = None,
    history_event: bool = False,
) -> Optional[Path]:
    """Write LATEST.md and optionally append a history snapshot. Best-effort."""
    vault = resolve_vault_path()
    if vault is None or not session_id:
        return None
    body = _format_checkpoint(
        state,
        session_id=session_id,
        event=event,
        error=error,
        transcript_tail=transcript_tail,
    )
    try:
        active_dir = vault / _ACTIVE_DIR
        active_dir.mkdir(parents=True, exist_ok=True)
        latest = active_dir / _LATEST_NAME
        latest.write_text(body, encoding="utf-8")
        written = latest
        if history_event:
            hist_dir = vault / _HISTORY_DIR
            hist_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d-%H%M%S")
            hist_path = hist_dir / f"{stamp}-{_slug(state.goal)}.md"
            hist_path.write_text(body, encoding="utf-8")
        return written
    except Exception as exc:
        logger.debug("goal vault checkpoint failed: %s", exc)
        return None


def read_latest_goal_checkpoint() -> Optional[Dict[str, Any]]:
    """Parse LATEST.md frontmatter + goal text. Returns None if missing."""
    vault = resolve_vault_path()
    if vault is None:
        return None
    latest = vault / _ACTIVE_DIR / _LATEST_NAME
    if not latest.is_file():
        return None
    try:
        text = latest.read_text(encoding="utf-8")
    except Exception:
        return None
    meta: Dict[str, Any] = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" not in line:
                    continue
                key, _, val = line.partition(":")
                meta[key.strip()] = val.strip()
            body = parts[2]
    goal = ""
    for line in body.splitlines():
        if line.startswith("# Standing goal"):
            continue
        if line.startswith("## "):
            break
        if line.strip():
            goal = line.strip()
            break
    if not goal:
        return None
    meta["goal"] = goal
    return meta


__all__ = [
    "resolve_vault_path",
    "write_goal_checkpoint",
    "read_latest_goal_checkpoint",
]
