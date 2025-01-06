import pulumi
from app import WebApp
from network import NetworkConfig
from config_file import config_app

config = pulumi.Config()

app_name = config_app["name"]
tls_cert = config.get_secret("tls_cert")
tls_key = config.get_secret("tls_key")

web_app = WebApp(app_name)
network = NetworkConfig("network",cert_file=tls_cert,key_file=tls_key)

pulumi.export("service_name", web_app.service.metadata["name"])
