<!-- Important commands to create yaml  -->


<!-- http://localhost:30080/  access the application using this url -->

kubectl create deploy deploy-application --image=sentientlabsolutions/learning_repo:latest --dry-run=client -o yaml > deployment.yaml


kubectl expose deployment deploy-application --dry-run=client -o yaml >service.yaml



<!-- Build docker images  -->
<!-- docker build -t sentientlabsolutions/learning_repo:2.0 . -->
<!-- docker build -t {image_name} . -->

<!-- kubectl get pods --show-labels -->