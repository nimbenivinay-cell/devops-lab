#!/usr/bin/env bash
set -e

echo "=== Exercise 4: Docker Networking with Multiple Containers ==="

# Task 1: Create a Bridge Network
echo "Task 1: Creating custom bridge network 'my-bridge-net'..."
docker network create --driver bridge my-bridge-net || echo "Network may already exist."

# Task 2: Verify the Network
echo "Task 2: Listing networks..."
docker network ls | grep my-bridge-net

# Task 3: Inspect the Network
echo "Task 3: Inspecting my-bridge-net..."
docker network inspect my-bridge-net

# Task 4: Launch Containers
echo "Task 4a: Building Flask API image..."
docker build -t flask-api .

echo "Task 4b: Launching MySQL container..."
docker run -d --name mysql --net=my-bridge-net -e MYSQL_ROOT_PASSWORD=rootpassword mysql:8.0

echo "Task 4c: Launching Redis container..."
docker run -d --name redis --net=my-bridge-net redis:7-alpine

echo "Task 4d: Launching Flask container..."
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api

echo "Containers running on my-bridge-net:"
docker ps --filter "name=flask" --filter "name=mysql" --filter "name=redis"

# Task 5: Test Connectivity
echo "Task 5a: Pinging MySQL container from Flask container..."
docker exec -it flask ping -c 3 mysql

echo "Task 5b: Pinging Redis container from Flask container..."
docker exec -it flask ping -c 3 redis

echo "Task 5c: Testing HTTP endpoint /about..."
curl -s http://localhost:5001/about
echo ""

echo "Docker Networking demonstration successful!"
