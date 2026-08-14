# Kubernetes ConfigMap + Deployment — Quick Revision Guide

This folder demonstrates using a ConfigMap in Deployments via two patterns: selecting individual keys (env) and importing all keys (envFrom). It also includes a placeholder for a Service.

Files here:
- cm.yaml — ConfigMap with keys first and last
- deployment.yaml — Deployment using specific keys from the ConfigMap via env/configMapKeyRef
- deploy_new.yaml — Deployment importing all keys from the ConfigMap via envFrom/configMapRef
- service.yaml — ClusterIP Service exposing port 3000 for Pods labeled app: sample-deploy-1

---

## 1) ConfigMap basics
A ConfigMap stores non-confidential configuration data as key/value pairs.

Declarative (recommended):
- Author cm.yaml and then apply it:
  kubectl apply -f cm.yaml

Imperative (one-off):
  kubectl create configmap my-config \
    --from-literal=key1=config1 \
    --from-literal=key2=config2

Generate YAML imperatively (dry-run) and save to a file (what this repo shows):
  kubectl create configmap sample-cm \
    --from-literal=first=piyush \
    --from-literal=last=sachdeva \
    --dry-run=client -o yaml > cm.yaml

Useful commands:
- View: kubectl get cm, kubectl get cm sample-cm -o yaml
- Edit: kubectl edit cm sample-cm
- Delete: kubectl delete cm sample-cm

Notes:
- Changing a ConfigMap does not automatically restart Pods that consume it via env or envFrom. Trigger a rollout restart (see Section 3) or re-deploy.
- If mounted as a volume (not shown here), updates are eventually reflected in files; processes may still need a reload.

---

## 2) Using ConfigMap in Deployments
Two patterns are shown.

A) Pick individual keys as environment variables (deployment.yaml)
Key ideas: use env with valueFrom.configMapKeyRef to target specific keys.
Example snippet:
  env:
  - name: FIRST_NAME
    valueFrom:
      configMapKeyRef:
        name: sample-cm
        key: first
  - name: LAST_NAME
    valueFrom:
      configMapKeyRef:
        name: sample-cm
        key: last

B) Import all keys as environment variables (deploy_new.yaml)
Key ideas: use envFrom with configMapRef to pull in all keys as env vars.
Example snippet:
  envFrom:
    - configMapRef:
        name: sample-cm

Validation tips:
- After applying, describe a Pod to confirm env vars:
  kubectl describe pod <pod-name>
- If the ConfigMap is missing or keys are misspelled, Pods may fail to start (CrashLoopBackOff or ImagePullBackOff for other reasons). Check:
  kubectl get pods
  kubectl describe pod <pod-name>
  kubectl logs <pod-name>

---

## 3) Deployment essentials (applies to both deployment.yaml and deploy_new.yaml)
What to look for:
- replicas: 3 — creates three Pod replicas
- labels/selectors — Pods labeled app: sample-deploy-1 matched by the Deployment selector
- container image — sentientlabsolutions/learning_repo:2.0
- ports — containerPort: 3000 (exposes it inside the Pod; a Service is needed to expose it on the cluster/network)
- strategy — default rolling update if unspecified

Core commands:
- Apply/update: kubectl apply -f deployment.yaml && kubectl apply -f deploy_new.yaml
- Watch rollout: kubectl rollout status deploy/sample-deploy-1
- List: kubectl get deploy,pods -l app=sample-deploy-1
- Inspect: kubectl describe deploy/sample-deploy-1
- Logs (one Pod): kubectl logs <pod-name>
- Scale: kubectl scale deploy/sample-deploy-1 --replicas=5
- Roll back last change: kubectl rollout undo deploy/sample-deploy-1
- Force a restart to pick up ConfigMap changes in env/envFrom:
  kubectl rollout restart deploy/sample-deploy-1

---

## 4) Service
A ClusterIP Service is provided in service.yaml to expose containerPort 3000 from Pods labeled app: sample-deploy-1.

Common Service types:
- ClusterIP (in-cluster only, default)
- NodePort (expose on each node’s IP at a static port)
- LoadBalancer (cloud provider integration)

Apply and test:
- kubectl apply -f service.yaml
- kubectl get svc sample-svc -o wide

---

## 5) Apply in order and clean up
Suggested order (to avoid missing references):
1) kubectl apply -f cm.yaml
2) kubectl apply -f deployment.yaml (or deploy_new.yaml)
3) kubectl apply -f service.yaml (if/when you add it)

Shortcuts:
- Apply everything in this folder: kubectl apply -f .
- Delete everything in this folder: kubectl delete -f .

---

## 6) Troubleshooting checklist
- ConfigMap present? kubectl get cm sample-cm -o yaml
- Keys match? first and last
- Pods picking up env? kubectl describe pod <pod-name>
- Deployment stable? kubectl rollout status deploy/sample-deploy-1
- Need restart after ConfigMap change? kubectl rollout restart deploy/sample-deploy-1

