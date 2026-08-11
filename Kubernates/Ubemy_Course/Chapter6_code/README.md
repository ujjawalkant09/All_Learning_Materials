# Chapter 6 — Pods and a simple Deployment

This folder contains a couple of bare Pods and a minimal Deployment to practice fundamentals.

## What’s here

- pod.yml — Pod named nginx-pod-2
  - labels: env=test
  - container: nginx:latest
- pod3.yml — Pod named nginx-3
  - labels: run=nginx-34
  - restartPolicy: Always (default)
- deploy.yaml — Deployment named sample
  - labels: app=sample
  - replicas: 1
  - container: nginx (latest by default)

## Try it out

Apply Pods one by one:

```sh
kubectl apply -f pod.yml
kubectl apply -f pod3.yml
kubectl get pods -o wide
```

Inspect and test:

```sh
# Logs and shell (pick one of the running pod names)
kubectl logs nginx-pod-2
kubectl exec -it nginx-pod-2 -- sh -lc 'nginx -v || cat /etc/os-release'
```

Apply the Deployment and watch rollout:

```sh
kubectl apply -f deploy.yaml
kubectl rollout status deploy/sample
kubectl get deploy,rs,pods -l app=sample -o wide
```

Optional port-forward to a Pod (since no Service is defined here):

```sh
# forward any sample-labeled pod to localhost:8080 for quick testing
POD=$(kubectl get pod -l app=sample -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward pod/$POD 8080:80
# then in another terminal
curl -I localhost:8080
```

Cleanup when done:

```sh
kubectl delete -f deploy.yaml || true
kubectl delete -f pod3.yml || true
kubectl delete -f pod.yml || true
```

Notes
- The nested deploy/ subfolder demonstrates multiple Service types for an Nginx Deployment. See deploy/README.md for details.
