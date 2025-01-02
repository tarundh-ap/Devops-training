import pulumi
from pulumi_kubernetes.apps.v1 import Deployment
from pulumi_kubernetes.core.v1 import Service
from pulumi_kubernetes.networking.v1 import Ingress, IngressSpecArgs, IngressRuleArgs, HTTPIngressRuleValueArgs, HTTPIngressPathArgs
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs


class NginxApp(pulumi.ComponentResource):
    def __init__(self, name: str, args, opts=None):
        super().__init__('custom:resource:NginxApp', name, None, opts)

        self.deployment = Deployment(
            f"{name}-deployment",
            metadata=ObjectMetaArgs(
                name=f"{name}-deployment",
                labels={"app": name}
            ),
            spec={
                "replicas": args.replicas,
                "selector": {
                    "matchLabels": {
                        "app": name,
                    },
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name,
                        },
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "nginx",
                                "image": args.image,
                                "ports": [
                                    {"containerPort": args.container_port}
                                ],
                            },
                        ],
                    },
                },
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.service = Service(
            f"{name}-service",
            metadata=ObjectMetaArgs(
                name=f"{name}-service"
            ),
            spec={
                "selector": {
                    "app": name,
                },
                "ports": [
                    {
                        "protocol": "TCP",
                        "port": args.service_port,
                        "targetPort": args.container_port,
                    }
                ],
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.ingress = Ingress(
            f"{name}-ingress",
            metadata=ObjectMetaArgs(
                name=f"{name}-ingress",
                annotations={
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                    "nginx.ingress.kubernetes.io/use-regex": "true",
                }
            ),
            spec=IngressSpecArgs(
                ingress_class_name="nginx",
                rules=[
                    IngressRuleArgs(
                        host=args.host,
                        http=HTTPIngressRuleValueArgs(
                            paths=[
                                HTTPIngressPathArgs(
                                    path="/",
                                    path_type="Prefix",
                                    backend={
                                        "service": {
                                            "name": self.service.metadata.name,
                                            "port": {
                                                "number": args.service_port
                                            }
                                        }
                                    }
                                )
                            ]
                        )
                    )
                ]
            ),
            opts=pulumi.ResourceOptions(parent=self)
        )


        self.register_outputs({
            "deployment": self.deployment,
            "service": self.service,
            "ingress": self.ingress,
        })


class NginxAppArgs:
    def __init__(self, replicas: int, image: str, container_port: int, service_port: int, host: str, ingress_annotations: dict):
        self.replicas = replicas
        self.image = image
        self.container_port = container_port
        self.service_port = service_port
        self.host = host
        self.ingress_annotations = ingress_annotations

app_args = NginxAppArgs(
    replicas=3,
    image="tarunapp/ingress-task:latest",
    container_port=80,
    service_port=80,
    host="example.com",
    ingress_annotations={
        "nginx.ingress.kubernetes.io/rewrite-target": "/"
    }
)

nginx_app = NginxApp("nginx-app", app_args)
