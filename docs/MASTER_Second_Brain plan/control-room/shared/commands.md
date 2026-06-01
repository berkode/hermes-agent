# Hermes commands (Berkode)

## Profiles

```bash
hermes profile list
hermes -p bej chat
hermes -p ops chat
hermes -p social chat
```

## MASTER / vault

```bash
hermes master init --vault-path ~/Master
hermes master init --vault-path ~/Master --overwrite
hermes -p bej master install-cron --vault-path ~/Master
```

## Cron (profile bej)

```bash
hermes -p bej cron list
hermes -p bej cron resume <job-id>    # one job at a time after shadow graduation
hermes -p bej cron pause <job-id>
hermes -p bej cron edit <id> --deliver discord
```

## Kanban

```bash
hermes kanban init
hermes kanban create berkode-ops --description "Berkode employee board"
hermes kanban list --board berkode-ops
hermes kanban tail --board berkode-ops
```

## Fleet (dashboard)

```bash
hermes dashboard    # http://127.0.0.1:8000 — Services tab for gateway, Pimono, etc.
```

## Env (no secrets in this doc)

Set in `~/.hermes/profiles/bej/.env`:

- `OBSIDIAN_VAULT_PATH=~/Master`
- `WIKI_PATH=~/Master`

Secrets: `~/.hermes/profiles/<profile>/.env.encrypted` only.
