import pulumi
from app import AppResource
from pulumi import Config
from network import create_ingress_with_tls, create_metallb

app = AppResource()

config = Config()
namespace = config.get("namespace") or "default"
name = config.get("name") or "my-app" 
service_name = app.service.metadata["name"]

with open('certificate.crt', 'r') as cert_file:
    certificate = cert_file.read()

with open('private_key.pem', 'r') as key_file:
    private_key = key_file.read()

ingress, secret = create_ingress_with_tls(name, namespace, service_name, cert_pem=certificate, key_pem=private_key)

ip_range = "192.168.49.240-192.168.49.250"  
metallb_config, metallb_service = create_metallb(namespace, ip_range)


pulumi.export("service_name", service_name)
pulumi.export("deployment_name", app.deployment.metadata["name"])
pulumi.export("ingress_name", ingress.metadata["name"])
pulumi.export("tls_secret_name", secret.metadata["name"])
