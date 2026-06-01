#!/usr/bin/env python3
"""Install MASTER second-brain cron jobs (paused by default)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SKILL_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_MANIFEST = _SKILL_ROOT / "references" / "cron-manifest.yaml"
_DEFAULT_VAULT = Path.home() / "Master"


def _load_workflow_prompt(workflows_dir: Path, filename: str) -> str:
    path = workflows_dir / filename
    if not path.is_file():
        raise FileNotFoundError(f"Workflow not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def _load_manifest(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "jobs" not in data:
        raise ValueError(f"Invalid manifest: {path}")
    return data


def _create_job(
    *,
    schedule: str,
    prompt: str,
    name: str,
    deliver: str,
    profile: str | None,
    workdir: Path,
    skills: List[str],
    enabled: bool,
    dry_run: bool,
) -> str:
    if dry_run:
        state = "enabled" if enabled else "paused"
        return f"[dry-run] {name} ({schedule}) -> {deliver} [{state}]"

    sys.path.insert(0, str(_REPO_ROOT))
    from cron.jobs import create_job, pause_job

    job = create_job(
        schedule=schedule,
        prompt=prompt,
        name=name,
        deliver=deliver,
        skills=skills,
        workdir=str(workdir),
        profile=profile,
    )
    job_id = job["id"]
    if not enabled:
        pause_job(job_id)
    return job_id


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install MASTER cron templates.")
    parser.add_argument("--vault-path", type=Path, default=_DEFAULT_VAULT)
    parser.add_argument("--manifest", type=Path, default=_DEFAULT_MANIFEST)
    parser.add_argument("--profile", default="bej")
    parser.add_argument("--deliver", default="discord")
    parser.add_argument("--enable", action="store_true", help="Create jobs enabled (default: paused)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    vault = args.vault_path.expanduser().resolve()
    hermes_dir = vault / "05-HERMES"
    workflows_dir = hermes_dir / "workflows"
    if not workflows_dir.is_dir():
        print(f"Run scaffold first; missing {workflows_dir}", file=sys.stderr)
        return 1

    manifest = _load_manifest(args.manifest.expanduser().resolve())
    created: List[str] = []
    for entry in manifest.get("jobs", []):
        if not isinstance(entry, dict):
            continue
        workflow = str(entry.get("workflow", "")).strip()
        if not workflow:
            continue
        prompt = _load_workflow_prompt(workflows_dir, workflow)
        schedule = str(entry["schedule"])
        name = str(entry.get("name", workflow))
        skills = list(entry.get("skills") or ["obsidian", "llm-wiki"])
        enabled = bool(entry.get("enabled", False)) or args.enable
        deliver = str(entry.get("deliver", args.deliver))
        profile = entry.get("profile", args.profile)
        job_id = _create_job(
            schedule=schedule,
            prompt=prompt,
            name=name,
            deliver=deliver,
            profile=str(profile) if profile else None,
            workdir=hermes_dir,
            skills=skills,
            enabled=enabled,
            dry_run=args.dry_run,
        )
        created.append(f"{name}: {job_id}")

    print("\n".join(created) if created else "No jobs installed.")
    if not args.enable and not args.dry_run:
        print("Jobs created paused. Enable with: hermes -p bej cron resume <job_id>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
