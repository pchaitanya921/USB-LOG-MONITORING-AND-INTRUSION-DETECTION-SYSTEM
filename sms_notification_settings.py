#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SMS Notification Settings Window
Provides a UI for configuring enhanced SMS notification settings
"""

import os
import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox, QGroupBox, 
    QFormLayout, QComboBox, QListWidget, QMessageBox,
    QTextEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

class PhoneNumberDialog(QDialog):
    """Dialog for adding a new phone number"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Add Phone Number")
        self.setMinimumWidth(300)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form
        form_layout = QFormLayout()
        
        # Phone number input
        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("+1234567890")
        form_layout.addRow("Phone Number:", self.phone_number)
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_phone_number(self):
        """Get the entered phone number"""
        number = self.phone_number.text().strip()
        
        # Add + prefix if missing
        if number and not number.startswith('+'):
            number = '+' + number
            
        return number

class NotificationSettingsWindow(QMainWindow):
    """Window for configuring SMS notification settings"""
    def __init__(self):
        super().__init__()
        
        # Set up window
        self.setWindowTitle("SMS Notification Settings")
        self.setMinimumSize(600, 500)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create notification settings group
        notification_group = QGroupBox("SMS Notification Settings")
        notification_layout = QVBoxLayout(notification_group)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Enable SMS notifications
        self.enable_sms = QCheckBox("Enable SMS Notifications")
        self.enable_sms.toggled.connect(self.toggle_sms_settings)
        form_layout.addRow("", self.enable_sms)
        
        # Notification level
        self.notification_level = QComboBox()
        self.notification_level.addItems(["All Scans", "Threats Only", "Critical Only"])
        form_layout.addRow("Notification Level:", self.notification_level)
        
        # Message detail
        self.message_detail = QComboBox()
        self.message_detail.addItems(["Brief", "Standard", "Detailed"])
        form_layout.addRow("Message Detail:", self.message_detail)
        
        # Add form to notification layout
        notification_layout.addLayout(form_layout)
        
        # Add notification group to main layout
        main_layout.addWidget(notification_group)
        
        # Create phone numbers group
        phone_group = QGroupBox("Phone Numbers")
        phone_layout = QVBoxLayout(phone_group)
        
        # Phone numbers list
        self.phone_list = QListWidget()
        phone_layout.addWidget(self.phone_list)
        
        # Phone number buttons
        phone_buttons = QHBoxLayout()
        
        self.add_button = QPushButton("Add Number")
        self.add_button.clicked.connect(self.add_phone_number)
        phone_buttons.addWidget(self.add_button)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_phone_number)
        phone_buttons.addWidget(self.remove_button)
        
        phone_layout.addLayout(phone_buttons)
        
        # Add phone group to main layout
        main_layout.addWidget(phone_group)
        
        # Create advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        
        # Include file details
        self.include_file_details = QCheckBox("Include file details in messages")
        advanced_layout.addRow("", self.include_file_details)
        
        # Include location information
        self.include_location = QCheckBox("Include system location information")
        advanced_layout.addRow("", self.include_location)
        
        # Maximum files to show
        self.max_files = QComboBox()
        self.max_files.addItems(["3", "5", "10", "All"])
        advanced_layout.addRow("Max files in message:", self.max_files)
        
        # Add advanced group to main layout
        main_layout.addWidget(advanced_group)
        
        # Create buttons layout
        buttons_layout = QHBoxLayout()
        
        # Test button
        self.test_button = QPushButton("Test SMS")
        self.test_button.clicked.connect(self.test_sms)
        buttons_layout.addWidget(self.test_button)
        
        # Spacer
        buttons_layout.addStretch()
        
        # Load button
        self.load_button = QPushButton("Load Settings")
        self.load_button.clicked.connect(self.load_settings)
        buttons_layout.addWidget(self.load_button)
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)
        
        # Add buttons layout to main layout
        main_layout.addLayout(buttons_layout)
        
        # Initialize settings
        self.config = {}
        self.load_settings()
        
        # Update UI state
        self.toggle_sms_settings(self.enable_sms.isChecked())
    
    def toggle_sms_settings(self, enabled):
        """Enable or disable SMS settings based on checkbox"""
        self.notification_level.setEnabled(enabled)
        self.message_detail.setEnabled(enabled)
        self.phone_list.setEnabled(enabled)
        self.add_button.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        self.include_file_details.setEnabled(enabled)
        self.include_location.setEnabled(enabled)
        self.max_files.setEnabled(enabled)
        self.test_button.setEnabled(enabled)
    
    def add_phone_number(self):
        """Add a new phone number to the list"""
        dialog = PhoneNumberDialog(self)
        
        if dialog.exec_():
            phone_number = dialog.get_phone_number()
            
            if not phone_number:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid phone number.")
                return
            
            # Check if number already exists
            for i in range(self.phone_list.count()):
                if self.phone_list.item(i).text() == phone_number:
                    QMessageBox.information(self, "Duplicate", f"Phone number {phone_number} already exists.")
                    return
            
            # Add to list
            self.phone_list.addItem(phone_number)
    
    def remove_phone_number(self):
        """Remove the selected phone number from the list"""
        selected_items = self.phone_list.selectedItems()
        
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a phone number to remove.")
            return
        
        # Remove selected items
        for item in selected_items:
            self.phone_list.takeItem(self.phone_list.row(item))
    
    def get_phone_numbers(self):
        """Get all phone numbers from the list"""
        numbers = []
        
        for i in range(self.phone_list.count()):
            numbers.append(self.phone_list.item(i).text())
        
        return numbers
    
    def load_settings(self):
        """Load settings from configuration file"""
        config_path = "notification_config.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                
                # Update UI with loaded settings
                self.enable_sms.setChecked(self.config.get("sms_enabled", False))
                
                # Set notification level
                notification_levels = {
                    "all": 0,
                    "threats_only": 1,
                    "critical_only": 2
                }
                level_index = notification_levels.get(self.config.get("notification_level", "all"), 0)
                self.notification_level.setCurrentIndex(level_index)
                
                # Set message detail
                message_formats = {
                    "brief": 0,
                    "standard": 1,
                    "detailed": 2
                }
                format_index = message_formats.get(self.config.get("message_format", "standard"), 1)
                self.message_detail.setCurrentIndex(format_index)
                
                # Set phone numbers
                self.phone_list.clear()
                for number in self.config.get("phone_numbers", []):
                    self.phone_list.addItem(number)
                
                # Set advanced settings
                self.include_file_details.setChecked(self.config.get("include_file_details", True))
                self.include_location.setChecked(self.config.get("include_location", False))
                
                # Set max files
                max_files = self.config.get("max_files_in_sms", 5)
                max_files_index = 1  # Default to 5
                
                if max_files == 3:
                    max_files_index = 0
                elif max_files == 5:
                    max_files_index = 1
                elif max_files == 10:
                    max_files_index = 2
                elif max_files > 10:
                    max_files_index = 3
                
                self.max_files.setCurrentIndex(max_files_index)
                
                QMessageBox.information(self, "Settings Loaded", "Notification settings loaded successfully.")
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load settings: {str(e)}")
        else:
            QMessageBox.information(self, "No Configuration", "No configuration file found. Using default settings.")
    
    def save_settings(self):
        """Save settings to configuration file"""
        # Get notification level
        level_index = self.notification_level.currentIndex()
        notification_levels = ["all", "threats_only", "critical_only"]
        notification_level = notification_levels[level_index]
        
        # Get message format
        format_index = self.message_detail.currentIndex()
        message_formats = ["brief", "standard", "detailed"]
        message_format = message_formats[format_index]
        
        # Get max files
        max_files_index = self.max_files.currentIndex()
        max_files_values = [3, 5, 10, 100]  # Use 100 for "All"
        max_files = max_files_values[max_files_index]
        
        # Update configuration
        self.config.update({
            "sms_enabled": self.enable_sms.isChecked(),
            "notification_level": notification_level,
            "message_format": message_format,
            "phone_numbers": self.get_phone_numbers(),
            "include_file_details": self.include_file_details.isChecked(),
            "include_location": self.include_location.isChecked(),
            "max_files_in_sms": max_files,
            
            # Map notification level to specific notification types
            "notification_levels": {
                "connect": notification_level == "all",
                "disconnect": False,  # Always off
                "scan_start": False,  # Always off
                "scan_complete": True,  # Always on
                "threat_detected": notification_level in ["all", "threats_only", "critical_only"],
                "suspicious_detected": notification_level in ["all", "threats_only"],
                "system_error": notification_level == "all"
            }
        })
        
        # Save to file
        config_path = "notification_config.json"
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            QMessageBox.information(self, "Settings Saved", "Notification settings saved successfully.")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
    
    def test_sms(self):
        """Send a test SMS notification"""
        if not self.enable_sms.isChecked():
            QMessageBox.warning(self, "SMS Disabled", "SMS notifications are disabled. Please enable them first.")
            return
        
        phone_numbers = self.get_phone_numbers()
        
        if not phone_numbers:
            QMessageBox.warning(self, "No Recipients", "Please add at least one phone number.")
            return
        
        # Ask which number to use for test
        if len(phone_numbers) > 1:
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Recipient")
            dialog.setMinimumWidth(300)
            
            layout = QVBoxLayout(dialog)
            
            layout.addWidget(QLabel("Select a phone number to send the test message:"))
            
            number_combo = QComboBox()
            number_combo.addItems(phone_numbers)
            layout.addWidget(number_combo)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            if dialog.exec_():
                test_number = number_combo.currentText()
            else:
                return
        else:
            test_number = phone_numbers[0]
        
        # Save current settings
        self.save_settings()
        
        # Import the notification service
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from enhanced_notification_service import EnhancedNotificationService
            
            # Create notification service
            notification_service = EnhancedNotificationService("notification_config.json")
            
            # Send test notification
            success = notification_service.test_notification(test_number)
            
            if success:
                QMessageBox.information(self, "Test Sent", f"Test SMS notification sent to {test_number}.")
            else:
                QMessageBox.warning(self, "Test Failed", "Failed to send test SMS notification. Check the logs for details.")
            
        except ImportError:
            QMessageBox.warning(self, "Module Not Found", "Enhanced notification service module not found.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error sending test SMS: {str(e)}")

# Run as standalone application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotificationSettingsWindow()
    window.show()
    sys.exit(app.exec_())
