"""Run every method on today's data and write results.json + charts."""
import json, pathlib, warnings
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from engine import build_features, label_events, load

warnings.filterwarnings("ignore")
OUT = pathlib.Path(__file__).parent / "out"; OUT.mkdir(exist_ok=True)
b = load("BTC"); f = build_features(); c = f.close
today = f.index[-1]; now = f.iloc[-1]
R = {"date": str(today.date()), "price": round(float(c.iloc[-1]), 0)}

# ---------------------------------------------------------------- A. snapshot + percentiles
snap_cols = ["dd_ath", "days_since_ath", "days_since_halving", "mayer", "p_200wma", "z_4y", "p_ma50", "p_ma200",
             "ma200_slope", "rsi_d", "rsi_w", "macd_w_hist", "roc30", "roc90", "vol30", "pos_55", "pos_365",
             "vol_z", "low_wick", "swing_score", "dxy_roc60", "us10y", "us10y_chg90", "us3m_chg90", "curve",
             "spx_p_ma200", "vix", "hyg_roc60", "oil_roc90", "corr_spx90", "macro_score", "ethbtc_roc90",
             "mstr_btc_roc90"]
R["snapshot"] = {k: {"value": round(float(now[k]), 4),
                     "pctile": round(float((f[k].dropna() < now[k]).mean() * 100), 1)} for k in snap_cols}
print(pd.DataFrame(R["snapshot"]).T.to_string())

# ---------------------------------------------------------------- B. cycle analogs (aligned by ATH)
cyc = {"2013-17 (ATH 2013-11-30)": "2013-11-30", "2017-21 (ATH 2017-12-17)": "2017-12-17",
       "2021-25 (ATH 2021-11-09)": "2021-11-09", "current (ATH 2025-10-06)": "2025-10-06"}
ath_paths, analog = {}, {}
dsa = int(now.days_since_ath)
for name, d in cyc.items():
    d = pd.Timestamp(d)
    base = c.asof(d) if d >= c.index[0] else {"2013-11-30": 1132.0}[str(d.date())]
    p = c[c.index >= d] / base
    p.index = (p.index - d).days
    ath_paths[name] = p[p.index <= 1100]
    if "current" not in name:
        seg = p[p.index <= 1100]
        bottom_day = int(seg.idxmin()); bottom_dd = float(seg.min() - 1)
        at_now = float(p.asof(dsa)) if dsa in p.index or dsa > p.index.min() else np.nan
        analog[name] = {"bottom_day_after_ath": bottom_day, "bottom_dd": round(bottom_dd, 3),
                        "dd_at_same_day": round(at_now - 1, 3) if not np.isnan(at_now) else None,
                        "ret_next_90d_from_same_day": round(float(p.asof(dsa + 90) / p.asof(dsa) - 1), 3)
                        if p.index.min() <= dsa else None,
                        "ret_next_365d_from_same_day": round(float(p.asof(dsa + 365) / p.asof(dsa) - 1), 3)
                        if p.index.min() <= dsa else None}
R["cycle_analogs"] = analog
print(json.dumps(analog, indent=1))

# ---------------------------------------------------------------- C. breakdown events & trap model
feat = ["dd_ath", "mayer", "p_200wma", "rsi_d", "rsi_w", "macd_w_hist", "roc30", "roc90", "vol30", "pos_365",
        "vol_z", "low_wick", "swing_score", "ma200_slope", "macro_score", "dxy_roc60", "us10y_chg90",
        "spx_p_ma200", "vix", "hyg_roc60", "days_since_halving"]
ev = label_events(f, b, "down").join(f[feat])
evu = label_events(f, b, "up").join(f[feat])
lab = ev.dropna(subset=["trap"] + feat)
R["breakdown_events"] = {"n": int(len(lab)), "base_bear_trap_rate": round(float(lab.trap.mean()), 3),
                         "median_r30": round(float(lab.r30.median()), 3), "median_r90": round(float(lab.r90.median()), 3)}
labu = evu.dropna(subset=["trap"] + feat)
R["breakout_events"] = {"n": int(len(labu)), "base_bull_trap_rate": round(float(labu.trap.mean()), 3)}
# conditional base rates
def cond(mask, name):
    s = lab[mask]
    return {"cond": name, "n": int(len(s)), "bear_trap_rate": round(float(s.trap.mean()), 3) if len(s) else None,
            "median_r90": round(float(s.r90.median()), 3) if len(s) else None}
