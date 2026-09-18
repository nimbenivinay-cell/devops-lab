#!/usr/bin/env bash
set -e

echo "=== Exercise 3: Scaling Flask App with ReplicaSets ==="

# 1. Start Minikube
echo "Step 1: Checking Minikube..."
if ! minikube status > /dev/null 2>&1; then
    minikube start --nodes=1
fi

# 2. Configure Docker daemon
echo "Step 2: Pointing Docker to Minikube..."
eval $(minikube docker-env)

# 3. Build image
echo "Step 3: Building image 'flashsale:1.0'..."
docker build -t flashsale:1.0 .

# 4. Apply ReplicaSet and Service
echo "Step 4: Applying flashsale-replicaset.yaml..."
kubectl apply -f flashsale-replicaset.yaml

# 5. Check initial 3 replicas
echo "Step 5: Verifying initial 3 replicas..."
kubectl get rs flashsale-rs
kubectl get pods -l app=flashsale -o wide

# 6. Scale up to 5 replicas
echo "Step 6: Scaling ReplicaSet to 5 replicas..."
kubectl scale rs flashsale-rs --replicas=5

# 7. Verify scaled pods
echo "Step 7: Verifying 5 replicas..."
kubectl get rs flashsale-rs
kubectl get pods -l app=flashsale -o wide

# 8. Test Self-Healing (Delete one pod)
POD_TO_DELETE=$(kubectl get pods -l app=flashsale -o jsonpath='{.items[0].metadata.name}')
echo "Step 8: Testing self-healing: deleting pod $POD_TO_DELETE..."
kubectl delete pod $POD_TO_DELETE

echo "Step 9: Observing new replacement pod created automatically..."
kubectl get pods -l app=flashsale -o wide

# 10. Access service
echo "Step 10: Service access URL:"
minikube service flashsale-svc --url
