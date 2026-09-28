Write-Host "=== Exercise 6: Real-time Operations Monitoring & Alerting ===" -ForegroundColor Cyan

# 1. Start Python metrics simulator
Write-Host "Starting delivery_metrics.py in background..."
Start-Process python -ArgumentList "delivery_metrics.py"

# 2. Run Prometheus
Write-Host "Starting Prometheus..."
docker run -d --name prometheus -p 9090:9090 `
  -v ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml `
  -v ${PWD}/alert_rules.yml:/etc/prometheus/alert_rules.yml `
  prom/prometheus

# 3. Run Grafana
Write-Host "Starting Grafana..."
docker run -d --name grafana -p 3000:3000 grafana/grafana

Write-Host "Monitoring stack started. Access Prometheus at http://localhost:9090 and Grafana at http://localhost:3000"
