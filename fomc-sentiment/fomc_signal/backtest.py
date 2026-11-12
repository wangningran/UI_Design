"""滚动样本外 (walk-forward) 回测。

对每个资产 × 预测周期：
- 只用例会 (scheduled) 事件，紧急会议的市场环境太特殊，单列观察。
- 第 i 次会议的预测只用 "目标已经实现" 的历史会议训练：要求训练样本的目标结束日 < 第 i 次会议的 t0。
- 每一步用训练集的均值/标准差做标准化，然后岭回归；预测值的符号就是多空方向。
- 评价：方向胜率 (含二项检验 z 值)、IC (预测值与实际值的秩相关)、按信号方向持仓的平均收益，
  并和"永远做多"基准对比。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import ASSETS, HORIZONS, MIN_TRAIN_EVENTS, MODEL_FEATURES, RIDGE_LAMBDA


def feature_list(asset_key: str, base: list[str] | None = None) -> list[str]:
    return list(base or MODEL_FEATURES) + [f"{asset_key}_ret_t0"]


def ridge_fit(X: np.ndarray, y: np.ndarray, lam: float) -> tuple[np.ndarray, float, np.ndarray, np.ndarray]:
    """返回 (beta, intercept, mu, sd)；截距不惩罚。"""
    mu = np.nanmean(X, axis=0)
    sd = np.nanstd(X, axis=0)
    sd[~np.isfinite(sd) | (sd == 0)] = 1.0
    Z = np.nan_to_num((X - mu) / sd)  # 缺失值填为训练均值 (=0)
    y_mean = float(y.mean())
    k = Z.shape[1]
    beta = np.linalg.solve(Z.T @ Z + lam * np.eye(k), Z.T @ (y - y_mean))
    return beta, y_mean, mu, sd


def ridge_predict(model, X: np.ndarray) -> np.ndarray:
    beta, intercept, mu, sd = model
    Z = np.nan_to_num((X - mu) / sd)
    return intercept + Z @ beta


def _prepare(events: pd.DataFrame, asset_key: str, horizon: int, features: list[str]) -> pd.DataFrame:
    target, end = f"{asset_key}_fwd{horizon}", f"{asset_key}_end{horizon}"
    df = events[events["scheduled"]].copy()
    df = df[df[target].notna() & df[f"{asset_key}_ret_t0"].notna()]
    df = df.sort_values("t0").reset_index(drop=True)
    df["_y"] = df[target]
    df["_end"] = pd.to_datetime(df[end])
    return df[["t0", "release_date", "_y", "_end"] + features]


def walk_forward(events: pd.DataFrame, asset_key: str, horizon: int,
                 features: list[str] | None = None, min_train: int = MIN_TRAIN_EVENTS,
                 lam: float = RIDGE_LAMBDA) -> pd.DataFrame:
    features = features or feature_list(asset_key)
    df = _prepare(events, asset_key, horizon, features)
    preds = []
    for i in range(len(df)):
        train = df.iloc[:i]
        train = train[train["_end"] < df.at[i, "t0"]]   # 只用已经实现的目标
        if len(train) < min_train:
            continue
        model = ridge_fit(train[features].to_numpy(float), train["_y"].to_numpy(float), lam)
        pred = float(ridge_predict(model, df.loc[[i], features].to_numpy(float))[0])
        preds.append({"t0": df.at[i, "t0"], "pred": pred, "actual": df.at[i, "_y"],
                      "n_train": len(train)})
    return pd.DataFrame(preds)


def _spearman(a: pd.Series, b: pd.Series) -> float:
    if len(a) < 3:
        return np.nan
    return float(np.corrcoef(a.rank(), b.rank())[0, 1])


@dataclass
class Metrics:
    n: int
    hit_rate: float
    hit_z: float
    ic: float
    signal_mean: float       # 按信号方向持仓的平均收益/变动
    signal_t: float
    long_mean: float         # 永远做多 (或永远看涨收益率)
    long_hit: float

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def evaluate(preds: pd.DataFrame) -> Metrics:
    p = preds[preds["actual"] != 0]
    n = len(p)
    if n == 0:
        return Metrics(0, *[np.nan] * 7)
    hits = (np.sign(p["pred"]) == np.sign(p["actual"])).sum()
    hit_rate = hits / n
    signed = np.sign(p["pred"]) * p["actual"]
    sd = signed.std(ddof=1)
    return Metrics(
        n=n,
        hit_rate=hit_rate,
        hit_z=(hits - n / 2) / np.sqrt(n / 4),
        ic=_spearman(p["pred"], p["actual"]),
        signal_mean=float(signed.mean()),
        signal_t=float(signed.mean() / (sd / np.sqrt(n))) if sd > 0 else np.nan,
        long_mean=float(p["actual"].mean()),
        long_hit=float((p["actual"] > 0).mean()),
    )


def run_all(events: pd.DataFrame, horizons=HORIZONS) -> tuple[pd.DataFrame, dict]:
    rows, all_preds = [], {}
    for asset in ASSETS:
        if f"{asset.key}_ret_t0" not in events:
            continue
        for h in horizons:
            preds = walk_forward(events, asset.key, h)
            all_preds[(asset.key, h)] = preds
            m = evaluate(preds) if len(preds) else Metrics(0, *[np.nan] * 7)
            rows.append({"asset": asset.key, "label": asset.label, "kind": asset.kind,
                         "horizon": h, **m.as_dict(),
                         "oos_start": preds["t0"].min() if len(preds) else pd.NaT})
    return pd.DataFrame(rows), all_preds


def univariate_ic(events: pd.DataFrame, horizon: int, features: list[str] | None = None) -> pd.DataFrame:
    """全样本单因子秩相关（样本内、仅作描述，不能当成可交易结果）。"""
    features = features or MODEL_FEATURES + ["own_ret_t0", "text_change", "dissent_net", "vix_pre", "baa_spread"]
    df = events[events["scheduled"]]
    out = {}
    for asset in ASSETS:
        y = df.get(f"{asset.key}_fwd{horizon}")
        if y is None:
            continue
        col = {}
        for f in features:
            x = df[f"{asset.key}_ret_t0"] if f == "own_ret_t0" else df.get(f)
            if x is None:
                continue
            ok = x.notna() & y.notna()
            col[f] = _spearman(x[ok], y[ok]) if ok.sum() > 20 else np.nan
        out[asset.key] = col
    return pd.DataFrame(out)


def latest_signals(events: pd.DataFrame, metrics: pd.DataFrame, horizons=HORIZONS) -> pd.DataFrame:
    """对最近一次声明给出信号：用所有目标已实现的历史例会训练。"""
    latest = events.sort_values("t0").iloc[-1]
    rows = []
    for asset in ASSETS:
        feats = feature_list(asset.key)
        if any(f not in events for f in feats) or pd.isna(latest[f"{asset.key}_ret_t0"]):
            continue
        for h in horizons:
            df = _prepare(events, asset.key, h, feats)
            train = df[df["_end"] < latest["t0"]]
            if len(train) < MIN_TRAIN_EVENTS:
                continue
            model = ridge_fit(train[feats].to_numpy(float), train["_y"].to_numpy(float), RIDGE_LAMBDA)
            x = latest[feats].to_numpy(float).reshape(1, -1)
            pred = float(ridge_predict(model, x)[0])
            # 各特征对预测值的贡献（标准化后 × 系数）
            beta, _, mu, sd = model
            contrib = np.nan_to_num((x[0] - mu) / sd) * beta
            top = sorted(zip(feats, contrib), key=lambda kv: -abs(kv[1]))[:3]
            m = metrics[(metrics.asset == asset.key) & (metrics.horizon == h)].iloc[0]
            rows.append({"asset": asset.key, "label": asset.label, "kind": asset.kind, "horizon": h,
                         "pred": pred, "direction": int(np.sign(pred)),
                         "oos_hit": m.hit_rate, "oos_z": m.hit_z, "oos_ic": m.ic, "oos_n": m.n,
                         "confidence": confidence_label(m.hit_z, m.ic),
                         "drivers": ", ".join(f"{f}({c:+.2f})" for f, c in top)})
    return pd.DataFrame(rows)


def confidence_label(z: float, ic: float) -> str:
    if not np.isfinite(z) or not np.isfinite(ic):
        return "无"
    if z >= 2 and ic > 0.1:
        return "高"
    if z >= 1 and ic > 0:
        return "中"
    return "低"
