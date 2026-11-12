"""基于词典的 FOMC 声明鹰鸽打分。

两层规则，全部事先写死、不从数据中学习（避免回测中的未来函数）：

1. 政策措辞短语 (权重 2)：如 "raise the target range" (鹰)、"exceptionally low levels" (鸽)。
   先匹配并遮盖，避免被第二层重复计数。
2. 主题 + 方向 (权重 1)，参考 Apel & Blix Grimaldi (2012) 的思路：
   同一句里 "通胀/增长/就业" 一类主题词与 "上升/强劲" 或 "下降/疲弱" 一类方向词
   在 6 个词以内同时出现即计一次。失业率方向相反（上升 = 鸽）。

hd_score = (鹰 - 鸽) / (鹰 + 鸽)，范围 [-1, 1]，正数偏鹰。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

POLICY_WEIGHT = 2.0
TOPIC_WEIGHT = 1.0
WINDOW = 6

# ---- 第一层：政策措辞 ----
HAWKISH_PHRASES = [
    r"rais\w* (?:its|the) target",
    r"increas\w* (?:its|the) target",
    r"decided today to raise",
    r"further (?:policy )?firming",
    r"additional (?:policy )?firming",
    r"policy firming",
    r"ongoing increases in the target range",
    r"further gradual increases",
    r"gradual increases in the target range",
    r"(?:removal|removing|remove) (?:of )?(?:policy )?accommodation",
    r"accommodation can be removed",
    r"reduc\w* (?:its|the) holdings",
    r"reduc\w* the (?:monthly )?pace of (?:its )?(?:asset |net asset )?purchases",
    r"balance sheet normalization",
    r"upside risks? to inflation",
    r"inflation risks",
    r"risk of (?:higher|rising) inflation",
    r"highly attentive to inflation risks",
    r"strongly committed to returning inflation",
    r"inflation (?:remains|has remained|is) elevated",
    r"elevated inflation",
    r"sufficiently restrictive",
    r"restrictive",
    r"some further policy firming",
    r"tighten\w*",
    r"deliver price stability",
]

DOVISH_PHRASES = [
    r"lower\w* (?:its|the) target",
    r"reduc\w* (?:its|the) target",
    r"decreas\w* (?:its|the) target",
    r"decided today to lower",
    r"exceptionally low levels",
    r"extended period",
    r"considerable period",
    r"considerable time",
    r"be patient",
    r"patient in determining",
    r"highly accommodative",
    r"maintain (?:a|an|the) (?:highly )?accommodative",
    r"stance of monetary policy remains accommodative",
    r"increas\w* (?:its|the) holdings",
    r"purchas\w* (?:additional )?(?:agency |treasury |longer-term )?(?:mortgage-backed )?securities",
    r"asset purchases",
    r"additional accommodation",
    r"downside risks?",
    r"act as appropriate to sustain the expansion",
    r"sustain the expansion",
    r"support (?:the|economic|continued) (?:economy|activity|expansion|growth|recovery)",
    r"provide (?:additional )?support",
    r"(?:inflation|it) (?:is |has been |continues to )?running below",
    r"below (?:its|the Committee's) (?:2 percent|longer-run)",
    r"low inflation",
    r"weaken\w*",
    r"eas\w* (?:of )?(?:monetary )?policy",
    r"policy easing",
]

# ---- 第二层：主题 + 方向 ----
TOPICS = {
    "inflation": [r"inflation\w*", r"prices?", r"price pressures?", r"cost pressures?",
                  r"compensation", r"wage\w*"],
    "activity": [r"economic activity", r"growth", r"spending", r"investment", r"output",
                 r"demand", r"economy", r"expansion", r"housing", r"production", r"sales"],
    "labor": [r"labor market\w*", r"employment", r"job gains", r"payrolls?", r"hiring",
              r"labor (?:market )?conditions"],
    "unemployment": [r"unemployment(?: rate)?", r"jobless\w*", r"underutilization", r"slack"],
}
UP_WORDS = [r"increas\w*", r"ris(?:e|es|ing|en)", r"rose", r"elevated", r"high(?:er)?", r"strong\w*",
            r"robust", r"solid", r"firm\w*", r"accelerat\w*", r"expand\w*", r"pick(?:ed)?_up",
            r"upward", r"upside", r"tight\w*", r"resilient", r"improv\w*", r"moved_up", r"edged_up", r"gain\w*",
            r"brisk", r"vigorous", r"healthy"]
DOWN_WORDS = [r"decreas\w*", r"declin\w*", r"low(?:er)?", r"weak\w*", r"soft\w*", r"subdued",
              r"slow\w*", r"moderat\w*", r"contract\w*", r"deteriorat\w*", r"downward", r"downside",
              r"eas(?:ed|ing)", r"below", r"f(?:a|e)ll(?:en)?", r"muted", r"restrained", r"sluggish",
              r"diminish\w*", r"moved_down", r"edged_down", r"cool\w*", r"contain\w*", r"stabiliz\w*"]

_SENT_SPLIT = re.compile(r"(?<=[.;:])\s+")
_TOKEN = re.compile(r"[a-z][a-z0-9_'\-]*")
_MULTIWORD = re.compile(r"\b(picked|pick|moved|edged) (up|down)\b")


def _compile(words):
    return [re.compile(rf"\b{w}\b") for w in words]


_HAWK_RE = _compile(HAWKISH_PHRASES)
_DOVE_RE = _compile(DOVISH_PHRASES)
_TOPIC_RE = {k: _compile(v) for k, v in TOPICS.items()}
_UP_RE = _compile(UP_WORDS)
_DOWN_RE = _compile(DOWN_WORDS)


@dataclass
class HawkDoveResult:
    hawk: float = 0.0
    dove: float = 0.0
    hits: list[tuple[str, str, float]] = field(default_factory=list)  # (方向, 命中文本, 权重)

    @property
    def score(self) -> float:
        total = self.hawk + self.dove
        return 0.0 if total == 0 else (self.hawk - self.dove) / total

    @property
    def net(self) -> float:
        return self.hawk - self.dove

    def top_hits(self, side: str, n: int = 5) -> list[str]:
        seen: dict[str, float] = {}
        for s, text, w in self.hits:
            if s == side:
                seen[text] = seen.get(text, 0) + w
        return [t for t, _ in sorted(seen.items(), key=lambda kv: -kv[1])[:n]]


def _mask(text: str, span: tuple[int, int]) -> str:
    return text[:span[0]] + " " * (span[1] - span[0]) + text[span[1]:]


def score_text(text: str) -> HawkDoveResult:
    res = HawkDoveResult()
    low = re.sub(r"\s+", " ", text.lower())

    # 第一层：政策短语（较长的模式写在前面，命中后遮盖）
    for side, patterns in (("hawk", _HAWK_RE), ("dove", _DOVE_RE)):
        for pat in patterns:
            for m in list(pat.finditer(low)):
                if not low[m.start():m.end()].strip():
                    continue
                res.hits.append((side, m.group(0), POLICY_WEIGHT))
                low = _mask(low, m.span())
    res.hawk += sum(w for s, _, w in res.hits if s == "hawk")
    res.dove += sum(w for s, _, w in res.hits if s == "dove")

    # 第二层：主题 + 方向
    low = _MULTIWORD.sub(r"\1_\2", low)
    for sent in _SENT_SPLIT.split(low):
        for topic, pats in _TOPIC_RE.items():
            for pat in pats:
                for m in pat.finditer(sent):
                    direction = _nearest_direction(sent, m.start(), m.end())
                    if direction is None:
                        continue
                    up = direction == "up"
                    hawkish = (not up) if topic == "unemployment" else up
                    side = "hawk" if hawkish else "dove"
                    res.hits.append((side, f"{m.group(0)}~{direction}", TOPIC_WEIGHT))
                    if hawkish:
                        res.hawk += TOPIC_WEIGHT
                    else:
                        res.dove += TOPIC_WEIGHT
    return res


def _nearest_direction(sent: str, start: int, end: int) -> str | None:
    """主题词前后 WINDOW 个词内最近的方向词。"""
    before = _TOKEN.findall(sent[:start])[-WINDOW:]
    after = _TOKEN.findall(sent[end:])[:WINDOW]
    best: tuple[int, str] | None = None
    for dist, tok in [(len(before) - i, t) for i, t in enumerate(before)] + \
                     [(i + 1, t) for i, t in enumerate(after)]:
        for direction, pats in (("up", _UP_RE), ("down", _DOWN_RE)):
            if any(p.fullmatch(tok) for p in pats):
                if best is None or dist < best[0]:
                    best = (dist, direction)
    return best[1] if best else None


def text_change(prev: str | None, curr: str) -> float:
    """与上一篇声明相比的措辞变化比例 (0 = 完全一样, 1 = 完全不同)。"""
    if not prev:
        return float("nan")
    return 1.0 - SequenceMatcher(None, prev.lower().split(), curr.lower().split(),
                                 autojunk=False).ratio()
