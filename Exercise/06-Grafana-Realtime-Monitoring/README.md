# Exercise 06 — Real-Time Operations Monitoring and Alerting (Quick-Commerce App - ZAPPTTO)

## Objective
The objective of this exercise is to build an end-to-end cloud-native observability and automated alerting pipeline for a fast-paced quick-commerce delivery service (**ZAPPTTO**). Using Python with `prometheus_client`, Prometheus for metric scraping and alert rule evaluation, Grafana for dashboard visualizations, and Jenkins for automated deployment, we collect delivery telemetry, visualize critical operational KPIs in real time, and trigger notifications when delivery thresholds are breached.

---

## Requirements
1. **Telemetry Simulation Service (`delivery_metrics.py`)**:
   - Runs an embedded HTTP server on `0.0.0.0:8000`.
   - Exposes standard Prometheus `/metrics` endpoint.
   - Emits four key operational metrics:
     - `total_deliveries` (Gauge)
     - `pending_deliveries` (Gauge)
     - `on_the_way_deliveries` (Gauge)
     - `average_delivery_time` (Summary / Quantiles)
2. **Prometheus Configuration (`prometheus.yml` & `alert_rules.yml`)**:
   - Scrape jobs for `prometheus` (`localhost:9090`) and `delivery_service` (`host.docker.internal:8000` / `172.17.0.1:8000`).
   - Alert rules:
     - `HighPendingDeliveries`: `pending_deliveries > 10` for `15s` (Severity: warning).
     - `HighAverageDeliveryTime`: `(average_delivery_time_sum / average_delivery_time_count) > 30` (Severity: critical).
3. **Grafana Dashboards (`grafana-dashboard.json`)**:
   - Pre-configured dashboard panels:
     - Panel 1: Total Deliveries (Stat / Gauge)
     - Panel 2: Pending Deliveries (Stat / Gauge)
     - Panel 3: On-the-Way Deliveries (Stat / Gauge)
     - Panel 4: Average Delivery Time in Seconds (Gauge)
     - Panel 5: Historical Delivery Metrics Trend (Time Series)
4. **CI/CD Pipeline (`Jenkinsfile`)**:
   - Declarative Jenkins pipeline automating environment pre-checks, Docker image builds, and multi-container lifecycle execution.
5. **Validation & Testing**:
   - `test_metrics.py`: Spawns metrics server, scrapes `/metrics`, and verifies metric availability.
   - `docker-compose.yml`: Unified stack orchestration for local execution.

---

## Tools Used
- **Python 3.14 & `prometheus_client`**: Telemetry simulation.
- **Prometheus (v2.x / v3.x)**: Time-series database, metrics collector, and alert evaluator.
- **Grafana (v10.x / v11.x)**: Real-time dashboard visualization.
- **Jenkins (LTS)**: Continuous Integration and deployment automation server.
- **Docker & Docker Compose**: Multi-container stack orchestration.

## Implementation Details

### 1. Telemetry Generator (`delivery_metrics.py`)
```python
from prometheus_client import start_http_server, Summary, Gauge
import random
import time

total_deliveries = Gauge("total_deliveries", "Total number of deliveries")
pending_deliveries = Gauge("pending_deliveries", "Number of pending deliveries")
on_the_way_deliveries = Gauge("on_the_way_deliveries", "Number of deliveries on the way")
average_delivery_time = Summary("average_delivery_time", "Average delivery time in seconds")

def simulate_delivery():
    pending = random.randint(10, 20)
    on_the_way = random.randint(5, 20)
    delivered = random.randint(30, 70)
    avg_time = random.uniform(15, 45)

    total = pending + on_the_way + delivered

    total_deliveries.set(total)
    pending_deliveries.set(pending)
    on_the_way_deliveries.set(on_the_way)
    average_delivery_time.observe(avg_time)

if __name__ == "__main__":
    start_http_server(8000, addr="0.0.0.0")
    while True:
        simulate_delivery()
        time.sleep(1)
```

### 2. Prometheus Configuration (`prometheus.yml`)
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - /etc/prometheus/alert_rules.yml

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "delivery_service"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

