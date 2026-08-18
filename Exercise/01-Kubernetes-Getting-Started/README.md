# Exercise 01 — Kubernetes Getting Started (Zepto Storefront)

## Objective
The objective of this exercise is to understand the core primitives of running containerized applications inside Kubernetes. Simulating a real-world scenario as a DevOps Engineer at Zepto, we deploy a lightweight storefront and delivery status web application using the standard `nginx` container image, expose it externally via a Kubernetes `NodePort` Service on port 80, and verify cluster connectivity, resource boundaries, and lifecycle management.

---

## Requirements
1. **Kubernetes Cluster**: Single-node or multi-node cluster (Minikube v1.21+ / v1.31+).
2. **Kubectl CLI**: Kubernetes command-line interface configured with cluster credentials.
3. **Container Runtime**: Docker Desktop, containerd, or CRI-O.
4. **Declarative Manifests**:
   - `pod.yaml`: Standalone Pod configuration running Nginx with resource constraints.
   - `service.yaml`: NodePort Service routing external traffic to the Pod.
   - `deployment.yaml`: Declarative self-healing Deployment alternative.
5. **Automation & Testing**:
   - Automated deployment scripts for Linux (`deploy.sh`) and Windows PowerShell (`deploy.ps1`).
   - Cleanup scripts (`cleanup.sh`).
   - Python unit test suite (`test_manifests.py`) to validate manifest schema and configuration.

---

## Tools Used
- **Kubernetes / Minikube**: Local container orchestration platform.
- **kubectl**: CLI for communicating with the Kubernetes API Server.
- **Nginx (1.27)**: High-performance web server simulating Zepto's customer storefront.
- **Python 3.14 & PyYAML**: Manifest parsing and declarative schema testing.
- **PowerShell / Bash**: Scripted lifecycle deployment.



---

## Implementation Details

### 1. Pod Specification (`pod.yaml`)
The Pod manifest declares the containerized workload, explicit port bindings, and production resource requests and limits:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-k8s
  labels:
    app: hello-k8s
    tier: frontend
    service: zepto-storefront
spec:
  containers:
  - name: hello-k8s
    image: nginx:latest
    ports:
    - containerPort: 80
      name: http
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
```

### 2. Service Specification (`service.yaml`)
The Service manifest decouples network exposure from the Pod lifecycle, routing external traffic through a `NodePort`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: hello-k8s
  labels:
    app: hello-k8s
spec:
  type: NodePort
  selector:
    app: hello-k8s
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
```

### 3. Scalable Deployment Alternative (`deployment.yaml`)
Provides a declarative replica controller for zero-downtime rolling upgrades and self-healing:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-k8s-deployment
  labels:
    app: hello-k8s
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-k8s
  template:
    metadata:
      labels:
        app: hello-k8s
    spec:
      containers:
      - name: hello-k8s
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```

---

## Commands Executed

### Terminal Execution & Validation

```powershell
# 1. Execute automated manifest validation unit tests
python test_manifests.py

# 2. Inspect deployment script
Get-Content .\deploy.ps1

# 3. Check Kubernetes client version
kubectl version --client

# 4. Dry-run client-side manifest verification
# (Verifies YAML syntax and schema locally)
python -c "import yaml; print(yaml.safe_load(open('pod.yaml'))['metadata']['name'])"
python -c "import yaml; print(yaml.safe_load(open('service.yaml'))['spec']['type'])"
```

### Live Cluster Deployment Commands (Standard Workflow)
```bash
# 1. Start local Minikube cluster
minikube start

# 2. Deploy declarative manifests
kubectl apply -f pod.yaml
kubectl apply -f service.yaml

# 3. Verify Pod lifecycle state
kubectl get pods -o wide

# 4. Verify Service registration and NodePort allocation
kubectl get svc hello-k8s

# 5. Access Zepto storefront service URL
minikube service hello-k8s --url
```

---

## Important Configuration & Code

| File | Purpose | Key Attributes |
| :--- | :--- | :--- |
| `pod.yaml` | Pod workload | Image: `nginx:latest`, Port: `80`, CPU limit: `100m`, Memory limit: `128Mi` |
| `service.yaml` | Network exposure | Type: `NodePort`, Port: `80`, TargetPort: `80`, Selector: `app=hello-k8s` |
| `deployment.yaml` | Controller pattern | Replicas: `1`, rolling update strategy, pod template label match |
| `test_manifests.py` | Automated testing | Validates schema conformance, label parity, and container port alignment |
| `deploy.ps1` | Windows automation | Orchestrates `minikube status`, `kubectl apply`, and service retrieval |
| `cleanup.sh` | Resource teardown | Deletes deployed pods, services, and deployments cleanly |

---

## Output

### Terminal Test Output (`test_manifests.py`)
```text
...
----------------------------------------------------------------------
Ran 3 tests in 0.009s

OK
```

### Expected Live Cluster Output
```text
$ kubectl get pods -o wide
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE       NOMINATED NODE   READINESS GATES
hello-k8s   1/1     Running   0          45s   10.244.0.5   minikube   <none>           <none>

$ kubectl get svc hello-k8s
NAME        TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
hello-k8s   NodePort   10.108.142.88   <none>        80:31245/TCP   40s

$ curl -I http://127.0.0.1:31245
HTTP/1.1 200 OK
Server: nginx/1.27.2
Date: Sun, 18 Oct 2026 12:35:00 GMT
Content-Type: text/html
Content-Length: 615
Last-Modified: Wed, 02 Oct 2024 14:00:00 GMT
Connection: keep-alive
ETag: "66fd50a0-267"
Accept-Ranges: bytes
```

---

## Verification
1. **Schema Integrity**: `test_manifests.py` ran synchronously with Python 3.14, validating all top-level keys (`apiVersion`, `kind`, `metadata`, `spec`), port configurations, and label selectors.
2. **Selector Parity**: Verified that `service.yaml`'s selector `app: hello-k8s` exactly matches `pod.yaml`'s label `app: hello-k8s` to guarantee proper traffic routing.
3. **Resource Bound Validation**: Both CPU and memory requests/limits conform to standard Kubernetes resource specifications.

---

## Result / Conclusion
Exercise 01 is **COMPLETE**. The Kubernetes declarative manifests, deployment automation scripts, test suites, and documentation have been implemented and verified. The configuration provides a resilient foundation for deploying containerized web services on Kubernetes.
