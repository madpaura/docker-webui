"""
Utility functions for the Docker Web UI application.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple


def validate_git_url(url: str) -> Tuple[bool, str]:
    """
    Validate a Git URL.

    Args:
        url: Git URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "Git URL is required"
    
    # Basic validation for common Git URL formats
    if re.match(r'^(https?|git|ssh)://', url) or re.match(r'^git@', url):
        return True, ""
    
    return False, "Invalid Git URL format"


def validate_docker_tag(tag: str) -> Tuple[bool, str]:
    """
    Validate a Docker tag.

    Args:
        tag: Docker tag to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tag:
        return False, "Tag is required"
    
    # Docker tag validation
    if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$', tag):
        return True, ""
    
    return False, "Invalid Docker tag format"


def validate_docker_repository(repository: str) -> Tuple[bool, str]:
    """
    Validate a Docker repository name.

    Args:
        repository: Docker repository name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not repository:
        return False, "Repository name is required"
    
    # Docker repository name validation
    if re.match(r'^[a-z0-9]+(?:[._-][a-z0-9]+)*$', repository):
        return True, ""
    
    return False, "Invalid Docker repository name format"


def validate_registry_url(url: str) -> Tuple[bool, str]:
    """
    Validate a Docker registry URL.

    Args:
        url: Registry URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "Registry URL is required"
    
    # Basic URL validation
    if re.match(r'^(https?://)?[a-zA-Z0-9][-a-zA-Z0-9.]*(\.[a-zA-Z0-9][-a-zA-Z0-9.]*)*(:[0-9]+)?$', url):
        return True, ""
    
    return False, "Invalid registry URL format"


def validate_dockerfile_content(content: str) -> Tuple[bool, str]:
    """
    Validate Dockerfile content.

    Args:
        content: Dockerfile content to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content:
        return False, "Dockerfile content is required"
    
    # Check for FROM instruction
    if not re.search(r'^\s*FROM\s+', content, re.MULTILINE):
        return False, "Dockerfile must contain a FROM instruction"
    
    return True, ""


def validate_build_args(build_args: Dict[str, str]) -> Tuple[bool, str]:
    """
    Validate build arguments.

    Args:
        build_args: Build arguments to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    for key, value in build_args.items():
        if not key or not re.match(r'^[a-zA-Z0-9_]+$', key):
            return False, f"Invalid build argument key: {key}"
    
    return True, ""


def format_docker_images(images: List[Dict[str, Any]]) -> str:
    """
    Format Docker images list for display.

    Args:
        images: List of Docker images

    Returns:
        Formatted string
    """
    if not images:
        return "No images found"
    
    formatted = []
    for image in images:
        repo_tag = f"{image.get('Repository', 'N/A')}:{image.get('Tag', 'N/A')}"
        image_id = image.get('ID', 'N/A')
        size = image.get('Size', 'N/A')
        created = image.get('CreatedAt', 'N/A')
        
        formatted.append(f"- {repo_tag} (ID: {image_id}, Size: {size}, Created: {created})")
    
    return "\n".join(formatted)


def format_build_log(logs: List[Dict[str, Any]]) -> str:
    """
    Format build logs for display.

    Args:
        logs: Build logs

    Returns:
        Formatted string
    """
    if not logs:
        return "No logs available"
    
    formatted = []
    for entry in logs:
        if 'stream' in entry:
            formatted.append(entry['stream'].rstrip())
        elif 'error' in entry:
            formatted.append(f"ERROR: {entry['error']}")
        elif 'status' in entry:
            if 'progressDetail' in entry and entry['progressDetail']:
                progress = entry['progressDetail'].get('current', 0)
                total = entry['progressDetail'].get('total', 0)
                if total > 0:
                    percentage = int(progress / total * 100)
                    formatted.append(f"{entry['status']} - {percentage}%")
                else:
                    formatted.append(entry['status'])
            else:
                formatted.append(entry['status'])
        else:
            formatted.append(str(entry))
    
    return "\n".join(formatted)


def format_dockerfile_for_display(content: str) -> str:
    """
    Format Dockerfile content for display.

    Args:
        content: Dockerfile content

    Returns:
        Formatted string with syntax highlighting markers
    """
    if not content:
        return ""
    
    # Add syntax highlighting markers
    return f"```dockerfile\n{content}\n```"


def format_repository_name(repository: str, tag: str) -> str:
    """
    Format repository name with tag.

    Args:
        repository: Repository name
        tag: Tag

    Returns:
        Formatted repository name
    """
    return f"{repository}:{tag}"


def format_error_message(message: str) -> str:
    """
    Format error message.

    Args:
        message: Error message

    Returns:
        Formatted error message
    """
    return f"Error: {message}"


def format_success_message(message: str) -> str:
    """
    Format success message.

    Args:
        message: Success message

    Returns:
        Formatted success message
    """
    return f"Success: {message}"


def format_registry_url(url: str) -> str:
    """
    Format registry URL.

    Args:
        url: Registry URL

    Returns:
        Formatted registry URL
    """
    # Ensure URL has protocol
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    
    # Ensure URL has trailing slash
    if not url.endswith("/"):
        url = f"{url}/"
    
    return url
