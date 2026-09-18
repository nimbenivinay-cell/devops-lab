# Exercise 03 — Scaling Flask App on Single Node using ReplicaSets

## Objective
The objective of this exercise is to demonstrate horizontal scaling, load distribution, and self-healing resiliency for a cloud-native Python Flask application under a simulated e-commerce **Flash Sale** traffic spike (e.g., Big Billion Day / Prime Day). The workload is orchestrated using Kubernetes **ReplicaSets**, configured with readiness and liveness HTTP probes, CPU/memory resource boundaries, scaled dynamically from 3 to 5 replicas, and tested for automatic pod regeneration upon failure.

---

## Requirements
1. **Flash Sale Application**:
   - `app.py` (and `ex3-flash-sale.py`):
     - `GET /`: Big Sale welcome message with serving pod hostname and timestamp.
     - `GET /buy`: Simulates checkout with random product selection (`Smartphone`, `Shoes`, `Headphones`, `Laptop`), user tracking, and serving pod ID.
     - `GET /health`: Health probe endpoint for Kubernetes liveness and readiness checks.
2. **Production Containerization**:
   - `Dockerfile` with Gunicorn production WSGI server (`gunicorn -b 0.0.0.0:5000 app:app --workers 1 --threads 2`).
   - `requirements.txt` specifying `Flask` and `gunicorn`.
3. **Declarative Kubernetes Configuration**:
   - `flashsale-replicaset.yaml`:
     - `ReplicaSet` (`flashsale-rs` / `flask-app-rs`) initially configured with 3 replicas.
     - HTTP readiness probe (`/health`, initialDelaySeconds: 2, periodSeconds: 5).
     - HTTP liveness probe (`/health`, initialDelaySeconds: 10, periodSeconds: 10).
     - Resource requests (`100m` CPU, `128Mi` RAM) and limits (`500m` CPU, `256Mi` RAM).
     - ClusterIP Service (`flashsale-svc`) mapping port 80 to containerPort 5000.
4. **Validation**:
   - Unit test suite (`test_app.py`) validating all 3 endpoints.
   - Dynamic scaling from 3 to 5 replicas via `kubectl scale`.
   - Pod deletion self-healing verification.

---

## Tools Used
- **Python 3.14**: Application execution and testing.
- **Flask**: Web application framework.
- **Gunicorn**: Production WSGI HTTP server for high concurrency.
- **Docker**: Containerization and image management.
- **Minikube**: Single-node Kubernetes cluster.
- **kubectl**: Cluster scaling, introspection, and pod management.

## Implementation Details

### 1. Flash Sale Application Code (`app.py`)
```python
from flask import Flask, request
import socket, time, random

app = Flask(__name__)

@app.get("/")
def homepage():
    return {
        "message": "Welcome to Big Sale!",
        "pod": socket.gethostname(),
        "ts": time.time()
    }

@app.get("/buy")
def buy():
    item = random.choice(["Smartphone", "Shoes", "Headphones", "Laptop"])
    user = request.args.get("user", f"user{random.randint(1,1000)}")
    return {
        "status": "success",
        "item": item,
        "user": user,
        "served_by_pod": socket.gethostname(),
        "time": time.strftime("%H:%M:%S")
    }

@app.get("/health")
def health():
    return {"status": "healthy", "pod": socket.gethostname()}
```

### 2. Gunicorn Container Definition (`Dockerfile`)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "1", "--threads", "2"]
```

### 3. ReplicaSet & Service Manifest (`flashsale-replicaset.yaml`)
```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: flashsale-rs
  labels:
    app: flashsale
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flashsale
  template:
    metadata:
      labels:
        app: flashsale
    spec:
      containers:
      - name: flashsale-container
        image: flashsale:1.0
        ports:
        - containerPort: 5000
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 2
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: flashsale-svc
spec:
  selector:
    app: flashsale
  ports:
  - name: http
    port: 80
    targetPort: 5000
  type: ClusterIP
