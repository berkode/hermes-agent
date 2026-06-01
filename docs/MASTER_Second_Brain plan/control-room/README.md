# Hermes control room (Berkode)

Mac-local fleet governance (adapted from the [Hermes Agent Operator](https://github.com/shannhk/hermes-agent-control-room) model). This folder is the **control plane** — docs and runbooks only. **No raw secrets.**

| Path | Purpose |
|------|---------|
| `control-room/` | Registry, runbooks, env maps (this folder) |
| `~/.hermes/profiles/{bej,ops,social}/` | Live Hermes runtime (config, cron, sessions) |
| `~/Master/05-HERMES/` | Company Brain + employee personas + workflows |

## Operator levels (Berkode)

| Level | What you have |
|-------|----------------|
| 1 | One lived-in agent (`bej`), shadow-mode rituals |
| 2 | Profiles `bej` / `ops` / `social` + 12 employee personas |
| 3 | `ops` Kanban orchestrator → board `berkode-ops` |
| 4 | Cron jobs (paused by default); requires gateway/dashboard up |

## Three interaction paths

1. **Control** — edit this folder; `hermes dashboard` Services tab
2. **Direct** — `hermes -p bej` (or `ops` / `social`) when you know the desk
3. **Orchestrated** — `hermes -p ops` + Kanban fan-out for cross-desk work

See [`FLEET_REGISTRY.md`](FLEET_REGISTRY.md) and [`shared/assignee-map.md`](shared/assignee-map.md).

## Quick commands

```bash
hermes dashboard                    # http://127.0.0.1:8000
hermes -p bej cron list
hermes -p bej master install-cron --vault-path ~/Master
hermes kanban list --board berkode-ops
hermes -p ops profile list
```

Fleet processes: start/stop via dashboard **Services** (`hermes_cli/bejcapital_fleet.py`). No LaunchAgents — manual start per operator policy.
