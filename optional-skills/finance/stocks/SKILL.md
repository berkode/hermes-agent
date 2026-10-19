---
name: stocks
description: Read-only quotes from APPROVED sources only. TradingView covers equities, ETFs, futures and FX. Hyperliquid and Binance cover crypto. IBKR marks for held positions come via bejtrader. Yahoo and Alpha Vantage were removed.
version: 0.2.0
author: Mibay (Mibayy), Hermes Agent; Bej policy edit 2026-10-19
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Stocks, Finance, Market, Crypto, Investing, TradingView, Hyperliquid, Binance, IBKR]
    category: finance
    related_skills: [dcf-model, comps-analysis, lbo-model]
---

# Stocks Skill (approved sources only)

**Policy (Master, 2026-10-19):** the only allowed price sources are IBKR, TradingView, Hyperliquid, Binance and axiom.trade. **Yahoo Finance and Alpha Vantage are banned as price sources.** Never call them, not even as a fallback. Alpha Vantage is used only for the daily earnings *dates* file, `~/berkode/bejcapital/data/earnings/earnings_calendar_latest.json`, which is not a price.

Sources used by `stocks_client.py`. All are free, need no key, and use Python stdlib only.
- **Equities, ETFs, futures, FX**: the TradingView public scanner plus symbol search. On the free feed, US equities usually lag by 15 minutes. Check `feed` (`update_mode`, e.g. `delayed_streaming_900`).
- **Crypto**: Hyperliquid `allMids` (perp mid) first, then Binance public market data (`data-api.binance.vision`). Binance adds the 24h change and volume.
- **IBKR marks for positions we hold**: `positions` reads bejtrader `GET http://127.0.0.1:5001/api/positions`. It is read-only.

## How to Run
```
SCRIPT=~/.hermes/profiles/bej/skills/finance/stocks/scripts/stocks_client.py
python3 $SCRIPT quote AAPL MSFT          # TradingView
python3 $SCRIPT quote NASDAQ:NVDA        # explicit TV symbol
python3 $SCRIPT search "Tesla"
python3 $SCRIPT history NVDA --range 6mo # TV performance summary (no daily bars)
python3 $SCRIPT compare AAPL MSFT GOOGL
python3 $SCRIPT crypto BTC ETH SOL       # Hyperliquid / Binance
python3 $SCRIPT positions                # IBKR marks via bejtrader
```
The output is JSON. Every row carries `source`.

## Pitfalls
- The free TradingView feed is delayed for many US listings, so never present it as real-time. Quote `feed`.
- `history` returns performance percentages and 52-week levels, not OHLCV. For bars, use IBKR (bejtrader) or a TradingView chart.
- Binance.com returns HTTP 451 from this VM, so the script uses the public `data-api.binance.vision` mirror instead.
- This skill is read-only. It has no order tools.

## Verification
`python3 $SCRIPT quote AAPL` returns `"source": "tradingview"` and a numeric `price`.
