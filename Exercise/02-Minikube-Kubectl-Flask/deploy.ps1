Write-Host "=== Exercise 2: Deploy Flask App on Minikube ===" -ForegroundColor Cyan

# 1. Start Minikube if needed
Write-Host "Checking Minikube..."
try { minikube status } catch { minikube start }

# 2. Build image
Write-Host "Configuring Docker and Building Image..."
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
docker build -t flask-app:latest .

# 3. Apply deployment
Write-Host "Applying Kubernetes manifests..."
kubectl apply -f flask-deployment.yaml

# 4. Check status
Write-Host "Checking Deployment and Service status..."
kubectl get deployments flask-app
kubectl get pods -l app=flask-app
kubectl get svc flask-app-service

# 5. Open service
Write-Host "Retrieving Service URL..."
minikube service flask-app-service --url
