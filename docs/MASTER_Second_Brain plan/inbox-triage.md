# Workflow: Inbox Triage (Employee 01)

**Trigger phrases**:  
- "triage inbox"  
- "process emails"  
- "email triage"

**Schedule**: Daily 1:00 PM CEST via Hermes cron

**Agent**: Employee 01 (BejCapital Research & Distribution Operator)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-01/EMPLOYEE_01.md`
- New emails from last 12 hours using Himalaya

## Task

For each important email from the last 12 hours:

### 1. Classify

Choose one:
- **reply**: Needs a response from you
- **ignore**: Not important, no action needed
- **follow-up**: Needs action later (schedule reminder)
- **delegate-to-human**: Needs someone else (activate another employee agent)

### 2. If "reply": Draft Reply

- Keep it concise (3–5 sentences max)
- Match your voice (professional but direct)
- Include clear next step or decision
- If you need more info, ask for it explicitly

### 3. Summarize

Create an entry:

```markdown
## Email: [Subject]

- **Sender**: [Name, Email]
- **Importance**: high / medium / low
- **Action needed**: [reply / follow-up / delegate]
- **Summary**: [2–3 sentences]
- **Draft reply**: [if applicable]
- **Next follow-up date**: [if applicable]
```

## Output Format

Save as `MASTER/05-HERMES/agents/employee-01/inbox-triage/YYYY-MM-DD.md` with:

```markdown
# Email Triage — YYYY-MM-DD

## Summary

- Total emails processed: N
- High importance: X
- Medium importance: Y
- Low importance: Z
- Replies drafted: A
- Follow-ups scheduled: B
- Delegated: C

## Entries

### Email 1: [Subject]

[Entry as above]

### Email 2: [Subject]

[Entry as above]

...
```

Send summary to Discord #hermes-chat:
- Count breakdown
- 2–3 high-priority emails
- 1–2 draft replies ready for review
- Ask: "Approve replies? (yes/no/modify)"

**Do NOT auto-send emails**.
