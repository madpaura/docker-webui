"""Docker operations module using CLI commands instead of SDK."""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any, Iterator, Union

from config import config


class DockerCLIHandler:
    """Handles Docker image operations using CLI commands."""

    def __init__(self):
        """Initialize the DockerCLIHandler."""
        # Check if Docker CLI is available
        try:
            result = subprocess.run(
                ["docker", "version", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                check=True
            )
            self.docker_info = json.loads(result.stdout)
            print(f"Successfully connected to Docker daemon using CLI")
            print(f"Docker version: {self.docker_info.get('Server', {}).get('Version', 'unknown')}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to initialize Docker client: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Docker version: {str(e)}")

    def build_image(
        self, 
        dockerfile_path: Path, 
        tag: str, 
        build_args: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Build a Docker image from a Dockerfile.

        Args:
            dockerfile_path: Path to the Dockerfile
            tag: Tag for the image
            build_args: Build arguments

        Returns:
            Tuple of (success, message, image_id)
        """
        try:
            # Prepare build command
            cmd = ["docker", "build", "-f", str(dockerfile_path), "-t", tag]
            
            # Add build args if provided
            if build_args:
                for key, value in build_args.items():
                    cmd.extend(["--build-arg", f"{key}={value}"])
            
            # Add context directory
            cmd.append(str(dockerfile_path.parent))
            
            # Run the build command
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                # Extract image ID from the output
                for line in process.stdout.splitlines():
                    if "Successfully built" in line:
                        image_id = line.split()[-1]
                        return True, f"Successfully built image: {tag}", image_id
                
                return True, f"Successfully built image: {tag}", None
            else:
                return False, f"Failed to build image: {process.stderr}", None
        except Exception as e:
            return False, f"Error building image: {str(e)}", None

    def tag_image(self, source_tag: str, target_tag: str) -> Tuple[bool, str]:
        try:
            process = subprocess.run(
                ["docker", "tag", source_tag, target_tag],
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                return True, f"Successfully tagged {source_tag} as {target_tag}"
            else:
                return False, f"Failed to tag image: {process.stderr}"
        except Exception as e:
            return False, f"Error tagging image: {str(e)}"

    def push_image(self, repository_or_full_tag: str, tag: str = None) -> Tuple[bool, str]:
        try:
            # If tag is None, assume repository_or_full_tag is a full tag
            # Otherwise, construct the full tag from repository and tag
            if tag is None:
                full_tag = repository_or_full_tag
            else:
                full_tag = f"{repository_or_full_tag}:{tag}"
                
            process = subprocess.run(
                ["docker", "push", full_tag],
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                return True, f"Successfully pushed image: {full_tag}"
            else:
                return False, f"Failed to push image: {process.stderr}"
        except Exception as e:
            return False, f"Error pushing image: {str(e)}"

    def list_images(self) -> Tuple[bool, List[Dict[str, Any]], str]:
        try:
            process = subprocess.run(
                ["docker", "images", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                images = []
                for line in process.stdout.splitlines():
                    if line.strip():
                        images.append(json.loads(line))
                
                return True, images, f"Found {len(images)} images"
            else:
                return False, [], f"Failed to list images: {process.stderr}"
        except Exception as e:
            return False, [], f"Error listing images: {str(e)}"

    def get_build_logs(self, build_output: str) -> List[Dict[str, Any]]:
        logs = []
        for line in build_output.splitlines():
            if line.strip():
                logs.append({"stream": line})
        
        return logs
