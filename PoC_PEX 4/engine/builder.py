
from .catalog import MetricSpec
from .k8s_graph import K8sGraph
from .nlu import ParsedQuery


def _label_selector(pairs: list) -> str:
    return "{" + ", ".join(pairs) + "}" if pairs else ""


def _resolve_filters(filters: dict, valid_labels: list, k8s_graph: K8sGraph | None):
    """
    Returns (selector_pairs, applied_label_keys, dropped_filters). Direct
    label matches (namespace=, node=, etc.) pass through unchanged. A
    `deployment=` or `service=` filter, when the metric only supports
    `pod=`, gets translated into a regex pod matcher using the k8s graph.
    Anything that can't be resolved at all is reported in `dropped_filters`
    rather than silently disappearing -- an unfiltered query that quietly
    ignores "for deployment X" is worse than one that says so.
    """
    pairs = []
    applied = []
    dropped = []

    for key, value in filters.items():
        if key in valid_labels:
            pairs.append(f'{key}="{value}"')
            applied.append(key)
            continue

        if key == "deployment" and "pod" in valid_labels:
            regex = k8s_graph.pod_regex_for_deployment(value) if k8s_graph else f"^{value}-.*"
            pairs.append(f'pod=~"{regex}"')
            applied.append("pod")
            continue

        if key == "service" and "pod" in valid_labels and k8s_graph:
            regex = k8s_graph.pod_regex_for_service(value)
            if regex:
                pairs.append(f'pod=~"{regex}"')
                applied.append("pod")
                continue

        dropped.append((key, value))

    return pairs, applied, dropped


def build(spec: MetricSpec, parsed: ParsedQuery, k8s_graph: K8sGraph | None = None):
    """Returns (promql, applied_label_keys, dropped_filters)."""
    pairs, applied, dropped = _resolve_filters(parsed.resource_filters, spec.valid_labels, k8s_graph)
    selector = _label_selector(pairs)

    if spec.is_composite:
        promql = _build_composite(spec, parsed, selector, pairs)
        return promql, applied, dropped

    if spec.kind == "counter":
        inner = f"rate({spec.promql_name}{selector}[{parsed.time_range}])"
    else:
        inner = f"{spec.promql_name}{selector}"

    agg = parsed.aggregation
    group_by = parsed.group_by

    if agg or group_by:
        agg_fn = agg or "sum"
        by_clause = f" by ({', '.join(group_by)})" if group_by else ""
        return f"{agg_fn}({inner}){by_clause}", applied, dropped

    return inner, applied, dropped


def _build_composite(spec: MetricSpec, parsed: ParsedQuery, selector: str, pairs: list) -> str:
    if spec.is_expression_composite:
        numerator = spec.numerator.replace("__RANGE__", parsed.time_range)
        denominator = spec.denominator.replace("__RANGE__", parsed.time_range)
        return f"{numerator} / {denominator}"

    num_selector = selector
    if spec.numerator_filter:
        inner_pairs = ", ".join(pairs)
        combined = ", ".join([p for p in [inner_pairs, spec.numerator_filter] if p])
        num_selector = "{" + combined + "}"

    numerator = f"sum(rate({spec.numerator}{num_selector}[{parsed.time_range}]))"
    denominator = f"sum(rate({spec.denominator}{selector}[{parsed.time_range}]))"
    return f"{numerator} / {denominator}"
