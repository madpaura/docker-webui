"""Formatting utilities for the Docker Web UI application."""

import datetime
from typing import Dict, Any, List, Optional
import humanize


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    return humanize.naturalsize(size_bytes)


def format_timestamp(timestamp: str) -> str:
    """
    Format ISO timestamp to human-readable format.

    Args:
        timestamp: ISO format timestamp

    Returns:
        Human-readable timestamp
    """
    try:
        dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return humanize.naturaltime(datetime.datetime.now(datetime.timezone.utc) - dt)
    except (ValueError, TypeError):
        return timestamp


def format_docker_image(image: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format Docker image information for display.

    Args:
        image: Docker image information

    Returns:
        Formatted image information
    """
    return {
        "id": image["id"][:12],  # Short ID
        "tags": image["tags"],
        "created": format_timestamp(image["created"]),
        "size": format_file_size(image["size"])
    }


def format_docker_images(images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format a list of Docker images for display.

    Args:
        images: List of Docker images

    Returns:
        Formatted list of images
    """
    return [format_docker_image(image) for image in images]


def format_build_log(log: str) -> str:
    """
    Format Docker build log for display.

    Args:
        log: Raw build log

    Returns:
        Formatted build log
    """
    # Remove ANSI color codes
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    log = ansi_escape.sub('', log)
    
    # Replace multiple newlines with a single newline
    log = re.sub(r'\n+', '\n', log)
    
    return log.strip()


def format_dockerfile_for_display(content: str) -> str:
    """
    Format Dockerfile content for display in the UI.

    Args:
        content: Raw Dockerfile content

    Returns:
        Formatted Dockerfile content
    """
    # Add line numbers
    lines = content.split('\n')
    numbered_lines = [f"{i+1:3d} | {line}" for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)


def format_repository_name(repo_url: str) -> str:
    """
    Format repository URL to a display name.

    Args:
        repo_url: Repository URL

    Returns:
        Repository display name
    """
    # Extract repository name from URL
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    
    # Handle both HTTPS and SSH URLs
    if '/' in repo_url:
        return repo_url.split('/')[-1]
    elif ':' in repo_url:
        return repo_url.split(':')[-1].split('/')[-1]
    else:
        return repo_url


def format_error_message(message: str) -> str:
    """
    Format error message for display.

    Args:
        message: Error message

    Returns:
        Formatted error message
    """
    return f"❌ {message}"


def format_success_message(message: str) -> str:
    """
    Format success message for display.

    Args:
        message: Success message

    Returns:
        Formatted success message
    """
    return f"✅ {message}"


def format_registry_url(registry_url: str, repository: str, tag: str) -> str:
    """
    Format full registry URL for an image.

    Args:
        registry_url: Registry URL
        repository: Repository name
        tag: Tag name

    Returns:
        Full registry URL for the image
    """
    # Remove protocol if present
    if registry_url.startswith(('http://', 'https://')):
        registry_url = registry_url.split('://', 1)[1]
    
    # Remove trailing slash if present
    if registry_url.endswith('/'):
        registry_url = registry_url[:-1]
    
    return f"{registry_url}/{repository}:{tag}"
