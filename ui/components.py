"""
UI components for the Docker Web UI application.
"""

import streamlit as st
from streamlit_ace import st_ace
import streamlit.components.v1 as components
from typing import Tuple, Dict, Any, Optional

from modules import GitHandler
from utils import validate_git_url, validate_docker_repository, validate_docker_tag
from utils.formatters import format_registry_url
from config import config

# In the repository_settings_dialog function, update the code to:

@st.dialog("Repository Settings", width="small")
def repository_settings_dialog(clone_repository_callback, load_dockerfile_callback):
    """Render the repository settings as a dialog."""
    # Git repository URL
    repo_url = st.text_input(
        "Git Repository URL",
        value=st.session_state.git_repo_url,
        placeholder="https://github.com/username/repo.git",
        help="URL of the Git repository containing the Dockerfile"
    )
    
    # Recent repositories dropdown
    if "recent_repositories" in st.session_state and st.session_state.recent_repositories:
        recent_repos = st.session_state.recent_repositories
        repo_options = [f"{repo['url']} ({repo['branch']})" for repo in recent_repos]
        repo_options.insert(0, "Select a recent repository")
        
        selected_repo = st.selectbox(
            "Recent Repositories",
            options=repo_options,
            index=0
        )
        
        if selected_repo != "Select a recent repository":
            # Extract URL and branch from selection
            selected_url = selected_repo.split(" (")[0]
            selected_branch = selected_repo.split("(")[1].rstrip(")")
            
            # Use the selected repository if the button is clicked
            if st.button("Use Selected Repository"):
                repo_url = selected_url
                st.session_state.git_branch = selected_branch
    
    # Git branch
    branch = st.text_input(
        "Branch",
        value=st.session_state.git_branch,
        placeholder="main",
        help="Branch to checkout"
    )
    
    # Form submission buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Cancel"):
            st.rerun()  # Close the dialog by triggering a rerun
    
    with col2:
        if st.button("Clone Repository", type="primary"):
            # Validate Git URL
            is_valid, error_message = validate_git_url(repo_url)
            if not is_valid:
                st.error(error_message)
            else:
                # Store in session state for persistence
                st.session_state.git_repo_url = repo_url
                st.session_state.git_branch = branch
                
                # Save to persistent storage
                from ui.app_state import save_git_repository_settings
                save_git_repository_settings(repo_url, branch)
                
                # Clear previous repository data if URL or branch changed
                if ("previous_repo_url" in st.session_state and 
                    (st.session_state.previous_repo_url != repo_url or 
                     st.session_state.previous_branch != branch)):
                    # Clear previous repository data
                    st.session_state.dockerfile_content = ""
                    st.session_state.available_dockerfiles = []
                    st.session_state.build_logs = ""
                    st.session_state.build_success = False
                    st.session_state.image_id = None
                
                # Clone the repository
                if clone_repository_callback(repo_url, branch):
                    # Store current repo info for comparison on next clone
                    st.session_state.previous_repo_url = repo_url
                    st.session_state.previous_branch = branch
                    load_dockerfile_callback(silent=False)
                    st.rerun()  # Close the dialog and refresh the app

def render_repository_settings_modal(clone_repository_callback, load_dockerfile_callback):
    """Legacy function to maintain compatibility - now uses st.dialog."""
    # Initialize session state for settings dialog
    if 'show_settings' not in st.session_state:
        st.session_state.show_settings = False
    
    # If settings dialog should be shown, call the dialog function
    if st.session_state.show_settings:
        repository_settings_dialog(clone_repository_callback, load_dockerfile_callback)
        # Reset the flag after dialog is shown
        st.session_state.show_settings = False

def render_repository_info(git_handler: Optional[GitHandler] = None):
    """Render repository information in the sidebar."""
    if git_handler and git_handler.repo:
        # Get repository information
        success, commit_info = git_handler.get_latest_commit_info()
        branch_success, branch_info = git_handler.get_branch_info()
        
        if success:
            import pandas as pd
            # Create table data as dictionary
            table_data = {
                "Repo": git_handler.repo_name,
                "Branch": branch_info['name'] if branch_success else git_handler.branch,
                "Commit": commit_info['id'],
                "Log": commit_info['message'][:50] + ('...' if len(commit_info['message']) > 50 else ''),
                "Author": commit_info['author'].split('<')[0],
                "Date": commit_info['date']
            }
            # Convert to DataFrame and display without index
            df = pd.DataFrame(list(table_data.items()), columns=["Field", "Value"])
            st.dataframe(df, hide_index=True)
    else:
        st.info("No repository cloned yet")

