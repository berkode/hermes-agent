# Hermes control room (Berkode)

Mac-local fleet governance (adapted from the [Hermes Agent Operator](https://github.com/shannhk/hermes-agent-control-room) model). This folder is the **control plane** — docs and runbooks only. **No raw secrets.**

| Path | Purpose |
|------|---------|
| `control-room/` | Registry, runbooks, env maps (this folder) |
| `~/.hermes/profiles/bej/` | Live Hermes runtime (config, cron, sessions, Kanban orchestrator) |
| `~/Master/05-HERMES/` | Company Brain + employee personas + workflows |

## Operator levels (Berkode)

| Level | What you have |
|-------|----------------|
| 1 | One lived-in agent (`bej`), shadow-mode rituals |
| 2 | Profile `bej` + 12 employee personas (retired `ops` / `social`) |
| 3 | `bej` + **`kanban-orchestrator`** → board `berkode-ops` |
| 4 | Cron jobs (paused by default); requires gateway/dashboard up |

## Interaction paths

1. **Grok CoS** — company conversation, org chart, route work to Hermes (`control-room/ORG.md`)
2. **Grok CEO Assistant** — personal calendar/digest only (not Hermes staff)
3. **Control** — edit this folder; `hermes dashboard` Services tab
4. **Direct** — `hermes -p bej` for any employee desk
5. **Orchestrated** — `hermes -p bej` + Kanban fan-out (`kanban-orchestrator` skill)

See [`ORG.md`](ORG.md), [`FLEET_REGISTRY.md`](FLEET_REGISTRY.md), and [`shared/assignee-map.md`](shared/assignee-map.md).

## Quick commands

```bash
hermes dashboard                    # http://127.0.0.1:8000
hermes -p bej cron list
hermes -p bej master install-cron --vault-path ~/Master
hermes kanban list --board berkode-ops
hermes -p bej profile list
```

Fleet processes: start/stop via dashboard **Services** (`hermes_cli/bejcapital_fleet.py`). No LaunchAgents — manual start per operator policy.
