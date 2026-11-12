"""全局配置：数据目录、资产清单、FRED 序列、回测参数。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("FOMC_DATA_DIR", PROJECT_ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
REPORT_DIR = Path(os.environ.get("FOMC_REPORT_DIR", PROJECT_ROOT / "reports"))

START_YEAR = 2000

# None = 使用 requests 默认 UA。FRED 会挂起带浏览器风格自定义 UA 的请求，默认 UA 则稳定可用。
USER_AGENT: str | None = None


@dataclass(frozen=True)
class Asset:
    key: str          # 内部名
    label: str        # 展示名
    source: str       # "fred" 或 "yahoo"
    symbol: str       # FRED 序列 ID 或 Yahoo 代码
    kind: str         # "yield"：目标为变动(bp)；"price"：目标为对数收益率(%)
    note: str = ""
    # Yahoo 上部分品种的日线收盘早于 14:00 ET 的声明发布，会议反应落在下一根 bar。
    # reaction_lag=1：会议反应 = prev -> t0+1，预测起点也从 t0+1 收盘开始，避免未来函数。
    reaction_lag: int = 0


ASSETS: list[Asset] = [
    Asset("ust2y", "美债 2Y 收益率", "fred", "DGS2", "yield"),
    Asset("ust10y", "美债 10Y 收益率", "fred", "DGS10", "yield"),
    Asset("spx", "标普 500", "yahoo", "^GSPC", "price"),
    Asset("ndx", "纳斯达克 100", "yahoo", "^NDX", "price"),
    Asset("dxy", "美元指数", "yahoo", "DX-Y.NYB", "price", "Yahoo 日线收盘早于声明，按 T+1 对齐", reaction_lag=1),
    Asset("eurusd", "EUR/USD", "yahoo", "EURUSD=X", "price", "2003 年后才有数据；按 T+1 对齐", reaction_lag=1),
    Asset("usdjpy", "USD/JPY", "yahoo", "JPY=X", "price", "按 T+1 对齐", reaction_lag=1),
    Asset("gold", "黄金期货", "yahoo", "GC=F", "price", "按 T+1 对齐", reaction_lag=1),
    Asset("btc", "比特币", "yahoo", "BTC-USD", "price", "2014 年后才有数据，样本少"),
]

ASSET_BY_KEY = {a.key: a for a in ASSETS}

# 特征/状态用的 FRED 序列
FRED_SERIES = {
    "DGS2": "2Y 国债收益率",
    "DGS10": "10Y 国债收益率",
    "DFEDTAR": "联邦基金目标利率 (至 2008-12-15)",
    "DFEDTARU": "联邦基金目标区间上限 (2008-12-16 起)",
    "VIXCLS": "VIX",
    "T10Y2Y": "10Y-2Y 期限利差",
    "BAA10Y": "穆迪 Baa 公司债 - 10Y 利差",
    "UMCSENT": "密歇根消费者信心",
}

HORIZONS = (1, 3, 5)

# 回测参数
MIN_TRAIN_EVENTS = 40      # 至少积累这么多次会议才开始样本外预测
RIDGE_LAMBDA = 5.0         # 岭回归惩罚，样本少时偏大一点更稳

# 模型使用的特征（每个资产额外加上自己的会议日反应 own_ret_t0）
MODEL_FEATURES = [
    "surprise_2y_bp",
    "decision_bp",
    "hd_score",
    "hd_delta",
    "vix_pctile",
    "curve_2s10s",
    "umcsent_dev",
]
