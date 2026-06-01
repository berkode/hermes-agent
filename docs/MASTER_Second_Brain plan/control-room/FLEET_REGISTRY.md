# Fleet registry

| Employee | Role | Hermes profile | Kanban assignee | Priority | Workflows (repo) |
|----------|------|----------------|-----------------|----------|------------------|
| 01 | Chief of Staff + Distribution | `bej` | `bej` | P0 | daily-brief, process-inbox, inbox-triage, social-drafts, end-of-day-learning |
| 02 | Quant + ML | `bej` | `bej` | P0 | quant-research, backtest-automation |
| 03 | Portfolio + Risk | `bej` | `bej` | P0 | portfolio-review |
| 04 | Architect + DevOps + Execution | `ops` | `ops` | P0 | architecture-review |
| 05 | Frontend UX + Full-stack | `ops` | `ops` | P1 | ux-design-review |
| 06 | Brentford deals | `bej` | `bej` | P0 | (manual / future deal workflow) |
| 07 | Contract + Legal + CRM | `bej` | `bej` | P0 | contract-automation |
| 08 | Altair merchandiser | `bej` | `bej` | P0 | merchandiser-automation |
| 09 | Rockerforce sales + delivery | `bej` | `bej` | P0 | sales-lead-generation |
| 10 | Marketing + Social | `social` | `social` | P1 | marketing-social-content, social-content-calendar |
| 11 | Automation + Data | `ops` | `ops` | P0 | automation-data-pipeline |
| 12 | CFO + CTO | `bej` | `bej` | P1 | executive-review |

**Orchestrator:** `ops` profile, skill `kanban-orchestrator`, board `berkode-ops`.

**Cron install:** `hermes -p bej master install-cron --vault-path ~/Master` (jobs paused unless `--enable`).

**Company Brain:** `05-HERMES/company-brain/*.md` — read before trading desk workflows.
