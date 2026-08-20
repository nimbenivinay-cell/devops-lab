#!/usr/bin/env bash
echo "Cleaning up Exercise 2 resources..."
kubectl delete -f flask-deployment.yaml --ignore-not-found=true
echo "Cleanup completed."
