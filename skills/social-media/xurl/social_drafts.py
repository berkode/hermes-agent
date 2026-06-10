"""Social draft queue for X/Twitter via xurl.

Draft posts are stored as JSONL in app/data/social_drafts/queue.jsonl.
When xurl OAuth is ready, queued drafts can be published via `xurl post`.

Usage:
    python -m app.agency.social_drafts add "Hello world!"
    python -m app.agency.social_drafts list
    python -m app.agency.social_drafts publish <id>
    python -m app.agency.social_drafts delete <id>
    python -m app.agency.social_drafts status   # xurl auth check
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "social_drafts"
QUEUE_FILE = DATA_DIR / "queue.jsonl"
SENT_FILE = DATA_DIR / "sent.jsonl"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class DraftStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class Draft(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    text: str
    status: DraftStatus = DraftStatus.DRAFT
    media_ids: list[str] = Field(default_factory=list)
    reply_to: Optional[str] = None
    quote_of: Optional[str] = None
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    sent_at: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_all(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _write_all(path: Path, rows: list[dict]) -> None:
    _ensure_data_dir()
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )


def _append_row(path: Path, row: dict) -> None:
    _ensure_data_dir()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Queue operations
# ---------------------------------------------------------------------------


def add_draft(
    text: str,
    media_ids: Optional[list[str]] = None,
    reply_to: Optional[str] = None,
    quote_of: Optional[str] = None,
) -> Draft:
    """Create a new draft and append it to the queue."""
    draft = Draft(
        text=text,
        media_ids=media_ids or [],
        reply_to=reply_to,
        quote_of=quote_of,
    )
    _append_row(QUEUE_FILE, draft.model_dump())
    logger.info("Draft %s added: %s", draft.id, draft.text[:60])
    return draft


def list_drafts(status: Optional[DraftStatus] = None) -> list[Draft]:
    """Return drafts, optionally filtered by status."""
    rows = _read_all(QUEUE_FILE)
    drafts = [Draft(**r) for r in rows]
    if status:
        drafts = [d for d in drafts if d.status == status]
    return drafts


def get_draft(draft_id: str) -> Optional[Draft]:
    """Look up a draft by id."""
    for d in list_drafts():
        if d.id == draft_id:
            return d
    return None


def update_draft(draft_id: str, **kwargs) -> Optional[Draft]:
    """Update fields on an existing draft."""
    rows = _read_all(QUEUE_FILE)
    updated = None
    for row in rows:
        if row.get("id") == draft_id:
            row.update(kwargs)
            row["updated_at"] = datetime.now(timezone.utc).isoformat()
            updated = Draft(**row)
            break
    if updated:
        _write_all(QUEUE_FILE, rows)
    return updated


def delete_draft(draft_id: str) -> bool:
    """Remove a draft from the queue. Returns True if found."""
    rows = _read_all(QUEUE_FILE)
    filtered = [r for r in rows if r.get("id") != draft_id]
    if len(filtered) == len(rows):
        return False
    _write_all(QUEUE_FILE, filtered)
    return True


# ---------------------------------------------------------------------------
# xurl integration
# ---------------------------------------------------------------------------


def xurl_check() -> dict:
    """Check xurl availability and auth status."""
    result: dict = {"installed": False, "authenticated": False, "detail": ""}
    try:
        r = subprocess.run(
            ["xurl", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        result["installed"] = r.returncode == 0
    except FileNotFoundError:
        result["detail"] = "xurl not found on PATH"
        return result
    except subprocess.TimeoutExpired:
        result["detail"] = "xurl --help timed out"
        return result

    r = subprocess.run(
        ["xurl", "auth", "status"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    output = r.stdout + r.stderr
    result["detail"] = output.strip()
    result["authenticated"] = "oauth2" in output.lower() and "none" not in output.lower()
    return result


def publish_draft(draft_id: str, dry_run: bool = False) -> Draft:
    """Publish a draft via xurl. Updates status to sent/failed."""
    draft = get_draft(draft_id)
    if not draft:
        raise ValueError(f"Draft {draft_id} not found")

    if draft.status == DraftStatus.SENT:
        logger.info("Draft %s already sent, skipping", draft_id)
        return draft

    check = xurl_check()
    if not check["installed"]:
        raise RuntimeError("xurl is not installed")
    if not check["authenticated"]:
        raise RuntimeError(
            "xurl OAuth not configured. "
            "Run `xurl auth apps add` and `xurl auth oauth2` manually first."
        )

    cmd = ["xurl"]
    if draft.reply_to:
        cmd += ["reply", draft.reply_to]
    elif draft.quote_of:
        cmd += ["quote", draft.quote_of]
    else:
        cmd += ["post"]

    if draft.media_ids:
        for mid in draft.media_ids:
            cmd += ["--media-id", mid]

    cmd.append(draft.text)

    if dry_run:
        logger.info("[dry-run] would run: %s", " ".join(cmd))
        return update_draft(
            draft_id,
            status=DraftStatus.QUEUED,
            error="dry-run: not sent",
        )

    logger.info("Publishing draft %s: %s", draft_id, " ".join(cmd))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            sent_at = datetime.now(timezone.utc).isoformat()
            draft = update_draft(
                draft_id,
                status=DraftStatus.SENT,
                sent_at=sent_at,
            )
            if draft:
                _append_row(SENT_FILE, draft.model_dump())
            logger.info("Draft %s sent successfully", draft_id)
        else:
            error_msg = (r.stderr or r.stdout or "unknown error").strip()
            draft = update_draft(
                draft_id,
                status=DraftStatus.FAILED,
                error=error_msg,
            )
            logger.error("Draft %s failed: %s", draft_id, error_msg)
    except subprocess.TimeoutExpired:
        draft = update_draft(
            draft_id,
            status=DraftStatus.FAILED,
            error="xurl timed out after 30s",
        )
        logger.error("Draft %s timed out", draft_id)

    return draft


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _fmt_draft(d: Draft) -> str:
    status_icon = {
        DraftStatus.DRAFT: "[DRAFT]",
        DraftStatus.QUEUED: "[QUEUE]",
        DraftStatus.SENT: "[SENT] ",
        DraftStatus.FAILED: "[FAIL] ",
    }.get(d.status, "[?]")
    meta = f" reply_to={d.reply_to}" if d.reply_to else ""
    meta += f" media={','.join(d.media_ids)}" if d.media_ids else ""
    err = f"\n  error: {d.error}" if d.error else ""
    return (
        f"{status_icon} [{d.id}] {d.text[:80]}{'...' if len(d.text) > 80 else ''}\n"
        f"  status={d.status.value}  created={d.created_at}{meta}{err}"
    )


def main() -> None:
    """Simple CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Social draft queue for X/Twitter")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a draft post")
    p_add.add_argument("text", help="Post text")
    p_add.add_argument("--media-id", action="append", default=[], help="Media ID (repeatable)")
    p_add.add_argument("--reply-to", help="Post ID to reply to")
    p_add.add_argument("--quote-of", help="Post ID to quote")

    # list
    p_list = sub.add_parser("list", help="List drafts")
    p_list.add_argument("--status", choices=[s.value for s in DraftStatus], help="Filter by status")

    # publish
    p_pub = sub.add_parser("publish", help="Publish a draft via xurl")
    p_pub.add_argument("draft_id", help="Draft ID to publish")
    p_pub.add_argument("--dry-run", action="store_true", help="Show command without sending")

    # delete
    p_del = sub.add_parser("delete", help="Delete a draft")
    p_del.add_argument("draft_id", help="Draft ID to delete")

    # status
    sub.add_parser("status", help="Check xurl auth status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "add":
        d = add_draft(
            text=args.text,
            media_ids=args.media_id or None,
            reply_to=args.reply_to,
            quote_of=args.quote_of,
        )
        print(f"Added draft [{d.id}]: {d.text[:80]}")

    elif args.command == "list":
        status = DraftStatus(args.status) if args.status else None
        drafts = list_drafts(status=status)
        if not drafts:
            print("No drafts found.")
        else:
            for d in drafts:
                print(_fmt_draft(d))
                print()

    elif args.command == "publish":
        try:
            d = publish_draft(args.draft_id, dry_run=args.dry_run)
            print(_fmt_draft(d))
        except (ValueError, RuntimeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "delete":
        if delete_draft(args.draft_id):
            print(f"Deleted draft {args.draft_id}")
        else:
            print(f"Draft {draft_id} not found", file=sys.stderr)
            sys.exit(1)

    elif args.command == "status":
        check = xurl_check()
        print(f"xurl installed: {check['installed']}")
        print(f"xurl authenticated: {check['authenticated']}")
        print(f"detail: {check['detail']}")


if __name__ == "__main__":
    main()
