"""Git operations module for cloning, committing, and pushing Dockerfiles."""

import os
from pathlib import Path
from typing import Optional, Tuple, List
import git
from git import Repo, GitCommandError

from config import config


class GitHandler:
    """Handles Git repository operations."""

    def __init__(self, repo_url: str, branch: str = "main"):
        """
        Initialize the GitHandler.

        Args:
            repo_url: URL of the Git repository
            branch: Branch to checkout (default: main)
        """
        self.repo_url = repo_url
        self.branch = branch
        self.repo_name = self._extract_repo_name(repo_url)
        self.repo_path = config.app.temp_dir / self.repo_name
        self.repo: Optional[Repo] = None

    @staticmethod
    def _extract_repo_name(repo_url: str) -> str:
        """
        Extract repository name from URL.

        Args:
            repo_url: URL of the Git repository

        Returns:
            Repository name
        """
        # Handle both HTTPS and SSH URLs
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]
        return repo_url.split("/")[-1]

    def clone(self) -> Tuple[bool, str]:
        """
        Clone the repository.

        Returns:
            Tuple of (success, message)
        """
        try:
            if self.repo_path.exists():
                # Repository already exists, pull latest changes
                self.repo = Repo(self.repo_path)
                origin = self.repo.remotes.origin
                origin.pull()
                return True, f"Repository already exists. Pulled latest changes from {self.branch}."
            else:
                # Clone the repository
                if config.git.token:
                    # Use token for authentication if provided
                    auth_url = self.repo_url.replace("https://", f"https://{config.git.token}@")
                    self.repo = Repo.clone_from(auth_url, self.repo_path, branch=self.branch)
                else:
                    self.repo = Repo.clone_from(self.repo_url, self.repo_path, branch=self.branch)
                return True, f"Successfully cloned repository to {self.repo_path}"
        except GitCommandError as e:
            return False, f"Git error: {str(e)}"
        except Exception as e:
            return False, f"Error cloning repository: {str(e)}"

    def get_dockerfile_path(self, dockerfile_path: Optional[str] = None) -> Path:
        """
        Get the path to the Dockerfile.

        Args:
            dockerfile_path: Custom path to Dockerfile (relative to repo root)

        Returns:
            Path to the Dockerfile
        """
        if dockerfile_path is None:
            dockerfile_path = config.app.default_dockerfile_path
        return self.repo_path / dockerfile_path

    def read_dockerfile(self, dockerfile_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Read the Dockerfile content.

        Args:
            dockerfile_path: Custom path to Dockerfile (relative to repo root)

        Returns:
            Tuple of (success, content or error message)
        """
        try:
            file_path = self.get_dockerfile_path(dockerfile_path)
            if not file_path.exists():
                return False, f"Dockerfile not found at {file_path}"
            
            with open(file_path, "r") as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"Error reading Dockerfile: {str(e)}"

    def write_dockerfile(self, content: str, dockerfile_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Write content to the Dockerfile.

        Args:
            content: Content to write
            dockerfile_path: Custom path to Dockerfile (relative to repo root)

        Returns:
            Tuple of (success, message)
        """
        try:
            file_path = self.get_dockerfile_path(dockerfile_path)
            with open(file_path, "w") as f:
                f.write(content)
            return True, f"Successfully updated Dockerfile at {file_path}"
        except Exception as e:
            return False, f"Error writing to Dockerfile: {str(e)}"

    def commit_changes(self, message: str, dockerfile_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Commit changes to the Dockerfile.

        Args:
            message: Commit message
            dockerfile_path: Custom path to Dockerfile (relative to repo root)

        Returns:
            Tuple of (success, message)
        """
        try:
            if self.repo is None:
                return False, "Repository not initialized"
            
            # Configure Git user if provided
            if config.git.username and config.git.email:
                self.repo.config_writer().set_value("user", "name", config.git.username).release()
                self.repo.config_writer().set_value("user", "email", config.git.email).release()
            
            # Get the relative path to the Dockerfile
            if dockerfile_path is None:
                dockerfile_path = config.app.default_dockerfile_path
            
            # Stage the Dockerfile
            self.repo.git.add(dockerfile_path)
            
            # Check if there are changes to commit
            if not self.repo.is_dirty():
                return False, "No changes to commit"
            
            # Commit the changes
            self.repo.git.commit("-m", message)
            return True, f"Successfully committed changes with message: {message}"
        except GitCommandError as e:
            return False, f"Git error: {str(e)}"
        except Exception as e:
            return False, f"Error committing changes: {str(e)}"

    def push_changes(self) -> Tuple[bool, str]:
        """
        Push committed changes to the remote repository.

        Returns:
            Tuple of (success, message)
        """
        try:
            if self.repo is None:
                return False, "Repository not initialized"
            
            # Push the changes
            origin = self.repo.remotes.origin
            push_info = origin.push()
            
            # Check if push was successful
            if push_info[0].flags & push_info[0].ERROR:
                return False, f"Error pushing changes: {push_info[0].summary}"
            
            return True, "Successfully pushed changes to remote repository"
        except GitCommandError as e:
            return False, f"Git error: {str(e)}"
        except Exception as e:
            return False, f"Error pushing changes: {str(e)}"

    def list_dockerfile_paths(self) -> List[str]:
        """
        List all Dockerfiles in the repository.

        Returns:
            List of paths to Dockerfiles
        """
        if self.repo is None:
            return []
        
        dockerfile_paths = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file == "Dockerfile" or file.endswith(".dockerfile") or file.endswith(".Dockerfile"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                    dockerfile_paths.append(rel_path)
        
        return dockerfile_paths
        
    def get_latest_commit_info(self) -> Tuple[bool, dict]:
        """
        Get information about the latest commit.
        
        Returns:
            Tuple of (success, commit_info)
            commit_info contains: id, message, author, date
        """
        try:
            if self.repo is None:
                return False, {"error": "Repository not initialized"}
            
            # Get the latest commit
            commit = self.repo.head.commit
            
            # Format the commit info
            commit_info = {
                "id": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": f"{commit.author.name} <{commit.author.email}>",
                "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "full_id": commit.hexsha
            }
            
            return True, commit_info
        except Exception as e:
            return False, {"error": f"Error getting commit info: {str(e)}"}
    
    def get_branch_info(self) -> Tuple[bool, dict]:
        """
        Get information about the current branch.
        
        Returns:
            Tuple of (success, branch_info)
            branch_info contains: name, tracking_branch
        """
        try:
            if self.repo is None:
                return False, {"error": "Repository not initialized"}
            
            # Get the current branch
            branch = self.repo.active_branch
            
            # Get the tracking branch if available
            tracking_branch = None
            try:
                tracking_branch = self.repo.git.config(f"branch.{branch.name}.remote")
                if tracking_branch:
                    tracking_branch = f"{tracking_branch}/{self.repo.git.config(f'branch.{branch.name}.merge').split('/')[-1]}"
            except:
                pass
            
            # Format the branch info
            branch_info = {
                "name": branch.name,
                "tracking_branch": tracking_branch
            }
            
            return True, branch_info
        except Exception as e:
            return False, {"error": f"Error getting branch info: {str(e)}"}
