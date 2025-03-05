"""Configuration management for the Docker Web UI application."""

import os
import socket
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Detect if running in Docker Compose environment
def is_docker_compose():
    """Check if running in Docker Compose environment."""
    # Check if running in Docker container
    if os.path.exists('/.dockerenv'):
        # Try to resolve the 'registry' hostname which would be available in Docker Compose network
        try:
            socket.gethostbyname('registry')
            return True
        except socket.gaierror:
            pass
    return False

# Adjust registry URL if running in Docker Compose
DEFAULT_REGISTRY_URL = "registry:5000" if is_docker_compose() else "localhost:5000"

class GitConfig(BaseModel):
    """Git configuration settings."""
    username: str = Field(default_factory=lambda: os.getenv("GIT_USERNAME", ""))
    email: str = Field(default_factory=lambda: os.getenv("GIT_EMAIL", ""))
    token: Optional[str] = Field(default_factory=lambda: os.getenv("GIT_TOKEN", None))

class RegistryConfig(BaseModel):
    """Docker registry configuration settings."""
    url: str = Field(default_factory=lambda: os.getenv("REGISTRY_URL", DEFAULT_REGISTRY_URL))
    username: Optional[str] = Field(default_factory=lambda: os.getenv("REGISTRY_USERNAME", None))
    password: Optional[str] = Field(default_factory=lambda: os.getenv("REGISTRY_PASSWORD", None))
    
    def __init__(self, **data):
        super().__init__(**data)
        # This will be updated by app_state.py when loading from storage
        self.url = os.getenv("REGISTRY_URL", DEFAULT_REGISTRY_URL)
        
class AppConfig(BaseModel):
    """Application configuration settings."""
    temp_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("TEMP_DIR", "/tmp/docker-webui"))
    )
    default_dockerfile_path: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_DOCKERFILE_PATH", "Dockerfile")
    )

class Config(BaseModel):
    """Main configuration class combining all settings."""
    git: GitConfig = Field(default_factory=GitConfig)
    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    app: AppConfig = Field(default_factory=AppConfig)

    def initialize(self):
        """Initialize configuration and create necessary directories."""
        os.makedirs(self.app.temp_dir, exist_ok=True)

# Create a global configuration instance
config = Config()
config.initialize()
