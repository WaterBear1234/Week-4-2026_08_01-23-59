import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import MetricCatalog, run

CATALOG = MetricCatalog(os.path.join(os.path.dirname(__file__), "..", "glossary", "metrics.yaml"))


def test_node_cpu_counter_gets_rate_wrapped():
    r = run("What is the CPU usage on instance node-1 over the last 5 minutes?", CATALOG)
    assert r.metric_key == "cpu_usage"
    assert r.verified
    assert r.used_llm_fallback is False
    assert "rate(node_cpu_seconds_total" in r.promql


def test_hyphenated_name_does_not_false_match_service_keyword():
    r = run("How many times has pod checkout-service restarted in the last 1 hour", CATALOG)
    assert r.metric_key == "pod_restarts"
    assert r.verified
    assert 'service="' not in r.promql
    assert 'pod="checkout-service"' in r.promql


def test_group_by_does_not_get_treated_as_a_filter():
    r = run("Container CPU usage per pod in namespace default over the last 5 minutes", CATALOG)
    assert r.verified
    assert "by (pod)" in r.promql
    assert 'container="' not in r.promql  # "CPU" must not be captured as a container= value


def test_composite_error_rate_builds_ratio():
    r = run("What's the error rate for service payment-api over the past 10 minutes", CATALOG)
    assert r.metric_key == "http_error_rate"
    assert r.verified
    assert " / " in r.promql
    assert 'status=~"5.."' in r.promql


def test_expression_composite_substitutes_range():
    r = run("cpu utilization percentage over the last 2 minutes", CATALOG)
    assert r.metric_key == "cpu_utilization_pct"
    assert r.verified
    assert "[2m]" in r.promql
    assert "__RANGE__" not in r.promql


def test_gauge_metric_has_no_rate_wrapper():
    r = run("What is the disk usage on instance node-1", CATALOG)
    assert r.metric_key == "disk_usage"
    assert "rate(" not in r.promql


def test_unresolvable_filter_is_reported_not_silently_dropped():
    r = run("Show me the average memory available for deployment api-gateway in the last 15 minutes", CATALOG)
    # memory_available is a node-level gauge with no pod/deployment label at
    # all -- "for deployment X" can't be resolved for this metric. It must
    # show up as an issue, not silently vanish into an unfiltered query.
    assert r.metric_key == "memory_available"
    assert r.verified is False
    assert any("deployment" in issue and "api-gateway" in issue for issue in r.issues)


def test_unmatched_question_without_llm_reports_gracefully():
    r = run("asdkjaslkdj random gibberish not about monitoring at all", CATALOG)
    assert r.promql is None
    assert r.metric_key is None
