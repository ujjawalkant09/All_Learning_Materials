# Kubernetes kubectl quick reference

## Official docs
- https://kubernetes.io/docs/home/
- https://kubernetes.io/docs/reference/kubectl/quick-reference/

## Create and expose
- kubectl run nginx --image=nginx
- kubectl create deploy nginx-deploy --image=nginx
- kubectl expose deploy nginx-deploy --port=80 --target-port=80

## Get and describe
- kubectl get pods,deploy,svc -o wide
- kubectl describe pod/nginx
- kubectl describe deploy/nginx-deploy

## Logs and exec
- kubectl logs pod/<pod-name>
- kubectl logs deploy/<deployment-name>
- kubectl exec -it <pod-name> -- sh

## Apply and delete
- kubectl apply -f <file-or-dir>
- kubectl delete -f <file-or-dir>

## Rollouts
- kubectl rollout status deploy/<name>
- kubectl rollout restart deploy/<name>
- kubectl rollout undo deploy/<name>

## Resource usage (needs Metrics Server)
- kubectl top nodes
- kubectl top pods -A --sort-by=cpu
