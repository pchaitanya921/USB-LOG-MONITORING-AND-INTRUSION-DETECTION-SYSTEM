#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enhanced SMS Notification Demo
Demonstrates the enhanced SMS notification features
"""

import os
import sys
import time
import json
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QGroupBox, QMessageBox

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import notification modules
from enhanced_notification_service import EnhancedNotificationService
from notification_integration import NotificationIntegration
from sms_notification_settings import NotificationSettingsWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("demo_enhanced_sms.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("demo_enhanced_sms")

class DemoDevice:
    """Demo USB device for testing"""
    def __init__(self, device_id, name, manufacturer, serial_number):
        self.id = device_id
        self.name = name
        self.manufacturer = manufacturer
        self.serial_number = serial_number
        self.connection_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        """Convert device to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "serial_number": self.serial_number,
            "connection_time": self.connection_time
        }

class DemoScanResult:
    """Demo scan result for testing"""
    def __init__(self, scanned_files, total_files, scan_duration, malicious_files=None, suspicious_files=None):
        self.scanned_files = scanned_files
        self.total_files = total_files
        self.scan_duration = scan_duration
        self.malicious_files = malicious_files or []
        self.suspicious_files = suspicious_files or []
    
    def to_dict(self):
        """Convert scan result to dictionary"""
        return {
            "scanned_files": self.scanned_files,
            "total_files": self.total_files,
            "scan_duration": self.scan_duration,
            "malicious_files": self.malicious_files,
            "suspicious_files": self.suspicious_files
        }

