#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main Window Module
Main application window that contains all views
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QStatusBar,
    QLabel, QPushButton, QToolBar, QAction, QMessageBox, QMenu,
    QDialog, QApplication, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon

from src.ui.dashboard import DashboardWidget
from src.ui.devices import DevicesWidget
from src.ui.scans import ScansWidget
from src.ui.alerts import AlertsWidget
from src.ui.settings import SettingsWidget
from src.ui.login_dialog import LoginDialog
from src.ui.user_management import UserManagementDialog
from src.ui.radial_scanning import RadialScanningBackground
from src.ui.styles import get_dark_theme_stylesheet

import os

from src.backend.usb_detector import USBDetector
from src.backend.scanner import Scanner
from src.backend.permissions import PermissionManager
from src.utils.auth import AuthManager
from src.utils.notifications import NotificationManager

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self, config=None):
        super().__init__()

        # Store config
        self.config = config or {}

        # Initialize backend components
        self.usb_detector = USBDetector()
        self.scanner = Scanner()
        self.permission_manager = PermissionManager()
        self.auth_manager = AuthManager()
        # Configure notifications
        # SMS notifications
        self.config["sms_notifications"] = True
        self.config["phone_number"] = "+919944273645"
        self.config["twilio_account_sid"] = "AC94656f2081ae1c98c4cece8dd68ca056"
        self.config["twilio_auth_token"] = "70cfd6672bc72163dd2077bc3562ffa9"
        self.config["twilio_phone_number"] = "+19082631380"

        # Email notifications
        self.config["email_notifications"] = True
        self.config["email_username"] = "chaitanyasai9391@gmail.com"
        self.config["email_password"] = "vvkdquyanoswsvso"
        self.config["email_address"] = "chaitanyasai401@gmail.com"
        self.config["email_smtp_server"] = "smtp.gmail.com"
        self.config["email_smtp_port"] = 587
        self.config["email_from"] = "chaitanyasai9391@gmail.com"

        self.notification_manager = NotificationManager(self.config)

        # Apply dark theme stylesheet
        self.setStyleSheet(get_dark_theme_stylesheet())

        # Set up UI
        self.setWindowTitle("USB Monitoring System")
        self.setMinimumSize(1000, 700)

        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                "assets", "icons", "usb_monitor.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Create a background frame for animations only
        self.background_frame = QFrame(self)
        self.background_frame.setGeometry(self.rect())
        self.background_frame.setStyleSheet("background-color: transparent;")

        # Create radial scanning background on the background frame
        self.animated_background = RadialScanningBackground(self.background_frame)
        self.animated_background.setGeometry(self.background_frame.rect())

        # Create central widget with solid background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Set solid background for central widget
        self.central_widget.setAutoFillBackground(True)
        self.central_widget.setStyleSheet("background-color: #0a1520;")

        # Make sure tab widget has fully opaque background
        self.tab_widget_style = """
            QTabWidget::pane {
                background-color: #0a1520;
                border: 1px solid #00aa00;
                opacity: 1.0;
            }

            QTabBar::tab {
                background-color: #0a1520;
                color: #00ff00;
                border: 1px solid #00aa00;
                padding: 5px 10px;
                opacity: 1.0;
            }

            QTabBar::tab:selected {
                background-color: #00aa00;
                color: #000000;
                opacity: 1.0;
            }

            QWidget {
                background-color: #0a1520;
                opacity: 1.0;
            }
        """

        # Connect resize event to update background size
        self.central_widget.resizeEvent = self.on_central_widget_resize

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self.tab_widget_style)
        self.layout.addWidget(self.tab_widget)

        # Create tabs
        self.dashboard_widget = DashboardWidget(self.usb_detector, self.scanner, self.permission_manager)
        self.devices_widget = DevicesWidget(self.usb_detector, self.scanner, self.permission_manager)
        self.scans_widget = ScansWidget(self.scanner)
        self.alerts_widget = AlertsWidget()
        self.settings_widget = SettingsWidget(config)

        # Set tab widget styling
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #00aa00;
                background-color: #0a0f14;
            }

            QTabBar::tab {
                background-color: #0a1520;
                color: #00ff00;
                border: 1px solid #00aa00;
                border-bottom: none;
                padding: 8px 15px;
                margin-right: 2px;
            }

            QTabBar::tab:selected {
                background-color: #1a2a3a;
                border-bottom: 1px solid #1a2a3a;
            }

            QTabBar::tab:hover:!selected {
                background-color: #152535;
            }
        """)

        # Get icon paths
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icons")
        dashboard_icon = QIcon(os.path.join(icons_dir, "dashboard.png"))
        devices_icon = QIcon(os.path.join(icons_dir, "devices.png"))
        scan_icon = QIcon(os.path.join(icons_dir, "scan.png"))
        alert_icon = QIcon(os.path.join(icons_dir, "alert.png"))
        settings_icon = QIcon(os.path.join(icons_dir, "settings.png"))

        # Add tabs to tab widget
        self.tab_widget.addTab(self.dashboard_widget, dashboard_icon, "Dashboard")
        self.tab_widget.addTab(self.devices_widget, devices_icon, "Devices")
        self.tab_widget.addTab(self.scans_widget, scan_icon, "Scans")
        self.tab_widget.addTab(self.alerts_widget, alert_icon, "Alerts")
        self.tab_widget.addTab(self.settings_widget, settings_icon, "Settings")

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add status bar widgets
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Add device count to status bar
        self.device_count_label = QLabel("No USB devices connected")
        self.status_bar.addPermanentWidget(self.device_count_label)

        # Add user info to status bar
        self.user_label = QLabel("Not logged in")
        self.status_bar.addPermanentWidget(self.user_label)

        # Create toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        # Set toolbar styling
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #0a0f14;
                border: none;
                spacing: 10px;
                padding: 5px;
            }

            QToolButton {
                background-color: transparent;
                border: none;
                color: #00ff00;
                padding: 5px;
            }

            QToolButton:hover {
                background-color: #1a2a3a;
                border: 1px solid #00aa00;
            }

            QToolButton:pressed {
                background-color: #0a1a2a;
            }
        """)

        # Add actions to toolbar
        # Refresh action
        refresh_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                       "assets", "icons", "refresh.png")
        self.refresh_action = QAction(QIcon(refresh_icon_path), "Refresh", self)
        self.refresh_action.triggered.connect(self.refresh_devices)
        self.refresh_action.setToolTip("Refresh USB devices")
        self.toolbar.addAction(self.refresh_action)

        # Set icon size for toolbar
        self.toolbar.setIconSize(QSize(32, 32))  # Larger icons for better visibility

        # Scan action
        scan_all_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    "assets", "icons", "scan_all.png")
        self.scan_all_action = QAction(QIcon(scan_all_icon_path), "Scan All Devices", self)
        self.scan_all_action.triggered.connect(self.scan_all_devices)
        self.scan_all_action.setToolTip("Scan all connected USB devices")
        self.toolbar.addAction(self.scan_all_action)

        # Add user menu to toolbar
        self.toolbar.addSeparator()

        # User action
        user_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    "assets", "icons", "user.png")
        self.user_action = QAction(QIcon(user_icon_path), "User", self)
        self.user_action.setToolTip("User account options")
        self.user_menu = QMenu(self)

        # Style the user menu
        self.user_menu.setStyleSheet("""
            QMenu {
                background-color: #0a1520;
                color: #00ff00;
                border: 1px solid #00aa00;
            }

            QMenu::item {
                padding: 5px 20px;
            }

            QMenu::item:selected {
                background-color: #1a2a3a;
            }

            QMenu::separator {
                height: 1px;
                background-color: #00aa00;
                margin: 5px 0px;
            }
        """)

        self.login_action = QAction("Login", self)
        self.login_action.triggered.connect(self.show_login_dialog)
        self.user_menu.addAction(self.login_action)

        self.logout_action = QAction("Logout", self)
        self.logout_action.triggered.connect(self.logout)
        self.logout_action.setEnabled(False)
        self.user_menu.addAction(self.logout_action)

        self.user_menu.addSeparator()

        self.manage_users_action = QAction("Manage Users", self)
        self.manage_users_action.triggered.connect(self.show_user_management)
        self.manage_users_action.setEnabled(False)
        self.user_menu.addAction(self.manage_users_action)

        self.user_action.setMenu(self.user_menu)
        self.toolbar.addAction(self.user_action)

        # Set up timer for device detection
        self.detection_timer = QTimer()
        self.detection_timer.timeout.connect(self.check_devices)
        self.detection_timer.start(5000)  # Check every 5 seconds

        # Initial device check
        self.check_devices()

        # Connect signals
        self.usb_detector.device_connected.connect(self.on_device_connected)
        self.usb_detector.device_disconnected.connect(self.on_device_disconnected)
        self.scanner.scan_started.connect(self.on_scan_started)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.permission_manager.permission_changed.connect(self.on_permission_changed)
        self.permission_manager.permission_error.connect(self.on_permission_error)

        # Connect auth signals
        self.auth_manager.user_logged_in.connect(self.on_user_logged_in)
        self.auth_manager.user_logged_out.connect(self.on_user_logged_out)

        # Show login dialog on startup
        QTimer.singleShot(500, self.show_login_dialog)

    def check_devices(self):
        """Check for connected USB devices"""
        devices = self.usb_detector.get_connected_devices()

        # Update device count label
        if not devices:
            self.device_count_label.setText("No USB devices connected")
        elif len(devices) == 1:
            self.device_count_label.setText("1 USB device connected")
        else:
            self.device_count_label.setText(f"{len(devices)} USB devices connected")

        # Update device list in tabs
        self.dashboard_widget.update_devices(devices)
        self.devices_widget.update_devices(devices)

    def refresh_devices(self):
        """Manually refresh device list"""
        self.status_label.setText("Refreshing devices...")
        self.check_devices()
        self.status_label.setText("Devices refreshed")

    def scan_all_devices(self):
        """Scan all connected devices"""
        devices = self.usb_detector.get_connected_devices()

        if not devices:
            QMessageBox.information(self, "No Devices", "No USB devices connected to scan.")
            return

        self.status_label.setText(f"Scanning {len(devices)} devices...")

        # Start scan for each device
        for device in devices:
            self.scanner.scan_device(device)

    def on_device_connected(self, device):
        """Handle device connected signal"""
        self.status_label.setText(f"USB device connected: {device.name}")

        # Send notification
        self.notification_manager.send_device_connected_notification(device)

        # Auto-scan if enabled
        if self.config.get("scan_on_connect", True):
            self.scanner.scan_device(device)

        self.check_devices()

    def on_device_disconnected(self, device_id):
        """Handle device disconnected signal"""
        # Get device info if available
        device = None
        for d in self.usb_detector.get_connected_devices():
            if d.id == device_id:
                device = d
                break

        self.status_label.setText(f"USB device disconnected: {device_id}")

        # Send notification if we have device info
        if device:
            self.notification_manager.send_device_disconnected_notification(device)

        self.check_devices()

    def on_scan_started(self, scan_id, device_id):
        """Handle scan started signal"""
        self.status_label.setText(f"Scan started for device: {device_id}")

    def on_scan_finished(self, scan_id, result):
        """Handle scan finished signal"""
        # Get device info
        device = None
        for d in self.usb_detector.get_connected_devices():
            if hasattr(result, 'device_id') and d.id == result.device_id:
                device = d
                break

        if result.status == "completed":
            if result.malicious_files:
                self.status_label.setText(f"Scan completed with {len(result.malicious_files)} malicious files found")

                # Create alert for malicious files
                alert = {
                    "severity": "critical",
                    "title": "Malicious Files Detected",
                    "message": f"{len(result.malicious_files)} malicious files found on device {device.name if device else 'Unknown'}",
                    "timestamp": result.timestamp,
                    "device_id": device.id if device else "unknown",
                    "scan_id": scan_id,
                    "resolved": False,
                    "files": result.malicious_files
                }

                # Add alert to alerts widget
                if hasattr(self, 'alerts_widget'):
                    self.alerts_widget.add_alert(alert)

                # Send notification with malicious status
                if device:
                    self.notification_manager.send_scan_completed_notification(device, result)

                    # Send security alert
                    self.notification_manager.send_security_alert_notification(
                        "malicious_files_detected",
                        device,
                        f"{len(result.malicious_files)} malicious files found on device {device.name}"
                    )

                    # Block device if configured
                    if self.config.get("block_on_threat", True):
                        # Only try to block if we have a valid device object
                        if device and hasattr(device, 'id'):
                            self.permission_manager.set_permission(device, "blocked")

            elif result.suspicious_files:
                self.status_label.setText(f"Scan completed with {len(result.suspicious_files)} suspicious files found")

                # Create alert for suspicious files
                alert = {
                    "severity": "warning",
                    "title": "Suspicious Files Detected",
                    "message": f"{len(result.suspicious_files)} suspicious files found on device {device.name if device else 'Unknown'}",
                    "timestamp": result.timestamp,
                    "device_id": device.id if device else "unknown",
                    "scan_id": scan_id,
                    "resolved": False,
                    "files": result.suspicious_files
                }

                # Add alert to alerts widget
                if hasattr(self, 'alerts_widget'):
                    self.alerts_widget.add_alert(alert)

                # Send notification with suspicious status
                if device:
                    self.notification_manager.send_scan_completed_notification(device, result)

                    # Send security alert
                    self.notification_manager.send_security_alert_notification(
                        "suspicious_files_detected",
                        device,
                        f"{len(result.suspicious_files)} suspicious files found on device {device.name}"
                    )
            else:
                self.status_label.setText("Scan completed, no threats found")

                # Create alert for clean scan
                alert = {
                    "severity": "info",
                    "title": "Scan Completed",
                    "message": f"No threats found on device {device.name if device else 'Unknown'}",
                    "timestamp": result.timestamp,
                    "device_id": device.id if device else "unknown",
                    "scan_id": scan_id,
                    "resolved": False
                }

                # Add alert to alerts widget
                if hasattr(self, 'alerts_widget'):
                    self.alerts_widget.add_alert(alert)

                # Send notification with clean status
                if device:
                    self.notification_manager.send_scan_completed_notification(device, result)
        else:
            self.status_label.setText(f"Scan {result.status}")

    def on_permission_changed(self, device_id, permission):
        """Handle permission changed signal"""
        self.status_label.setText(f"Permission for device {device_id} set to {permission}")

        # Get device info
        device = None
        for d in self.usb_detector.get_connected_devices():
            if d.id == device_id:
                device = d
                break

        # Send notification if we have device info
        if device:
            # Determine security status based on permission
            security_status = "secured"
            if permission == "blocked":
                security_status = "malicious"

            # Send notification
            self.notification_manager.send_device_connected_notification(device, security_status)

            # Send security alert if device is blocked
            if permission == "blocked":
                self.notification_manager.send_security_alert_notification(
                    "device_blocked",
                    device,
                    f"Device {device.name} has been blocked"
                )

        self.check_devices()

    def on_permission_error(self, device_id, error_message):
        """Handle permission error signal"""
        self.status_label.setText(f"Error setting permission for device {device_id}: {error_message}")

        # Get device info
        device = None
        for d in self.usb_detector.get_connected_devices():
            if d.id == device_id:
                device = d
                break

        # Send security alert if we have device info
        if device:
            self.notification_manager.send_security_alert_notification(
                "permission_error",
                device,
                f"Error setting permission: {error_message}"
            )

        QMessageBox.warning(self, "Permission Error", f"Error setting permission for device {device_id}:\n{error_message}")

    def show_login_dialog(self):
        """Show login dialog"""
        # Create login dialog
        dialog = LoginDialog(self.auth_manager, self)

        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            # User logged in successfully
            self.update_user_interface()
        else:
            # User cancelled login
            if not self.auth_manager.get_current_user():
                # No user logged in, exit application
                self.close()

    def logout(self):
        """Log out current user"""
        # Confirm logout
        reply = QMessageBox.question(
            self, "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Log out
            success, message = self.auth_manager.logout()

            if success:
                # Update UI
                self.update_user_interface()

                # Show login dialog
                self.show_login_dialog()
            else:
                QMessageBox.warning(self, "Error", message)

    def show_user_management(self):
        """Show user management dialog"""
        # Check if current user has permission
        if not self.auth_manager.has_permission("manage_users"):
            QMessageBox.warning(self, "Permission Denied", "You do not have permission to manage users.")
            return

        # Create user management dialog
        dialog = UserManagementDialog(self.auth_manager, self)

        # Show dialog
        dialog.exec_()

    def update_user_interface(self):
        """Update user interface based on current user"""
        # Get current user
        user = self.auth_manager.get_current_user()

        if user:
            # User is logged in
            self.user_label.setText(f"Logged in as: {user.username} ({user.role})")

            # Enable/disable actions based on permissions
            self.login_action.setEnabled(False)
            self.logout_action.setEnabled(True)
            self.manage_users_action.setEnabled(user.has_permission("manage_users"))

            # Enable/disable tabs based on permissions
            self.tab_widget.setTabEnabled(3, user.has_permission("view_history"))  # Alerts tab
            self.tab_widget.setTabEnabled(4, user.has_permission("change_settings"))  # Settings tab

            # Update status
            self.status_label.setText(f"Logged in as {user.username}")
        else:
            # No user logged in
            self.user_label.setText("Not logged in")

            # Disable actions
            self.login_action.setEnabled(True)
            self.logout_action.setEnabled(False)
            self.manage_users_action.setEnabled(False)

            # Disable tabs
            self.tab_widget.setTabEnabled(3, False)  # Alerts tab
            self.tab_widget.setTabEnabled(4, False)  # Settings tab

            # Update status
            self.status_label.setText("Not logged in")

    def on_user_logged_in(self, username):
        """Handle user logged in signal"""
        self.update_user_interface()

    def on_user_logged_out(self, username):
        """Handle user logged out signal"""
        self.update_user_interface()

    def resizeEvent(self, event):
        """Handle window resize event"""
        super().resizeEvent(event)

        # Resize background frame and animated background to match window size
        if hasattr(self, 'background_frame'):
            self.background_frame.setGeometry(self.rect())

        if hasattr(self, 'animated_background'):
            self.animated_background.setGeometry(self.background_frame.rect())

    def on_central_widget_resize(self, event):
        """Handle central widget resize event"""
        # Call original resize event if it exists
        original_resize = getattr(QWidget, 'resizeEvent')
        if original_resize:
            original_resize(self.central_widget, event)

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop device detection timer
        self.detection_timer.stop()

        # Stop USB monitoring
        self.usb_detector.stop_monitoring()

        # Accept the event
        event.accept()
