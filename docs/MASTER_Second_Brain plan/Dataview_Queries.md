
# Obsidian Dataview Queries — Daily Tasks from Employee Goals

## How to Use

1. Create a new note in `MASTER/04-PROJECTS/Daily-Tasks/` called `YYYY-MM-DD-daily-tasks.md`
2. Add this query at the top of the note
3. Dataview will automatically surface tasks due today from all employee goals

---

## Query 1: Daily Tasks Due Today (All Employees)

```dataview
TASK
FROM "05-HERMES/agents"
WHERE !completed AND due = date(today)
GROUP BY file.link
SORT file.name
```

**What it does**:
- Shows all incomplete tasks due today
- Groups by file (employee note)
- Sorted by filename

---

## Query 2: Daily Tasks by Employee (With Context)

```dataview
TABLE WITHOUT ID
file.link AS "Source",
table.readyState AS "Status",
description AS "Task",
due AS "Due"
FROM "05-HERMES/agents"
WHERE !completed AND due = date(today)
FLATTEN list(page.content) AS task
SORT file.name
```

**What it does**:
- Shows task description with file link
- Includes status and due date
- Flattens content to find tasks inline

---

## Query 3: This Week's Tasks (All Employees)

```dataview
TASK
FROM "05-HERMES/agents"
WHERE !completed AND due <= date(today) + dur(6 days) AND due >= date(today)
GROUP BY file.link
SORT due
```

**What it does**:
- Shows all incomplete tasks due this week (today + 6 days)
- Groups by employee
- Sorted by due date

---

## Query 4: Overdue Tasks (All Employees)

```dataview
TASK
FROM "05-HERMES/agents"
WHERE !completed AND due < date(today)
GROUP BY file.link
SORT due DESC
```

**What it does**:
- Shows all overdue incomplete tasks
- Groups by employee
- Sorted by due date (oldest first)

---

## Query 5: Employee Quota Tracking (Weekly Goals)

```dataview
TABLE WITHOUT ID
file.name AS "Employee",
length(levels(page.content, "### ")) AS "Weekly Goals",
length(sorted(x => !x.completed)(levels(page.content, "- "))) AS "Completed",
length(sorted(x => !x.completed)(levels(page.content, "- "))) / length(levels(page.content, "- ")) * 100 AS "Progress %"
FROM "05-HERMES/agents"
WHERE file.day >= date(today) - dur(6 days)
SORT file.name
```

**What it does**:
- Counts weekly goals per employee
- Counts completed tasks
- Calculates progress %
- Shows last 7 days

---

## Query 6: Upcoming Weekly Goals (Next Week)

```dataview
TABLE WITHOUT ID
file.link AS "Employee",
content AS "Goal Summary"
FROM "05-HERMES/agents/employee-*/learning"
WHERE file.day = date(today) + dur(7 days)
```

**What it does**:
- Shows weekly goals set for next week
- From learning notes

---

## Template for Daily Task Note

Create `MASTER/04-PROJECTS/Daily-Tasks/YYYY-MM-DD-daily-tasks.md`:

```markdown
# Daily Tasks — {{date:YYYY-MM-DD}}

## Tasks Due Today

```dataview
TASK
FROM "05-HERMES/agents"
WHERE !completed AND due = date(today)
GROUP BY file.link
SORT file.name
```

## Overdue Tasks

```dataview
TASK
FROM "05-HERMES/agents"
WHERE !completed AND due < date(today)
GROUP BY file.link
SORT due DESC
```

## This Week's Tasks

```dataview
TASK
FROM "05-HERMES/agents"
WHERE !completed AND due <= date(today) + dur(6 days) AND due >= date(today)
GROUP BY file.link
SORT due
```

## Notes

- [Add any manual notes here]
```

---

## How to Add Tasks with Due Dates

In any employee note (e.g., `05-HERMES/agents/employee-02-quant-researcher/EMPLOYEE_02.md`), add tasks like this:

```markdown
## Weekly Goals

- [ ] Research 5 new strategy ideas --daily due=2026-05-29
- [ ] Backtest 3 strategies --daily due=2026-05-30
- [ ] Write 2 research notes --daily due=2026-05-31
```

**Format**: `- [ ] Task description --daily due=YYYY-MM-DD`

Dataview will pick this up automatically.

---

## Alternative: Use Task Metadata in Frontmatter

If you prefer frontmatter:

```yaml
---
created: 2026-05-28
due: 2026-05-29
status: todo
employee: employee-02
goal: Research 5 new strategy ideas
---
```

Then query:

```dataview
TASK
FROM "05-HERMES/agents"
WHERE !completed AND due = date(today)
GROUP BY employee
SORT file.name
```

---

## Installing Dataview Plugin in Obsidian

1. Open Obsidian → Settings → Community Plugins
2. Browse → Search "Dataview"
3. Install → Enable
4. Reload vault

Now queries will work.
