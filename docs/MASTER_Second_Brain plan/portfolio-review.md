# Workflow: Portfolio Review (Employee 03)

**Trigger phrases**:  
- "portfolio review"  
- "weekly portfolio review"  
- "risk assessment"  
- "stress test portfolio"

**Schedule**: Weekly Friday afternoon or Monday morning

**Agent**: Employee 03 (BejPortfolio Manager 03)

**Safety:** No live rebalancing or kill-switch changes from Hermes; recommendations only. Cross-check `05-HERMES/company-brain/risk-framework.md`.

**Prompt**:

## Context

Read:
- `05-HERMES/HERMES.md`
- `05-HERMES/agents/employee-03-portfolio-manager/EMPLOYEE_03.md`
- `05-HERMES/company-brain/risk-framework.md`
- `05-HERMES/company-brain/strategy-catalog.md`
- All backtest reports from Employee 02 (`05-HERMES/agents/employee-02-quant-researcher/backtests/`)
- Active positions and trades (from Bejtrader/Nautilus logs or manual input)
- Risk assessments (`05-HERMES/agents/employee-03-portfolio-manager/risk-assessments/`)

## Portfolio Review Task

### 1. Aggregate Portfolio-Level Metrics

Calculate or summarize:

- **Total exposure**: Long vs short, gross vs net.
- **Sharpe ratio**: Annualized Sharpe across all strategies.
- **Max drawdown**: Peak-to-trough across all strategies.
- **Win rate**: Overall win rate across all trades.
- **Profit factor**: Gross profit / gross loss.
- **Turnover**: Weekly/monthly turnover.
- **Correlation**: Correlation matrix between strategies.
- **Concentration**: Top 5 positions by notional, top 3 sectors.

### 2. Identify Risk Flags

Flag any of the following:

- **Concentration risk**: >20% in single position, >40% in single sector.
- **Regime exposure**: Heavy exposure to one regime (e.g., all strategies long-only, all rely on trending markets).
- **Liquidity risk**: Small-cap or low-float positions with high slippage.
- **Overfitting**: Strategies with suspiciously high Sharpe and low drawdown.
- **Correlation risk**: Multiple strategies correlated >0.7.
- **Leverage risk**: High gross exposure relative to capital.

### 3. Stress Test Under Regimes

Test portfolio under:

- **Financial meltdown**: 2008-style crash, high vol, correlations → 1.
- **Inflation spike**: 1970s-style inflation, commodity rally, equities flat/down.
- **Rate hike**: 1980s-style rate hike, growth stocks down, value up.
- **Sector rotation shock**: Rapid sector rotation, momentum strategies fail.

For each regime:
- Estimate portfolio P&L (qualitative if no data).
- Identify which strategies would succeed/fail.
- Flag unhedged risks.

### 4. Generate Recommendations

Provide clear recommendations:

- **Increase exposure**: Which strategies/sectors to increase? Why?
- **Decrease exposure**: Which to reduce? Why?
- **Hedge**: What hedging instruments (options, inverse ETFs, futures)?
- **Rebalance**: What target weights?
- **Retire**: Which strategies to retire or put on hold?

### 5. Write Portfolio Review Report

Create a new markdown file in `05-HERMES/agents/employee-03-portfolio-manager/portfolio-reviews/`:

`YYYY-WW-portfolio-review.md`

Include:
- Portfolio overview (exposure, metrics)
- Risk flags (table)
- Stress test results (qualitative or quantitative)
- Recommendations (table with action, rationale, target weights)
- Next steps (specific, actionable)

### 6. Output Summary

Print a 200–300 word summary for Discord #hermes-chat:

- 3 key metrics
- 2 risk flags
- 2 recommendations

Save full report and post summary to Discord.
