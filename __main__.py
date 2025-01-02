"""A Kubernetes Python Pulumi program"""

import pulumi
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Service, Namespace

#a custom namespace for testing purpose
namespace = Namespace("test-ns")
app_labels = { "app": "nginx" }

deployment = Deployment(
    "nginx-deployment",
    spec={
        "selector": { "matchLabels": app_labels },
        "replicas": 2,
        "template": {
            "metadata": { "labels": app_labels },
            "spec": {
                "containers": [{ "name": "nginx",
                                      "image": "nginx:latest",
                                      "ports": [{"containerPort": 80}],
                        }] 
                },
            },
        },
        metadata={
            "namespace": namespace.metadata["name"]
        }
    )

# Create a service
service  = Service(
    "nginx-service",
    spec={
        "selector": app_labels,
        "ports": [{"port": 80, "targetPort": 80, "protocol": "TCP"}],
        "type": "NodePort"
    },
    metadata={
        "namespace": namespace.metadata["name"]
    }
)
pulumi.export("name", deployment.metadata["name"])
# pulumi.export("service_ip", service.status.apply(lambda s: s.load_balancer.ingress[0].ip if s.load_balancer.ingress else None))
