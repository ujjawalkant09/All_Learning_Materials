# 📦 Kubernetes Storage: PersistentVolume (PV) & PersistentVolumeClaim (PVC)

This guide covers persistent storage concepts in Kubernetes using Kind (Kubernetes in Docker).

---

## 💡 Core Concepts & Architecture

```
[ Local Host Machine ] 
       │ (/Users/iamujjawal/Desktop/kind-data/worker1)
       ▼ (Kind extraMounts)
[ Kind Worker Node ] 
       │ (/mnt/data)
       ▼ (PV hostPath)
[ PersistentVolume (PV) ] ── (Binds via StorageClass & AccessMode) ──► [ PersistentVolumeClaim (PVC) ]
                                                                                   │
                                                                                   ▼ (Volume Mount)
                                                                             [ Nginx Pod ]
                                                                      (/usr/share/nginx/html)
```

### 1. PersistentVolume (PV) — `pv.yaml`
* **What it is**: A piece of storage in the cluster provisioned by an administrator or dynamically.
* **Lifecycle**: Independent of any individual Pod that uses it.
* **Key Configuration (`pv.yaml`)**:
  ```yaml
  apiVersion: v1
  kind: PersistentVolume
  metadata:
    name: pv-volume
  spec:
    storageClassName: standard
    capacity:
      storage: 1Gi
    accessModes:
      - ReadWriteOnce
    hostPath:
      path: /mnt/data
  ```

### 2. PersistentVolumeClaim (PVC) — `pvc.yaml`
* **What it is**: A request for storage by a user/developer. It requests a specific size and access mode.
* **Binding**: Kubernetes matches the PVC request to an available PV.
* **Key Configuration (`pvc.yaml`)**:
  ```yaml
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: nginx-pvc
  spec:
    storageClassName: standard
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 500Mi
  ```

### 3. Pod Mounting PVC — `pods.yaml`
* **What it is**: The workload that consumes the PVC.
* **Key Configuration (`pods.yaml`)**:
  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: nginx
  spec:
    volumes:
      - name: nginx-storage
        persistentVolumeClaim:
          claimName: nginx-pvc
    containers:
      - name: nginx
        image: nginx:latest
        volumeMounts:
          - name: nginx-storage
            mountPath: /usr/share/nginx/html
  ```

---

## ⚡ Important Gotcha: Why PVC Status Stays `Pending`

If `kubectl get pvc` shows **`STATUS: Pending`**, the most common reasons are:

1. **`VOLUMEBINDINGMODE: WaitForFirstConsumer`**:
   The default `standard` StorageClass in Kind/Minikube sets `volumeBindingMode: WaitForFirstConsumer`. 
   * Kubernetes **will not bind** the PVC to a PV until a Pod that references the PVC is actually created.
2. **Pod configuration mismatch**:
   If the Pod uses `emptyDir: {}` instead of `persistentVolumeClaim: { claimName: nginx-pvc }`, Kubernetes does not know the Pod needs `nginx-pvc`, so the PVC stays `Pending`.

---

## 🛠️ Commands & Verification Workflow

### 1. Apply Manifests
```bash
# Apply PV, PVC, and Pod
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl apply -f pods.yaml
```

### 2. Check Status
```bash
# Check PV, PVC, and Pod in one command
kubectl get pv,pvc,pod

# Watch real-time changes
kubectl get pvc -w
```

### 3. Inspect Node & Persistence
```bash
# List worker nodes
kubectl get nodes

# Inspect files on the Kind worker node
docker exec my-kind-cluster-worker ls -la /mnt/data

# Read a test file inside the Kind worker node mount
docker exec my-kind-cluster-worker cat /mnt/data/test.txt
```

---

## 🧠 Revision Cheat Sheet

| Field / Term | Description |
| :--- | :--- |
| **`ReadWriteOnce` (RWO)** | Volume can be mounted as read-write by a single node. |
| **`ReadOnlyMany` (ROX)** | Volume can be mounted as read-only by many nodes. |
| **`ReadWriteMany` (RWX)** | Volume can be mounted as read-write by many nodes. |
| **`Retain` Policy** | Manual reclamation; PV is kept intact even after PVC is deleted. |
| **`Delete` Policy** | Automatic deletion of PV and underlying storage when PVC is deleted. |
| **`hostPath`** | Mounts a file/directory from the host node filesystem into the PV (useful for single-node development). |