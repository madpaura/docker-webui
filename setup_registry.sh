#!/bin/bash

# Setup script for Docker Registry server

# Ensure Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Ensure Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create required directories
mkdir -p /tmp/docker-registry
mkdir -p /tmp/docker-webui

echo "Created directories:"
echo "  - /tmp/docker-registry (for registry data)"
echo "  - /tmp/docker-webui (for temporary files)"

# Check if registry is already running
if docker ps | grep -q "docker-registry"; then
    echo "Docker Registry is already running."
else
    # Start the registry using Docker Compose
    echo "Starting Docker Registry and Web UI..."
    docker-compose up -d
    
    # Check if startup was successful
    if [ $? -eq 0 ]; then
        echo "Docker Registry and Web UI started successfully!"
        echo "Registry URL: http://localhost:5000"
        echo "Web UI URL: http://localhost:8501"
    else
        echo "Failed to start Docker Registry and Web UI."
        exit 1
    fi
fi

# Print usage instructions
echo ""
echo "Usage:"
echo "  - To view registry contents: curl http://localhost:5000/v2/_catalog"
echo "  - To stop the registry: docker-compose down"
echo "  - To view logs: docker-compose logs -f"
echo ""
echo "The Docker Web UI is now available at: http://localhost:8501"
