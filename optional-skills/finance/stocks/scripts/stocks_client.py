#!/usr/bin/env python3
"""Live market-data CLI. Unapproved delayed tapes are not sources.

Approved live sources only:
- BejTrader IB OHLCV on loopback (default http://127.0.0.1:5001/scan)
- TradingView public scanner / symbol search
- Hyperliquid public /info (crypto)
- Binance public REST (crypto)

No approved live source → refuse with ``no approved live source``.
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

USER_AGENT = "Mozilla/5.0 (compatible; HermesAgent/1.0)"
HL_INFO = "https://api.hyperliquid.xyz/info"
BINANCE_API = "https://api.binance.com"
TV_SCANNER = "https://scanner.tradingview.com/symbol"
TV_SEARCH = "https://symbol-search.tradingview.com/symbol_search/"
DEFAULT_IB_URL = "http://127.0.0.1:5001"
REFUSE = "no approved live source"

_CRYPTO = frozenset(
    {
        "BTC",
        "ETH",
        "SOL",
        "XRP",
        "DOGE",
        "AVAX",
        "LINK",
        "ADA",
        "DOT",
        "MATIC",
        "ARB",
        "OP",
        "SUI",
        "APT",
        "LTC",
        "BCH",
        "ATOM",
        "NEAR",
        "INJ",
        "TIA",
    }
)

_APPROVED_HOSTS = frozenset(
    {
        "127.0.0.1",
        "localhost",
        "::1",
        "api.hyperliquid.xyz",
        "api.binance.com",
        "scanner.tradingview.com",
        "symbol-search.tradingview.com",
    }
)

_RANGE_BARS = {
    "1mo": 32,
    "3mo": 80,
    "6mo": 140,
    "1y": 270,
    "5y": 1300,
}

MAX_RETRIES = 3
BACKOFF_BASE = 1.5


def print_json(data: dict | list) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def refuse(symbol: str | None = None, detail: str = "", tried: list[str] | None = None) -> dict:
    payload: dict = {"error": REFUSE}
    if symbol:
        payload["symbol"] = symbol
    if detail:
        payload["detail"] = detail
    if tried:
        payload["tried"] = tried
    return payload


def fmt_price(value) -> str | None:
    if value is None:
        return None
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return None


def fmt_large(value) -> str | None:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if abs(v) >= 1e12:
        return f"{v / 1e12:.2f}T"
    if abs(v) >= 1e9:
        return f"{v / 1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"{v / 1e6:.2f}M"
    return str(int(v))


def fmt_pct(value) -> str | None:
    if value is None:
        return None
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return None


def ts_to_date(ts) -> str | None:
    if ts is None:
        return None
    try:
        if isinstance(ts, str) and "T" in ts:
            return ts[:10]
        raw = float(ts)
        if raw > 1e12:
            raw /= 1000.0
        return datetime.fromtimestamp(int(raw), tz=timezone.utc).strftime("%Y-%m-%d")
    except (OSError, ValueError, TypeError):
        return None


def is_approved_live_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    if host not in _APPROVED_HOSTS:
        return False
    if host in {"127.0.0.1", "localhost", "::1"}:
        return True
    return parsed.scheme == "https"


def crypto_coin(symbol: str) -> str | None:
    sym = (symbol or "").upper().strip()
    for suffix in ("-USD-PERP", "-USD", "USDT", "USDC", "USD", "-PERP"):
        if sym.endswith(suffix) and len(sym) > len(suffix):
            sym = sym[: -len(suffix)]
            break
    return sym if sym in _CRYPTO else None


def ib_base_url() -> str:
    raw = (os.environ.get("BEJTRADER_URL") or os.environ.get("BEJMIND_IB_URL") or DEFAULT_IB_URL).strip()
    return raw.rstrip("/")


def _build_request(url: str, payload: dict | list | None = None) -> urllib.request.Request:
    if not is_approved_live_url(url):
        raise PermissionError(f"{REFUSE}: blocked host {url}")
    data = None
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    for key, value in headers.items():
        req.add_header(key, value)
    return req


def fetch_json(url: str, payload: dict | list | None = None, retries: int = MAX_RETRIES) -> dict | list | None:
    last_err = None
    for attempt in range(retries):
        try:
            req = _build_request(url, payload)
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                return json.loads(raw.decode("utf-8", errors="replace"))
        except PermissionError:
            return None
        except urllib.error.HTTPError as exc:
            last_err = exc
            if exc.code in {400, 404, 422}:
                break
            time.sleep(BACKOFF_BASE ** attempt)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last_err = exc
            time.sleep(BACKOFF_BASE ** attempt)
    del last_err
    return None


def _bar(ts, open_, high, low, close, volume) -> dict | None:
    try:
        ohlc = [float(open_), float(high), float(low), float(close)]
    except (TypeError, ValueError):
        return None
    if any(v != v for v in ohlc):  # NaN
        return None
    try:
        vol = float(volume or 0)
    except (TypeError, ValueError):
        vol = 0.0
    return {
        "timestamp": ts,
        "open": ohlc[0],
        "high": ohlc[1],
        "low": ohlc[2],
        "close": ohlc[3],
        "volume": vol,
    }


def fetch_ib_ohlcv(symbol: str, timeframe: str, limit: int) -> tuple[list[dict], str | None]:
    base = ib_base_url()
    url = f"{base}/scan"
    if not is_approved_live_url(url):
        return [], "ib_not_loopback"
    payload = {"ticker": symbol, "timeframe": timeframe, "lookback_bars": int(limit)}
    data = fetch_json(url, payload=payload)
    if not isinstance(data, dict):
        return [], "ib_unavailable"
    rows = data.get("ohlcv")
    if not isinstance(rows, list) or not rows:
        return [], "ib_empty"
    bars: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        bar = _bar(
            row.get("timestamp"),
            row.get("open"),
            row.get("high"),
            row.get("low"),
            row.get("close"),
            row.get("volume"),
        )
        if bar:
            bars.append(bar)
    return bars, "ibkr" if bars else "ib_empty"


def fetch_hl_ohlcv(coin: str, interval: str, limit: int) -> tuple[list[dict], str | None]:
    seconds = {"1m": 60, "1h": 3600, "1d": 86400}.get(interval, 86400)
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - (limit + 2) * seconds * 1000
    payload = {
        "type": "candleSnapshot",
        "req": {"coin": coin, "interval": interval, "startTime": start_ms, "endTime": end_ms},
    }
    data = fetch_json(HL_INFO, payload=payload)
    if not isinstance(data, list) or not data:
        return [], "hyperliquid_empty"
    bars: list[dict] = []
    for candle in data:
        if not isinstance(candle, dict):
            continue
        bar = _bar(candle.get("t"), candle.get("o"), candle.get("h"), candle.get("l"), candle.get("c"), candle.get("v"))
        if bar:
            bars.append(bar)
    return bars[-limit:], "hyperliquid" if bars else "hyperliquid_empty"


def fetch_binance_ohlcv(symbol: str, vs: str, interval: str, limit: int) -> tuple[list[dict], str | None]:
    pair = f"{symbol.upper()}{vs.upper()}"
    qs = urllib.parse.urlencode({"symbol": pair, "interval": interval, "limit": int(limit)})
    url = f"{BINANCE_API}/api/v3/klines?{qs}"
    data = fetch_json(url)
    if not isinstance(data, list) or not data:
        return [], "binance_empty"
    bars: list[dict] = []
    for row in data:
        if not isinstance(row, list) or len(row) < 6:
            continue
        bar = _bar(row[0], row[1], row[2], row[3], row[4], row[5])
        if bar:
            bars.append(bar)
    return bars, "binance" if bars else "binance_empty"


def fetch_tv_quote(symbol: str) -> dict | None:
    fields = "close,change,change_percent,volume,high,low,price_52_week_high,price_52_week_low,description"
    candidates = [symbol]
    if ":" not in symbol:
        candidates.extend([f"NASDAQ:{symbol}", f"NYSE:{symbol}", f"AMEX:{symbol}", f"CBOE:{symbol}"])
    for ticker in candidates:
        qs = urllib.parse.urlencode({"symbol": ticker, "fields": fields})
        data = fetch_json(f"{TV_SCANNER}?{qs}")
        if not isinstance(data, dict):
            continue
        close = data.get("close")
        if close is None:
            continue
        return {
            "symbol": symbol.upper(),
            "price": fmt_price(close),
            "change": fmt_price(data.get("change")),
            "change_pct": fmt_pct(data.get("change_percent")),
            "volume": data.get("volume"),
            "52w_high": fmt_price(data.get("price_52_week_high")),
            "52w_low": fmt_price(data.get("price_52_week_low")),
            "short_name": data.get("description"),
            "data_source": "tradingview",
        }
    return None


def fetch_tv_search(query: str, count: int = 5) -> list[dict]:
    qs = urllib.parse.urlencode({"text": query, "hl": 1, "lang": "en", "domain": "production"})
    data = fetch_json(f"{TV_SEARCH}?{qs}")
    if not isinstance(data, list):
        return []
    out: list[dict] = []
    for row in data[:count]:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "symbol": row.get("symbol"),
                "name": row.get("description"),
                "exchange": row.get("exchange"),
                "type": row.get("type"),
            }
        )
    return out


def bars_to_quote(symbol: str, bars: list[dict], source: str) -> dict:
    last = bars[-1]
    prev = bars[-2] if len(bars) >= 2 else None
    price = last["close"]
    change = None
    change_pct = None
    if prev and prev.get("close"):
        change = price - float(prev["close"])
        change_pct = (change / float(prev["close"])) * 100
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]
    return {
        "symbol": symbol.upper(),
        "price": fmt_price(price),
        "change": fmt_price(change),
        "change_pct": fmt_pct(change_pct),
        "volume": last.get("volume"),
        "52w_high": fmt_price(max(highs) if highs else None),
        "52w_low": fmt_price(min(lows) if lows else None),
        "data_source": source,
    }


def live_ohlcv(symbol: str, *, timeframe: str, limit: int, vs: str = "USD") -> tuple[list[dict], str | None, list[str]]:
    tried: list[str] = []
    coin = crypto_coin(symbol)
    if coin is not None:
        hl_interval = {"1d": "1d", "1h": "1h", "1m": "1m"}.get(timeframe, "1d")
        bars, src = fetch_hl_ohlcv(coin, hl_interval, limit)
        tried.append("hyperliquid")
        if bars:
            return bars, src, tried
        bn_interval = {"1d": "1d", "1h": "1h", "1m": "1m"}.get(timeframe, "1d")
        bars, src = fetch_binance_ohlcv(coin, vs, bn_interval, limit)
        tried.append("binance")
        if bars:
            return bars, src, tried
        return [], None, tried
    bars, src = fetch_ib_ohlcv(symbol, timeframe, limit)
    tried.append("ibkr")
    if bars:
        return bars, src, tried
    return [], None, tried


def cmd_quote(symbols: list[str]) -> None:
    results = []
    for raw in symbols:
        sym = raw.upper().strip()
        bars, source, tried = live_ohlcv(sym, timeframe="1d", limit=30)
        if bars and source:
            results.append(bars_to_quote(sym, bars, source))
            continue
        tv = fetch_tv_quote(sym)
        tried.append("tradingview")
        if tv:
            results.append(tv)
            continue
        results.append(refuse(sym, detail="IB/TV/HL/Binance returned no live tape", tried=tried))
    print_json(results[0] if len(results) == 1 else results)


def cmd_search(query: str) -> None:
    matches = fetch_tv_search(query, count=5)
    if not matches:
        print_json(refuse(detail=f"TradingView search empty for {query!r}", tried=["tradingview"]))
        return
    print_json({"query": query, "matches": matches, "data_source": "tradingview"})


def cmd_history(symbol: str, range_: str = "1mo") -> None:
    valid = tuple(_RANGE_BARS)
    if range_ not in valid:
        print_json({"error": f"Invalid range '{range_}'. Valid: {', '.join(valid)}"})
        return
    sym = symbol.upper().strip()
    bars, source, tried = live_ohlcv(sym, timeframe="1d", limit=_RANGE_BARS[range_])
    if not bars or not source:
        print_json(refuse(sym, detail="no live OHLCV", tried=tried))
        return
    history = []
    for bar in bars:
        history.append(
            {
                "date": ts_to_date(bar["timestamp"]),
                "open": round(bar["open"], 2),
                "close": round(bar["close"], 2),
                "high": round(bar["high"], 2),
                "low": round(bar["low"], 2),
                "volume": bar.get("volume"),
            }
        )
    closes = [row["close"] for row in history if row["close"] is not None]
    stats: dict = {}
    if closes:
        stats["min"] = fmt_price(min(closes))
        stats["max"] = fmt_price(max(closes))
        stats["avg"] = fmt_price(sum(closes) / len(closes))
        if len(closes) >= 2 and closes[0]:
            stats["total_return_pct"] = fmt_pct(((closes[-1] - closes[0]) / closes[0]) * 100)
    print_json(
        {
            "symbol": sym,
            "range": range_,
            "data_points": len(history),
            "stats": stats,
            "history": history,
            "data_source": source,
        }
    )


def cmd_compare(symbols: list[str]) -> None:
    if len(symbols) < 2:
        print_json({"error": "compare requires at least 2 symbols"})
        return
    comparison = []
    for raw in symbols:
        sym = raw.upper().strip()
        bars, source, tried = live_ohlcv(sym, timeframe="1d", limit=30)
        if bars and source:
            quote = bars_to_quote(sym, bars, source)
        else:
            quote = fetch_tv_quote(sym)
            if quote is None:
                comparison.append(refuse(sym, tried=tried + ["tradingview"]))
                continue
        comparison.append(
            {
                "symbol": quote["symbol"],
                "price": quote.get("price"),
                "change_pct": quote.get("change_pct"),
                "52w_high": quote.get("52w_high"),
                "52w_low": quote.get("52w_low"),
                "data_source": quote.get("data_source"),
            }
        )
    print_json({"comparison": comparison, "symbols": [s.upper() for s in symbols]})


def cmd_crypto(symbol: str, vs: str = "USD") -> None:
    coin = crypto_coin(symbol) or symbol.upper().strip()
    bars, source, tried = live_ohlcv(coin, timeframe="1d", limit=5, vs=vs)
    if not bars or not source:
        print_json(refuse(coin, detail="crypto requires Hyperliquid or Binance", tried=tried))
        return
    quote = bars_to_quote(coin, bars, source)
    quote["quote_currency"] = vs.upper()
    print_json(quote)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stocks_client",
        description="Live stock & crypto quotes — IB / TradingView / Hyperliquid / Binance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  stocks_client.py quote AAPL MSFT
  stocks_client.py search Tesla
  stocks_client.py history AAPL --range 3mo
  stocks_client.py compare AAPL MSFT
  stocks_client.py crypto BTC
  BEJTRADER_URL=http://127.0.0.1:5001 stocks_client.py quote ES
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_quote = sub.add_parser("quote", help="Live quote (IB, TV, HL, or Binance)")
    p_quote.add_argument("symbols", nargs="+", metavar="SYMBOL")

    p_search = sub.add_parser("search", help="Ticker search via TradingView")
    p_search.add_argument("query")

    p_history = sub.add_parser("history", help="Daily OHLCV from an approved live source")
    p_history.add_argument("symbol", metavar="SYMBOL")
    p_history.add_argument("--range", dest="range_", default="1mo", choices=list(_RANGE_BARS))

    p_compare = sub.add_parser("compare", help="Side-by-side live quotes")
    p_compare.add_argument("symbols", nargs="+", metavar="SYMBOL")

    p_crypto = sub.add_parser("crypto", help="Crypto via Hyperliquid then Binance")
    p_crypto.add_argument("symbol", metavar="SYMBOL")
    p_crypto.add_argument("--vs", default="USD", metavar="CURRENCY")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "quote":
            cmd_quote(args.symbols)
        elif args.command == "search":
            cmd_search(args.query)
        elif args.command == "history":
            cmd_history(args.symbol, range_=args.range_)
        elif args.command == "compare":
            cmd_compare(args.symbols)
        elif args.command == "crypto":
            cmd_crypto(args.symbol, vs=args.vs)
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print_json({"error": "Interrupted by user"})
        sys.exit(130)
    except Exception as exc:
        print_json({"error": f"Unexpected error: {exc}", "type": type(exc).__name__})
        sys.exit(1)


if __name__ == "__main__":
    main()
