# Workflow: UX Design Review (Employee 05)

**Trigger phrases**:  
- "UX review"  
- "design review"  
- "ui improvements"  
- "what's confusing in the UI?"

**Schedule**: Weekly Tuesday 9:00 AM CEST via Hermes cron

**Agent**: Employee 05 (BejUX 05)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-05-frontend-ux/EMPLOYEE_05.md`
- `MASTER/04-PROJECTS/Bejtrader/` (current UI code, if any)
- `MASTER/05-HERMES/agents/employee-04-software-architect/design-docs/` (architecture docs)
- User feedback (from Discord, email, or manual input)
- Screenshots or descriptions of current UI (manual input)

## Task

### 1. Review Current UI/UX

Analyze the BejCapital platform UI:

- **Clarity**: Is the purpose of each screen clear within 5 seconds?
- **Flow**: Do users know what to do next on each screen?
- **Feedback**: Does the UI provide clear feedback on actions (loading, success, error)?
- **Data Visualization**: Are charts, tables, and metrics easy to read and interpret?
- **Consistency**: Are colors, typography, spacing, and components consistent?

### 2. Identify 3–5 UX Observations

For each observation:
- Name the issue (e.g., "Backtest results table is cluttered, hard to compare strategies")
- Explain the impact (e.g., "Users can't quickly identify best strategy")
- Suggest a fix (e.g., "Add sorting, filtering, and highlight top performer")

### 3. Create 2–3 Wireframe Sketches

For each wireframe (in markdown with ASCII or mermaid):

```
+-----------------------+
|  Strategy Backtest    |
+-----------------------+
| [Chart]               |
|                       |
| +-----+-----+-----+   |
| |Name |Sharpe|DD  |   |
| +-----+-----+-----+   |
| |Strat1| 2.3 | 5% |   |
| |Strat2| 1.8 | 8% |   |
| +-----+-----+-----+   |
| [Sort by Sharpe ▼]    |
+-----------------------+
```

Include:
- Screen goal
- Layout (top-down, left-right)
- Key elements
- Interactions (click, hover, drill-down)

### 4. Propose 1 Design System

Define a minimal design system:

- **Colors**: Primary, secondary, success, warning, error
- **Typography**: Headings (H1–H3), body text, code
- **Spacing**: Base unit (e.g., 8px), margins, paddings
- **Components**: Buttons, cards, tables, charts, forms

### 5. Flag 1 UX Risk

- What could go wrong if we don't address this soon?
- What is the worst-case scenario (user confusion, low adoption)?
- What is the mitigation plan?

## Output Format

Save as `MASTER/05-HERMES/agents/employee-05-frontend-ux/ux-notes/YYYY-WW-ux-review.md`:

```markdown
# UX Design Review — YYYY-WW

## Current State Summary

[2–3 paragraph summary of the current UI]

## Key Observations (3–5)

### 1. [Observation Name]

- Issue: ...
- Impact: ...
- Suggested fix: ...

### 2. [Observation Name]

...

## Wireframe Sketches (2–3)

### 1. [Screen Name]

```
[ASCII or mermaid diagram]
```
- Goal: ...
- Layout: ...
- Key elements: ...
- Interactions: ...

### 2. [Screen Name]

...

## Design System Proposal

- Colors: ...
- Typography: ...
- Spacing: ...
- Components: ...

## UX Risk Flag

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
- 2 wireframe ideas
- 1 risk flagged