R["conditional"] = [
    cond(lab.mayer < 1, "Mayer<1 (below 200DMA)"),
    cond(lab.ma200_slope < 0, "200DMA falling"),
    cond(lab.macro_score < 0, "macro headwind (score<0)"),
    cond((lab.ma200_slope < 0) & (lab.macro_score < 0), "200DMA falling AND macro headwind"),
    cond(lab.dd_ath < -0.4, "already >40% below ATH"),
    cond((lab.dd_ath < -0.4) & (lab.macro_score < 0), ">40% below ATH AND macro headwind"),
    cond(lab.rsi_d < 30, "daily RSI<30 at breakdown"),
    cond(lab.vol_z > 1, "volume spike (z>1)"),
    cond(lab.swing_score < 0, "weekly swing structure bearish"),
    cond(lab.ma200_slope > 0, "200DMA rising (bull-market dips)"),
]
for r in R["conditional"]: print(r)

# walk-forward: train on events before each test year, predict that year
probs = []
for yr in range(2018, today.year + 1):
    tr = lab[lab.index.year < yr]; te = ev[(ev.index.year == yr)].dropna(subset=feat)
    if len(tr) < 12 or tr.trap.nunique() < 2 or te.empty: continue
    lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=2000)).fit(tr[feat], tr.trap)
    gb = GradientBoostingClassifier(n_estimators=150, max_depth=2, learning_rate=0.05, subsample=0.8,
                                    random_state=0).fit(tr[feat], tr.trap)
    p = 0.5 * lr.predict_proba(te[feat])[:, 1] + 0.5 * gb.predict_proba(te[feat])[:, 1]
    probs.append(pd.DataFrame({"p": p, "trap": te.trap, "r30": te.r30, "r90": te.r90}, index=te.index))
wf = pd.concat(probs)
wfl = wf.dropna(subset=["trap"])
acc = float(((wfl.p > 0.5) == (wfl.trap == 1)).mean())
brier = float(((wfl.p - wfl.trap) ** 2).mean())
R["walk_forward"] = {"n_test": int(len(wfl)), "accuracy": round(acc, 3), "brier": round(brier, 3),
                     "base_rate_accuracy": round(float(max(wfl.trap.mean(), 1 - wfl.trap.mean())), 3),
                     "hi_conf_trap_hit": round(float(wfl[wfl.p > 0.6].trap.mean()), 3) if (wfl.p > 0.6).any() else None,
                     "lo_conf_trap_hit": round(float(wfl[wfl.p < 0.4].trap.mean()), 3) if (wfl.p < 0.4).any() else None,
                     "n_hi": int((wfl.p > 0.6).sum()), "n_lo": int((wfl.p < 0.4).sum())}
# final model on everything, score today (today is itself a breakdown day if brk_dn55==1)
lr = make_pipeline(StandardScaler(), LogisticRegression(C=0.3, max_iter=2000)).fit(lab[feat], lab.trap)
gb = GradientBoostingClassifier(n_estimators=150, max_depth=2, learning_rate=0.05, subsample=0.8,
                                random_state=0).fit(lab[feat], lab.trap)
x = f[feat].iloc[[-1]]
p_today = 0.5 * lr.predict_proba(x)[0, 1] + 0.5 * gb.predict_proba(x)[0, 1]
coef = pd.Series(lr[-1].coef_[0], index=feat)
contrib = (coef * lr[0].transform(x)[0]).sort_values()
R["today_breakdown_flag"] = int(now.brk_dn55)
R["low_55d"] = round(float(b.low.iloc[-56:-1].min()), 0)
R["p_bear_trap_today"] = round(float(p_today), 3)
R["trap_drivers"] = {k: round(float(v), 3) for k, v in contrib.items()}
R["gb_importance"] = {k: round(float(v), 3) for k, v in
                      pd.Series(gb.feature_importances_, index=feat).sort_values(ascending=False).head(8).items()}
print("walk-forward", R["walk_forward"], "P(bear trap) today", p_today)
print(contrib)

# was the Aug-Sep breakout a bull trap?
R["recent_breakouts"] = [{"date": str(d.date()), "trap": None if np.isnan(r.trap) else int(r.trap),
                          "r30": None if np.isnan(r.r30) else round(r.r30, 3)} for d, r in evu[evu.index > "2025-06-01"].iterrows()]
R["recent_breakdowns"] = [{"date": str(d.date()), "trap": None if np.isnan(r.trap) else int(r.trap),
                           "r30": None if np.isnan(r.r30) else round(r.r30, 3)} for d, r in ev[ev.index > "2025-06-01"].iterrows()]
