for adddons metrix server 

1. Install Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml


2. For kind, allow insecure kubelet TLS

Kind commonly needs this because the kubelet certificate isn't trusted by Metrics Server.

Patch the deployment:
kubectl -n kube-system patch deployment metrics-server \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'


  3. Check Metrics Server
  kubectl get pods -n kube-system | grep metrics


  kubectl top node

  kubectl top pod 


  kubectl top pod -A --sort-by=cpu

 kubectl autoscale deployment -h // help for syntax 


kubectl autoscale deployment {deployment_name}  --min=1 --max=3 --cpu-percent=15


kubectl autoscale deploy deploy-application --min=1 --max=3 --cpu-percent=15
output -

Flag --cpu-percent has been deprecated, Use --cpu with percentage or resource quantity format (e.g., '70%' for utilization or '500m' for milliCPU).
horizontalpodautoscaler.autoscaling/deploy-application autoscaled

--

kubectl get hpa