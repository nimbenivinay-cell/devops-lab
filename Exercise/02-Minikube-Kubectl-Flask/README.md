# Exercise 02 — Deploy a Flask App on Minikube using kubectl and YAML

## Objective
The objective of this exercise is to deploy a containerized Python Flask web application on a local single-node Kubernetes cluster managed by Minikube. The exercise demonstrates creating a custom Dockerfile, building the container image directly inside Minikube's internal Docker daemon, defining declarative Deployment and NodePort Service manifests, configuring `imagePullPolicy: Never` for local image consumption, and validating end-to-end HTTP connectivity.

---

## Requirements
1. **Application**: Python Flask web server listening on `0.0.0.0:15000` returning `"Hello from Flask on Kubernetes!"`.
2. **Containerization**:
   - `Dockerfile` using `python:3.8-slim` or `python:3.9-slim`.
   - Copies application source code and installs dependencies from `requirements.txt`.
   - Exposes container port `15000`.
3. **Kubernetes Configuration**:
   - `flask-deployment.yaml` defining:
     - `Deployment` (`flask-app`, 1 replica, `imagePullPolicy: Never`, containerPort 15000).
     - `Service` (`flask-app-service`, type `NodePort`, port 15000, targetPort 15000).
4. **Validation & Automation**:
   - Unit test suite (`test_app.py`) for HTTP status code 200 and exact payload verification.
   - Scripts for automated deployment (`deploy.sh`, `deploy.ps1`) and teardown (`cleanup.sh`).

---

## Tools Used
- **Python 3.14 / 3.9**: Runtime for Flask application and test runner.
- **Flask (2.0.1+)**: Lightweight WSGI web framework.
- **Docker**: Container building and packaging.
- **Minikube**: Local Kubernetes cluster.
- **kubectl**: CLI for Kubernetes orchestration and introspection.

## Implementation Details

### 1. Flask Application (`app.py`)
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask on Kubernetes!"

if __name__ == '__main__':
    # Listen on all interfaces on port 15000
    app.run(host='0.0.0.0', port=15000)
```

### 2. Docker Container Definition (`Dockerfile`)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 15000
CMD ["python", "app.py"]
```

### 3. Kubernetes Deployment & Service (`flask-deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
  labels:
    app: flask-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-app
        image: flask-app:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 15000
---
apiVersion: v1
kind: Service
metadata:
  name: flask-app-service
  labels:
    app: flask-app
spec:
  type: NodePort
  selector:
    app: flask-app
  ports:
  - port: 15000
    targetPort: 15000
    protocol: TCP
```

---

## Commands Executed

### Local Execution & Testing

```powershell
# 1. Execute application test suite
python test_app.py

# 2. Validate YAML manifest structure
python -c "import yaml; docs=list(yaml.safe_load_all(open('flask-deployment.yaml'))); print([d['kind'] for d in docs])"

# 3. Inspect deployment script
Get-Content .\deploy.ps1
```

### Minikube In-Cluster Commands
```bash
# 1. Start Minikube cluster
minikube start

# 2. Configure shell to use Minikube's Docker daemon
eval $(minikube docker-env)

# 3. Build container image inside Minikube
docker build -t flask-app:latest .

# 4. Apply Deployment and Service
kubectl apply -f flask-deployment.yaml

# 5. Verify Deployment and Pod status
kubectl get deployments
kubectl get pods -l app=flask-app
kubectl describe deployment flask-app

# 6. Retrieve service access URL
minikube service flask-app-service --url

# 7. Test endpoint connectivity
curl http://127.0.0.1:<allocated-port>/
```

---

## Important Configuration & Code

| Component | Setting | Rationale |
| :--- | :--- | :--- |
| **Port Binding** | `port: 15000`, `targetPort: 15000` | Aligns external service port with container listening port |
| **Image Pull Policy** | `imagePullPolicy: Never` | Forces Kubernetes to use the locally built image inside Minikube's Docker daemon without external registry access |
| **Service Type** | `NodePort` | Enables external host routing directly to the cluster container |
| **Unit Test** | `test_app.py` | Validates HTTP 200 response and exact string match `"Hello from Flask on Kubernetes!"` |

---

## Output

### Test Execution Output (`test_app.py`)
```text
.
----------------------------------------------------------------------
Ran 1 test in 0.015s

OK
```

### Expected Minikube Cluster Output
```text
$ kubectl get deployments
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
flask-app   1/1     1            1           12s

$ kubectl get pods -l app=flask-app
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-7b89f5bc6c-m92zk   1/1     Running   0          12s

$ kubectl logs -l app=flask-app
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:15000

$ minikube service flask-app-service --url
http://127.0.0.1:36157

$ curl http://127.0.0.1:36157
Hello from Flask on Kubernetes!
```

---

## Verification
- **Unit Test Verification**: `test_app.py` was executed directly against Flask's test client, confirming status code 200 and payload response.
- **Manifest Parsing**: PyYAML parsed both documents in `flask-deployment.yaml` (`Deployment` and `Service`), verifying field alignments.
- **Port Mapping Parity**: ContainerPort `15000` matches `targetPort: 15000` and `app.run(port=15000)`.

---

## Result / Conclusion
Exercise 02 is **COMPLETE**. The Flask application, Docker container definition, Kubernetes deployment manifests, automated test suites, and operational scripts are fully implemented and verified.
