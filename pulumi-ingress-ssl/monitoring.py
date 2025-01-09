import pulumi
import pulumi_kubernetes as k8s
from config_file import config_net
from grafana_loki import LokiAndPromtail

host = config_net["host"]
class MonitoringComponent(pulumi.ComponentResource):
    def __init__(self, name: str, opts: pulumi.ResourceOptions = None):
        super().__init__('my:monitoring:MonitoringComponent', name, {}, opts)

        prometheus_config_map = k8s.core.v1.ConfigMap(
    f"{name}-prometheus-config",
    metadata={'name': "prometheus-server", 'namespace': "monitoring"},
    data={
        "prometheus.yml": """
        scrape_configs:
        - job_name: 'nginx-ingress-controller'
          metrics_path: '/metrics'
          static_configs:
            - targets: ['ingress-nginx-controller.ingress-nginx.svc:10254']

        - job_name: 'node-exporter'
          static_configs:
            - targets: ['node-exporter.monitoring.svc:9100']
        """
    },
    opts=pulumi.ResourceOptions(parent=self)
)


        prometheus_deployment = k8s.apps.v1.Deployment(
            f"{name}-prometheus-deployment",
            metadata={'name': "prometheus", 'namespace': "monitoring"},
            spec={
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": "prometheus"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "prometheus"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "prometheus",
                            "image": "prom/prometheus:v2.31.0",
                            "args" : ["--config.file=/etc/prometheus/prometheus.yml"],
                            "ports": [{"containerPort": 9090}],
                            "volumeMounts": [{
                                "name": "prometheus-config",
                                "mountPath": "/etc/prometheus/prometheus.yml",
                                "subPath": "prometheus.yml"
                            }]
                        }],
                        "volumes": [{
                            "name": "prometheus-config",
                            "configMap": {
                                "name": "prometheus-server"
                            }
                        }]
                    }
                }
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        prometheus_service = k8s.core.v1.Service(
            f"{name}-prometheus-service",
            metadata={'name': "prometheus-pul", 'namespace': "monitoring"},
            spec={
                'ports': [{
                    'port': 9090,
                    'targetPort': 9090,
                    'protocol': "TCP",
                    'name': "http"
                }],
                'selector': {"app": "prometheus"},
                'type': "ClusterIP"
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        grafana_deployment = k8s.apps.v1.Deployment(
            f"{name}-grafana-deployment",
            metadata={'name': "grafana", 'namespace': "monitoring"},
            spec={
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": "grafana"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "grafana"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "grafana",
                            "image": "grafana/grafana:latest",
                            "ports": [{"containerPort": 3000}],
                            "env": [
                                {
                                    "name": "GF_SERVER_ROOT_URL",
                                    "value": "https://example.com:8080/monitor/"
                                },
                                {
                                    "name": "GF_SERVER_SERVE_FROM_SUB_PATH",
                                    "value": "true"
                                },
                            #     # {
                            #     #     "name": "GF_AUTH_DISABLE_LOGIN_FORM",
                            #     #     "value": "true"
                            #     # }

                            ]
                        }]
                    }
                }
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        grafana_service = k8s.core.v1.Service(
            f"{name}-grafana-service",
            metadata={'name': "grafana", 'namespace': "monitoring"},
            spec={
                'ports': [{
                    'port': 3000,
                    'targetPort': 3000,
                    'protocol': "TCP",
                    'name': "http"
                }],
                'selector': {"app": "grafana"},
                'type': "ClusterIP"
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        node_exporter_daemonset = k8s.apps.v1.DaemonSet(
            f"{name}-node-exporter",
            metadata={'name': "node-exporter", 'namespace': "monitoring"},
            spec={
                "selector": {
                    "matchLabels": {"app": "node-exporter"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "node-exporter"}
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "node-exporter",
                                "image": "prom/node-exporter:latest",
                                "ports": [
                                    {"containerPort": 9100,
                                     "name": "metrics", 
                                     "protocol": "TCP"}
                                ],
                                "resources": {
                                    "requests": {"cpu": "50m", "memory": "50Mi"},
                                    "limits": {"cpu": "100m", "memory": "100Mi"}
                                },
                                "volumeMounts": [
                                    {"name": "proc", "mountPath": "/host/proc", "readOnly": True},
                                    {"name": "sys", "mountPath": "/host/sys", "readOnly": True},
                                    {"name": "root", "mountPath": "/host/root", "readOnly": True}
                                ]
                            }
                        ],
                        "volumes": [
                            {"name": "proc", "hostPath": {"path": "/proc", "type": "Directory"}},
                            {"name": "sys", "hostPath": {"path": "/sys", "type": "Directory"}},
                            {"name": "root", "hostPath": {"path": "/", "type": "Directory"}}
                        ],
                        # "hostNetwork": True,
                        "tolerations": [
                            {
                                "key": "node.kubernetes.io/not-ready",
                                "operator": "Exists",
                                "effect": "NoSchedule"
                            },
                            {
                                "key": "node.kubernetes.io/unreachable",
                                "operator": "Exists",
                                "effect": "NoSchedule"
                            }
                        ]
                    }
                }
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        node_exporter_service = k8s.core.v1.Service(
            f"{name}-node-exporter-service",
            metadata={'name': "node-exporter", 'namespace': "monitoring"},
            spec={

                "ports": [{"port": 9100,
                           "targetPort": 9100,
                           "name": "metrics"}],
                "selector": {"app": "node-exporter"},
                "type": "ClusterIP"
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        grafana_loki = LokiAndPromtail(name=name)
