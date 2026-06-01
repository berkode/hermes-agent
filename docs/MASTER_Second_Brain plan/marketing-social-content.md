# Workflow: Marketing & Social Content (Employee 10)

**Trigger phrases**:  
- "marketing content"  
- "social content plan"  
- "what to post this week?"  
- "campaign performance"

**Schedule**: Weekly Friday 11:00 AM CEST via Hermes cron

**Agent**: Employee 10 (BejMarketing 10)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-10-marketing-social/EMPLOYEE_10.md`
- `MASTER/04-PROJECTS/` (active work, wins, milestones across all companies)
- `MASTER/05-HERMES/agents/employee-01/social-drafts/` (Employee 01 drafts)
- `MASTER/05-HERMES/agents/employee-02-quant-researcher/research/` (quant insights)
- `MASTER/05-HERMES/agents/employee-09-rockerforce-sales/leads/` (sales wins)
- Recent news in space, AI, quant trading, alternative finance, automation

## Task

### 1. Build 2-Week Content Calendar (All Companies)

For each day in the next 2 weeks, create posts for:
- **LinkedIn**: 3 posts/week (professional, 200–400 chars)
- **X**: 5 posts/week (punchy, 100–200 chars)
- **Substack**: 1 issue/week (title + headings + key points)
- **Instagram**: 2 posts/week (if relevant, 1–2 sentences + emoji)

For each post:
- **Date**: YYYY-MM-DD
- **Platform**: LinkedIn, X, Substack, Instagram
- **Company**: BejCapital, Brentford, Altair, Rockerforce, or All
- **Topic/theme**: What this post is about
- **Hook**: First sentence (grab attention)
- **Key points**: 2–4 bullets
- **Call-to-action**: What should the reader do next?

### 2. Draft Campaign Copy

For active campaigns (paid ads, email campaigns, landing pages):
- Draft 2–3 ad copy variations (short, medium, long)
- Draft email subject lines (5 variations)
- Draft email body (headline, 3–5 bullets, CTA)
- Draft landing page headline + subheadline + 3 bullets + CTA

### 3. Review Campaign Performance

Read:
- Social analytics (manual input or future API integration)
- Email campaign metrics (open rate, click rate, conversion)
- Landing page conversion rates

Produce:
- Top 3 posts/campaigns (what worked, why)
- Bottom 3 posts/campaigns (what didn't, why)
- Hypothesis for next week's test
- 3 specific experiments to run

### 4. Check Brand Consistency

- Are all posts consistent with brand voice across companies?
- Are there controversial claims that need human review?
- Are hashtags and topics aligned with current trends?

## Output Format

### Content Calendar

Save as `MASTER/05-HERMES/agents/employee-10-marketing-social/content-calendars/YYYY-WW-content-calendar.md`:

```markdown
# Content Calendar — YYYY-WW to YYYY-WW

## Week 1

| Date | Platform | Company | Topic | Hook | Key Points | CTA |
|------|----------|---------|-------|------|------------|-----|
| Mon | LinkedIn | BejCapital | Sector Rotation | "Why sector rotation beats buy-and-hold in 2026" | - Point 1<br>- Point 2 | "What's your take?" |
| Mon | X | Rockerforce | AI Automation | "Just shipped automation that saved 20 hrs/week" | - Point 1 | "RT if useful" |
| ... | ... | ... | ... | ... | ... | ... |

## Week 2

| Date | Platform | Company | Topic | Hook | Key Points | CTA |
|------|----------|---------|-------|------|------------|-----|
| Mon | LinkedIn | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... |
```

### Campaign Copy

Save as `MASTER/05-HERMES/agents/employee-10-marketing-social/campaign-copies/YYYY-WW-{campaign-name}.md`:

```markdown
# Campaign Copy: {Campaign Name} — YYYY-WW

## Ad Copy Variations

### Short (100 chars)
[Copy]

### Medium (200 chars)
[Copy]

### Long (400 chars)
[Copy]

## Email Subject Lines (5)

1. [Subject 1]
2. [Subject 2]
3. [Subject 3]
4. [Subject 4]
5. [Subject 5]

## Email Body

**Headline**: [Headline]

**Bullets**:
- Bullet 1
- Bullet 2
- Bullet 3

**CTA**: [Button text + link]

## Landing Page

**Headline**: [Headline]

**Subheadline**: [Subheadline]

**Bullets**:
- Bullet 1
- Bullet 2
- Bullet 3

**CTA**: [Button text + link]
```

### Campaign Review

Save as `MASTER/05-HERMES/agents/employee-10-marketing-social/campaign-reviews/YYYY-WW-campaign-review.md`:

```markdown
# Campaign Review — YYYY-WW

## Top 3 Posts/Campaigns

### 1. [Name]

- Metric: [e.g., 500 likes, 50 clicks, 5 conversions]
- Why it worked: [hypothesis]

### 2. [Name]

...

## Bottom 3 Posts/Campaigns

### 1. [Name]

- Metric: [e.g., 10 likes, 0 clicks]
- Why it didn't work: [hypothesis]

### 2. [Name]

...

## Next Week's Experiments

1. [Experiment 1] — Hypothesis: ...
2. [Experiment 2] — Hypothesis: ...
3. [Experiment 3] — Hypothesis: ...
```

Post a 200–300 word summary to Discord #hermes-chat:
- Content calendar overview (2 weeks, 15+ posts)
- 3 standout posts this week
- 1 brand consistency flag (if any)
- Top 3 campaign performers
- Ask: "Approve this calendar? (yes/no/modify)"
