Write-Host "=== Exercise 7: Jenkins Installation & CI Setup ===" -ForegroundColor Cyan

# 1. Run container
Write-Host "Starting Jenkins container..."
docker run -d --name jenkins `
  -p 8080:8080 -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  jenkins/jenkins:lts

Write-Host "Waiting 25 seconds for initial admin password generation..."
Start-Sleep -Seconds 25

# 2. Retrieve Initial Admin Password
Write-Host "Retrieving Initial Admin Password:"
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

Write-Host "Navigate to http://localhost:8080 in your browser."
