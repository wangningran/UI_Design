# FOMC 会议情绪信号（MVP）

观察美联储议息会议（FOMC）：声明措辞的鹰鸽变化、会议日的利率意外、会前市场情绪，
据此对会后 1/3/5 个交易日的资产走向给出**可回测的量化信号**。

第一版只用免费数据和词典法，目的是先把"数据 → 事件表 → 样本外回测 → 信号"这条链路跑通，
并如实检验信号到底有没有用。最新一次回测结果见 [`docs/mvp_report_20261112.md`](docs/mvp_report_20261112.md)。

## 快速开始

```bash
cd fomc-sentiment
pip install -r requirements.txt

python -m fomc_signal report    # 下载数据（首次约 3 分钟，之后走缓存）-> 回测 -> reports/report_YYYYMMDD.md
python -m fomc_signal latest    # 最近一次会议的解读 + 信号（会后推送用）
python -m fomc_signal daily     # 每日快照：利率、VIX、距下次会议天数
python -m fomc_signal report --refresh   # 强制拉取最新数据（会后使用）

python -m pytest -q             # 离线单元测试，不需要联网
```

## 数据来源（全部免费）

| 数据 | 来源 | 用途 |
| --- | --- | --- |
| 2000 年至今的 FOMC 声明全文、会议日历 | federalreserve.gov | 鹰鸽打分、措辞变化、反对票 |
| 2Y/10Y 国债收益率、联邦基金目标利率 | FRED | 利率意外代理、利率决定、目标资产 |
| VIX、10Y-2Y 利差、Baa 信用利差、密歇根消费者信心 | FRED | 会前情绪/状态 |
| 标普 500、纳指 100、美元指数、EUR/USD、USD/JPY、黄金、BTC | Yahoo Finance | 目标资产 |
| AAII 散户情绪调查（可选） | 手动下载 | AAII 禁止自动下载；放到 `data/raw/aaii/sentiment.xls` 后自动纳入事件表 |

## 方法

**事件表**（`data/events.csv`，每次声明一行）

- `t0`：声明发布后的第一个美股交易日（周日的紧急降息会落到周一）；`prev`：前一个交易日。
- 会议特征：`decision_bp` 利率决定、`surprise_2y_bp` 会议日 2Y 变动（利率意外代理）、
  `hd_score` / `hd_delta` 鹰鸽分及其变化、`text_change` 措辞变化比例、`dissent_net` 净鹰派反对票。
- 会前状态（只用 `prev` 及以前的数据）：`vix_pctile`、`curve_2s10s`、`baa_spread`，
  `umcsent_dev`（月度数据额外滞后 35 天，避免用到还没发布的值）。
- 目标：会后第一个收盘 → 之后第 h 个交易日的变化（收益率用 bp，其他用对数收益率 %）。

**鹰鸽词典**（`fomc_signal/hawkdove.py`），规则事先写死，不从数据里学：

1. 政策措辞短语，权重 2，例如 `raise the target range`、`ongoing increases`（鹰）/`exceptionally low levels`、`extended period`（鸽）。
2. 主题 + 方向，权重 1：通胀/增长/就业类主题词，6 个词以内出现上升或下降类方向词就计一次；失业率的方向相反。

`hd_score = (鹰 - 鸽) / (鹰 + 鸽)`，范围 [-1, 1]。

**回测**（`fomc_signal/backtest.py`）

- 只用例会；滚动扩展窗口，先积累 40 次会议再开始预测。
- 每次只用"目标已经实现"的历史会议训练，用岭回归，标准化只用训练集的统计量。
- 评价指标：方向胜率及二项检验 z 值、IC（秩相关）、按信号持仓的平均收益，并和永远做多的基准对比。

### 收盘时间对齐

Yahoo 上美元指数、EUR/USD、USD/JPY、黄金的日线收盘早于 14:00 ET 的声明发布。
最初直接按 t0 对齐时，EUR/USD、USD/JPY、黄金的 1 日"胜率"达到 62%–69%，其实是把会议反应当成了预测。
现在这几个品种设置了 `reaction_lag=1`：会议反应 = prev → T+1，预测从 T+1 收盘开始，
`tests/test_features_backtest.py` 里有对应测试。

## 当前结论（2026-11-12）

在 2005–2026 年约 170 次样本外会议上，**27 个资产 × 周期组合里没有一个达到 z ≥ 2 且 IC > 0.1**。
基础版特征没有稳健的方向预测力。这是 MVP 要验证的核心问题，也给下一步改进提供了基准线。

## 目录

```
fomc-sentiment/
├── fomc_signal/
│   ├── config.py        # 资产清单、FRED 序列、回测参数
│   ├── http.py          # 下载 + 磁盘缓存 + 重试
│   ├── sources/         # fed.py（声明/日历）、fred.py、prices.py（Yahoo）、aaii.py
│   ├── hawkdove.py      # 鹰鸽词典
│   ├── features.py      # 事件表
│   ├── backtest.py      # 样本外回测、最新信号
│   ├── report.py        # Markdown 报告、日报
│   └── __main__.py      # 命令行
├── tests/               # 离线单元测试
├── docs/                # 回测报告存档
├── data/                # 缓存（git 忽略）
└── reports/             # 生成的报告（git 忽略）
```

## 下一步

1. 改进利率意外：用日内期货数据，或者用"市场隐含降息概率 vs 实际决定"。
2. 文本：换成 LLM/FinBERT，逐句对比上一篇声明；纳入发布会文字稿和会议纪要。
3. 会间更新：纳入 CPI、非农、官员讲话。
4. 推送：信号验证有效后接 Telegram/飞书，在会后和每天早上各推一次。
