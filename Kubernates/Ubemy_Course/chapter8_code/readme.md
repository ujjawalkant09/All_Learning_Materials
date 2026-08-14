minikube ssh -n=minikube-02
mkdir /mnt/dir
echo index.html

# create the pv
storageClassName: standard
  capacity:
  accessModes:
  hostPath:
    path: "/mnt/dir"

# create pvc
storageClassName: standard
  accessModes:
  resources:
    requests:
      storage: 500Mi

exec into the po