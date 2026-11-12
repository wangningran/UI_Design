"""FRED 公开 CSV 接口（无需 API Key）。"""

from __future__ import annotations

import io

import pandas as pd

from ..config import RAW_DIR, START_YEAR
from ..http import get_text

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={start}"


def load_series(series_id: str, *, refresh: bool = False, start: str | None = None) -> pd.Series:
    """返回以日期为索引的 float Series，缺失值 ('.') 已去掉。"""
    start = start or f"{START_YEAR - 2}-01-01"
    cache = RAW_DIR / "fred" / f"{series_id}.csv"
    if cache.exists() and not refresh:
        text = cache.read_text()
    else:
        # 注意：不带 cosd 的全量请求在 FRED 上偶尔会被断开，所以总是带起始日期
        text = get_text(FRED_CSV.format(sid=series_id, start=start), refresh=True, suffix=".csv")
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(text)
    return parse_fred_csv(text, series_id)


def parse_fred_csv(text: str, series_id: str) -> pd.Series:
    df = pd.read_csv(io.StringIO(text))
    date_col = df.columns[0]
    s = pd.to_numeric(df[series_id], errors="coerce")
    s.index = pd.to_datetime(df[date_col])
    s.name = series_id
    return s.dropna().sort_index()
