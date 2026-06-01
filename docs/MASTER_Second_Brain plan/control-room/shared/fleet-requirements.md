# Level 4 automation requirements

Cron and Kanban dispatch require a **running gateway** on this Mac.

## Manual start (operator policy)

1. Open `hermes dashboard` → http://127.0.0.1:8000
2. **Services** tab → start **hermes-gateway** (and Pimono proxy if using BejMind LLM path)
3. Verify Discord delivery channel is configured in profile `bej`

`hermes -p bej cron status` may report gateway down when gateway runs from default `~/.hermes` — use dashboard Services as source of truth.

## Graduating cron (Employee 01)

1. Complete shadow mode: 5+ weekdays manual ritual ([`SHADOW_MODE.md`](../SHADOW_MODE.md))
2. `hermes -p bej master install-cron --vault-path ~/Master`
3. Resume **one** job: `hermes -p bej cron resume <daily-brief-id>`
4. Document job id in `agents/employee-01-chief/inventory.md`

## Safety

- No autonomous live trading from Hermes tool calls
- Email/social: draft-only until human approval
- Pin `company-brain/risk-framework.md` — do not let agents rewrite without review
