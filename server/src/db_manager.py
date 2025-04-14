"""
Database Manager for the Energy Investment Decision Support System.

This module provides a unified interface for database operations including
user management, project storage, and data persistence.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
import sqlite3
import json
import os
import datetime
import uuid

class DatabaseManager:
    """Handles database interactions for the application."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database file (default: 'energy_tool.db' in the current directory)
        """
        self.db_path = db_path or os.environ.get('DB_PATH', 'energy_tool.db')
        
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Initialize database tables
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables if they don't exist."""
        # Create projects table
        projects_table = """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            location_lat REAL,
            location_lon REAL,
            parameters TEXT,
            results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        
        # Create shared projects table for collaboration
        shared_projects_table = """
        CREATE TABLE IF NOT EXISTS shared_projects (
            project_id TEXT,
            shared_with_id TEXT,
            permissions TEXT,
            shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (project_id, shared_with_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (shared_with_id) REFERENCES users(id)
        )
        """
        
        self.execute_query(projects_table)
        self.execute_query(shared_projects_table)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection.
        
        Returns:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        
        # Enable foreign keys
        conn.execute('PRAGMA foreign_keys = ON')
        
        # Configure connection to return rows as dictionaries
        conn.row_factory = sqlite3.Row
        
        return conn
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> None:
        """Execute a database query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        """
        conn = self.get_connection()
        try:
            if params:
                conn.execute(query, params)
            else:
                conn.execute(query)
            conn.commit()
        finally:
            conn.close()
    
    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[tuple]:
        """Fetch a single row from the database.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Row as a tuple, or None if no result
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        finally:
            conn.close()
    
    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from the database.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of rows as dictionaries
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Convert rows to dictionaries
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # Project management methods
    def save_project(self, 
                    user_id: str, 
                    name: str, 
                    description: Optional[str] = None,
                    location_lat: Optional[float] = None,
                    location_lon: Optional[float] = None,
                    parameters: Optional[Dict[str, Any]] = None,
                    results: Optional[Dict[str, Any]] = None,
                    project_id: Optional[str] = None) -> str:
        """Save a new project or update an existing one.
        
        Args:
            user_id: User ID
            name: Project name
            description: Project description (optional)
            location_lat: Location latitude (optional)
            location_lon: Location longitude (optional)
            parameters: Project parameters as dictionary (optional)
            results: Calculation results as dictionary (optional)
            project_id: Project ID for updates (optional, generates new ID if None)
            
        Returns:
            Project ID
        """
        # Convert parameters and results to JSON strings
        parameters_json = json.dumps(parameters) if parameters else None
        results_json = json.dumps(results) if results else None
        
        if project_id:
            # Update existing project
            query = """
            UPDATE projects
            SET name = ?, description = ?, location_lat = ?, location_lon = ?, 
                parameters = ?, results = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
            """
            self.execute_query(
                query, 
                (name, description, location_lat, location_lon, 
                 parameters_json, results_json, project_id, user_id)
            )
            return project_id
        else:
            # Create new project
            project_id = str(uuid.uuid4())
            query = """
            INSERT INTO projects (
                id, user_id, name, description, location_lat, 
                location_lon, parameters, results
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.execute_query(
                query, 
                (project_id, user_id, name, description, location_lat, 
                 location_lon, parameters_json, results_json)
            )
            return project_id
    
    def get_project(self, 
                   project_id: str, 
                   user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a project by ID.
        
        Args:
            project_id: Project ID
            user_id: User ID (if provided, ensures the project belongs to this user)
            
        Returns:
            Project data as dictionary, or None if not found
        """
        if user_id:
            # Get project for specific user
            query = """
            SELECT * FROM projects 
            WHERE id = ? AND user_id = ?
            """
            project = self.fetch_one(query, (project_id, user_id))
        else:
            # Get project by ID only (used for shared projects)
            query = """
            SELECT * FROM projects 
            WHERE id = ?
            """
            project = self.fetch_one(query, (project_id,))
        
        if not project:
            return None
        
        # Convert project to dictionary
        result = dict(project)
        
        # Parse JSON strings
        if result.get('parameters'):
            result['parameters'] = json.loads(result['parameters'])
        
        if result.get('results'):
            result['results'] = json.loads(result['results'])
        
        return result
    
    def get_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of project dictionaries
        """
        query = """
        SELECT id, name, description, location_lat, location_lon, 
               created_at, updated_at
        FROM projects 
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """
        projects = self.fetch_all(query, (user_id,))
        
        # Also get projects shared with this user
        shared_query = """
        SELECT p.id, p.name, p.description, p.location_lat, p.location_lon, 
               p.created_at, p.updated_at, u.username as owner_name, 
               sp.permissions
        FROM projects p
        JOIN shared_projects sp ON p.id = sp.project_id
        JOIN users u ON p.user_id = u.id
        WHERE sp.shared_with_id = ?
        ORDER BY p.updated_at DESC
        """
        shared_projects = self.fetch_all(shared_query, (user_id,))
        
        # Mark shared projects
        for project in shared_projects:
            project['shared'] = True
            project['permissions'] = json.loads(project['permissions'])
        
        # Combine own and shared projects
        all_projects = projects + shared_projects
        
        # Sort by updated_at
        all_projects.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return all_projects
    
    def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project.
        
        Args:
            project_id: Project ID
            user_id: User ID (to ensure the project belongs to this user)
            
        Returns:
            True if project was deleted, False if not found
        """
        # First check if project exists and belongs to user
        query = "SELECT id FROM projects WHERE id = ? AND user_id = ?"
        project = self.fetch_one(query, (project_id, user_id))
        
        if not project:
            return False
        
        # Delete any sharing records first
        self.execute_query(
            "DELETE FROM shared_projects WHERE project_id = ?", 
            (project_id,)
        )
        
        # Delete the project
        self.execute_query(
            "DELETE FROM projects WHERE id = ?", 
            (project_id,)
        )
        
        return True
    
    def share_project(self, 
                     project_id: str, 
                     owner_id: str, 
                     shared_with_id: str,
                     permissions: Dict[str, bool]) -> bool:
        """Share a project with another user.
        
        Args:
            project_id: Project ID
            owner_id: Owner's user ID
            shared_with_id: ID of user to share with
            permissions: Dictionary of permissions (read, edit, etc.)
            
        Returns:
            True if project was shared, False if not found or not owned by owner_id
        """
        # First check if project exists and belongs to owner
        query = "SELECT id FROM projects WHERE id = ? AND user_id = ?"
        project = self.fetch_one(query, (project_id, owner_id))
        
        if not project:
            return False
        
        # Convert permissions to JSON
        permissions_json = json.dumps(permissions)
        
        # Check if already shared
        check_query = """
        SELECT project_id FROM shared_projects 
        WHERE project_id = ? AND shared_with_id = ?
        """
        existing = self.fetch_one(check_query, (project_id, shared_with_id))
        
        if existing:
            # Update existing share
            update_query = """
            UPDATE shared_projects
            SET permissions = ?, shared_at = CURRENT_TIMESTAMP
            WHERE project_id = ? AND shared_with_id = ?
            """
            self.execute_query(update_query, (permissions_json, project_id, shared_with_id))
        else:
            # Create new share
            insert_query = """
            INSERT INTO shared_projects (project_id, shared_with_id, permissions)
            VALUES (?, ?, ?)
            """
            self.execute_query(insert_query, (project_id, shared_with_id, permissions_json))
        
        return True
    
    def unshare_project(self, 
                       project_id: str, 
                       owner_id: str, 
                       shared_with_id: str) -> bool:
        """Unshare a project.
        
        Args:
            project_id: Project ID
            owner_id: Owner's user ID
            shared_with_id: ID of user to unshare with
            
        Returns:
            True if project was unshared, False if not found or not owned by owner_id
        """
        # First check if project exists and belongs to owner
        query = "SELECT id FROM projects WHERE id = ? AND user_id = ?"
        project = self.fetch_one(query, (project_id, owner_id))
        
        if not project:
            return False
        
        # Delete the share record
        self.execute_query(
            "DELETE FROM shared_projects WHERE project_id = ? AND shared_with_id = ?", 
            (project_id, shared_with_id)
        )
        
        return True
    
    def search_users(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for users by username or email.
        
        Args:
            search_term: Search string
            limit: Maximum number of results (default: 10)
            
        Returns:
            List of user dictionaries
        """
        search_pattern = f"%{search_term}%"
        
        query = """
        SELECT id, username, email
        FROM users
        WHERE username LIKE ? OR email LIKE ?
        LIMIT ?
        """
        
        users = self.fetch_all(query, (search_pattern, search_pattern, limit))
        
        # Remove sensitive information
        for user in users:
            if 'password_hash' in user:
                del user['password_hash']
            if 'salt' in user:
                del user['salt']
        
        return users

# Example usage
if __name__ == "__main__":
    # This is for demonstration purposes only
    db = DatabaseManager()
    
    # Example project
    # project_id = db.save_project(
    #     user_id="test_user_id",
    #     name="Sample Project",
    #     description="Testing the database manager",
    #     location_lat=39.7392,
    #     location_lon=-104.9903,
    #     parameters={
    #         "system_capacity": 10,
    #         "module_type": 1
    #     },
    #     results={
    #         "production": 15000,
    #         "savings": 2000
    #     }
    # )
    # print(f"Saved project with ID: {project_id}")
    
    # Retrieve project
    # project = db.get_project(project_id, "test_user_id")
    # print("Retrieved project:", project)