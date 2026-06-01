# Workflow: Process Inbox (Employee 01)

**Trigger phrases**:  
- "process my inbox"  
- "clear the inbox"  
- "morning processing"

**Schedule**: Manual (on-demand) or daily 8:00 AM CEST

**Agent**: Employee 01 (BejCapital Research & Distribution Operator)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-01/EMPLOYEE_01.md`
- `MASTER/00-INBOX/` (last 24 hours)
- `MASTER/01-WIKI/` (existing structure for reference)

## Task

Read every note in `MASTER/00-INBOX` from the last 24 hours.

For each note:
1. **Determine target folder**:
   - Is it an article highlight? → `01-WIKI/articles/`
   - Is it my own thinking? → `01-WIKI/ideas/`
   - Is it a cross-domain pattern? → `01-WIKI/patterns/`
   - Is it an unanswered question? → `01-WIKI/questions/`
   - Is it a specific number/data point? → `01-WIKI/numbers/`
   - Is it trading-related? → `01-WIKI/trading/`
   - Is it research-related? → `01-WIKI/research/`
   - Is it business-related? → `01-WIKI/business/`

2. **Sharpen the raw capture**:
   - Turn it into one specific, punchy sentence.
   - Example: "Saw that RKLB announced new rocket" → "RKLB announced new medium-lift rocket targeting small satellite constellation market, Q3 2026 launch planned."
   - A sharpened note must be specific enough that a stranger understands exactly what was observed without any additional context.

3. **Move it**:
   - Create new file in target folder: `YYYY-MM-DD-{short-title}.md`
   - Add YAML frontmatter:
     ```yaml
     ---
     created: YYYY-MM-DD
     source: inbox
     tags: [capture, {type}]
     related: []
     ---
     ```
   - Add wikilinks to related notes if applicable.

## Output

After processing all notes, report:

1. **Total notes processed**: N
2. **Where each went**:
   - `01-WIKI/articles/`: X notes
   - `01-WIKI/ideas/`: Y notes
   - `01-WIKI/patterns/`: Z notes
   - etc.
3. **Patterns noticed**:
   - Any recurring themes across today's captures?
   - Any unexpected connections?
4. **One connection worth exploring**:
   - Name one specific connection between today's captures and older notes.

Save this report to `MASTER/00-INBOX/process-inbox-YYYY-MM-DD.md` and post summary to Discord #hermes-chat.
