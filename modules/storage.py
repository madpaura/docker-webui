"""
Persistent storage module for Docker Web UI application.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from config import config


class Storage:
    """Handles persistent storage operations using SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the Storage handler.

        Args:
            db_path: Path to the SQLite database file (default: config.app.temp_dir / 'settings.db')
        """
        if db_path is None:
            db_path = config.app.temp_dir / 'settings.db'
        
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the database with required tables."""
        os.makedirs(self.db_path.parent, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        # Create git_repositories table to store recent repositories
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS git_repositories (
            url TEXT PRIMARY KEY,
            branch TEXT NOT NULL,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value by key.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            try:
                return json.loads(result[0])
            except json.JSONDecodeError:
                return result[0]
        return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a setting value.

        Args:
            key: Setting key
            value: Setting value (will be JSON serialized)

        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert value to JSON string if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)
        
        cursor.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, value)
        )
        
        conn.commit()
        conn.close()
        return True
    
    def delete_setting(self, key: str) -> bool:
        """
        Delete a setting by key.

        Args:
            key: Setting key

        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM settings WHERE key = ?', (key,))
        
        conn.commit()
        conn.close()
        return True
    
    def add_git_repository(self, url: str, branch: str) -> bool:
        """
        Add or update a git repository in the history.

        Args:
            url: Repository URL
            branch: Repository branch

        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO git_repositories (url, branch, last_used) VALUES (?, ?, CURRENT_TIMESTAMP)',
            (url, branch)
        )
        
        conn.commit()
        conn.close()
        return True
    
    def get_recent_repositories(self, limit: int = 5) -> List[Dict[str, str]]:
        """
        Get recent git repositories.

        Args:
            limit: Maximum number of repositories to return

        Returns:
            List of repository dictionaries with 'url' and 'branch' keys
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT url, branch FROM git_repositories ORDER BY last_used DESC LIMIT ?',
            (limit,)
        )
        results = cursor.fetchall()
        
        conn.close()
        
        return [{'url': url, 'branch': branch} for url, branch in results]


# Create a global storage instance
storage = Storage()
