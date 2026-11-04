"""Stocks optional-skill: approved live hosts only, no Yahoo tape."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO / "optional-skills" / "finance" / "stocks"
SCRIPT_PATH = SKILL_DIR / "scripts" / "stocks_client.py"
SKILL_MD = SKILL_DIR / "SKILL.md"


def load_module():
    spec = importlib.util.spec_from_file_location("stocks_skill_client", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_description_hardline() -> None:
    text = SKILL_MD.read_text(encoding="utf-8")
    line = next(row for row in text.splitlines() if row.startswith("description: "))
    desc = line.split(":", 1)[1].strip()
    assert len(desc) <= 60
    assert desc.endswith(".")


def test_module_constants_have_no_yahoo_hosts() -> None:
    mod = load_module()
    strings = [str(value) for value in vars(mod).values() if isinstance(value, str)]
    blob = " ".join(strings).lower()
    assert "yahoo" not in blob
    assert "query1.finance" not in blob
    assert "query2.finance" not in blob
    assert "yfinance" not in blob


def test_skill_docs_do_not_name_yahoo() -> None:
    text = SKILL_MD.read_text(encoding="utf-8").lower()
    assert "yahoo" not in text
    assert "yfinance" not in text
    assert "query1.finance" not in text


def test_url_gate_allows_approved_hosts_only() -> None:
    mod = load_module()
    assert mod.is_approved_live_url("http://127.0.0.1:5001/scan") is True
    assert mod.is_approved_live_url("https://api.hyperliquid.xyz/info") is True
    assert mod.is_approved_live_url("https://api.binance.com/api/v3/klines") is True
    assert mod.is_approved_live_url("https://scanner.tradingview.com/symbol") is True
    assert mod.is_approved_live_url("https://query1.finance.yahoo.com/v8/finance/chart/AAPL") is False
    assert mod.is_approved_live_url("https://query2.finance.yahoo.com/v8/finance/chart/AAPL") is False
    assert mod.is_approved_live_url("http://example.com/scan") is False
    assert mod.is_approved_live_url("https://bejtrader.example.com/scan") is False


def test_fetch_json_never_opens_yahoo(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = load_module()
    opened: list[str] = []

    def _open(req, timeout=15):  # noqa: ANN001
        opened.append(req.full_url)
        raise AssertionError("network should not run")

    monkeypatch.setattr(mod.urllib.request, "urlopen", _open)
    assert mod.fetch_json("https://query1.finance.yahoo.com/v8/finance/chart/AAPL") is None
    assert opened == []


def test_quote_uses_loopback_ib_then_refuses(capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = load_module()
    seen: list[str] = []

    def fake_fetch(url: str, payload=None, retries: int = 3):  # noqa: ANN001
        seen.append(url)
        return None

    monkeypatch.setattr(mod, "fetch_json", fake_fetch)
    mod.cmd_quote(["AAPL"])
    out = json.loads(capsys.readouterr().out)
    assert out["error"] == "no approved live source"
    assert seen
    assert all("yahoo" not in url.lower() for url in seen)
    assert any("127.0.0.1:5001/scan" in url for url in seen)
    assert any("scanner.tradingview.com" in url for url in seen)


def test_crypto_uses_hyperliquid_then_binance(capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = load_module()
    seen: list[str] = []

    def fake_fetch(url: str, payload=None, retries: int = 3):  # noqa: ANN001
        seen.append(url)
        if "hyperliquid" in url:
            return [
                {"t": 1_700_000_000_000, "o": 100, "h": 110, "l": 90, "c": 105, "v": 1},
                {"t": 1_700_086_400_000, "o": 105, "h": 120, "l": 100, "c": 118, "v": 2},
            ]
        raise AssertionError(f"unexpected url {url}")

    monkeypatch.setattr(mod, "fetch_json", fake_fetch)
    mod.cmd_crypto("BTC")
    out = json.loads(capsys.readouterr().out)
    assert out["symbol"] == "BTC"
    assert out["data_source"] == "hyperliquid"
    assert out["price"] == "118.00"
    assert seen == ["https://api.hyperliquid.xyz/info"]
