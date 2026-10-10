# 🚀 Amazon EKS: Complete Master Guide & Step-by-Step Practical Blueprint

This comprehensive guide covers Amazon EKS (Elastic Kubernetes Service) from cluster setup to workload deployment, resource management, AWS Network Load Balancers, dynamic EBS storage, and Cluster Autoscaling.

---

## 💡 Core Architecture & Concepts

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 AWS EKS Control Plane                   │
                  │             (API Server, etcd, Controllers)             │
                  └────────────────────────────┬────────────────────────────┘
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               │                                                               │
               ▼                                                               ▼
┌─────────────────────────────┐                                 ┌─────────────────────────────┐
│  Worker Node Group (AZ-1)   │                                 │  Worker Node Group (AZ-2)   │
│ ┌─────────────────────────┐ │                                 │ ┌─────────────────────────┐ │
│ │ Pod (hello-app)         │ │ ◄── [AWS NLB (LoadBalancer)] ──►│ │ Pod (hello-app)         │ │
│ │  • Requests: 0.25 CPU   │ │                                 │ │  • Requests: 0.25 CPU   │ │
│ │  • Limits: 0.5 CPU      │ │                                 │ │  • Limits: 0.5 CPU      │ │
│ └────────────┬────────────┘ │                                 │ └────────────┬────────────┘ │
│              │              │                                 │              │              │
│              ▼              │                                 │              ▼              │
│    [AWS EBS Volume (gp2)]   │                                 │    [AWS EBS Volume (gp2)]   │
└─────────────────────────────┘                                 └─────────────────────────────┘
```

* **EKS Control Plane**: AWS-managed Kubernetes API server and etcd database.
* **Worker Node Groups**: AWS EC2 instances running `kubelet` and container runtime hosting your application Pods.
* **AWS Load Balancer Controller**: Provisioner that automatically creates AWS Elastic Load Balancers (NLB/ALB) when a Kubernetes Service or Ingress is created.
* **AWS EBS CSI Driver**: Plugin that enables dynamic provisioning of AWS Elastic Block Store (EBS) volumes via Persistent Volume Claims (PVC).
* **Cluster Autoscaler**: Controller running in `kube-system` that scales EC2 worker nodes up/down based on Pod resource requests.

---

## ⚙️ Prerequisites Checklist

Before starting, ensure you have:
1. **AWS CLI** installed (`aws --version`) and authenticated (`aws configure` or `aws sso login`).
2. **`kubectl`** CLI installed.
3. **IAM Cluster Role (`EKSClusterRole`)**: IAM role with `AmazonEKSClusterPolicy` attached.
4. **VPC with Multi-AZ Subnets**: Minimum 2 public/private subnets across different Availability Zones (Reference: [AWS VPC CloudFormation Template](https://docs.aws.amazon.com/eks/latest/userguide/creating-a-vpc.html)).

---

## 🛠️ Step 1: EKS Cluster Provisioning & Setup

### 1. Set Default AWS Region
```bash
aws configure set region ap-south-1
```

### 2. Provision EKS Control Plane
```bash
aws eks create-cluster \
  --name my-first-eks \
  --kubernetes-version 1.32 \
  --region ap-south-1 \
  --role-arn arn:aws:iam::585768174200:role/EKSClusterRole \
  --resources-vpc-config subnetIds=subnet-0f7e27c51809021cd,subnet-007edd7389bc3554e
```

### 3. Monitor Status Until Active
```bash
aws eks describe-cluster --name my-first-eks --query "cluster.status"
```

### 4. Connect Local `kubectl` Context
```bash
aws eks update-kubeconfig --name my-first-eks --region ap-south-1
```

### 5. Verify Cluster Access
```bash
kubectl get nodes
kubectl get svc
```

---

## 📦 Step 2: Workload Deployment & Resource Management

Kubernetes allows setting **`requests`** (minimum guaranteed resources) and **`limits`** (maximum allowed resources) for Pods.

* **`requests`**: Used by the Kubernetes Scheduler to find a node with enough capacity.
* **`limits`**: Hard upper bounds. CPU is throttled if exceeded; Memory causes container termination (`OOMKilled`) if exceeded.

### Manifest: `AWS_SAMPLE_DEPLOYMENTS_WITH_RESOURCE_AND_LIMIT.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-app
  template:
    metadata:
      labels:
        app: hello-app
    spec:
      containers:
        - name: hello-app
          image: public.ecr.aws/nginx/nginx:alpine-slim
          ports:
            - containerPort: 80
          resources:
            requests:
              memory: "20Mi"
              cpu: "0.25"     # 250m CPU cores
            limits:
              memory: "50Mi"
              cpu: "0.5"      # 500m CPU cores
