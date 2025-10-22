#!/bin/bash
echo "🔍 Jules verifying Docker setup..."
docker login -u dreamaware --password-stdin <<< "${DOCKER_PASSWORD}"
docker pull dreamaware/jules:latest
docker run --rm dreamaware/jules:latest echo "✅ Jules container runs clean"
