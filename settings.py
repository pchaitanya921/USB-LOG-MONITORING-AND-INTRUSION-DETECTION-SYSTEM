#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Settings Widget
Allows configuration of application settings
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QComboBox, QSpinBox, QLineEdit,
    QFormLayout, QGroupBox, QTabWidget, QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QFont

from src.utils.system_integration import SystemIntegration
from src.ui.notification_settings import NotificationSettingsDialog

class SettingsWidget(QWidget):
    """Settings widget for configuring application settings"""
    def __init__(self, config=None, parent=None):
        super().__init__(parent)

        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        # Store config
        self.config = config or {}

        # Create layout
        layout = QVBoxLayout(self)

        # Add title
        title_label = QLabel("Settings")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # Create tab widget for settings categories
        tab_widget = QTabWidget()

        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QFormLayout(startup_group)

        self.start_with_system = QCheckBox("Start with system")
        self.start_with_system.setChecked(self.config.get("start_with_system", False))
        startup_layout.addRow("", self.start_with_system)

        self.start_minimized = QCheckBox("Start minimized")
        self.start_minimized.setChecked(self.config.get("start_minimized", False))
        startup_layout.addRow("", self.start_minimized)

        general_layout.addWidget(startup_group)

        # UI settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout(ui_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText(self.config.get("theme", "System"))
        ui_layout.addRow("Theme:", self.theme_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German"])
        self.language_combo.setCurrentText(self.config.get("language", "English"))
        ui_layout.addRow("Language:", self.language_combo)

        general_layout.addWidget(ui_group)

        # Add spacer
        general_layout.addStretch()

        tab_widget.addTab(general_tab, "General")

        # Scanning settings tab
        scanning_tab = QWidget()
        scanning_layout = QVBoxLayout(scanning_tab)

        # Scan settings
        scan_group = QGroupBox("Scan Settings")
        scan_layout = QFormLayout(scan_group)

        self.scan_on_connect = QCheckBox("Scan devices on connect")
        self.scan_on_connect.setChecked(self.config.get("scan_on_connect", True))
        scan_layout.addRow("", self.scan_on_connect)

        self.block_on_threat = QCheckBox("Block devices with threats")
        self.block_on_threat.setChecked(self.config.get("block_on_threat", True))
        scan_layout.addRow("", self.block_on_threat)

        self.scan_depth_combo = QComboBox()
        self.scan_depth_combo.addItems(["Quick Scan", "Full Scan", "Custom"])
        self.scan_depth_combo.setCurrentText(self.config.get("scan_depth", "Quick Scan"))
        scan_layout.addRow("Scan Depth:", self.scan_depth_combo)

        self.scan_interval = QSpinBox()
        self.scan_interval.setMinimum(0)
        self.scan_interval.setMaximum(60)
        self.scan_interval.setValue(self.config.get("scan_interval", 0))
        self.scan_interval.setSuffix(" minutes")
        scan_layout.addRow("Auto-scan Interval:", self.scan_interval)

        scanning_layout.addWidget(scan_group)

        # File types settings
        filetypes_group = QGroupBox("File Types to Scan")
        filetypes_layout = QVBoxLayout(filetypes_group)

        self.scan_executables = QCheckBox("Executable files (.exe, .dll, .bat, etc.)")
        self.scan_executables.setChecked(self.config.get("scan_executables", True))
        filetypes_layout.addWidget(self.scan_executables)

        self.scan_documents = QCheckBox("Document files (.doc, .pdf, .xlsx, etc.)")
        self.scan_documents.setChecked(self.config.get("scan_documents", True))
        filetypes_layout.addWidget(self.scan_documents)

        self.scan_archives = QCheckBox("Archive files (.zip, .rar, .7z, etc.)")
        self.scan_archives.setChecked(self.config.get("scan_archives", True))
        filetypes_layout.addWidget(self.scan_archives)

        self.scan_all_files = QCheckBox("All files")
        self.scan_all_files.setChecked(self.config.get("scan_all_files", False))
        filetypes_layout.addWidget(self.scan_all_files)

        scanning_layout.addWidget(filetypes_group)

        # Add spacer
        scanning_layout.addStretch()

        tab_widget.addTab(scanning_tab, "Scanning")

        # Permissions settings tab
        permissions_tab = QWidget()
        permissions_layout = QVBoxLayout(permissions_tab)

        # Default permissions
        permissions_group = QGroupBox("Default Permissions")
        permissions_form = QFormLayout(permissions_group)

        self.default_permission = QComboBox()
        self.default_permission.addItems(["Read Only", "Full Access", "Blocked"])
        self.default_permission.setCurrentText(self.config.get("default_permission", "Read Only"))
        permissions_form.addRow("Default Permission:", self.default_permission)

        self.trusted_devices = QCheckBox("Allow full access for trusted devices")
        self.trusted_devices.setChecked(self.config.get("trusted_devices", True))
        permissions_form.addRow("", self.trusted_devices)

        permissions_layout.addWidget(permissions_group)

        # Trusted devices
        trusted_group = QGroupBox("Trusted Devices")
        trusted_layout = QVBoxLayout(trusted_group)

        # Add trusted devices list (simplified)
        trusted_layout.addWidget(QLabel("No trusted devices configured"))

        # Add button to add trusted device
        add_trusted_button = QPushButton("Add Trusted Device")
        trusted_layout.addWidget(add_trusted_button)

        permissions_layout.addWidget(trusted_group)

        # Add spacer
        permissions_layout.addStretch()

        tab_widget.addTab(permissions_tab, "Permissions")

        # Notifications settings tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)

        # Notification settings
        notifications_group = QGroupBox("Notification Settings")
        notifications_form = QFormLayout(notifications_group)

        self.desktop_notifications = QCheckBox("Show desktop notifications")
        self.desktop_notifications.setChecked(self.config.get("desktop_notifications", True))
        notifications_form.addRow("", self.desktop_notifications)

        self.email_notifications = QCheckBox("Send email notifications")
        self.email_notifications.setChecked(self.config.get("email_notifications", False))
        notifications_form.addRow("", self.email_notifications)

        self.email_address = QLineEdit(self.config.get("email_address", ""))
        notifications_form.addRow("Email Address:", self.email_address)

        self.sms_notifications = QCheckBox("Send SMS notifications")
        self.sms_notifications.setChecked(self.config.get("sms_notifications", False))
        notifications_form.addRow("", self.sms_notifications)

        self.phone_number = QLineEdit(self.config.get("phone_number", ""))
        notifications_form.addRow("Phone Number:", self.phone_number)

        # Advanced notification settings button
        advanced_notifications_button = QPushButton("Advanced Notification Settings...")
        advanced_notifications_button.clicked.connect(self.open_advanced_notifications)
        notifications_form.addRow("", advanced_notifications_button)

        notifications_layout.addWidget(notifications_group)

        # Notification events
        events_group = QGroupBox("Notification Events")
        events_layout = QVBoxLayout(events_group)

        self.notify_connect = QCheckBox("Device connected")
        self.notify_connect.setChecked(self.config.get("notify_connect", True))
        events_layout.addWidget(self.notify_connect)

        self.notify_disconnect = QCheckBox("Device disconnected")
        self.notify_disconnect.setChecked(self.config.get("notify_disconnect", False))
        events_layout.addWidget(self.notify_disconnect)

        self.notify_scan = QCheckBox("Scan completed")
        self.notify_scan.setChecked(self.config.get("notify_scan", True))
        events_layout.addWidget(self.notify_scan)

        self.notify_threat = QCheckBox("Threat detected")
        self.notify_threat.setChecked(self.config.get("notify_threat", True))
        events_layout.addWidget(self.notify_threat)

        notifications_layout.addWidget(events_group)

        # Add spacer
        notifications_layout.addStretch()

        tab_widget.addTab(notifications_tab, "Notifications")

        # Advanced settings tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # Logging settings
        logging_group = QGroupBox("Logging")
        logging_form = QFormLayout(logging_group)

        self.enable_logging = QCheckBox("Enable logging")
        self.enable_logging.setChecked(self.config.get("enable_logging", True))
        logging_form.addRow("", self.enable_logging)

        self.log_level = QComboBox()
        self.log_level.addItems(["Debug", "Info", "Warning", "Error"])
        self.log_level.setCurrentText(self.config.get("log_level", "Info"))
        logging_form.addRow("Log Level:", self.log_level)

        self.log_path = QLineEdit(self.config.get("log_path", "logs"))
        logging_form.addRow("Log Directory:", self.log_path)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_log_path)
        logging_form.addRow("", browse_button)

        advanced_layout.addWidget(logging_group)

        # System tray settings
        tray_group = QGroupBox("System Tray")
        tray_layout = QVBoxLayout(tray_group)

        self.system_tray = QCheckBox("Show in system tray")
        self.system_tray.setChecked(self.config.get("system_tray", True))
        tray_layout.addWidget(self.system_tray)

        self.minimize_to_tray = QCheckBox("Minimize to tray instead of taskbar")
        self.minimize_to_tray.setChecked(self.config.get("minimize_to_tray", True))
        tray_layout.addWidget(self.minimize_to_tray)

        self.close_to_tray = QCheckBox("Close to tray instead of exiting")
        self.close_to_tray.setChecked(self.config.get("close_to_tray", True))
        tray_layout.addWidget(self.close_to_tray)

        advanced_layout.addWidget(tray_group)

        # System integration tab
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)

        # Startup integration
        startup_group = QGroupBox("Startup Integration")
        startup_layout = QVBoxLayout(startup_group)

        self.register_startup = QCheckBox("Start application when system boots")
        self.register_startup.setChecked(self.config.get("register_startup", False))
        self.register_startup.toggled.connect(self.toggle_startup_registration)
        startup_layout.addWidget(self.register_startup)

        # Add startup status label
        self.startup_status = QLabel("Startup registration is disabled")
        startup_layout.addWidget(self.startup_status)

        system_layout.addWidget(startup_group)

        # Context menu integration
        context_group = QGroupBox("Context Menu Integration")
        context_layout = QVBoxLayout(context_group)

        self.register_context_menu = QCheckBox("Add 'Scan with USB Monitor' to context menu")
        self.register_context_menu.setChecked(self.config.get("register_context_menu", False))
        self.register_context_menu.toggled.connect(self.toggle_context_menu)
        context_layout.addWidget(self.register_context_menu)

        # Add context menu status label
        self.context_menu_status = QLabel("Context menu integration is disabled")
        context_layout.addWidget(self.context_menu_status)

        system_layout.addWidget(context_group)

        # Add spacer
        system_layout.addStretch()

        tab_widget.addTab(system_tab, "System Integration")

        # Add spacer
        advanced_layout.addStretch()

        tab_widget.addTab(advanced_tab, "Advanced")

        layout.addWidget(tab_widget)

        # Add buttons
        buttons_layout = QHBoxLayout()

        # Add spacer
        buttons_layout.addStretch()

        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(reset_button)

        # Save button
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)

        layout.addLayout(buttons_layout)

    def browse_log_path(self):
        """Browse for log directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Log Directory", self.log_path.text()
        )

        if directory:
            self.log_path.setText(directory)

    def reset_settings(self):
        """Reset settings to defaults"""
        # Confirm with user
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Reset general settings
            self.start_with_system.setChecked(False)
            self.start_minimized.setChecked(False)
            self.theme_combo.setCurrentText("System")
            self.language_combo.setCurrentText("English")

            # Reset scanning settings
            self.scan_on_connect.setChecked(True)
            self.block_on_threat.setChecked(True)
            self.scan_depth_combo.setCurrentText("Quick Scan")
            self.scan_interval.setValue(0)
            self.scan_executables.setChecked(True)
            self.scan_documents.setChecked(True)
            self.scan_archives.setChecked(True)
            self.scan_all_files.setChecked(False)

            # Reset permissions settings
            self.default_permission.setCurrentText("Read Only")
            self.trusted_devices.setChecked(True)

            # Reset notifications settings
            self.desktop_notifications.setChecked(True)
            self.email_notifications.setChecked(False)
            self.email_address.setText("")
            self.sms_notifications.setChecked(False)
            self.phone_number.setText("")
            self.notify_connect.setChecked(True)
            self.notify_disconnect.setChecked(False)
            self.notify_scan.setChecked(True)
            self.notify_threat.setChecked(True)

            # Reset advanced settings
            self.enable_logging.setChecked(True)
            self.log_level.setCurrentText("Info")
            self.log_path.setText("logs")
            self.system_tray.setChecked(True)
            self.minimize_to_tray.setChecked(True)
            self.close_to_tray.setChecked(True)

            QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults.")

    def toggle_startup_registration(self, enabled):
        """Toggle startup registration"""
        # Initialize system integration if not already done
        if not hasattr(self, 'system_integration'):
            self.system_integration = SystemIntegration()

        # Register or unregister startup
        success, message = self.system_integration.register_startup(enabled)

        if success:
            self.startup_status.setText(message)
            self.config["register_startup"] = enabled
        else:
            QMessageBox.warning(self, "Startup Registration Error", message)
            # Revert checkbox state
            self.register_startup.setChecked(not enabled)

    def toggle_context_menu(self, enabled):
        """Toggle context menu integration"""
        # Initialize system integration if not already done
        if not hasattr(self, 'system_integration'):
            self.system_integration = SystemIntegration()

        # Add or remove context menu
        success, message = self.system_integration.add_context_menu(enabled)

        if success:
            self.context_menu_status.setText(message)
            self.config["register_context_menu"] = enabled
        else:
            QMessageBox.warning(self, "Context Menu Integration Error", message)
            # Revert checkbox state
            self.register_context_menu.setChecked(not enabled)

    def open_advanced_notifications(self):
        """Open advanced notification settings dialog"""
        # Create dialog
        dialog = NotificationSettingsDialog(self.config, self)

        # Show dialog
        if dialog.exec_():
            # Update config
            self.config.update(dialog.config)

            # Update UI
            self.email_notifications.setChecked(self.config.get("email_notifications", False))
            self.email_address.setText(self.config.get("email_address", ""))
            self.sms_notifications.setChecked(self.config.get("sms_notifications", False))
            self.phone_number.setText(self.config.get("phone_number", ""))

            QMessageBox.information(self, "Settings Updated", "Notification settings have been updated.")

    def save_settings(self):
        """Save settings"""
        # Validate settings
        if self.email_notifications.isChecked() and not self.email_address.text():
            QMessageBox.warning(self, "Invalid Settings", "Please enter an email address for email notifications.")
            return

        if self.sms_notifications.isChecked() and not self.phone_number.text():
            QMessageBox.warning(self, "Invalid Settings", "Please enter a phone number for SMS notifications.")
            return

        # Update config
        self.config["start_with_system"] = self.start_with_system.isChecked()
        self.config["start_minimized"] = self.start_minimized.isChecked()
        self.config["theme"] = self.theme_combo.currentText()
        self.config["language"] = self.language_combo.currentText()

        self.config["scan_on_connect"] = self.scan_on_connect.isChecked()
        self.config["block_on_threat"] = self.block_on_threat.isChecked()
        self.config["scan_depth"] = self.scan_depth_combo.currentText()
        self.config["scan_interval"] = self.scan_interval.value()
        self.config["scan_executables"] = self.scan_executables.isChecked()
        self.config["scan_documents"] = self.scan_documents.isChecked()
        self.config["scan_archives"] = self.scan_archives.isChecked()
        self.config["scan_all_files"] = self.scan_all_files.isChecked()

        self.config["default_permission"] = self.default_permission.currentText()
        self.config["trusted_devices"] = self.trusted_devices.isChecked()

        self.config["desktop_notifications"] = self.desktop_notifications.isChecked()
        self.config["email_notifications"] = self.email_notifications.isChecked()
        self.config["email_address"] = self.email_address.text()
        self.config["sms_notifications"] = self.sms_notifications.isChecked()
        self.config["phone_number"] = self.phone_number.text()
        self.config["notify_connect"] = self.notify_connect.isChecked()
        self.config["notify_disconnect"] = self.notify_disconnect.isChecked()
        self.config["notify_scan"] = self.notify_scan.isChecked()
        self.config["notify_threat"] = self.notify_threat.isChecked()

        # If email or SMS notifications are disabled, clear credentials for security
        if not self.config["email_notifications"]:
            self.config["email_password"] = ""

        if not self.config["sms_notifications"]:
            self.config["twilio_auth_token"] = ""
            self.config["nexmo_api_secret"] = ""

        self.config["enable_logging"] = self.enable_logging.isChecked()
        self.config["log_level"] = self.log_level.currentText()
        self.config["log_path"] = self.log_path.text()
        self.config["system_tray"] = self.system_tray.isChecked()
        self.config["minimize_to_tray"] = self.minimize_to_tray.isChecked()
        self.config["close_to_tray"] = self.close_to_tray.isChecked()

        # System integration settings
        self.config["register_startup"] = self.register_startup.isChecked()
        self.config["register_context_menu"] = self.register_context_menu.isChecked()

        # Save to settings file (in a real app)
        # QSettings().setValue("config", self.config)

        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")

        # Apply settings (in a real app, this would apply the settings immediately)
        # self.parent().apply_settings(self.config)