```

**Apply deployment:**
```bash
kubectl apply -f AWS_SAMPLE_DEPLOYMENTS_WITH_RESOURCE_AND_LIMIT.yaml
```

---

## 🌐 Step 3: Exposing Workload via AWS Network Load Balancer (NLB)

In EKS, annotations on a Service tell AWS how to construct the Load Balancer.

### Manifest: `AWS_SVC.yaml`
```yaml
apiVersion: v1
kind: Service
metadata:
  name: hello-app-service
  annotations:
    # Make the NLB internet-facing (publicly accessible)
    service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
    # Route traffic directly to Pod IPs (improves latency & simplifies SG rules)
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: ip
spec:
  selector:
    app: hello-app
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
  type: LoadBalancer
```

**Apply service & get public endpoint:**
```bash
kubectl apply -f AWS_SVC.yaml

# Fetch the external AWS ELB DNS URL
kubectl get svc hello-app-service
```
> The `EXTERNAL-IP` field will output an AWS Load Balancer DNS name (e.g. `k8s-default-helloapp-123456.elb.ap-south-1.amazonaws.com`).

---

## 💾 Step 4: Dynamic Storage Provisioning (AWS EBS)

Dynamic provisioning automatically creates AWS EBS volumes whenever a `PersistentVolumeClaim` (PVC) is created.

### 1. StorageClass Definition
Defines the AWS storage provider (`kubernetes.io/aws-ebs` or `ebs.csi.aws.com`) and volume type (e.g., `gp2` or `gp3`).

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-sc
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
```

### 2. PersistentVolumeClaim (PVC) Definition
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: ebs-sc
```

### 3. Workflow & How It Works
1. You apply the `StorageClass` and `PersistentVolumeClaim`.
2. Kubernetes requests AWS to automatically create a **1Gi gp2 EBS volume**.
3. AWS creates the EBS volume and binds it to a `PersistentVolume` (PV).
4. Your Pod mounts the PVC into its filesystem.

---

## 📈 Step 5: EKS Cluster Autoscaler

Unlike GKE or AKS where autoscaling is enabled by a single checkbox, EKS requires deploying the **Cluster Autoscaler** controller into your cluster.

### How Cluster Autoscaler Works on EKS
1. **Monitors Unschedulable Pods**: When Pods cannot be scheduled due to insufficient CPU/Memory requests, Cluster Autoscaler detects them.
2. **Auto Discovery**: Cluster Autoscaler scans AWS Auto Scaling Groups (ASGs) tagged with:
   * `k8s.io/cluster-autoscaler/enabled = true`
   * `k8s.io/cluster-autoscaler/<cluster-name> = owned` (or `shared`)
3. **Scales EC2 Nodes**: It automatically increases the ASG desired capacity to launch new EC2 worker nodes.
4. **Scale Down**: When nodes are underutilized for a prolonged period, Cluster Autoscaler safely drains and terminates redundant EC2 nodes.

---

## 🧠 Master Revision Cheat Sheet

| Task / Feature | File / Command | Key Note |
| :--- | :--- | :--- |
| **Create Cluster** | `aws eks create-cluster ...` | Requires minimum 2 subnets & IAM Cluster Role. |
| **Configure `kubectl`** | `aws eks update-kubeconfig --name <cluster>` | Updates local `~/.kube/config`. |
| **Deploy with Limits** | [`AWS_SAMPLE_DEPLOYMENTS_WITH_RESOURCE_AND_LIMIT.yaml`](file:///Users/iamujjawal/Desktop/AllLearningMaterial/All_Learning_Materials/Kubernates/Ubemy_Course/aws_eks/AWS_SAMPLE_DEPLOYMENTS_WITH_RESOURCE_AND_LIMIT.yaml) | Defines `requests` (guaranteed) & `limits` (cap). |
| **Expose NLB** | [`AWS_SVC.yaml`](file:///Users/iamujjawal/Desktop/AllLearningMaterial/All_Learning_Materials/Kubernates/Ubemy_Course/aws_eks/AWS_SVC.yaml) | Uses `internet-facing` & `nlb-target-type: ip` annotations. |
| **Check External IP** | `kubectl get svc hello-app-service` | Retrieves public AWS ELB DNS endpoint. |
| **Dynamic Storage** | `StorageClass` + `PersistentVolumeClaim` | Automatically provisions AWS EBS volumes (`gp2`/`gp3`). |
| **Cluster Autoscaler** | Deployment in `kube-system` namespace | Auto-scales EC2 worker nodes based on Pod resource requests. |