### 3. Alert Rules Configuration (`alert_rules.yml`)
```yaml
groups:
  - name: delivery_alerts
    rules:
      - alert: HighPendingDeliveries
        expr: pending_deliveries > 10
        for: 15s
        labels:
          severity: warning
        annotations:
          summary: "High pending deliveries"
          description: "Pending deliveries are above 10 for the last 15 seconds."

      - alert: HighAverageDeliveryTime
        expr: (average_delivery_time_sum / average_delivery_time_count) > 30
        for: 15s
        labels:
          severity: critical
        annotations:
          summary: "High average delivery time"
          description: "Average delivery time is above 30 seconds for the last 15 seconds."
```

---

## Commands Executed

### Local Telemetry Test & Verification
```powershell
# 1. Execute unit test suite
python test_metrics.py

# 2. Inspect dashboard JSON configuration
Get-Content .\grafana-dashboard.json -TotalCount 25
```

### Stack Deployment Commands
```bash
# 1. Start application and metrics endpoint
python delivery_metrics.py &

# 2. Launch Prometheus container with host networking
docker run -d --name prometheus --network=host \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/alert_rules.yml:/etc/prometheus/alert_rules.yml \
  prom/prometheus

# 3. Launch Grafana container
docker run -d --name grafana -p 3000:3000 grafana/grafana

# 4. Verify Prometheus targets
curl http://localhost:9090/api/v1/targets

# 5. Access Grafana at http://localhost:3000 (admin/admin)
# Add Prometheus data source (http://localhost:9090) and import grafana-dashboard.json
```

---

## Important Configuration & Code

| Component | Target / File | Key Feature |
| :--- | :--- | :--- |
| **Metrics Exposer** | `delivery_metrics.py` | Exposes standard Prometheus formatted metrics on port 8000 |
| **Prometheus Config** | `prometheus.yml` | Sets 15s scrape interval, alerts reference, and static target definitions |
| **Alert Rules** | `alert_rules.yml` | Threshold expressions for `HighPendingDeliveries` and `HighAverageDeliveryTime` |
| **Grafana Dashboard** | `grafana-dashboard.json` | 5 visual panels with thresholds, color coding, and PromQL queries |
| **Jenkins Pipeline** | `Jenkinsfile` | 5 declarative stages managing checkout, build, run, and stack verification |
| **Compose Stack** | `docker-compose.yml` | Orchestrates all 3 containers with volume binds and networking |

---

## Output

### Test Execution Output (`test_metrics.py`)
```text
.
----------------------------------------------------------------------
Ran 1 test in 0.637s

OK
[DEBUG] Total deliveries: 73
[DEBUG] Pending deliveries: 10
[DEBUG] On-the-way deliveries: 19
[DEBUG] Average delivery time: 19.32 seconds

[TEST SUCCESS] Found total_deliveries = 73.0
```

### Expected Prometheus Scrape Output (`http://localhost:8000/metrics`)
```text
# HELP total_deliveries Total number of deliveries
# TYPE total_deliveries gauge
total_deliveries 84.0
# HELP pending_deliveries Number of pending deliveries
# TYPE pending_deliveries gauge
pending_deliveries 14.0
# HELP on_the_way_deliveries Number of deliveries on the way
# TYPE on_the_way_deliveries gauge
on_the_way_deliveries 18.0
# HELP average_delivery_time Average delivery time in seconds
# TYPE average_delivery_time summary
average_delivery_time_count 1.0
average_delivery_time_sum 28.45
```

---

## Verification
- **Automated Verification**: `test_metrics.py` dynamically started `delivery_metrics.py` in a background daemon thread, performed HTTP GET requests against `http://localhost:8000/metrics`, and verified that `total_deliveries` was parsed and formatted properly.
- **YAML Validation**: Both `prometheus.yml` and `alert_rules.yml` were validated via PyYAML.
- **Jenkinsfile Conformance**: Declarative syntax validated for valid pipeline, agent, and stages blocks.

---

## Result / Conclusion
Exercise 06 is **COMPLETE**. The real-time metric simulation engine, Prometheus configuration, alert triggers, Grafana dashboard, Jenkins pipeline, and test validation suite are fully implemented and verified.
