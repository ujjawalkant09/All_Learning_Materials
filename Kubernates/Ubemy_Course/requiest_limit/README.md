# Pod: stress-test (memory requests/limits demo)

This repository contains a single-container Pod that allocates memory briefly to demonstrate how Kubernetes memory requests and limits work.

## Manifest (pod.yaml)
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: stress-test 
spec:
  containers:
  - image: polinux/stress
    name: stress-test 
    command: ["stress"]
    resources:
      requests:
        memory: "50Mi"
      limits:
        memory: "100Mi"
    args: ["--vm","1","--vm-bytes","80M","--timeout","10s"]
```

## What each field does (crisp but complete)
- apiVersion: v1 and kind: Pod
  - Core API object for running a single Pod (no controller).
- metadata.name: stress-test
  - Pod name; must be unique within the namespace.
- spec.containers[0]
  - image: polinux/stress — small utility image to generate CPU/memory load.
  - name: stress-test — container name inside the Pod.
  - command/args: runs `stress --vm 1 --vm-bytes 80M --timeout 10s`
    - --vm 1: start one memory worker.
    - --vm-bytes 80M: each worker allocates ~80 MB (decimal megabytes).
    - --timeout 10s: run for ~10 seconds, then exit.
  - resources:
    - requests.memory: 50Mi — scheduler guarantee; the Pod will be placed only on a node that can spare at least ~50 MiB.
    - limits.memory: 100Mi — hard cgroup cap; if the process exceeds ~100 MiB, it will be OOM-killed by the kernel.

Notes on units:
- M (as used by stress) is decimal megabytes (1,000,000 bytes).
- Mi (as used by Kubernetes) is mebibytes (1,048,576 bytes). Here, 80M < 100Mi, so the container should not be OOMKilled.

## Expected behavior
- Pod schedules if a node has ≥50Mi free allocatable memory.
- Container allocates ~80 MB for ~10 seconds and then exits successfully.
- Because restartPolicy defaults to Always for Pods, the container will restart after it exits. You will see the Restarts count increase. If you want it to run only once, set `restartPolicy: Never`.

Optional one-shot variant:
```yaml
spec:
  restartPolicy: Never
  containers:
    # ... same as above
```

## How to run
- Apply the manifest
  ```bash
  kubectl apply -f pod.yaml
  ```
- Watch the Pod
  ```bash
  kubectl get pod stress-test -w
  ```
- Inspect details and events
  ```bash
  kubectl describe pod stress-test
  ```
- View logs (shows stress output)
  ```bash
  kubectl logs pod/stress-test
  ```

## Clean up
```bash
kubectl delete pod stress-test
```

## Experiments (quick knobs)
- Trigger an OOMKill: raise the workload above the limit (e.g., `--vm-bytes 120M`) or lower `limits.memory` (e.g., `70Mi`). Then check `kubectl describe pod` for OOMKilled in Last State / Events.
- Scheduling pressure demo: raise `requests.memory` (e.g., `500Mi`) to see Pending when the cluster lacks headroom.

## Summary
This Pod is a minimal, reproducible setup to see how memory requests affect scheduling and how memory limits enforce a hard cap leading to OOMKill when exceeded. It runs a short-lived memory allocation to keep the demo quick and observable.
