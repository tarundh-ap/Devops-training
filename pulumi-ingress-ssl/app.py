import pulumi
from pulumi_kubernetes import Provider
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Service
from config import config_val as config

k8s_provider = Provider("k8s-provider")

class AppResource(pulumi.ComponentResource):
    def __init__(self, opts=None):
        super().__init__('custom:resource:AppResource', config["name"], {}, opts)

        name = config["name"]
        namespace = config["namespace"]
        image = config["image"]
        replicas = config["replicas"]
        ports = config["ports"]

   
        app_labels = {"app": name}


        self.deployment = Deployment(
            f"{name}-deployment",
            metadata={
                "name": name,
                "namespace": namespace,
            },
            spec={
                "replicas": replicas,
                "selector": {"matchLabels": app_labels},
                "template": {
                    "metadata": {"labels": app_labels},
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": image,
                            "ports": [{"containerPort": p} for p in ports],
                        }],
                    },
                },
            },
            opts=pulumi.ResourceOptions(parent=self, provider=k8s_provider),
        )

        self.service = Service(
            f"{name}-service",
            metadata={
                "name": f"{name}-service",
                "namespace": namespace,
            },
            spec={
                "selector": app_labels,
                "ports": [{"port": p, "targetPort": p} for p in ports],
                "type": "ClusterIP", 
            },
            opts=pulumi.ResourceOptions(parent=self, provider=k8s_provider),
        )

        self.register_outputs({
            "deployment_name": self.deployment.metadata["name"],
            "service_name": self.service.metadata["name"],
        })
