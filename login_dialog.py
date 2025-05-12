#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Login Dialog
Dialog for user authentication
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox, QFormLayout
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QPixmap

class LoginDialog(QDialog):
    """Dialog for user login"""
    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)
        
        # Store auth manager
        self.auth_manager = auth_manager
        
        # Set up dialog
        self.setWindowTitle("USB Monitoring System - Login")
        self.setMinimumWidth(400)
        self.setWindowIcon(QIcon("assets/icons/app_icon.png"))
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("assets/icons/app_icon.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)
        
        # Add title
        title_label = QLabel("USB Monitoring System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Add form
        form_layout = QFormLayout()
        
        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_edit)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember username")
        form_layout.addRow("", self.remember_checkbox)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Load saved username if available
        self.load_saved_username()
        
        # Connect signals
        self.username_edit.textChanged.connect(self.validate_input)
        self.password_edit.textChanged.connect(self.validate_input)
        
        # Initial validation
        self.validate_input()
    
    def validate_input(self):
        """Validate input fields"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        # Enable login button if both fields are filled
        self.login_button.setEnabled(bool(username and password))
    
    def login(self):
        """Attempt to log in"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        # Attempt login
        success, message = self.auth_manager.login(username, password)
        
        if success:
            # Save username if remember me is checked
            if self.remember_checkbox.isChecked():
                self.save_username(username)
            else:
                self.clear_saved_username()
            
            # Accept dialog
            self.accept()
        else:
            # Show error message
            QMessageBox.warning(self, "Login Failed", message)
    
    def save_username(self, username):
        """Save username to settings"""
        settings = QSettings("USBMonitor", "USBMonitoringSystem")
        settings.setValue("login/username", username)
        settings.setValue("login/remember", True)
    
    def clear_saved_username(self):
        """Clear saved username"""
        settings = QSettings("USBMonitor", "USBMonitoringSystem")
        settings.remove("login/username")
        settings.setValue("login/remember", False)
    
    def load_saved_username(self):
        """Load saved username"""
        settings = QSettings("USBMonitor", "USBMonitoringSystem")
        remember = settings.value("login/remember", False, type=bool)
        
        if remember:
            username = settings.value("login/username", "")
            self.username_edit.setText(username)
            self.remember_checkbox.setChecked(True)
            
            # Set focus to password field
            self.password_edit.setFocus()

class UserDialog(QDialog):
    """Dialog for creating or editing users"""
    def __init__(self, auth_manager, username=None, parent=None):
        super().__init__(parent)
        
        # Store auth manager
        self.auth_manager = auth_manager
        self.editing = username is not None
        
        # Set up dialog
        self.setWindowTitle("Create User" if not self.editing else "Edit User")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add form
        form_layout = QFormLayout()
        
        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_edit)
        
        # Email field
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter email")
        form_layout.addRow("Email:", self.email_edit)
        
        # Password field (only for new users)
        if not self.editing:
            self.password_edit = QLineEdit()
            self.password_edit.setPlaceholderText("Enter password")
            self.password_edit.setEchoMode(QLineEdit.Password)
            form_layout.addRow("Password:", self.password_edit)
            
            self.confirm_password_edit = QLineEdit()
            self.confirm_password_edit.setPlaceholderText("Confirm password")
            self.confirm_password_edit.setEchoMode(QLineEdit.Password)
            form_layout.addRow("Confirm Password:", self.confirm_password_edit)
        
        # Role field
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "manager", "admin"])
        form_layout.addRow("Role:", self.role_combo)
        
        # Active checkbox
        self.active_checkbox = QCheckBox("User is active")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("", self.active_checkbox)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.save_user)
        buttons_layout.addWidget(self.save_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Load user data if editing
        if self.editing:
            self.load_user(username)
        
        # Connect signals
        self.username_edit.textChanged.connect(self.validate_input)
        self.email_edit.textChanged.connect(self.validate_input)
        if not self.editing:
            self.password_edit.textChanged.connect(self.validate_input)
            self.confirm_password_edit.textChanged.connect(self.validate_input)
        
        # Initial validation
        self.validate_input()
    
    def validate_input(self):
        """Validate input fields"""
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        
        valid = bool(username and email)
        
        if not self.editing:
            password = self.password_edit.text()
            confirm_password = self.confirm_password_edit.text()
            valid = valid and bool(password) and password == confirm_password
        
        # Enable save button if all fields are valid
        self.save_button.setEnabled(valid)
    
    def load_user(self, username):
        """Load user data"""
        user = self.auth_manager.get_user(username)
        if user:
            self.username_edit.setText(user.username)
            self.username_edit.setReadOnly(True)  # Can't change username
            self.email_edit.setText(user.email)
            self.role_combo.setCurrentText(user.role)
            self.active_checkbox.setChecked(user.is_active)
    
    def save_user(self):
        """Save user data"""
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        role = self.role_combo.currentText()
        is_active = self.active_checkbox.isChecked()
        
        if self.editing:
            # Update existing user
            success, message = self.auth_manager.update_user(
                username=username,
                email=email,
                role=role,
                is_active=is_active
            )
        else:
            # Create new user
            password = self.password_edit.text()
            
            # Validate password
            if len(password) < 6:
                QMessageBox.warning(self, "Invalid Password", "Password must be at least 6 characters long.")
                return
            
            # Create user
            success, message = self.auth_manager.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
        
        if success:
            # Accept dialog
            self.accept()
        else:
            # Show error message
            QMessageBox.warning(self, "Error", message)

from PyQt5.QtWidgets import QComboBox
