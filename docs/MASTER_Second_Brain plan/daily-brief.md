# Workflow: Daily Brief (Employee 01)

**Trigger phrases**:  
- "daily brief"  
- "morning brief"  
- "what should I focus on today?"

**Schedule**: Daily 6:00 AM CEST via Hermes cron

**Agent**: Employee 01 (BejCapital Research & Distribution Operator)

**Prompt**:

## Context

Read:
- `05-HERMES/HERMES.md`
- `05-HERMES/BEJMIND.md`
- `05-HERMES/agents/employee-01/EMPLOYEE_01.md`
- `05-HERMES/company-brain/strategy-catalog.md`
- `05-HERMES/company-brain/risk-framework.md`
- `00-INBOX/` (last 24 hours)
- `01-WIKI/trading/` (last 7 days)
- `MASTER/01-WIKI/articles/` (last 7 days)
- `MASTER/01-WIKI/research/` (last 7 days)
- `MASTER/04-PROJECTS/BejCapital/`, `Bejtrader/`, `BejMind/` (active work)
- GitHub `bej` repos (read-only MCP) for recent commits or changes

## Task

Read everything from the above sources and produce a **daily brief** with three sections:

### 1. CONNECTIONS (3 most interesting)

Find the 3 most interesting connections between:
- Recent captures (last 24–7 days)
- Older notes (1–3 months ago)
- Active projects (BejCapital, Bejtrader, BejMind)

For each connection:
- Name the connection (e.g., "Sector rotation + small-cap value convergence")
- Quote 1–2 relevant passages from actual notes
- Explain why this connection matters now
- Suggest one action or experiment to test this connection

### 2. PATTERN (1 key pattern)

Identify **one pattern** across everything you've been reading this week:
- What is your brain clearly working on even if you have not stated it explicitly?
- What theme keeps appearing across different domains?
- What question keeps resurfacing?

Explain:
- What the pattern is
- Where it appears (which notes, which projects)
- Why it matters
- One question worth sitting with today (not a task, a question)

### 3. ACTIONS (top 3 for today)

Based on the connections and pattern, list the **top 3 actions** for today:

1. **Action 1** (BejCapital/Bejtrader): Specific, actionable, with estimated time
2. **Action 2** (BejMind/RESEARCH): Specific, actionable, with estimated time
3. **Action 3** (Business/other): Specific, actionable, with estimated time

Each action should be:
- Crystal clear what to do
- Measurable (done when X is true)
- Time-boxed (est. 30 min / 1 hr / 2 hrs)

## Output Format

Save as `MASTER/00-INBOX/brief-YYYY-MM-DD.md` with this structure:

```markdown
# Daily Brief — YYYY-MM-DD

## CONNECTIONS

### 1. [Connection Name]

- Quote: "..."
- Why it matters: ...
- Action: ...

### 2. [Connection Name]

...

## PATTERN

- Pattern: ...
- Where it appears: ...
- Why it matters: ...
- Question: ...

## ACTIONS

1. [Action 1] — Est. X min
2. [Action 2] — Est. Y min
3. [Action 3] — Est. Z min
```

Post a 200–300 word summary to Discord #hermes-chat.

## Kanban handoff (optional)

If any of the top 3 actions need multi-step follow-up beyond today, create Kanban tasks on board **`berkode-ops`**:
- Title prefix: `[brief]`
- Assignee: `bej` (or `ops` / `social` per `05-HERMES/control-room/shared/assignee-map.md`)
- Use `kanban_create` with a one-line goal and link to this brief file

Do not create more than 3 `[brief]` tasks per brief.
