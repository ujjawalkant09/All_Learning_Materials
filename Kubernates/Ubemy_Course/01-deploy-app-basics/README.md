# Deploying an application — Deployment + NodePort Service

This folder deploys a simple web app using a Kubernetes Deployment and exposes it with a NodePort Service for easy local access.

- Access URL (kind with port mapping): http://localhost:30080/
- Workload image: sentientlabsolutions/learning_repo:latest (containerPort 3000)

## What’s in this folder

- deployment.yaml — Deployment deploy-application
  - labels: app=deploy-application, replicas: 3
  - container: sentientlabsolutions/learning_repo:latest
  - ports: containerPort 3000
- service.yaml — Service (NodePort) srv-deploy-application
  - selector: app=deploy-application
  - port: 80 → targetPort: 3000
  - nodePort: 30080

## Your original quick-reference (kept for convenience)

```sh
# Important commands to create yaml
# Access the application using this URL when NodePort is 30080 on kind
# http://localhost:30080/

kubectl create deploy deploy-application \
  --image=sentientlabsolutions/learning_repo:latest \
  --dry-run=client -o yaml > deployment.yaml

kubectl expose deployment deploy-application \
  --dry-run=client -o yaml > service.yaml

# Build docker images
# docker build -t sentientlabsolutions/learning_repo:2.0 .
# docker build -t {image_name} .

# Labels on pods
# kubectl get pods --show-labels

# Create service (generic example)
kubectl expose deployment deploy-application \
  --name=deploy-application-svc \
  --port=80 \
  --target-port=80 \
  --type=NodePort \
  --dry-run=client -o yaml > service.yaml
```

Notes
- In this project the app listens on 3000; set targetPort to 3000 (see Recommended below).

## Recommended: generate manifests that match this app

```sh
# Deployment manifest (same as above)
kubectl create deploy deploy-application \
  --image=sentientlabsolutions/learning_repo:latest \
  --dry-run=client -o yaml > deployment.yaml

# Service manifest: NodePort 30080 → targetPort 3000, name matches existing YAML
kubectl expose deployment deploy-application \
  --name=srv-deploy-application \
  --port=80 \
  --target-port=3000 \
  --type=NodePort \
  --dry-run=client -o yaml > service.yaml
```

## Apply

```sh
kubectl apply -f deployment.yaml
kubectl rollout status deploy/deploy-application
kubectl get deploy,rs,pods -l app=deploy-application -o wide

kubectl apply -f service.yaml
kubectl get svc srv-deploy-application
```

## Test access

- kind (Extras/kind-cluster-deply.yml maps container port 30080 to host 30080)
  - curl -i http://localhost:30080/
- Generic NodePort
  - NODE_IP=$(kubectl get node -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
  - curl -i http://$NODE_IP:30080/

## Common operations to revise

- Scale up/down
  - kubectl scale deploy/deploy-application --replicas=5
- Update image (rolling update)
  - kubectl set image deploy/deploy-application learning-repo-s27c5=sentientlabsolutions/learning_repo:2.0
  - kubectl rollout status deploy/deploy-application
  - kubectl rollout history deploy/deploy-application
  - kubectl rollout undo deploy/deploy-application --to-revision=1
- Inspect pods and labels
  - kubectl get pods -l app=deploy-application --show-labels -o wide
  - kubectl describe deploy/deploy-application
  - kubectl describe svc/srv-deploy-application
- Logs and debug
  - POD=$(kubectl get pod -l app=deploy-application -o jsonpath='{.items[0].metadata.name}')
  - kubectl logs "$POD"
  - kubectl exec -it "$POD" -- sh -lc 'printenv | sort'

## Service types recap

- ClusterIP: in-cluster only; use port-forward to access locally.
- NodePort: exposes on nodeIP:nodePort (30080 here); simple for local clusters.
- LoadBalancer: cloud LB with external IP (if your cluster supports it).

## Docker build/publish notes

- docker build -t sentientlabsolutions/learning_repo:2.0 .
- docker push sentientlabsolutions/learning_repo:2.0
- Update the Deployment image to use the new tag (see update image above).

## Cleanup

```sh
kubectl delete -f service.yaml --ignore-not-found
kubectl delete -f deployment.yaml --ignore-not-found
```

## Appendix: flag meanings (from your notes)

| Part                      | Meaning                        |
|---------------------------|--------------------------------|
| deploy-application        | Deployment name                |
| srv-deploy-application    | Service name                   |
| 80 (port)                 | Service port (client-facing)   |
| 3000 (targetPort)         | Pod/container port             |
| NodePort                  | Service type                   |
| service.yaml              | Output YAML file               |
