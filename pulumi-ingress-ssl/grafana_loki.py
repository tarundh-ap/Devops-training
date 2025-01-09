import pulumi
import pulumi_kubernetes as k8s

class LokiAndPromtail(pulumi.ComponentResource):
    def __init__(self, name: str, opts: pulumi.ResourceOptions = None):
        super().__init__('my:monitoring:LokiAndPromtail', name, {}, opts)

        loki_config = k8s.core.v1.ConfigMap(
    "lokiConfig",
    metadata={
        "name": "loki-config",
        "namespace": "monitoring",
    },
    data={
        "loki-config.yaml": """  # Change the key to match the expected filename
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 127.0.0.1
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

        """
    },
)

        loki_deploy = k8s.apps.v1.Deployment(
            "lokideploy",
            metadata={
                "name": "loki",
                "namespace": "monitoring",
            },
            spec={
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "loki",
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "loki",
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "loki",
                                "image": "grafana/loki:3.0.0",
                                "ports": [
                                    {"containerPort": 3100, "name": "http"},
                                ],
                                "args": ["-config.file=/etc/loki/loki-config.yaml"],
                                "volumeMounts": [
                                    {
                                        "name": "config",
                                        "mountPath": "/etc/loki",  
                                    },
                                ],
                            }
                        ],
                        "volumes": [
                            {
                                "name": "config",
                                "configMap": {
                                    "name": "loki-config", 
                                },
                            }
                        ],
                    },
                },
            },
        )



        loki_service = k8s.core.v1.Service(
            f"{name}-loki-service",
            metadata={"name": "loki", "namespace": "monitoring"},
            spec={
                "ports": [{"port": 3100, "targetPort": 3100, "protocol": "TCP"}],
                "selector": {"app": "loki"},
                "type": "ClusterIP",
            },
            opts=pulumi.ResourceOptions(parent=self),
        )

        promtail_service_account = k8s.core.v1.ServiceAccount(
            "promtail-service-account",
            metadata={
                "name": "promtail",
                "namespace": "monitoring"
            }
        )

        cluster_role = k8s.rbac.v1.ClusterRole(
            "promtail-cluster-role",
            rules=[
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get","list","watch"]
                }
            ]
        )

        cluster_role_binding = k8s.rbac.v1.ClusterRoleBinding(
    "promtail-cluster-role-binding",
    metadata={
        "name": "promtail-cluster-role-binding"
    },
    role_ref={
        "api_group": "rbac.authorization.k8s.io",
        "kind": "ClusterRole",
        "name": cluster_role.metadata["name"]
    },
    subjects=[{
        "kind": "ServiceAccount",
        "name": promtail_service_account.metadata["name"],
        "namespace": "monitoring"
    }]
)


        promtail_config_map = k8s.core.v1.ConfigMap(
            f"{name}-promtail-config",
            metadata={"name": "promtail-config", "namespace": "monitoring"},
            data={
                "promtail-config.yaml": """
server:
  http_listen_port: 9080
  grpc_listen_port: 0
  log_level: debug

clients:
  - url: http://loki.monitoring.svc:3100/loki/api/v1/push

positions:
  filename: /tmp/positions.yaml

scrape_configs:
  - job_name: 'application-logs'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: web-app
    
  - job_name: 'nginx-ingress-logs'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: ingress-nginx-controller

"""
            },
            opts=pulumi.ResourceOptions(parent=self),
        )

        promtail_daemonset = k8s.apps.v1.DaemonSet(
            f"{name}-promtail",
            metadata={"name": "promtail", "namespace": "monitoring"},
            spec={
                "selector": {"matchLabels": {"app": "promtail"}},
                "template": {
                    "metadata": {"labels": {"app": "promtail"}},
                    "spec": {
                        "serviceAccountName": promtail_service_account.metadata["name"],
                        "containers": [
                            {
                                "name": "promtail",
                                "image": "grafana/promtail:2.9.0",
                                "args": ["-config.file=/etc/promtail/promtail-config.yaml"],
                                "ports": [{"containerPort": 9080}],
                                "volumeMounts": [
                                    {"name": "config", "mountPath": "/etc/promtail"},
                                    {"name": "varlog", "mountPath": "/var/log"},
                                    {"name": "positions", "mountPath": "/tmp"},
                                ],
                            }
                        ],
                        "volumes": [
                            {"name": "config", "configMap": {"name": "promtail-config"}},
                            {"name": "varlog", "hostPath": {"path": "/var/log"}},
                            {"name": "positions", "emptyDir": {}},
                        ],
                    },
                },
            },
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({})
