#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dashboard Widget
Shows overview of USB devices and system status
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from src.ui.terminal_widgets import (
    TerminalCard, TerminalBlock, TerminalStatusBlock,
    TerminalButton, TerminalLabel, TerminalHeader
)
from src.ui.usb_animation import USBAnimation

class StatCard(TerminalStatusBlock):
    """Card widget for displaying statistics in terminal style"""
    def __init__(self, title, value, icon_path=None, parent=None):
        super().__init__(title, value, parent=parent)

        # Set minimum size
        self.setMinimumSize(QSize(200, 120))

class DeviceCard(TerminalCard):
    """Card widget for displaying a USB device in terminal style"""
    def __init__(self, device, parent=None):
        # Initialize with empty title since we'll show the name beside the animation
        super().__init__("", parent)

        # Store device
        self.device = device

        # Create main content layout
        main_layout = QVBoxLayout()

        # Create animation and name layout (horizontal)
        animation_name_layout = QHBoxLayout()

        # Add USB animation
        self.usb_animation = USBAnimation(self)
        self.usb_animation.set_connected(True)  # Device is connected
        self.usb_animation.setFixedSize(60, 40)
        animation_name_layout.addWidget(self.usb_animation)

        # Add device name label beside the animation
        name_label = TerminalLabel(f"[USB] {device.name}")
        name_label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 14px;")
        animation_name_layout.addWidget(name_label)

        # Add stretch to push animation and name to the left
        animation_name_layout.addStretch()

        # Add animation and name layout to main layout
        main_layout.addLayout(animation_name_layout)

        # Create details layout
        details_layout = QVBoxLayout()

        # Add drive letter if available
        if device.drive_letter:
            drive_label = TerminalLabel(f"Drive: {device.drive_letter}")
            details_layout.addWidget(drive_label)

        # Add size if available
        if device.size:
            size_label = TerminalLabel(f"Size: {device.size}")
            details_layout.addWidget(size_label)

        # Add connection time
        time_label = TerminalLabel(f"Connected: {device.connection_time}")
        details_layout.addWidget(time_label)

        # Add permission status
        self.status_label = TerminalLabel(self._get_permission_text(device.permission))
        if device.permission == "blocked":
            self.status_label.setStyleSheet("color: #ff0000;")
            # Set animation to disconnected for blocked devices
            self.usb_animation.set_connected(False)
        elif device.permission == "read_only":
            self.status_label.setStyleSheet("color: #ffaa00;")
        elif device.permission == "full_access":
            self.status_label.setStyleSheet("color: #00ff00;")

        details_layout.addWidget(self.status_label)

        # Add details layout to main layout
        main_layout.addLayout(details_layout)

        # Add main layout to card
        self.add_layout(main_layout)

        # Add buttons
        buttons_layout = QHBoxLayout()

        # Scan button
        self.scan_button = TerminalButton("[ SCAN ]")
        self.scan_button.clicked.connect(self._on_scan_clicked)
        buttons_layout.addWidget(self.scan_button)

        # Block/Unblock button
        button_text = "[ BLOCK ]" if device.permission != "blocked" else "[ UNBLOCK ]"
        self.block_button = TerminalButton(button_text)
        self.block_button.clicked.connect(self._on_block_clicked)
        buttons_layout.addWidget(self.block_button)

        self.add_layout(buttons_layout)

        # Set minimum size
        self.setMinimumSize(QSize(250, 180))

    def update_device(self, device):
        """Update the device information"""
        self.device = device

        # Update status label
        self.status_label.setText(self._get_permission_text(device.permission))

        # Update status label color and animation state
        if device.permission == "blocked":
            self.status_label.setStyleSheet("color: #ff0000;")
            # Set animation to disconnected for blocked devices
            self.usb_animation.set_connected(False)
        elif device.permission == "read_only":
            self.status_label.setStyleSheet("color: #ffaa00;")
            self.usb_animation.set_connected(True)
        elif device.permission == "full_access":
            self.status_label.setStyleSheet("color: #00ff00;")
            self.usb_animation.set_connected(True)

        # Update block button
        self.block_button.setText("[ BLOCK ]" if device.permission != "blocked" else "[ UNBLOCK ]")

    def _get_permission_text(self, permission):
        """Get text representation of permission"""
        if permission == "blocked":
            return "Status: [BLOCKED]"
        elif permission == "read_only":
            return "Status: [READ ONLY]"
        elif permission == "full_access":
            return "Status: [FULL ACCESS]"
        else:
            return f"Status: [{permission.upper()}]"

    def _on_scan_clicked(self):
        """Handle scan button click"""
        # Find the DashboardWidget by traversing up the parent hierarchy
        parent = self.parent()
        while parent and not isinstance(parent, DashboardWidget):
            parent = parent.parent()

        if parent and isinstance(parent, DashboardWidget):
            parent.scan_device(self.device)
        else:
            print("Error: Could not find DashboardWidget parent")

    def _on_block_clicked(self):
        """Handle block button click"""
        # Find the DashboardWidget by traversing up the parent hierarchy
        parent = self.parent()
        while parent and not isinstance(parent, DashboardWidget):
            parent = parent.parent()

        if parent and isinstance(parent, DashboardWidget):
            if self.device.permission == "blocked":
                parent.set_device_permission(self.device, "read_only")
            else:
                parent.set_device_permission(self.device, "blocked")
        else:
            print("Error: Could not find DashboardWidget parent")

