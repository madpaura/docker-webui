#!/bin/bash

# Script to stop Docker Registry and Web UI

echo "Stopping Docker Registry and Web UI..."
docker-compose down

if [ $? -eq 0 ]; then
    echo "Docker Registry and Web UI stopped successfully."
    
    # Ask if user wants to clean up data
    read -p "Do you want to clean up registry data in /tmp/docker-registry? (y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        echo "Cleaning up registry data..."
        rm -rf /tmp/docker-registry
        echo "Registry data cleaned up."
    else
        echo "Registry data preserved in /tmp/docker-registry."
    fi
    
    # Ask if user wants to clean up temporary files
    read -p "Do you want to clean up temporary files in /tmp/docker-webui? (y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        echo "Cleaning up temporary files..."
        rm -rf /tmp/docker-webui
        echo "Temporary files cleaned up."
    else
        echo "Temporary files preserved in /tmp/docker-webui."
    fi
    
    echo "Cleanup completed."
else
    echo "Failed to stop Docker Registry and Web UI."
    exit 1
fi