print(R["recent_breakouts"], R["recent_breakdowns"])

# ---------------------------------------------------------------- D. kNN state analog
kcols = ["dd_ath", "mayer", "p_200wma", "rsi_w", "macd_w_hist", "roc90", "ma200_slope", "pos_365", "macro_score",
         "days_since_halving"]
hist = f[kcols].dropna().iloc[:-180]
fwd = pd.DataFrame({h: c.shift(-h) / c - 1 for h in (30, 90, 180)}).reindex(hist.index)
mu, sd = hist.mean(), hist.std()
dist = (((hist - mu) / sd - (f[kcols].iloc[-1] - mu) / sd) ** 2).sum(axis=1) ** 0.5
# take best day per 30-day block to avoid clustered duplicates
nn = dist.groupby(dist.index.to_period("M")).idxmin().map(dist).sort_values().head(15)
nn_idx = dist.groupby(dist.index.to_period("M")).idxmin().loc[nn.index]
R["knn"] = {"analog_dates": [str(d.date()) for d in nn_idx],
            **{f"median_r{h}": round(float(fwd.loc[nn_idx, h].median()), 3) for h in (30, 90, 180)},
            **{f"p_up_{h}": round(float((fwd.loc[nn_idx, h] > 0).mean()), 3) for h in (30, 90, 180)},
            "q10_r90": round(float(fwd.loc[nn_idx, 90].quantile(.1)), 3),
            "q90_r90": round(float(fwd.loc[nn_idx, 90].quantile(.9)), 3)}
print("kNN", R["knn"])

# ---------------------------------------------------------------- E. composite position score & backtest
def zs(s):
    return ((s - s.expanding(365).mean()) / s.expanding(365).std()).clip(-3, 3)
score = pd.DataFrame(index=f.index)
score["valuation"] = -(zs(np.log(f.mayer)) + zs(np.log(f.p_200wma)) + zs(f.z_4y)) / 3   # cheap = +
score["trend"] = (zs(f.p_ma200) + zs(f.ma200_slope) + zs(f.p_w20) + f.swing_score / 2) / 4
score["momentum"] = (zs(f.rsi_w) + zs(f.macd_w_hist) + zs(f.roc90)) / 3
score["cycle"] = np.where(f.days_since_ath.between(300, 450) & (f.dd_ath < -0.45), 1.0,
                          np.where(f.days_since_ath < 120, -0.5, 0)) + np.where(f.days_since_halving.between(350, 550), 0.5, 0)
