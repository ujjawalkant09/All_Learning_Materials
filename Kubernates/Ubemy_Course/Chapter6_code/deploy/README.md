# Nginx Deployment + Service types

This subfolder shows a standard Nginx Deployment exposed via different Service types.

## Manifests

- deploy.yaml — Deployment nginx-deployment
  - labels: app=nginx
  - replicas: 3
  - container: nginx:latest, containerPort: 80
- clusterIP.yaml — Service (ClusterIP) nginx-clusterip
  - selector: app=nginx
  - ports: 80 → targetPort 80 (implicit when omitted)
- service.yaml — Service (NodePort) nginx-nodeport
  - selector: app=nginx
  - ports: 80 → targetPort 80, nodePort: 30080
- lb.yaml — Service (LoadBalancer) nginx-lb
  - selector: app=nginx
  - ports: 80 (cloud LB assigns external IP)

## Apply

```sh
# 1) Deploy the workload
kubectl apply -f deploy.yaml
kubectl rollout status deploy/nginx-deployment
kubectl get deploy,rs,pods -l app=nginx -o wide

# 2) Pick ONE service type to expose
# ClusterIP (inside cluster or via port-forward)
kubectl apply -f clusterIP.yaml
# OR NodePort (nodeIP:nodePort)
kubectl apply -f service.yaml
# OR LoadBalancer (external IP if your cluster supports it)
kubectl apply -f lb.yaml

kubectl get svc
```

## Test

- ClusterIP
  ```sh
  kubectl port-forward svc/nginx-clusterip 8080:80
  # in another terminal
  curl -I http://localhost:8080/
  ```

- NodePort (kind mapping in Extras/kind-cluster-deply.yml exposes 30080 → host 30080)
  ```sh
  # substitute the node IP if not using kind + port mapping
  curl -I http://localhost:30080/
  ```

- LoadBalancer
  ```sh
  # wait for EXTERNAL-IP then curl it
  kubectl get svc nginx-lb -w
  ```

## Switching service types

Services are different objects. If you re-use the same name, delete the old one first:

```sh
kubectl delete svc/nginx-nodeport || true
kubectl delete svc/nginx-clusterip || true
kubectl delete svc/nginx-lb || true
```

## Cleanup

```sh
kubectl delete -f lb.yaml --ignore-not-found
kubectl delete -f service.yaml --ignore-not-found
kubectl delete -f clusterIP.yaml --ignore-not-found
kubectl delete -f deploy.yaml --ignore-not-found
```
