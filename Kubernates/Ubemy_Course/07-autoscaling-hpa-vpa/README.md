# Kubernetes autoscaling (HPA) with a sample app — plus Metrics Server setup

This folder helps you learn how Horizontal Pod Autoscaler (HPA) works end‑to‑end using a simple HTTP app. You’ll:
- Install and verify Metrics Server (HPA depends on it)
- Deploy a sample app with resource requests/limits
- Expose it via a Service
- Create an HPA and watch it scale up/down under load

Note: VPA (Vertical Pod Autoscaler) is explained at a high level near the end, but manifests here focus on HPA.

## What’s in this folder
- deployments.yaml — A Deployment with 2 replicas of the sample app, including CPU requests/limits (required for HPA on CPU).
- service_for_deployment.yaml — NodePort Service exposing the Deployment on port 80 (targetPort 3000) at nodePort 30080.
- pod.yaml — A single Pod version of the same app (handy for quick tests).
- service.yaml — NodePort Service targeting the standalone Pod (also nodePort 30080). Do not apply both Services at once.
- metrix_servercomponents.yaml — A local copy of Metrics Server components you can apply if needed.
- reameme.md — Your original notes (kept for reference). The instructions below fold those ideas into a clean flow.

## Prerequisites
- A running Kubernetes cluster and kubectl configured to talk to it
- Cluster can pull Docker Hub images (for sentientlabsolutions/learning_repo:latest)
- For KinD or some local clusters, Metrics Server may need an extra TLS flag

## 1) Install and verify Metrics Server
HPA requires the resource metrics API (metrics.k8s.io) provided by Metrics Server.

Option A — Use the local manifest in this folder:
```bash
kubectl apply -f metrix_servercomponents.yaml
```

Option B — Use the official release manifest (alternative to A):
- See the Metrics Server docs for the latest components.yaml and apply it.

KinD or other local clusters often need this extra kubelet TLS flag because the kubelet cert isn’t trusted by Metrics Server:
```bash
kubectl -n kube-system patch deployment metrics-server \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

Verify Metrics Server is running and serving metrics:
```bash
kubectl get pods -n kube-system | grep metrics
kubectl top nodes
kubectl top pods -A --sort-by=cpu
```
If these top commands fail, fix Metrics Server before moving on (HPA won’t work without it).

## 2) Deploy the sample app
Use the Deployment path (recommended):
```bash
kubectl apply -f deployments.yaml
kubectl apply -f service_for_deployment.yaml
```
This exposes the app on NodePort 30080. If your cluster nodes are reachable from your machine, the app will be available at http://<node-ip>:30080/.

Alternatively, for a single Pod test:
```bash
kubectl apply -f pod.yaml
kubectl apply -f service.yaml
```
Important: service.yaml and service_for_deployment.yaml both claim nodePort 30080 — only apply one of them at a time.

Check everything is up:
```bash
kubectl get deploy,po,svc
```

## 3) Create an HPA for the Deployment
HPA will scale replicas based on average CPU utilization relative to each Pod’s CPU request. In deployments.yaml each container requests 100m CPU, so a target of 70% means ~70m average per Pod.

Note: The old flag --cpu-percent is deprecated. Use --cpu with a percentage.
```bash
kubectl autoscale deployment deploy-application \
  --min=1 --max=5 \
  --cpu=70%
```
Inspect the HPA:
```bash
kubectl get hpa
kubectl describe hpa deploy-application
```

## 4) Generate load and watch it scale
Pick one of these simple approaches:

- From your laptop via port-forward:
  ```bash
  kubectl port-forward svc/srv-hpa-vpa 8080:80
  # new terminal:
  while true; do curl -s http://127.0.0.1:8080/ >/dev/null; done
  ```

- From inside the cluster (DNS to the Service name works):
  ```bash
  kubectl run loadgen --rm -it --image=busybox -- /bin/sh -c \
    "while true; do wget -q -O- http://srv-hpa-vpa >/dev/null; done"
  ```

Then watch metrics and replicas change:
```bash
kubectl get hpa -w
kubectl get deploy deploy-application -w
kubectl top pods -l app=hpa-vpa-deploy-application
```
As CPU rises above target, HPA increases replicas up to max. When load drops, it scales down (respecting stabilization windows and cooldowns).

## How it works (concepts)
- Metrics Server: Aggregates resource usage (CPU/memory) from kubelets and serves it via the metrics.k8s.io API. HPA reads from here.
- Requests vs limits: HPA’s CPU target is expressed as a percentage of each Pod’s CPU requests. Make sure requests are set (they are in deployments.yaml). If requests are too low or too high, scaling decisions may feel off.
- HPA: Periodically checks metrics and adjusts the Deployment’s replica count within min/max bounds to meet the target. Defaults to CPU; you can also use memory or custom/external metrics with the right adapters.
- Stabilization and rollout: HPA uses rolling averages and stabilization windows to avoid thrashing. Scaling affects Deployments, which perform rolling updates.

## Notes on VPA (Vertical Pod Autoscaler)
- VPA changes Pod resource requests (and optionally limits) up or down to match observed usage. It can recommend values or actively update Pods.
- Do not run HPA and VPA in “control” mode on the same resource dimension (e.g., CPU) for the same workload; use VPA in recommendation mode if combining.
- This repo’s manifests focus on HPA. If you later explore VPA, start in recommendation mode and inspect suggested requests before enabling updates.

## Troubleshooting
- kubectl top fails: Fix Metrics Server (check its Pod logs, TLS flags, APIService status). Without it, HPA shows “unknown” metrics.
- HPA doesn’t scale: Ensure CPU is actually used in the container (generate enough load), requests are set, and the target percentage is reasonable.
- Service not reachable: If NodePort is blocked, use port-forward instead.

## Cleanup
```bash
kubectl delete hpa deploy-application || true
kubectl delete -f service_for_deployment.yaml || true
kubectl delete -f deployments.yaml || true
# Or if you used the Pod path:
# kubectl delete -f service.yaml || true
# kubectl delete -f pod.yaml || true
```

You now have a complete loop: metrics → HPA decision → replica scaling. Tweak requests, targets, and load to see how behavior changes.
