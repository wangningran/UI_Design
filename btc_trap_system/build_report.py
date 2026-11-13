"""Fill report_template.html with out/results.json + out/charts.json -> out/report.html"""
import json, pathlib
H = pathlib.Path(__file__).parent
R = json.loads((H / "out/results.json").read_text()); CH = (H / "out/charts.json").read_text()
S = R["snapshot"]; pct = lambda k: f'{S[k]["pctile"]:.0f}%'
P = R["price"]
def lean(x): return {"bear": '<span class="lean bear">偏空</span>', "bull": '<span class="lean bull">偏多</span>', "mid": '<span class="lean mid">中性</span>'}[x]
ev = [
 ("周期·时间", f'ATH 后第 {S["days_since_ath"]["value"]:.0f} 天，减半后第 {S["days_since_halving"]["value"]:.0f} 天', "前三轮在 ATH 后第 363–410 天见底，减半后第 889–924 天见底", "bull"),
 ("周期·幅度", f'距 ATH {S["dd_ath"]["value"]*100:.1f}%，本轮最深 −53%', "前三轮最深 −84% / −83% / −76%，回撤逐轮递减", "mid"),
 ("估值·200 周均线", f'价格 / 200WMA = {S["p_200wma"]["value"]:.3f}', f'{pct("p_200wma")} 分位；2022 年跌破后又跌了 21–24%，2020 和 2023 年跌破即是底', "bull"),
 ("估值·Mayer 倍数", f'{S["mayer"]["value"]:.3f}', f'{pct("mayer")} 分位，偏低但不极端（真正的底部通常低于 0.7）', "mid"),
 ("估值·4 年 z 分数", f'{S["z_4y"]["value"]:.2f}', f'{pct("z_4y")} 分位，价格处在 4 年对数均值附近', "bull"),
 ("趋势·均线", f'低于 50 日均线 {S["p_ma50"]["value"]*100:.1f}%，低于 200 日均线 {S["p_ma200"]["value"]*100:.1f}%', "跌破 55 日低点 73.6k，为 8 月以来最低", "bear"),
 ("趋势·周线结构", "周线高低点仍是 HH/HL（+2）", "6 月低点 58.6k 守住之前，周线结构还没有转空", "bull"),
 ("动量·日 RSI", f'{S["rsi_d"]["value"]:.1f}', f'{pct("rsi_d")} 分位，极度超卖，短线容易反弹', "bull"),
 ("动量·周 RSI / MACD", f'周 RSI {S["rsi_w"]["value"]:.1f}', "周线没有超卖，历史大底的周 RSI 一般低于 30", "bear"),
 ("K 线·量能", f'成交量 z = {S["vol_z"]["value"]:.2f}，下影线比例 {S["low_wick"]["value"]:.2f}', "放量下跌，但没有长下影，还不是投降式的 K 线", "bear"),
 ("K 线·9 月突破", "82,262 突破失败，现价低于突破位 16.9%", "满足牛市陷阱定义", "bear"),
 ("回测·条件基准率", "距 ATH 超过 40% 且宏观逆风时跌破", "熊市陷阱比例 22%（9 个样本），90 天收益中位数 −3.2%", "bear"),
 ("回测·事件模型", f'P(熊市陷阱) = {R["p_bear_trap_today"]*100:.0f}%', "样本外准确率 33%，不可靠，只作参考", "bear"),
 ("回测·kNN 相似状态", "最像 2018-11、2022-04/05、2020-03", f'90 天收益中位数 {R["knn"]["median_r90"]*100:.0f}%，上涨概率 {R["knn"]["p_up_90"]*100:.0f}%；180 天上涨概率 {R["knn"]["p_up_180"]*100:.0f}%', "bear"),
 ("回测·综合评分", f'{R["score_now"]["total"]:.2f}（{R["score_pctile_now"]:.0f}% 分位）', f'相近评分的历史日子：365 天收益中位数 +{R["score_near_now"]["median_r365"]*100:.0f}%，上涨概率 {R["score_near_now"]["p_up_365"]*100:.0f}%；90 天上涨概率 {R["score_near_now"]["p_up_90"]*100:.0f}%', "bull"),
 ("宏观·利率", f'10Y {S["us10y"]["value"]:.2f}%，90 天 +{S["us10y_chg90"]["value"]*100:.0f}bp', f'{pct("us10y")} 分位，12 月加息定价接近 100%', "bear"),
 ("宏观·美元与信用", f'DXY 60 天 +{S["dxy_roc60"]["value"]*100:.1f}%，HYG {S["hyg_roc60"]["value"]*100:.1f}%', f'美元 {pct("dxy_roc60")} 分位走强，信用利差走阔', "bear"),
 ("宏观·美股联动", f'BTC 与 SPX 90 日相关 {S["corr_spx90"]["value"]:.2f}', "标普卡在 200 日均线，VIX 19.3", "bear"),
 ("资金·ETF", "11/5–11/12 净流出约 14.9 亿美元", "IBIT 连续 9 天流出", "bear"),
 ("资金·风险偏好", f'ETH/BTC 90 天 {S["ethbtc_roc90"]["value"]*100:.1f}%', "山寨币相对走弱，风险偏好低", "bear"),
]
rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{lean(d)}</td></tr>" for a, b, c, d in ev)
cn = {"Mayer<1 (below 200DMA)": "价格低于 200 日均线", "200DMA falling": "200 日均线向下", "macro headwind (score<0)": "宏观逆风（评分 < 0）",
      "200DMA falling AND macro headwind": "200 日均线向下且宏观逆风", "already >40% below ATH": "距 ATH 超过 40%",
      ">40% below ATH AND macro headwind": "距 ATH 超过 40% 且宏观逆风", "daily RSI<30 at breakdown": "跌破时日 RSI < 30",
      "volume spike (z>1)": "跌破时放量（z > 1）", "weekly swing structure bearish": "周线结构偏空", "200DMA rising (bull-market dips)": "200 日均线向上（牛市回调）"}
