# Employee 01 — Shadow mode (manual week)

Cron stays **off**. You run each workflow in chat, review output, label quality in Discord or a note.

## One-time

```bash
# Hermes CLI pinned to repo .venv (MacPorts 3.13)
ln -sf ~/berkode/hermes-agent/scripts/hermes-wrapper.sh ~/.local/bin/hermes

# Profile env (paths only — use your encrypted flow for secrets)
# In ~/.hermes/profiles/bej/.env:
# OBSIDIAN_VAULT_PATH=/Users/morpheus/Master
# WIKI_PATH=/Users/morpheus/Master

cd ~/berkode/bejcapital
hermes -p bej
```

## Daily ritual (~15–20 min)

Run in order inside `hermes -p bej` (from bejcapital cwd for code tools; vault via Obsidian skill):

| Step | Command / phrase | Save location |
|------|------------------|---------------|
| 1 | `process my inbox` | `00-INBOX/process-inbox-YYYY-MM-DD.md` |
| 2 | `run daily brief` or `morning brief` | `00-INBOX/brief-YYYY-MM-DD.md` |
| 3 | `run social drafts` | `05-HERMES/agents/employee-01/social-drafts/YYYY-MM-DD/` |
| 4 | `run inbox triage` (Himalaya) | `05-HERMES/agents/employee-01/inbox-triage/YYYY-MM-DD.md` |
| 5 | `end of day learning` | `05-HERMES/agents/employee-01/learning/YYYY-MM-DD.md` |

Reference files: `05-HERMES/HERMES.md`, `BEJMIND.md`, `agents/employee-01/EMPLOYEE_01.md`, `workflows/*.md`.

## Quality labels (reply to Hermes)

Use short labels so patterns stick in the vault:

- `good` — keep this style
- `too wordy` — shorten
- `too salesy` — more analytical
- `missed risk` — flag downside
- `good pattern, weak connection` — logic ok, links weak

## Graduate to cron when

For **5+ weekdays**: brief is useful without heavy edits, triage catches important mail, at least one social or email draft you would send.

Then:

1. Start gateway via `hermes dashboard` → Services (Level 4 requires gateway up).
2. Install cron templates (jobs stay paused until you resume each):

```bash
hermes -p bej master install-cron --vault-path ~/Master
hermes -p bej cron list
hermes -p bej cron resume <daily-brief-job-id>   # one job only at first
```

3. Record the job id in `05-HERMES/control-room/agents/employee-01-chief/inventory.md`.

**Order after daily brief is stable:** inbox triage → social drafts → end-of-day learning. Enable portfolio review (Employee 03) only after quant/risk workflows look good in shadow.

See `05-HERMES/control-room/shared/fleet-requirements.md` for full Level 4 checklist.

## Trading desk shadow (Employees 02–04)

Before enabling desk crons, run each workflow **2–3 times** manually:

| Employee | Phrase | Profile |
|----------|--------|---------|
| 02 Quant | `quant research on [topic]` | `bej` |
| 03 Portfolio | `portfolio review` | `bej` |
| 04 Architect | `architecture review` | `ops` |

Read `05-HERMES/company-brain/` on every trading-desk run. No live trading from Hermes.

## Two “homes” (not a bug)

| Setting | Purpose |
|---------|---------|
| `terminal.cwd` → bejcapital | Code, terminal, GitHub |
| Vault `05-HERMES/` + `OBSIDIAN_VAULT_PATH` | Briefs, employees, notes |
| Cron `--workdir …/05-HERMES` | Only for scheduled brief jobs |

Interactive chat uses bejcapital; Obsidian skill reads `~/Master` via env.
