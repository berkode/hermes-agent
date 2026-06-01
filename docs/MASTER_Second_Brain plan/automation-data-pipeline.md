# Workflow: Automation & Data Pipeline (Employee 11)

**Trigger phrases**:  
- "automation audit"  
- "data pipeline review"  
- "new automation idea"  
- "fix brittle automation"

**Schedule**: Weekly Saturday 10:00 AM CEST via Hermes cron

**Agent**: Employee 11 (BejAutomation 11)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-11-automation-data/EMPLOYEE_11.md`
- All existing automation workflows (n8n, Zapier, Hermes cron, custom scripts)
- Employee workflow outputs (01–10)
- System logs (manual input or future monitoring)
- Data sources (OHLCV, fundamentals, alternative data)
- Data quality logs (missing values, duplicates, errors)
- Employee 02 research needs

## Task

### 1. Audit Existing Automations

For each automation:
1. What does it do? (one sentence)
2. How often does it run? (daily, weekly, on-demand)
3. Success rate? (% of runs that complete without error)
4. Last failure? (date, error message, root cause if known)
5. Is it brittle? (yes/no, why)
6. Maintenance effort? (low/medium/high)

### 2. Identify 3–5 Automations That Worked Well

For each:
- Name the automation
- What it does
- Why it works well (reliable, simple, well-monitored)
- How much time it saves (hours/week)

### 3. Identify 2–3 Automations That Failed or Are Brittle

For each:
- Name the automation
- What it does
- Why it fails (dependency change, API rate limit, logic error)
- Root cause
- Suggested fix

### 4. Propose 1–2 New Automation Opportunities

For each:
- What it would do
- Why it matters (time saved, risk reduced)
- Rough implementation plan (steps, tools needed)
- Effort estimate (hours, complexity)
- Priority (high/medium/low)

### 5. Propose 1 Refactor for a Brittle Automation

- Which automation to refactor
- Current state (what's brittle)
- Proposed design (new architecture, new tools)
- Benefits (reliability, maintainability)
- Effort estimate
- Migration plan (how to roll out without breaking)

### 6. Data Pipeline Review

For each data pipeline:
1. What data does it pull? (OHLCV, fundamentals, news, sentiment)
2. What sources? (Yahoo Finance, Alpha Vantage, IEX, NewsAPI, etc.)
3. How often? (daily, hourly, real-time)
4. Data quality metrics (completeness %, accuracy %, timeliness)
5. Missing data handling (skip, impute, error)
6. Last failure (date, error, root cause)

Produce:
- Data quality report (completeness, accuracy, timeliness per source)
- 2–3 data gaps (missing sources, missing fields)
- 1–2 new data pipeline proposals
- Refactor proposal for a brittle pipeline

## Output Format

### Automation Audit

Save as `MASTER/05-HERMES/agents/employee-11-automation-data/automation-audit/YYYY-WW-automation-audit.md`:

```markdown
# Automation Audit — YYYY-WW

## Summary

- Total automations: N
- Working well: X
- Brittle/failing: Y
- New opportunities proposed: Z

## Automations Working Well (3–5)

### 1. [Name]

- What it does: ...
- Success rate: X%
- Time saved: Y hrs/week
- Why it works: ...

### 2. [Name]

...

## Automations Failing/Brittle (2–3)

### 1. [Name]

- What it does: ...
- Failure rate: X%
- Last failure: YYYY-MM-DD
- Root cause: ...
- Suggested fix: ...

### 2. [Name]

...

## New Automation Opportunities (1–2)

### 1. [Name]

- What it would do: ...
- Why it matters: ...
- Implementation plan: ...
- Effort: X hrs, complexity: low/medium/high
- Priority: high/medium/low

### 2. [Name]

...

## Refactor Proposal: [Automaton Name]

- Current state: ...
- Proposed design: ...
- Benefits: ...
- Effort: X hrs
- Migration plan: ...
```

### Data Pipeline Review

Save as `MASTER/05-HERMES/agents/employee-11-automation-data/data-pipeline/YYYY-WW-data-pipeline-review.md`:

```markdown
# Data Pipeline Review — YYYY-WW

## Summary

- Total pipelines: N
- Healthy: X
- Problematic: Y

## Data Quality Report

| Source | Completeness % | Accuracy % | Timeliness | Last Failure |
|--------|---------------|------------|------------|--------------|
| Yahoo Finance | 98% | 95% | Daily | YYYY-MM-DD |
| Alpha Vantage | 95% | 92% | Hourly | YYYY-MM-DD |
| ... | ... | ... | ... | ... |

## Data Gaps (2–3)

1. [Gap 1]: Missing [data type] for [symbols/timeframes]
2. [Gap 2]: ...
3. [Gap 3]: ...

## New Data Pipeline Proposals (1–2)

### 1. [Name]

- What it would pull: ...
- Sources: ...
- Why it matters: ...
- Effort: X hrs

### 2. [Name]

...

## Refactor Proposal: [Pipeline Name]

- Current state: ...
- Proposed design: ...
- Benefits: ...
- Effort: X hrs
- Migration plan: ...
```

Post a 200–300 word summary to Discord #hermes-chat:
- 3 automations working well
- 2 brittle automations flagged
- 1 new automation opportunity
- Data quality summary (completeness %, accuracy %)
- Ask: "Approve refactor? (yes/no/modify)"
