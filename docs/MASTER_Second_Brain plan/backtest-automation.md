# Workflow: Backtest Automation (Employee 02)

**Trigger phrases**:  
- "backtest strategy [strategy-name]"  
- "run backtest on [EURUSD, sector-rotation]"  
- "evaluate backtest results [file-name]"  
- "compare strategy versions [v1 vs v2]"

**Schedule**: Manual (on-demand) or weekly Wednesday

**Agent**: Employee 02 (BejQuant Researcher 02)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-02-quant-researcher/EMPLOYEE_02.md`
- Strategy code in `04-PROJECTS/Bejtrader/strategies/{strategy-name}/`
- Backtest config in `04-PROJECTS/Bejtrader/config/`
- GitHub `bej` repos (read-only MCP) for code and logs
- Previous backtest reports in `05-HERMES/agents/employee-02-quant-researcher/backtests/`

## Backtest Task

### 1. Identify Strategy and Config

- Which strategy code to use?
- Which config file (symbols, timeframe, transaction costs, slippage)?
- What is the evaluation period (train/test/walk-forward windows)?

### 2. Generate or Run Backtest

**Option A: If Python sandbox is enabled**

- Run backtest using NautilusTrader or custom Python code.
- Capture metrics: Sharpe, max drawdown, win rate, profit factor, turnover, exposure, regime performance.

**Option B: If Python sandbox is NOT enabled**

- Generate a complete backtest script in Python that:
  - Loads data
  - Implements strategy logic
  - Runs backtest
  - Outputs metrics
  - Saves results to `05-HERMES/agents/employee-02-quant-researcher/backtests/{strategy-name}-YYYY-MM-DD.md`
- Post script to Discord for manual execution.

### 3. Evaluate Results

Analyze the backtest results:

- **Performance metrics**: Sharpe, max drawdown, win rate, profit factor, turnover, exposure.
- **Regime performance**: How does it perform in trending vs mean-reverting, bull vs bear, high vol vs low vol?
- **Overfitting risk**: Does it look too good? Is performance driven by a few large trades?
- **Data leakage**: Any look-ahead bias? Any feature that uses future information?
- **Transaction costs**: Are costs realistic? Are slippage and fees included?

### 4. Compare to Baseline and Prior Versions

- Compare to:
  - Buy-and-hold baseline
  - Prior strategy version (v1 vs v2)
  - Similar strategies (sector rotation vs momentum vs mean reversion)

Identify:
- What improved?
- What got worse?
- Is the improvement statistically significant or just noise?

### 5. Write Backtest Report

Create a new markdown file in `05-HERMES/agents/employee-02-quant-researcher/backtests/`:

`YYYY-WW-{strategy-name}-backtest-report.md`

Include:
- Strategy description
- Backtest config (symbols, timeframe, train/test split, costs)
- Performance metrics (table)
- Regime performance
- Overfitting/leakage analysis
- Comparison to baseline and prior versions
- Recommendation: keep / modify / retire
- Next steps (specific, actionable)

### 6. Output Summary

Print a 200–300 word summary for Discord #hermes-chat:

- 3 key metrics
- 1 regime insight
- 1 risk flag
- Recommendation (keep/modify/retire)

Save full report and post summary to Discord.
