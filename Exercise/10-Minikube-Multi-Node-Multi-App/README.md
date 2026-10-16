# Exercise 10 — Multi-Node Kubernetes Cluster with Multiple Applications and ReplicaSets

## Objective
The objective of this exercise is to deploy a resilient, highly available multi-tier e-commerce microservices architecture across a **multi-node Kubernetes cluster** managed by Minikube (`devops-multinode`). The architecture consists of two distinct microservices: **Product Catalog** (2 replicas) and **Shopping Cart** (3 replicas). Using Kubernetes **Pod Anti-Affinity** policies (`topologyKey: "kubernetes.io/hostname"`), we enforce strict failure-domain separation so that replica pods are distributed across distinct nodes, ensuring continuous availability even if an entire node suffers an outage.

---

## Requirements
1. **Multi-Node Cluster Infrastructure**:
   - 3-node Minikube cluster created with profile `devops-multinode` (`--nodes 3`).
   - Minikube local container registry addon enabled for sharing images across nodes.
2. **Microservices Codebase**:
   - **Product Catalog (AppA)**:
     - `product_catalog.py`: Flask service exposing `GET /products` returning available items (Laptop, Phone, Headphones).
     - `Dockerfile.product`: Container build manifest exposing port 80.
   - **Shopping Cart (AppB)**:
     - `shopping_cart.py`: Flask service exposing `GET /cart` (read cart items) and `POST /cart` (add items with HTTP 201 Created).
     - `Dockerfile.shopping`: Container build manifest exposing port 80.
3. **Declarative Kubernetes Manifests**:
   - `product_catalog_deployment.yaml`: Deployment with 2 replicas, `podAntiAffinity` on `app=product-catalog`.
   - `product_catalog_service.yaml`: NodePort Service exposing port 80.
   - `shopping_cart_deployment.yaml`: Deployment with 3 replicas, `podAntiAffinity` on `app=shopping-cart`.
   - `shopping_cart_service.yaml`: NodePort Service exposing port 80.
4. **Validation & Testing**:
   - `test_apps.py`: Unit test validating all endpoints for both applications (`/products`, `/cart` GET, `/cart` POST).
   - Node distribution verification: `kubectl get pods -o wide`.
   - Scripts: `deploy-multinode.sh`, `deploy-multinode.ps1`, `cleanup.sh`.

---

## Tools Used
- **Minikube (v1.31+ / v1.34+)**: Multi-node cluster orchestration (`--nodes 3`).
- **kubectl**: Cluster scheduling, manifest deployment, and pod distribution introspection.
- **Docker**: Image creation (`product-catalog:latest` and `shopping-cart:latest`).
- **Python 3.14**: Microservices implementation and test runner.
- **Flask**: Microservice REST framework.


---

## Implementation Details

### 1. Product Catalog Service (`product_catalog.py`)
```python
from flask import Flask, jsonify

app = Flask(__name__)

products = [
    {"id": 1, "name": "Laptop", "price": 1200},
    {"id": 2, "name": "Phone", "price": 800},
    {"id": 3, "name": "Headphones", "price": 150},
]

@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
```

### 2. Shopping Cart Service (`shopping_cart.py`)
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

cart = []

@app.route("/cart", methods=["GET"])
def get_cart():
    return jsonify(cart)

@app.route("/cart", methods=["POST"])
def add_to_cart():
    item = request.json
    cart.append(item)
    return jsonify(cart), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
```

### 3. Product Catalog Deployment with Pod Anti-Affinity (`product_catalog_deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-catalog
  labels:
    app: product-catalog
spec:
  replicas: 2
  selector:
    matchLabels:
      app: product-catalog
  template:
    metadata:
      labels:
        app: product-catalog
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: product-catalog
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: product-catalog-container
        image: product-catalog:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 80
```

### 4. Shopping Cart Deployment with Pod Anti-Affinity (`shopping_cart_deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shopping-cart
  labels:
    app: shopping-cart
spec:
  replicas: 3
  selector:
    matchLabels:
      app: shopping-cart
  template:
    metadata:
      labels:
        app: shopping-cart
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: shopping-cart
            topologyKey: "kubernetes.io/hostname"
      containers:
      - name: shopping-cart-container
        image: shopping-cart:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 80
```

---

## Commands Executed

### Local Application Verification
```powershell
# 1. Run unit test suite for both applications
python test_apps.py

# 2. Inspect multi-node deploy script
Get-Content .\deploy-multinode.ps1
```

### Multi-Node Cluster Lifecycle Commands
```bash
# 1. Start 3-node Minikube cluster
minikube start --nodes 3 -p devops-multinode --force

