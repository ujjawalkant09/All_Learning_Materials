# Kubernetes Secrets and Private Registry Demo

This mini-project demonstrates three core Kubernetes concepts:
- Creating an opaque Secret (generic key/value) and understanding base64 encoding
- Creating a Docker registry credential Secret to pull a private image
- Deploying a workload that uses `imagePullSecrets` to authenticate when pulling the image

The manifests in this folder are intentionally small and focused so you can revise the concepts quickly.

## Prerequisites
- A working Kubernetes cluster and `kubectl` configured to talk to it
- A Docker Hub username and a Personal Access Token (or password) for a private image
- Optional: a target namespace (examples default to the current namespace)

## Repository contents
- `Opaque_secrets.yaml` — an opaque Secret named `demo-secret` that stores a key `password` (base64-encoded).
- `docker_secrets.yaml` — a Docker registry Secret (`type: kubernetes.io/dockerconfigjson`) named `sample-docker-secret`.
- `deployment.yaml` — a Deployment that pulls the private image `sentientlabsolutions/learning_private_repo:latest` using `imagePullSecrets: sample-docker-secret`.

> Important: Never commit real credentials. If you previously stored real tokens in YAML/markdown, rotate them and replace with placeholders immediately.

## Quick start
1) Create or update the Secrets

Option A — generate YAML locally (recommended for revision) and apply it:

```bash
# Docker registry Secret (Docker Hub)
kubectl create secret docker-registry sample-docker-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username={{DOCKER_USERNAME}} \
  --docker-password={{DOCKER_TOKEN}} \
  --docker-email={{EMAIL}} \
  --dry-run=client -o yaml > docker_secrets.yaml

kubectl apply -f docker_secrets.yaml

# Opaque Secret (generic key/value)
kubectl create secret generic demo-secret \
  --from-literal=password=hellopass \
  --dry-run=client -o yaml > Opaque_secrets.yaml

kubectl apply -f Opaque_secrets.yaml
```

Option B — create directly (no YAML on disk):

```bash
kubectl create secret docker-registry sample-docker-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username={{DOCKER_USERNAME}} \
  --docker-password={{DOCKER_TOKEN}} \
  --docker-email={{EMAIL}}

kubectl create secret generic demo-secret --from-literal=password=hellopass
```

2) Deploy the app that pulls a private image

```bash
kubectl apply -f deployment.yaml
kubectl get deploy,pods
```

3) Verify the registry Secret and events

```bash
# Secret type should be kubernetes.io/dockerconfigjson
kubectl get secret sample-docker-secret -o jsonpath='{.type}{"\n"}'

# Look for successful image pulls or errors
kubectl describe pod <one-of-the-pods>
```

## Base64: encode/decode refresher
Kubernetes stores Secret data in base64-encoded form. This is not encryption — just encoding.

```bash
# Encode (note -n to avoid a trailing newline in input)
echo -n "hellopass" | base64

# Decode (example uses the value from Opaque_secrets.yaml)
echo "aGVsbG9wYXNz" | base64 --decode
```

To read and decode a key directly from the cluster:

```bash
kubectl get secret demo-secret -o jsonpath='{.data.password}' | base64 --decode; echo
```

## Consuming Secrets in Pods (patterns)
Although the provided `deployment.yaml` focuses on image pulling, here are common ways to consume opaque Secrets:

- As an environment variable
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example
spec:
  replicas: 1
  selector:
    matchLabels: { app: example }
  template:
    metadata:
      labels: { app: example }
    spec:
      containers:
      - name: app
        image: nginx
        env:
        - name: APP_PASSWORD
          valueFrom:
            secretKeyRef:
              name: demo-secret
              key: password
```

- As a mounted file
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-volume-demo
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: secret-vol
      mountPath: /etc/secret
  volumes:
  - name: secret-vol
    secret:
      secretName: demo-secret
```

## Troubleshooting
- ImagePullBackOff or ErrImagePull
  - Ensure `sample-docker-secret` exists in the same namespace as the Deployment.
  - Confirm it is of type `kubernetes.io/dockerconfigjson` and the name matches `imagePullSecrets`.
  - Validate your Docker Hub token is active and has pull access to the image.
- Secret not found when referenced as env or volume
  - Secret and workload must be in the same namespace, or reference it correctly within that namespace.
- Base64 surprises
  - Use `echo -n` for encoding to avoid adding an extra newline; decode with `base64 --decode`.

## Cleanup
```bash
kubectl delete -f deployment.yaml
kubectl delete -f docker_secrets.yaml || kubectl delete secret sample-docker-secret
kubectl delete -f Opaque_secrets.yaml || kubectl delete secret demo-secret
```

## Notes and next steps
- Avoid committing real secrets to Git. Consider using tools like Sealed Secrets (Bitnami), External Secrets Operator, or your cloud provider's KMS + CSI driver for production.
- Names must match: `imagePullSecrets.name` in `deployment.yaml` must equal the Secret metadata `name` used for your registry credentials.
