# Organization chart — Grok office + Hermes plant

Berkode runs a **two-layer** model: Grok agents are the conversational office; Hermes profile **`bej`** executes scheduled work and all 12 specialist personas in the Obsidian vault.

## Reporting lines

```text
Berk (operator)
├── Grok Chief of Staff          ← company: org chart, priorities, Hermes staff routing
│   └── Hermes profile `bej`
│       └── Employees 01–12 (see FLEET_REGISTRY.md)
│           └── kanban-orchestrator skill on same profile when orchestrating board berkode-ops
│
└── Grok CEO Assistant           ← personal only: calendar, digest, Perplexity/Obsidian memory
    (NOT company staff — does not manage Hermes employees)
```

## Role split

| Agent | Layer | Owns | Does not own |
|-------|-------|------|--------------|
| **Grok Chief of Staff** | Grok (company) | Conversational front door; org chart; task routing to Hermes; priority calls across companies | Cron execution, vault file writes, live trading, auto-send email/social |
| **Grok CEO Assistant** | Grok (personal) | Berk's calendar, personal digest, personal memory (Perplexity/Obsidian) | Company brief, inbox triage, social drafts, employee routing |
| **BejChief 01** (Hermes) | Hermes plant | Scheduled daily brief (6:00), social drafts (8:00), inbox triage (13:00), EOD (18:00), Monday HERMES.md | Personal calendar; conversational chat with Berk (Grok CoS handles that) |
| **Employees 02–12** | Hermes plant | Specialist outputs per `EMPLOYEE_XX.md` | Binding decisions, auto-send, live trading |

## Interaction paths

1. **Talk to Grok CoS** — strategy, cross-company priorities, "run Employee 03 portfolio review", org changes, who owns what.
2. **Talk to Grok CEO Assistant** — personal schedule, personal notes, non-company errands.
3. **Hermes cron + Kanban** — all personas run on **`bej`**; BejChief 01 and others execute on schedule or when CoS (or Kanban) dispatches work.

## Hermes profile (execution layer)

| Profile | Employees | Skill / orchestrator |
|---------|-----------|----------------------|
| `bej` | 01–12 (all personas) | Company brain, trading desk, Brentford/Altair/Rockerforce, terminal/CI on bejcapital cwd, social drafts (approval required), **`kanban-orchestrator`** on board `berkode-ops` |

Profiles **`ops`** and **`social`** are retired — do not create or route to them. See [`shared/assignee-map.md`](shared/assignee-map.md).

## Draft-only boundaries (all layers)

- Email and social: **draft only** until Berk approves.
- Trading and capital: **no autonomous live execution** from any employee persona.
- Secrets: live in `$HERMES_HOME/.env.encrypted` — never in vault templates or this repo.

## Related docs

- [`FLEET_REGISTRY.md`](FLEET_REGISTRY.md) — employee ↔ profile ↔ workflow map
- [`../AGILE_REVISION.md`](../AGILE_REVISION.md) — 12-role philosophy (not 30)
- [`../EMPLOYEE_01.md`](../EMPLOYEE_01.md) … [`../EMPLOYEE_12.md`](../EMPLOYEE_12.md) — persona specs
