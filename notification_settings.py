#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notification Settings Dialog
Dialog for configuring advanced notification settings
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QGroupBox, QFormLayout, QSpinBox,
    QTabWidget, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt

class NotificationSettingsDialog(QDialog):
    """Dialog for configuring advanced notification settings"""
    def __init__(self, config=None, parent=None):
        super().__init__(parent)

        # Store config
        self.config = config or {}

        # Set up dialog
        self.setWindowTitle("Advanced Notification Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Create layout
        layout = QVBoxLayout(self)

        # Create tab widget
        tab_widget = QTabWidget()

        # Create tabs
        self.email_tab = QWidget()
        self.sms_tab = QWidget()

        # Add tabs to tab widget
        tab_widget.addTab(self.email_tab, "Email Notifications")
        tab_widget.addTab(self.sms_tab, "SMS Notifications")

        # Set up tabs
        self._setup_email_tab()
        self._setup_sms_tab()

        layout.addWidget(tab_widget)

        # Add buttons
        buttons_layout = QHBoxLayout()

        # Add spacer
        buttons_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)

        layout.addLayout(buttons_layout)

    def _setup_email_tab(self):
        """Set up email tab"""
        layout = QVBoxLayout(self.email_tab)

        # Email settings
        email_group = QGroupBox("Email Settings")
        email_form = QFormLayout(email_group)

        # Enable email notifications
        self.email_notifications = QCheckBox("Enable email notifications")
        self.email_notifications.setChecked(self.config.get("email_notifications", False))
        self.email_notifications.toggled.connect(self.toggle_email_settings)
        email_form.addRow("", self.email_notifications)

        # Email recipients
        self.email_address = QLineEdit(self.config.get("email_address", ""))
        self.email_address.setEnabled(self.config.get("email_notifications", False))
        self.email_address.setPlaceholderText("Recipient email address")
        email_form.addRow("Email Address:", self.email_address)

        # SMTP settings
        smtp_group = QGroupBox("SMTP Server Settings")
        smtp_form = QFormLayout(smtp_group)

        self.email_from = QLineEdit(self.config.get("email_from", ""))
        self.email_from.setEnabled(self.config.get("email_notifications", False))
        self.email_from.setPlaceholderText("Sender email address")
        smtp_form.addRow("From Address:", self.email_from)

        self.email_smtp_server = QLineEdit(self.config.get("email_smtp_server", "smtp.gmail.com"))
        self.email_smtp_server.setEnabled(self.config.get("email_notifications", False))
        smtp_form.addRow("SMTP Server:", self.email_smtp_server)

        self.email_smtp_port = QSpinBox()
        self.email_smtp_port.setRange(1, 65535)
        self.email_smtp_port.setValue(self.config.get("email_smtp_port", 587))
        self.email_smtp_port.setEnabled(self.config.get("email_notifications", False))
        smtp_form.addRow("SMTP Port:", self.email_smtp_port)

        self.email_username = QLineEdit(self.config.get("email_username", ""))
        self.email_username.setEnabled(self.config.get("email_notifications", False))
        self.email_username.setPlaceholderText("SMTP username")
        smtp_form.addRow("Username:", self.email_username)

        self.email_password = QLineEdit(self.config.get("email_password", ""))
        self.email_password.setEnabled(self.config.get("email_notifications", False))
        self.email_password.setEchoMode(QLineEdit.Password)
        self.email_password.setPlaceholderText("SMTP password")
        smtp_form.addRow("Password:", self.email_password)

        self.email_use_tls = QCheckBox("Use TLS")
        self.email_use_tls.setChecked(self.config.get("email_use_tls", True))
        self.email_use_tls.setEnabled(self.config.get("email_notifications", False))
        smtp_form.addRow("", self.email_use_tls)

        # Test email button
        self.test_email_button = QPushButton("Test Email")
        self.test_email_button.setEnabled(self.config.get("email_notifications", False))
        self.test_email_button.clicked.connect(self.test_email)
        smtp_form.addRow("", self.test_email_button)

        # Add groups to layout
        layout.addWidget(email_group)
        layout.addWidget(smtp_group)

        # Add spacer
        layout.addStretch()

    def _setup_sms_tab(self):
        """Set up SMS tab"""
        layout = QVBoxLayout(self.sms_tab)

        # SMS settings
        sms_group = QGroupBox("SMS Settings")
        sms_form = QFormLayout(sms_group)

        # Enable SMS notifications
        self.sms_notifications = QCheckBox("Enable SMS notifications")
        self.sms_notifications.setChecked(self.config.get("sms_notifications", False))
        self.sms_notifications.toggled.connect(self.toggle_sms_settings)
        sms_form.addRow("", self.sms_notifications)

        # SMS provider selection
        self.sms_provider = QComboBox()
        self.sms_provider.addItems(["Twilio", "Nexmo/Vonage"])
        current_provider = self.config.get("sms_provider", "twilio")
        if current_provider == "nexmo":
            self.sms_provider.setCurrentText("Nexmo/Vonage")
        else:
            self.sms_provider.setCurrentText("Twilio")
        self.sms_provider.setEnabled(self.config.get("sms_notifications", False))
        self.sms_provider.currentTextChanged.connect(self.toggle_sms_provider)
        sms_form.addRow("SMS Provider:", self.sms_provider)

        # Recipient phone number
        self.phone_number = QLineEdit(self.config.get("phone_number", ""))
        self.phone_number.setEnabled(self.config.get("sms_notifications", False))
        self.phone_number.setPlaceholderText("+1234567890")
        sms_form.addRow("Phone Number:", self.phone_number)

        # Add SMS group to layout
        layout.addWidget(sms_group)

        # Twilio settings
        self.twilio_group = QGroupBox("Twilio Settings")
        twilio_form = QFormLayout(self.twilio_group)

        self.twilio_account_sid = QLineEdit(self.config.get("twilio_account_sid", ""))
        self.twilio_account_sid.setEnabled(self.config.get("sms_notifications", False))
        self.twilio_account_sid.setPlaceholderText("Twilio Account SID")
        twilio_form.addRow("Account SID:", self.twilio_account_sid)

        self.twilio_auth_token = QLineEdit(self.config.get("twilio_auth_token", ""))
        self.twilio_auth_token.setEnabled(self.config.get("sms_notifications", False))
        self.twilio_auth_token.setEchoMode(QLineEdit.Password)
        self.twilio_auth_token.setPlaceholderText("Twilio Auth Token")
        twilio_form.addRow("Auth Token:", self.twilio_auth_token)

        self.twilio_phone_number = QLineEdit(self.config.get("twilio_phone_number", ""))
        self.twilio_phone_number.setEnabled(self.config.get("sms_notifications", False))
        self.twilio_phone_number.setPlaceholderText("+1234567890")
        twilio_form.addRow("From Number:", self.twilio_phone_number)

        # Add Twilio group to layout
        layout.addWidget(self.twilio_group)

        # Nexmo/Vonage settings
        self.nexmo_group = QGroupBox("Nexmo/Vonage Settings")
        nexmo_form = QFormLayout(self.nexmo_group)

        self.nexmo_api_key = QLineEdit(self.config.get("nexmo_api_key", ""))
        self.nexmo_api_key.setEnabled(self.config.get("sms_notifications", False))
        self.nexmo_api_key.setPlaceholderText("Nexmo API Key")
        nexmo_form.addRow("API Key:", self.nexmo_api_key)

        self.nexmo_api_secret = QLineEdit(self.config.get("nexmo_api_secret", ""))
        self.nexmo_api_secret.setEnabled(self.config.get("sms_notifications", False))
        self.nexmo_api_secret.setEchoMode(QLineEdit.Password)
        self.nexmo_api_secret.setPlaceholderText("Nexmo API Secret")
        nexmo_form.addRow("API Secret:", self.nexmo_api_secret)

        self.nexmo_phone_number = QLineEdit(self.config.get("nexmo_phone_number", ""))
        self.nexmo_phone_number.setEnabled(self.config.get("sms_notifications", False))
        self.nexmo_phone_number.setPlaceholderText("+1234567890")
        nexmo_form.addRow("From Number:", self.nexmo_phone_number)

        # Add Nexmo group to layout
        layout.addWidget(self.nexmo_group)

        # Test SMS button
        test_button_layout = QHBoxLayout()

        self.test_sms_button = QPushButton("Test SMS")
        self.test_sms_button.setEnabled(self.config.get("sms_notifications", False))
        self.test_sms_button.clicked.connect(self.test_sms)
        test_button_layout.addStretch()
        test_button_layout.addWidget(self.test_sms_button)

        layout.addLayout(test_button_layout)

        # Add spacer
        layout.addStretch()

        # Show/hide provider settings based on current selection
        self.toggle_sms_provider(self.sms_provider.currentText())

    def toggle_email_settings(self, enabled):
        """Toggle email settings based on checkbox"""
        self.email_address.setEnabled(enabled)
        self.email_from.setEnabled(enabled)
        self.email_smtp_server.setEnabled(enabled)
        self.email_smtp_port.setEnabled(enabled)
        self.email_username.setEnabled(enabled)
        self.email_password.setEnabled(enabled)
        self.email_use_tls.setEnabled(enabled)
        self.test_email_button.setEnabled(enabled)

    def toggle_sms_settings(self, enabled):
        """Toggle SMS settings based on checkbox"""
        self.sms_provider.setEnabled(enabled)
        self.phone_number.setEnabled(enabled)
        self.twilio_account_sid.setEnabled(enabled)
        self.twilio_auth_token.setEnabled(enabled)
        self.twilio_phone_number.setEnabled(enabled)
        self.nexmo_api_key.setEnabled(enabled)
        self.nexmo_api_secret.setEnabled(enabled)
        self.nexmo_phone_number.setEnabled(enabled)
        self.test_sms_button.setEnabled(enabled)

        # Show/hide provider settings based on current selection
        self.toggle_sms_provider(self.sms_provider.currentText())

    def toggle_sms_provider(self, provider):
        """Toggle SMS provider settings based on selection"""
        if provider == "Twilio":
            self.twilio_group.setVisible(True)
            self.nexmo_group.setVisible(False)
        else:  # Nexmo/Vonage
            self.twilio_group.setVisible(False)
            self.nexmo_group.setVisible(True)

    def test_email(self):
        """Test email notification"""
        # Validate email settings
        if not self.email_address.text():
            QMessageBox.warning(self, "Invalid Settings", "Please enter a recipient email address.")
            return

        if not self.email_smtp_server.text() or not self.email_username.text() or not self.email_password.text():
            QMessageBox.warning(self, "Invalid Settings", "Please enter SMTP server settings.")
            return

        # Update config with current settings
        self.update_config()

        # Create notification manager
        from src.utils.notifications import NotificationManager
        notification_manager = NotificationManager(self.config)

        # Send test email
        QMessageBox.information(self, "Sending Test Email", "Sending a test email notification...")

        # Create test device info
        device_info = {
            "id": "TEST_DEVICE",
            "name": "Test Device",
            "connection_time": "2023-01-01 12:00:00",
            "device_type": "Test",
            "vendor_id": "0000",
            "product_id": "0000",
            "manufacturer": "Test Manufacturer",
            "size": "1.0GB"
        }

        # Send notification
        notification_manager.send_notification(
            "Test Email Notification",
            "This is a test email notification from USB Monitoring System.",
            "info",
            device_info
        )

        QMessageBox.information(self, "Test Email", "Test email has been sent. Please check your inbox.")

    def test_sms(self):
        """Test SMS notification"""
        # Validate SMS settings
        if not self.phone_number.text():
            QMessageBox.warning(self, "Invalid Settings", "Please enter a recipient phone number.")
            return

        provider = self.sms_provider.currentText()

        if provider == "Twilio":
            if not self.twilio_account_sid.text() or not self.twilio_auth_token.text() or not self.twilio_phone_number.text():
                QMessageBox.warning(self, "Invalid Settings", "Please enter Twilio settings.")
                return
        else:  # Nexmo/Vonage
            if not self.nexmo_api_key.text() or not self.nexmo_api_secret.text():
                QMessageBox.warning(self, "Invalid Settings", "Please enter Nexmo/Vonage settings.")
                return

        # Update config with current settings
        self.update_config()

        # Force SMS notifications to be enabled for the test
        self.config["sms_notifications"] = True
        self.config["notify_threat"] = True

        # Create notification manager
        from src.utils.notifications import NotificationManager
        notification_manager = NotificationManager(self.config)

        # Send test SMS
        QMessageBox.information(self, "Sending Test SMS", "Sending a test SMS notification...")

        # Create test device info with scan results
        device_info = {
            "id": "TEST_DEVICE",
            "name": "Test Device",
            "connection_time": "2023-01-01 12:00:00",
            "manufacturer": "Test Manufacturer",
            "serial_number": "TEST123456",
            "custom_sms": f"Sent from your Twilio trial account - TEST: This is a test SMS from USB Monitor.\n\nDevice ID: TEST_DEVICE\nDevice Name: Test Device\nManufacturer: Test Manufacturer\nSerial Number: TEST123456\nFiles Scanned: 100 of 100\nScan Duration: 2.5 seconds\nInfected Files: None\nSuspicious Files: None"
        }

        # Send notification directly using SMS method
        notification_manager._send_sms_notification(
            "Test SMS",
            "This is a test SMS from USB Monitor",
            "critical",  # Use critical to ensure SMS is sent
            device_info
        )

        QMessageBox.information(self, "Test SMS", "Test SMS has been sent. Please check your phone.")

    def update_config(self):
        """Update config with current settings"""
        # Email settings
        self.config["email_notifications"] = self.email_notifications.isChecked()
        self.config["email_address"] = self.email_address.text()
        self.config["email_from"] = self.email_from.text()
        self.config["email_smtp_server"] = self.email_smtp_server.text()
        self.config["email_smtp_port"] = self.email_smtp_port.value()
        self.config["email_username"] = self.email_username.text()
        self.config["email_password"] = self.email_password.text()
        self.config["email_use_tls"] = self.email_use_tls.isChecked()

        # SMS settings
        self.config["sms_notifications"] = self.sms_notifications.isChecked()
        self.config["phone_number"] = self.phone_number.text()

        # Set SMS provider
        provider = self.sms_provider.currentText()
        if provider == "Twilio":
            self.config["sms_provider"] = "twilio"
        else:
            self.config["sms_provider"] = "nexmo"

        # Twilio settings
        self.config["twilio_account_sid"] = self.twilio_account_sid.text()
        self.config["twilio_auth_token"] = self.twilio_auth_token.text()
        self.config["twilio_phone_number"] = self.twilio_phone_number.text()

        # Nexmo settings
        self.config["nexmo_api_key"] = self.nexmo_api_key.text()
        self.config["nexmo_api_secret"] = self.nexmo_api_secret.text()
        self.config["nexmo_phone_number"] = self.nexmo_phone_number.text()

    def save_settings(self):
        """Save notification settings"""
        # Validate settings
        if self.email_notifications.isChecked():
            if not self.email_address.text():
                QMessageBox.warning(self, "Invalid Settings", "Please enter a recipient email address.")
                return

            if not self.email_smtp_server.text() or not self.email_username.text() or not self.email_password.text():
                QMessageBox.warning(self, "Invalid Settings", "Please enter SMTP server settings.")
                return

        if self.sms_notifications.isChecked():
            if not self.phone_number.text():
                QMessageBox.warning(self, "Invalid Settings", "Please enter a recipient phone number.")
                return

            provider = self.sms_provider.currentText()

            if provider == "Twilio":
                if not self.twilio_account_sid.text() or not self.twilio_auth_token.text() or not self.twilio_phone_number.text():
                    QMessageBox.warning(self, "Invalid Settings", "Please enter Twilio settings.")
                    return
            else:  # Nexmo/Vonage
                if not self.nexmo_api_key.text() or not self.nexmo_api_secret.text():
                    QMessageBox.warning(self, "Invalid Settings", "Please enter Nexmo/Vonage settings.")
                    return

        # Update config
        self.update_config()

        # Accept dialog
        self.accept()
