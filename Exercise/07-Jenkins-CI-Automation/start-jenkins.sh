#!/usr/bin/env bash
set -e

echo "=== Exercise 7: Jenkins Installation & CI Setup with Docker ==="

# 1. Start Jenkins container
echo "Starting Jenkins LTS container..."
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

echo "Waiting for Jenkins to initialize (approx 20 seconds)..."
sleep 20

# 2. Check container status
docker ps --filter "name=jenkins"

# 3. Retrieve Initial Admin Password
echo "Retrieving Jenkins Initial Admin Password:"
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword || true

echo "Access Jenkins at: http://localhost:8080"
