"""生成 Markdown 回测报告 + 最新会议信号 + 日报快照。"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from .config import ASSET_BY_KEY, ASSETS, HORIZONS, MIN_TRAIN_EVENTS, MODEL_FEATURES, RIDGE_LAMBDA

FEATURE_CN = {
    "surprise_2y_bp": "会议日 2Y 变动 (bp，利率意外代理)",
    "decision_bp": "利率决定 (bp)",
    "hd_score": "声明鹰鸽分 [-1,1]",
    "hd_delta": "鹰鸽分较上次变化",
    "vix_pctile": "会前 VIX 一年分位",
    "curve_2s10s": "会前 10Y-2Y 利差",
    "umcsent_dev": "密歇根信心偏离 5 年均值",
    "own_ret_t0": "该资产会议反应",
    "text_change": "措辞变化比例",
    "dissent_net": "净鹰派反对票",
    "vix_pre": "会前 VIX",
    "baa_spread": "会前 Baa 信用利差",
}


def md_table(df: pd.DataFrame, floatfmt: str = "{:.2f}") -> str:
    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "—" if not np.isfinite(v) else floatfmt.format(v)
        if isinstance(v, pd.Timestamp):
            return v.strftime("%Y-%m-%d")
        return str(v)
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt(row[c]) for c in cols) + " |")
    return "\n".join(lines)


def _unit(kind: str) -> str:
    return "bp" if kind == "yield" else "%"


def _direction_word(kind: str, d: int) -> str:
    if kind == "yield":
        return "收益率↑" if d > 0 else ("收益率↓" if d < 0 else "中性")
    return "看多" if d > 0 else ("看空" if d < 0 else "中性")


def latest_meeting_section(events: pd.DataFrame) -> str:
    e = events.sort_values("t0").iloc[-1]
    stance = "偏鹰" if e.hd_score > 0.2 else ("偏鸽" if e.hd_score < -0.2 else "中性")
    delta = e.hd_delta
    delta_txt = "—" if not np.isfinite(delta) else (f"{delta:+.2f}（" + ("转鹰" if delta > 0.05 else "转鸽" if delta < -0.05 else "基本不变") + "）")
    move = ", ".join(
        f"{a.label} {e[f'{a.key}_ret_t0']:+.2f}{_unit(a.kind)}"
        for a in ASSETS if f"{a.key}_ret_t0" in e and np.isfinite(e[f"{a.key}_ret_t0"]))
    lines = [
        f"- 声明日期：{e.release_date:%Y-%m-%d}（{e.label}{'' if e.scheduled else '，非例会'}）",
        f"- 利率决定：{e.decision_bp:+.0f} bp",
        f"- 2Y 会议日变动（利率意外代理）：{e.surprise_2y_bp:+.0f} bp；10Y：{e.d10y_bp:+.0f} bp",
        f"- 声明鹰鸽分：{e.hd_score:+.2f}（{stance}），较上次 {delta_txt}；措辞变化 {e.text_change:.0%}",
        f"- 鹰派措辞：{e.hawk_terms or '—'}",
        f"- 鸽派措辞：{e.dove_terms or '—'}",
        f"- 净鹰派反对票：{int(e.dissent_net):+d}",
        f"- 会前状态：VIX {e.vix_pre:.1f}（一年分位 {e.vix_pctile:.0%}），10Y-2Y {e.curve_2s10s:+.2f}，"
        f"Baa 利差 {e.baa_spread:.2f}，密歇根信心偏离 {e.umcsent_dev:+.1f}",
        f"- 会议反应：{move}",
    ]
    return "\n".join(lines)


def signals_table(sig: pd.DataFrame) -> str:
    if sig.empty:
        return "（数据不足，无法生成信号）"
    rows = []
    for r in sig.itertuples():
        rows.append({
            "资产": r.label, "周期": f"{r.horizon}日",
            "方向": _direction_word(r.kind, r.direction),
            "预测值": f"{r.pred:+.2f}{_unit(r.kind)}",
            "样本外胜率": r.oos_hit, "胜率 z": r.oos_z, "IC": r.oos_ic,
            "可信度": r.confidence, "主要驱动": r.drivers,
        })
    return md_table(pd.DataFrame(rows))


def backtest_table(metrics: pd.DataFrame) -> str:
    rows = []
    for r in metrics.itertuples():
        u = _unit(r.kind)
        rows.append({
            "资产": r.label, "周期": f"{r.horizon}日", "样本外次数": r.n,
            "胜率": r.hit_rate, "z": r.hit_z, "IC": r.ic,
            f"信号平均收益": f"{r.signal_mean:+.2f}{u}" if np.isfinite(r.signal_mean) else "—",
            "t": r.signal_t,
            "做多基准": f"{r.long_mean:+.2f}{u}" if np.isfinite(r.long_mean) else "—",
            "起始": r.oos_start,
        })
    return md_table(pd.DataFrame(rows))


def summarize(metrics: pd.DataFrame) -> str:
    m = metrics.dropna(subset=["hit_z"])
    strong = m[(m.hit_z >= 2) & (m.ic > 0.1)]
    n_tests = len(m)
    expected = n_tests * 0.023  # 单侧 z>=2 的随机概率约 2.3%
    if strong.empty:
        verdict = ("**没有任何资产/周期组合达到 z ≥ 2 且 IC > 0.1**，基础版特征（词典鹰鸽分 + 2Y 利率意外 + 会前状态）"
                   "在样本外没有稳健的方向预测力。")
    else:
        names = ", ".join(f"{ASSET_BY_KEY[r.asset].label} {r.horizon}日" for r in strong.itertuples())
        verdict = (f"达到 z ≥ 2 且 IC > 0.1 的组合：{names}。注意共做了 {n_tests} 次检验，"
                   f"纯随机也会有约 {expected:.1f} 个组合达标，需要在新数据上继续验证。")
    return verdict + f"\n\n共 {n_tests} 个检验；随机情况下预期约 {expected:.1f} 个 z ≥ 2 的“假阳性”。"


def build_report(events: pd.DataFrame, metrics: pd.DataFrame, signals: pd.DataFrame,
                 ic5: pd.DataFrame, upcoming: list[date] | None = None, aaii_loaded: bool = False) -> str:
    sched = events[events.scheduled]
    ic5 = ic5.rename(index=FEATURE_CN, columns={k: ASSET_BY_KEY[k].label for k in ic5.columns})
    ic5.insert(0, "特征", ic5.index)
    nxt = f"{upcoming[0]:%Y-%m-%d}" if upcoming else "未知"
    lag_assets = "、".join(a.label for a in ASSETS if a.reaction_lag)

    return f"""# FOMC 会议情绪信号 · MVP 报告

