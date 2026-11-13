"""BTC trap / price-position engine.

Layers (each produces features that are only computed from data available at that date — no look-ahead):
  1. Cycle      : days since ATH, days since halving, drawdown from ATH, analog-cycle path
  2. Valuation  : Mayer multiple (P/200DMA), P/200WMA, z-score of log price vs 4y trend
  3. Trend      : MA stack, MA slopes, weekly 20/50 structure
  4. Momentum   : RSI(14) daily/weekly, MACD weekly, 30/90d rate of change
  5. K-line     : swing structure (HH/HL/LH/LL), breakdown/breakout of N-day range, candle wicks, volume spikes
  6. Macro      : DXY, US10Y, curve (10y-3m), SPX trend, VIX, HYG credit, gold, oil, USDJPY; BTC-SPX correlation
  7. Crypto-rel : ETH/BTC trend, MSTR/BTC (proxy for leverage/premium appetite)
"""
from __future__ import annotations
import pathlib
import numpy as np
import pandas as pd

DATA = pathlib.Path(__file__).parent / "data"
HALVINGS = pd.to_datetime(["2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20", "2028-04-15"])


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"{name}.csv", index_col=0, parse_dates=True)


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def build_features() -> pd.DataFrame:
    b = load("BTC")
    c, h, l, v = b.close, b.high, b.low, b.volume
    f = pd.DataFrame(index=b.index)
    f["close"] = c

    # 1. cycle -------------------------------------------------------------
    ath = c.cummax()
    f["dd_ath"] = c / ath - 1
    ath_date = c.expanding().apply(lambda x: x.argmax(), raw=True)
    f["days_since_ath"] = np.arange(len(c)) - ath_date.values
    last_h = pd.Series(HALVINGS, index=HALVINGS)
    f["days_since_halving"] = [(d - last_h[last_h <= d].iloc[-1]).days for d in c.index]
    f["max_dd_cycle"] = f["dd_ath"].groupby((f["dd_ath"] == 0).cumsum()).cummin()

    # 2. valuation ---------------------------------------------------------
    f["mayer"] = c / c.rolling(200).mean()
    wk = c.resample("W").last()
    wma200 = wk.rolling(200, min_periods=150).mean().reindex(c.index, method="ffill")
    f["p_200wma"] = c / wma200
    lc = np.log(c)
    f["z_4y"] = (lc - lc.rolling(1460, min_periods=700).mean()) / lc.rolling(1460, min_periods=700).std()

    # 3. trend -------------------------------------------------------------
    for n in (20, 50, 100, 200):
        f[f"p_ma{n}"] = c / c.rolling(n).mean() - 1
    f["ma50_slope"] = c.rolling(50).mean().pct_change(20)
    f["ma200_slope"] = c.rolling(200).mean().pct_change(30)
    f["golden"] = (c.rolling(50).mean() > c.rolling(200).mean()).astype(int)
    wk20 = wk.rolling(20).mean().reindex(c.index, method="ffill")
    f["p_w20"] = c / wk20 - 1

    # 4. momentum ----------------------------------------------------------
    f["rsi_d"] = rsi(c)
    f["rsi_w"] = rsi(wk).reindex(c.index, method="ffill")
    m = wk.ewm(span=12).mean() - wk.ewm(span=26).mean()
    f["macd_w_hist"] = ((m - m.ewm(span=9).mean()) / wk).reindex(c.index, method="ffill")
    for n in (7, 30, 90, 180):
        f[f"roc{n}"] = c.pct_change(n)
    f["vol30"] = np.log(c).diff().rolling(30).std() * np.sqrt(365)

    # 5. K-line structure ----------------------------------------------------
    f["pos_55"] = (c - l.rolling(55).min()) / (h.rolling(55).max() - l.rolling(55).min())
    f["pos_365"] = (c - l.rolling(365).min()) / (h.rolling(365).max() - l.rolling(365).min())
    f["brk_dn55"] = (c < l.shift(1).rolling(55).min()).astype(int)
    f["brk_up55"] = (c > h.shift(1).rolling(55).max()).astype(int)
    rng = (h - l).replace(0, np.nan)
    f["low_wick"] = ((np.minimum(b.open, c) - l) / rng).rolling(3).mean()
    f["up_wick"] = ((h - np.maximum(b.open, c)) / rng).rolling(3).mean()
    f["vol_z"] = (np.log(v) - np.log(v).rolling(90).mean()) / np.log(v).rolling(90).std()
    f["down_days_10"] = (c.diff() < 0).rolling(10).sum()
    # swing structure on weekly closes: compare last two confirmed swing highs / lows (5-week pivots)
    f["swing_score"] = swing_structure(wk).reindex(c.index, method="ffill")

    # 6. macro ---------------------------------------------------------------
    mac = {n: load(n).close.reindex(c.index).ffill() for n in
           ["DXY", "US10Y", "US3M", "SPX", "VIX", "HYG", "GOLD", "OIL", "USDJPY", "TLT"]}
    f["dxy_roc60"] = mac["DXY"].pct_change(60)
    f["dxy_p_ma200"] = mac["DXY"] / mac["DXY"].rolling(200).mean() - 1
    f["us10y"] = mac["US10Y"]
    f["us10y_chg90"] = mac["US10Y"].diff(90)
    f["curve"] = mac["US10Y"] - mac["US3M"]
    f["us3m_chg90"] = mac["US3M"].diff(90)  # policy-rate direction proxy
    f["spx_p_ma200"] = mac["SPX"] / mac["SPX"].rolling(200).mean() - 1
    f["spx_roc60"] = mac["SPX"].pct_change(60)
    f["vix"] = mac["VIX"]
    f["hyg_roc60"] = mac["HYG"].pct_change(60)
    f["gold_roc90"] = mac["GOLD"].pct_change(90)
    f["oil_roc90"] = mac["OIL"].pct_change(90)
    f["jpy_roc60"] = mac["USDJPY"].pct_change(60)
    r_btc, r_spx = np.log(c).diff(), np.log(mac["SPX"]).diff()
    f["corr_spx90"] = r_btc.rolling(90).corr(r_spx)
    # composite macro liquidity score (+ = supportive): weak dollar, falling yields, healthy credit, risk-on equities
    z = lambda s: (s - s.rolling(750, min_periods=250).mean()) / s.rolling(750, min_periods=250).std()
    f["macro_score"] = (-z(f["dxy_roc60"]) - z(f["us10y_chg90"]) - z(f["us3m_chg90"]) + z(f["hyg_roc60"])
                        + z(f["spx_p_ma200"]) - z(f["vix"])) / 6

    # 7. crypto-relative -----------------------------------------------------
    eth = load("ETH").close.reindex(c.index).ffill()
    f["ethbtc_roc90"] = (eth / c).pct_change(90)
    mstr = load("MSTR").close.reindex(c.index).ffill()
    f["mstr_btc_roc90"] = (mstr / c).pct_change(90)
    return f


