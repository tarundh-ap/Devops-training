config_app = {
    "name": "web-app",
    "replicas": 1,
    "image": "nginx"
}

config_net = {
    "host": "example.com",
    "image": "nginx",
    "pool-add": ["172.20.0.120-172.20.0.130"]
}