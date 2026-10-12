---
name: stocks
description: Live IB, TradingView, Hyperliquid, or Binance quotes.
version: 0.2.0
author: Mibay (Mibayy), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Stocks, Finance, Market, Crypto, Investing]
    category: finance
    related_skills: [dcf-model, comps-analysis, lbo-model]
---

# Stocks Skill

Read-only live quotes and daily bars. Unapproved delayed tapes are not
sources. Equities go through the BejTrader IB `/scan` endpoint on
loopback; crypto through Hyperliquid then Binance; TradingView is the
scanner/search tape. No approved live source → refuse.

## When to Use

- User asks for a current stock or crypto price
- User wants OHLCV history or a side-by-side compare
- User wants a ticker lookup by name (TradingView search)

## Prerequisites

Python 3 stdlib only. On the Oracle VM, BejTrader must be listening on
`http://127.0.0.1:5001` for IB-backed equity/futures bars. Override with
`BEJTRADER_URL` only when the host is loopback. Crypto does not need IB.

## How to Run

Invoke through the `terminal` tool. Once installed:

```
SCRIPT=~/.hermes/skills/finance/stocks/scripts/stocks_client.py
python $SCRIPT quote AAPL
```

All output is JSON on stdout.

## Quick Reference

```
python $SCRIPT quote AAPL
python $SCRIPT quote AAPL MSFT
python $SCRIPT search Tesla
python $SCRIPT history NVDA --range 6mo
python $SCRIPT compare AAPL MSFT
python $SCRIPT crypto BTC
```

## Commands

### `quote SYMBOL [SYMBOL2 ...]`

Last live close, change, volume. IB `/scan` first for non-crypto; TV scanner
if IB is down. Crypto uses Hyperliquid then Binance.

### `search QUERY`

TradingView symbol search. Top 5 matches.

### `history SYMBOL [--range RANGE]`

Daily OHLCV. Ranges: `1mo`, `3mo`, `6mo`, `1y`, `5y`. Default: `1mo`.

### `compare SYMBOL1 SYMBOL2 [...]`

Side-by-side live quotes.

### `crypto SYMBOL`

Hyperliquid public candles, else Binance. Pass `BTC` (USD quote).

## Pitfalls

- Missing IB on loopback plus a failed TV/HL/Binance fetch prints
  `{"error": "no approved live source"}` — there is no delayed fallback.
- `BEJTRADER_URL` must stay loopback (`127.0.0.1` / `localhost`). Public
  hosts are refused.
- This is read-only — no order placement.

## Verification

```
python ~/.hermes/skills/finance/stocks/scripts/stocks_client.py quote AAPL
```

On the VM with BejTrader up, JSON includes `symbol` and `price` and
`data_source` of `ibkr`, `tradingview`, `hyperliquid`, or `binance`.
Without a live tape the JSON `error` is `no approved live source`.