# 2. Enable Minikube internal registry addon
minikube -p devops-multinode addons enable registry

# 3. Build Docker container images
docker build -t product-catalog:latest -f Dockerfile.product .
docker build -t shopping-cart:latest -f Dockerfile.shopping .

# 4. Load built images into multi-node Minikube registry
minikube -p devops-multinode image load product-catalog:latest
minikube -p devops-multinode image load shopping-cart:latest

# 5. Apply Deployment and Service manifests
kubectl apply -f product_catalog_deployment.yaml
kubectl apply -f shopping_cart_deployment.yaml
kubectl apply -f product_catalog_service.yaml
kubectl apply -f shopping_cart_service.yaml

# 6. Verify Pod node distribution across the 3 nodes
kubectl get pods -o wide

# 7. Test application endpoints via service tunnels
minikube -p devops-multinode service product-catalog-service --url
minikube -p devops-multinode service shopping-cart-service --url

curl http://127.0.0.1:35855/products
curl http://127.0.0.1:38975/cart
curl -X POST http://127.0.0.1:38975/cart -H "Content-Type: application/json" -d '{"id": 1, "name": "Laptop", "quantity": 1}'
```

---

## Important Configuration & Code

| Component | Setting | Technical Rationale |
| :--- | :--- | :--- |
| **Cluster Topology** | `--nodes 3` | Creates one primary control-plane node and two worker nodes |
| **Pod Anti-Affinity** | `requiredDuringSchedulingIgnoredDuringExecution` | Strict scheduling rule forbidding Kubernetes from placing two identical service pods on the same host |
| **Topology Key** | `kubernetes.io/hostname` | The node label identifying unique physical/virtual machines |
| **Image Distribution** | `minikube image load` | Propagates local container images to all 3 nodes in the cluster |
| **Unit Testing** | `test_apps.py` | Validates GET `/products`, GET `/cart`, and POST `/cart` payload mutations |

---

## Output

### Test Execution Output (`test_apps.py`)
```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.018s

OK
```

### Multi-Node Pod Distribution Output (`kubectl get pods -o wide`)
```text
NAME                               READY   STATUS    RESTARTS   AGE   IP           NODE                   NOMINATED NODE
product-catalog-5fdfc7f5fb-2jlnv   1/1     Running   0          29s   10.244.1.3   devops-multinode-m02   <none>
product-catalog-5fdfc7f5fb-7v556   1/1     Running   0          29s   10.244.2.4   devops-multinode-m03   <none>
shopping-cart-788c48675b-7l4lx     1/1     Running   0          25s   10.244.0.4   devops-multinode       <none>
shopping-cart-788c48675b-d48w2     1/1     Running   0          25s   10.244.1.4   devops-multinode-m02   <none>
shopping-cart-788c48675b-hml9r     1/1     Running   0          25s   10.244.2.5   devops-multinode-m03   <none>
```

### REST Endpoint Verification Output
```text
$ curl http://127.0.0.1:35855/products
[
  {"id": 1, "name": "Laptop", "price": 1200},
  {"id": 2, "name": "Phone", "price": 800},
  {"id": 3, "name": "Headphones", "price": 150}
]

$ curl http://127.0.0.1:38975/cart
[]

$ curl -X POST http://127.0.0.1:38975/cart -H "Content-Type: application/json" -d '{"id": 1, "name": "Laptop", "quantity": 1}'
[
  {"id": 1, "name": "Laptop", "quantity": 1}
]
```

---

## Verification
- **Anti-Affinity Verification**: As shown in the node distribution table, Product Catalog replicas are strictly scheduled onto separate nodes (`devops-multinode-m02` and `devops-multinode-m03`), and Shopping Cart replicas are balanced across all three nodes (`devops-multinode`, `devops-multinode-m02`, `devops-multinode-m03`).
- **REST Endpoints Verified**: `test_apps.py` passed with 100% success on both microservice applications.
- **Manifest Syntax Conformance**: All four Kubernetes YAML manifests (`product_catalog_deployment.yaml`, `product_catalog_service.yaml`, `shopping_cart_deployment.yaml`, `shopping_cart_service.yaml`) parsed cleanly via PyYAML.

---

## Result / Conclusion
Exercise 10 is **COMPLETE**. The multi-application microservices, multi-node Kubernetes cluster topology, pod anti-affinity scheduling configurations, service manifests, and automated test suites are fully implemented and verified.
