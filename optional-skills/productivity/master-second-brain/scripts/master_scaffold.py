#!/usr/bin/env python3
"""Scaffold the MASTER Obsidian vault and copy Hermes second-brain assets."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

# Repo layout: optional-skills/productivity/master-second-brain/scripts/this_file
_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_SOURCE = _REPO_ROOT / "docs" / "MASTER_Second_Brain plan"
_DEFAULT_VAULT = Path.home() / "Master"

_VAULT_DIRS: Tuple[str, ...] = (
    "00-INBOX",
    "01-WIKI/articles",
    "01-WIKI/ideas",
    "01-WIKI/patterns",
    "01-WIKI/questions",
    "01-WIKI/numbers",
    "01-WIKI/trading",
    "01-WIKI/research",
    "01-WIKI/business",
    "02-CONNECTIONS",
    "03-INSIGHTS",
    "04-PROJECTS/BejCapital",
    "04-PROJECTS/Bejtrader",
    "04-PROJECTS/BejMind",
    "04-PROJECTS/Brentford Capital",
    "04-PROJECTS/Altair",
    "04-PROJECTS/Rockerforce",
    "04-PROJECTS/OKR-Tracking/weekly",
    "05-HERMES/workflows",
    "05-HERMES/agile",
    "05-HERMES/references",
    "05-HERMES/company-brain",
    "05-HERMES/control-room",
    "05-RAW/sources",
    "05-RAW/assets",
    "99-NOTION-MIGRATION/Workspace Export",
)

_AGENT_DIRS: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("employee-01", ("social-drafts", "inbox-triage", "learning")),
    ("employee-02-quant-researcher", ("research", "backtests", "learning")),
    ("employee-03-portfolio-manager", ("portfolio-reviews", "risk-assessments", "learning")),
    ("employee-04-architect-devops", ("architecture-notes", "design-docs", "learning")),
    ("employee-05-frontend-ux", ("ux-notes", "design-systems", "learning")),
    ("employee-06-brentford-deals", ("pipeline", "memos", "learning")),
    ("employee-07-brentford-legal", ("contracts", "relationships", "learning")),
    ("employee-08-altair-merchandiser", ("customer-comments", "action-plans", "learning")),
    ("employee-09-rockerforce-sales", ("leads", "projects", "learning")),
    ("employee-10-marketing-social", ("content-calendars", "campaigns", "learning")),
    ("employee-11-automation-data", ("automation-audits", "data-pipelines", "learning")),
    ("employee-12-cfo-cto", ("financial-plans", "tech-strategy", "executive-reviews", "learning")),
)

_EMPLOYEE_FILES: Tuple[Tuple[str, str], ...] = (
    ("EMPLOYEE_01.md", "05-HERMES/agents/employee-01/EMPLOYEE_01.md"),
    ("EMPLOYEE_02.md", "05-HERMES/agents/employee-02-quant-researcher/EMPLOYEE_02.md"),
    ("EMPLOYEE_03.md", "05-HERMES/agents/employee-03-portfolio-manager/EMPLOYEE_03.md"),
    ("EMPLOYEE_04.md", "05-HERMES/agents/employee-04-architect-devops/EMPLOYEE_04.md"),
    ("EMPLOYEE_05.md", "05-HERMES/agents/employee-05-frontend-ux/EMPLOYEE_05.md"),
    ("EMPLOYEE_06.md", "05-HERMES/agents/employee-06-brentford-deals/EMPLOYEE_06.md"),
    ("EMPLOYEE_07.md", "05-HERMES/agents/employee-07-brentford-legal/EMPLOYEE_07.md"),
    ("EMPLOYEE_08.md", "05-HERMES/agents/employee-08-altair-merchandiser/EMPLOYEE_08.md"),
    ("EMPLOYEE_09.md", "05-HERMES/agents/employee-09-rockerforce-sales/EMPLOYEE_09.md"),
    ("EMPLOYEE_10.md", "05-HERMES/agents/employee-10-marketing-social/EMPLOYEE_10.md"),
    ("EMPLOYEE_11.md", "05-HERMES/agents/employee-11-automation-data/EMPLOYEE_11.md"),
    ("EMPLOYEE_12.md", "05-HERMES/agents/employee-12-cfo-cto/EMPLOYEE_12.md"),
)

_WORKFLOW_FILES: Tuple[str, ...] = (
    "process-inbox.md",
    "daily-brief.md",
    "social-drafts.md",
    "inbox-triage.md",
    "end-of-day-learning.md",
    "quant-research.md",
    "backtest-automation.md",
    "portfolio-review.md",
    "architecture-review.md",
    "ux-design-review.md",
    "merchandiser-automation.md",
    "contract-automation.md",
    "sales-lead-generation.md",
    "social-content-calendar.md",
    "marketing-social-content.md",
    "automation-data-pipeline.md",
    "executive-review.md",
)

_MASTER_PREFIX_RE = re.compile(r"\bMASTER/")


def _normalize_markdown(text: str) -> str:
    """Paths in workflows are relative to the vault root, not a fixed MASTER/ prefix."""
    return _MASTER_PREFIX_RE.sub("", text)


def _ensure_dirs(vault: Path, dry_run: bool) -> None:
    for rel in _VAULT_DIRS:
        target = vault / rel
        if dry_run:
            print(f"mkdir {target}")
            continue
        target.mkdir(parents=True, exist_ok=True)
    for agent, subdirs in _AGENT_DIRS:
        for sub in subdirs:
            target = vault / "05-HERMES" / "agents" / agent / sub
            if dry_run:
                print(f"mkdir {target}")
            else:
                target.mkdir(parents=True, exist_ok=True)


def _copy_text_file(
    source: Path,
    dest: Path,
    *,
    dry_run: bool,
    overwrite: bool,
    normalize: bool,
) -> bool:
    if not source.is_file():
        print(f"skip missing source: {source}", file=sys.stderr)
        return False
    if dest.exists() and not overwrite:
        print(f"skip exists: {dest}")
        return False
    if dry_run:
        print(f"copy {source} -> {dest}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = source.read_text(encoding="utf-8")
    if normalize:
        content = _normalize_markdown(content)
    dest.write_text(content, encoding="utf-8")
    return True


def _install_files(source: Path, vault: Path, *, dry_run: bool, overwrite: bool) -> int:
    copied = 0
    pairs: List[Tuple[str, str, bool]] = [
        ("HERMES.md", "05-HERMES/HERMES.md", False),
        ("BEJMIND.md", "05-HERMES/BEJMIND.md", False),
        ("AGILE_REVISION.md", "05-HERMES/agile/AGILE_REVISION.md", True),
        ("GOALS_FRAMEWORK.md", "05-HERMES/agile/GOALS_FRAMEWORK.md", True),
        ("EMPLOYEE_SPAN_ANALYSIS.md", "05-HERMES/EMPLOYEE_SPAN_ANALYSIS.md", True),
        ("Dataview_Queries.md", "04-PROJECTS/Dataview_Queries.md", True),
        ("DISCORD_BOT_INVITE.md", "05-HERMES/references/DISCORD_BOT_INVITE.md", False),
        ("SHADOW_MODE.md", "05-HERMES/SHADOW_MODE.md", False),
    ]
    for src_name, dest_rel, normalize in pairs:
        if _copy_text_file(
            source / src_name,
            vault / dest_rel,
            dry_run=dry_run,
            overwrite=overwrite,
            normalize=normalize,
        ):
            copied += 1

    for name, rel in _EMPLOYEE_FILES:
        if _copy_text_file(
            source / name,
            vault / rel,
            dry_run=dry_run,
            overwrite=overwrite,
            normalize=True,
        ):
            copied += 1

    for name in _WORKFLOW_FILES:
        if _copy_text_file(
            source / name,
            vault / "05-HERMES" / "workflows" / name,
            dry_run=dry_run,
            overwrite=overwrite,
            normalize=True,
        ):
            copied += 1

    okr_src = source / "Weekly_OKR_Dashboard.md"
    okr_dest = vault / "04-PROJECTS" / "OKR-Tracking" / "weekly" / "okr-dashboard-template.md"
    if _copy_text_file(okr_src, okr_dest, dry_run=dry_run, overwrite=overwrite, normalize=True):
        copied += 1

    copied += _install_tree(
        source / "company-brain",
        vault / "05-HERMES" / "company-brain",
        dry_run=dry_run,
        overwrite=overwrite,
        normalize=True,
    )
    copied += _install_tree(
        source / "control-room",
        vault / "05-HERMES" / "control-room",
        dry_run=dry_run,
        overwrite=overwrite,
        normalize=False,
    )
    return copied


def _install_tree(
    source_dir: Path,
    dest_dir: Path,
    *,
    dry_run: bool,
    overwrite: bool,
    normalize: bool,
) -> int:
    """Copy all files under source_dir into dest_dir, preserving relative paths."""
    if not source_dir.is_dir():
        print(f"skip missing tree: {source_dir}", file=sys.stderr)
        return 0
    count = 0
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source_dir)
        if _copy_text_file(
            path,
            dest_dir / rel,
            dry_run=dry_run,
            overwrite=overwrite,
            normalize=normalize,
        ):
            count += 1
    return count


def _write_vault_readme(vault: Path, *, dry_run: bool, overwrite: bool) -> None:
    readme = vault / "VAULT_README.md"
    if readme.exists() and not overwrite:
        return
    body = f"""# MASTER vault

