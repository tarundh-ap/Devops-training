import pulumi
import pulumi_kubernetes as k8s
from config_file import config_net
import base64

host = config_net["host"]
addresses = config_net["pool-add"]

class NetworkConfig:
    def __init__(self, name: str, cert_file: any, key_file: any):

        # with open(cert_file, 'r') as cert:
        #     tls_cert = cert.read()
        # with open(key_file, 'r') as key:
        #     tls_key = key.read()

        # tls_cert = base64.b64encode(tls_cert.encode()).decode('utf-8')
        # tls_key = base64.b64encode(tls_key.encode()).decode('utf-8')
        tls_cert = cert_file
        tls_key = key_file


        self.tls_secret = k8s.core.v1.Secret(
            f"{name}-tls-secret",
            metadata={
                "name": "web-app-tls",
                "namespace": "default", 
            },
            type="kubernetes.io/tls",
            data={
                "tls.crt": pulumi.Output.secret(tls_cert),
                "tls.key": pulumi.Output.secret(tls_key),
            }
        )

        self.ip_pool = k8s.apiextensions.CustomResource(
            f"{name}-ip-pool",
            api_version="metallb.io/v1beta1",
            kind="IPAddressPool",
            metadata={
                "name": "first-pool",
                "namespace": "metallb-system"
            },
            spec={
                "addresses": ["172.20.0.120-172.20.0.130"]
            }
        )

        self.l2_advertisement = k8s.apiextensions.CustomResource(
            f"{name}-l2-advertisement",
            api_version="metallb.io/v1beta1",
            kind="L2Advertisement",
            metadata={
                "name": "homelab-l2",
                "namespace": "metallb-system"
            },
            spec={
                "ipAddressPools": ["first-pool"]
            }
        )

        self.ingress = k8s.networking.v1.Ingress(
            f"{name}-ingress",
            metadata={
                "name": "web-app",
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    # "nginx.ingress.kubernetes.io/rewrite-target": "/",
                }
            },
            spec={
                "ingressClassName": "nginx",
                "rules": [
                    {
                        "host": host,
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "web-app",
                                            "port": {"number": 80}
                                        }
                                    }
                                },
                                # {
                                #     "path": "/monitor",
                                #     "pathType": "Prefix",
                                #     "backend":{
                                #         "service":{
                                #             "name": "grafana",
                                #             "namespace": "monitoring",
                                #             "port": {"number": 3000},
                                #         }
                                #     }
                                # }
                            ]
                        }
                    }
                ],
                "tls": [
                    {
                        "hosts": [host],
                        "secretName": self.tls_secret.metadata["name"],
                    }
                ]
            }
        )

        grafana_ingress = k8s.networking.v1.Ingress(
            f"{name}-grafana-ingress",
            metadata={
                "name": "grafana-ingress",
                "namespace": "monitoring",
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    # "nginx.ingress.kubernetes.io/rewrite-target": "/"
                }
            },
            spec={
                "ingressClassName": "nginx",
                "rules": [
                    {
                        "host": host, 
                        "http": {
                            "paths": [
                                {
                                    "path": "/monitor", 
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {
                                            "name": "grafana",
                                            "port": {"number": 3000},
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ],
                "tls": [
                    {
                        "hosts": [host],
                        "secretName": self.tls_secret.metadata["name"],
                    }
                ]
            }
        )
