#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User Management Dialog
Dialog for managing users
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QMenu, QAction, QInputDialog, QWidget, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor

from src.ui.login_dialog import UserDialog

class UserManagementDialog(QDialog):
    """Dialog for managing users"""
    def __init__(self, auth_manager, parent=None):
        super().__init__(parent)

        # Store auth manager
        self.auth_manager = auth_manager

        # Set up dialog
        self.setWindowTitle("User Management")
        self.setMinimumSize(800, 500)

        # Create layout
        layout = QVBoxLayout(self)

        # Add title
        title_label = QLabel("User Management")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Add controls
        controls_layout = QHBoxLayout()

        # Add user button
        self.add_button = QPushButton("Add User")
        self.add_button.setIcon(QIcon("assets/icons/add_user.png"))
        self.add_button.clicked.connect(self.add_user)
        controls_layout.addWidget(self.add_button)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        self.refresh_button.clicked.connect(self.refresh_users)
        controls_layout.addWidget(self.refresh_button)

        # Add spacer
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Add users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "Username", "Email", "Role", "Status", "Last Login", "Actions"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.users_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.users_table)

        # Add buttons
        buttons_layout = QHBoxLayout()

        # Add spacer
        buttons_layout.addStretch()

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_button)

        layout.addLayout(buttons_layout)

        # Load users
        self.refresh_users()

    def refresh_users(self):
        """Refresh users table"""
        # Clear table
        self.users_table.setRowCount(0)

        # Get current user
        current_user = self.auth_manager.get_current_user()

        # Get all users
        users = self.auth_manager.get_all_users()

        # Add users to table
        for i, (username, user) in enumerate(users.items()):
            self.users_table.insertRow(i)

            # Username
            username_item = QTableWidgetItem(username)
            if current_user and current_user.username == username:
                username_item.setForeground(QColor("#3498db"))  # Highlight current user
            self.users_table.setItem(i, 0, username_item)

            # Email
            email_item = QTableWidgetItem(user.email)
            self.users_table.setItem(i, 1, email_item)

            # Role
            role_item = QTableWidgetItem(user.role)
            self.users_table.setItem(i, 2, role_item)

            # Status
            status_item = QTableWidgetItem("Active" if user.is_active else "Inactive")
            status_item.setForeground(QColor("#2ecc71" if user.is_active else "#e74c3c"))
            self.users_table.setItem(i, 3, status_item)

            # Last login
            last_login_item = QTableWidgetItem(user.last_login or "Never")
            self.users_table.setItem(i, 4, last_login_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)

            # Edit button
            edit_button = QPushButton("Edit")
            edit_button.setProperty("username", username)
            edit_button.clicked.connect(lambda checked, u=username: self.edit_user(u))
            actions_layout.addWidget(edit_button)

            # Reset password button
            reset_button = QPushButton("Reset Password")
            reset_button.setProperty("username", username)
            reset_button.clicked.connect(lambda checked, u=username: self.reset_password(u))
            actions_layout.addWidget(reset_button)

            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.setProperty("username", username)
            delete_button.clicked.connect(lambda checked, u=username: self.delete_user(u))

            # Disable delete button for current user
            if current_user and current_user.username == username:
                delete_button.setEnabled(False)
                delete_button.setToolTip("Cannot delete current user")

            actions_layout.addWidget(delete_button)

            self.users_table.setCellWidget(i, 5, actions_widget)

    def add_user(self):
        """Add a new user"""
        # Check if current user has permission
        if not self.auth_manager.has_permission("manage_users"):
            QMessageBox.warning(self, "Permission Denied", "You do not have permission to manage users.")
            return

        # Create user dialog
        dialog = UserDialog(self.auth_manager, parent=self)

        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Refresh users
            self.refresh_users()

    def edit_user(self, username):
        """Edit a user"""
        # Check if current user has permission
        if not self.auth_manager.has_permission("manage_users"):
            QMessageBox.warning(self, "Permission Denied", "You do not have permission to manage users.")
            return

        # Create user dialog
        dialog = UserDialog(self.auth_manager, username, parent=self)

        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # Refresh users
            self.refresh_users()

    def reset_password(self, username):
        """Reset a user's password"""
        # Check if current user has permission
        if not self.auth_manager.has_permission("manage_users"):
            QMessageBox.warning(self, "Permission Denied", "You do not have permission to manage users.")
            return

        # Get new password
        password, ok = QInputDialog.getText(
            self, "Reset Password", f"Enter new password for {username}:",
            QLineEdit.Password
        )

        if ok and password:
            # Validate password
            if len(password) < 6:
                QMessageBox.warning(self, "Invalid Password", "Password must be at least 6 characters long.")
                return

            # Reset password
            success, message = self.auth_manager.reset_password(username, password)

            if success:
                QMessageBox.information(self, "Password Reset", f"Password for {username} has been reset.")
            else:
                QMessageBox.warning(self, "Error", message)

    def delete_user(self, username):
        """Delete a user"""
        # Check if current user has permission
        if not self.auth_manager.has_permission("manage_users"):
            QMessageBox.warning(self, "Permission Denied", "You do not have permission to manage users.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete user {username}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Delete user
            success, message = self.auth_manager.delete_user(username)

            if success:
                # Refresh users
                self.refresh_users()
            else:
                QMessageBox.warning(self, "Error", message)

    def show_context_menu(self, position):
        """Show context menu for users table"""
        # Get selected row
        row = self.users_table.rowAt(position.y())
        if row < 0:
            return

        # Get username
        username = self.users_table.item(row, 0).text()

        # Create menu
        menu = QMenu(self)

        # Add actions
        edit_action = QAction("Edit User", self)
        edit_action.triggered.connect(lambda: self.edit_user(username))
        menu.addAction(edit_action)

        reset_action = QAction("Reset Password", self)
        reset_action.triggered.connect(lambda: self.reset_password(username))
        menu.addAction(reset_action)

        # Get user
        user = self.auth_manager.get_user(username)

        # Add toggle active action
        if user.is_active:
            deactivate_action = QAction("Deactivate User", self)
            deactivate_action.triggered.connect(lambda: self.toggle_active(username, False))
            menu.addAction(deactivate_action)
        else:
            activate_action = QAction("Activate User", self)
            activate_action.triggered.connect(lambda: self.toggle_active(username, True))
            menu.addAction(activate_action)

        menu.addSeparator()

        delete_action = QAction("Delete User", self)
        delete_action.triggered.connect(lambda: self.delete_user(username))

        # Disable delete action for current user
        current_user = self.auth_manager.get_current_user()
        if current_user and current_user.username == username:
            delete_action.setEnabled(False)

        menu.addAction(delete_action)

        # Show menu
        menu.exec_(self.users_table.mapToGlobal(position))

    def toggle_active(self, username, active):
        """Toggle user active status"""
        # Check if current user has permission
        if not self.auth_manager.has_permission("manage_users"):
            QMessageBox.warning(self, "Permission Denied", "You do not have permission to manage users.")
            return

        # Update user
        success, message = self.auth_manager.update_user(username, is_active=active)

        if success:
            # Refresh users
            self.refresh_users()
        else:
            QMessageBox.warning(self, "Error", message)
