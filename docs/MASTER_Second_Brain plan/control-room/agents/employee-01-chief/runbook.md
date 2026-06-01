# Runbook — Employee 01

## Shadow mode (manual)

```bash
cd ~/berkode/bejcapital
hermes -p bej
```

Phrases: `run daily brief`, `process my inbox`, `run social drafts`, `run inbox triage`, `end of day learning`.

## Enable cron (one job at a time)

```bash
hermes -p bej master install-cron --vault-path ~/Master
hermes -p bej cron list
hermes -p bej cron resume <daily-brief-job-id>
```

Requires gateway up — see `shared/fleet-requirements.md`.

## Kanban follow-ups

When brief lists actionable follow-ups, create `[brief]` tasks on board `berkode-ops` (assignee `bej`).

## Debug

- Brief empty: check `OBSIDIAN_VAULT_PATH` in `~/.hermes/profiles/bej/.env`
- No Discord: verify gateway + Discord platform in profile config
- Logs: `hermes -p bej logs --follow`
