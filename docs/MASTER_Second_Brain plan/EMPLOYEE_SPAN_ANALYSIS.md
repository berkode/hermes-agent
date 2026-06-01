# Employee Span Analysis

> **Superseded for operations:** use [`AGILE_REVISION.md`](AGILE_REVISION.md) (12 core roles) and [`control-room/FLEET_REGISTRY.md`](control-room/FLEET_REGISTRY.md) for the live fleet map. This document remains as historical gap analysis (30-role vision).

# Employee Span Analysis (historical) — What We're Missing for Full Company Structures

## Current Employee Coverage (9 Employees)

| Employee | Role | Company | Coverage | Gaps |
|----------|------|---------|----------|------|
| **01** | Research & Distribution Operator | BejCapital | ✅ Daily brief, social drafts, inbox triage, learning | ❌ No real-time market data integration, no auto-posting yet |
| **02** | Quant Researcher & Analyst | BejCapital | ✅ Research, backtests, strategy ideas | ❌ No live data feed, no auto-deploy strategies |
| **03** | Portfolio Manager | BejCapital | ✅ Portfolio review, risk assessment, stress tests | ❌ No live position tracking, no auto-rebalance |
| **04** | Software Architect | BejCapital | ✅ Architecture reviews, design docs, refactor proposals | ❌ No auto-code generation, no CI/CD integration |
| **05** | Frontend UX Designer | BejCapital | ✅ UX reviews, wireframes, design systems | ❌ No auto-ui implementation, no A/B testing |
| **06** | Altair Merchandiser | Altair | ✅ Customer comments, action plans, follow-ups | ❌ No auto-translate API, no web scraper for comments |
| **07** | Brentford Contract Manager | Brentford Capital | ✅ Contract drafts, task follow-ups, opportunities | ❌ No auto-signature, no legal review automation |
| **08** | Rockerforce Sales | Rockerforce | ✅ Lead generation, proposals, follow-ups | ❌ No auto-outreach, no CRM integration |
| **09** | Rockerforce Social | Rockerforce | ✅ Content calendar, post drafts, brand checks | ❌ No auto-posting, no analytics integration |

## Missing Roles for Full Company Structures

### A. BejCapital / Bejtrader (Quant Trading Platform)

**Current**: Employee 01 (ops), 02 (research), 03 (portfolio), 04 (architect), 05 (UX)

**Missing**:

| Role | Name | Responsibilities | Priority |
|------|------|------------------|----------|
| **Data Engineer** | Employee 10 | Build/maintain data pipelines (OHLCV, fundamentals, alternative data), ensure data quality, handle missing data | P0 |
| **Execution Engineer** | Employee 11 | Build/maintain order routing, slippage modeling, transaction cost analysis, broker adapters (IBKR, others) | P0 |
| **Risk Engineer** | Employee 12 | Real-time risk monitoring, position limits, drawdown controls, kill switches, regulatory compliance | P0 |
| **ML Engineer** | Employee 13 | Feature engineering, model training pipelines, hyperparameter optimization, model monitoring, drift detection | P1 |
| **DevOps Engineer** | Employee 14 | CI/CD pipelines, containerization (Docker/K8s), monitoring (Prometheus/Grafana), alerts, uptime | P1 |

### B. Brentford Capital (Alternative Finance / Deal Advisory)

**Current**: Employee 07 (contract manager)

**Missing**:

| Role | Name | Responsibilities | Priority |
|------|------|------------------|----------|
| **Deal Origination Specialist** | Employee 15 | Find deals (commodity trades, project finance, M&A), screen opportunities, initial due diligence | P0 |
| **Financial Analyst** | Employee 16 | Financial modeling, valuation, DCF, comparables, sensitivity analysis, investment memos | P0 |
| **Legal Counsel (AI-assisted)** | Employee 17 | Contract review, clause library, legal research, regulatory compliance, risk flagging | P1 |
| **Relationship Manager** | Employee 18 | Client relationships, networking, follow-ups, meeting notes, CRM updates | P1 |

### C. Altair (Merchandising / Customer → Factory)

**Current**: Employee 06 (merchandiser)

**Missing**:

| Role | Name | Responsibilities | Priority |
|------|------|------------------|----------|
| **Quality Control Specialist** | Employee 19 | Product quality checks, factory audits, defect tracking, supplier ratings | P0 |
| **Supply Chain Coordinator** | Employee 20 | Logistics, shipping, customs, inventory management, lead time tracking | P1 |
| **Pricing Analyst** | Employee 21 | Cost modeling, margin analysis, price optimization, competitor pricing | P1 |

### D. Rockerforce (AI Automation Agency)

