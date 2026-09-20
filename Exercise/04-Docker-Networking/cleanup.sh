#!/usr/bin/env bash
echo "Stopping and removing containers..."
docker stop mysql redis flask 2>/dev/null || true
docker rm mysql redis flask 2>/dev/null || true

echo "Removing network 'my-bridge-net'..."
docker network rm my-bridge-net 2>/dev/null || true
echo "Cleanup complete."
