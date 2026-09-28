#!/usr/bin/env bash
set -e

echo "=== Exercise 6: Real-time Operations Monitoring & Alerting (ZAPPTTO) ==="

# 1. Start delivery metrics application locally or in Docker
echo "Step 1: Starting delivery_metrics in background..."
python3 delivery_metrics.py &
METRICS_PID=$!
echo "Metrics server running with PID $METRICS_PID"

# 2. Start Prometheus
echo "Step 2: Starting Prometheus container..."
docker run -d --name prometheus -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/alert_rules.yml:/etc/prometheus/alert_rules.yml \
  prom/prometheus

# 3. Start Grafana
echo "Step 3: Starting Grafana container..."
docker run -d --name grafana -p 3000:3000 grafana/grafana

echo "Monitoring stack initialized:"
echo " - Metrics Endpoint : http://localhost:8000/metrics"
echo " - Prometheus UI    : http://localhost:9090"
echo " - Grafana UI       : http://localhost:3000 (User: admin / admin)"
