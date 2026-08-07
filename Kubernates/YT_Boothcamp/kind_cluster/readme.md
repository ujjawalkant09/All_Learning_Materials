# List nodes
kubectl get nodes

# List namespaces
kubectl get ns

# List Pods in current namespace
kubectl get pods

# List Pods in nginx namespace
kubectl get pods -n nginx

# List Pods in all namespaces
kubectl get pods -A

# Show node, IP, etc.
kubectl get pods -n nginx -o wide

# Describe a Pod (gives you very details about the pod)
<!-- This is the  first place to check if you are having some issue with pods-->
kubectl describe pod nginx-pod -n nginx

# View logs
kubectl logs nginx-pod -n nginx

# Execute a shell
kubectl exec -it nginx-pod -n nginx -- /bin/sh

# View Pod YAML
kubectl get pod nginx-pod -n nginx -o yaml

# Delete a Pod  
kubectl delete pod nginx-pod -n nginx


# To Check weather the image is available in the node -->
kubectl run nginx-3 --image=nginx --dry-run=client

# To Genereate the yam file using existing images -->
kubectl run nginx-3 --image=nginx --dry-run=client -o yaml > pod3.yml



# To Edit the pod directly 
kubectl edit pod {pod-name} 


# To Apply the changes 
kubectl apply -f pod3.yml 

# TO SHOW PODS LABELS
kubectl get pods --show-labels

<!-- HOw to create pods -->
kubectl create -f {yml file name}



<!-- How to get into the pods  -->
kubectl exec -it {pod-name} -n {namespace} -- /bin/sh 

<!-- Examples  -->
kubectl exec -it nginx-3 -- bash


<!-- For better details  -->
kubectl get pods -o wide


NAME          READY   STATUS    RESTARTS   AGE   IP           NODE                              NOMINATED NODE   READINESS GATES
nginx-3       1/1     Running   0          14m   10.244.1.3   kind-kubernetes-cluster-worker2   <none>           <none>
nginx-pod     1/1     Running   0          32h   10.244.1.2   kind-kubernetes-cluster-worker2   <none>           <none>
nginx-pod-2   1/1     Running   0          21m   10.244.2.2   kind-kubernetes-cluster-worker    <none>           <none>



kubectl create → Creates a resource once. If it already exists, it fails.
kubectl apply → Creates the resource if it doesn't exist, or updates it if it does


| Feature                          | `kubectl create` | `kubectl apply` |
| -------------------------------- | ---------------- | --------------- |
| Creates new resource             | ✅                | ✅               |
| Updates existing resource        | ❌                | ✅               |
| Fails if resource already exists | ✅                | ❌               |
| Safe to run multiple times       | ❌                | ✅               |
| Common in CI/CD                  | ❌                | ✅               |
| Style                            | Imperative       | Declarative     |



kubectl create --help


kubectl create deployment --help


kubectl create deploy nginx-deply  --image=nginx --replicas=3

kubectl get deployment


kubectl get deploy


kubectl describe deploy {deplyment-name}

kubectl describe deploy nginx-deply


kubectl scale --help


<!-- Scale the replicas  -->
kubectl scale deployment nginx-deply --replicas=2


kubectl create deploy sample --image=nginx --dry-run=client -o yaml > deploy.yaml

<!-- rollout -->
kubectl rollout --help

kubectl rollout restart deploy  nginx-deply

kubectl rollout history deploy 


kubectl rollout history deploy nginx-deply

<!-- To rollout back the changes  -->

kubectl rollout undo deployment/nginx-deply 

 or 

kubectl rollout undo deployment nginx-deply


kubectl rollout undo deployment {deplyment_name}


kubectl expose --help


kubectl expose deployment sample --port=80

kubectl expose deployment {deplyment-name} --port=80


kubectl describe svc sample


for accessing the cluster ip for kind setup run this commands after creating the service 

Cluster id is for k8 internal pods only 

kubectl port-forward svc/sample 8080:80


| Minikube                  | Kind / Standard Kubernetes                                                         |
| ------------------------- | ---------------------------------------------------------------------------------- |
| `minikube service list`   | `kubectl get svc -A`                                                               |
| `minikube service <name>` | `kubectl port-forward svc/<name> ...` or access via NodePort                       |
| `minikube ip`             | `docker inspect kind-control-plane` (or `kubectl get nodes -o wide` for node info) |





<!-- ```
 1198  kubectl apply -f nodeport_deploy.yaml
 1199  kubectl apply -f nodeport_deploy.yaml
 1200  kubectl get svc
 1201  kubectl describe svc nginx-clusterip
 1202  kubectl ep
 1203  kubectl get eo
 1204  kubectl get ep
 1205  kubectl port-forward svc/nginx-clusterip 8080:80
 1206  kubectl apply -f nodeport_deploy.yaml
 1207  kubectl apply -f nodeport_deploy.yaml
 1208  kubectl get ep
 1209  kubectl delete svc nginx-clusterip
 1210  kubectl get ep
 1211  kubectl describe svc nginx-nodeport
 1212  kubectl describe svc nginx-nodeport
 1213  hostory ``` -->


 kind get clusters

 If you still see:-> kind-twf-cluster


Delete it
kind delete cluster --name kind-twf-cluster 

Then recreate it:
kind create cluster --config config.yml --name kind-twf-cluster