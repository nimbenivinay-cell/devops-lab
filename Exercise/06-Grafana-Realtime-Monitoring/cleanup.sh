#!/usr/bin/env bash
echo "Stopping Prometheus, Grafana, and delivery_metrics containers..."
docker stop prometheus grafana delivery_metrics 2>/dev/null || true
docker rm prometheus grafana delivery_metrics 2>/dev/null || true
pkill -f delivery_metrics.py 2>/dev/null || true
echo "Cleanup completed."
