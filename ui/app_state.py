"""
Application state initialization and management.
"""

import os
import streamlit as st

from modules import GitHandler, RegistryHandler
from modules.docker_cli_handler import DockerCLIHandler
from modules.storage import storage  # Add this import
from config import config


def init_session_state():
    """Initialize the session state variables."""
    # Load git repository settings from persistent storage
    if "git_repo_url" not in st.session_state:
        st.session_state.git_repo_url = storage.get_setting("git_repo_url", "")
    if "git_branch" not in st.session_state:
        st.session_state.git_branch = storage.get_setting("git_branch", "main")
    if "previous_repo_url" not in st.session_state:
        st.session_state.previous_repo_url = ""
    if "previous_branch" not in st.session_state:
        st.session_state.previous_branch = ""
    if "dockerfile_path" not in st.session_state:
        st.session_state.dockerfile_path = "Dockerfile"
    if "dockerfile_content" not in st.session_state:
        st.session_state.dockerfile_content = ""
    if "build_success" not in st.session_state:
        st.session_state.build_success = False
    if "image_id" not in st.session_state:
        st.session_state.image_id = None
    if "build_logs" not in st.session_state:
        st.session_state.build_logs = ""
        
    # Load Docker image settings from persistent storage
    if "repository" not in st.session_state:
        st.session_state.repository = storage.get_setting("repository", "")
    if "tag" not in st.session_state:
        st.session_state.tag = storage.get_setting("tag", "latest")
    if "commit_message" not in st.session_state:
        st.session_state.commit_message = ""
    if "git_handler" not in st.session_state:
        st.session_state.git_handler = None
    if "available_dockerfiles" not in st.session_state:
        st.session_state.available_dockerfiles = []
    if "docker_handler" not in st.session_state:
        st.session_state.docker_handler = None
    if "registry_handler" not in st.session_state:
        st.session_state.registry_handler = None
        
    # Load registry settings from persistent storage
    if "registry_url" not in st.session_state:
        registry_url = storage.get_setting("registry_url", config.registry.url)
        st.session_state.registry_url = registry_url
        # Update config with persisted registry URL
        config.registry.url = registry_url
        
    # Load recent repositories
    if "recent_repositories" not in st.session_state:
        st.session_state.recent_repositories = storage.get_recent_repositories()


def init_handlers():
    """Initialize handlers for Docker and Registry operations."""
    try:
        # Use the CLI handler instead of the SDK handler
        st.session_state.docker_handler = DockerCLIHandler()
        st.session_state.registry_handler = RegistryHandler()
    except Exception as e:
        st.error(f"Error initializing handlers: {str(e)}")


def reload_repository():
    if ("git_repo_url" in st.session_state and st.session_state.git_repo_url and 
        "git_branch" in st.session_state and st.session_state.git_branch and
        ("git_handler" not in st.session_state or st.session_state.git_handler is None)):
        
        # Create the temp directory if it doesn't exist
        os.makedirs(config.app.temp_dir, exist_ok=True)
        
        # Silently try to re-clone the repository
        try:
            # Create a new GitHandler instance
            st.session_state.git_handler = GitHandler(st.session_state.git_repo_url, st.session_state.git_branch)
            
            # Check if the repository directory exists
            if st.session_state.git_handler.repo_path.exists():
                # If it exists, try to load the Dockerfile silently
                from core.operations import load_dockerfile
                load_dockerfile(silent=True)
            else:
                # If the directory doesn't exist, try to clone
                success, _ = st.session_state.git_handler.clone()
                if success:
                    # Try to load the Dockerfile silently
                    from core.operations import load_dockerfile
                    load_dockerfile(silent=True)
        except Exception:
            # Don't show error on silent reload
            pass


def save_git_repository_settings(url: str, branch: str):
    # Save to persistent storage
    storage.set_setting("git_repo_url", url)
    storage.set_setting("git_branch", branch)
    
    # Add to recent repositories
    if url:
        storage.add_git_repository(url, branch)
        # Refresh recent repositories list
        st.session_state.recent_repositories = storage.get_recent_repositories()


def save_registry_settings(registry_url: str):
    # Save to persistent storage
    storage.set_setting("registry_url", registry_url)
    
    # Update session state and config
    st.session_state.registry_url = registry_url
    config.registry.url = registry_url


def save_docker_image_settings(repository: str, tag: str):
    # Save to persistent storage
    storage.set_setting("repository", repository)
    storage.set_setting("tag", tag)