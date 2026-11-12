"""AAII 散户情绪调查（可选）。

AAII 官网对自动下载返回 403，所以这里只读本地文件：
登录 AAII 后手动下载 sentiment.xls，放到 data/raw/aaii/sentiment.xls
（或导出成 CSV：至少要有 Date、Bullish、Bearish 三列）。
文件不存在时返回 None，模型自动跳过这个特征。
"""

from __future__ import annotations

import pandas as pd

from ..config import RAW_DIR

AAII_DIR = RAW_DIR / "aaii"


def load_bull_bear_spread() -> pd.Series | None:
    for name in ("sentiment.csv", "sentiment.xls", "sentiment.xlsx"):
        path = AAII_DIR / name
        if path.exists():
            return _parse(path)
    return None


def _parse(path) -> pd.Series:
    if path.suffix == ".csv":
        raw = pd.read_csv(path)
    else:
        raw = pd.read_excel(path, header=None)
        # xls 文件前几行是标题，找到含 "Bullish" 的表头行
        header_row = next(i for i, row in raw.iterrows()
                          if row.astype(str).str.contains("Bullish", case=False).any())
        raw.columns = [str(c).strip() for c in raw.iloc[header_row]]
        raw = raw.iloc[header_row + 1:]
    cols = {c.lower().strip(): c for c in raw.columns}
    date_col = next(cols[c] for c in cols if "date" in c)
    bull = pd.to_numeric(raw[cols["bullish"]], errors="coerce")
    bear = pd.to_numeric(raw[cols["bearish"]], errors="coerce")
    idx = pd.to_datetime(raw[date_col], errors="coerce")
    s = pd.Series((bull - bear).values, index=idx, name="aaii_bull_bear").dropna()
    s = s[s.index.notna()].sort_index()
    if s.abs().max() <= 1.0:  # 百分比可能是 0.35 这种小数
        s = s * 100
    return s
