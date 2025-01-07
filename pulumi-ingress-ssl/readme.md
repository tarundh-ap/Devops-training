# Install MetallB
```
$ kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.9/config/manifests/metallb-native.yaml
```

### Verify MetallB Installation
```
$ kubectl -n metallb-system get pods
$ kubectl api-resources| grep metallb

# Install NGINX Ingress Controller with Helm
```

# Install nginx controller
```
$ helm pull oci://ghcr.io/nginxinc/charts/nginx-ingress --untar --version 0.17.1
$ cd nginx-ingress
$ kubectl apply -f crds
$ helm install nginx-ingress oci://ghcr.io/nginxinc/charts/nginx-ingress --version 0.17.1
$ cd nginx-ingress
$ kubectl apply -f crds
```


# tsl and ssl
 ```Generate tsl and ssl certificates and add it into the pulumi config```


# Do pulumi up

```
$ pulumi up
```

# Edit the ingress-nginx-controller to LoadBalancer service if it's already not, to connect with metalLB and get external IP from IP_address_pool
```
$ kubectl edit svc/ingress-nginx-controller -n ingress-nginx
```

# If on a minikube cluster, edit the ip address pool according to minikube ip or do a port forward to the ingress-nginx-controller
```
$ kubectl port-forward svc/ingress-nginx-controller 8080:443
```

# Map the localhost with domain name in /etc/hosts
```
echo "192.168.42.2       example.com" | sudo tee -a /etc/hosts > /dev/null
```
