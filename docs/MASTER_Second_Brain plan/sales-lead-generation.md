# Workflow: Sales Lead Generation (Employee 08)

**Trigger phrases**:  
- "lead generation"  
- "find automation projects"  
- "sales pipeline review"  
- "new leads this week"

**Schedule**: Weekly Thursday 10:00 AM CEST via Hermes cron

**Agent**: Employee 08 (RockerforceSales 08)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-08-rockerforce-sales/EMPLOYEE_08.md`
- `MASTER/04-PROJECTS/Rockerforce/leads/` (past leads)
- `MASTER/04-PROJECTS/Rockerforce/projects/` (active projects)
- Recent emails (Himalaya, Rockerforce-related)
- LinkedIn posts, X posts (if available)
- Industry news (via web search if enabled)

## Task

### 1. Generate New Leads

Scan sources for potential automation projects:

For each potential lead:
1. Source (email, LinkedIn, X, news, referral)
2. Company name, contact person
3. Likely automation need (based on context)
4. Estimated project size (small < $5k, medium $5k–$20k, large > $20k)
5. Priority (high/medium/low)
6. Next action (outreach email, call, meeting)

### 2. Draft Proposals for Active Leads

For each active lead:
1. Summarize customer need
2. Draft proposal (scope, timeline, rough estimate)
3. Draft follow-up email
4. Track next follow-up date

### 3. Generate Weekly Summary

- New leads found (count + 2 key ones)
- Proposals drafted
- Follow-ups scheduled
- Stalled leads flagged

## Output Format

### Lead Note

Save as `MASTER/04-PROJECTS/Rockerforce/leads/YYYY-WW-{company-name}-lead.md`:

```markdown
# Lead: {Company Name} — YYYY-WW

## Source

- Channel: [email / LinkedIn / X / news / referral]
- Date: YYYY-MM-DD
- Contact: [Name, Email, LinkedIn]

## Need

- Likely automation need: [description]
- Industry: [industry]
- Company size: [small/medium/large]

## Estimate

- Project size: small/medium/large
- Priority: high/medium/low
- Confidence: low/medium/high

## Next Action

- Action: [outreach email / call / meeting]
- Due date: YYYY-MM-DD
- Draft outreach: [email draft]
```

### Proposal Draft

Save as `MASTER/04-PROJECTS/Rockerforce/projects/YYYY-WW-{project-name}-proposal.md`:

```markdown
# Proposal: {Project Name} — YYYY-WW

## Customer Need

[2–3 paragraph summary]

## Proposed Scope

- Deliverables: [list]
- Timeline: X weeks
- Estimate: $X

## Timeline

- Week 1: [tasks]
- Week 2: [tasks]
- ...

## Follow-Up Email (Draft)

[Email draft]

## Next Follow-Up Date

YYYY-MM-DD
```

Post a 200–300 word summary to Discord #hermes-chat:
- New leads (count + 2 key ones)
- Proposals drafted
- Follow-ups scheduled
- Stalled leads flagged
