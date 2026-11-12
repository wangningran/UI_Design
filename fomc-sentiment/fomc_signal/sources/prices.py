"""Yahoo Finance 日线收盘价 (yfinance)。"""

from __future__ import annotations

import pandas as pd

from ..config import RAW_DIR, START_YEAR


def load_close(symbol: str, *, refresh: bool = False) -> pd.Series:
    """日线收盘价。去掉今天的 bar（盘中时还不是收盘价）。"""
    s = _load_close(symbol, refresh=refresh)
    return s[s.index < pd.Timestamp.today().normalize()]


def _load_close(symbol: str, *, refresh: bool = False) -> pd.Series:
    safe = symbol.replace("^", "_").replace("=", "_").replace("/", "_")
    cache = RAW_DIR / "yahoo" / f"{safe}.csv"
    if cache.exists() and not refresh:
        s = pd.read_csv(cache, index_col=0, parse_dates=True).iloc[:, 0]
        s.name = symbol
        return s.dropna()

    import yfinance as yf  # 延迟导入，测试时不需要

    df = yf.download(symbol, start=f"{START_YEAR - 1}-01-01", auto_adjust=True,
                     progress=False, threads=False)
    if df is None or df.empty:
        raise RuntimeError(f"Yahoo 没有返回数据: {symbol}")
    close = df["Close"]
    if isinstance(close, pd.DataFrame):  # 新版 yfinance 返回多级列
        close = close.iloc[:, 0]
    close = close.dropna()
    close.index = pd.to_datetime(close.index).tz_localize(None).normalize()
    close.name = symbol
    cache.parent.mkdir(parents=True, exist_ok=True)
    close.to_frame("close").to_csv(cache)
    return close
