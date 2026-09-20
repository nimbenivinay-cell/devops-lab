Write-Host "=== Exercise 4: Docker Networking with Multiple Containers ===" -ForegroundColor Cyan

# Task 1: Create Bridge Network
Write-Host "Creating bridge network 'my-bridge-net'..."
docker network create --driver bridge my-bridge-net

# Task 2: Verify Network
docker network ls

# Task 3: Inspect Network
docker network inspect my-bridge-net

# Task 4: Launch Containers
docker build -t flask-api .
docker run -d --name mysql --net=my-bridge-net -e MYSQL_ROOT_PASSWORD=rootpassword mysql:8.0
docker run -d --name redis --net=my-bridge-net redis:7-alpine
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api

# Task 5: Test Connectivity
docker exec -it flask ping -c 3 mysql
docker exec -it flask ping -c 3 redis
curl http://localhost:5001/about
