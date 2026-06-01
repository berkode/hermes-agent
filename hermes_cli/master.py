"""hermes master — MASTER second-brain vault setup."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hermes_cli.setup import print_error, print_info, print_success
from hermes_constants import get_optional_skills_dir

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

_SKILL_SCRIPTS = (
    get_optional_skills_dir(PROJECT_ROOT / "optional-skills")
    / "productivity"
    / "master-second-brain"
    / "scripts"
)


def _script(name: str) -> Path:
    path = _SKILL_SCRIPTS / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing script: {path}")
    return path


def _run_script(script: Path, argv: list[str]) -> int:
    cmd = [sys.executable, str(script), *argv]
    print_info(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd)


def master_command(args) -> None:
    action = getattr(args, "master_action", None)
    if action == "init":
        argv = ["--vault-path", str(Path(args.vault_path).expanduser())]
        if args.source:
            argv.extend(["--source", str(Path(args.source).expanduser())])
        if args.dry_run:
            argv.append("--dry-run")
        if args.overwrite:
            argv.append("--overwrite")
        if args.profile:
            argv.extend(["--profile", args.profile])
        code = _run_script(_script("master_scaffold.py"), argv)
        if code == 0:
            print_success("MASTER vault scaffold complete.")
        else:
            print_error(f"Scaffold failed (exit {code}).")
        raise SystemExit(code)

    if action == "install-cron":
        argv = ["--vault-path", str(Path(args.vault_path).expanduser())]
        if args.profile:
            argv.extend(["--profile", args.profile])
        if args.deliver:
            argv.extend(["--deliver", args.deliver])
        if args.dry_run:
            argv.append("--dry-run")
        if args.enable:
            argv.append("--enable")
        code = _run_script(_script("install_cron_templates.py"), argv)
        if code == 0:
            print_success("Cron templates installed.")
        else:
            print_error(f"Cron install failed (exit {code}).")
        raise SystemExit(code)

    print_error("Unknown master action. Use: hermes master init | install-cron")
    raise SystemExit(2)
