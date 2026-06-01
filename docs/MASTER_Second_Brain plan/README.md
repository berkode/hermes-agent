# MASTER Second Brain — Hermes package

Consolidated templates for the MASTER Obsidian vault + Hermes employee workflows.

## Recommended vault location

**Default: `~/Master`** (your current Obsidian vault).

- One personal “operating system” vault at `~/Master`.
- Optional **company vaults as siblings** later, for example `~/BejCapital`, `~/Brentford`, each with its own `05-HERMES/` — not nested inside `~/Master` unless you want a single graph.
- `~/Documents/Obsidian/Master` is fine if you prefer Documents; the installer default is `~/Master` for a short path and easy CLI use.

## Python / Hermes CLI (MacPorts)

Hermes must run from the repo **`.venv`**, built with MacPorts CPython 3.13:

```bash
cd ~/berkode/hermes-agent
export UV_CACHE_DIR=~/berkode/hermes-agent/.uv-cache
bash scripts/ensure_hermes_venv.sh    # uv venv --python /opt/local/bin/python3.13 + uv sync
ln -sf ~/berkode/hermes-agent/scripts/hermes-wrapper.sh ~/.local/bin/hermes
hermes --version   # should show Python: 3.13.12
```

The wrapper pins the CLI to `.venv/bin/hermes` (absolute shebang). Do not use a bare `python3` on PATH for `hermes` subcommands.

## Quick start (macOS)

```bash
cd /Users/morpheus/berkode/hermes-agent
source .venv/bin/activate   # not the old venv/ folder

# Scaffold into your existing Obsidian vault (preserves .obsidian/)
hermes master init --vault-path ~/Master

# Refresh templates after doc updates
hermes master init --vault-path ~/Master --overwrite

# Optional: install cron jobs (paused until you resume them)
hermes -p bej master install-cron --vault-path ~/Master
```

Add to `~/.hermes/profiles/bej/.env`:

```bash
OBSIDIAN_VAULT_PATH=/Users/morpheus/Master
WIKI_PATH=/Users/morpheus/Master
```

Cron jobs use `--workdir /Users/morpheus/Master/05-HERMES` so `HERMES.md` loads as project context. Keep `terminal.cwd` on bejcapital for code.

## Layout (vault root)

```text
~/Master/
├── 00-INBOX/
├── 01-WIKI/{articles,ideas,patterns,questions,numbers,trading,research,business}/
├── 02-CONNECTIONS/
├── 03-INSIGHTS/
├── 04-PROJECTS/{BejCapital,Bejtrader,BejMind,...}/
├── 05-HERMES/{HERMES.md,BEJMIND.md,agents/,workflows/,agile/}
├── 05-RAW/{sources,assets}/
└── 99-NOTION-MIGRATION/
```

Paths in workflow markdown are **relative to the vault root** (no hardcoded `MASTER/` prefix).

## File map

| Source file | Vault destination |
|-------------|-------------------|
| HERMES.md | `05-HERMES/HERMES.md` |
| BEJMIND.md | `05-HERMES/BEJMIND.md` |
| EMPLOYEE_01.md … EMPLOYEE_12.md | `05-HERMES/agents/.../EMPLOYEE_XX.md` |
| `*.md` workflows | `05-HERMES/workflows/` |
| `company-brain/*.md` | `05-HERMES/company-brain/` |
| `control-room/` | `05-HERMES/control-room/` (fleet registry, runbooks) |
| AGILE_REVISION.md, GOALS_FRAMEWORK.md | `05-HERMES/agile/` |
| Dataview_Queries.md | `04-PROJECTS/Dataview_Queries.md` |

## Hermes skills

- `obsidian` — vault read/write (`OBSIDIAN_VAULT_PATH`)
- `llm-wiki` — Karpathy wiki layer (`WIKI_PATH`, same as vault)
- `himalaya`, `xurl` — email and X drafts (approval required before send)

## Shadow mode (start here)

See `SHADOW_MODE.md` (copied to `05-HERMES/SHADOW_MODE.md` in the vault). Run workflows manually in `hermes -p bej` for one week before enabling cron.

## Operator levels (Berkode)

| Level | Setup |
|-------|--------|
| 1 | `bej` profile + shadow mode (`SHADOW_MODE.md`) |
| 2 | Profiles `bej` / `ops` / `social` + 12 employees (`AGILE_REVISION.md`) |
| 3 | `ops` Kanban orchestrator → board `berkode-ops` (`control-room/shared/assignee-map.md`) |
| 4 | Cron jobs (paused by default); gateway via `hermes dashboard` Services |

## Training order

1. **Employee 01** — daily brief, inbox, social drafts (shadow → cron paused → enable one job at a time)
2. **Employees 02–04** — quant, portfolio, architecture (shadow 2–3 runs each → cron)
3. **Employees 05–12** — as needed per company

## Do not move `~/.hermes` into this repo

Keep profile state in `~/.hermes/profiles/bej/`. Optional symlink from the repo for editing:

```bash
ln -s ~/.hermes/profiles/bej ~/berkode/hermes-agent/config-bej-profile
```
