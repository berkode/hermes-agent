# Workflow: Architecture Review (Employee 04)

**Trigger phrases**:  
- "architecture review"  
- "system design review"  
- "tech debt review"  
- "what needs refactoring?"

**Schedule**: Weekly Monday 9:00 AM CEST via Hermes cron (paused by default; profile `ops`)

**Agent**: Employee 04 (BejArchitect 04 — Architect + DevOps + Execution)

**Prompt**:

## Context

Read:
- `05-HERMES/HERMES.md`
- `05-HERMES/agents/employee-04-architect-devops/EMPLOYEE_04.md`
- `05-HERMES/company-brain/execution-constraints.md`
- `04-PROJECTS/Bejtrader/` (current code, strategies, execution engine)
- `04-PROJECTS/BejMind/` (LLM layer, agent logic)
- `04-PROJECTS/BejCapital/` (workflow automation)
- `05-HERMES/agents/employee-02-quant-researcher/` (strategy research)
- `05-HERMES/agents/employee-03-portfolio-manager/` (portfolio reviews)
- GitHub `bej` repos (read-only MCP) for recent commits, PRs, issues

## Task

### 1. Assess Current Architecture

Analyze the BejCapital platform structure:

- **Modularity**: Are components loosely coupled? Can strategies be swapped without touching execution?
- **Scalability**: Can the system handle 10x more strategies, 10x more data, 10x more trades?
- **Performance**: Are there bottlenecks in data loading, backtest execution, or order routing?
- **Testability**: Are components easily testable (unit tests, integration tests)?
- **Documentation**: Is the codebase self-documenting? Are there clear READMEs, docstrings, architecture docs?

### 2. Identify 3–5 Key Observations

For each observation:
- Name the issue (e.g., "Tight coupling between Pine Script parser and Nautilus executor")
- Explain the impact (e.g., "Hard to add new broker without rewriting parser")
- Suggest a fix (e.g., "Introduce adapter pattern, separate parser from executor")

### 3. Propose 2–3 Refactors

For each refactor:
- What to change (specific files/modules)
- Why it matters (benefit, risk reduction)
- Effort estimate (hours, complexity)
- Risk level (low/medium/high)
- Migration plan (how to roll out without breaking production)

### 4. Design 1 New Module

For a needed feature (e.g., "walk-forward optimization engine", "multi-broker adapter"):
- Module name
- Purpose and responsibilities
- Input/output interfaces
- Dependencies
- Pseudocode or interface sketch
- Test strategy

### 5. Flag 1 Technical Risk

- What could go wrong if we don't address this soon?
- What is the worst-case scenario?
- What is the mitigation plan?

## Output Format

Save as `05-HERMES/agents/employee-04-architect-devops/architecture-notes/YYYY-WW-architecture-review.md`:

```markdown
# Architecture Review — YYYY-WW

## Current State Summary

[2–3 paragraph summary of the platform's current architecture]

## Key Observations (3–5)

### 1. [Observation Name]

- Issue: ...
- Impact: ...
- Suggested fix: ...

### 2. [Observation Name]

...

## Refactor Proposals (2–3)

### 1. [Refactor Name]

- What to change: ...
- Why it matters: ...
- Effort: X hours, complexity: low/medium/high
- Risk: low/medium/high
- Migration plan: ...

### 2. [Refactor Name]

...

## New Module Design: [Module Name]

- Purpose: ...
- Interfaces: ...
- Dependencies: ...
- Pseudocode:
  ```python
  ...
  ```
- Test strategy: ...

## Technical Risk Flag

- Risk: ...
- Worst-case: ...
- Mitigation: ...

## Next Steps

1. [Action 1] — Est. X hrs
2. [Action 2] — Est. Y hrs
3. [Action 3] — Est. Z hrs
```

Post a 200–300 word summary to Discord #hermes-chat:
- 3 key observations
- 2 refactor proposals
- 1 risk flagged
