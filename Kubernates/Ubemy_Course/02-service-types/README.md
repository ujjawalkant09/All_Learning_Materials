# Deployments + Service variants (sample app)

This folder deploys a sample nginx-backed app and exposes it with different Service types.

## Manifests

- deploy.yaml — Deployment sample
  - labels: app=sample, replicas: 3, containerPort: 80
- deploy_cluster_ip.yaml — Service (ClusterIP) nginx-clusterip
  - selector: app=sample, port 80 → targetPort 80
- nodeport_deploy.yaml — Service (NodePort) nginx-nodeport
  - selector: app=sample, port 80 → targetPort 80, nodePort 30080
- load_balancer_service.yaml — Service (LoadBalancer) nginx-loadbalancer
  - selector: app=sample, port 80
- svc.yaml — Example output of an in-cluster ClusterIP Service (captured via `kubectl get svc sample -o yaml`)

## Apply

```sh
# 1) Workload
kubectl apply -f deploy.yaml
kubectl rollout status deploy/sample
kubectl get deploy,rs,pods -l app=sample -o wide

# 2) Choose ONE service flavor
kubectl apply -f deploy_cluster_ip.yaml   # ClusterIP
# OR
kubectl apply -f nodeport_deploy.yaml     # NodePort
# OR
kubectl apply -f load_balancer_service.yaml  # LoadBalancer

kubectl get svc
```

## Test

- ClusterIP
  ```sh
  kubectl port-forward svc/nginx-clusterip 8080:80
  curl -I http://localhost:8080/
  ```
- NodePort (kind port 30080 is mapped to host 30080 per Extras)
  ```sh
  curl -I http://localhost:30080/
  ```
- LoadBalancer
  ```sh
  kubectl get svc nginx-loadbalancer -w   # wait for EXTERNAL-IP then curl it
  ```

## Cleanup

```sh
kubectl delete -f load_balancer_service.yaml --ignore-not-found
kubectl delete -f nodeport_deploy.yaml --ignore-not-found
kubectl delete -f deploy_cluster_ip.yaml --ignore-not-found
kubectl delete -f deploy.yaml --ignore-not-found
```
