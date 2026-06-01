# Workflow: Executive Review (Employee 12)

**Trigger phrases**:  
- "financial plan"  
- "tech strategy"  
- "executive review"  
- "OKR progress"  
- "budget review"

**Schedule**: Monthly 1st day, 9:00 AM CEST via Hermes cron (Quarterly for executive review)

**Agent**: Employee 12 (BejExecutive 12)

**Prompt**:

## Context

Read:
- `MASTER/05-HERMES/HERMES.md`
- `MASTER/05-HERMES/agents/employee-12-cfo-cto/EMPLOYEE_12.md`
- `MASTER/04-PROJECTS/` (all companies, revenue, expenses)
- Financial reports (manual input or future accounting integration)
- Tech stack docs (Hermes, BejMind, Obsidian, Nautilus, IBKR, etc.)
- Vendor contracts (software subscriptions, cloud services)
- Security audit logs (manual input or future monitoring)
- Employee feedback on tools
- All monthly financial plans (past 3 months)
- All monthly tech strategy docs (past 3 months)
- All company OKRs (progress toward goals)

## Task (Monthly: Financial Plan + Tech Strategy)

### A. Financial Plan (CFO)

1. **P&L Statement**
   - Revenue by company (BejCapital, Brentford, Altair, Rockerforce)
   - Expenses by category (software, salaries, infrastructure, marketing, travel)
   - Gross profit, operating income, net income
   - Month-over-month change (%)

2. **Cash Flow Forecast**
   - Cash inflow (revenue, investments)
   - Cash outflow (expenses, CapEx)
   - Net cash flow
   - Ending cash balance
   - Runway (months until cash runs out at current burn rate)

3. **Budget Recommendations**
   - Where to cut (underperforming areas)
   - Where to invest (high-ROI opportunities)
   - 3 specific budget decisions for b. to make

4. **Financial Decisions for b.**
   - Decision 1: [e.g., "Approve $5k marketing budget for Q3"]
   - Decision 2: [e.g., "Hire freelance developer for $3k/month"]
   - Decision 3: [e.g., "Renew Nautilus subscription ($2k/year)"]

### B. Tech Strategy (CTO)

1. **Tech Stack Health Check**
   - What works well (list tools)
   - What doesn't work (list tools, why)
   - Bottlenecks (performance, reliability, cost)

2. **Vendor Comparison**
   - For key tools (e.g., cloud provider, monitoring, analytics)
   - Compare 2–3 options (features, price, reliability)
   - Recommendation

3. **Security Audit**
   - What's secure (list systems)
   - What's not secure (list vulnerabilities)
   - Risks (data breach, downtime, compliance)
   - Mitigation plan

4. **Tech Debt Roadmap**
   - What to fix (list items)
   - Effort (hours, complexity)
   - Priority (high/medium/low)
   - When to fix (timeline)

5. **Tech Decisions for b.**
   - Decision 1: [e.g., "Switch from AWS to GCP ($1k/month savings)"]
   - Decision 2: [e.g., "Upgrade Hermes to v2.0 (breaking changes)"]
   - Decision 3: [e.g., "Hire freelance security consultant ($2k)"]

## Output Format (Monthly)

### Financial Plan

Save as `MASTER/05-HERMES/agents/employee-12-cfo-cto/financial-plans/YYYY-MM-financial-plan.md`:

```markdown
# Financial Plan — YYYY-MM

## P&L Statement

### Revenue

| Company | Revenue | MoM Change |
|---------|---------|------------|
| BejCapital | $X | +Y% |
| Brentford | $X | +Y% |
| Altair | $X | +Y% |
| Rockerforce | $X | +Y% |
| **Total** | **$X** | **+Y%** |

### Expenses

| Category | Amount | MoM Change |
|----------|--------|------------|
| Software | $X | +Y% |
| Salaries | $X | +Y% |
| Infrastructure | $X | +Y% |
| Marketing | $X | +Y% |
| Travel | $X | +Y% |
| **Total** | **$X** | **+Y%** |

### Summary

- Gross profit: $X
- Operating income: $X
- Net income: $X
- Margin: X%

## Cash Flow Forecast (Next 3 Months)

| Month | Inflow | Outflow | Net | Ending Balance |
|-------|--------|---------|-----|----------------|
| M+1 | $X | $X | $X | $X |
| M+2 | $X | $X | $X | $X |
| M+3 | $X | $X | $X | $X |

**Runway**: X months at current burn rate

## Budget Recommendations

1. **Cut**: [Area], save $X/month
2. **Invest**: [Area], spend $X/month, expected ROI Y%
3. **Hold**: [Area], no change

## Financial Decisions for b.

1. [Decision 1]
2. [Decision 2]
3. [Decision 3]
```

