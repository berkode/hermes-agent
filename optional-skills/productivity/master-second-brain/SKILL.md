---
name: master-second-brain
description: Scaffold MASTER Obsidian vault and Hermes cron templates.
version: 1.0.0
author: Berkode
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [obsidian, vault, cron, productivity]
    category: productivity
    related_skills: [obsidian, llm-wiki]
---

# MASTER Second Brain

Scaffold the MASTER Obsidian vault (company-brain, control-room, employees) and optional Hermes cron jobs for Employee 01–12 workflows.

## CLI

```bash
hermes master init --vault-path ~/Master
hermes master init --vault-path ~/Master --overwrite
hermes master install-cron --vault-path ~/Master --profile bej
hermes master install-cron --enable   # only after shadow-mode review
```

## Default vault path

`~/Master` — matches a single Obsidian vault at home. Company-specific vaults can live as siblings (for example `~/BejCapital`) later; point `OBSIDIAN_VAULT_PATH` per profile when you split them.

## Profile env

Add to `~/.hermes/profiles/bej/.env`:

```
OBSIDIAN_VAULT_PATH=/Users/you/Master
WIKI_PATH=/Users/you/Master
```

## Scripts

- `scripts/master_scaffold.py` — folders, employee profiles, workflows
- `scripts/install_cron_templates.py` — cron from `references/cron-manifest.yaml`

Source templates ship in `docs/MASTER_Second_Brain plan/` in the hermes-agent repo.

## Cron workdir

Use `--workdir <vault>/05-HERMES` so `HERMES.md` loads via context files. Keep `terminal.cwd` on bejcapital for code work.

## Safety

- Email and social workflows are draft-only in the templates.
- Cron jobs install **paused** by default.
