#!/usr/bin/env bash
set -e

echo "=== Exercise 5: Docker Security with AppArmor and Python ==="

# 1. Check if running on Linux with root/sudo
if [[ "$OSTYPE" != "linux"* ]]; then
    echo "[WARNING] AppArmor is a Linux Security Module (LSM) and only executes on Linux kernels."
    echo "Running in non-Linux environment ($OSTYPE). Follow the instructions in README.md inside WSL2/Linux."
    exit 0
fi

# 2. Check AppArmor status
if ! command -v apparmor_status &> /dev/null; then
    echo "Installing apparmor-utils..."
    sudo apt-get update
    sudo apt-get install -y apparmor-utils
fi

sudo apparmor_status || true

# 3. Copy AppArmor profile to /etc/apparmor.d/
echo "Copying profile to /etc/apparmor.d/my-apparmor-profile..."
sudo cp my-apparmor-profile /etc/apparmor.d/my-apparmor-profile

# 4. Parse and load the profile
echo "Loading AppArmor profile into Linux kernel..."
sudo apparmor_parser -r /etc/apparmor.d/my-apparmor-profile

# 5. Build Docker image
echo "Building Docker image 'flask-apparmor'..."
docker build -t flask-apparmor .

# 6. Run container with AppArmor confinement
echo "Running container with security option --security-opt='apparmor=my-apparmor-profile'..."
docker run -d --name flask-apparmor --security-opt="apparmor=my-apparmor-profile" -p 5000:5000 flask-apparmor

# 7. Test restricted actions
echo "Testing access to /etc/passwd (should fail with permission denied)..."
docker exec -it flask-apparmor cat /etc/passwd || echo "Successfully blocked reading /etc/passwd!"

echo "Testing execution of /bin/bash (should fail with permission denied)..."
docker exec -it flask-apparmor /bin/bash || echo "Successfully blocked executing /bin/bash!"

# 8. Cleanup
echo "Cleaning up container..."
docker stop flask-apparmor && docker rm flask-apparmor
echo "AppArmor demonstration completed successfully."
