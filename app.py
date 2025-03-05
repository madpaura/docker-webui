"""
Docker Web UI - A Streamlit application for building Docker images from Git repositories
and publishing them to a local registry server.
"""

import streamlit as st

from ui.app_state import init_session_state, init_handlers, reload_repository
from ui.components import (
    render_sidebar, render_edit_tab, render_build_tab, 
    render_logs_tab, render_publish_tab
)
from core.operations import (
    clone_repository, load_dockerfile, save_dockerfile,
    build_docker_image, push_to_registry, commit_dockerfile_changes
)


# Set page configuration
st.set_page_config(
    page_title="Docker Web UI",
    page_icon="🐳",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main application function."""
    # Initialize session state
    init_session_state()
    
    # Initialize handlers
    try:
        if "docker_handler" not in st.session_state or st.session_state.docker_handler is None or \
           "registry_handler" not in st.session_state or st.session_state.registry_handler is None:
            init_handlers()
            
        # Check if we need to reload the repository on refresh
        reload_repository()
    except Exception as e:
        st.error(f"Error initializing handlers: {str(e)}")
        st.info("Please check your Docker installation and try again.")
    
    # Application header
    st.title("🐳 Docker Web UI")
    st.markdown("""
    Build Docker images from Git repositories and publish them to a local registry server.
    """)
    
    # Render the sidebar
    repository, tag = render_sidebar(clone_repository, load_dockerfile, init_handlers)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Edit Dockerfile", "Build", "Logs", "Publish"])
    
    # Tab 1: Edit Dockerfile
    with tab1:
        should_reload = render_edit_tab(save_dockerfile)
        if should_reload:
            load_dockerfile()
    
    # Tab 2: Build
    with tab2:
        render_build_tab(repository, tag, build_docker_image)
    
    # Tab 3: Logs
    with tab3:
        render_logs_tab()
    
    # Tab 4: Publish
    with tab4:
        render_publish_tab(push_to_registry, commit_dockerfile_changes)


if __name__ == "__main__":
    main()
