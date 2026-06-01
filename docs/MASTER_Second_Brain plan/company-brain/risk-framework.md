# Risk framework (Company Brain)

> Position limits and kill-switches are enforced in **bejcapital code**. This file is the agent-facing doctrine for reviews and briefs.

## Portfolio limits (targets)

| Metric | Limit | Action if breached |
|--------|-------|-------------------|
| Single name | 20% notional | Flag in portfolio review; no auto trade |
| Single sector | 40% notional | Flag; propose hedge or trim |
| Gross exposure | Per capital plan in vault | Human approval to change |
| Max drawdown (book) | Define per strategy sleeve | Pause sleeve; alert Discord |

## Stress scenarios

- Rates shock (+50bp)
- Oil spike / risk-off
- Liquidity crunch (small-cap widen)

Employee 03 documents results in `portfolio-reviews/` — no automatic rebalancing.

## Kill-switch (human + code)

- Hermes agents **must not** place orders or change kill-switch state
- Execution monitoring only via Employee 04 runbooks
- Live halt: operator via bejtrader/Nautilus controls

## Memory hygiene

- Agents reference this file; do not silently rewrite limits
- Contradictions → flag in brief with links to vault notes

Last reviewed: _(update weekly)_
