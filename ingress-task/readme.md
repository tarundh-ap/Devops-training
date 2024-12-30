1. Used a one page bootstrap template and used nginx as the base image.
2. Deployed 3 replicas of using deployment.yaml
3. Exposed the nodes with a service name my-service
4. Created an ingress resource to configure the ingress controller 
5. Used the ingress controller used in AWS `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0-beta.0/deploy/static/provider/aws/deploy.yaml`
6. Edited the ingress-nginx-controller from a loadbalancer to a nodeport to access it.