cond = f'<tr><td><b>全部事件</b></td><td class="n">{R["breakdown_events"]["n"]}</td><td class="n">{R["breakdown_events"]["base_bear_trap_rate"]*100:.0f}%</td><td class="n">{R["breakdown_events"]["median_r90"]*100:+.1f}%</td></tr>'
cond += "".join(f'<tr><td>{cn[c["cond"]]}</td><td class="n">{c["n"]}</td><td class="n">{c["bear_trap_rate"]*100:.0f}%</td><td class="n">{c["median_r90"]*100:+.1f}%</td></tr>' for c in R["conditional"])
zh = {"200WMA": "200 周均线", "200DMA": "200 日均线", "111DMA": "111 日均线", "50DMA": "50 日均线", "2026 low (Jun)": "2026 年 6 月低点",
      "Sep-2026 high": "2026 年 9 月高点", "Feb-2026 low": "2026 年 2 月低点", "0.618 retr. 58.6k→86.6k": "0.618 回撤（58.6k→86.6k）",
      "0.786 retr.": "0.786 回撤", "-60% from ATH": "距 ATH −60%", "-70% from ATH": "距 ATH −70%", "2021 ATH (69k)": "2021 年前高（收盘）"}
lv = [(zh.get(k, k.replace("vol-node", "成交密集区")), v) for k, v in R["levels"].items()] + [("现价", P)]
lv.sort(key=lambda t: -t[1])
levels = "".join(f'<tr class="{"now" if k=="现价" else ""}"><td>{k}</td><td class="n">{v:,.0f}</td><td class="n">{(v/P-1)*100:+.1f}%</td></tr>' for k, v in lv)
q = R["score_quintiles_median_fwd"]; mc = R["monte_carlo"]; ic = R["score_ic"]
rep = {"__DATE__": R["date"], "__PRICE__": f"{P:,.0f}", "__DD__": f'{S["dd_ath"]["value"]*100:.1f}%', "__DSA__": f'{S["days_since_ath"]["value"]:.0f}',
       "__DSH__": f'{S["days_since_halving"]["value"]:.0f}', "__RSI__": f'{S["rsi_d"]["value"]:.1f}', "__US10Y__": f'{S["us10y"]["value"]:.2f}',
       "__EVIDENCE__": rows, "__COND__": cond, "__LEVELS__": levels, "__NEV__": str(R["breakdown_events"]["n"]),
       "__POOL__": str(mc["pool_days"]), "__MC90__": f'${mc["d90"]["p50"]:,.0f}', "__P60__": f'{mc["p_touch_60k_90d"]*100:.0f}%',
       "__P80__": f'{mc["p_reclaim_80k_90d"]*100:.0f}%', "__MACRO__": f'{S["macro_score"]["value"]:.2f}',
       "__IC30__": f'{ic["30"]:.2f}', "__IC90__": f'{ic["90"]:.2f}', "__IC180__": f'{ic["180"]:.2f}', "__IC365__": f'{ic["365"]:.2f}',
       "__Q1__": f'{q["Q1 low"]["365"]*100:+.0f}%', "__Q5__": f'{q["Q5 high"]["365"]*100:+.0f}%', "__CHARTS__": CH}
t = (H / "report_template.html").read_text()
for k, v in rep.items(): t = t.replace(k, v)
assert "__" not in t.replace("__agentproxy", ""), [l for l in t.split() if "__" in l][:5]
(H / "out/report.html").write_text(t); print("ok", len(t))
