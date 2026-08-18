Write-Host "=== Exercise 1: Kubernetes Getting Started (Zepto Storefront) ===" -ForegroundColor Cyan

# 1. Start Minikube if available
Write-Host "Checking Minikube..."
try {
    minikube status
} catch {
    Write-Host "Starting Minikube..."
    minikube start
}

# 2. Apply manifests
Write-Host "Applying Pod and Service YAML..."
kubectl apply -f pod.yaml
kubectl apply -f service.yaml

# 3. Check status
Write-Host "Inspecting resources..."
kubectl get pods -o wide
kubectl get svc hello-k8s

# 4. Display service access
Write-Host "Accessing Service..."
minikube service hello-k8s --url
