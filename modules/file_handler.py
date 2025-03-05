"""File operations module for reading and writing files."""

from pathlib import Path
from typing import Tuple, List, Optional
import os
import shutil


class FileHandler:
    """Handles file operations."""

    @staticmethod
    def read_file(file_path: Path) -> Tuple[bool, str]:
        """
        Read the content of a file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (success, content or error message)
        """
        try:
            if not file_path.exists():
                return False, f"File not found at {file_path}"
            
            with open(file_path, "r") as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    @staticmethod
    def write_file(file_path: Path, content: str) -> Tuple[bool, str]:
        """
        Write content to a file.

        Args:
            file_path: Path to the file
            content: Content to write

        Returns:
            Tuple of (success, message)
        """
        try:
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w") as f:
                f.write(content)
            return True, f"Successfully wrote to {file_path}"
        except Exception as e:
            return False, f"Error writing to file: {str(e)}"

    @staticmethod
    def delete_file(file_path: Path) -> Tuple[bool, str]:
        """
        Delete a file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (success, message)
        """
        try:
            if not file_path.exists():
                return False, f"File not found at {file_path}"
            
            os.remove(file_path)
            return True, f"Successfully deleted {file_path}"
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"

    @staticmethod
    def list_files(directory_path: Path, pattern: Optional[str] = None) -> List[Path]:
        """
        List files in a directory, optionally matching a pattern.

        Args:
            directory_path: Path to the directory
            pattern: Optional glob pattern to match

        Returns:
            List of file paths
        """
        if not directory_path.exists():
            return []
        
        if pattern:
            return list(directory_path.glob(pattern))
        else:
            return [p for p in directory_path.iterdir() if p.is_file()]

    @staticmethod
    def ensure_directory(directory_path: Path) -> Tuple[bool, str]:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory

        Returns:
            Tuple of (success, message)
        """
        try:
            directory_path.mkdir(parents=True, exist_ok=True)
            return True, f"Directory {directory_path} is ready"
        except Exception as e:
            return False, f"Error creating directory: {str(e)}"

    @staticmethod
    def delete_directory(directory_path: Path, recursive: bool = False) -> Tuple[bool, str]:
        """
        Delete a directory.

        Args:
            directory_path: Path to the directory
            recursive: Whether to delete recursively

        Returns:
            Tuple of (success, message)
        """
        try:
            if not directory_path.exists():
                return False, f"Directory not found at {directory_path}"
            
            if recursive:
                shutil.rmtree(directory_path)
            else:
                os.rmdir(directory_path)
            
            return True, f"Successfully deleted directory {directory_path}"
        except Exception as e:
            return False, f"Error deleting directory: {str(e)}"
