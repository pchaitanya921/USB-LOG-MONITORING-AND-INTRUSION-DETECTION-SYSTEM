#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Network Devices Widget
Widget for displaying and managing network devices
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QComboBox, QCheckBox, QProgressBar, QMenu,
    QAction, QTabWidget, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor, QBrush, QFont

class NetworkDevicesWidget(QWidget):
    """Widget for displaying and managing network devices"""
    def __init__(self, network_detector, scanner, parent=None):
        super().__init__(parent)
        
        # Store references
        self.network_detector = network_detector
        self.scanner = scanner
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add title
        title_label = QLabel("Network Devices")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Create left panel (device list)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add controls
        controls_layout = QHBoxLayout()
        
        # Scan network button
        self.scan_button = QPushButton("Scan Network")
        self.scan_button.setIcon(QIcon("assets/icons/scan_network.png"))
        self.scan_button.clicked.connect(self.scan_network)
        controls_layout.addWidget(self.scan_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        self.refresh_button.clicked.connect(self.refresh_devices)
        controls_layout.addWidget(self.refresh_button)
        
        # Add spacer
        controls_layout.addStretch()
        
        left_layout.addLayout(controls_layout)
        
        # Add device table
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels([
            "Device", "IP Address", "MAC Address", "Type", "Status", "Actions"
        ])
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.device_table.verticalHeader().setVisible(False)
        self.device_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.device_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.device_table.setAlternatingRowColors(True)
        self.device_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.device_table.customContextMenuRequested.connect(self.show_context_menu)
        self.device_table.itemSelectionChanged.connect(self.on_device_selected)
        
        left_layout.addWidget(self.device_table)
        
        # Add scan progress
        self.scan_progress_group = QGroupBox("Scan Progress")
        self.scan_progress_group.setVisible(False)
        scan_progress_layout = QVBoxLayout(self.scan_progress_group)
        
        self.scan_status_label = QLabel("Scanning network...")
        scan_progress_layout.addWidget(self.scan_status_label)
        
        self.scan_progress_bar = QProgressBar()
        scan_progress_layout.addWidget(self.scan_progress_bar)
        
        left_layout.addWidget(self.scan_progress_group)
        
        # Create right panel (device details)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add device details
        self.details_group = QGroupBox("Device Details")
        details_layout = QVBoxLayout(self.details_group)
        
        # Add device info
        self.device_info_tree = QTreeWidget()
        self.device_info_tree.setHeaderLabels(["Property", "Value"])
        self.device_info_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        details_layout.addWidget(self.device_info_tree)
        
        right_layout.addWidget(self.details_group)
        
        # Add device actions
        actions_group = QGroupBox("Device Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # Scan device button
        self.scan_device_button = QPushButton("Scan Device")
        self.scan_device_button.setIcon(QIcon("assets/icons/scan.png"))
        self.scan_device_button.clicked.connect(self.scan_selected_device)
        self.scan_device_button.setEnabled(False)
        actions_layout.addWidget(self.scan_device_button)
        
        # Trust device button
        self.trust_device_button = QPushButton("Trust Device")
        self.trust_device_button.setIcon(QIcon("assets/icons/trust.png"))
        self.trust_device_button.clicked.connect(self.toggle_trust_selected_device)
        self.trust_device_button.setEnabled(False)
        actions_layout.addWidget(self.trust_device_button)
        
        # Block device button
        self.block_device_button = QPushButton("Block Device")
        self.block_device_button.setIcon(QIcon("assets/icons/block.png"))
        self.block_device_button.clicked.connect(self.block_selected_device)
        self.block_device_button.setEnabled(False)
        actions_layout.addWidget(self.block_device_button)
        
        right_layout.addWidget(actions_group)
        
        # Add device history
        history_group = QGroupBox("Device History")
        history_layout = QVBoxLayout(history_group)
        
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Event", "Time"])
        self.history_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        history_layout.addWidget(self.history_tree)
        
        right_layout.addWidget(history_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])
        
        layout.addWidget(splitter)
        
        # Connect signals
        self.network_detector.device_connected.connect(self.on_device_connected)
        self.network_detector.device_disconnected.connect(self.on_device_disconnected)
        self.network_detector.device_updated.connect(self.on_device_updated)
        self.network_detector.scan_started.connect(self.on_scan_started)
        self.network_detector.scan_progress.connect(self.on_scan_progress)
        self.network_detector.scan_finished.connect(self.on_scan_finished)
        
        # Initial device refresh
        self.refresh_devices()
        
        # Start network monitoring
        self.network_detector.start_monitoring()
    
    def refresh_devices(self):
        """Refresh device list"""
        # Clear table
        self.device_table.setRowCount(0)
        
        # Get devices
        devices = self.network_detector.get_connected_devices()
        
        # Add devices to table
        for i, (device_id, device) in enumerate(devices.items()):
            self.device_table.insertRow(i)
            
            # Device name/hostname
            name_item = QTableWidgetItem(device.hostname or "Unknown")
            if device.is_trusted:
                name_item.setIcon(QIcon("assets/icons/trusted.png"))
            self.device_table.setItem(i, 0, name_item)
            
            # IP address
            ip_item = QTableWidgetItem(device.ip_address)
            self.device_table.setItem(i, 1, ip_item)
            
            # MAC address
            mac_item = QTableWidgetItem(device.mac_address or "Unknown")
            self.device_table.setItem(i, 2, mac_item)
            
            # Device type
            type_item = QTableWidgetItem(device.device_type.capitalize())
            type_item.setIcon(QIcon(device.get_device_icon()))
            self.device_table.setItem(i, 3, type_item)
            
            # Status
            status_item = QTableWidgetItem(device.status.capitalize())
            if device.status == "active":
                status_item.setForeground(QBrush(QColor("#2ecc71")))
            elif device.status == "disconnected":
                status_item.setForeground(QBrush(QColor("#e74c3c")))
            self.device_table.setItem(i, 4, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            # Scan button
            scan_button = QPushButton()
            scan_button.setIcon(QIcon("assets/icons/scan.png"))
            scan_button.setToolTip("Scan Device")
            scan_button.setProperty("device_id", device_id)
            scan_button.clicked.connect(lambda checked, d=device_id: self.scan_device(d))
            actions_layout.addWidget(scan_button)
            
            # Trust/Untrust button
            trust_button = QPushButton()
            if device.is_trusted:
                trust_button.setIcon(QIcon("assets/icons/untrust.png"))
                trust_button.setToolTip("Untrust Device")
            else:
                trust_button.setIcon(QIcon("assets/icons/trust.png"))
                trust_button.setToolTip("Trust Device")
            trust_button.setProperty("device_id", device_id)
            trust_button.clicked.connect(lambda checked, d=device_id: self.toggle_trust_device(d))
            actions_layout.addWidget(trust_button)
            
            # Block button
            block_button = QPushButton()
            block_button.setIcon(QIcon("assets/icons/block.png"))
            block_button.setToolTip("Block Device")
            block_button.setProperty("device_id", device_id)
            block_button.clicked.connect(lambda checked, d=device_id: self.block_device(d))
            actions_layout.addWidget(block_button)
            
            self.device_table.setCellWidget(i, 5, actions_widget)
    
    def scan_network(self):
        """Scan network for devices"""
        success, message = self.network_detector.scan_network()
        
        if not success:
            QMessageBox.warning(self, "Scan Error", message)
    
    def scan_device(self, device_id):
        """Scan a specific device"""
        success, message = self.network_detector.scan_device(device_id)
        
        if not success:
            QMessageBox.warning(self, "Scan Error", message)
    
    def toggle_trust_device(self, device_id):
        """Toggle trust status for a device"""
        device = self.network_detector.get_device(device_id)
        if device:
            self.network_detector.set_device_trusted(device_id, not device.is_trusted)
            self.refresh_devices()
    
    def block_device(self, device_id):
        """Block a device"""
        # In a real implementation, this would add firewall rules to block the device
        QMessageBox.information(self, "Block Device", f"Device {device_id} has been blocked.")
    
    def on_device_connected(self, device_id):
        """Handle device connected signal"""
        self.refresh_devices()
    
    def on_device_disconnected(self, device_id):
        """Handle device disconnected signal"""
        self.refresh_devices()
    
    def on_device_updated(self, device_id):
        """Handle device updated signal"""
        self.refresh_devices()
        
        # Update device details if this is the selected device
        selected_items = self.device_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            table_device_id = self.get_device_id_from_row(row)
            
            if table_device_id == device_id:
                self.update_device_details(device_id)
    
    def on_scan_started(self, scan_id):
        """Handle scan started signal"""
        self.scan_progress_group.setVisible(True)
        self.scan_status_label.setText("Scanning network...")
        self.scan_progress_bar.setValue(0)
        self.scan_button.setEnabled(False)
    
    def on_scan_progress(self, scan_id, scanned, total):
        """Handle scan progress signal"""
        self.scan_progress_bar.setMaximum(total)
        self.scan_progress_bar.setValue(scanned)
        self.scan_status_label.setText(f"Scanning network... ({scanned}/{total})")
    
    def on_scan_finished(self, scan_id, result):
        """Handle scan finished signal"""
        self.scan_progress_group.setVisible(False)
        self.scan_button.setEnabled(True)
        
        if result and result.get("status") == "completed":
            QMessageBox.information(self, "Scan Completed", f"Network scan completed. Found {result.get('devices_found', 0)} devices.")
            self.refresh_devices()
        else:
            QMessageBox.warning(self, "Scan Error", f"Network scan failed: {result.get('error', 'Unknown error')}")
    
    def get_device_id_from_row(self, row):
        """Get device ID from table row"""
        # Get actions widget
        actions_widget = self.device_table.cellWidget(row, 5)
        if actions_widget:
            # Get first button (scan button)
            scan_button = actions_widget.layout().itemAt(0).widget()
            if scan_button:
                return scan_button.property("device_id")
        
        return None
    
    def on_device_selected(self):
        """Handle device selection changed"""
        selected_items = self.device_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            device_id = self.get_device_id_from_row(row)
            
            if device_id:
                self.update_device_details(device_id)
                
                # Enable device action buttons
                self.scan_device_button.setEnabled(True)
                self.trust_device_button.setEnabled(True)
                self.block_device_button.setEnabled(True)
                
                # Update trust button text
                device = self.network_detector.get_device(device_id)
                if device and device.is_trusted:
                    self.trust_device_button.setText("Untrust Device")
                    self.trust_device_button.setIcon(QIcon("assets/icons/untrust.png"))
                else:
                    self.trust_device_button.setText("Trust Device")
                    self.trust_device_button.setIcon(QIcon("assets/icons/trust.png"))
            else:
                self.clear_device_details()
                
                # Disable device action buttons
                self.scan_device_button.setEnabled(False)
                self.trust_device_button.setEnabled(False)
                self.block_device_button.setEnabled(False)
        else:
            self.clear_device_details()
            
            # Disable device action buttons
            self.scan_device_button.setEnabled(False)
            self.trust_device_button.setEnabled(False)
            self.block_device_button.setEnabled(False)
    
    def update_device_details(self, device_id):
        """Update device details panel"""
        device = self.network_detector.get_device(device_id)
        if not device:
            self.clear_device_details()
            return
        
        # Update device info tree
        self.device_info_tree.clear()
        
        # Basic info
        basic_info = QTreeWidgetItem(self.device_info_tree, ["Basic Information", ""])
        basic_info.setExpanded(True)
        
        QTreeWidgetItem(basic_info, ["Hostname", device.hostname or "Unknown"])
        QTreeWidgetItem(basic_info, ["IP Address", device.ip_address])
        QTreeWidgetItem(basic_info, ["MAC Address", device.mac_address or "Unknown"])
        QTreeWidgetItem(basic_info, ["Device Type", device.device_type.capitalize()])
        QTreeWidgetItem(basic_info, ["Vendor", device.vendor or "Unknown"])
        QTreeWidgetItem(basic_info, ["OS Type", device.os_type or "Unknown"])
        QTreeWidgetItem(basic_info, ["Status", device.status.capitalize()])
        QTreeWidgetItem(basic_info, ["Trusted", "Yes" if device.is_trusted else "No"])
        
        # Connection info
        connection_info = QTreeWidgetItem(self.device_info_tree, ["Connection Information", ""])
        connection_info.setExpanded(True)
        
        QTreeWidgetItem(connection_info, ["First Seen", device.first_seen])
        QTreeWidgetItem(connection_info, ["Last Seen", device.last_seen])
        QTreeWidgetItem(connection_info, ["Connection Count", str(device.connection_count)])
        
        # Scan info
        if device.last_scan_time:
            scan_info = QTreeWidgetItem(self.device_info_tree, ["Scan Information", ""])
            scan_info.setExpanded(True)
            
            QTreeWidgetItem(scan_info, ["Last Scan", device.last_scan_time])
            QTreeWidgetItem(scan_info, ["Scan Result", device.scan_result or "Unknown"])
            
            # Open ports
            if device.open_ports:
                ports_item = QTreeWidgetItem(scan_info, ["Open Ports", f"{len(device.open_ports)} ports"])
                for port in device.open_ports:
                    QTreeWidgetItem(ports_item, [str(port), ""])
            
            # Services
            if device.services:
                services_item = QTreeWidgetItem(scan_info, ["Services", f"{len(device.services)} services"])
                for service in device.services:
                    QTreeWidgetItem(services_item, [service, ""])
        
        # Update history tree
        self.update_device_history(device_id)
    
    def update_device_history(self, device_id):
        """Update device history tree"""
        self.history_tree.clear()
        
        device = self.network_detector.get_device(device_id)
        if not device:
            return
        
        # Add connection event
        connection_item = QTreeWidgetItem(self.history_tree, ["Connected", device.connection_time])
        connection_item.setIcon(0, QIcon("assets/icons/connect.png"))
        
        # Add scan event if available
        if device.last_scan_time:
            scan_item = QTreeWidgetItem(self.history_tree, ["Scanned", device.last_scan_time])
            scan_item.setIcon(0, QIcon("assets/icons/scan.png"))
    
    def clear_device_details(self):
        """Clear device details panel"""
        self.device_info_tree.clear()
        self.history_tree.clear()
    
    def scan_selected_device(self):
        """Scan the selected device"""
        selected_items = self.device_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            device_id = self.get_device_id_from_row(row)
            
            if device_id:
                self.scan_device(device_id)
    
    def toggle_trust_selected_device(self):
        """Toggle trust status for the selected device"""
        selected_items = self.device_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            device_id = self.get_device_id_from_row(row)
            
            if device_id:
                self.toggle_trust_device(device_id)
    
    def block_selected_device(self):
        """Block the selected device"""
        selected_items = self.device_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            device_id = self.get_device_id_from_row(row)
            
            if device_id:
                self.block_device(device_id)
    
    def show_context_menu(self, position):
        """Show context menu for device table"""
        selected_items = self.device_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        device_id = self.get_device_id_from_row(row)
        
        if not device_id:
            return
        
        device = self.network_detector.get_device(device_id)
        if not device:
            return
        
        # Create menu
        menu = QMenu(self)
        
        # Add actions
        scan_action = QAction("Scan Device", self)
        scan_action.triggered.connect(lambda: self.scan_device(device_id))
        menu.addAction(scan_action)
        
        if device.is_trusted:
            trust_action = QAction("Untrust Device", self)
            trust_action.triggered.connect(lambda: self.toggle_trust_device(device_id))
        else:
            trust_action = QAction("Trust Device", self)
            trust_action.triggered.connect(lambda: self.toggle_trust_device(device_id))
        menu.addAction(trust_action)
        
        block_action = QAction("Block Device", self)
        block_action.triggered.connect(lambda: self.block_device(device_id))
        menu.addAction(block_action)
        
        # Show menu
        menu.exec_(self.device_table.mapToGlobal(position))