生成日期：{date.today():%Y-%m-%d}　|　下次 FOMC 会议：{nxt}

## 1. 结论

{summarize(metrics)}

这套框架（数据采集 → 事件表 → 样本外回测 → 信号输出）已经可以用，后续可以往上加更强的特征（见第 6 节）。

## 2. 最近一次会议

{latest_meeting_section(events)}

### 信号（用全部历史例会训练）

{signals_table(signals)}

> 收益率类资产的“方向”指收益率本身的涨跌（收益率↑ = 债券价格↓）。
> 可信度来自下面的样本外回测：高 = z≥2 且 IC>0.1；中 = z≥1 且 IC>0；其余为低。可信度为“低”的信号只作参考。

## 3. 样本外回测

- 样本：{sched.release_date.min():%Y-%m} 至 {sched.release_date.max():%Y-%m} 的 {len(sched)} 次例会（另有 {len(events) - len(sched)} 次紧急会议/表决不参与回测）。
- 方法：滚动扩展窗口，先积累 {MIN_TRAIN_EVENTS} 次会议再开始预测；每次只用目标已经实现的历史会议训练；
  岭回归 (λ={RIDGE_LAMBDA})，用训练集统计量做标准化。
- 特征：{", ".join(FEATURE_CN.get(f, f) for f in MODEL_FEATURES)}，外加该资产自身的会议反应。
- 预测起点：会后第一个收盘价。{lag_assets} 在 Yahoo 上的日线收盘早于 14:00 声明发布，
  所以按 T+1 收盘对齐，否则会把会议反应误算成“预测”。