class AlertCard(TerminalCard):
    """Card widget for displaying an alert in terminal style"""
    def __init__(self, alert, parent=None):
        # Determine severity for title styling
        severity = alert.get("severity", "info")
        if severity == "critical":
            title = f"[!] {alert.get('title', 'Alert')}"
        elif severity == "warning":
            title = f"[*] {alert.get('title', 'Alert')}"
        else:
            title = f"[i] {alert.get('title', 'Alert')}"

        super().__init__(title, parent)

        # Create message layout
        message_layout = QVBoxLayout()

        # Add alert message
        message_label = TerminalLabel(alert.get("message", ""))
        message_label.setWordWrap(True)

        # Set color based on severity
        if severity == "critical":
            message_label.setStyleSheet("color: #ff0000;")
        elif severity == "warning":
            message_label.setStyleSheet("color: #ffaa00;")

        message_layout.addWidget(message_label)

        # Add timestamp
        time_label = TerminalLabel(f"Time: {alert.get('timestamp', '')}")
        time_label.setAlignment(Qt.AlignRight)
        time_label.setStyleSheet("color: #00aa00; font-size: 10px;")
        message_layout.addWidget(time_label)

        self.add_layout(message_layout)

        # Set minimum size
        self.setMinimumSize(QSize(300, 100))

