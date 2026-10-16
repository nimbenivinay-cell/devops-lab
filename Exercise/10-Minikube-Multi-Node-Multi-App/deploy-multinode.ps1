Write-Host "=== Exercise 10: Multi-Node Kubernetes Cluster with Multiple Applications ===" -ForegroundColor Cyan

$ProfileName = "devops-multinode"

# 1. Start 3-node cluster
Write-Host "Starting 3-node Minikube cluster..."
minikube start --nodes 3 -p $ProfileName --force

# 2. Enable registry
Write-Host "Enabling registry add-on..."
minikube -p $ProfileName addons enable registry

# 3. Build images
Write-Host "Building Docker images..."
docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .

# 4. Load images
Write-Host "Loading images into Minikube nodes..."
minikube -p $ProfileName image load product-catalog:latest
minikube -p $ProfileName image load shopping-cart:latest

# 5. Apply manifests
Write-Host "Applying deployments and services..."
kubectl apply -f product_catalog_deployment.yaml
kubectl apply -f shopping_cart_deployment.yaml
kubectl apply -f product_catalog_service.yaml
kubectl apply -f shopping_cart_service.yaml

# 6. Verify distribution
Write-Host "Checking pod distribution across nodes:"
kubectl get nodes
kubectl get pods -o wide
