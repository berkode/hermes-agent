# Reaching Hermes agents on Oracle VM

VM host: `ubuntu@150.136.38.43` (SSH key `~/.ssh/id_ed25519_oracle_cloud`).  
Browser access: Cloudflare tunnel with Google OAuth (see `~/.hermes/SETUP_BERKODE.md`).

## What syncs automatically (every ~30 min from Mac)

| Component | Mechanism | VM path |
|-----------|-----------|---------|
| Profiles `bej` / `ops` / `social` | `oracle-sync-fleet.sh` → `rsync-hermes-home-to-vm.sh` | `~/.hermes/profiles/*` |
| MASTER cron job definitions | same + `merge-hermes-config.py` (rewrites `workdir` + prompt paths) | `~/.hermes/profiles/bej/cron/jobs.json` |
| Kanban orchestrator config | merged into `ops` profile | `~/.hermes/profiles/ops/config.yaml` |
| Hermes + bejcapital code | `rsync-fleet-code-to-vm.sh` | `~/berkode/hermes-agent`, `~/berkode/bejcapital` |
| Employee personas + workflows | `sync-obsidian-vault-to-vm.sh` (now in fleet sync) | `~/Master/05-HERMES/` |

**Not synced:** chat sessions, SQLite DBs, logs (by design).

## 12 employee roles (personas, not separate processes)

| # | Role | Reach via |
|---|------|-----------|
| 01 | Chief of Staff + Distribution | `hermes -p bej chat` — phrases in `workflows/daily-brief.md` |
| 02 | Quant + ML | `hermes -p bej` — `quant research on [topic]` |
| 03 | Portfolio + Risk | `hermes -p bej` — `portfolio review` |
| 04 | Architect + DevOps | `hermes -p ops` — `architecture review` |
| 05 | Frontend UX | `hermes -p ops` — `ux design review` |
| 06 | Brentford deals | `hermes -p bej` — deal workflows |
| 07 | Contract + Legal | `hermes -p bej` — `contract automation` |
| 08 | Altair merchandiser | `hermes -p bej` — `merchandiser automation` |
| 09 | Rockerforce sales | `hermes -p bej` — `sales lead generation` |
| 10 | Marketing + Social | `hermes -p social chat` (draft-only) |
| 11 | Automation + Data | `hermes -p ops` — `automation audit` |
| 12 | CFO + CTO | `hermes -p bej` — `executive review` |

**Orchestrator:** `ops` profile + Kanban board `berkode-ops` — fans work to assignees `bej` / `ops` / `social`.

Persona files: `05-HERMES/agents/employee-*/EMPLOYEE_*.md`. Registry: `control-room/FLEET_REGISTRY.md`.

## SSH to VM (direct)

```bash
ssh -i ~/.ssh/id_ed25519_oracle_cloud ubuntu@150.136.38.43

# On VM
cd ~/berkode/bejcapital
hermes -p bej cron list                    # MASTER employee crons
hermes -p bej chat                         # trading desk + Employee 01
hermes -p ops chat                         # architect, UX, automation, orchestrator
hermes -p social chat                      # Employee 10 (draft-only)
hermes kanban list --board berkode-ops
ls ~/Master/05-HERMES/agents/              # persona markdown
```

VM LLM: local `ollama/gemma3:12b` (not Mac Pimono unless tunnel is up).

## Mac → VM manual sync (if cron missed or you need immediate push)

```bash
# Full fleet (config + code + ~/.hermes + vault)
bash ~/berkode/bejcapital/app/scripts/oracle/sync-mac-oracle-fleet.sh --no-commit

# Vault only (employee personas, control-room, workflows)
bash ~/berkode/bejcapital/app/scripts/oracle/sync-obsidian-vault-to-vm.sh

# Pull VM-written inbox notes back to Mac
bash ~/berkode/bejcapital/app/scripts/oracle/sync-obsidian-vault-to-vm.sh --pull-inbox
```

Verify VM cron paths after sync:

```bash
ssh -i ~/.ssh/id_ed25519_oracle_cloud ubuntu@150.136.38.43 \
  'python3 -c "import json; j=json.load(open(\"/home/ubuntu/.hermes/profiles/bej/cron/jobs.json\")); jobs=j if isinstance(j,list) else j[\"jobs\"]; print([x[\"workdir\"] for x in jobs if x.get(\"name\",\"\").startswith(\"MASTER\")][:1])"'
```

Expected: `/home/ubuntu/Master/05-HERMES` (not `/Users/morpheus/...`).

## Cron on VM (paused by default)

Install from Mac (jobs sync to VM on next fleet tick):

```bash
hermes -p bej master install-cron --vault-path ~/Master
```

Graduate one job at a time: `hermes -p bej cron resume <id>` (start on Mac; config merges to VM).

## Three ways to interact

1. **Direct chat** — SSH or tunnel → `hermes -p <profile> chat`, use workflow trigger phrases.
2. **Scheduled** — MASTER cron jobs (Employee 01–12 workflows), deliver to Discord when enabled.
3. **Orchestrated** — create Kanban tasks on `berkode-ops`; `ops` dispatcher assigns to `bej` / `ops` / `social`.

See also: `shared/commands.md`, `shared/assignee-map.md`, `../SHADOW_MODE.md`.
