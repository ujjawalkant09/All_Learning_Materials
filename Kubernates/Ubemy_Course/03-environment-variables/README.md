# Environment variables in Deployments + NodePort Services

This folder demonstrates setting container environment variables via the Deployment spec and exposing the app.

## Manifests

- deploy.yaml — Deployment deploy2
  - labels: app=deploy2, replicas: 2
  - container: sentientlabsolutions/learning_repo:2.0
  - env: APP_NAME=kubernetes-101
  - containerPort: 3000
- service.yaml — Service (NodePort) deploy2
  - selector: app=deploy2, port: 80 → targetPort: 3000, nodePort: 30080
- learn_sample.yaml — Service (NodePort) svc-learn
  - selector: app=deploy2, port: 3000 → targetPort: 3000, nodePort: 30080

## Apply

```sh
kubectl apply -f deploy.yaml
kubectl rollout status deploy/deploy2
kubectl get deploy,rs,pods -l app=deploy2 -o wide

# pick ONE service; both target the same pods but use different service ports
kubectl apply -f service.yaml        # 80 → 3000
# OR
kubectl apply -f learn_sample.yaml   # 3000 → 3000

kubectl get svc
```

## Verify the environment variable

```sh
# Grab a pod from the deployment and print APP_NAME
POD=$(kubectl get pod -l app=deploy2 -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it "$POD" -- sh -lc 'printenv APP_NAME'
```

## Test the service

- kind (30080 mapped to host)
  ```sh
  curl -i http://localhost:30080/
  ```
- Generic NodePort
  ```sh
  NODE_IP=$(kubectl get node -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
  curl -i http://$NODE_IP:30080/
  ```

## Cleanup

```sh
kubectl delete -f learn_sample.yaml --ignore-not-found
kubectl delete -f service.yaml --ignore-not-found
kubectl delete -f deploy.yaml --ignore-not-found
```
