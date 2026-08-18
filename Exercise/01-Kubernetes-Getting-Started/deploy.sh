#!/usr/bin/env bash
set -e

echo "=== Exercise 1: Kubernetes Getting Started (Zepto Storefront) ==="

# 1. Check or start Minikube
echo "Checking Minikube status..."
if ! minikube status > /dev/null 2>&1; then
    echo "Starting Minikube cluster..."
    minikube start
else
    echo "Minikube is already running."
fi

# 2. Deploy Pod and Service (declarative method)
echo "Applying Kubernetes manifests..."
kubectl apply -f pod.yaml
kubectl apply -f service.yaml

# 3. Wait for pod to be ready
echo "Waiting for hello-k8s pod to reach Running state..."
kubectl wait --for=condition=Ready pod/hello-k8s --timeout=60s

# 4. Inspect resources
echo "--- Pods ---"
kubectl get pods -l app=hello-k8s -o wide

echo "--- Services ---"
kubectl get svc hello-k8s

# 5. Access service
echo "Service URL:"
minikube service hello-k8s --url
