import pulumi
import pulumi_kubernetes as k8s
from config_file import config_app

image = config_app["image"]
replicas = config_app["replicas"]

class WebApp:
    def __init__(self, name: str):
        labels = {"app.kubernetes.io/name": name}

        self.deployment = k8s.apps.v1.Deployment(
            f"{name}-deployment",
            metadata={"name": name},
            spec={
                "replicas": 1,
                "selector": {"matchLabels": labels},
                "template": {
                    "metadata": {"labels": labels},
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": image,
                                "command": [
                                    "/bin/sh",
                                    "-c",
                                    "echo 'welcome to my web app!' > /usr/share/nginx/html/index.html && nginx -g 'daemon off;'"
                                ]
                            }
                        ],
                        "dnsConfig": {"options": [{"name": "ndots", "value": "2"}]}
                    }
                }
            }
        )

        self.service = k8s.core.v1.Service(
            f"{name}-service",
            metadata={"name": name},
            spec={
                "selector": labels,
                "ports": [{"name": "http", "protocol": "TCP", "port": 80, "targetPort": 80}],
                "type": "ClusterIP"
            }
        )
