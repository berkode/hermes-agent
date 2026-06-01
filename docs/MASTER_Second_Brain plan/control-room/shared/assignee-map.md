# Kanban assignee map

Board: **`berkode-ops`**

| Kanban `assignee` | Hermes profile | Employees |
|-------------------|----------------|-----------|
| `bej` | `bej` | 01, 02, 03, 06, 07, 08, 09, 12 |
| `ops` | `ops` | 04, 05, 11 + orchestrator |
| `social` | `social` | 10 |

## Orchestrator setup

1. Merge [`ops-kanban-config.example.yaml`](ops-kanban-config.example.yaml) into `~/.hermes/profiles/ops/config.yaml`
2. Install skill: `hermes -p ops skills install kanban-orchestrator` (bundled skill name may vary — use `hermes skills list`)
3. Ensure gateway is running (dashboard Services) so dispatcher ticks

## Brief → Kanban handoff

When Employee 01 daily brief surfaces follow-ups, create tasks:

- Title prefix: `[brief]`
- Board: `berkode-ops`
- Assignee: per table above

See workflow `daily-brief.md` in vault `05-HERMES/workflows/`.
