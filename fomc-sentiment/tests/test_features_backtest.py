import numpy as np
import pandas as pd

from fomc_signal import backtest as bt
from fomc_signal.features import _asset_moves, build_events


def _bdays(start="2020-01-01", periods=60):
    return pd.bdate_range(start, periods=periods)


def _fred(idx):
    flat = pd.Series(1.0, index=idx)
    return {
        "DGS2": pd.Series(np.linspace(1.0, 1.59, len(idx)), index=idx),
        "DGS10": flat * 2,
        "DFEDTAR": pd.Series(dtype=float, index=pd.DatetimeIndex([])),
        "DFEDTARU": pd.Series([1.5] * 18 + [1.25] * (len(idx) - 18), index=idx),
        "VIXCLS": flat * 20, "T10Y2Y": flat, "BAA10Y": flat * 2,
        "UMCSENT": pd.Series(80.0, index=pd.date_range("2015-01-01", periods=70, freq="MS")),
    }


def test_weekend_release_maps_to_next_trading_day():
    idx = _bdays()
    sunday = pd.Timestamp("2020-01-26")
    st = pd.DataFrame({"date": [sunday], "url": ["u"], "label": ["x (unscheduled)"],
                       "scheduled": [False], "text": ["The Committee decided to lower the target range."]})
    spx = pd.Series(np.arange(len(idx), dtype=float) + 100, index=idx)
    ev = build_events(st, _fred(idx), {"spx": spx})
    row = ev.iloc[0]
    assert row.t0 == pd.Timestamp("2020-01-27")          # 周日 -> 周一
    assert row.prev == pd.Timestamp("2020-01-24")
    assert row.decision_bp == -25.0                      # 1/27 (第 18 个交易日) 起降到 1.25
    assert np.isclose(row.surprise_2y_bp, 1.0)           # 每天 +1bp


def test_reaction_lag_shifts_reaction_and_target():
    idx = _bdays(periods=10)
    s = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109], index=idx, dtype=float)
    t0 = idx[3]
    no_lag = _asset_moves(s, t0, "price", "x", lag=0)
    lag = _asset_moves(s, t0, "price", "x", lag=1)
    assert np.isclose(no_lag["x_ret_t0"], np.log(103 / 102) * 100)
    assert np.isclose(lag["x_ret_t0"], np.log(104 / 102) * 100)      # 反应窗口包含 T+1
    assert np.isclose(lag["x_fwd1"], np.log(105 / 104) * 100)        # 预测从 T+1 收盘开始
    assert lag["x_end1"] == idx[5]


def _synthetic_events(n=120, seed=0):
    rng = np.random.default_rng(seed)
    t0 = pd.bdate_range("2000-01-03", periods=n, freq="30B")
    x = rng.normal(size=n)
    y = 2 * x + rng.normal(scale=0.5, size=n)
    ev = pd.DataFrame({"t0": t0, "release_date": t0, "scheduled": True,
                       "f": x, "spx_ret_t0": rng.normal(size=n), "spx_fwd1": y,
                       "spx_end1": t0 + pd.offsets.BDay(1)})
    return ev


def test_walk_forward_recovers_signal():
    ev = _synthetic_events()
    preds = bt.walk_forward(ev, "spx", 1, features=["f"], min_train=30)
    m = bt.evaluate(preds)
    assert m.n == 90
    assert m.hit_rate > 0.8 and m.ic > 0.8


def test_walk_forward_has_no_lookahead():
    ev = _synthetic_events()
    base = bt.walk_forward(ev, "spx", 1, features=["f"], min_train=30)
    tampered = ev.copy()
    tampered.loc[100:, "spx_fwd1"] *= -50        # 篡改未来的目标值
    after = bt.walk_forward(tampered, "spx", 1, features=["f"], min_train=30)
    cutoff = ev.t0.iloc[100]
    pd.testing.assert_series_equal(base[base.t0 <= cutoff].pred, after[after.t0 <= cutoff].pred)


def test_training_excludes_targets_not_yet_realised():
    ev = _synthetic_events(n=50)
    ev["spx_end1"] = ev["t0"] + pd.Timedelta(days=400)   # 目标很久之后才实现
    preds = bt.walk_forward(ev, "spx", 1, features=["f"], min_train=5)
    for p in preds.itertuples():
        realised = (ev.spx_end1 < p.t0).sum()
        assert p.n_train == realised