def render_sidebar(clone_repository_callback, load_dockerfile_callback, init_handlers_callback):
    """Render the sidebar with repository and image configuration."""
    with st.sidebar:
        # Repository section with settings icon
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("Git Repo Config")
        with col2:
            # Settings icon button
            settings_icon = "⚙️"
            if st.button(settings_icon, key="settings_button"):
                st.session_state.show_settings = True
        
        # Render repository information if a repository is cloned
        if st.session_state.git_handler:
            render_repository_info(st.session_state.git_handler)
        else:
            st.info("Click the settings icon to configure and clone a repository")
        
        # Render settings modal
        render_repository_settings_modal(clone_repository_callback, load_dockerfile_callback)
        
        # Separator
        st.divider()
        
        # Image configuration
        st.header("Docker Image Configuration")
        
        # Repository name
        repository = st.text_input(
            "Docker Image Name",
            value=st.session_state.repository,
            placeholder="dv/qvp",
            help="Name of the Docker image"
        )
        
        # Tag
        tag = st.text_input(
            "Tag",
            value=st.session_state.tag,
            placeholder="latest",
            help="Tag for the Docker image"
        )
        
        # Save Docker image settings when changed
        if repository != st.session_state.repository or tag != st.session_state.tag:
            st.session_state.repository = repository
            st.session_state.tag = tag
            from ui.app_state import save_docker_image_settings
            save_docker_image_settings(repository, tag)
        
        # Registry URL
        st.divider()
        st.header("Registry Configuration")
        
        registry_url = st.text_input(
            "Registry URL",
            value=st.session_state.registry_url,
            placeholder="localhost:5000",
            help="URL of the Docker registry"
        )
        
        # Save registry URL when changed
        if registry_url != st.session_state.registry_url:
            from ui.app_state import save_registry_settings
            save_registry_settings(registry_url)
        
        if st.button("Check Registry Connection"):
            if st.session_state.registry_handler is None:
                st.error("Registry handler not initialized. Please refresh the page.")
                # Try to initialize handlers again
                try:
                    init_handlers_callback()
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Failed to initialize handlers: {str(e)}")
            else:
                try:
                    success, message = st.session_state.registry_handler.check_connection()
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                except Exception as e:
                    st.error(f"Error checking registry connection: {str(e)}")
    
    return repository, tag

def render_edit_tab(save_dockerfile_callback):
    """Render the Edit Dockerfile tab."""
    if st.session_state.git_handler:
        st.header("Edit Dockerfile")
        
        # Dockerfile selection if multiple are available
        if st.session_state.available_dockerfiles:
            selected_dockerfile = st.selectbox(
                "Select Dockerfile",
                options=st.session_state.available_dockerfiles,
                index=st.session_state.available_dockerfiles.index(st.session_state.dockerfile_path) 
                if st.session_state.dockerfile_path in st.session_state.available_dockerfiles else 0
            )
            
            if selected_dockerfile != st.session_state.dockerfile_path:
                st.session_state.dockerfile_path = selected_dockerfile
                return True  # Signal to load the new dockerfile
        
        # Dockerfile editor with syntax highlighting
        st.markdown("### Dockerfile Content")
        
        # Use the Ace editor with syntax highlighting
        dockerfile_content = st_ace(
            value=st.session_state.dockerfile_content,
            language="dockerfile",
            theme="monokai",
            font_size=14,
            min_lines=20,
            key="dockerfile_editor",
            height=500,
            show_gutter=True,
            wrap=True,
            auto_update=True,
            tab_size=2
        )
        
        # Update session state with the editor content
        if dockerfile_content:
            st.session_state.dockerfile_content = dockerfile_content
        
        # Save button
        if st.button("Save Dockerfile"):
            if save_dockerfile_callback(dockerfile_content):
                st.session_state.build_success = False  # Reset build status
    else:
        st.info("Please clone a Git repository to edit the Dockerfile")
    
    return False  # No need to load a new dockerfile


def render_build_tab(repository, tag, build_docker_image_callback):
    """Render the Build Docker Image tab."""
    if st.session_state.git_handler:
        st.header("Build Docker Image")
        
        # Show current configuration
        st.subheader("Build Configuration")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Repository:** {repository}")
            st.markdown(f"**Tag:** {tag}")
            st.markdown(f"**Dockerfile:** {st.session_state.dockerfile_path}")
        
        # Build button
        if st.button("Build Image"):
            # Validate inputs
            valid_repo, repo_error = validate_docker_repository(repository)
            valid_tag, tag_error = validate_docker_tag(tag)
            
            if not valid_repo:
                st.error(repo_error)
            elif not valid_tag:
                st.error(tag_error)
            else:
                st.session_state.repository = repository
                st.session_state.tag = tag
                build_docker_image_callback(repository, tag, None)
        
        # Show build status
        if st.session_state.build_success:
            st.success(f"Build successful! Image ID: {st.session_state.image_id[:12]}")
        elif st.session_state.build_logs:
            st.error("Build failed. Check the logs for details.")
    else:
        st.info("Please clone a Git repository to build a Docker image")


