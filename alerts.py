#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Alerts Widget
Shows security alerts and notifications
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QComboBox, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

class AlertsWidget(QWidget):
    """Alerts widget showing security alerts and notifications"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        # Initialize alerts list
        self.alerts = []

        # Create layout
        layout = QVBoxLayout(self)

        # Add title
        title_label = QLabel("Security Alerts")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # Add controls
        controls_layout = QHBoxLayout()

        # Filter label
        filter_label = QLabel("Filter:")
        controls_layout.addWidget(filter_label)

        # Filter combo box
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Alerts", "Critical", "Warning", "Info"])
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        controls_layout.addWidget(self.filter_combo)

        # Show resolved checkbox
        self.show_resolved = QCheckBox("Show Resolved")
        self.show_resolved.setChecked(True)
        self.show_resolved.stateChanged.connect(self.apply_filter)
        controls_layout.addWidget(self.show_resolved)

        # Export button
        export_button = QPushButton("Export Alerts")
        export_button.setIcon(QIcon("assets/icons/export.png"))
        export_button.clicked.connect(self.export_alerts)
        controls_layout.addWidget(export_button)

        # Clear button
        clear_button = QPushButton("Clear All")
        clear_button.setIcon(QIcon("assets/icons/clear.png"))
        clear_button.clicked.connect(self.clear_alerts)
        controls_layout.addWidget(clear_button)

        # Add spacer
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Add alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            "Severity", "Title", "Message", "Timestamp", "Actions"
        ])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.alerts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.alerts_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.alerts_table.verticalHeader().setVisible(False)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.alerts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_table.setAlternatingRowColors(True)

        layout.addWidget(self.alerts_table)

        # Add notification settings section
        settings_label = QLabel("Notification Settings")
        settings_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(settings_label)

        # Add notification settings
        settings_layout = QVBoxLayout()

        # Email notifications
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email Notifications:"))

        self.email_enabled = QCheckBox("Enabled")
        email_layout.addWidget(self.email_enabled)

        email_layout.addWidget(QLabel("Email Address:"))
        self.email_address = QComboBox()
        self.email_address.setEditable(True)
        self.email_address.addItems(["admin@example.com"])
        email_layout.addWidget(self.email_address)

        email_layout.addStretch()

        settings_layout.addLayout(email_layout)

        # SMS notifications
        sms_layout = QHBoxLayout()
        sms_layout.addWidget(QLabel("SMS Notifications:"))

        self.sms_enabled = QCheckBox("Enabled")
        self.sms_enabled.setChecked(True)  # Enable SMS by default
        sms_layout.addWidget(self.sms_enabled)

        sms_layout.addWidget(QLabel("Phone Number:"))
        self.phone_number = QComboBox()
        self.phone_number.setEditable(True)
        self.phone_number.addItems(["+919944273645", "+1234567890"])  # Your phone number first
        sms_layout.addWidget(self.phone_number)

        sms_layout.addStretch()

        settings_layout.addLayout(sms_layout)

        # Desktop notifications
        desktop_layout = QHBoxLayout()
        desktop_layout.addWidget(QLabel("Desktop Notifications:"))

        self.desktop_enabled = QCheckBox("Enabled")
        self.desktop_enabled.setChecked(True)
        desktop_layout.addWidget(self.desktop_enabled)

        desktop_layout.addStretch()

        settings_layout.addLayout(desktop_layout)

        # Save settings button
        save_button = QPushButton("Save Notification Settings")
        save_button.clicked.connect(self.save_notification_settings)
        settings_layout.addWidget(save_button)

        layout.addLayout(settings_layout)

        # Set layout stretch factors
        layout.setStretch(2, 3)  # Alerts table

    def add_alert(self, alert):
        """Add an alert to the list"""
        # Add to alerts list
        self.alerts.append(alert)

        # Update table
        self.apply_filter()

    def apply_filter(self):
        """Apply filter to alerts table"""
        # Get filter settings
        filter_index = self.filter_combo.currentIndex()
        show_resolved = self.show_resolved.isChecked()

        # Clear table
        self.alerts_table.setRowCount(0)

        # Filter alerts
        filtered_alerts = []

        for alert in self.alerts:
            # Check if resolved
            if not show_resolved and alert.get("resolved", False):
                continue

            # Check severity filter
            if filter_index == 1 and alert.get("severity") != "critical":
                continue
            elif filter_index == 2 and alert.get("severity") != "warning":
                continue
            elif filter_index == 3 and alert.get("severity") != "info":
                continue

            filtered_alerts.append(alert)

        # Add alerts to table
        for i, alert in enumerate(filtered_alerts):
            self.alerts_table.insertRow(i)

            # Severity
            severity_item = QTableWidgetItem(alert.get("severity", "").capitalize())
            severity_item.setForeground(QColor(self._get_severity_color(alert.get("severity"))))
            self.alerts_table.setItem(i, 0, severity_item)

            # Title
            title_item = QTableWidgetItem(alert.get("title", ""))
            self.alerts_table.setItem(i, 1, title_item)

            # Message
            message = alert.get("message", "")

            # Add file details if available
            if "files" in alert and alert["files"]:
                message += "\n\nFiles:"
                for file_path in alert["files"][:5]:  # Show first 5 files
                    message += f"\n- {file_path}"
                if len(alert["files"]) > 5:
                    message += f"\n- ... and {len(alert['files']) - 5} more files"

            message_item = QTableWidgetItem(message)
            self.alerts_table.setItem(i, 2, message_item)

            # Timestamp
            time_item = QTableWidgetItem(alert.get("timestamp", ""))
            self.alerts_table.setItem(i, 3, time_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)

            # Resolve/Unresolve button
            resolve_button = QPushButton("Unresolve" if alert.get("resolved", False) else "Resolve")
            resolve_button.setProperty("alert_index", i)
            resolve_button.clicked.connect(lambda checked, idx=i: self.toggle_resolved(idx))
            actions_layout.addWidget(resolve_button)

            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.setProperty("alert_index", i)
            delete_button.clicked.connect(lambda checked, idx=i: self.delete_alert(idx))
            actions_layout.addWidget(delete_button)

            # View Details button (if files are present)
            if "files" in alert and alert["files"]:
                details_button = QPushButton("View Files")
                details_button.setProperty("alert_index", i)
                details_button.clicked.connect(lambda checked, idx=i: self.show_file_details(idx))
                actions_layout.addWidget(details_button)

            self.alerts_table.setCellWidget(i, 4, actions_widget)

    def toggle_resolved(self, index):
        """Toggle resolved status of an alert"""
        # Get alert
        alert = self.alerts[index]

        # Toggle resolved status
        alert["resolved"] = not alert.get("resolved", False)

        # Update table
        self.apply_filter()

    def delete_alert(self, index):
        """Delete an alert"""
        # Remove from alerts list
        del self.alerts[index]

        # Update table
        self.apply_filter()

    def export_alerts(self):
        """Export alerts to a file"""
        # Get file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Alerts", "alerts.txt", "Text Files (*.txt)"
        )

        if not file_path:
            return

        # Write to file
        try:
            with open(file_path, "w") as f:
                f.write(f"USB Monitoring System - Security Alerts\n")
                f.write(f"======================================\n\n")

                for alert in self.alerts:
                    f.write(f"[{alert.get('severity', '').upper()}] {alert.get('title', '')}\n")
                    f.write(f"Timestamp: {alert.get('timestamp', '')}\n")
                    f.write(f"Message: {alert.get('message', '')}\n")
                    f.write(f"Status: {'Resolved' if alert.get('resolved', False) else 'Unresolved'}\n")
                    f.write(f"\n")

            QMessageBox.information(self, "Export Successful", f"Alerts exported to {file_path}")

        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Error exporting alerts: {str(e)}")

    def clear_alerts(self):
        """Clear all alerts"""
        # Confirm with user
        reply = QMessageBox.question(
            self, "Clear Alerts",
            "Are you sure you want to clear all alerts?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Clear alerts
            self.alerts = []

            # Update table
            self.apply_filter()

    def save_notification_settings(self):
        """Save notification settings"""
        # Get settings
        email_enabled = self.email_enabled.isChecked()
        email_address = self.email_address.currentText()
        sms_enabled = self.sms_enabled.isChecked()
        phone_number = self.phone_number.currentText()
        desktop_enabled = self.desktop_enabled.isChecked()

        # Validate settings
        if email_enabled and not email_address:
            QMessageBox.warning(self, "Invalid Settings", "Please enter an email address.")
            return

        if sms_enabled and not phone_number:
            QMessageBox.warning(self, "Invalid Settings", "Please enter a phone number.")
            return

        # Save settings to config file
        try:
            import json
            import os

            # Create config directory if it doesn't exist
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
            os.makedirs(config_dir, exist_ok=True)

            # Create config file
            config_path = os.path.join(config_dir, "notification_config.json")

            # Create config data
            config_data = {
                "sms_notifications": sms_enabled,
                "sms_provider": "twilio",
                "phone_number": phone_number,
                "twilio_account_sid": "AC94656f2081ae1c98c4cece8dd68ca056",
                "twilio_auth_token": "70cfd6672bc72163dd2077bc3562ffa9",
                "twilio_phone_number": "+19082631380",
                "email_notifications": email_enabled,
                "email_address": email_address,
                "notify_connect": True,
                "notify_disconnect": False,
                "notify_scan": True,
                "notify_threat": True,
                "desktop_notifications": desktop_enabled
            }

            # Save config data
            with open(config_path, "w") as f:
                json.dump(config_data, f, indent=4)

            # Show success message
            QMessageBox.information(self, "Settings Saved", "Notification settings saved successfully.")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving settings: {str(e)}")

    def show_file_details(self, index):
        """Show details of files in an alert"""
        # Get alert
        alert = self.alerts[index]

        # Check if files are present
        if "files" not in alert or not alert["files"]:
            QMessageBox.information(self, "No Files", "No files to display.")
            return

        # Create message with file details
        message = f"Files detected in {alert.get('title', 'Alert')}:\n\n"

        for i, file_path in enumerate(alert["files"]):
            message += f"{i+1}. {file_path}\n"

        # Show message box with file details
        QMessageBox.information(self, "File Details", message)

    def _get_severity_color(self, severity):
        """Get color for severity level"""
        if severity == "critical":
            return "#e74c3c"  # Red
        elif severity == "warning":
            return "#f39c12"  # Orange
        elif severity == "info":
            return "#3498db"  # Blue
        else:
            return "#bdc3c7"  # Light gray
