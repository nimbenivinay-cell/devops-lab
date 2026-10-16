#!/usr/bin/env bash
PROFILE="devops-multinode"
echo "Cleaning up Exercise 10 resources..."
kubectl delete -f shopping_cart_service.yaml --ignore-not-found=true
kubectl delete -f product_catalog_service.yaml --ignore-not-found=true
kubectl delete -f shopping_cart_deployment.yaml --ignore-not-found=true
kubectl delete -f product_catalog_deployment.yaml --ignore-not-found=true
echo "Stopping and deleting ${PROFILE} minikube profile..."
minikube stop -p "${PROFILE}" 2>/dev/null || true
minikube delete -p "${PROFILE}" 2>/dev/null || true
echo "Cleanup complete."
