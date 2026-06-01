# Execution constraints (Company Brain)

## Brokers and paths

| Path | Use | Hermes access |
|------|-----|---------------|
| IBKR / configured brokers | Live and paper execution | Read logs only; no order tools |
| Nautilus | Bejtrader execution engine | Architecture review + monitoring drafts |
| TV signals | Signal ingress | Document in vault; no auto wiring from Hermes |

## Latency and ops

- Mac-local fleet: not colocated — no HFT assumptions
- Gateway and Pimono must be up for cron/discord (manual start via dashboard)

## Human approval gates

| Action | Approval |
|--------|----------|
| New live strategy deployment | Master |
| Position size change | Master |
| Email / social send | Master (draft-only agents) |
| Contract signature | Master + counsel |

## Agent allowed outputs

- Monitoring checklists, incident summaries, ADRs
- Draft config changes as markdown in vault — not direct production edits

Last reviewed: _(update when broker or stack changes)_
