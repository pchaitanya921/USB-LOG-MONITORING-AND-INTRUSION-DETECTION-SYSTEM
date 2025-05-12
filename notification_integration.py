#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notification Integration Module
Integrates the enhanced notification service with the USB monitoring application
"""

import os
import json
import logging
import threading
from enhanced_notification_service import EnhancedNotificationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notification_integration.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("notification_integration")

class NotificationIntegration:
    """Integrates enhanced notification service with the application"""
    
    def __init__(self, config_path="notification_config.json"):
        """Initialize the notification integration"""
        self.config_path = config_path
        self.notification_service = None
        
        # Initialize notification service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the notification service"""
        try:
            self.notification_service = EnhancedNotificationService(self.config_path)
            logger.info("Enhanced notification service initialized")
        except Exception as e:
            logger.error(f"Error initializing notification service: {str(e)}")
    
    def reload_config(self):
        """Reload configuration from file"""
        try:
            if self.notification_service:
                # Load config from file
                if os.path.exists(self.config_path):
                    with open(self.config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Update notification service config
                    self.notification_service.update_config(config)
                    logger.info("Notification service configuration reloaded")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error reloading configuration: {str(e)}")
            return False
    
    def notify_device_connected(self, device):
        """Send notification for device connection"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown'),
                "connection_time": getattr(device, 'connection_time', 'Unknown')
            }
            
            # Send notification
            return self.notification_service.send_notification(
                "connect",
                device_info
            )
        except Exception as e:
            logger.error(f"Error sending device connected notification: {str(e)}")
            return False
    
    def notify_device_disconnected(self, device):
        """Send notification for device disconnection"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown'),
                "disconnection_time": getattr(device, 'disconnection_time', 'Unknown')
            }
            
            # Send notification
            return self.notification_service.send_notification(
                "disconnect",
                device_info
            )
        except Exception as e:
            logger.error(f"Error sending device disconnected notification: {str(e)}")
            return False
    
    def notify_scan_started(self, device):
        """Send notification for scan started"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown')
            }
            
            # Send notification
            return self.notification_service.send_notification(
                "scan_start",
                device_info
            )
        except Exception as e:
            logger.error(f"Error sending scan started notification: {str(e)}")
            return False
    
    def notify_scan_completed(self, device, scan_result):
        """Send notification for scan completed"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown')
            }
            
            # Convert scan result to dict if needed
            scan_results = scan_result.to_dict() if hasattr(scan_result, 'to_dict') else {
                "scanned_files": getattr(scan_result, 'scanned_files', 0),
                "total_files": getattr(scan_result, 'total_files', 0),
                "scan_duration": getattr(scan_result, 'scan_duration', 0),
                "malicious_files": getattr(scan_result, 'malicious_files', []),
                "suspicious_files": getattr(scan_result, 'suspicious_files', [])
            }
            
            # Send notification
            return self.notification_service.send_notification(
                "scan_complete",
                device_info,
                scan_results
            )
        except Exception as e:
            logger.error(f"Error sending scan completed notification: {str(e)}")
            return False
    
    def notify_threat_detected(self, device, threat_info):
        """Send notification for threat detected"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown')
            }
            
            # Create scan results with threat info
            scan_results = {
                "malicious_files": [threat_info],
                "suspicious_files": [],
                "scanned_files": 1,
                "total_files": 1,
                "scan_duration": 0
            }
            
            # Send notification
            return self.notification_service.send_notification(
                "threat_detected",
                device_info,
                scan_results
            )
        except Exception as e:
            logger.error(f"Error sending threat detected notification: {str(e)}")
            return False
    
    def notify_suspicious_detected(self, device, suspicious_info):
        """Send notification for suspicious file detected"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown')
            }
            
            # Create scan results with suspicious info
            scan_results = {
                "malicious_files": [],
                "suspicious_files": [suspicious_info],
                "scanned_files": 1,
                "total_files": 1,
                "scan_duration": 0
            }
            
            # Send notification
            return self.notification_service.send_notification(
                "suspicious_detected",
                device_info,
                scan_results
            )
        except Exception as e:
            logger.error(f"Error sending suspicious detected notification: {str(e)}")
            return False
    
    def notify_system_error(self, device, error_message):
        """Send notification for system error"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown')
            }
            
            # Send notification
            return self.notification_service.send_notification(
                "system_error",
                device_info,
                custom_message=error_message
            )
        except Exception as e:
            logger.error(f"Error sending system error notification: {str(e)}")
            return False
    
    def send_custom_notification(self, notification_type, device, message, scan_results=None):
        """Send a custom notification"""
        if not self.notification_service:
            return False
        
        try:
            # Convert device to dict if needed
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "manufacturer": getattr(device, 'manufacturer', 'Unknown'),
                "serial_number": getattr(device, 'serial_number', 'Unknown')
            }
            
            # Send notification
            return self.notification_service.send_notification(
                notification_type,
                device_info,
                scan_results,
                message
            )
        except Exception as e:
            logger.error(f"Error sending custom notification: {str(e)}")
            return False
    
    def stop(self):
        """Stop the notification service"""
        if self.notification_service:
            self.notification_service.stop()
            logger.info("Notification service stopped")

# Example usage
if __name__ == "__main__":
    # Create notification integration
    integration = NotificationIntegration()
    
    # Create a test device
    class TestDevice:
        def __init__(self):
            self.id = "TEST-123"
            self.name = "Test Device"
            self.manufacturer = "Test Manufacturer"
            self.serial_number = "TEST-SN-123456"
    
    # Create a test scan result
    class TestScanResult:
        def __init__(self):
            self.scanned_files = 100
            self.total_files = 100
            self.scan_duration = 2.5
            self.malicious_files = [
                {
                    "path": "C:\\test\\malware.exe",
                    "detection_type": "Signature match",
                    "threat_level": "critical"
                }
            ]
            self.suspicious_files = [
                {
                    "path": "C:\\test\\suspicious.js",
                    "detection_type": "Heuristic detection",
                    "threat_level": "medium"
                }
            ]
    
    # Send test notifications
    device = TestDevice()
    scan_result = TestScanResult()
    
    integration.notify_device_connected(device)
    integration.notify_scan_started(device)
    integration.notify_scan_completed(device, scan_result)
    
    # Stop the service
    integration.stop()
