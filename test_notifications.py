#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Notifications
Tests both email and SMS notifications
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the notification manager
from usb_monitor_desktop.src.utils.notifications import NotificationManager

def load_config():
    """Load notification configuration"""
    config_path = "usb_monitor_desktop/config/notification_config.json"
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return {}

def test_notifications():
    """Test both email and SMS notifications"""
    # Load configuration
    config = load_config()
    
    # Create notification manager
    notification_manager = NotificationManager(config)
    
    # Create test device info
    device_info = {
        "id": "TEST-123",
        "name": "Test USB Device",
        "manufacturer": "Test Manufacturer",
        "serial_number": "TEST-SERIAL-123",
        "connection_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": 100,
        "scanned_files": 100,
        "scan_duration": 5.2,
        "malicious_files": ["E:\\test\\malware.exe", "E:\\test\\virus.bat"],
        "suspicious_files": ["E:\\test\\suspicious.js"]
    }
    
    # Test email notification
    print("Testing email notification...")
    notification_manager._send_email_notification(
        "Test Email Notification",
        "This is a test email notification from the USB Monitoring System.",
        "critical",
        device_info
    )
    
    # Test SMS notification
    print("\nTesting SMS notification...")
    notification_manager._send_twilio_sms(
        "USB Monitor Test: This is a test SMS notification from the USB Monitoring System.",
        "+919944273645"
    )
    
    print("\nNotification tests completed. Check your email and phone for messages.")

if __name__ == "__main__":
    test_notifications()