def swing_structure(wk: pd.Series, k: int = 3) -> pd.Series:
    """+2 = HH & HL (uptrend), -2 = LH & LL (downtrend), mixed in between. Pivots confirmed k weeks later."""
    out = pd.Series(np.nan, index=wk.index)
    highs, lows = [], []
    vals = wk.values
    for i in range(2 * k, len(wk)):
        j = i - k  # candidate pivot confirmed now
        win = vals[j - k:j + k + 1]
        if vals[j] == win.max():
            highs.append(vals[j])
        if vals[j] == win.min():
            lows.append(vals[j])
        s = 0
        if len(highs) >= 2:
            s += 1 if highs[-1] > highs[-2] else -1
        if len(lows) >= 2:
            s += 1 if lows[-1] > lows[-2] else -1
        out.iloc[i] = s
    return out


# --------------------------------------------------------------------------------------------
# Trap labelling: an event is a 55-day range breakdown (or breakout). Look 60 days forward.
#   breakdown → BEAR TRAP  if price closes back above the broken level +5% before falling a further 10%
#             → CONTINUATION otherwise
#   breakout  → BULL TRAP  if price closes back below the broken level -5% before rising a further 10%
# --------------------------------------------------------------------------------------------
def label_events(f: pd.DataFrame, b: pd.DataFrame, side: str = "down", horizon: int = 60,
                 cool: int = 20) -> pd.DataFrame:
    c, h, l = b.close, b.high, b.low
    col = "brk_dn55" if side == "down" else "brk_up55"
    level = l.shift(1).rolling(55).min() if side == "down" else h.shift(1).rolling(55).max()
    rows, last = [], None
    for d in f.index[f[col] == 1]:
        if last is not None and (d - last).days < cool:
            continue
        last = d
        i = c.index.get_loc(d)
        fut = c.iloc[i + 1:i + 1 + horizon]
        if len(fut) < horizon:
            lab = np.nan
        else:
            lev = level.loc[d]
            if side == "down":
                rec = fut[fut > lev * 1.05].index.min()
                ext = fut[fut < c.loc[d] * 0.90].index.min()
            else:
                rec = fut[fut < lev * 0.95].index.min()
                ext = fut[fut > c.loc[d] * 1.10].index.min()
            if pd.isna(rec):
                lab = 0
            elif pd.isna(ext):
                lab = 1
            else:
                lab = int(rec < ext)
        r30 = c.iloc[i + 30] / c.iloc[i] - 1 if i + 30 < len(c) else np.nan
        r90 = c.iloc[i + 90] / c.iloc[i] - 1 if i + 90 < len(c) else np.nan
        rows.append({"date": d, "trap": lab, "r30": r30, "r90": r90})
    return pd.DataFrame(rows).set_index("date")
