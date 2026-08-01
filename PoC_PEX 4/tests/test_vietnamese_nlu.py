import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine import MetricCatalog, run
from engine.k8s_graph import K8sGraph
from engine.nlu import parse

CATALOG = MetricCatalog(os.path.join(os.path.dirname(__file__), "..", "glossary", "metrics.yaml"))

PODS = [
    {"name": "checkout-service-7d9f5-abcde", "namespace": "default", "node": "node-1",
     "owner_deployment": "checkout-service", "labels": {"app": "checkout-service"}},
    {"name": "checkout-service-7d9f5-fghij", "namespace": "default", "node": "node-2",
     "owner_deployment": "checkout-service", "labels": {"app": "checkout-service"}},
]
DEPLOYMENTS = [{"name": "checkout-service", "namespace": "default"}]


def build_fixture_graph() -> K8sGraph:
    g = K8sGraph()
    g.build_from_snapshot(PODS, DEPLOYMENTS, [], ["node-1", "node-2"])
    return g


def test_language_detection_flags_vietnamese_diacritics():
    assert parse("sử dụng cpu trên instance node-1 trong 5 phút qua").language == "vi"
    assert parse("cpu usage on instance node-1 over the last 5 minutes").language == "en"


def test_vietnamese_time_range_minutes():
    p = parse("bộ nhớ khả dụng trên instance node-1 trong 5 phút qua")
    assert p.time_range == "5m"


def test_vietnamese_time_range_hours():
    p = parse("số lần khởi động lại của pod checkout-service trong 1 giờ trước")
    assert p.time_range == "1h"


def test_vietnamese_aggregation_average():
    p = parse("trung bình sử dụng bộ nhớ container của pod checkout-service")
    assert p.aggregation == "avg"


def test_vietnamese_aggregation_max():
    p = parse("mức sử dụng cpu tối đa trên instance node-1")
    assert p.aggregation == "max"


def test_vietnamese_end_to_end_cpu_query():
    r = run("Cho tôi biết mức sử dụng cpu trên instance node-1 trong 5 phút qua", CATALOG)
    assert r.metric_key == "cpu_usage"
    assert r.verified
    assert r.promql == 'rate(node_cpu_seconds_total{instance="node-1"}[5m])'


def test_vietnamese_end_to_end_restart_query():
    r = run("Pod checkout-service đã khởi động lại bao nhiêu lần trong 1 giờ trước", CATALOG)
    assert r.metric_key == "pod_restarts"
    assert r.verified
    assert 'pod="checkout-service"' in r.promql
    assert "[1h]" in r.promql


def test_vietnamese_end_to_end_error_rate_query():
    r = run("Tỷ lệ lỗi của service payment-api trong 10 phút qua là bao nhiêu", CATALOG)
    assert r.metric_key == "http_error_rate"
    assert r.verified
    assert " / " in r.promql
    assert "[10m]" in r.promql


def test_vietnamese_disk_space_query():
    r = run("Dung lượng ổ đĩa còn trống trên instance node-1", CATALOG)
    assert r.metric_key == "disk_usage"
    assert 'instance="node-1"' in r.promql


def test_vietnamese_deployment_query_resolved_via_k8s_graph():
    # container_cpu_usage's valid_labels don't include 'deployment' -- only
    # the live k8s graph (or its naming-convention fallback) can translate
    # "deployment checkout-service" into a pod=~"..." matcher.
    graph = build_fixture_graph()
    r = run("CPU của container cho deployment checkout-service trong 5 phút qua", CATALOG, k8s_graph=graph)
    assert r.metric_key == "container_cpu_usage"
    assert r.verified
    assert "checkout-service-7d9f5-abcde" in r.promql
    assert "checkout-service-7d9f5-fghij" in r.promql
