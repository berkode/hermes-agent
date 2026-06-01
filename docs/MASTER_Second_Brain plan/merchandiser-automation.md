# Workflow: Merchandiser Automation (Employee 08)

**Trigger phrases**:  
- "merchandiser automation"  
- "customer comments review"  
- "factory action plan"  
- "what tasks are stalled?"

**Schedule**: Daily 10:00 AM CEST via Hermes cron

**Agent**: Employee 08 (AltairMerch 08)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `05-HERMES/agents/employee-08-altair-merchandiser/EMPLOYEE_08.md`
- `MASTER/04-PROJECTS/Altair/` (business notes, customer info)
- New customer comments from web page (manual input or future scraper)
- Yesterday's action plans and follow-ups (`05-HERMES/agents/employee-08-altair-merchandiser/action-plans/`)
- Recent emails (Himalaya, Altair-related)

## Task

### 1. Process New Customer Comments

For each new comment:
1. Translate to English (if not already)
2. Summarize the core request / issue (1–2 sentences)
3. Classify priority (high/medium/low)
4. Propose 3–5 action items (step-by-step)
5. Flag if it requires human review (legal, financial, complex negotiation)

### 2. Update Action Plans

For each active task:
1. Check progress (last update date, what was done)
2. If no progress in 2+ days: flag as stalled
3. Draft next follow-up message to factory (if needed)
4. Set reminder (what to check, when)

### 3. Generate Daily Summary

- New comments count
- Action items created
- Stalled tasks count
- Key quotes from customers (1–2)

## Output Format

### Daily Comment Summary

Save as `05-HERMES/agents/employee-08-altair-merchandiser/customer-comments/YYYY-MM-DD-comments.md`:

```markdown
# Customer Comments — YYYY-MM-DD

## New Comments (N)

### 1. [Customer Name]

- Source: [web page / email / WhatsApp]
- Original: "[Original text]"
- Translation: "[English translation]"
- Summary: [1–2 sentences]
- Priority: high/medium/low
- Action items:
  1. ...
  2. ...
  3. ...
```

### Daily Action Plan

Save as `05-HERMES/agents/employee-08-altair-merchandiser/action-plans/YYYY-MM-DD-action-plan.md`:

```markdown
# Action Plan — YYYY-MM-DD

## Active Tasks (N)

### 1. [Task Name]

- Status: in progress / stalled / complete
- Last update: YYYY-MM-DD
- Next action: ...
- Follow-up message (draft): ...
- Reminder: Check on YYYY-MM-DD

### 2. [Task Name]

...

## Stalled Tasks (N)

- [Task 1] — No progress for X days
- [Task 2] — No progress for Y days

## Key Customer Quotes

- "[Quote 1]" — [Customer Name]
- "[Quote 2]" — [Customer Name]
```

Post a 150–200 word summary to Discord #hermes-chat:
- New comments (count + 1–2 key quotes)
- Action items created
- Stalled tasks flagged
