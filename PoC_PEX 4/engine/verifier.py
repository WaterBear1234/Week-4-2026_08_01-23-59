
from dataclasses import dataclass, field

from .catalog import MetricSpec


@dataclass
class VerifyResult:
    ok: bool
    issues: list = field(default_factory=list)


def _brackets_balanced(promql: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in promql:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack


def verify(promql: str, spec: MetricSpec | None, applied_labels: list, dropped_filters: list | None = None) -> VerifyResult:
    issues = []

    if not promql.strip():
        issues.append("empty query")
        return VerifyResult(ok=False, issues=issues)

    if not _brackets_balanced(promql):
        issues.append("unbalanced brackets/braces")

    if spec is not None:
        for label_key in applied_labels:
            if label_key not in spec.valid_labels:
                issues.append(f"label '{label_key}' is not valid for metric '{spec.key}'")

        if not spec.is_composite and spec.kind == "counter":
            if "rate(" not in promql and "irate(" not in promql and "increase(" not in promql:
                issues.append(f"counter metric '{spec.key}' queried without rate()/increase()")

        if not spec.is_composite and spec.promql_name not in promql:
            issues.append(f"expected metric name '{spec.promql_name}' not found in output")

    for key, value in (dropped_filters or []):
        issues.append(f"could not apply filter '{key}=\"{value}\"': not supported for this metric "
                       f"(dropped rather than silently ignored)")

    return VerifyResult(ok=(len(issues) == 0), issues=issues)
