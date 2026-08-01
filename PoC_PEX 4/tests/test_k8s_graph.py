import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.k8s_graph import K8sGraph

# A small fixture cluster: one namespace, one deployment ("checkout-service")
# owning two pods, one service selecting the same pods, two nodes.
PODS = [
    {"name": "checkout-service-7d9f5-abcde", "namespace": "default", "node": "node-1",
     "owner_deployment": "checkout-service", "labels": {"app": "checkout-service"}},
    {"name": "checkout-service-7d9f5-fghij", "namespace": "default", "node": "node-2",
     "owner_deployment": "checkout-service", "labels": {"app": "checkout-service"}},
    {"name": "payment-api-abc12-klmno", "namespace": "default", "node": "node-1",
     "owner_deployment": "payment-api", "labels": {"app": "payment-api"}},
]
DEPLOYMENTS = [
    {"name": "checkout-service", "namespace": "default"},
    {"name": "payment-api", "namespace": "default"},
]
SERVICES = [
    {"name": "checkout-service", "namespace": "default", "selector": {"app": "checkout-service"}},
]
NODES = ["node-1", "node-2"]


def build_fixture_graph() -> K8sGraph:
    g = K8sGraph()
    g.build_from_snapshot(PODS, DEPLOYMENTS, SERVICES, NODES)
    return g


def test_deployment_resolves_to_exact_pod_names():
    g = build_fixture_graph()
    regex = g.pod_regex_for_deployment("checkout-service")
    assert "checkout-service-7d9f5-abcde" in regex
    assert "checkout-service-7d9f5-fghij" in regex
    assert "payment-api-abc12-klmno" not in regex


def test_service_resolves_to_selected_pod_names():
    g = build_fixture_graph()
    regex = g.pod_regex_for_service("checkout-service")
    assert "checkout-service-7d9f5-abcde" in regex
    assert "checkout-service-7d9f5-fghij" in regex


def test_unknown_deployment_falls_back_to_naming_convention():
    g = build_fixture_graph()
    regex = g.pod_regex_for_deployment("scaled-to-zero-deploy")
    assert regex == "^scaled-to-zero-deploy-.*"


def test_resource_type_of_distinguishes_pod_deployment_service():
    g = build_fixture_graph()
    assert g.resource_type_of("checkout-service") == "deployment"  # deployment name wins over same-named service
    assert g.resource_type_of("checkout-service-7d9f5-abcde") == "pod"
    assert g.resource_type_of("node-1") == "node"
    assert g.resource_type_of("default") == "namespace"
    assert g.resource_type_of("does-not-exist") is None


def test_namespace_of_resolves_across_resource_types():
    g = build_fixture_graph()
    assert g.namespace_of("checkout-service-7d9f5-abcde") == "default"
    assert g.namespace_of("payment-api") == "default"
