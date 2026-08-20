#!/usr/bin/env bash
set -e

echo "=== Exercise 2: Deploy Flask App on Minikube using kubectl and YAML ==="

# 1. Start Minikube
echo "Step 1: Checking Minikube..."
if ! minikube status > /dev/null 2>&1; then
    minikube start
fi

# 2. Configure Docker environment for Minikube
echo "Step 2: Configuring Minikube Docker environment..."
eval $(minikube docker-env)

# 3. Build Docker image inside Minikube
echo "Step 3: Building Docker image 'flask-app'..."
docker build -t flask-app:latest .

# 4. Apply Kubernetes deployment and service
echo "Step 4: Applying flask-deployment.yaml..."
kubectl apply -f flask-deployment.yaml

# 5. Wait for deployment rollout
echo "Step 5: Waiting for Deployment rollout..."
kubectl rollout status deployment/flask-app --timeout=60s

# 6. Check resources
echo "Step 6: Checking deployments and pods..."
kubectl get deployments flask-app
kubectl get pods -l app=flask-app -o wide
kubectl get services flask-app-service

# 7. Print access URL
echo "Step 7: Service access URL:"
minikube service flask-app-service --url