score["macro"] = f.macro_score.clip(-3, 3)
W = {"valuation": .30, "trend": .25, "momentum": .15, "cycle": .15, "macro": .15}
score["total"] = sum(score[k] * w for k, w in W.items())
bt = score.join(pd.DataFrame({h: c.shift(-h) / c - 1 for h in (30, 90, 180, 365)})).dropna()
bt = bt[bt.index > "2016-01-01"]
bt["q"] = pd.qcut(bt.total, 5, labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"])
qt = bt.groupby("q")[[90, 180, 365]].median().round(3)
R["score_weights"] = W
R["score_now"] = {k: round(float(score[k].iloc[-1]), 3) for k in list(W) + ["total"]}
R["score_quintiles_median_fwd"] = {str(k): {str(h): float(v) for h, v in r.items()} for k, r in qt.iterrows()}
R["score_ic"] = {str(h): round(float(bt.total.corr(bt[h], method="spearman")), 3) for h in (30, 90, 180, 365)}
R["score_pctile_now"] = round(float((bt.total < score.total.iloc[-1]).mean() * 100), 1)
# score bucket containing today's value
lo, hi = score.total.iloc[-1] - 0.15, score.total.iloc[-1] + 0.15
near = bt[(bt.total > lo) & (bt.total < hi)]
R["score_near_now"] = {"n_days": int(len(near)), **{f"median_r{h}": round(float(near[h].median()), 3) for h in (90, 180, 365)},
                       **{f"p_up_{h}": round(float((near[h] > 0).mean()), 3) for h in (90, 180, 365)}}
print(qt, R["score_now"], R["score_ic"], R["score_near_now"])

# ---------------------------------------------------------------- F. regime-conditioned Monte Carlo
r = np.log(c).diff().dropna()
regime = ((f.mayer < 1) & (f.macro_score < 0)).shift(1).fillna(False)
pool = r[regime.reindex(r.index).fillna(False)].dropna()
rng = np.random.default_rng(7); H = 180; block = 10; N = 5000
paths = np.empty((N, H))
pv = pool.values
for i in range(N):
    seq = []
    while len(seq) < H:
        s = rng.integers(0, len(pv) - block); seq.extend(pv[s:s + block])
    paths[i] = np.cumsum(seq[:H])
px = c.iloc[-1] * np.exp(paths)
R["monte_carlo"] = {"pool_days": int(len(pool)), "regime": "price<200DMA & macro headwind",
                    **{f"d{d}": {f"p{q}": round(float(np.percentile(px[:, d - 1], q)), 0) for q in (10, 25, 50, 75, 90)}
                       for d in (30, 90, 180)},
                    "p_touch_60k_90d": round(float((px[:, :90].min(axis=1) < 60000).mean()), 3),
                    "p_touch_55k_180d": round(float((px.min(axis=1) < 55000).mean()), 3),
                    "p_reclaim_80k_90d": round(float((px[:, :90].max(axis=1) > 80000).mean()), 3)}
print(R["monte_carlo"])

# ---------------------------------------------------------------- G. key levels
wk = c.resample("W").last()
lv = {"200WMA": wk.rolling(200).mean().iloc[-1], "200DMA": c.rolling(200).mean().iloc[-1],
      "111DMA": c.rolling(111).mean().iloc[-1], "50DMA": c.rolling(50).mean().iloc[-1],
      "2026 low (Jun)": c["2026"].min(), "Sep-2026 high": c["2026-08":].max(),
      "Feb-2026 low": c["2026-02"].min(), "0.618 retr. 58.6k→86.6k": 86603 - 0.618 * (86603 - 58559),
      "0.786 retr.": 86603 - 0.786 * (86603 - 58559),
      "-60% from ATH": c.max() * 0.4, "-70% from ATH": c.max() * 0.3, "2021 ATH (69k)": 67567}
# volume profile (last 365d) high-volume nodes
y = b[b.index > today - pd.Timedelta(days=365)]
bins = np.linspace(y.low.min(), y.high.max(), 40)
vp = pd.Series(0.0, index=(bins[:-1] + bins[1:]) / 2)
for _, row in y.iterrows():
    m = (vp.index >= row.low) & (vp.index <= row.high)
    if m.any(): vp[m] += row.volume / m.sum()
top = vp.sort_values(ascending=False).head(4).index
for i, t in enumerate(sorted(top)): lv[f"vol-node {i+1}"] = t
R["levels"] = {k: round(float(v), 0) for k, v in sorted(lv.items(), key=lambda kv: -kv[1])}
print(R["levels"])

# ---------------------------------------------------------------- chart data for report
ch = {}
d3 = f[f.index > "2024-06-01"]
ch["price"] = {"dates": [str(d.date()) for d in d3.index], "close": d3.close.round(0).tolist(),
               "ma200": c.rolling(200).mean().reindex(d3.index).round(0).tolist(),
               "wma200": (c / f.p_200wma).reindex(d3.index).round(0).tolist(),
               "ma50": c.rolling(50).mean().reindex(d3.index).round(0).tolist()}
ch["cycles"] = {k: {"x": [int(i) for i in v.index[::3]], "y": [round(float(y), 4) for y in v.values[::3]]}
                for k, v in ath_paths.items()}
s2 = score[score.index > "2016-01-01"].dropna(subset=["total"])
s2 = s2.iloc[::-1].iloc[::3].iloc[::-1]  # every 3rd day, always keeping today
ch["score"] = {"dates": [str(d.date()) for d in s2.index], "total": s2.total.round(3).tolist(),
               "close": c.reindex(s2.index).round(0).tolist()}
ch["mc"] = {"days": list(range(1, H + 1)),
            **{f"p{q}": np.percentile(px, q, axis=0).round(0).tolist() for q in (10, 25, 50, 75, 90)}}
ch["macro"] = {"dates": [str(d.date()) for d in d3.index[::2]],
               **{k: f[k].reindex(d3.index).round(4).values[::2].tolist() for k in ["us10y", "macro_score", "corr_spx90"]},
               "dxy": load("DXY").close.reindex(d3.index).ffill().round(2).values[::2].tolist()}
(OUT / "results.json").write_text(json.dumps(R, indent=1, default=float))
(OUT / "charts.json").write_text(json.dumps(ch, default=float))
print("written")
