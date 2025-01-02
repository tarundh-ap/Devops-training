1. Start a new pulumi project
  `pulumi new kubernetes-python`
2. Copy the content of this main.py to the main.py in the pulumi project folder
3. Run this in the terminal
  `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0-beta.0/deploy/static/provider/aws/deploy.yaml`
4. This will apply the ingress controller.
5. run `pulumi up`
6. The loadbalancer will be handled by the cloud provider, if using minikube on a local system, either use `minikube tunnel` to expose the loadbalancer ip or turn the loadbalancer type to nodeport using `kubectl edit` command.
