Write-Host "=== Exercise 3: Scaling Flask App with ReplicaSets ===" -ForegroundColor Cyan

# 1. Start Minikube if needed
Write-Host "Checking Minikube..."
try { minikube status } catch { minikube start --nodes=1 }

# 2. Build image
Write-Host "Configuring Docker environment and building image..."
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
docker build -t flashsale:1.0 .

# 3. Apply manifests
Write-Host "Applying ReplicaSet and Service manifests..."
kubectl apply -f flashsale-replicaset.yaml

# 4. Verify initial state
Write-Host "Verifying initial ReplicaSet (3 desired)..."
kubectl get rs flashsale-rs
kubectl get pods -l app=flashsale -o wide

# 5. Scale to 5
Write-Host "Scaling ReplicaSet to 5 replicas..."
kubectl scale rs flashsale-rs --replicas=5
kubectl get rs flashsale-rs
kubectl get pods -l app=flashsale -o wide

# 6. Service URL
Write-Host "Service URL:"
minikube service flashsale-svc --url