### Tech Strategy

Save as `MASTER/05-HERMES/agents/employee-12-cfo-cto/tech-strategy/YYYY-MM-tech-strategy.md`:

```markdown
# Tech Strategy — YYYY-MM

## Tech Stack Health Check

### Works Well

- [Tool 1]: [why]
- [Tool 2]: [why]

### Doesn't Work

- [Tool 1]: [why]
- [Tool 2]: [why]

### Bottlenecks

1. [Bottleneck 1]: [impact]
2. [Bottleneck 2]: [impact]

## Vendor Comparison: [Tool Category]

| Vendor | Features | Price | Reliability | Recommendation |
|--------|----------|-------|-------------|----------------|
| Vendor A | ... | $X/mo | 99.9% | **Yes** |
| Vendor B | ... | $Y/mo | 99.5% | No |
| Vendor C | ... | $Z/mo | 99.0% | No |

## Security Audit

### Secure

- [System 1]: [why]
- [System 2]: [why]

### Not Secure

- [System 1]: [vulnerability]
- [System 2]: [vulnerability]

### Risks

1. [Risk 1]: [impact]
2. [Risk 2]: [impact]

### Mitigation Plan

1. [Action 1] — Effort: X hrs
2. [Action 2] — Effort: Y hrs

## Tech Debt Roadmap

| Item | Effort | Priority | When |
|------|--------|----------|------|
| [Item 1] | X hrs | High | M+1 |
| [Item 2] | Y hrs | Medium | M+2 |
| [Item 3] | Z hrs | Low | M+3 |

## Tech Decisions for b.

1. [Decision 1]
2. [Decision 2]
3. [Decision 3]
```

## Output Format (Quarterly: Executive Review)

Save as `MASTER/05-HERMES/agents/employee-12-cfo-cto/executive-reviews/YYYY-Q-executive-review.md`:

```markdown
# Executive Review — YYYY-Q

## Executive Summary

[2–3 paragraph summary: what's working, what's not, strategic pivots needed]

## OKR Progress Table

| Objective | Key Result | Status | Progress | Notes |
|-----------|------------|--------|----------|-------|
| Automate 80% | 12 employees trained | 🟢 | 10/12 | On track |
| Automate 80% | 5+ workflows on cron | 🟡 | 3/5 | Need 2 more |
| Bejtrader platform | 5+ strategies | 🔴 | 2/5 | Behind schedule |
| ... | ... | ... | ... | ... |

**Legend**: 🟢 On track, 🟡 At risk, 🔴 Behind

## Strategic Pivots Needed

1. [Pivot 1]: [rationale]
2. [Pivot 2]: [rationale]

## Next Quarter Priorities (Top 3)

1. [Priority 1] — Owner: [Employee], Deadline: [Date]
2. [Priority 2] — Owner: [Employee], Deadline: [Date]
3. [Priority 3] — Owner: [Employee], Deadline: [Date]

## Board Prep Deck (if applicable)

- Slide 1: Executive summary
- Slide 2: OKR progress
- Slide 3: Financials (P&L, cash flow)
- Slide 4: Tech stack health
- Slide 5: Risks & mitigations
- Slide 6: Next quarter priorities
```

Post a 300–400 word summary to Discord #hermes-chat:
- Monthly financial summary (revenue, expenses, runway)
- Key tech decisions needed (3)
- OKR progress (green/yellow/red)
- Next quarter top 3 priorities
- Ask: "Approve budget/tech decisions? (yes/no/modify)"
