# Kubernetes Revision Path (Udemy Course Materials)

Follow these folders in order. Each module has self-contained manifests and a README with exact commands to apply, verify, and clean up. Skip Chapter6_code and chapter8_code (left untouched).

0. 00-prereqs-and-tools
   - Goal: Set up local cluster (KinD) and kubectl basics
   - Do: Create/delete clusters, switch contexts, use kubectl cheatsheet
   - Verify: `kubectl cluster-info`, `kubectl get nodes`, run `kubectl top` after Metrics Server (later)

1. 01-deploy-app-basics
   - Goal: Deploy a simple app with a Deployment and expose with NodePort
   - Files: deployment.yaml, service.yaml
   - Do: `kubectl apply -f deployment.yaml && kubectl apply -f service.yaml`
   - Verify: curl http://localhost:30080/ (KinD mapping from 00-prereqs-and-tools/kind-cluster-deploy.yml)

2. 02-service-types
   - Goal: Compare ClusterIP vs NodePort vs LoadBalancer
   - Files: deploy.yaml, deploy_cluster_ip.yaml, nodeport_deploy.yaml, load_balancer_service.yaml
   - Do: Apply Deployment, then ONE Service type at a time
   - Verify: curl via port-forward (ClusterIP), nodeIP:nodePort (NodePort), EXTERNAL-IP (LoadBalancer)

3. 03-environment-variables
   - Goal: Set container env vars via Deployment; expose with NodePort
   - Files: deploy.yaml, service.yaml or learn_sample.yaml
   - Do: Apply Deployment, pick ONE Service manifest
   - Verify: `kubectl exec` into a pod and `printenv APP_NAME`; curl service

4. 04-configmaps
   - Goal: Use ConfigMap values in Deployments (env and envFrom)
   - Files: cm.yaml, deployment.yaml, deploy_new.yaml, service.yaml
   - Do: Apply cm.yaml first, then a Deployment variant, then Service
   - Verify: `kubectl describe pod` shows env from ConfigMap; restart rollout on CM updates

5. 05-secrets-and-private-registry
   - Goal: Create opaque Secret and Docker registry Secret; pull a private image
   - Files: Opaque_secrets.yaml, docker_secrets.yaml, deployment.yaml
   - Do: Generate/apply Secrets; deploy app using imagePullSecrets
   - Verify: Secret type is kubernetes.io/dockerconfigjson; pod pulls private image successfully

6. 06-requests-limits
   - Goal: Understand memory requests/limits and OOM behavior
   - Files: pod.yaml (stress-test)
   - Do: Apply pod, watch memory use; tweak requests/limits and args to trigger OOM or Pending
   - Verify: `kubectl describe pod stress-test` (events), restarts, OOMKilled when over limit

7. 07-autoscaling-hpa-vpa
   - Goal: Install Metrics Server and practice HPA scaling on CPU
   - Files: metrics_server_components.yaml, deployments.yaml, service_for_deployment.yaml (or pod.yaml+service.yaml)
   - Do: Install Metrics Server, deploy app+service, create HPA, generate load
   - Verify: `kubectl get hpa -w`, replicas change; `kubectl top pods` shows CPU

Tips
- Use `kubectl apply -f .` inside a module to create everything, and `kubectl delete -f .` to clean up.
- Keep only one Service manifest active when ports conflict (e.g., NodePort 30080 appears in several places).
- Names and labels must match across Deployment/Service/ConfigMap/Secret.