**Current**: Employee 08 (sales), 09 (social)

**Missing**:

| Role | Name | Responsibilities | Priority |
|------|------|------------------|----------|
| **Delivery Manager** | Employee 22 | Project delivery, client communication, milestone tracking, scope management | P0 |
| **Automation Engineer** | Employee 23 | Build automation scripts (n8n, Zapier, custom), API integrations, workflow design | P0 |
| **Customer Success Manager** | Employee 24 | Onboarding, training, support tickets, renewal conversations, upsell opportunities | P1 |
| **Marketing Specialist** | Employee 25 | Paid ads, SEO, email campaigns, landing pages, conversion optimization | P1 |

### E. Cross-Company / Platform-Level

**Missing**:

| Role | Name | Responsibilities | Priority |
|------|------|------------------|----------|
| **Chief of Staff (AI)** | Employee 26 | Executive support, meeting prep, decision tracking, strategic initiatives, board prep | P0 |
| **CFO (AI-assisted)** | Employee 27 | Financial planning, cash flow, budgeting, tax prep, investor reporting | P0 |
| **CTO (AI-assisted)** | Employee 28 | Tech strategy, vendor selection, security, architecture governance, tech debt roadmap | P0 |
| **HR / Culture Officer** | Employee 29 | Hiring, onboarding, performance reviews, culture docs, team alignment | P2 |
| **IT Support** | Employee 30 | Helpdesk, troubleshooting, software licenses, hardware, security patches | P2 |

## Priority Matrix

### P0 (Critical — Must Have for Operations)

1. **Employee 10: Data Engineer** (BejCapital) — No data, no trading
2. **Employee 11: Execution Engineer** (BejCapital) — Can't execute trades without it
3. **Employee 12: Risk Engineer** (BejCapital) — Can't risk blown-up account
4. **Employee 15: Deal Origination** (Brentford) — No deals, no business
5. **Employee 16: Financial Analyst** (Brentford) — Can't value deals
6. **Employee 22: Delivery Manager** (Rockerforce) — Can't deliver projects
7. **Employee 23: Automation Engineer** (Rockerforce) — Can't build automation
8. **Employee 26: Chief of Staff** (Cross-company) — Executive-level coordination

### P1 (High — Important but Can Wait 1–2 Months)

- Employee 13: ML Engineer
- Employee 14: DevOps Engineer
- Employee 17: Legal Counsel
- Employee 18: Relationship Manager
- Employee 20: Supply Chain Coordinator
- Employee 21: Pricing Analyst
- Employee 24: Customer Success Manager
- Employee 25: Marketing Specialist
- Employee 27: CFO
- Employee 28: CTO

### P2 (Medium — Nice to Have, Can Wait 3+ Months)

- Employee 19: Quality Control Specialist
- Employee 29: HR / Culture Officer
- Employee 30: IT Support

## Implementation Strategy

### Phase A: Fill P0 Gaps (Weeks 17–24)

Add 8 new employees (10–18, 22–23, 26):
- Week 17–18: Employee 10 (Data Engineer)
- Week 19–20: Employee 11 (Execution Engineer)
- Week 21–22: Employee 12 (Risk Engineer)
- Week 23–24: Employee 15–16 (Brentford core)

### Phase B: Fill P1 Gaps (Weeks 25–36)

Add 10 new employees (13–14, 17–18, 20–21, 24–25, 27–28):
- 1–2 employees per 1–2 weeks
- Prioritize by business impact

### Phase C: Fill P2 Gaps (Weeks 37+)

Add remaining 3 employees (19, 29–30):
- Only if workload justifies it

## Revised Total: 30 Employees

| Category | Count |
|----------|-------|
| Original 9 | 9 |
| P0 additions | 8 |
| P1 additions | 10 |
| P2 additions | 3 |
| **Total** | **30** |

## Key Insight

You don't need all 30 employees at once. **Start with the original 9**, train them, then **incrementally add P0 roles** as:
- Workload increases
- You identify bottlenecks
- You have cash flow to support more automation

The original 9 are your **MVP team**. The additional 21 are **scale-up roles**.

## Recommendation

1. **Weeks 1–16**: Build and train the original 9 employees (as per CURSOR_PROJECT_PLAN.md)
2. **Weeks 17–24**: Add P0 roles (Data Engineer, Execution Engineer, Risk Engineer, Deal Origination, Financial Analyst, Delivery Manager, Automation Engineer, Chief of Staff)
3. **Weeks 25+**: Add P1/P2 roles only if needed

This keeps your **initial workload manageable** while giving you a **clear roadmap to full company structure**.
