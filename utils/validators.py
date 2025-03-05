"""Validation utilities for the Docker Web UI application."""

import re
from typing import Tuple, Dict, Any, Optional
from urllib.parse import urlparse


def validate_git_url(url: str) -> Tuple[bool, str]:
    """
    Validate a Git repository URL.

    Args:
        url: Git repository URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if URL is empty
    if not url:
        return False, "Git URL cannot be empty"
    
    # Check for common Git URL formats
    # HTTPS format: https://github.com/username/repo.git
    # SSH format: git@github.com:username/repo.git
    https_pattern = r'^https?://[a-zA-Z0-9_.-]+\.[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:\.git)?$'
    ssh_pattern = r'^git@[a-zA-Z0-9_.-]+\.[a-zA-Z0-9_.-]+:[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+(?:\.git)?$'
    
    if re.match(https_pattern, url) or re.match(ssh_pattern, url):
        return True, ""
    
    return False, "Invalid Git URL format. Expected format: https://github.com/username/repo.git or git@github.com:username/repo.git"


def validate_docker_tag(tag: str) -> Tuple[bool, str]:
    """
    Validate a Docker image tag.

    Args:
        tag: Docker tag to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if tag is empty
    if not tag:
        return False, "Docker tag cannot be empty"
    
    # Docker tag validation according to Docker's naming rules
    # Lowercase letters, digits, and separators (period, underscore, or hyphen)
    # Must begin and end with alphanumeric character
    pattern = r'^[a-z0-9][a-z0-9._-]*[a-z0-9]$|^[a-z0-9]$'
    
    if re.match(pattern, tag):
        return True, ""
    
    return False, "Invalid Docker tag format. Tags must be lowercase, can contain digits, periods, underscores, or hyphens, and must begin and end with alphanumeric characters."


def validate_docker_repository(repository: str) -> Tuple[bool, str]:
    """
    Validate a Docker repository name.

    Args:
        repository: Docker repository name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if repository is empty
    if not repository:
        return False, "Docker repository cannot be empty"
    
    # Docker repository validation according to Docker's naming rules
    # Lowercase letters, digits, and separators (period, underscore, or hyphen)
    # Components separated by forward slashes
    # Must begin and end with alphanumeric character
    pattern = r'^[a-z0-9]+(?:[._-][a-z0-9]+)*(?:/[a-z0-9]+(?:[._-][a-z0-9]+)*)*$'
    
    if re.match(pattern, repository):
        return True, ""
    
    return False, "Invalid Docker repository format. Repository names must be lowercase, can contain digits, periods, underscores, or hyphens, and components must be separated by forward slashes."


def validate_registry_url(url: str) -> Tuple[bool, str]:
    """
    Validate a Docker registry URL.

    Args:
        url: Docker registry URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if URL is empty
    if not url:
        return False, "Registry URL cannot be empty"
    
    # Add http:// prefix if not present for urlparse
    if not url.startswith(('http://', 'https://')):
        url = f"http://{url}"
    
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Check if hostname is present
    if not parsed_url.netloc:
        return False, "Invalid registry URL format. Expected format: hostname:port or http(s)://hostname:port"
    
    return True, ""


def validate_dockerfile_content(content: str) -> Tuple[bool, str]:
    """
    Validate Dockerfile content.

    Args:
        content: Dockerfile content to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if content is empty
    if not content:
        return False, "Dockerfile content cannot be empty"
    
    # Check for required FROM instruction
    if not re.search(r'^\s*FROM\s+\S+', content, re.MULTILINE):
        return False, "Dockerfile must contain a FROM instruction"
    
    return True, ""


def validate_build_args(build_args: Optional[Dict[str, Any]]) -> Tuple[bool, str, Dict[str, str]]:
    """
    Validate Docker build arguments.

    Args:
        build_args: Dictionary of build arguments

    Returns:
        Tuple of (is_valid, error_message, validated_build_args)
    """
    if build_args is None:
        return True, "", {}
    
    validated_args = {}
    
    for key, value in build_args.items():
        # Validate key format
        if not re.match(r'^[a-zA-Z0-9_]+$', key):
            return False, f"Invalid build argument key: {key}. Keys must contain only alphanumeric characters and underscores.", {}
        
        # Convert value to string
        validated_args[key] = str(value)
    
    return True, "", validated_args
