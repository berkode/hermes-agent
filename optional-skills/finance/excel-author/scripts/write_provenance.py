#!/usr/bin/env python3
"""Write a provenance sidecar JSON next to a finance artifact.

Usage:
  python write_provenance.py <artifact.xlsx|pptx|html> \\
      --skill dcf-model --skill-version 1.0.0 \\
      [--model MODEL] [--provider PROVIDER] \\
      [--privacy-posture hybrid|strict|trusted] \\
      [--source SOURCE ...] [--out path.meta.json]

Default output is <artifact>.meta.json beside the artifact.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_provenance(
    artifact: Path,
    *,
    skill: str,
    skill_version: str,
    model: str | None,
    provider: str | None,
    privacy_posture: str,
    sources: list[str],
) -> dict[str, Any]:
    return {
        "artifact": str(artifact.resolve()),
        "artifact_name": artifact.name,
        "skill": skill,
        "skill_version": skill_version,
        "model": model or os.environ.get("HERMES_FINANCE_MODEL") or os.environ.get("BEJMIND_FINANCE_MODEL"),
        "provider": provider
        or os.environ.get("HERMES_FINANCE_MODEL_PROVIDER")
        or os.environ.get("BEJMIND_FINANCE_MODEL_PROVIDER"),
        "privacy_posture": privacy_posture
        or os.environ.get("BEJMIND_PRIVACY_POSTURE")
        or "hybrid",
        "data_sources": sources,
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "disclaimer": (
            "Draft work product for human review. Not investment, legal, tax, "
            "or accounting advice. Do not execute trades, approve onboarding, "
            "or post to a ledger from this artifact alone."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--skill-version", default="1.0.0")
    parser.add_argument("--model", default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--privacy-posture", default="")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    artifact = args.artifact.resolve()
    if not artifact.exists():
        print(json.dumps({"status": "error", "error": f"File not found: {artifact}"}))
        raise SystemExit(1)

    payload = build_provenance(
        artifact,
        skill=args.skill,
        skill_version=args.skill_version,
        model=args.model,
        provider=args.provider,
        privacy_posture=args.privacy_posture,
        sources=list(args.source),
    )
    out = args.out.resolve() if args.out else Path(str(artifact) + ".meta.json")
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "success", "meta": str(out), **payload}, indent=2))


if __name__ == "__main__":
    main()
