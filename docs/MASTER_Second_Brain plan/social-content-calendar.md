# Workflow: Social Content Calendar (Employee 09)

**Trigger phrases**:  
- "content calendar"  
- "social content plan"  
- "what to post this week?"  
- "draft social posts"

**Schedule**: Weekly Friday 10:00 AM CEST via Hermes cron

**Agent**: Employee 09 (RockerforceSocial 09)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-09-rockerforce-social/EMPLOYEE_09.md`
- `MASTER/04-PROJECTS/` (active work, wins, milestones across all companies)
- `MASTER/05-HERMES/agents/employee-01/social-drafts/` (Employee 01 drafts)
- `MASTER/05-HERMES/agents/employee-02-quant-researcher/research/` (quant insights)
- `MASTER/05-HERMES/agents/employee-04-software-architect/architecture-notes/` (tech insights)
- Recent news in space, AI, quant trading, alternative finance

## Task

### 1. Build 2-Week Content Calendar

For each day in the next 2 weeks:

- **Date**: YYYY-MM-DD
- **Platform**: LinkedIn, X, Substack, Instagram
- **Topic / theme**: What this post is about
- **Hook**: First sentence (grab attention)
- **Key points**: 2–4 bullets
- **Call-to-action**: What should the reader do next?

### 2. Draft Posts for Each Day

For each day:
- Draft 1 LinkedIn post (professional, 200–400 chars)
- Draft 1 X post (punchy, 100–200 chars)
- Draft 1 Substack outline (title + headings + key points)
- Draft 1 Instagram caption (if relevant)

### 3. Check Brand Consistency

- Are all posts consistent with brand voice?
- Are there any controversial claims that need human review?
- Are hashtags and topics aligned with current trends?

### 4. Generate Weekly Summary

- Content calendar overview (2 weeks)
- 3 standout posts this week
- 1 brand consistency flag (if any)

## Output Format

### Content Calendar

Save as `MASTER/05-HERMES/agents/employee-09-rockerforce-social/content-calendars/YYYY-WW-content-calendar.md`:

```markdown
# Content Calendar — YYYY-WW to YYYY-WW

## Week 1

| Date | Platform | Topic | Hook | Key Points | CTA |
|------|----------|-------|------|------------|-----|
| Mon | LinkedIn | Sector Rotation | "Why sector rotation beats buy-and-hold in 2026" | - Point 1<br>- Point 2 | "What's your take?" |
| Mon | X | Space Sector | "RKLB just dropped something big" | - Point 1 | "RT if you're bullish" |
| ... | ... | ... | ... | ... | ... |

## Week 2

| Date | Platform | Topic | Hook | Key Points | CTA |
|------|----------|-------|------|------------|-----|
| Mon | LinkedIn | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |
```

### Draft Posts

Save in `MASTER/05-HERMES/agents/employee-09-rockerforce-social/social-content/YYYY-MM-DD/`:

- `LinkedIn-post.md`
- `X-post.md`
- `Substack-outline.md`
- `Instagram-caption.md`

Post a 200–300 word summary to Discord #hermes-chat:
- Content calendar overview (2 weeks)
- 3 standout posts this week
- 1 brand consistency flag (if any)
- Ask: "Approve this calendar? (yes/no/modify)"