def render_logs_tab():
    """Render the Build Logs tab."""
    st.header("Build Logs")
    
    if st.session_state.build_logs:
        # Use Ace editor in read-only mode for better log display
        st_ace(
            value=st.session_state.build_logs,
            language="sh",
            theme="terminal",
            font_size=14,
            key="build_logs_viewer",
            height=500,
            show_gutter=True,
            wrap=True,
            readonly=True,  # Make it read-only
            auto_update=True
        )
    else:
        st.info("No build logs available. Build an image to see logs.")


def render_publish_tab(push_to_registry_callback, commit_dockerfile_changes_callback):
    """Render the Publish to Registry tab."""
    st.header("Publish to Registry")
    
    if st.session_state.build_success and st.session_state.image_id:
        st.success("Image built successfully and ready to publish")
        
        # Commit message
        commit_message = st.text_input(
            "Commit Message",
            value=st.session_state.commit_message,
            placeholder="Updated Dockerfile",
            help="Message for the Git commit"
        )
        
        # Publish button
        if st.button("Publish Image and Commit Changes"):
            if not commit_message:
                st.error("Please enter a commit message")
            else:
                st.session_state.commit_message = commit_message
                
                # Push to registry
                if push_to_registry_callback(st.session_state.repository, st.session_state.tag):
                    # Commit changes
                    commit_dockerfile_changes_callback(commit_message)
    else:
        st.info("Build an image successfully before publishing")


def render_registry_images_tab():
    """Render the Registry Images tab that lists available images remotely in the registry server."""
    st.header("Registry Images")
    
    # Registry URL information
    registry_url = st.session_state.registry_url
    st.subheader(f"Registry: {registry_url}")
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        refresh = st.button("🔄 Refresh")
    
    # Check connection to registry
    if not hasattr(st.session_state, "registry_images") or refresh:
        with st.spinner("Connecting to registry..."):
            # Check connection first
            connection_success, connection_message = st.session_state.registry_handler.check_connection()
            
            if connection_success:
                # List all images
                success, images, message = st.session_state.registry_handler.list_all_images()
                if success:
                    st.session_state.registry_images = images
                    st.session_state.registry_message = message
                else:
                    st.session_state.registry_images = []
                    st.session_state.registry_message = message
            else:
                st.error(f"Failed to connect to registry: {connection_message}")
                st.session_state.registry_images = []
                st.session_state.registry_message = connection_message
    
    # Display registry images
    if hasattr(st.session_state, "registry_images"):
        if st.session_state.registry_images:
            # Display images in an expandable format
            for repo_index, repo_data in enumerate(st.session_state.registry_images):
                repository = repo_data["repository"]
                tags = repo_data["tags"]
                
                with st.expander(f"📦 {repository} ({len(tags)} tags)"):
                    # Create a table for tags
                    if tags:
                        # Convert tag data to a format suitable for a dataframe
                        tag_data = []
                        for tag_info in tags:
                            tag_name = tag_info["tag"]
                            created = tag_info["created"]
                            size = tag_info["size"]
                            
                            # Format size to human-readable format
                            if size > 0:
                                size_str = f"{size / (1024 * 1024):.2f} MB"
                            else:
                                size_str = "Unknown"
                                
                            # Format created date if available
                            created_str = created[:19].replace("T", " ") if created else "Unknown"
                            
                            tag_data.append({
                                "Tag": tag_name,
                                "Created": created_str,
                                "Size": size_str,
                                "Full Name": f"{repository}:{tag_name}"
                            })
                        
                        # Display as a dataframe
                        import pandas as pd
                        df = pd.DataFrame(tag_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Add a button to pull the selected image
                        selected_tag = st.selectbox(
                            "Select a tag to pull",
                            options=[tag_info["tag"] for tag_info in tags],
                            key=f"select_tag_{repo_index}"
                        )
                        
                        if st.button(f"Pull {repository}:{selected_tag}", key=f"pull_button_{repo_index}"):
                            st.info(f"Pulling {repository}:{selected_tag} from {registry_url}...")
                            # This would need to be implemented in the Docker handler
                            st.warning("Pull functionality not yet implemented")
                    else:
                        st.info("No tags found for this repository")
        else:
            st.info("No images found in the registry")
            if hasattr(st.session_state, "registry_message"):
                st.info(st.session_state.registry_message)
