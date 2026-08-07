---
name: tradingview-sync
description: Push edited Pine scripts to TradingView via Playwright.
version: 0.1.0
author: Master + Hermes Agent
license: MPL-2.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [tradingview, pine, bejcapital, automation, playwright]
    category: devops
    related_skills: [github-pr-workflow]
---

# TradingView Sync Skill

Automates pushing local Pine Script™ files in
`bejcapital/bejtrader/tradingview/` to TradingView's Pine Editor so the user
never has to copy/paste from VS Code → TV.

Use when the user says any of:

- "sync TV", "push to TradingView", "publish library", "bump library version"
- "watch TradingView" (start the daemon)
- "what's mapped on TradingView?"

## When to Use

- After editing a `.pine` file under `bejcapital/bejtrader/tradingview/`.
- When a BejCap library has been edited and downstream strategies need the
  new version (publish path bumps the import index).
- To list which scripts are mapped and which are missing URLs.

## When NOT to Use

- For Pine debugging or compilation help — that's a code task, not a sync
  task. Edit locally and only sync once the script compiles.
- For TradingView chart screenshots — that's the `chart_fetcher` /
  vision pipeline, not this skill.

## Prerequisites

1. **`TRADINGVIEW_SESSION_ID`** in encrypted env (already plumbed via
   `bejtrader.config.settings`).
2. **Browser** — one of:
   - **`CAMOFOX_URL`** (recommended): Camofox running via Hermes dashboard /
     `app/scripts/start-camofox.sh`. No Playwright install needed.
   - **`BROWSER_CDP_URL`** or Hermes `browser.cdp_url`: attached Chrome debug.
   - **Fallback only**: `python -m playwright install chromium` inside the
     bejtrader venv (use `python -m`, not the bare `playwright` command).
3. **Mapping file** at `bejtrader/config/tradingview_scripts.yaml`
   (`tv-sync init` if missing).

## How to Run

All commands go through `terminal` with `cwd=~/berkode/bejcapital` and the
local venv activated.

### Show what's mapped

```bash
source .venv/bin/activate
python -m bejtrader.tradingview.sync.cli list
```

### Push a single script (save, no version bump)

```bash
python -m bejtrader.tradingview.sync.cli push "BejCap Dashboard [BejCapital].pine"
```

### Publish a new library version (bumps `/n/` import)

```bash
python -m bejtrader.tradingview.sync.cli push libraries/BejCore.pine --publish
```

### Scheduled fleet push (preferred — Hermes cron)

No manual start and no platform-start hook needed. Once installed, Hermes
gateway fires a **script-only** cron every 6 hours:

```bash
./bejtrader/scripts/install-tv-sync-hermes-cron.sh
# creates ~/.hermes/profiles/bej/scripts/tv-sync-push.sh
# + cron job "TradingView Pine fleet sync" (0 */6 * * *, --no-agent)
```

Worker: `bejtrader/scripts/tv-sync-cron-push.sh` → `tv-sync watch --once`.
Logs: `~/.hermes/logs/tv-sync-cron.log`. Deliver: `local` (errors alert).

```bash
hermes --profile bej cron list | grep -A8 'TradingView Pine'
hermes --profile bej cron run <job_id>   # fire once to test
```

### Daemon — local long-running watcher (optional)

Only if Hermes gateway is unavailable:

```bash
./bejtrader/scripts/start-tv-sync-watcher.sh
# or: python -m bejtrader.tradingview.sync.cli watch
```

Default config: **fleet push every 6 hours** (`poll_seconds: 21600`,
`push_all_on_poll: true`). Prefer Hermes cron over this daemon.

### Bootstrap the mapping file

```bash
python -m bejtrader.tradingview.sync.cli init
```

Then edit `bejtrader/config/tradingview_scripts.yaml` and paste each script's
TradingView URL into the matching entry.

## Quick Reference

| Command | What it does |
|---------|--------------|
| `tv-sync.cli list`                       | Print file ↔ URL mapping table. |
| `tv-sync.cli push <file>`                | Save script (no version bump). |
| `tv-sync.cli push <file> --publish`      | Library only — publish new version. |
| `tv-sync.cli push` (no args)             | Push every mapped script. |
| `tv-sync.cli watch`                      | Daemon — poll + auto-push (optional). |
| `tv-sync.cli watch --once`               | Single sweep, then exit (CI / Hermes cron). |
| `tv-sync.cli init`                       | Write `tradingview_scripts.yaml` template. |
| `install-tv-sync-hermes-cron.sh`         | Register 6h Hermes no-agent cron (preferred). |
| `tv-sync-cron-push.sh`                   | One-shot fleet push used by that cron. |

## Procedure

1. Confirm the user has saved their edits.
2. Run `tv-sync list` first to see if the target file has a URL set.
3. If URL is empty → tell the user to push it once via the TV UI (or use
   `--headed` so the user can paste the URL after); then add the URL to
   `tradingview_scripts.yaml`.
4. For library edits — ask whether to **save** or **publish new version**.
   Default to **publish** if the file is under `libraries/` and downstream
   strategies use it.
5. Run the push and report the per-file result (action, duration, errors).

## Pitfalls

- **Empty file refuses to push.** The client raises `TvSyncError` rather
  than blanking a TradingView script. Investigate the local file first.
- **2FA accounts** must also set `TRADINGVIEW_SESSION_ID_SIGN`.
- **Pine compile errors** still apply — the editor will save the broken
  source. After a successful push, verify on TradingView that the script
  compiles. The skill cannot detect Pine compile errors remotely.
- **Library version bump propagation**: bumping `BejCore` to `/2/` does
  *not* automatically rewrite import lines in downstream scripts. Update
  those `import BejCapital/BejCore/2 as core` lines manually (or with
  `sed`) and re-sync them.
- **Headless on macOS**: TV occasionally throws a captcha on first
  headless session. If sync fails with a generic timeout, retry with
  `--headed` once to clear the challenge.
- **Camofox vs Playwright**: Prefer `CAMOFOX_URL` — it reuses the same
  anti-detection browser Hermes already runs and avoids installing Chromium.

## Verification

After a save:

1. Open the script's URL in a real browser and confirm the source
   matches the local file.
2. For libraries, check the "Version history" panel to confirm the
   new version is listed.
3. For strategies, attach the chart and confirm there are no
   compilation errors in TV's status bar.

## See Also

- `bejcapital/bejtrader/tradingview/README.md` — full surface docs.
- `bejcapital/bejtrader/tradingview/sync/client.py` — implementation.
- `bejcapital/bejtrader/tradingview/push_tv_levels.py` — operator-level
  YAML pusher (different tool — that one drives `input.price()` values,
  not source code).
