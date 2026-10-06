#!/usr/bin/env bash
echo "Cleaning up Exercise 9 deployment artifacts..."
if [ -f python-app-deploy/app.pid ]; then
    kill $(cat python-app-deploy/app.pid) 2>/dev/null || true
fi
rm -rf python-app-deploy
echo "Cleanup complete."