- 单位：收益率为 bp 变动，其余为对数收益率 %。

{backtest_table(metrics)}

## 4. 单因子相关（全样本，5 日目标，样本内仅供描述）

秩相关 (Spearman)。|IC| < 0.1 基本可以视为噪音；这张表是样本内统计，不能直接当作可交易的结果。

{md_table(ic5)}

## 5. 数据与已知局限

- 数据来源：美联储官网（声明全文）、FRED（国债收益率、目标利率、VIX、期限利差、信用利差、密歇根信心）、
  Yahoo Finance（股指、美元、汇率、黄金、BTC）。AAII 散户情绪：{"已加载" if aaii_loaded else "未加载（官网禁止自动下载，可手动放文件）"}。
- 用会议日 2Y 收益率的日变动代替利率意外：它混入了当天其他新闻，比日内窗口（会前 10 分钟到会后 20 分钟）粗糙很多。
- 词典法在很多声明里会饱和（鹰鸽分 ±1），声明里的套话（例如缩表措辞）也会拉高分数。
- 样本少：每年 8 次会议；BTC 只有 2014 年之后的数据，样本外预测不到 60 次。
- 做了多次检验（资产 × 周期），单个组合显著不代表真有效。

## 6. 下一步建议

1. **改进利率意外**：用 2Y 国债期货/SOFR 期货的日内数据，或者会前市场隐含的降息概率与实际决定之差。
2. **文本**：换成 LLM 或 FinBERT 打分，并在句子层面对比上一篇声明的改动；把发布会文字稿和会议纪要也纳入。
3. **会间信号**：把 CPI、非农、官员讲话纳入，按周持续更新“政策预期”。
4. **推送**：信号稳定后，再接 Telegram/飞书，在会后 30 分钟和每天早上各推一次。
"""


def daily_snapshot(fred: dict[str, pd.Series], events: pd.DataFrame, upcoming: list[date]) -> str:
    """每日快照：当前市场状态 + 距离下次会议天数 + 最近一次会议信号概要。"""
    def last(sid):
        s = fred[sid].dropna()
        return s.index[-1], float(s.iloc[-1])

    d2, y2 = last("DGS2")
    _, y10 = last("DGS10")
    dv, vix = last("VIXCLS")
    vix_s = fred["VIXCLS"].dropna().tail(252)
    _, curve = last("T10Y2Y")
    _, baa = last("BAA10Y")
    nxt = upcoming[0] if upcoming else None
    days = (nxt - date.today()).days if nxt else None
    e = events.sort_values("t0").iloc[-1]
    since = (pd.Timestamp.today().normalize() - e.t0).days
    lines = [
        f"FOMC 日报 · {date.today():%Y-%m-%d}",
        f"下次会议：{nxt:%Y-%m-%d}（{days} 天后）" if nxt else "下次会议：未知",
        f"2Y {y2:.2f}%  10Y {y10:.2f}%  10Y-2Y {curve:+.2f}  （FRED 截至 {d2:%m-%d}）",
        f"VIX {vix:.1f}（一年分位 {(vix_s <= vix).mean():.0%}，截至 {dv:%m-%d}）  Baa 利差 {baa:.2f}",
        f"上次会议 {e.release_date:%Y-%m-%d}（{since} 天前）：决定 {e.decision_bp:+.0f}bp，"
        f"鹰鸽分 {e.hd_score:+.2f}，2Y 反应 {e.surprise_2y_bp:+.0f}bp",
    ]
    return "\n".join(lines)
