#!/usr/bin/env bash
echo "Cleaning up Exercise 1 resources..."
kubectl delete -f service.yaml --ignore-not-found=true
kubectl delete -f pod.yaml --ignore-not-found=true
kubectl delete -f deployment.yaml --ignore-not-found=true
echo "Cleanup completed."
