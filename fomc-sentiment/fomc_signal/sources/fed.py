"""美联储官网：FOMC 会议列表与声明全文。

- 近几年 (约 5 年)：https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- 更早年份：https://www.federalreserve.gov/monetarypolicy/fomchistorical{YYYY}.htm

不同年份的链接格式不同（boarddocs/press/general、newsevents/press/monetary、
newsevents/pressreleases/monetaryYYYYMMDDa.htm），所以统一按链接文字 "Statement"
或会议块里的声明链接来抓，日期取 URL 里的 8 位数字（= 声明发布日）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import date, datetime
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup

from ..config import RAW_DIR, START_YEAR
from ..http import get_text

BASE = "https://www.federalreserve.gov"
CALENDAR_URL = f"{BASE}/monetarypolicy/fomccalendars.htm"
HISTORICAL_URL = f"{BASE}/monetarypolicy/fomchistorical{{year}}.htm"

_DATE_IN_URL = re.compile(r"((?:19|20)\d{6})")
_CAL_STATEMENT = re.compile(r"/newsevents/pressreleases/monetary(\d{8})a\.htm$")
_NOT_SCHEDULED = ("unscheduled", "conference call", "notation", "cancelled")
_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}


@dataclass
class Statement:
    date: date          # 声明发布日
    url: str
    label: str          # 页面上的会议标题
    scheduled: bool     # 是否为例会（非紧急电话会/表决）


def _is_scheduled(label: str) -> bool:
    low = label.lower()
    return not any(word in low for word in _NOT_SCHEDULED)


def parse_historical_page(html: str, page_url: str) -> list[Statement]:
    soup = BeautifulSoup(html, "lxml")
    out: list[Statement] = []
    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True) != "Statement":
            continue
        m = _DATE_IN_URL.search(a["href"])
        if not m:
            continue
        heading = a.find_previous(["h4", "h5"])
        label = heading.get_text(" ", strip=True) if heading else ""
        scheduled = "meeting" in label.lower() and _is_scheduled(label)
        out.append(Statement(datetime.strptime(m.group(1), "%Y%m%d").date(),
                             urljoin(page_url, a["href"]), label, scheduled))
    return out


def parse_calendar_page(html: str) -> tuple[list[Statement], list[date], set[int]]:
    """返回 (已发布声明, 全部会议结束日(含未来), 页面覆盖的年份)。"""
    soup = BeautifulSoup(html, "lxml")
    statements: list[Statement] = []
    meeting_days: list[date] = []
    years: set[int] = set()
    for panel in soup.select("div.panel"):
        heading = panel.select_one(".panel-heading")
        ym = re.search(r"(\d{4}) FOMC Meetings", heading.get_text(" ", strip=True)) if heading else None
        if not ym:
            continue
        year = int(ym.group(1))
        years.add(year)
        for meeting in panel.select("div.fomc-meeting"):
            month_el = meeting.select_one(".fomc-meeting__month")
            date_el = meeting.select_one(".fomc-meeting__date")
            if not (month_el and date_el):
                continue
            month_txt, date_txt = month_el.get_text(strip=True), date_el.get_text(strip=True)
            label = f"{month_txt} {date_txt} - {year}"
            end_day = _meeting_end(year, month_txt, date_txt)
            if end_day:
                meeting_days.append(end_day)
            for a in meeting.find_all("a", href=True):
                m = _CAL_STATEMENT.search(a["href"])
                if m:
                    statements.append(Statement(datetime.strptime(m.group(1), "%Y%m%d").date(),
                                                urljoin(BASE, a["href"]), label, _is_scheduled(label)))
                    break
    return statements, sorted(set(meeting_days)), years


def _meeting_end(year: int, month_txt: str, date_txt: str) -> date | None:
    """'April/May' + '30-1*' -> 5 月 1 日。"""
    months = [_MONTHS.get(p.strip().lower()) for p in month_txt.split("/")]
    days = re.findall(r"\d+", date_txt)
    if not days or not months or months[-1] is None:
        return None
    try:
        return date(year, months[-1], int(days[-1]))
    except ValueError:
        return None


def list_statements(*, start_year: int = START_YEAR, refresh: bool = False) -> pd.DataFrame:
    cal_html = get_text(CALENDAR_URL, refresh=refresh)
    statements, _, cal_years = parse_calendar_page(cal_html)
    this_year = date.today().year
    for year in range(start_year, this_year + 1):
        if year in cal_years:
            continue
        url = HISTORICAL_URL.format(year=year)
        # 往年页面不会再变，只有当前年份需要刷新
        statements += parse_historical_page(get_text(url, refresh=refresh and year >= this_year - 1), url)

    df = pd.DataFrame([asdict(s) for s in statements])
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"].dt.year >= start_year]
    df = df.sort_values("date").drop_duplicates("date", keep="first").reset_index(drop=True)
    return df


def upcoming_meetings(*, refresh: bool = False) -> list[date]:
    _, days, _ = parse_calendar_page(get_text(CALENDAR_URL, refresh=refresh))
    today = date.today()
    return [d for d in days if d >= today]


# ---------- 声明正文 ----------

_CUT_MARKERS = (
    "Voting for the FOMC monetary policy action",
    "Voting for the monetary policy action",
    "Voting for the FOMC",
    "Voting for this action",
    "Voting for the action",
    "Voting for the policy action",
    "Voting in favor",
    "Voting against",
    "Monetary policy Home",
    "Last update:",
    "Implementation Note",
    "For media inquiries",
)
_START_MARKERS = (
    "Information received",
    "Recent indicators",
    "The Federal Open Market Committee",
    "The Federal Reserve",
    "Economic activity",
    "Indicators of economic activity",
    "Although",
    "Readings on",
    "The economic outlook",
)


def extract_full_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    node = soup.select_one("#article") or soup.select_one("#content") or soup.body or soup
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True))


def extract_statement_text(html: str) -> str:
    """只保留政策声明正文：去掉表决名单、贴现率等附带内容和页脚。"""
    text = extract_full_text(html)

    starts = [text.find(m) for m in _START_MARKERS if text.find(m) >= 0]
    if starts:
        text = text[min(starts):]
    # "In a related action" 在 2000 年代的声明里紧跟利率决定之后，只删掉这一段
    text = re.sub(r"In a related action.*?(?=(?:The Committee|Against the background|The Federal|Although|Nonetheless|Recent|Information received)|$)",
                  "", text, count=1)
    cuts = [text.find(m) for m in _CUT_MARKERS if text.find(m) > 0]
    if cuts:
        text = text[:min(cuts)]
    return text.strip()


def load_statement_texts(statements: pd.DataFrame, *, refresh: bool = False) -> pd.DataFrame:
    """补充 text 列，正文另存到 data/raw/statements/ 方便人工检查。"""
    out_dir = RAW_DIR / "statements"
    out_dir.mkdir(parents=True, exist_ok=True)
    texts, dissents = [], []
    for row in statements.itertuples():
        html = get_text(row.url, refresh=refresh)
        text = extract_statement_text(html)
        (out_dir / f"{row.date:%Y%m%d}.txt").write_text(text, encoding="utf-8")
        texts.append(text)
        dissents.append(parse_dissents(extract_full_text(html)))
    out = statements.copy()
    out["text"] = texts
    for k in ("hawk", "dove", "hold", "other"):
        out[f"dissent_{k}"] = [d[k] for d in dissents]
    return out


# ---------- 反对票 ----------

_HAWK_VERBS = ("raise", "increase", "tighten", "firm", "begin reducing", "end ", "reduce the pace", "taper")
_DOVE_VERBS = ("lower", "decrease", "reduce the target", "cut", "ease", "provide additional", "expand",
               "continue purchas", "continue the")
_HOLD_VERBS = ("maintain", "keep", "leave", "hold", "retain")


def parse_dissents(full_text: str) -> dict[str, int]:
    """统计反对票方向：{"hawk": 偏鹰, "dove": 偏鸽, "hold": 主张按兵不动, "other": 无法判断}。

    "hold" 的方向要看本次决定：降息时主张不动 = 偏鹰，加息时 = 偏鸽，在特征层处理。
    """
    counts = {"hawk": 0, "dove": 0, "hold": 0, "other": 0}
    idx = full_text.find("Voting against")
    if idx < 0:
        return counts
    block = full_text[idx:]
    stop = re.search(r"\.\s+(?:In a related|Implementation|For media|Voting for|Last update|\d{4} Monetary)", block)
    if stop:
        block = block[:stop.start() + 1]
    for clause in re.split(r";\s*(?:and\s+)?", block):
        low = clause.lower()
        k = low.find("preferred to ")
        n = _count_names(clause)
        if k < 0:
            if " who " in low:
                counts["other"] += n
            continue
        verb = low[k + len("preferred to "):][:60]
        if verb.startswith(_HOLD_VERBS) or "unchanged" in verb:
            counts["hold"] += n
        elif verb.startswith(_DOVE_VERBS):
            counts["dove"] += n
        elif verb.startswith(_HAWK_VERBS):
            counts["hawk"] += n
        else:
            counts["other"] += n
    return counts


def _count_names(clause: str) -> int:
    """'Voting against the action were A and B, who preferred...' -> 2"""
    head = clause.split(" who ")[0]
    m = re.search(r"\b(?:was|were)\s+(.+)$", head)
    names = (m.group(1) if m else head).strip(" ,.")
    names = re.sub(r"^and\s+", "", names)
    parts = [p for p in re.split(r",\s*(?:and\s+)?|\s+and\s+", names) if p.strip()]
    # 去掉 "Jr." 之类被逗号拆开的片段
    parts = [p for p in parts if len(p.strip()) > 3]
    return max(1, len(parts))
