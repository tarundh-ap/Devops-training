import pulumi
import pulumi_kubernetes
from pulumi_kubernetes.networking.v1 import Ingress
from pulumi_kubernetes.core.v1 import Secret, Service
from pulumi_kubernetes.apps.v1 import Deployment
import base64

def create_ingress_with_tls(name: str, namespace: str, service_name: str, host: str = 'mydomain.com', cert_pem: str = None, key_pem: str = None):
    if cert_pem and key_pem:
        secret = Secret(
            f"{name}-tls-secret",
            metadata={
                "name": f"{name}-tls-secret",
                "namespace": namespace,
            },
            data={
                "tls.crt": base64.b64encode(cert_pem.encode('utf-8')).decode('utf-8'),
                "tls.key": base64.b64encode(key_pem.encode('utf-8')).decode('utf-8'),
            },
            opts=pulumi.ResourceOptions(parent=None),
        )
    else:
        raise ValueError("You must provide the certificate and private key as strings.")

    ingress = Ingress(
        f"{name}-ingress",
        metadata={
            "name": f"{name}-ingress",
            "namespace": namespace,
        },
        spec={
            "rules": [{
                "host": host,
                "http": {
                    "paths": [{
                        "path": "/",
                        "pathType": "Prefix",
                        "backend": {
                            "service": {
                                "name": service_name,
                                "port": {
                                    "number": 80,
                                },
                            },
                        },
                    }],
                },
            }],
            "tls": [{
                "hosts": [host],
                "secretName": secret.metadata["name"],
            }],
        },
        opts=pulumi.ResourceOptions(parent=None),
    )

    return ingress, secret

def create_metallb(namespace: str, ip_range: str):
    config_map = pulumi_kubernetes.core.v1.ConfigMap(
        "metallb-config",
        metadata={
            "name": "config",
            "namespace": namespace,
        },
        data={
            "config": f"""
                address-pools:
                - name: default
                  protocol: layer2
                  addresses:
                  - {ip_range}
            """
        },
    )

    service = Service(
        "metallb-service",
        metadata={
            "name": "metallb-service",
            "namespace": namespace,
        },
        spec={
            "type": "LoadBalancer",
            "selector": {"app": "metallb-controller"},
            "ports": [{
                "protocol": "TCP",
                "port": 80,
                "targetPort": 80,
            }],
        },
    )

    return config_map, service
