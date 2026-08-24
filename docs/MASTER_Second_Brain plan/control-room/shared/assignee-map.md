# Kanban assignee map

Board: **`berkode-ops`**

| Kanban `assignee` | Hermes profile | Employees |
|-------------------|----------------|-----------|
| `bej` | `bej` | 01–12 (all personas) + **`kanban-orchestrator`** dispatcher |

Retired assignees **`ops`** and **`social`** — route all new tasks to **`bej`**.

## Orchestrator setup

1. Merge [`ops-kanban-config.example.yaml`](ops-kanban-config.example.yaml) into `~/.hermes/profiles/bej/config.yaml` (filename is legacy; config lives on **`bej`** now)
2. Install skill: `hermes -p bej skills install kanban-orchestrator` (bundled skill name may vary — use `hermes skills list`)
3. Ensure gateway is running (dashboard Services) so dispatcher ticks

## Brief → Kanban handoff

When Employee 01 daily brief surfaces follow-ups, create tasks:

- Title prefix: `[brief]`
- Board: `berkode-ops`
- Assignee: **`bej`**

See workflow `daily-brief.md` in vault `05-HERMES/workflows/`.
