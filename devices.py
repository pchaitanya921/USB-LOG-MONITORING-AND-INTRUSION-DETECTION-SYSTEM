#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Devices Widget
Shows detailed list of USB devices and allows management
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QCheckBox, QMessageBox, QMenu
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

class DevicesWidget(QWidget):
    """Devices widget showing detailed list of USB devices"""
    def __init__(self, usb_detector, scanner, permission_manager, parent=None):
        super().__init__(parent)

        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        # Store backend components
        self.usb_detector = usb_detector
        self.scanner = scanner
        self.permission_manager = permission_manager

        # Create layout
        layout = QVBoxLayout(self)

        # Add title
        title_label = QLabel("USB Devices")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # Add controls
        controls_layout = QHBoxLayout()

        # Refresh button
        refresh_button = QPushButton("Refresh Devices")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        refresh_button.setIconSize(QSize(24, 24))  # Larger icon size
        refresh_button.clicked.connect(self.refresh_devices)
        refresh_button.setStyleSheet("QPushButton { padding: 6px 12px; }")
        controls_layout.addWidget(refresh_button)

        # Scan all button
        scan_all_button = QPushButton("Scan All Devices")
        scan_all_button.setIcon(QIcon("assets/icons/scan_all.png"))
        scan_all_button.setIconSize(QSize(24, 24))  # Larger icon size
        scan_all_button.clicked.connect(self.scan_all_devices)
        scan_all_button.setStyleSheet("QPushButton { padding: 6px 12px; }")
        controls_layout.addWidget(scan_all_button)

        # Block all button
        block_all_button = QPushButton("Block All Devices")
        block_all_button.setIcon(QIcon("assets/icons/block.png"))
        block_all_button.clicked.connect(self.block_all_devices)
        controls_layout.addWidget(block_all_button)

        # Add spacer
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Add devices table
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(7)
        self.devices_table.setHorizontalHeaderLabels([
            "Name", "Drive", "Size", "Free Space", "Connected", "Status", "Actions"
        ])
        self.devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.devices_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.devices_table.verticalHeader().setVisible(False)
        self.devices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.devices_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.devices_table.setAlternatingRowColors(True)
        self.devices_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.devices_table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.devices_table)

        # Add device history section
        history_label = QLabel("Device History")
        history_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(history_label)

        # Add history table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "Device Name", "Event", "Timestamp", "Details"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)

        layout.addWidget(self.history_table)

        # Set layout stretch factors
        layout.setStretch(2, 2)  # Devices table
        layout.setStretch(4, 1)  # History table

        # Initialize device history
        self.device_history = []

        # Connect signals
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.permission_manager.permission_changed.connect(self.on_permission_changed)

    def update_devices(self, devices):
        """Update the devices table"""
        # Clear table
        self.devices_table.setRowCount(0)

        # Add devices to table
        for i, device in enumerate(devices):
            self.devices_table.insertRow(i)

            # Device name
            name_item = QTableWidgetItem(device.name)
            self.devices_table.setItem(i, 0, name_item)

            # Drive letter
            drive_item = QTableWidgetItem(device.drive_letter if device.drive_letter else "N/A")
            self.devices_table.setItem(i, 1, drive_item)

            # Size
            size_item = QTableWidgetItem(device.size if device.size else "N/A")
            self.devices_table.setItem(i, 2, size_item)

            # Free space
            free_item = QTableWidgetItem(device.free_space if device.free_space else "N/A")
            self.devices_table.setItem(i, 3, free_item)

            # Connection time
            time_item = QTableWidgetItem(device.connection_time)
            self.devices_table.setItem(i, 4, time_item)

            # Status
            status_item = QTableWidgetItem(self._get_permission_text(device.permission))
            status_item.setForeground(QColor(self._get_permission_color(device.permission)))
            self.devices_table.setItem(i, 5, status_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)

            # Scan button
            scan_button = QPushButton("Scan")
            scan_button.setIcon(QIcon("assets/icons/scan.png"))
            scan_button.setIconSize(QSize(20, 20))  # Slightly smaller for the table
            scan_button.setProperty("device_id", device.id)
            scan_button.clicked.connect(lambda checked, d=device: self.scan_device(d))
            scan_button.setStyleSheet("QPushButton { padding: 4px 8px; }")
            actions_layout.addWidget(scan_button)

            # Permission combo box
            permission_combo = QComboBox()
            permission_combo.addItems(["Read Only", "Full Access", "Blocked"])

            # Set current permission
            if device.permission == "read_only":
                permission_combo.setCurrentIndex(0)
            elif device.permission == "full_access":
                permission_combo.setCurrentIndex(1)
            elif device.permission == "blocked":
                permission_combo.setCurrentIndex(2)

            permission_combo.setProperty("device_id", device.id)
            permission_combo.currentIndexChanged.connect(
                lambda index, d=device: self.change_permission(d, index)
            )
            actions_layout.addWidget(permission_combo)

            self.devices_table.setCellWidget(i, 6, actions_widget)

        # Update history when devices change
        self._update_device_history(devices)

    def refresh_devices(self):
        """Refresh the devices list"""
        devices = self.usb_detector.get_connected_devices()
        self.update_devices(devices)

    def scan_device(self, device):
        """Scan a USB device"""
        # Add to history
        self._add_history_event(device.name, "scan", "Scan initiated")

        # Start scan
        scan_id = self.scanner.scan_device(device)

    def scan_all_devices(self):
        """Scan all connected devices"""
        devices = self.usb_detector.get_connected_devices()

        if not devices:
            QMessageBox.information(self, "No Devices", "No USB devices connected to scan.")
            return

        # Scan each device
        for device in devices:
            self.scan_device(device)

    def block_all_devices(self):
        """Block all connected devices"""
        devices = self.usb_detector.get_connected_devices()

        if not devices:
            QMessageBox.information(self, "No Devices", "No USB devices connected to block.")
            return

        # Confirm with user
        reply = QMessageBox.question(
            self, "Block All Devices",
            f"Are you sure you want to block all {len(devices)} connected devices?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Block each device
            for device in devices:
                self.permission_manager.set_permission(device, "blocked")

    def change_permission(self, device, index):
        """Change permission for a device"""
        # Map index to permission
        permissions = ["read_only", "full_access", "blocked"]
        permission = permissions[index]

        # Set permission
        self.permission_manager.set_permission(device, permission)

    def show_context_menu(self, position):
        """Show context menu for devices table"""
        # Get selected row
        row = self.devices_table.rowAt(position.y())
        if row < 0:
            return

        # Create menu
        menu = QMenu(self)

        # Add actions
        scan_action = menu.addAction("Scan Device")
        block_action = menu.addAction("Block Device")
        unblock_action = menu.addAction("Unblock Device")

        # Show menu and get selected action
        action = menu.exec_(self.devices_table.mapToGlobal(position))

        # Handle action
        if action == scan_action:
            # Get device
            device_name = self.devices_table.item(row, 0).text()
            devices = self.usb_detector.get_connected_devices()
            device = next((d for d in devices if d.name == device_name), None)

            if device:
                self.scan_device(device)

        elif action == block_action:
            # Get device
            device_name = self.devices_table.item(row, 0).text()
            devices = self.usb_detector.get_connected_devices()
            device = next((d for d in devices if d.name == device_name), None)

            if device:
                self.permission_manager.set_permission(device, "blocked")

        elif action == unblock_action:
            # Get device
            device_name = self.devices_table.item(row, 0).text()
            devices = self.usb_detector.get_connected_devices()
            device = next((d for d in devices if d.name == device_name), None)

            if device:
                self.permission_manager.set_permission(device, "read_only")

    def on_scan_finished(self, scan_id, result):
        """Handle scan finished signal"""
        # Update devices
        self.refresh_devices()

        # Add to history
        if result.malicious_files:
            self._add_history_event(
                "Unknown Device", "scan_result",
                f"Found {len(result.malicious_files)} malicious files"
            )
        elif result.suspicious_files:
            self._add_history_event(
                "Unknown Device", "scan_result",
                f"Found {len(result.suspicious_files)} suspicious files"
            )
        else:
            self._add_history_event(
                "Unknown Device", "scan_result",
                "No threats found"
            )

    def on_permission_changed(self, device_id, permission):
        """Handle permission changed signal"""
        # Update devices
        self.refresh_devices()

        # Add to history
        self._add_history_event(
            device_id, "permission_change",
            f"Permission set to {permission}"
        )

    def _add_history_event(self, device_name, event_type, details):
        """Add an event to the device history"""
        import datetime

        # Create event
        event = {
            "device_name": device_name,
            "event_type": event_type,
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            "details": details
        }

        # Add to history
        self.device_history.insert(0, event)

        # Limit history size
        if len(self.device_history) > 50:
            self.device_history = self.device_history[:50]

        # Update history table
        self._update_history_table()

    def _update_device_history(self, devices):
        """Update device history based on connected devices"""
        # Check for new connections
        current_device_names = set(d.name for d in devices)
        previous_device_names = set()

        # Get previous device names from history
        for event in self.device_history:
            if event["event_type"] == "connected":
                previous_device_names.add(event["device_name"])

        # Add new connections to history
        for device in devices:
            if device.name not in previous_device_names:
                self._add_history_event(
                    device.name, "connected",
                    f"Connected to {device.drive_letter if device.drive_letter else 'system'}"
                )

    def _update_history_table(self):
        """Update the history table with current history"""
        # Clear table
        self.history_table.setRowCount(0)

        # Add events to table
        for i, event in enumerate(self.device_history):
            self.history_table.insertRow(i)

            # Device name
            name_item = QTableWidgetItem(event["device_name"])
            self.history_table.setItem(i, 0, name_item)

            # Event type
            event_item = QTableWidgetItem(self._get_event_text(event["event_type"]))
            event_item.setForeground(QColor(self._get_event_color(event["event_type"])))
            self.history_table.setItem(i, 1, event_item)

            # Timestamp
            time_item = QTableWidgetItem(event["timestamp"])
            self.history_table.setItem(i, 2, time_item)

            # Details
            details_item = QTableWidgetItem(event["details"])
            self.history_table.setItem(i, 3, details_item)

    def _get_permission_text(self, permission):
        """Get text representation of permission"""
        if permission == "blocked":
            return "Blocked"
        elif permission == "read_only":
            return "Read Only"
        elif permission == "full_access":
            return "Full Access"
        else:
            return permission.capitalize()

    def _get_permission_color(self, permission):
        """Get color for permission status"""
        if permission == "blocked":
            return "#e74c3c"  # Red
        elif permission == "read_only":
            return "#f39c12"  # Orange
        elif permission == "full_access":
            return "#2ecc71"  # Green
        else:
            return "#bdc3c7"  # Light gray

    def _get_event_text(self, event_type):
        """Get text representation of event type"""
        if event_type == "connected":
            return "Connected"
        elif event_type == "disconnected":
            return "Disconnected"
        elif event_type == "scan":
            return "Scan"
        elif event_type == "scan_result":
            return "Scan Result"
        elif event_type == "permission_change":
            return "Permission Change"
        else:
            return event_type.capitalize()

    def _get_event_color(self, event_type):
        """Get color for event type"""
        if event_type == "connected":
            return "#2ecc71"  # Green
        elif event_type == "disconnected":
            return "#e74c3c"  # Red
        elif event_type == "scan":
            return "#3498db"  # Blue
        elif event_type == "scan_result":
            return "#9b59b6"  # Purple
        elif event_type == "permission_change":
            return "#f39c12"  # Orange
        else:
            return "#bdc3c7"  # Light gray
