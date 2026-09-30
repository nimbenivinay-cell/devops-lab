#!/usr/bin/env bash
echo "Stopping and removing Jenkins container..."
docker stop jenkins 2>/dev/null || true
docker rm jenkins 2>/dev/null || true
rm -rf dist
echo "Cleanup complete."
