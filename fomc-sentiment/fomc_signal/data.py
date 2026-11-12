"""一次性加载全部数据（带缓存），供 CLI 和报告使用。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import ASSETS, FRED_SERIES, RAW_DIR, START_YEAR
from .features import build_events
from .sources import aaii, fed, fred, prices


@dataclass
class Dataset:
    statements: pd.DataFrame
    fred: dict[str, pd.Series]
    prices: dict[str, pd.Series]
    aaii: pd.Series | None
    events: pd.DataFrame


def load_all(*, refresh: bool = False, start_year: int = START_YEAR, log=print) -> Dataset:
    log("· 美联储：会议列表与声明全文")
    statements = fed.load_statement_texts(fed.list_statements(start_year=start_year, refresh=refresh),
                                          refresh=False)
    log(f"  {len(statements)} 篇声明（例会 {int(statements.scheduled.sum())} 次）")

    log("· FRED 序列")
    fred_data = {sid: fred.load_series(sid, refresh=refresh) for sid in FRED_SERIES}

    log("· 资产价格")
    price_data: dict[str, pd.Series] = {}
    for asset in ASSETS:
        try:
            if asset.source == "fred":
                series = fred_data.get(asset.symbol)
                price_data[asset.key] = series if series is not None else fred.load_series(asset.symbol, refresh=refresh)
            else:
                price_data[asset.key] = prices.load_close(asset.symbol, refresh=refresh)
        except Exception as err:  # 某个资产下载失败不影响其他资产
            log(f"  ! {asset.label} ({asset.symbol}) 获取失败：{err}")

    sentiment = aaii.load_bull_bear_spread()
    log("· AAII 散户情绪：" + ("已加载" if sentiment is not None else
                              f"未找到本地文件（可选，放到 {aaii.AAII_DIR}/sentiment.xls）"))

    events = build_events(statements, fred_data, price_data, sentiment)
    out = RAW_DIR.parent / "events.csv"
    events.to_csv(out, index=False)
    log(f"· 事件表 {len(events)} 行 -> {out}")
    return Dataset(statements, fred_data, price_data, sentiment, events)
