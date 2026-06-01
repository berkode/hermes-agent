# Workflow: Contract Automation (Employee 07)

**Trigger phrases**:  
- "contract review"  
- "contract draft"  
- "task follow-up"  
- "opportunity review"

**Schedule**: Weekly Wednesday 10:00 AM CEST via Hermes cron

**Agent**: Employee 07 (BrentfordContract 07)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `05-HERMES/agents/employee-07-brentford-legal/EMPLOYEE_07.md`
- `MASTER/04-PROJECTS/Brentford Capital/contracts/` (active contracts)
- `MASTER/04-PROJECTS/Brentford Capital/task-followups/` (open tasks)
- `MASTER/04-PROJECTS/Brentford Capital/opportunities/` (open opportunities)
- Recent emails (Himalaya, Brentford-related)
- Meeting notes

## Task

### 1. Contract Draft & Iteration

For each active contract:
1. Summarize current state (version, last change, open clauses)
2. Suggest 2–3 clause improvements or risk mitigations
3. Draft next revision (in markdown)
4. Flag any legal risk (must be reviewed by human)

### 2. Task & Opportunity Follow-Up

For each open task/opportunity:
1. Summarize current state
2. Identify next action
3. Draft follow-up email (if needed)
4. Flag stalled items (no progress in 5+ days)

### 3. Generate Weekly Summary

- New contracts created
- Contracts revised
- Tasks/opportunities action items
- Stalled items flagged

## Output Format

### Contract Draft

Save as `05-HERMES/agents/employee-07-brentford-legal/contracts/YYYY-WW-{contract-name}-draft.md`:

```markdown
# Contract Draft: {Contract Name} — YYYY-WW

## Current State

- Version: X.Y
- Last change: YYYY-MM-DD
- Open clauses: N

## Clause Improvements

### 1. [Clause Name]

- Current: "[Current text]"
- Suggested: "[Suggested text]"
- Rationale: ...

### 2. [Clause Name]

...

## Next Revision Draft

[Full draft of next revision]

## Legal Risk Flag

- Risk: ...
- Recommendation: Human review required
```

### Task Follow-Up

Save as `05-HERMES/agents/employee-07-brentford-legal/relationships/YYYY-WW-followup.md`:

```markdown
# Task Follow-Up — YYYY-WW

## Open Tasks (N)

### 1. [Task Name]

- Status: in progress / stalled / complete
- Last update: YYYY-MM-DD
- Next action: ...
- Follow-up email (draft): ...

### 2. [Task Name]

...

## Open Opportunities (N)

### 1. [Opportunity Name]

- Value: $X
- Probability: Y%
- Next action: ...
- Follow-up email (draft): ...

### 2. [Opportunity Name]

...

## Stalled Items (N)

- [Task 1] — No progress for X days
- [Opportunity 1] — No progress for Y days
```

Post a 200–300 word summary to Discord #hermes-chat:
- New contracts created
- Contracts revised
- Tasks/opportunities action items
- Stalled items flagged
