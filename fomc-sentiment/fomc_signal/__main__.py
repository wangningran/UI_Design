"""命令行入口。

    python -m fomc_signal report   # 拉数据（有缓存）-> 回测 -> 生成报告 reports/report_YYYYMMDD.md
    python -m fomc_signal latest   # 只输出最近一次会议的解读和信号（会后推送用）
    python -m fomc_signal daily    # 每日快照
    加 --refresh 强制重新下载最新数据
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from . import backtest as bt
from .config import REPORT_DIR
from .data import load_all
from .report import build_report, daily_snapshot, latest_meeting_section, signals_table
from .sources import fed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fomc_signal", description="FOMC 会议情绪信号 MVP")
    parser.add_argument("command", choices=["report", "latest", "daily"])
    parser.add_argument("--refresh", action="store_true", help="重新下载最新数据")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    log = (lambda *a: None) if args.quiet else (lambda *a: print(*a, file=sys.stderr))
    ds = load_all(refresh=args.refresh, log=log)
    try:
        upcoming = fed.upcoming_meetings()
    except Exception as err:
        log(f"! 获取会议日历失败：{err}")
        upcoming = []

    if args.command == "daily":
        print(daily_snapshot(ds.fred, ds.events, upcoming))
        return 0

    log("· 样本外回测")
    metrics, _ = bt.run_all(ds.events)
    signals = bt.latest_signals(ds.events, metrics)

    if args.command == "latest":
        print("## 最近一次 FOMC 会议\n")
        print(latest_meeting_section(ds.events))
        print("\n## 信号\n")
        print(signals_table(signals))
        return 0

    text = build_report(ds.events, metrics, signals, bt.univariate_ic(ds.events, 5),
                        upcoming, aaii_loaded=ds.aaii is not None)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"report_{date.today():%Y%m%d}.md"
    out.write_text(text, encoding="utf-8")
    metrics.to_csv(REPORT_DIR / "backtest_metrics.csv", index=False)
    signals.to_csv(REPORT_DIR / "latest_signals.csv", index=False)
    print(f"报告已生成：{out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
