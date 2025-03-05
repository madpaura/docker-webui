#!/usr/bin/env python3
"""
Test script to verify Docker CLI Handler functionality
"""

import os
import sys
import tempfile
from pathlib import Path
from modules.docker_cli_handler import DockerCLIHandler

def test_docker_cli():
    """Test Docker CLI handler."""
    print("Testing Docker CLI handler...")
    
    try:
        # Initialize the Docker CLI handler
        docker_handler = DockerCLIHandler()
        
        # List images
        success, images, message = docker_handler.list_images()
        if success:
            print(f"✅ Successfully listed images: {len(images)} images found")
            for image in images[:5]:  # Show first 5 images
                print(f"   - {image.get('Repository')}:{image.get('Tag')}")
            if len(images) > 5:
                print(f"   ... and {len(images) - 5} more")
        else:
            print(f"❌ Failed to list images: {message}")
        
        # Create a simple test Dockerfile
        with tempfile.TemporaryDirectory() as temp_dir:
            dockerfile_path = Path(temp_dir) / "Dockerfile"
            with open(dockerfile_path, "w") as f:
                f.write("FROM alpine:latest\nCMD [\"echo\", \"Hello from test image\"]")
            
            # Build the test image
            print("\nBuilding test image...")
            success, message, image_id = docker_handler.build_image(
                dockerfile_path=dockerfile_path,
                tag="test-cli-image:latest",
                build_args={"TEST_ARG": "test_value"}
            )
            
            if success:
                print(f"✅ {message}")
                print(f"   Image ID: {image_id}")
                return True
            else:
                print(f"❌ {message}")
                return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_docker_cli()
    sys.exit(0 if success else 1)
