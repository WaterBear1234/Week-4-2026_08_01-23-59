
import difflib
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class MetricSpec:
    key: str
    promql_name: str
    kind: str                  # 'counter' | 'gauge'
    category: str
    keywords: list
    keywords_vi: list
    valid_labels: list
    unit: str
    is_composite: bool = False
    numerator: Optional[str] = None
    numerator_filter: Optional[str] = None
    denominator: Optional[str] = None
    is_expression_composite: bool = False


class MetricCatalog:
    def __init__(self, glossary_path: str):
        with open(glossary_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        self.specs: dict[str, MetricSpec] = {}
        for key, m in raw.get("metrics", {}).items():
            self.specs[key] = MetricSpec(
                key=key,
                promql_name=m["promql_name"],
                kind=m["kind"],
                category=m["category"],
                keywords=m["keywords"],
                keywords_vi=m.get("keywords_vi", []),
                valid_labels=m["valid_labels"],
                unit=m["unit"],
            )
        for key, m in raw.get("composites", {}).items():
            numerator = m["numerator"]
            self.specs[key] = MetricSpec(
                key=key,
                promql_name="",
                kind="composite",
                category=m["category"],
                keywords=m["keywords"],
                keywords_vi=m.get("keywords_vi", []),
                valid_labels=m["valid_labels"],
                unit=m["unit"],
                is_composite=True,
                numerator=numerator,
                numerator_filter=m.get("numerator_filter"),
                denominator=m["denominator"],
                is_expression_composite="(" in numerator,
            )

    def all_keywords(self):
        for spec in self.specs.values():
            for kw in spec.keywords:
                yield kw, spec
            for kw in spec.keywords_vi:
                yield kw, spec

    def match(self, query: str) -> tuple[Optional[MetricSpec], float]:
        """Returns (best_matching_spec, confidence 0..1)."""
        q = query.lower()

        best_spec, best_len = None, 0
        for kw, spec in self.all_keywords():
            if kw.lower() in q and len(kw) > best_len:
                best_spec, best_len = spec, len(kw)
        if best_spec is not None:
            return best_spec, 0.95

        all_kw = [kw for kw, _ in self.all_keywords()]
        matches = difflib.get_close_matches(q, all_kw, n=1, cutoff=0.4)
        if matches:
            for kw, spec in self.all_keywords():
                if kw == matches[0]:
                    ratio = difflib.SequenceMatcher(None, q, kw).ratio()
                    return spec, min(0.75, 0.4 + ratio)

        return None, 0.0
