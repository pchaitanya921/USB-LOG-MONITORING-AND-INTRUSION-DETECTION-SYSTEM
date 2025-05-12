#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Scans Widget
Shows scan history and results
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QSplitter, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

class ScansWidget(QWidget):
    """Scans widget showing scan history and results"""
    def __init__(self, scanner, parent=None):
        super().__init__(parent)

        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        # Store scanner
        self.scanner = scanner

        # Create layout
        layout = QVBoxLayout(self)

        # Add title
        title_label = QLabel("USB Scans")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # Add controls
        controls_layout = QHBoxLayout()

        # Export button
        export_button = QPushButton("Export Scan Results")
        export_button.setIcon(QIcon("assets/icons/export.png"))
        export_button.clicked.connect(self.export_results)
        controls_layout.addWidget(export_button)

        # Clear history button
        clear_button = QPushButton("Clear Scan History")
        clear_button.setIcon(QIcon("assets/icons/clear.png"))
        clear_button.clicked.connect(self.clear_history)
        controls_layout.addWidget(clear_button)

        # Add spacer
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Create splitter for scan history and details
        splitter = QSplitter(Qt.Vertical)

        # Add scan history table
        self.scans_table = QTableWidget()
        self.scans_table.setColumnCount(6)
        self.scans_table.setHorizontalHeaderLabels([
            "Scan ID", "Device", "Status", "Files Scanned", "Threats Found", "Timestamp"
        ])
        self.scans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scans_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.scans_table.verticalHeader().setVisible(False)
        self.scans_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.scans_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.scans_table.setAlternatingRowColors(True)
        self.scans_table.itemSelectionChanged.connect(self.on_scan_selected)

        splitter.addWidget(self.scans_table)

        # Add scan details widget
        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)

        # Add details title
        details_title = QLabel("Scan Details")
        details_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        details_layout.addWidget(details_title)

        # Add details tree
        self.details_tree = QTreeWidget()
        self.details_tree.setHeaderLabels(["File", "Status", "Details"])
        self.details_tree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.details_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        details_layout.addWidget(self.details_tree)

        splitter.addWidget(self.details_widget)

        # Set initial splitter sizes
        splitter.setSizes([300, 200])

        layout.addWidget(splitter)

        # Connect signals
        self.scanner.scan_started.connect(self.on_scan_started)
        self.scanner.scan_progress.connect(self.on_scan_progress)
        self.scanner.scan_finished.connect(self.on_scan_finished)

        # Initialize with empty data
        self.update_scans([])

    def update_scans(self, scans):
        """Update the scans table with scan history"""
        # Clear table
        self.scans_table.setRowCount(0)

        # Add scans to table
        for i, scan in enumerate(scans):
            self.scans_table.insertRow(i)

            # Scan ID
            id_item = QTableWidgetItem(scan.scan_id[:8] + "...")
            id_item.setData(Qt.UserRole, scan.scan_id)
            self.scans_table.setItem(i, 0, id_item)

            # Device
            device_item = QTableWidgetItem("Unknown Device")  # Would be set from device info
            self.scans_table.setItem(i, 1, device_item)

            # Status
            status_item = QTableWidgetItem(self._get_status_text(scan.status))
            status_item.setForeground(QColor(self._get_status_color(scan.status)))
            self.scans_table.setItem(i, 2, status_item)

            # Files scanned
            files_item = QTableWidgetItem(f"{scan.scanned_files} / {scan.total_files}")
            self.scans_table.setItem(i, 3, files_item)

            # Threats found
            threats_count = len(scan.malicious_files) + len(scan.suspicious_files)
            threats_item = QTableWidgetItem(str(threats_count))
            if threats_count > 0:
                threats_item.setForeground(QColor("#e74c3c"))  # Red
            self.scans_table.setItem(i, 4, threats_item)

            # Timestamp
            time_item = QTableWidgetItem(scan.timestamp)
            self.scans_table.setItem(i, 5, time_item)

    def on_scan_selected(self):
        """Handle scan selection in the table"""
        # Clear details tree
        self.details_tree.clear()

        # Get selected scan
        selected_items = self.scans_table.selectedItems()
        if not selected_items:
            return

        # Get scan ID
        scan_id = selected_items[0].data(Qt.UserRole)

        # Get scan result
        scan_result = self.scanner.get_scan_result(scan_id)
        if not scan_result:
            return

        # Add malicious files
        if scan_result.malicious_files:
            malicious_root = QTreeWidgetItem(self.details_tree, ["Malicious Files"])
            malicious_root.setForeground(0, QColor("#e74c3c"))  # Red
            malicious_root.setExpanded(True)

            for file_path in scan_result.malicious_files:
                file_item = QTreeWidgetItem(malicious_root, [file_path, "Malicious", ""])
                file_item.setForeground(1, QColor("#e74c3c"))  # Red

        # Add suspicious files
        if scan_result.suspicious_files:
            suspicious_root = QTreeWidgetItem(self.details_tree, ["Suspicious Files"])
            suspicious_root.setForeground(0, QColor("#f39c12"))  # Orange
            suspicious_root.setExpanded(True)

            for file_path in scan_result.suspicious_files:
                file_item = QTreeWidgetItem(suspicious_root, [file_path, "Suspicious", ""])
                file_item.setForeground(1, QColor("#f39c12"))  # Orange

        # Add scan info
        info_root = QTreeWidgetItem(self.details_tree, ["Scan Information"])
        info_root.setExpanded(True)

        QTreeWidgetItem(info_root, ["Scan ID", "", scan_result.scan_id])
        QTreeWidgetItem(info_root, ["Status", "", self._get_status_text(scan_result.status)])
        QTreeWidgetItem(info_root, ["Timestamp", "", scan_result.timestamp])
        QTreeWidgetItem(info_root, ["Duration", "", f"{scan_result.scan_duration:.2f} seconds"])
        QTreeWidgetItem(info_root, ["Files Scanned", "", f"{scan_result.scanned_files} / {scan_result.total_files}"])

        # Add scanned files section
        if hasattr(scan_result, 'scanned_file_list') and scan_result.scanned_file_list:
            scanned_files_root = QTreeWidgetItem(self.details_tree, ["Scanned Files"])
            scanned_files_root.setExpanded(False)  # Collapsed by default due to potentially large number

            # Group files by status
            clean_files = []
            malicious_files = []
            suspicious_files = []

            for file_info in scan_result.scanned_file_list:
                if file_info['status'] == 'malicious':
                    malicious_files.append(file_info)
                elif file_info['status'] == 'suspicious':
                    suspicious_files.append(file_info)
                else:
                    clean_files.append(file_info)

            # Add malicious files first
            if malicious_files:
                malicious_group = QTreeWidgetItem(scanned_files_root, ["Malicious Files", f"{len(malicious_files)} files", ""])
                malicious_group.setForeground(0, QColor("#e74c3c"))  # Red
                malicious_group.setExpanded(True)  # Expand malicious files by default

                for file_info in malicious_files:
                    file_item = QTreeWidgetItem(malicious_group, [file_info['path'], file_info['status'], file_info['timestamp']])
                    file_item.setForeground(1, QColor("#e74c3c"))  # Red

            # Add suspicious files
            if suspicious_files:
                suspicious_group = QTreeWidgetItem(scanned_files_root, ["Suspicious Files", f"{len(suspicious_files)} files", ""])
                suspicious_group.setForeground(0, QColor("#f39c12"))  # Orange
                suspicious_group.setExpanded(True)  # Expand suspicious files by default

                for file_info in suspicious_files:
                    file_item = QTreeWidgetItem(suspicious_group, [file_info['path'], file_info['status'], file_info['timestamp']])
                    file_item.setForeground(1, QColor("#f39c12"))  # Orange

            # Add clean files (collapsed by default)
            if clean_files:
                clean_group = QTreeWidgetItem(scanned_files_root, ["Clean Files", f"{len(clean_files)} files", ""])
                clean_group.setForeground(0, QColor("#2ecc71"))  # Green

                for file_info in clean_files:
                    file_item = QTreeWidgetItem(clean_group, [file_info['path'], file_info['status'], file_info['timestamp']])
                    file_item.setForeground(1, QColor("#2ecc71"))  # Green

    def export_results(self):
        """Export scan results to a file"""
        # Get selected scan
        selected_items = self.scans_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a scan to export.")
            return

        # Get scan ID
        scan_id = selected_items[0].data(Qt.UserRole)

        # Get scan result
        scan_result = self.scanner.get_scan_result(scan_id)
        if not scan_result:
            QMessageBox.warning(self, "Error", "Could not find scan result.")
            return

        # Get file path
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Scan Results", f"scan_{scan_id[:8]}.txt", "Text Files (*.txt)"
        )

        if not file_path:
            return

        # Write to file
        try:
            with open(file_path, "w") as f:
                f.write(f"USB Monitoring System - Scan Results\n")
                f.write(f"===================================\n\n")
                f.write(f"Scan ID: {scan_result.scan_id}\n")
                f.write(f"Timestamp: {scan_result.timestamp}\n")
                f.write(f"Status: {self._get_status_text(scan_result.status)}\n")
                f.write(f"Duration: {scan_result.scan_duration:.2f} seconds\n")
                f.write(f"Files Scanned: {scan_result.scanned_files} / {scan_result.total_files}\n\n")

                if scan_result.malicious_files:
                    f.write(f"Malicious Files ({len(scan_result.malicious_files)}):\n")
                    f.write(f"-----------------------------------\n")
                    for file_path in scan_result.malicious_files:
                        f.write(f"- {file_path}\n")
                        # Add detection details if available
                        if hasattr(scan_result, 'detection_details') and file_path in scan_result.detection_details:
                            details = scan_result.detection_details[file_path]
                            f.write(f"  Detection type: {details['detection_type']}\n")
                            f.write(f"  Details: {details['details']}\n")
                    f.write("\n")

                if scan_result.suspicious_files:
                    f.write(f"Suspicious Files ({len(scan_result.suspicious_files)}):\n")
                    f.write(f"-----------------------------------\n")
                    for file_path in scan_result.suspicious_files:
                        f.write(f"- {file_path}\n")
                        # Add detection details if available
                        if hasattr(scan_result, 'detection_details') and file_path in scan_result.detection_details:
                            details = scan_result.detection_details[file_path]
                            f.write(f"  Detection type: {details['detection_type']}\n")
                            f.write(f"  Details: {details['details']}\n")
                    f.write("\n")

                if not scan_result.malicious_files and not scan_result.suspicious_files:
                    f.write("No threats found.\n")

                # Add list of all scanned files
                if hasattr(scan_result, 'scanned_file_list') and scan_result.scanned_file_list:
                    f.write("\nAll Scanned Files:\n")
                    f.write("-----------------------------------\n")
                    for file_info in scan_result.scanned_file_list:
                        f.write(f"- {file_info['path']} ({file_info['status']}) - {file_info['timestamp']}\n")

            QMessageBox.information(self, "Export Successful", f"Scan results exported to {file_path}")

        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Error exporting scan results: {str(e)}")

    def clear_history(self):
        """Clear scan history"""
        # Confirm with user
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all scan history?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Clear history
            self.scanner.scan_history = []

            # Update table
            self.update_scans([])

            # Clear details
            self.details_tree.clear()

    def on_scan_started(self, scan_id, device_id):
        """Handle scan started signal"""
        # Update scans table
        self.update_scans(self.scanner.scan_history)

    def on_scan_progress(self, scan_id, scanned_files, total_files):
        """Handle scan progress signal"""
        # Update scans table
        self.update_scans(self.scanner.scan_history)

    def on_scan_finished(self, scan_id, result):
        """Handle scan finished signal"""
        # Update scans table
        self.update_scans(self.scanner.scan_history)

    def _get_status_text(self, status):
        """Get text representation of scan status"""
        if status == "pending":
            return "Pending"
        elif status == "in_progress":
            return "In Progress"
        elif status == "completed":
            return "Completed"
        elif status == "failed":
            return "Failed"
        elif status == "cancelled":
            return "Cancelled"
        else:
            return status.capitalize()

    def _get_status_color(self, status):
        """Get color for scan status"""
        if status == "pending":
            return "#3498db"  # Blue
        elif status == "in_progress":
            return "#f39c12"  # Orange
        elif status == "completed":
            return "#2ecc71"  # Green
        elif status == "failed":
            return "#e74c3c"  # Red
        elif status == "cancelled":
            return "#95a5a6"  # Gray
        else:
            return "#bdc3c7"  # Light gray
