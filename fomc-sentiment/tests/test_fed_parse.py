from datetime import date

from fomc_signal.sources.fed import (extract_statement_text, parse_calendar_page, parse_dissents,
                                     parse_historical_page)

HISTORICAL = """
<html><body>
<h5>January 21 Conference Call - 2008</h5>
<p><a href="/newsevents/press/monetary/20080122b.htm">Statement</a></p>
<h5>January 29-30 Meeting - 2008</h5>
<p><a href="/newsevents/press/monetary/20080130a.htm">Statement</a>
   <a href="/aboutthefed/fed-financial-statements.htm">Fed Financial Statements</a></p>
</body></html>
"""

CALENDAR = """
<html><body>
<div class="panel"><div class="panel-heading"><h4>2026 FOMC Meetings</h4></div>
  <div class="fomc-meeting">
    <div class="fomc-meeting__month">April/May</div><div class="fomc-meeting__date">30-1</div>
    <a href="/newsevents/pressreleases/monetary20260501a.htm">HTML</a>
    <a href="/newsevents/pressreleases/monetary20260501a1.htm">Implementation Note</a>
  </div>
  <div class="fomc-meeting">
    <div class="fomc-meeting__month">December</div><div class="fomc-meeting__date">8-9*</div>
  </div>
</div>
</body></html>
"""


def test_parse_historical_page_flags_unscheduled():
    st = parse_historical_page(HISTORICAL, "https://www.federalreserve.gov/x.htm")
    assert [s.date for s in st] == [date(2008, 1, 22), date(2008, 1, 30)]
    assert [s.scheduled for s in st] == [False, True]
    assert st[0].url == "https://www.federalreserve.gov/newsevents/press/monetary/20080122b.htm"


def test_parse_calendar_page():
    st, days, years = parse_calendar_page(CALENDAR)
    assert years == {2026}
    assert len(st) == 1 and st[0].date == date(2026, 5, 1)
    assert days == [date(2026, 5, 1), date(2026, 12, 9)]   # 跨月会议取最后一天；未来会议也在列


def test_extract_statement_text_strips_votes_and_footer():
    html = """<html><body><div id="article"><p>For release at 2:00 p.m.</p>
    <p>Information received since the Committee met indicates growth.</p>
    <p>Voting for the monetary policy action were A; B.</p></div></body></html>"""
    assert extract_statement_text(html) == "Information received since the Committee met indicates growth."


def test_parse_dissents():
    text = ("... Voting against the action were Lisa D. Cook and Beth M. Hammack, who preferred to raise "
            "the target range by 1/4 percentage point at this meeting.")
    assert parse_dissents(text) == {"hawk": 2, "dove": 0, "hold": 0, "other": 0}
    text = ("Voting against this action was Stephen I. Miran, who preferred to lower the target range by "
            "1/2 percentage point.")
    assert parse_dissents(text)["dove"] == 1
    assert parse_dissents("no dissent here") == {"hawk": 0, "dove": 0, "hold": 0, "other": 0}
