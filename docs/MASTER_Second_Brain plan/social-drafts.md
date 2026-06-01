# Workflow: Social Drafts (Employee 01)

**Trigger phrases**:  
- "social drafts"  
- "draft posts"  
- "what should I post today?"

**Schedule**: Daily 8:00 AM CEST via Hermes cron (DISABLED until Week 3+)

**Agent**: Employee 01 (BejCapital Research & Distribution Operator)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-01/EMPLOYEE_01.md`
- `MASTER/01-WIKI/trading/` (last 7 days)
- `MASTER/01-WIKI/articles/` (last 7 days)
- `MASTER/01-WIKI/patterns/` (last 7 days)
- `MASTER/04-PROJECTS/BejCapital/`, `Bejtrader/`, `BejMind/` (active milestones)
- `MASTER/00-INBOX/brief-YYYY-MM-DD.md` (today's daily brief)

## Task

From this context, produce **draft social posts** for 4 platforms:

### 1. X Post (Twitter)

- 1–2 ideas, punchy
- 100–200 characters max
- Hook in first sentence
- Optional: 1 relevant hashtag

### 2. LinkedIn Post

- Professional tone
- 1–2 insights from your work
- 200–400 characters
- Optional: 1–2 relevant hashtags
- Call-to-action (question or invitation to discuss)

### 3. Substack Outline

- Title (10–12 words, intriguing)
- 3–5 section headings
- Key points under each heading (2–3 bullets each)
- Conclusion (1–2 sentences)
- Optional: teaser for next issue

### 4. Instagram Caption (if relevant)

- Short, engaging
- 1–2 sentences
- Optional: 1 emoji
- Call-to-action (question or "link in bio")

## Output Format

Save each in `MASTER/05-HERMES/agents/employee-01/social-drafts/YYYY-MM-DD/`:

- `X-post.md`
- `LinkedIn-post.md`
- `Substack-outline.md`
- `Instagram-caption.md`

**Do NOT auto-post**. Await explicit approval.

Post a summary to Discord #hermes-chat:
- 1-line preview of each draft
- Ask: "Approve X post? (yes/no/modify)"