class DemoWindow(QMainWindow):
    """Demo window for testing enhanced SMS notifications"""
    def __init__(self):
        super().__init__()
        
        # Set up window
        self.setWindowTitle("Enhanced SMS Notification Demo")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create settings button
        settings_button = QPushButton("Open SMS Settings")
        settings_button.clicked.connect(self.open_settings)
        main_layout.addWidget(settings_button)
        
        # Create device selection group
        device_group = QGroupBox("Select USB Device")
        device_layout = QVBoxLayout(device_group)
        
        # Device selection
        self.device_combo = QComboBox()
        self.device_combo.addItems([
            "SanDisk Ultra (16GB)",
            "Kingston DataTraveler (32GB)",
            "Samsung BAR Plus (64GB)",
            "Lexar JumpDrive (128GB)",
            "WD My Passport (1TB)"
        ])
        device_layout.addWidget(self.device_combo)
        
        main_layout.addWidget(device_group)
        
        # Create notification test group
        test_group = QGroupBox("Test Notifications")
        test_layout = QVBoxLayout(test_group)
        
        # Connection notification
        connect_button = QPushButton("Test Device Connected Notification")
        connect_button.clicked.connect(self.test_connect)
        test_layout.addWidget(connect_button)
        
        # Scan started notification
        scan_start_button = QPushButton("Test Scan Started Notification")
        scan_start_button.clicked.connect(self.test_scan_start)
        test_layout.addWidget(scan_start_button)
        
        # Clean scan notification
        clean_scan_button = QPushButton("Test Clean Scan Notification")
        clean_scan_button.clicked.connect(self.test_clean_scan)
        test_layout.addWidget(clean_scan_button)
        
        # Suspicious scan notification
        suspicious_scan_button = QPushButton("Test Suspicious Files Notification")
        suspicious_scan_button.clicked.connect(self.test_suspicious_scan)
        test_layout.addWidget(suspicious_scan_button)
        
        # Malicious scan notification
        malicious_scan_button = QPushButton("Test Malicious Files Notification")
        malicious_scan_button.clicked.connect(self.test_malicious_scan)
        test_layout.addWidget(malicious_scan_button)
        
        # System error notification
        error_button = QPushButton("Test System Error Notification")
        error_button.clicked.connect(self.test_error)
        test_layout.addWidget(error_button)
        
        main_layout.addWidget(test_group)
        
        # Create message format group
        format_group = QGroupBox("Message Format")
        format_layout = QVBoxLayout(format_group)
        
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Brief", "Standard", "Detailed"])
        self.format_combo.setCurrentIndex(1)  # Default to Standard
        self.format_combo.currentIndexChanged.connect(self.update_format)
        format_layout.addWidget(self.format_combo)
        
        main_layout.addWidget(format_group)
        
        # Create status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        # Initialize notification integration
        self.integration = NotificationIntegration()
        
        # Update format
        self.update_format(self.format_combo.currentIndex())
    
    def open_settings(self):
        """Open SMS settings window"""
        settings_window = NotificationSettingsWindow()
        settings_window.exec_()
        
        # Reload configuration
        self.integration.reload_config()
        
        self.status_label.setText("Settings updated")
    
    def update_format(self, index):
        """Update message format"""
        formats = ["brief", "standard", "detailed"]
        format_name = formats[index]
        
        # Update config
        config_path = "notification_config.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                config["message_format"] = format_name
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=4)
                
                # Reload configuration
                self.integration.reload_config()
                
                self.status_label.setText(f"Message format set to {format_name}")
                
            except Exception as e:
                self.status_label.setText(f"Error updating format: {str(e)}")
    
    def get_selected_device(self):
        """Get the selected device"""
        device_name = self.device_combo.currentText()
        
        # Parse device info
        if "SanDisk" in device_name:
            return DemoDevice("456", "SanDisk Ultra", "SanDisk", "9876543210")
        elif "Kingston" in device_name:
            return DemoDevice("789", "Kingston DataTraveler", "Kingston", "1234567890")
        elif "Samsung" in device_name:
            return DemoDevice("123", "Samsung BAR Plus", "Samsung", "5678901234")
        elif "Lexar" in device_name:
            return DemoDevice("234", "Lexar JumpDrive", "Lexar", "6789012345")
        else:
            return DemoDevice("345", "WD My Passport", "Western Digital", "7890123456")
    
    def test_connect(self):
        """Test device connected notification"""
        device = self.get_selected_device()
        
        # Send notification
        success = self.integration.notify_device_connected(device)
        
        if success:
            self.status_label.setText(f"Device connected notification sent for {device.name}")
        else:
            self.status_label.setText("Failed to send device connected notification")
    
    def test_scan_start(self):
        """Test scan started notification"""
        device = self.get_selected_device()
        
        # Send notification
        success = self.integration.notify_scan_started(device)
        
        if success:
            self.status_label.setText(f"Scan started notification sent for {device.name}")
        else:
            self.status_label.setText("Failed to send scan started notification")
    
    def test_clean_scan(self):
        """Test clean scan notification"""
        device = self.get_selected_device()
        
        # Create scan result
        scan_result = DemoScanResult(
            scanned_files=150,
            total_files=150,
            scan_duration=3.5,
            malicious_files=[],
            suspicious_files=[]
        )
        
        # Send notification
        success = self.integration.notify_scan_completed(device, scan_result)
        
        if success:
            self.status_label.setText(f"Clean scan notification sent for {device.name}")
        else:
            self.status_label.setText("Failed to send clean scan notification")
    
    def test_suspicious_scan(self):
        """Test suspicious files notification"""
        device = self.get_selected_device()
        
        # Create scan result
        scan_result = DemoScanResult(
            scanned_files=200,
            total_files=200,
            scan_duration=4.2,
            malicious_files=[],
            suspicious_files=[
                {
                    "path": "D:\\Documents\\suspicious_script.js",
                    "detection_type": "Heuristic detection",
                    "threat_level": "medium"
                },
                {
                    "path": "D:\\Downloads\\unusual_behavior.exe",
                    "detection_type": "Behavioral analysis",
                    "threat_level": "medium"
                },
                {
                    "path": "D:\\Photos\\hidden_data.jpg",
                    "detection_type": "Steganography detection",
                    "threat_level": "low"
                }
            ]
        )
        
        # Send notification
        success = self.integration.notify_scan_completed(device, scan_result)
        
        if success:
            self.status_label.setText(f"Suspicious files notification sent for {device.name}")
        else:
            self.status_label.setText("Failed to send suspicious files notification")
    
    def test_malicious_scan(self):
        """Test malicious files notification"""
        device = self.get_selected_device()
        
        # Create scan result
        scan_result = DemoScanResult(
            scanned_files=180,
            total_files=180,
            scan_duration=5.1,
            malicious_files=[
                {
                    "path": "D:\\Programs\\infected_app.exe",
                    "detection_type": "Signature match",
                    "threat_level": "critical"
                },
                {
                    "path": "D:\\System\\trojan.dll",
                    "detection_type": "Known malware",
                    "threat_level": "critical"
                }
            ],
            suspicious_files=[
                {
                    "path": "D:\\Downloads\\suspicious_file.pdf",
                    "detection_type": "Suspicious content",
                    "threat_level": "medium"
                }
            ]
        )
        
        # Send notification
        success = self.integration.notify_scan_completed(device, scan_result)
        
        if success:
            self.status_label.setText(f"Malicious files notification sent for {device.name}")
        else:
            self.status_label.setText("Failed to send malicious files notification")
    
    def test_error(self):
        """Test system error notification"""
        device = self.get_selected_device()
        
        # Send notification
        success = self.integration.notify_system_error(
            device,
            "Error accessing USB device. The device may be disconnected or malfunctioning."
        )
        
        if success:
            self.status_label.setText(f"System error notification sent for {device.name}")
        else:
            self.status_label.setText("Failed to send system error notification")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop notification service
        self.integration.stop()
        event.accept()

# Run as standalone application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec_())
