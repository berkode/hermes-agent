# Strategy catalog (Company Brain)

> Stable doctrine — curate manually; pin in curator. Agents may propose updates in research notes, not overwrite this file without review.

## Active strategies

| Strategy | Regime | Status | Notes |
|----------|--------|--------|-------|
| Sector rotation | Multi-TF momentum + mean reversion | Active | BejCapital watchlist automation |
| Small-cap value + quality | Fundamental + momentum filter | Research | |
| Space basket | RKLB, ASTS, RDW, FLY, LUNR | Active thesis | See `01-WIKI/trading/` |
| Commodities overlay | Gold, oil, nat gas | Active | Macro-linked |

## Inactive / parked

| Strategy | Reason parked |
|----------|----------------|
| _add when retired_ | |

## Regime definitions

- **Risk-on trending:** prefer momentum, wider gross exposure caps per risk-framework
- **Risk-off / vol spike:** reduce gross, favor hedges and cash-like exposure
- **Range / mean-reverting:** favor mean reversion sleeves; tighten momentum size

## Promotion criteria (research → paper → live)

1. Walk-forward Sharpe and max DD within limits in `risk-framework.md`
2. Correlation to existing book < 0.7 unless intentional hedge
3. Human sign-off on capital deployment (see `execution-constraints.md`)

Last reviewed: _(update weekly)_
