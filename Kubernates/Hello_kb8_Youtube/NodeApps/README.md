# 🐳 Hello Kubernetes (Node.js App + Docker Desktop Kubernetes)

This repository contains a simple Express Node.js application, containerized with Docker, and deployed to Docker Desktop Kubernetes using Pod, Deployment, and Service manifests.

---

## 📁 File Structure

* **`app/app.js`**: Express server listening on port 3000 returning `"Hello World!"`.
* **`package.json`**: App configuration and dependencies (`express: ^5.2.1`).
* **`Dockerfile`**: Container definition built on `node:20-alpine`.
* **`hello-pod.yaml`**: Standalone Kubernetes Pod manifest.
* **`hello-deployment.yaml`**: Kubernetes Deployment manifest (3 replicas).
* **`hello-service.yaml`**: Kubernetes Service manifest (`type: LoadBalancer`).

---

## 🛠️ Step-by-Step Execution Guide (Docker Desktop Kubernetes)

### 1. Build Docker Image
```bash
docker build -t hello-k8s:v1 .
```

### 2. Ensure Context is Set to Docker Desktop
```bash
kubectl config use-context docker-desktop
kubectl get nodes
```

### 3. Deploy the Application
```bash
# Apply Deployment (3 replicas)
kubectl apply -f hello-deployment.yaml

# Apply LoadBalancer Service
kubectl apply -f hello-service.yaml

# Check deployed resources
kubectl get all
```

### 4. Access the Application
Since Docker Desktop automatically binds `type: LoadBalancer` services to your host, access the app at:
```text
http://localhost:80   (or simply http://localhost)
```

---

## ⚠️ Common Issues & Troubleshooting Guide

### ❌ Issue 1: `open Dockerfile: no such file or directory`
* **Cause**: File was named `DockerFile` (with a capital `F`). `docker build` expects standard lowercase `Dockerfile`.
* **Solution**: Rename the file to `Dockerfile`.

---

### ❌ Issue 2: Dockerfile Syntax Error (`COPY. .`)
* **Cause**: Missing space between `COPY` command and source path (`COPY. .`).
* **Solution**: Update line to `COPY . .`.

---

### ❌ Issue 3: `npm WARN notsup Unsupported engine for express@5.2.1`
* **Cause**: Base image `node:14-alpine` was used, but Express 5 requires Node `>= 18`.
* **Solution**: Upgrade Dockerfile base image to `FROM node:20-alpine`.

---

### ❌ Issue 4: `no matches for kind "Deployment" in version "app/v1"`
* **Cause**: Typo in `hello-deployment.yaml` (`apiVersion: app/v1` missing the `s`).
* **Solution**: Change `apiVersion: app/v1` to `apiVersion: apps/v1`.

---

### ❌ Issue 5: Pod Status `ImagePullBackOff` / `ErrImagePull`
* **Cause**: Image `hello-k8s:v1` existed on host machine Docker engine, but Kubernetes attempted to pull from Docker Hub (`docker.io/library/hello-k8s:v1`).
* **Solution**: Set `imagePullPolicy: IfNotPresent` or `imagePullPolicy: Never` in your manifests so Kubernetes uses the local Docker Desktop image.

---

### ❌ Issue 6: Cannot Access `localhost:3000` via Service
* **Cause**: In `hello-service.yaml`, `port: 80` exposes the service on port 80 (forwarding to `targetPort: 3000` inside containers).
* **Solution**: Access the app via `http://localhost` (port 80) instead of port 3000.



   kubectl cluster-info
   kubectl apply -f deploy.yaml
   kubectl get namespaces
   kubectl get deploy --all-namespaces
   kubectl get deploy --all-namespaces
   kubectl get deploy --all-namespaces
   kubectl get deploy --all-namespaces
   kubectl get pods
   kubectl get pods --all-namespaces

kubectl delete all --all -n default
