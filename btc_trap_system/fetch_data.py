"""Download daily history from Yahoo Finance chart API (BTC + macro proxies)."""
import json, sys, time, urllib.request, pandas as pd, pathlib
TICKERS = {
    "BTC": "BTC-USD", "ETH": "ETH-USD", "DXY": "DX-Y.NYB", "US10Y": "^TNX",
    "US3M": "^IRX", "SPX": "^GSPC", "NDX": "^NDX", "VIX": "^VIX", "GOLD": "GC=F",
    "HYG": "HYG", "TLT": "TLT", "IBIT": "IBIT", "MSTR": "MSTR", "COIN": "COIN",
    "USDJPY": "JPY=X", "OIL": "CL=F",
}
out = pathlib.Path(__file__).parent / "data"
def get(sym, interval="1d"):
    url = (f"https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}"
           f"?period1=1262304000&period2={int(time.time())}&interval={interval}&events=history")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for i in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=30))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            df = pd.DataFrame({k: q[k] for k in ["open", "high", "low", "close", "volume"]},
                              index=pd.to_datetime(r["timestamp"], unit="s").normalize())
            return df.dropna(subset=["close"])
        except Exception as e:
            print(sym, "retry", e, file=sys.stderr); time.sleep(3 * (i + 1))
    raise RuntimeError(sym)
import urllib.parse
for name, sym in TICKERS.items():
    df = get(sym); df = df[~df.index.duplicated(keep="last")]
    df.to_csv(out / f"{name}.csv"); print(name, len(df), df.index[0].date(), df.index[-1].date(), round(df.close.iloc[-1], 2))
    time.sleep(1)
w = get("BTC-USD", "1wk"); w.to_csv(out / "BTC_weekly.csv")
h = get.__wrapped__ if hasattr(get, "__wrapped__") else None
