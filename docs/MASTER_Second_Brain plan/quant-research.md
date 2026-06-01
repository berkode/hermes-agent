# Workflow: Quant Research (Employee 02)

**Trigger phrases**:  
- "quant research on [topic]"  
- "new strategy idea on [topic]"  
- "what do I know about [topic]"  
- "research sector rotation"  
- "research small-cap value"  
- "research space sector"

**Schedule**: Manual (on-demand) or weekly Monday morning

**Agent**: Employee 02 (BejQuant Researcher 02)

**Prompt**:

## Context

Read:
- `05-HERMES/HERMES.md`
- `05-HERMES/BEJMIND.md`
- `05-HERMES/agents/employee-02-quant-researcher/EMPLOYEE_02.md`
- `05-HERMES/company-brain/strategy-catalog.md`
- `05-HERMES/company-brain/risk-framework.md`
- `01-WIKI/trading/` (last 30 days)
- `01-WIKI/research/` (last 30 days)
- `01-WIKI/articles/` (last 30 days, quant/strategy/market microstructure)
- `04-PROJECTS/Bejtrader/` (active strategies, code, backtest results)
- GitHub `bej` repos (read-only MCP) for strategy code and backtest logs

## Research Task

Based on the topic or your best judgment, do the following:

### 1. Summarize Current State

- What do I currently believe about {topic} based on my actual notes?
- What strategies or ideas have I already explored?
- What data sources, features, or models have I used so far?

### 2. Identify Contradictions and Gaps

- What have I saved that contradicts my current belief? Show both sides from my notes.
- What perspective is clearly missing from my research based on what I am and am not reading?
- What is the single most important question I have not asked yet about this topic?

### 3. Propose New Research Directions

Generate 2–3 concrete research directions:

For each direction:
- **Hypothesis**: One sentence hypothesis to test.
- **Data needed**: Specific data sources, timeframes, symbols.
- **Features**: Suggested features or engineered variables.
- **Model approach**: Suggested model (e.g., XGB with walk-forward, RF ensemble, MLP with dropout).
- **Backtest plan**: Clear backtest design (training/test split, walk-forward windows, transaction costs).
- **Risk checks**: What could go wrong (overfitting, data leakage, regime dependence)?

### 4. Write Research Note

Create a new markdown note in `01-WIKI/research/` named:

`YYYY-MM-DD-{topic}-research-{direction}.md`

Include:
- Summary of current state
- Contradictions and gaps
- Proposed research directions
- Next steps (specific, actionable tasks)
- Links to related notes in `01-WIKI/` and `04-PROJECTS/Bejtrader/`.

### 5. Output Summary

Print a 200–300 word summary for Discord #hermes-chat:

- 3 key findings
- 2 new research directions
- 1 contradiction or risk flagged

Save full note to `01-WIKI/research/` and post summary to Discord.

## Safety

- No live trading, order placement, or production strategy deploy
- Align proposals with `05-HERMES/company-brain/risk-framework.md`
- Human approval required before any capital deployment
