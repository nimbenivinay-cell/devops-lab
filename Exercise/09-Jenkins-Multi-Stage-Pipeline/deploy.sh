#!/usr/bin/env bash
set -e

echo "=== Exercise 9: Jenkins Multi-Stage Pipeline Execution ==="

WORKSPACE=$(pwd)
DEPLOY_DIR="${WORKSPACE}/python-app-deploy"

# Stage 1: Build
echo "[Stage 1: Build] Installing dependencies..."
pip install -r requirements.txt

# Stage 2: Test
echo "[Stage 2: Test] Running unit tests..."
python3 -m unittest discover -s .

# Stage 3: Deploy
echo "[Stage 3: Deploy] Deploying to ${DEPLOY_DIR}..."
mkdir -p "${DEPLOY_DIR}"
cp "${WORKSPACE}/app.py" "${DEPLOY_DIR}/"

# Stage 4: Run Application
echo "[Stage 4: Run Application] Launching application in background..."
nohup python3 "${DEPLOY_DIR}/app.py" > "${DEPLOY_DIR}/app.log" 2>&1 &
APP_PID=$!
echo "${APP_PID}" > "${DEPLOY_DIR}/app.pid"
sleep 2

# Stage 5: Test Application
echo "[Stage 5: Test Application] Verifying running application..."
python3 "${WORKSPACE}/test_app.py"

# Cleanup
echo "Stopping application daemon (PID ${APP_PID})..."
kill ${APP_PID} 2>/dev/null || true
rm -f "${DEPLOY_DIR}/app.pid"

echo "Pipeline completed successfully!"
