import pulumi
import pulumi_kubernetes as k8s

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
                            "ports": [{"containerPort": 3000}]
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