Personal second brain (Hermes + BejMind + Obsidian).

- **Vault root:** `{vault}`
- **Hermes layer:** `05-HERMES/` (`HERMES.md`, agents, workflows, `company-brain/`, `control-room/`)
- **Company vaults (optional):** add sibling folders under `{vault.parent}/` when needed

Set in `~/.hermes/profiles/bej/.env`:

```
OBSIDIAN_VAULT_PATH={vault}
WIKI_PATH={vault}
```

Cron jobs should use `--workdir {vault / '05-HERMES'}` so `HERMES.md` loads as project context.
"""
    if dry_run:
        print(f"write {readme}")
        return
    readme.write_text(body, encoding="utf-8")


def _print_env_hint(vault: Path, profile: str) -> None:
    hermes_dir = vault / "05-HERMES"
    print()
    print("Next steps:")
    print(f"  1. Open Obsidian vault: {vault}")
    print(f"  2. Add to ~/.hermes/profiles/{profile}/.env:")
    print(f"     OBSIDIAN_VAULT_PATH={vault}")
    print(f"     WIKI_PATH={vault}")
    print(f"  3. Optional cron (shadow mode): hermes -p {profile} master install-cron --vault-path {vault}")
    print(f"     Cron workdir: {hermes_dir}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold MASTER Obsidian vault for Hermes.")
    parser.add_argument(
        "--vault-path",
        type=Path,
        default=_DEFAULT_VAULT,
        help=f"Obsidian vault directory (default: {_DEFAULT_VAULT})",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=_DEFAULT_SOURCE,
        help="Directory with MASTER_Second_Brain plan markdown files",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions only")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing files")
    parser.add_argument("--profile", default="bej", help="Hermes profile name for hints")
    args = parser.parse_args(list(argv) if argv is not None else None)

    vault = args.vault_path.expanduser().resolve()
    source = args.source.expanduser().resolve()
    if not source.is_dir():
        print(f"Source directory not found: {source}", file=sys.stderr)
        return 1

    if not args.dry_run:
        vault.mkdir(parents=True, exist_ok=True)

    _ensure_dirs(vault, args.dry_run)
    copied = _install_files(source, vault, dry_run=args.dry_run, overwrite=args.overwrite)
    _write_vault_readme(vault, dry_run=args.dry_run, overwrite=args.overwrite)

    print(f"{'Would copy' if args.dry_run else 'Copied'} {copied} file(s) into {vault}")
    if not args.dry_run:
        _print_env_hint(vault, args.profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
