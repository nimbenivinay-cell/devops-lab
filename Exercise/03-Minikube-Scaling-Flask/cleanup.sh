#!/usr/bin/env bash
echo "Cleaning up Exercise 3 resources..."
kubectl delete -f flashsale-replicaset.yaml --ignore-not-found=true
echo "Cleanup completed."
