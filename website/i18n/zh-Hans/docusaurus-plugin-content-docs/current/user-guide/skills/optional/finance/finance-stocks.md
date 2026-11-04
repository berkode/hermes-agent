---
title: "Stocks — 通过 IB、TradingView、Hyperliquid 或 Binance 获取实时报价"
sidebar_label: "Stocks"
description: "通过 IB、TradingView、Hyperliquid 或 Binance 获取实时报价"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Stocks

通过 IB、TradingView、Hyperliquid 或 Binance 获取实时报价。

## Skill 元数据

| | |
|---|---|
| 来源 | 可选 — 使用 `hermes skills install official/finance/stocks` 安装 |
| 路径 | `optional-skills/finance/stocks` |
| 版本 | `0.2.0` |
| 作者 | Mibay (Mibayy), Hermes Agent |
| 许可证 | MIT |
| 平台 | linux, macos, windows |
| 标签 | `Stocks`, `Finance`, `Market`, `Crypto`, `Investing` |
| 相关 skill | [`dcf-model`](/user-guide/skills/optional/finance/finance-dcf-model), [`comps-analysis`](/user-guide/skills/optional/finance/finance-comps-analysis), [`lbo-model`](/user-guide/skills/optional/finance/finance-lbo-model) |

## 参考：完整 SKILL.md

:::info
以下是 Hermes 在触发此 skill 时加载的完整 skill 定义。这是 agent 在 skill 激活时所看到的指令内容。
:::

# Stocks Skill

只读实时报价与日线。未批准的延迟行情不是数据源。股票通过 loopback 上的
BejTrader IB `/scan`；加密货币先 Hyperliquid 再 Binance；TradingView 用于
扫描与搜索。没有批准的实时源则拒绝。

## 使用场景

- 用户询问当前股票或加密货币价格
- 用户需要 OHLCV 历史或并排比较
- 用户希望通过名称查找代码（TradingView 搜索）

## 前置条件

仅需 Python 3 标准库。Oracle VM 上 BejTrader 需监听
`http://127.0.0.1:5001` 以提供 IB 股票/期货 K 线。仅在 loopback 上可用
`BEJTRADER_URL` 覆盖。加密货币不需要 IB。

## 运行方式

通过 `terminal` 工具调用。安装完成后：

```
SCRIPT=~/.hermes/skills/finance/stocks/scripts/stocks_client.py
python $SCRIPT quote AAPL
```

所有输出均为 stdout 上的 JSON。

## 快速参考

```
python $SCRIPT quote AAPL
python $SCRIPT quote AAPL MSFT
python $SCRIPT search Tesla
python $SCRIPT history NVDA --range 6mo
python $SCRIPT compare AAPL MSFT
python $SCRIPT crypto BTC
```

## 命令

### `quote SYMBOL [SYMBOL2 ...]`

最近一次实时收盘、涨跌、成交量。非加密货币先走 IB `/scan`，IB 不可用则
TradingView。加密货币走 Hyperliquid，然后 Binance。

### `search QUERY`

TradingView 代码搜索。返回前 5 条。

### `history SYMBOL [--range RANGE]`

每日 OHLCV。范围：`1mo`、`3mo`、`6mo`、`1y`、`5y`。默认：`1mo`。

### `compare SYMBOL1 SYMBOL2 [...]`

并排实时报价。

### `crypto SYMBOL`

Hyperliquid 公开 K 线，否则 Binance。传入 `BTC`。

## 注意事项

- loopback 上没有 IB 且 TV/HL/Binance 也失败时，输出
  `{"error": "no approved live source"}`——没有延迟兜底。
- `BEJTRADER_URL` 必须是 loopback（`127.0.0.1` / `localhost`）。公网主机被拒绝。
- 本 skill 为只读——不支持下单。

## 验证

```
python ~/.hermes/skills/finance/stocks/scripts/stocks_client.py quote AAPL
```

VM 上 BejTrader 可用时，JSON 含 `symbol`、`price` 以及 `ibkr` /
`tradingview` / `hyperliquid` / `binance` 的 `data_source`。没有实时行情时
`error` 为 `no approved live source`。
