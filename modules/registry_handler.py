"""Docker registry operations module."""

import json
import requests
import urllib3
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urljoin

from config import config

# Suppress SSL warnings for local development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RegistryHandler:
    """Handles Docker registry operations."""

    def __init__(self):
        """Initialize the RegistryHandler."""
        self.registry_url = config.registry.url
        self.username = config.registry.username
        self.password = config.registry.password
        
        # Ensure the registry URL has the correct format
        if not self.registry_url.startswith(("http://", "https://")):
            self.registry_url = f"http://{self.registry_url}"
        
        # Add trailing slash if missing
        if not self.registry_url.endswith("/"):
            self.registry_url = f"{self.registry_url}/"
        
        self.api_url = urljoin(self.registry_url, "v2/")

    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get authentication header for registry API requests.

        Returns:
            Authentication header dict
        """
        headers = {}
        if self.username and self.password:
            import base64
            auth_string = f"{self.username}:{self.password}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_auth}"
        return headers

    def check_connection(self) -> Tuple[bool, str]:
        """
        Check connection to the registry.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Print debug information
            print(f"Attempting to connect to registry at: {self.registry_url}")
            print(f"API URL: {self.api_url}")
            
            # Try with a longer timeout
            response = requests.get(
                self.api_url,
                headers=self._get_auth_header(),
                timeout=10,
                verify=False  # Disable SSL verification for local registries
            )
            
            print(f"Registry response status code: {response.status_code}")
            
            if response.status_code == 200:
                return True, f"Successfully connected to registry at {self.registry_url}"
            else:
                return False, f"Failed to connect to registry: {response.status_code} {response.reason}"
        except requests.RequestException as e:
            return False, f"Error connecting to registry: {str(e)}"

    def list_repositories(self) -> Tuple[bool, List[str], str]:
        """
        List all repositories in the registry.

        Returns:
            Tuple of (success, repositories list, message)
        """
        try:
            response = requests.get(
                urljoin(self.api_url, "_catalog"),
                headers=self._get_auth_header(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                repositories = data.get("repositories", [])
                return True, repositories, f"Found {len(repositories)} repositories"
            else:
                return False, [], f"Failed to list repositories: {response.status_code} {response.reason}"
        except requests.RequestException as e:
            return False, [], f"Error listing repositories: {str(e)}"
        except json.JSONDecodeError:
            return False, [], "Error parsing registry response"

    def list_tags(self, repository: str) -> Tuple[bool, List[str], str]:
        """
        List all tags for a repository.

        Args:
            repository: Repository name

        Returns:
            Tuple of (success, tags list, message)
        """
        try:
            response = requests.get(
                urljoin(self.api_url, f"{repository}/tags/list"),
                headers=self._get_auth_header(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tags = data.get("tags", [])
                return True, tags, f"Found {len(tags)} tags for repository {repository}"
            elif response.status_code == 404:
                return False, [], f"Repository {repository} not found"
            else:
                return False, [], f"Failed to list tags: {response.status_code} {response.reason}"
        except requests.RequestException as e:
            return False, [], f"Error listing tags: {str(e)}"
        except json.JSONDecodeError:
            return False, [], "Error parsing registry response"

    def get_image_manifest(self, repository: str, tag: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get manifest for an image.

        Args:
            repository: Repository name
            tag: Tag name

        Returns:
            Tuple of (success, manifest dict, message)
        """
        try:
            headers = self._get_auth_header()
            # Add accept headers for manifest v2
            headers["Accept"] = "application/vnd.docker.distribution.manifest.v2+json"
            
            response = requests.get(
                urljoin(self.api_url, f"{repository}/manifests/{tag}"),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                manifest = response.json()
                return True, manifest, "Successfully retrieved manifest"
            elif response.status_code == 404:
                return False, None, f"Image {repository}:{tag} not found"
            else:
                return False, None, f"Failed to get manifest: {response.status_code} {response.reason}"
        except requests.RequestException as e:
            return False, None, f"Error getting manifest: {str(e)}"
        except json.JSONDecodeError:
            return False, None, "Error parsing manifest response"

    def delete_image(self, repository: str, tag: str) -> Tuple[bool, str]:
        """
        Delete an image from the registry.

        Args:
            repository: Repository name
            tag: Tag name

        Returns:
            Tuple of (success, message)
        """
        try:
            # First, get the digest for the image
            success, manifest, message = self.get_image_manifest(repository, tag)
            if not success:
                return False, message
            
            digest = manifest.get("config", {}).get("digest")
            if not digest:
                return False, "Could not determine image digest"
            
            # Delete the image using the digest
            response = requests.delete(
                urljoin(self.api_url, f"{repository}/manifests/{digest}"),
                headers=self._get_auth_header(),
                timeout=10
            )
            
            if response.status_code in (202, 200):
                return True, f"Successfully deleted image {repository}:{tag}"
            elif response.status_code == 404:
                return False, f"Image {repository}:{tag} not found"
            else:
                return False, f"Failed to delete image: {response.status_code} {response.reason}"
        except requests.RequestException as e:
            return False, f"Error deleting image: {str(e)}"
