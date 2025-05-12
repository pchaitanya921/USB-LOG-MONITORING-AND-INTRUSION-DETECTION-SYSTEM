#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test USB Scan Notification
Simulates a USB scan and sends a notification
"""

import os
import sys
import json
import datetime

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the notification manager
from usb_monitor_desktop.src.utils.notifications import NotificationManager

# Create a mock device
class MockDevice:
    def __init__(self):
        self.id = "456"
        self.name = "SanDisk Ultra"
        self.manufacturer = "SanDisk"
        self.serial_number = "9876543210"
        self.connection_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.drive_letter = "E:\\"
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "serial_number": self.serial_number,
            "connection_time": self.connection_time,
            "drive_letter": self.drive_letter
        }

# Create a mock scan result
class MockScanResult:
    def __init__(self, has_threats=False, has_suspicious=False):
        self.scan_id = "scan123"
        self.timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.status = "completed"
        self.total_files = 150
        self.scanned_files = 150
        self.scan_duration = 3.5
        self.device_id = "456"
        
        if has_threats:
            self.malicious_files = [
                "E:\\malware.exe",
                "E:\\ransomware.txt",
                "E:\\virus.dll"
            ]
        else:
            self.malicious_files = []
            
        if has_suspicious:
            self.suspicious_files = [
                "E:\\suspicious.bat",
                "E:\\crack.exe"
            ]
        else:
            self.suspicious_files = []
            
    def to_dict(self):
        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "total_files": self.total_files,
            "scanned_files": self.scanned_files,
            "scan_duration": self.scan_duration,
            "device_id": self.device_id,
            "malicious_files": self.malicious_files,
            "suspicious_files": self.suspicious_files
        }

def main():
    # Create notification manager
    notification_manager = NotificationManager()
    
    # Create mock device
    device = MockDevice()
    
    # Test scenarios
    print("Testing clean scan notification...")
    clean_scan = MockScanResult()
    notification_manager.send_scan_completed_notification(device, clean_scan)
    
    print("\nTesting suspicious scan notification...")
    suspicious_scan = MockScanResult(has_suspicious=True)
    notification_manager.send_scan_completed_notification(device, suspicious_scan)
    
    print("\nTesting malicious scan notification...")
    malicious_scan = MockScanResult(has_threats=True)
    notification_manager.send_scan_completed_notification(device, malicious_scan)
    
    print("\nTesting malicious and suspicious scan notification...")
    both_scan = MockScanResult(has_threats=True, has_suspicious=True)
    notification_manager.send_scan_completed_notification(device, both_scan)
    
if __name__ == "__main__":
    main()
