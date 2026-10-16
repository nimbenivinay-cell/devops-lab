#!/usr/bin/env bash
set -e

echo "=== Exercise 10: Multi-Node Kubernetes Cluster with Multiple Applications ==="

PROFILE="devops-multinode"

# Step 0: Cleanup previous minikube cluster if needed
echo "Step 0: Checking minikube profile ${PROFILE}..."

# Step 1a: Start 3-node Minikube cluster
echo "Step 1a: Starting 3-node Minikube cluster (profile: ${PROFILE})..."
minikube start --nodes 3 -p "${PROFILE}" --force

# Step 1b: Enable Minikube registry add-on
echo "Step 1b: Enabling registry add-on..."
minikube -p "${PROFILE}" addons enable registry

# Step 4: Build Docker images
echo "Step 4: Building Docker images for Product Catalog and Shopping Cart..."
docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .

# Step 5: Load images into Minikube cluster nodes
echo "Step 5: Loading images into Minikube multi-node registry..."
minikube -p "${PROFILE}" image load product-catalog:latest
minikube -p "${PROFILE}" image load shopping-cart:latest

# Step 6: Deploy manifests
echo "Step 6: Applying Deployments with Pod Anti-Affinity rules..."
kubectl apply -f product_catalog_deployment.yaml
kubectl apply -f shopping_cart_deployment.yaml

# Step 7: Expose Services
echo "Step 7: Applying Services..."
kubectl apply -f product_catalog_service.yaml
kubectl apply -f shopping_cart_service.yaml

# Step 8: Verify Pod Distribution across nodes
echo "Step 8: Verifying node distribution (each pod should be scheduled on a different node):"
kubectl get nodes
kubectl get pods -o wide

# Step 9: Service access URLs
echo "Product Catalog Service URL:"
minikube -p "${PROFILE}" service product-catalog-service --url

echo "Shopping Cart Service URL:"
minikube -p "${PROFILE}" service shopping-cart-service --url
