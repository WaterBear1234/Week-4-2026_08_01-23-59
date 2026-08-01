
import re
from dataclasses import dataclass, field

RESOURCE_LABEL_KEYS = {
    "pod": "pod",
    "namespace": "namespace",
    "deployment": "deployment",
    "node": "node",
    "instance": "instance",
    "service": "service",
    "container": "container",
    "device": "device",
    "job": "job",
    "mountpoint": "mountpoint",
}

AGG_KEYWORDS = {
    # English
    "average": "avg", "avg": "avg", "mean": "avg",
    "total": "sum", "sum": "sum",
    "maximum": "max", "max": "max", "highest": "max", "peak": "max",
    "minimum": "min", "min": "min", "lowest": "min",
    # Vietnamese
    "trung bình": "avg",
    "tổng": "sum", "tổng cộng": "sum",
    "tối đa": "max", "cao nhất": "max", "lớn nhất": "max",
    "tối thiểu": "min", "thấp nhất": "min", "nhỏ nhất": "min",
}

TIME_RANGE_RE = re.compile(
    r"(?:last|past|previous)\s+(\d+)\s*(second|sec|minute|min|hour|hr|day)s?", re.I
)
VI_TIME_RANGE_RE = re.compile(
    r"(\d+)\s*(giây|phút|giờ|ngày)\s*(?:qua|trước|gần\s*đây)?", re.I
)
TIME_UNIT_MAP = {
    "second": "s", "sec": "s",
    "minute": "m", "min": "m",
    "hour": "h", "hr": "h",
    "day": "d",
    "giây": "s", "phút": "m", "giờ": "h", "ngày": "d",
}

DEFAULT_RANGE = "5m"

# Words the ASCII-only capture regex could grab instead of a real
# identifier. Vietnamese diacritic words (của, trên, trước, là, ...) are
# already excluded for free -- [a-zA-Z0-9_\-\.]+ can't match them -- but a
# few unaccented Vietnamese connectors (trong, cho, qua) are added
# defensively in case someone types without diacritics.
STOPWORDS = {
    "in", "over", "for", "the", "a", "an", "of", "to", "has", "have",
    "is", "was", "restarted", "restarting", "and", "or", "with",
    "up", "down", "healthy",
    "cpu", "memory", "disk", "network", "usage", "restart", "restarts",
    "rate", "traffic", "bytes", "space", "percentage", "percent",
    "utilization", "available", "free", "receive", "transmit",
    "trong", "cho", "qua", "la", "co", "cua",
}

GROUP_BY_MARKERS = ["per", "by", "each", "mỗi", "theo"]


@dataclass
class ParsedQuery:
    raw: str
    resource_filters: dict = field(default_factory=dict)
    aggregation: str | None = None
    group_by: list = field(default_factory=list)
    time_range: str = DEFAULT_RANGE
    language: str = "en"


def _detect_language(text: str) -> str:
    vietnamese_diacritics = re.compile(
        r"[àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]", re.I
    )
    return "vi" if vietnamese_diacritics.search(text) else "en"


def _extract_resource_filters(text: str) -> dict:
    filters = {}
    for kind, label_key in RESOURCE_LABEL_KEYS.items():
        group_by_prefix = "|".join(GROUP_BY_MARKERS)
        pattern = (
            rf"(?<![\w-])(?:{group_by_prefix})\s+{kind}\b"
            rf"|(?<![\w-]){kind}\b\s+([a-zA-Z0-9_\-\.]+)"
        )
        for m in re.finditer(pattern, text, re.I):
            if m.group(1) is None:
                continue  # matched the group-by branch, not a filter
            value = m.group(1).strip(").,?!")
            if value.lower() in STOPWORDS or value.lower() in RESOURCE_LABEL_KEYS:
                continue
            filters[label_key] = value
    return filters


def _extract_aggregation(text: str) -> str | None:
    # longer phrases first so "trung bình" matches before any shorter
    # accidental substring would
    for kw in sorted(AGG_KEYWORDS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(kw)}\b", text, re.I):
            return AGG_KEYWORDS[kw]
    return None


def _extract_time_range(text: str) -> str:
    m = TIME_RANGE_RE.search(text)
    if m:
        amount, unit = m.group(1), m.group(2).lower()
        return f"{amount}{TIME_UNIT_MAP[unit]}"

    m = VI_TIME_RANGE_RE.search(text)
    if m:
        amount, unit = m.group(1), m.group(2).lower()
        return f"{amount}{TIME_UNIT_MAP[unit]}"

    return DEFAULT_RANGE


def parse(query: str) -> ParsedQuery:
    filters = _extract_resource_filters(query)
    agg = _extract_aggregation(query)
    time_range = _extract_time_range(query)
    language = _detect_language(query)

    group_by = []
    group_by_prefix = "|".join(GROUP_BY_MARKERS)
    for kind, label_key in RESOURCE_LABEL_KEYS.items():
        if re.search(rf"\b(?:{group_by_prefix})\s+{kind}\b", query, re.I):
            group_by.append(label_key)

    return ParsedQuery(
        raw=query,
        resource_filters=filters,
        aggregation=agg,
        group_by=group_by,
        time_range=time_range,
        language=language,
    )