```

---

## Commands Executed

### Local Unit Testing & Verification
```powershell
# 1. Execute full unit test suite
python test_app.py

# 2. Inspect deploy and clean scripts
Get-Content .\deploy.ps1
Get-Content .\cleanup.sh
```

### Cluster Lifecycle & Scaling Workflow
```bash
# 1. Start single-node Minikube cluster
minikube start --nodes=1

# 2. Point Docker CLI to Minikube daemon and build image
eval $(minikube docker-env)
docker build -t flashsale:1.0 .

# 3. Apply ReplicaSet and Service
kubectl apply -f flashsale-replicaset.yaml

# 4. Verify initial 3 replicas
kubectl get rs flashsale-rs
kubectl get pods -l app=flashsale

# 5. Scale workload up to 5 replicas for flash sale
kubectl scale rs flashsale-rs --replicas=5

# 6. Verify updated replica count
kubectl get rs flashsale-rs
kubectl get pods -l app=flashsale -o wide

# 7. Test self-healing by deleting one running pod
POD_TO_DELETE=$(kubectl get pods -l app=flashsale -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD_TO_DELETE

# 8. Verify ReplicaSet automatically spawned a replacement pod
kubectl get pods -l app=flashsale
```

---

## Important Configuration & Code

| Component | Setting | Rationale |
| :--- | :--- | :--- |
| **Gunicorn Concurrency** | `--workers 1 --threads 2` | Threaded WSGI concurrency suitable for containerized microservices |
| **Readiness Probe** | `path: /health`, `period: 5s` | Prevents traffic routing to pod until container is initialized |
| **Liveness Probe** | `path: /health`, `period: 10s` | Kubelet automatically restarts container if it hangs or deadlocks |
| **Resource Requests** | `cpu: 100m`, `mem: 128Mi` | Guarantees minimum node allocation for the container |
| **Resource Limits** | `cpu: 500m`, `mem: 256Mi` | Prevents runaway memory leaks from consuming node capacity |

---

## Output

### Terminal Test Output (`test_app.py`)
```text
...
----------------------------------------------------------------------
Ran 3 tests in 0.019s

OK
```

### Cluster Scaling & Distribution Logs
```text
$ kubectl get pods
NAME                 READY   STATUS    RESTARTS   AGE
flashsale-rs-8gbfp   1/1     Running   0          3m35s
flashsale-rs-f4gsl   1/1     Running   0          3m35s
flashsale-rs-nb5kl   1/1     Running   0          3m35s

$ kubectl scale rs flashsale-rs --replicas=5
replicaset.apps/flashsale-rs scaled

$ kubectl get pods -o wide
NAME                 READY   STATUS    RESTARTS   AGE     IP            NODE       NOMINATED NODE
flashsale-rs-8gbfp   1/1     Running   0          4m10s   10.244.0.7    minikube   <none>
flashsale-rs-f4gsl   1/1     Running   0          4m10s   10.244.0.8    minikube   <none>
flashsale-rs-nb5kl   1/1     Running   0          4m10s   10.244.0.9    minikube   <none>
flashsale-rs-nsmlx   1/1     Running   0          32s     10.244.0.10   minikube   <none>
flashsale-rs-wfbb4   1/1     Running   0          32s     10.244.0.11   minikube   <none>
```

---

## Verification
- **Endpoint Test Validation**: `test_app.py` passed with 3 tests:
  - `test_homepage`: Validates `"Welcome to Big Sale!"`, host metadata, and timestamp.
  - `test_buy_endpoint`: Validates simulated checkout, query string handling, and random product selection.
  - `test_health_endpoint`: Validates HTTP 200 health response.
- **Manifest Syntax Validation**: PyYAML validated both YAML documents in `flashsale-replicaset.yaml`.

---

## Result / Conclusion
Exercise 03 is **COMPLETE**. The flash sale application, Gunicorn WSGI containerization, declarative ReplicaSet with probes and limits, scaling workflows, and test suites are fully implemented and verified.
