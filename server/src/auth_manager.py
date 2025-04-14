#server/src/auth_manager.py
"""
Authentication Manager for the Energy Investment Decision Support System.

This module provides user authentication and authorization functionality using JWT tokens.
It handles user registration, login, password management, and token validation.
"""
from typing import Dict, Optional, Tuple, Union, Any
import jwt
import datetime
import uuid
import hashlib
import os
import sys
from functools import wraps
from flask import request, jsonify, current_app

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import db manager
from db_manager import DatabaseManager

class AuthManager:
    """Handles user authentication and authorization."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None, 
                secret_key: Optional[str] = None,
                token_expiry: int = 24):
        """Initialize the authentication manager.
        
        Args:
            db_manager: Database manager instance
            secret_key: Secret key for JWT token signing
            token_expiry: Token expiry time in hours (default: 24)
        """
        self.db_manager = db_manager or DatabaseManager()
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
        self.token_expiry = token_expiry
        
        # Ensure user table exists
        self._ensure_user_table()
    
    def _ensure_user_table(self) -> None:
        """Ensure the user table exists in the database."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """
        self.db_manager.execute_query(create_table_sql)
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password with a salt for secure storage.
        
        Args:
            password: Plain text password
            salt: Salt string (generated if None)
            
        Returns:
            Tuple of (password_hash, salt)
        """
        if salt is None:
            salt = uuid.uuid4().hex
        
        # Create hash using PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000  # Number of iterations
        ).hex()
        
        return password_hash, salt
    
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Password
            
        Returns:
            Dictionary with registration result
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        check_query = "SELECT id FROM users WHERE username = ? OR email = ?"
        existing_user = self.db_manager.fetch_one(check_query, (username, email))
        
        if existing_user:
            raise ValueError("Username or email already exists")
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        password_hash, salt = self._hash_password(password)
        
        # Insert user into database
        insert_query = """
        INSERT INTO users (id, username, email, password_hash, salt)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db_manager.execute_query(
            insert_query, 
            (user_id, username, email, password_hash, salt)
        )
        
        # Generate authentication token
        token = self._generate_token(user_id, username)
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "token": token
        }
    
    def login_user(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user and generate a token.
        
        Args:
            username_or_email: Username or email
            password: Password
            
        Returns:
            Dictionary with login result
            
        Raises:
            ValueError: If authentication fails
        """
        # Find user by username or email
        query = "SELECT id, username, email, password_hash, salt FROM users WHERE username = ? OR email = ?"
        user = self.db_manager.fetch_one(query, (username_or_email, username_or_email))
        
        if not user:
            raise ValueError("User not found")
        
        # Verify password
        user_id, username, email, stored_hash, salt = user
        calculated_hash, _ = self._hash_password(password, salt)
        
        if calculated_hash != stored_hash:
            raise ValueError("Invalid password")
        
        # Update last login timestamp
        update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        self.db_manager.execute_query(update_query, (user_id,))
        
        # Generate authentication token
        token = self._generate_token(user_id, username)
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "token": token
        }
    
    def _generate_token(self, user_id: str, username: str) -> str:
        """Generate a JWT token for a user.
        
        Args:
            user_id: User ID
            username: Username
            
        Returns:
            JWT token string
        """
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.token_expiry),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
            'username': username
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm='HS256'
        )
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change a user's password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed successfully
            
        Raises:
            ValueError: If current password is incorrect
        """
        # Get current password hash and salt
        query = "SELECT password_hash, salt FROM users WHERE id = ?"
        result = self.db_manager.fetch_one(query, (user_id,))
        
        if not result:
            raise ValueError("User not found")
        
        stored_hash, salt = result
        
        # Verify current password
        calculated_hash, _ = self._hash_password(current_password, salt)
        
        if calculated_hash != stored_hash:
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_hash, new_salt = self._hash_password(new_password)
        
        # Update password in database
        update_query = "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?"
        self.db_manager.execute_query(update_query, (new_hash, new_salt, user_id))
        
        return True
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and extract the payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary with token payload
            
        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get a user's profile data.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user profile data
            
        Raises:
            ValueError: If user not found
        """
        query = """
        SELECT id, username, email, created_at, last_login 
        FROM users
        WHERE id = ?
        """
        user = self.db_manager.fetch_one(query, (user_id,))
        
        if not user:
            raise ValueError("User not found")
        
        user_id, username, email, created_at, last_login = user
        
        return {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": created_at,
            "last_login": last_login
        }

# Flask decorator for token authentication
def token_required(f):
    """Decorator for Flask routes that require token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            # Get the AuthManager instance
            auth_manager = kwargs.get('auth_manager') or AuthManager()
            
            # Verify token
            payload = auth_manager.verify_token(token)
            
            # Add user data to kwargs
            kwargs['user_id'] = payload['sub']
            kwargs['username'] = payload['username']
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# Example usage
if __name__ == "__main__":
    # This is for demonstration purposes only
    auth = AuthManager()
    
    # Register a user
    # user = auth.register_user("test_user", "test@example.com", "password123")
    # print("Registered user:", user)
    
    # Login
    # login_result = auth.login_user("test_user", "password123")
    # print("Login result:", login_result)
    
    # Verify token
    # token = login_result['token']
    # payload = auth.verify_token(token)
    # print("Token payload:", payload)