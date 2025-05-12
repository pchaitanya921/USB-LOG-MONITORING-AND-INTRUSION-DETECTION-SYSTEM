#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Authentication Module
Handles user authentication and authorization
"""

import os
import json
import hashlib
import secrets
import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class User:
    """Class representing a user"""
    def __init__(self, username, email, role="user", is_active=True):
        self.username = username
        self.email = email
        self.role = role  # admin, manager, user
        self.is_active = is_active
        self.last_login = None
        self.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.permissions = self._get_default_permissions(role)
    
    def _get_default_permissions(self, role):
        """Get default permissions based on role"""
        if role == "admin":
            return {
                "scan_devices": True,
                "block_devices": True,
                "manage_users": True,
                "view_history": True,
                "update_database": True,
                "change_settings": True,
                "export_data": True,
                "view_logs": True
            }
        elif role == "manager":
            return {
                "scan_devices": True,
                "block_devices": True,
                "manage_users": False,
                "view_history": True,
                "update_database": True,
                "change_settings": True,
                "export_data": True,
                "view_logs": True
            }
        else:  # user
            return {
                "scan_devices": True,
                "block_devices": True,
                "manage_users": False,
                "view_history": True,
                "update_database": False,
                "change_settings": False,
                "export_data": True,
                "view_logs": False
            }
    
    def to_dict(self):
        """Convert user to dictionary for serialization"""
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "permissions": self.permissions
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        user = cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            role=data.get("role", "user"),
            is_active=data.get("is_active", True)
        )
        user.last_login = data.get("last_login")
        user.created_at = data.get("created_at", user.created_at)
        user.permissions = data.get("permissions", user.permissions)
        return user
    
    def has_permission(self, permission):
        """Check if user has a specific permission"""
        return self.permissions.get(permission, False)

class AuthManager(QObject):
    """Class for managing authentication and authorization"""
    # Define signals
    user_logged_in = pyqtSignal(str)  # username
    user_logged_out = pyqtSignal(str)  # username
    user_created = pyqtSignal(str)  # username
    user_updated = pyqtSignal(str)  # username
    user_deleted = pyqtSignal(str)  # username
    
    def __init__(self):
        super().__init__()
        self.users = {}  # Dictionary of users
        self.current_user = None
        
        # Load users
        self._load_users()
        
        # Create default admin user if no users exist
        if not self.users:
            self._create_default_admin()
    
    def _load_users(self):
        """Load users from file"""
        users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "users.json")
        
        if os.path.exists(users_file):
            try:
                with open(users_file, "r") as f:
                    data = json.load(f)
                    
                    # Load users
                    for username, user_data in data.get("users", {}).items():
                        self.users[username] = User.from_dict(user_data)
                    
                    # Load password hashes
                    self.password_hashes = data.get("password_hashes", {})
            except Exception as e:
                print(f"Error loading users: {str(e)}")
                self.users = {}
                self.password_hashes = {}
        else:
            self.users = {}
            self.password_hashes = {}
    
    def _save_users(self):
        """Save users to file"""
        users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "users.json")
        
        try:
            # Convert users to dictionary
            users_dict = {}
            for username, user in self.users.items():
                users_dict[username] = user.to_dict()
            
            # Create data dictionary
            data = {
                "users": users_dict,
                "password_hashes": self.password_hashes
            }
            
            # Save to file
            with open(users_file, "w") as f:
                json.dump(data, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving users: {str(e)}")
            return False
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_user = User("admin", "admin@example.com", "admin")
        self.users["admin"] = admin_user
        
        # Generate random password
        password = "admin123"  # In a real app, this would be randomly generated
        
        # Hash password
        self.password_hashes = {}
        self.password_hashes["admin"] = self._hash_password(password)
        
        # Save users
        self._save_users()
        
        print(f"Created default admin user with password: {password}")
    
    def _hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Hash password with salt
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()
        
        # Return salt and hash
        return f"{salt}${password_hash}"
    
    def _verify_password(self, password, password_hash):
        """Verify password against hash"""
        # Split salt and hash
        salt, hash_value = password_hash.split("$")
        
        # Hash password with salt
        new_hash = self._hash_password(password, salt).split("$")[1]
        
        # Compare hashes
        return new_hash == hash_value
    
    def login(self, username, password):
        """Log in a user"""
        # Check if user exists
        if username not in self.users:
            return False, "User does not exist"
        
        # Check if user is active
        if not self.users[username].is_active:
            return False, "User is not active"
        
        # Check if password is correct
        if username not in self.password_hashes:
            return False, "Password not set for user"
        
        if not self._verify_password(password, self.password_hashes[username]):
            return False, "Incorrect password"
        
        # Set current user
        self.current_user = self.users[username]
        
        # Update last login
        self.current_user.last_login = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save users
        self._save_users()
        
        # Emit signal
        self.user_logged_in.emit(username)
        
        return True, "Login successful"
    
    def logout(self):
        """Log out current user"""
        if self.current_user:
            username = self.current_user.username
            self.current_user = None
            
            # Emit signal
            self.user_logged_out.emit(username)
            
            return True, "Logout successful"
        
        return False, "No user logged in"
    
    def create_user(self, username, email, password, role="user"):
        """Create a new user"""
        # Check if user already exists
        if username in self.users:
            return False, "User already exists"
        
        # Create user
        user = User(username, email, role)
        self.users[username] = user
        
        # Hash password
        self.password_hashes[username] = self._hash_password(password)
        
        # Save users
        self._save_users()
        
        # Emit signal
        self.user_created.emit(username)
        
        return True, "User created successfully"
    
    def update_user(self, username, email=None, role=None, is_active=None, permissions=None):
        """Update a user"""
        # Check if user exists
        if username not in self.users:
            return False, "User does not exist"
        
        # Update user
        if email:
            self.users[username].email = email
        
        if role:
            self.users[username].role = role
            # Reset permissions to default for new role
            self.users[username].permissions = self.users[username]._get_default_permissions(role)
        
        if is_active is not None:
            self.users[username].is_active = is_active
        
        if permissions:
            # Update specific permissions
            for permission, value in permissions.items():
                self.users[username].permissions[permission] = value
        
        # Save users
        self._save_users()
        
        # Emit signal
        self.user_updated.emit(username)
        
        return True, "User updated successfully"
    
    def delete_user(self, username):
        """Delete a user"""
        # Check if user exists
        if username not in self.users:
            return False, "User does not exist"
        
        # Check if user is current user
        if self.current_user and self.current_user.username == username:
            return False, "Cannot delete current user"
        
        # Delete user
        del self.users[username]
        
        # Delete password hash
        if username in self.password_hashes:
            del self.password_hashes[username]
        
        # Save users
        self._save_users()
        
        # Emit signal
        self.user_deleted.emit(username)
        
        return True, "User deleted successfully"
    
    def change_password(self, username, old_password, new_password):
        """Change a user's password"""
        # Check if user exists
        if username not in self.users:
            return False, "User does not exist"
        
        # Check if old password is correct
        if not self._verify_password(old_password, self.password_hashes[username]):
            return False, "Incorrect password"
        
        # Hash new password
        self.password_hashes[username] = self._hash_password(new_password)
        
        # Save users
        self._save_users()
        
        return True, "Password changed successfully"
    
    def reset_password(self, username, new_password):
        """Reset a user's password (admin only)"""
        # Check if current user is admin
        if not self.current_user or self.current_user.role != "admin":
            return False, "Only admins can reset passwords"
        
        # Check if user exists
        if username not in self.users:
            return False, "User does not exist"
        
        # Hash new password
        self.password_hashes[username] = self._hash_password(new_password)
        
        # Save users
        self._save_users()
        
        return True, "Password reset successfully"
    
    def get_current_user(self):
        """Get current user"""
        return self.current_user
    
    def get_user(self, username):
        """Get a user by username"""
        return self.users.get(username)
    
    def get_all_users(self):
        """Get all users"""
        return self.users
    
    def has_permission(self, permission):
        """Check if current user has a specific permission"""
        if not self.current_user:
            return False
        
        return self.current_user.has_permission(permission)
