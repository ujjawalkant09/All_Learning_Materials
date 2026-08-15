# ⚡ Ephemeral Storage: `emptyDir` Volumes in Kubernetes

This guide covers `emptyDir` volumes in Kubernetes — an ephemeral, temporary storage mechanism tied directly to a Pod's lifecycle.

---

## 💡 Core Concepts & Architecture

```
[ Kubernetes Node ]
       │
       ▼
 ┌─────────── Pod (nginx) ────────────┐
 │                                    │
 │  ┌──────────────────────────────┐  │
 │  │ Container (nginx)            │  │
 │  │ Mount: /usr/share/nginx/html │  │
 │  └──────────────┬───────────────┘  │
 │                 │                  │
 │                 ▼                  │
 │   ┌──────────────────────────┐     │
 │   │  Volume: emptyDir        │     │
 │   │  (Ephemeral Node Disk)   │     │
 │   └──────────────────────────┘     │
 └────────────────────────────────────┘
```

### What is `emptyDir`?
* **Ephemeral Volume**: Created when a Pod is assigned to a Node. It starts out completely empty.
* **Shared Storage**: All containers running inside the same Pod can read and write files in the `emptyDir` volume.
* **Storage Medium**: By default, `emptyDir` is stored on whatever medium backs the Node (Disk, SSD, or Network Storage). It can optionally be configured to use RAM (`medium: Memory`).

---

## 📄 Manifest Structure — `pod.yaml`

```yaml
apiVersion: v1 
kind: Pod 
metadata:
  name: nginx
  labels:
    app: nginx 
spec:
  volumes:
    - name: nginx-storage
      emptyDir: {}  # Creates an empty volume on Pod startup
  containers:
  - name: nginx
    image: nginx:latest 
    volumeMounts:
    - name: nginx-storage
      mountPath: /usr/share/nginx/html  # Mounts the volume into the container
    ports:
    - containerPort: 3000
```

---

## 🔄 Lifecycle & Data Retention Rules

| Event | What happens to `emptyDir` data? | Reason |
| :--- | :--- | :--- |
| **Container Restart/Crash** | ✅ **Data Preserved** | The Pod remains on the node; only the container process restarts. |
| **Pod Deleting & Recreating** | ❌ **Data Lost** | When a Pod is deleted (`kubectl delete pod`), its `emptyDir` is wiped. |
| **Node Failure / Rescheduling** | ❌ **Data Lost** | `emptyDir` is bound to the specific Node host filesystem. |

---

## 🛠️ Step-by-Step Hands-on Experiment

### 1. Apply the Pod
```bash
kubectl apply -f pod.yaml
kubectl get pods
```

### 2. Create Data in `emptyDir`
```bash
# Exec into the container
kubectl exec -it nginx -- bash

# Write a test file into the mounted directory
echo "Hello from emptyDir!" > /usr/share/nginx/html/test.txt
cat /usr/share/nginx/html/test.txt

# Exit container
exit
```

### 3. Experiment A: Test Container Crash / Restart (Data Preserved)
```bash
# Kill container process to force a container restart inside the Pod
kubectl exec -it nginx -- kill 1

# Wait for container to restart (STATUS: Running, RESTARTS: 1)
kubectl get pods

# Verify data still exists!
kubectl exec -it nginx -- cat /usr/share/nginx/html/test.txt
# Output: Hello from emptyDir!
```

### 4. Experiment B: Delete Pod (Data Wiped)
```bash
# Delete the pod
kubectl delete pod nginx

# Recreate the pod
kubectl apply -f pod.yaml

# Check the directory -> File is gone!
kubectl exec -it nginx -- ls -la /usr/share/nginx/html/
```

---

## 🧠 Revision Cheat Sheet

| Use Case | When to use `emptyDir` |
| :--- | :--- |
| **Scratch Space** | Temporary disk-based file manipulation, sorting, or caching. |
| **Sidecar Pattern** | Sharing files between two containers in the same Pod (e.g. webserver container + content-puller sidecar). |
| **RAM Disk (`medium: Memory`)** | High-speed temporary scratch space backed by tmpfs (uses Node RAM). |

> [!WARNING]
> **Do NOT use `emptyDir` for database storage or persistent data!** For data that must survive Pod deletions, use **PersistentVolumeClaims (PVC)** instead.
