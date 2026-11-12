"""把会议、文本、市场数据对齐成一张"事件表"：每次 FOMC 声明一行。

时间约定（避免未来函数）：
- release_date：声明发布日（URL 里的日期，可能是周末，如 2020-03-15）。
- t0：发布日当天或之后的第一个美股交易日；prev：t0 之前的那个交易日。
  例会声明在 14:00 ET 发布，所以 t0 收盘价已经包含会议反应。
- 会议特征：只用到 t0 收盘为止的信息（声明文本、t0 当天的 2Y 变动等）。
- 会前状态：只用 prev 及更早的数据（月度数据还额外滞后，见 umcsent_dev）。
- 目标：t0 收盘 -> t0 之后第 h 个交易日收盘的变化。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import ASSETS, HORIZONS
from .hawkdove import score_text, text_change

UMCSENT_LAG_DAYS = 35   # 密歇根信心指数按月初日期标记，终值在月底发布，保守滞后 35 天


def combined_target_rate(dfedtar: pd.Series, dfedtaru: pd.Series) -> pd.Series:
    """2008-12-16 之前用单一目标利率，之后用目标区间上限。"""
    cut = pd.Timestamp("2008-12-16")
    return pd.concat([dfedtar[dfedtar.index < cut], dfedtaru[dfedtaru.index >= cut]]).sort_index()


def _asof(s: pd.Series, when: pd.Timestamp) -> float:
    sub = s[s.index <= when]
    return float(sub.iloc[-1]) if len(sub) else np.nan


def _exact(s: pd.Series, when: pd.Timestamp) -> float:
    return float(s.loc[when]) if when in s.index else np.nan


def _before(s: pd.Series, when: pd.Timestamp) -> float:
    sub = s[s.index < when]
    return float(sub.iloc[-1]) if len(sub) else np.nan


def _pctile(s: pd.Series, when: pd.Timestamp, window: int = 252) -> float:
    sub = s[s.index <= when].tail(window)
    if len(sub) < 20:
        return np.nan
    return float((sub <= sub.iloc[-1]).mean())


def build_events(statements: pd.DataFrame, fred: dict[str, pd.Series],
                 prices: dict[str, pd.Series], aaii: pd.Series | None = None,
                 calendar: pd.DatetimeIndex | None = None) -> pd.DataFrame:
    """
    statements: list_statements + load_statement_texts 的结果 (date, url, label, scheduled, text, dissent_*)
    fred:       FRED 序列 ID -> Series
    prices:     资产 key -> 收盘价/收益率 Series（收益率资产直接传 FRED 序列）
    calendar:   交易日历，默认用标普 500 的交易日
    """
    if calendar is None:
        calendar = prices["spx"].index if "spx" in prices else fred["DGS2"].index
    calendar = pd.DatetimeIndex(sorted(calendar))
    target = combined_target_rate(fred["DFEDTAR"], fred["DFEDTARU"])

    rows = []
    prev_text = None
    prev_score = np.nan
    for st in statements.sort_values("date").itertuples():
        release = pd.Timestamp(st.date)
        pos = calendar.searchsorted(release)
        if pos >= len(calendar) or pos == 0:
            continue
        t0, prev = calendar[pos], calendar[pos - 1]

        hd = score_text(st.text)
        decision = (_asof(target, release + pd.Timedelta(days=1))
                    - _asof(target, release - pd.Timedelta(days=1))) * 100

        hold = getattr(st, "dissent_hold", 0)
        hold_sign = -1 if decision > 0 else (1 if decision < 0 else 0)
        dissent_net = getattr(st, "dissent_hawk", 0) - getattr(st, "dissent_dove", 0) + hold_sign * hold

        row = {
            "release_date": release,
            "t0": t0,
            "prev": prev,
            "label": st.label,
            "scheduled": bool(st.scheduled),
            "decision_bp": round(decision, 1),
            "surprise_2y_bp": (_exact(fred["DGS2"], t0) - _before(fred["DGS2"], t0)) * 100,
            "d10y_bp": (_exact(fred["DGS10"], t0) - _before(fred["DGS10"], t0)) * 100,
            "hd_score": hd.score,
            "hd_net": hd.net,
            "hd_delta": hd.score - prev_score,
            "text_change": text_change(prev_text, st.text),
            "dissent_net": dissent_net,
            "hawk_terms": "; ".join(hd.top_hits("hawk", 4)),
            "dove_terms": "; ".join(hd.top_hits("dove", 4)),
            "vix_pre": _asof(fred["VIXCLS"], prev),
            "vix_pctile": _pctile(fred["VIXCLS"], prev),
            "curve_2s10s": _asof(fred["T10Y2Y"], prev),
            "baa_spread": _asof(fred["BAA10Y"], prev),
            "umcsent_dev": _umcsent_dev(fred["UMCSENT"], t0),
            "aaii_bull_bear": _asof(aaii, prev) if aaii is not None else np.nan,
        }
        for asset in ASSETS:
            s = prices.get(asset.key)
            if s is None:
                continue
            row.update(_asset_moves(s, t0, asset.kind, asset.key, asset.reaction_lag))
        rows.append(row)
        prev_text, prev_score = st.text, hd.score

    return pd.DataFrame(rows)


def _umcsent_dev(s: pd.Series, t0: pd.Timestamp) -> float:
    sub = s[s.index <= t0 - pd.Timedelta(days=UMCSENT_LAG_DAYS)]
    if len(sub) < 24:
        return np.nan
    return float(sub.iloc[-1] - sub.tail(60).mean())


def _asset_moves(s: pd.Series, t0: pd.Timestamp, kind: str, key: str, lag: int = 0) -> dict:
    """会议反应 (own_ret_t0) 和未来 h 日目标 fwd_h，以及目标结束日（用于防止训练集泄露）。

    lag>0 时（日线收盘早于声明发布的品种），"会后第一个收盘" 是 t0 之后第 lag 根 bar：
    会议反应 = prev -> t0+lag，预测目标从 t0+lag 收盘开始算。
    """
    s = s.dropna()
    out = {f"{key}_ret_t0": np.nan}
    for h in HORIZONS:
        out[f"{key}_fwd{h}"] = np.nan
        out[f"{key}_end{h}"] = pd.NaT
    if t0 not in s.index:
        return out
    pos = s.index.get_loc(t0)
    if pos == 0:
        return out

    def move(a: float, b: float) -> float:
        return (b - a) * 100 if kind == "yield" else np.log(b / a) * 100

    base = pos + lag
    if base >= len(s):
        return out
    out[f"{key}_ret_t0"] = move(s.iloc[pos - 1], s.iloc[base])
    for h in HORIZONS:
        if base + h < len(s):
            out[f"{key}_fwd{h}"] = move(s.iloc[base], s.iloc[base + h])
            out[f"{key}_end{h}"] = s.index[base + h]
    return out