class DashboardWidget(QWidget):
    """Dashboard widget showing overview of USB devices and system status"""
    def __init__(self, usb_detector, scanner, permission_manager, parent=None):
        super().__init__(parent)

        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        # Store backend components
        self.usb_detector = usb_detector
        self.scanner = scanner
        self.permission_manager = permission_manager

        # Initialize counters
        self.connected_devices_count = 0
        self.total_devices_count = 0
        self.total_scans_count = 0
        self.detected_threats_count = 0

        # Create layout
        layout = QVBoxLayout(self)

        # Add title
        title_label = TerminalHeader("=== USB MONITORING SYSTEM DASHBOARD ===")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Add stats cards
        stats_layout = QHBoxLayout()

        # Connected devices card
        self.connected_devices_card = StatCard("CONNECTED DEVICES", "0")
        stats_layout.addWidget(self.connected_devices_card)

        # Total devices card
        self.total_devices_card = StatCard("TOTAL DEVICES", "0")
        stats_layout.addWidget(self.total_devices_card)

        # Total scans card
        self.total_scans_card = StatCard("TOTAL SCANS", "0")
        stats_layout.addWidget(self.total_scans_card)

        # Detected threats card
        self.detected_threats_card = StatCard("DETECTED THREATS", "0")
        stats_layout.addWidget(self.detected_threats_card)

        layout.addLayout(stats_layout)

        # Add devices section
        devices_block = TerminalBlock("CONNECTED USB DEVICES")
        devices_layout = QVBoxLayout()

        # Create devices scroll area
        self.devices_scroll = QScrollArea()
        self.devices_scroll.setWidgetResizable(True)
        self.devices_scroll.setFrameShape(QFrame.NoFrame)
        self.devices_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #0a1520;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #00aa00;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Create devices container
        self.devices_container = QWidget()
        self.devices_layout = QGridLayout(self.devices_container)
        self.devices_layout.setContentsMargins(5, 5, 5, 5)
        self.devices_layout.setSpacing(10)
        self.devices_scroll.setWidget(self.devices_container)

        devices_layout.addWidget(self.devices_scroll)
        devices_block.add_layout(devices_layout)
        layout.addWidget(devices_block)

        # Add alerts section
        alerts_block = TerminalBlock("RECENT ALERTS")
        alerts_layout = QVBoxLayout()

        # Create alerts scroll area
        self.alerts_scroll = QScrollArea()
        self.alerts_scroll.setWidgetResizable(True)
        self.alerts_scroll.setFrameShape(QFrame.NoFrame)
        self.alerts_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #0a1520;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #00aa00;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Create alerts container
        self.alerts_container = QWidget()
        self.alerts_layout = QVBoxLayout(self.alerts_container)
        self.alerts_layout.setContentsMargins(5, 5, 5, 5)
        self.alerts_layout.setSpacing(10)
        self.alerts_scroll.setWidget(self.alerts_container)

        alerts_layout.addWidget(self.alerts_scroll)
        alerts_block.add_layout(alerts_layout)
        layout.addWidget(alerts_block)

        # Set layout stretch factors
        layout.setStretch(2, 2)  # Devices section
        layout.setStretch(4, 1)  # Alerts section

        # Connect signals
        self.scanner.scan_finished.connect(self.on_scan_finished)

    def update_devices(self, devices):
        """Update the devices display"""
        # Update connected devices count
        self.connected_devices_count = len(devices)
        self.connected_devices_card.update_value(str(self.connected_devices_count))

        # Update total devices count (unique devices)
        device_ids = set()
        for device in devices:
            device_ids.add(device.id)

        # If total is less than connected, update it
        if self.total_devices_count < len(device_ids):
            self.total_devices_count = len(device_ids)
            self.total_devices_card.update_value(str(self.total_devices_count))

        # Clear devices layout
        self._clear_layout(self.devices_layout)

        # Add device cards
        if not devices:
            # Show empty state
            empty_label = TerminalLabel("[ NO USB DEVICES CONNECTED ]")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #555555; font-size: 14px; padding: 20px;")
            self.devices_layout.addWidget(empty_label, 0, 0)
        else:
            # Add device cards in a grid
            for i, device in enumerate(devices):
                row = i // 2
                col = i % 2
                device_card = DeviceCard(device, self)
                self.devices_layout.addWidget(device_card, row, col)

    def update_alerts(self, alerts):
        """Update the alerts display"""
        # Clear alerts layout
        self._clear_layout(self.alerts_layout)

        # Add alert cards
        if not alerts:
            # Show empty state
            empty_label = TerminalLabel("[ NO RECENT ALERTS ]")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #555555; font-size: 14px; padding: 20px;")
            self.alerts_layout.addWidget(empty_label)
        else:
            # Add alert cards
            for alert in alerts:
                alert_card = AlertCard(alert, self)
                self.alerts_layout.addWidget(alert_card)

    def scan_device(self, device):
        """Scan a USB device"""
        scan_id = self.scanner.scan_device(device)

        # Update total scans count
        self.total_scans_count += 1
        self.total_scans_card.update_value(str(self.total_scans_count))

    def set_device_permission(self, device, permission):
        """Set permission for a USB device"""
        self.permission_manager.set_permission(device, permission)

    def on_scan_finished(self, scan_id, result):
        """Handle scan finished signal"""
        # Update detected threats count
        threats_count = len(result.malicious_files) + len(result.suspicious_files)
        if threats_count > 0:
            self.detected_threats_count += threats_count
            self.detected_threats_card.update_value(str(self.detected_threats_count))

            # Add alert for detected threats
            alert = {
                "title": "Threats Detected",
                "message": f"Found {len(result.malicious_files)} malicious and {len(result.suspicious_files)} suspicious files",
                "timestamp": result.timestamp
            }
            self.update_alerts([alert])

    def _clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self._clear_layout(item.layout())
