
from .k8s_graph import K8sGraph


def _load_k8s_client():
    from kubernetes import client, config
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    return client.CoreV1Api(), client.AppsV1Api()


def fetch_snapshot(namespace: str | None = None):
    """
    Returns (pods, deployments, services, node_names) in the plain-dict
    shape K8sGraph.build_from_snapshot expects. `namespace=None` fetches
    cluster-wide.
    """
    core, apps = _load_k8s_client()

    pod_list = core.list_namespaced_pod(namespace) if namespace else core.list_pod_for_all_namespaces()
    pods = []
    for p in pod_list.items:
        owner_deployment = None
        for owner in (p.metadata.owner_references or []):
            if owner.kind == "ReplicaSet":
                # ReplicaSet names are "<deployment>-<hash>"; strip the hash suffix
                owner_deployment = "-".join(owner.name.split("-")[:-1]) or owner.name
        pods.append({
            "name": p.metadata.name,
            "namespace": p.metadata.namespace,
            "node": p.spec.node_name,
            "owner_deployment": owner_deployment,
            "labels": dict(p.metadata.labels or {}),
        })

    dep_list = apps.list_namespaced_deployment(namespace) if namespace else apps.list_deployment_for_all_namespaces()
    deployments = [{"name": d.metadata.name, "namespace": d.metadata.namespace} for d in dep_list.items]

    svc_list = core.list_namespaced_service(namespace) if namespace else core.list_service_for_all_namespaces()
    services = [
        {"name": s.metadata.name, "namespace": s.metadata.namespace, "selector": dict(s.spec.selector or {})}
        for s in svc_list.items
    ]

    node_list = core.list_node()
    node_names = [n.metadata.name for n in node_list.items]

    return pods, deployments, services, node_names


def build_live_graph(namespace: str | None = None) -> K8sGraph:
    pods, deployments, services, node_names = fetch_snapshot(namespace)
    graph = K8sGraph()
    graph.build_from_snapshot(pods, deployments, services, node_names)
    return graph


class RefreshingK8sGraph:
    """
    Thin TTL cache around build_live_graph() so the API doesn't hit the
    k8s API server on every single request -- refreshes at most once per
    `ttl_seconds`, serves the cached graph in between.
    """
    def __init__(self, namespace: str | None = None, ttl_seconds: float = 30.0):
        self.namespace = namespace
        self.ttl_seconds = ttl_seconds
        self._graph: K8sGraph | None = None
        self._fetched_at: float = 0.0

    def get(self) -> K8sGraph:
        import time
        now = time.time()
        if self._graph is None or (now - self._fetched_at) > self.ttl_seconds:
            self._graph = build_live_graph(self.namespace)
            self._fetched_at = now
        return self._graph
