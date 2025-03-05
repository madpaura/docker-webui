"""
Core operations for the Docker Web UI application.
"""

import streamlit as st
from typing import Optional, Dict, Any, Tuple

from modules import GitHandler
from utils import validate_dockerfile_content, validate_build_args
from utils.formatters import format_build_log, format_registry_url
from config import config


def clone_repository(repo_url: str, branch: str) -> bool:
    try:
        st.session_state.git_handler = GitHandler(repo_url, branch)
        success, message = st.session_state.git_handler.clone()
        
        if success:
            st.success(message)
            # List available Dockerfiles
            st.session_state.available_dockerfiles = st.session_state.git_handler.list_dockerfile_paths()
            if st.session_state.available_dockerfiles:
                st.session_state.dockerfile_path = st.session_state.available_dockerfiles[0]
            return True
        else:
            st.error(message)
            return False
    except Exception as e:
        st.error(f"Error cloning repository: {str(e)}")
        return False


def load_dockerfile(silent: bool = False) -> bool:

    if not st.session_state.git_handler:
        if not silent:
            st.error("Git repository not initialized")
        return False
    
    try:
        # Try to load the default Dockerfile first
        success, content = st.session_state.git_handler.read_dockerfile(st.session_state.dockerfile_path)
        
        if success:
            st.session_state.dockerfile_content = content
            return True
        else:
            # If the default Dockerfile is not found, try to find any Dockerfile
            dockerfile_paths = st.session_state.git_handler.list_dockerfile_paths()
            
            if dockerfile_paths:
                # Use the first available Dockerfile
                st.session_state.dockerfile_path = dockerfile_paths[0]
                success, content = st.session_state.git_handler.read_dockerfile(st.session_state.dockerfile_path)
                
                if success:
                    st.session_state.dockerfile_content = content
                    return True
            
            # If we still don't have a Dockerfile, show an error
            if not silent:
                st.error(content)  # Error message is returned in the content
            return False
    except Exception as e:
        if not silent:
            st.error(f"Error loading Dockerfile: {str(e)}")
        return False


def save_dockerfile(content: str) -> bool:

    if not st.session_state.git_handler:
        st.error("Git repository not initialized")
        return False
    
    try:
        # Validate Dockerfile content
        is_valid, error_message = validate_dockerfile_content(content)
        if not is_valid:
            st.error(error_message)
            return False
        
        # Save the content
        success, message = st.session_state.git_handler.write_dockerfile(
            content, st.session_state.dockerfile_path
        )
        
        if success:
            st.session_state.dockerfile_content = content
            st.success(message)
            return True
        else:
            st.error(message)
            return False
    except Exception as e:
        st.error(f"Error saving Dockerfile: {str(e)}")
        return False


def build_docker_image(repository: str, tag: str, build_args: Optional[Dict[str, str]] = None) -> bool:
    if not st.session_state.git_handler:
        st.error("Git repository not initialized")
        return False
    
    try:
        # Get the Dockerfile path
        dockerfile_path = st.session_state.git_handler.get_dockerfile_path(st.session_state.dockerfile_path)
        
        # Build the image
        full_tag = f"{repository}:{tag}"
        
        with st.spinner(f"Building Docker image {full_tag}..."):
            success, logs, image_id = st.session_state.docker_handler.build_image(
                dockerfile_path=dockerfile_path,
                tag=full_tag,
                build_args=build_args
            )
        
        # Store build logs
        st.session_state.build_logs = format_build_log(logs)
        
        if success:
            st.session_state.build_success = True
            st.session_state.image_id = image_id
            st.success(f"Successfully built Docker image: {full_tag}")
            return True
        else:
            st.session_state.build_success = False
            st.session_state.image_id = None
            st.error("Build failed. Check the logs for details.")
            return False
    except Exception as e:
        st.error(f"Error building Docker image: {str(e)}")
        st.session_state.build_success = False
        return False


def push_to_registry(repository: str, tag: str) -> bool:
    if not st.session_state.build_success or not st.session_state.image_id:
        st.error("No successfully built image to push")
        return False
    
    # Get registry URL from settings
    registry_url = config.registry.url
    
    # Clean registry URL for proper tagging
    clean_registry_url = registry_url
    if clean_registry_url.startswith(('http://', 'https://')):
        clean_registry_url = clean_registry_url.split('://', 1)[1]
    if clean_registry_url.endswith('/'):
        clean_registry_url = clean_registry_url[:-1]
    
    try:
        # Create full tag with registry URL
        with st.spinner(f"Tagging and pushing image {repository}:{tag} to registry {registry_url}..."):
            # First tag the image with the registry URL
            full_tag = f"{clean_registry_url}/{repository}:{tag}"
            st.success(full_tag)
            tag_success, tag_message = st.session_state.docker_handler.tag_image(st.session_state.image_id, full_tag)
            
            if not tag_success:
                st.error(f"Failed to tag image: {tag_message}")
                return False
            
            # Then push the image to the registry
            success, message = st.session_state.docker_handler.push_image(full_tag)
        
        if success:
            st.success(f"Successfully pushed image to registry: {format_registry_url(registry_url, repository, tag)}")
            return True
        else:
            st.error(message)
            return False
    except Exception as e:
        st.error(f"Error pushing image to registry: {str(e)}")
        return False


def commit_dockerfile_changes(commit_message: str) -> bool:

    if not st.session_state.git_handler:
        st.error("Git repository not initialized")
        return False
    
    try:
        with st.spinner("Committing changes to Git repository..."):
            success, message = st.session_state.git_handler.commit_changes(
                commit_message, st.session_state.dockerfile_path
            )
        
        if success:
            st.success(message)
            
            # Push changes to remote repository
            push_success, push_message = st.session_state.git_handler.push_changes()
            if push_success:
                st.success(push_message)
                return True
            else:
                st.error(push_message)
                return False
        else:
            st.error(message)
            return False
    except Exception as e:
        st.error(f"Error committing changes: {str(e)}")
        return False


def parse_build_args(build_args_text: str) -> Tuple[bool, Dict[str, str], str]:
    build_args = {}
    
    if not build_args_text.strip():
        return True, {}, ""
    
    try:
        for line in build_args_text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" not in line:
                return False, {}, f"Invalid build argument format: {line}. Expected format: KEY=VALUE"
            
            key, value = line.split("=", 1)
            build_args[key.strip()] = value.strip()
        
        # Validate build args
        is_valid, error_message, validated_args = validate_build_args(build_args)
        if not is_valid:
            return False, {}, error_message
        
        return True, validated_args, ""
    except Exception as e:
        return False, {}, f"Error parsing build arguments: {str(e)}"
