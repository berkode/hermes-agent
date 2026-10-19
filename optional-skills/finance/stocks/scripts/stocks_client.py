#!/usr/bin/env python3
"""Read-only market data via APPROVED sources only (Bej policy 2026-10-19).

Equities/ETFs/futures/FX: TradingView public scanner + symbol search (free, no key;
  US equities are typically 15-min delayed on the free feed -> see "update_mode").
Crypto: Hyperliquid public info API (mids), Binance public market data
  (data-api.binance.vision) for 24h change/volume.
IBKR marks for HELD positions: bejtrader GET http://127.0.0.1:5001/api/positions (read-only).

Yahoo Finance and Alpha Vantage price paths were REMOVED 2026-10-19 (banned price sources).
Stdlib only. Output is JSON on stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

TV_SCAN = "https://scanner.tradingview.com/symbol"
TV_SEARCH = "https://symbol-search.tradingview.com/symbol_search/v3/"
HL_INFO = "https://api.hyperliquid.xyz/info"
BINANCE = "https://data-api.binance.vision/api/v3"
BEJTRADER_POSITIONS = "http://127.0.0.1:5001/api/positions"
UA = {"User-Agent": "Mozilla/5.0 (bej-hermes-stocks-skill)", "Origin": "https://www.tradingview.com",
      "Referer": "https://www.tradingview.com/"}
QUOTE_FIELDS = ["description", "close", "change", "change_abs", "volume", "price_52_week_high",
                "price_52_week_low", "market_cap_basic", "price_earnings_ttm", "currency", "exchange",
                "update_mode", "type"]
PERF_FIELDS = ["close", "Perf.W", "Perf.1M", "Perf.3M", "Perf.6M", "Perf.YTD", "Perf.Y", "Perf.5Y",
               "price_52_week_high", "price_52_week_low", "update_mode"]


def out(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def http_json(url: str, data: dict | None = None, timeout: float = 15.0):
    body = json.dumps(data).encode() if data is not None else None
    headers = dict(UA)
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers)
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 404):
                return None
            time.sleep(1 + attempt)
        except Exception:  # noqa: BLE001
            time.sleep(1 + attempt)
    return None


def tv_search(text: str, limit: int = 5) -> list[dict]:
    qs = urllib.parse.urlencode({"text": text, "hl": 0, "lang": "en", "domain": "production"})
    data = http_json(f"{TV_SEARCH}?{qs}") or {}
    rows = data.get("symbols", []) if isinstance(data, dict) else []
    res = []
    for r in rows[:limit]:
        res.append({"symbol": r.get("symbol"), "exchange": r.get("exchange"),
                    "tv_symbol": f"{r.get('exchange')}:{r.get('symbol')}",
                    "name": r.get("description"), "type": r.get("type"),
                    "currency": r.get("currency_code")})
    return res


def resolve(symbol: str) -> str | None:
    s = symbol.strip().upper()
    if ":" in s:
        return s
    for r in tv_search(s, limit=10):
        if (r.get("symbol") or "").upper() == s and r.get("type") in ("stock", "fund", "dr", "index", "futures"):
            return r["tv_symbol"]
    hits = tv_search(s, limit=1)
    return hits[0]["tv_symbol"] if hits else None


def tv_fields(tv_symbol: str, fields: list[str]) -> dict | None:
    qs = urllib.parse.urlencode({"symbol": tv_symbol, "fields": ",".join(fields)})
    d = http_json(f"{TV_SCAN}?{qs}")
    return d if isinstance(d, dict) else None


def quote_one(symbol: str) -> dict:
    tv = resolve(symbol)
    if not tv:
        return {"symbol": symbol.upper(), "error": "symbol not found on TradingView"}
    d = tv_fields(tv, QUOTE_FIELDS)
    if not d:
        return {"symbol": symbol.upper(), "tv_symbol": tv, "error": "no data from TradingView scanner"}
    return {"symbol": symbol.upper(), "tv_symbol": tv, "name": d.get("description"),
            "price": d.get("close"), "change": d.get("change_abs"), "change_pct": d.get("change"),
            "volume": d.get("volume"), "fifty_two_week_high": d.get("price_52_week_high"),
            "fifty_two_week_low": d.get("price_52_week_low"), "market_cap": d.get("market_cap_basic"),
            "pe_ratio": d.get("price_earnings_ttm"), "currency": d.get("currency"),
            "feed": d.get("update_mode"), "source": "tradingview"}


def cmd_quote(symbols: list[str]) -> None:
    res = [quote_one(s) for s in symbols]
    out(res[0] if len(res) == 1 else res)


def cmd_search(query: str) -> None:
    out({"query": query, "results": tv_search(query), "source": "tradingview"})


def cmd_history(symbol: str, range_: str = "1mo") -> None:
    tv = resolve(symbol)
    d = tv_fields(tv, PERF_FIELDS) if tv else None
    if not d:
        out({"symbol": symbol.upper(), "error": "no data from TradingView scanner"})
        return
    key = {"1w": "Perf.W", "1mo": "Perf.1M", "3mo": "Perf.3M", "6mo": "Perf.6M", "ytd": "Perf.YTD",
           "1y": "Perf.Y", "5y": "Perf.5Y"}.get(range_, "Perf.1M")
    out({"symbol": symbol.upper(), "tv_symbol": tv, "range": range_, "price": d.get("close"),
         "total_return_pct": d.get(key),
         "performance_pct": {k: d.get(v) for k, v in [("1w", "Perf.W"), ("1mo", "Perf.1M"), ("3mo", "Perf.3M"),
                                                       ("6mo", "Perf.6M"), ("ytd", "Perf.YTD"), ("1y", "Perf.Y"),
                                                       ("5y", "Perf.5Y")]},
         "fifty_two_week_high": d.get("price_52_week_high"), "fifty_two_week_low": d.get("price_52_week_low"),
         "feed": d.get("update_mode"), "source": "tradingview",
         "note": "Daily OHLCV bars are not served by the free TradingView scanner; for bars use IBKR (bejtrader) or a TradingView chart."})


def cmd_compare(symbols: list[str]) -> None:
    rows = []
    for s in symbols:
        tv = resolve(s)
        d = tv_fields(tv, ["description", "close", "change", "Perf.Y", "price_52_week_high", "price_52_week_low"]) if tv else None
        rows.append({"symbol": s.upper(), "tv_symbol": tv, "name": (d or {}).get("description"),
                     "price": (d or {}).get("close"), "change_pct": (d or {}).get("change"),
                     "perf_1y_pct": (d or {}).get("Perf.Y"),
                     "fifty_two_week_high": (d or {}).get("price_52_week_high"),
                     "fifty_two_week_low": (d or {}).get("price_52_week_low")})
    out({"comparison": rows, "source": "tradingview"})


def cmd_crypto(symbols: list[str], vs: str = "USD") -> None:
    mids = http_json(HL_INFO, {"type": "allMids"}) or {}
    res = []
    for raw in symbols:
        sym = raw.upper().replace("-USD", "").replace("USDT", "")
        row = {"symbol": sym}
        if sym in mids:
            row.update({"price": float(mids[sym]), "source": "hyperliquid", "quote": "USD(C) perp mid"})
        t = http_json(f"{BINANCE}/ticker/24hr?symbol={sym}USDT")
        if isinstance(t, dict) and t.get("lastPrice"):
            row.setdefault("price", float(t["lastPrice"]))
            row.setdefault("source", "binance")
            row.update({"binance_last_usdt": float(t["lastPrice"]),
                        "change_pct_24h": float(t.get("priceChangePercent") or 0),
                        "volume_24h_base": float(t.get("volume") or 0)})
        if "price" not in row:
            row["error"] = "not found on Hyperliquid or Binance"
        res.append(row)
    out(res[0] if len(res) == 1 else res)


def cmd_positions() -> None:
    d = http_json(BEJTRADER_POSITIONS, timeout=10)
    out({"source": "ibkr via bejtrader (read-only)", "positions": d} if d is not None
        else {"error": "bejtrader positions API unreachable"})


def main() -> None:
    p = argparse.ArgumentParser(description="Read-only quotes: TradingView (equities), Hyperliquid/Binance (crypto), IBKR marks via bejtrader. Yahoo/Alpha Vantage removed.")
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("quote"); a.add_argument("symbols", nargs="+")
    a = sub.add_parser("search"); a.add_argument("query")
    a = sub.add_parser("history"); a.add_argument("symbol"); a.add_argument("--range", default="1mo",
        choices=["1w", "1mo", "3mo", "6mo", "ytd", "1y", "5y"])
    a = sub.add_parser("compare"); a.add_argument("symbols", nargs="+")
    a = sub.add_parser("crypto"); a.add_argument("symbols", nargs="+")
    sub.add_parser("positions", help="IBKR-marked held positions via bejtrader (read-only)")
    args = p.parse_args()
    if args.command == "quote":
        cmd_quote(args.symbols)
    elif args.command == "search":
        cmd_search(args.query)
    elif args.command == "history":
        cmd_history(args.symbol, args.range)
    elif args.command == "compare":
        cmd_compare(args.symbols)
    elif args.command == "crypto":
        cmd_crypto(args.symbols)
    elif args.command == "positions":
        cmd_positions()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
