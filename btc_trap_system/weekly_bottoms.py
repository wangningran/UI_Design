"""Weekly K-line anatomy around prior cycle lows vs now."""
import pandas as pd, numpy as np
from engine import load, rsi
d = load("BTC")
w = d.resample("W-SUN").agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna()
c = w.close
w["rsi"] = rsi(c)
m = c.ewm(span=12).mean() - c.ewm(span=26).mean(); w["macd"] = m; w["mh"] = m - m.ewm(span=9).mean()
w["wma200"] = c.rolling(200, min_periods=150).mean(); w["wma50"] = c.rolling(50).mean(); w["wma20"] = c.rolling(20).mean()
sd = c.rolling(20).std(); w["pb"] = (c - (w.wma20 - 2 * sd)) / (4 * sd)
w["red"] = (w.close < w.open).astype(int)
w["vol_r"] = w.volume / w.volume.rolling(20).mean()
rng = w.high - w.low
w["lwick"] = (np.minimum(w.open, w.close) - w.low) / rng
w["body"] = (w.close - w.open) / w.open
def streak(s):
    out, n = [], 0
    for v in s: n = n + 1 if v else 0; out.append(n)
    return pd.Series(out, index=s.index)
w["red_streak"] = streak(w.red)
w["ll_streak"] = streak(w.low < w.low.shift(1))  # consecutive lower lows
events = {"2015-01 底": "2015-01-14", "2018-12 底": "2018-12-15", "2020-03 新冠": "2020-03-13",
          "2022-06 夏季低点": "2022-06-18", "2022-11 底": "2022-11-21", "2026-07 夏季低点": "2026-07-01", "当前": str(w.index[-1].date())}
rows = {}
for name, dt in events.items():
    i = w.index.searchsorted(pd.Timestamp(dt)); i = min(i, len(w) - 1); r = w.iloc[i]
    win = w.iloc[max(0, i - 12):i + 1]
    # max red streak and lower-low streak within 12 weeks before the low
    peak = w.close.iloc[max(0, i - 52):i + 1].max()
    nxt = w.iloc[i + 1:i + 9]
    rows[name] = {
        "week": str(w.index[i].date()), "low": round(r.low),
        "最长连阴(前12周)": int(win.red_streak.max()), "低点周连阴数": int(r.red_streak),
        "连续更低低点": int(win.ll_streak.max()),
        "近12周阴线数": int(win.red.sum()),
        "周RSI": round(r.rsi, 1), "周RSI最低(前12周)": round(win.rsi.min(), 1),
        "MACD柱": round(r["mh"] / r.close * 100, 2),
        "距200WMA": None if np.isnan(r.wma200) else f"{r.close / r.wma200 - 1:+.0%}",
        "低点距200WMA": None if np.isnan(r.wma200) else f"{r.low / r.wma200 - 1:+.0%}",
        "距50WMA": f"{r.close / r.wma50 - 1:+.0%}",
        "布林%b": round(r.pb, 2),
        "量能/20周均量": round(r.vol_r, 2), "最大量能(前6周)": round(w.vol_r.iloc[max(0, i - 6):i + 1].max(), 2),
        "下影比例": round(r.lwick, 2), "实体": f"{r.body:+.1%}",
        "距52周高点": f"{r.close / peak - 1:+.0%}",
        "后8周最大涨幅": None if nxt.empty else f"{nxt.high.max() / r.low - 1:+.0%}",
        "后8周是否破低": None if nxt.empty else bool(nxt.low.min() < r.low),
    }
t = pd.DataFrame(rows); print(t.to_string())
# detail: 16 weeks into each final low
for name in ["2018-12 底", "2022-11 底", "当前"]:
    i = w.index.searchsorted(pd.Timestamp(events[name])); i = min(i, len(w) - 1)
    seg = w.iloc[i - 14:i + 5][["open", "close", "low", "red", "rsi", "mh", "vol_r", "lwick"]].copy()
    seg["chg"] = (seg.close / seg.open - 1).map("{:+.1%}".format)
    seg["mh"] = (seg.mh / seg.close * 100).round(2)
    print("\n", name); print(seg.round(2).to_string())
