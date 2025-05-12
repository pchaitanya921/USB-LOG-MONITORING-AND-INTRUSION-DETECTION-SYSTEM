import os
import sys
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.app import app, socketio
from backend.models.db import db
from backend.models.device import USBDevice, PermissionLevel
from backend.models.alert import Alert
from backend.models.settings import UserSettings
from backend.models.scan import ScanResult
from backend.utils.usb_detector import get_connected_devices
from backend.utils.notification import send_connection_notification
from backend.utils.scanner import scan_device

class USBMonitor:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        self.last_devices = {}

    def start(self):
        """Start the USB monitoring thread"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()

        print("USB monitoring started")

    def stop(self):
        """Stop the USB monitoring thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

        print("USB monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                with self.app.app_context():
                    self._check_devices()
            except Exception as e:
                print(f"Error in USB monitor: {e}")

            # Sleep for a short time before checking again
            time.sleep(2)

    def _check_devices(self):
        """Check for USB device changes"""
        # Get currently connected devices
        current_devices = get_connected_devices()

        # Check for new devices
        for device_id, device_info in current_devices.items():
            if device_id not in self.last_devices:
                self._handle_new_device(device_id, device_info)

        # Check for disconnected devices
        for device_id in list(self.last_devices.keys()):
            if device_id not in current_devices:
                self._handle_disconnected_device(device_id)

        # Update last devices
        self.last_devices = current_devices

    def _handle_new_device(self, device_id, device_info):
        """Handle a newly connected USB device"""
        # Check if device already exists in database
        device = USBDevice.query.filter_by(device_id=device_id).first()

        if device:
            # Update existing device
            device.is_connected = True
            device.last_connected_at = datetime.utcnow()
            if not device.mount_point and 'mount_point' in device_info:
                device.mount_point = device_info['mount_point']

            alert_type = "reconnection"
            message = f"USB device reconnected: {device.product_name or 'Unknown Device'}"
        else:
            # Create new device with read-only permission by default
            device = USBDevice(
                device_id=device_id,
                vendor_id=device_info.get('vendor_id'),
                product_id=device_info.get('product_id'),
                manufacturer=device_info.get('manufacturer'),
                product_name=device_info.get('product_name'),
                serial_number=device_info.get('serial_number'),
                mount_point=device_info.get('mount_point'),
                is_connected=True,
                is_permitted=True  # Allow read-only access by default
            )
            # Set the property values
            device.has_threats = False
            db.session.add(device)
            # Commit to get the device ID
            db.session.commit()

            alert_type = "new_connection"
            message = f"New USB device connected: {device_info.get('product_name', 'Unknown Device')}. Set to read-only mode."

        # Create an alert
        alert = Alert(
            device_id=device.id,
            alert_type=alert_type,
            message=message,
            severity="warning"
        )
        db.session.add(alert)
        db.session.commit()

        # Send notification
        send_connection_notification(device, alert_type)

        # Emit socket event
        socketio.emit('usb_connected', {
            'device': device.to_dict(),
            'alert': alert.to_dict()
        })

        # Auto-scan if enabled
        settings = UserSettings.query.first()
        if settings and settings.auto_scan and device.is_permitted and device.mount_point:
            self._auto_scan_device(device)

    def _handle_disconnected_device(self, device_id):
        """Handle a disconnected USB device"""
        device = USBDevice.query.filter_by(device_id=device_id).first()

        if device:
            device.is_connected = False
            device.last_disconnected_at = datetime.utcnow()

            # Create an alert
            alert = Alert(
                device_id=device.id,
                alert_type="disconnection",
                message=f"USB device disconnected: {device.product_name or 'Unknown Device'}",
                severity="info"
            )
            db.session.add(alert)
            db.session.commit()

            # Emit socket event
            socketio.emit('usb_disconnected', {
                'device': device.to_dict(),
                'alert': alert.to_dict()
            })

    def _auto_scan_device(self, device):
        """Automatically scan a USB device"""
        try:
            # Create a new scan result
            scan_result = ScanResult(
                device_id=device.id,
                status='in_progress',
                scan_date=datetime.utcnow()
            )
            db.session.add(scan_result)
            db.session.commit()

            # Emit socket event for scan start
            socketio.emit('scan_started', {
                'device': device.to_dict(),
                'scan': scan_result.to_dict()
            })

            # Start the scan in a background thread
            threading.Thread(
                target=self._perform_scan,
                args=(device, scan_result)
            ).start()

        except Exception as e:
            print(f"Error starting auto-scan: {e}")

    def _perform_scan(self, device, scan_result):
        """Perform the actual scan in a background thread"""
        try:
            with self.app.app_context():
                start_time = time.time()

                # Perform the scan
                scan_results = scan_device(device.mount_point)

                # Update scan result
                scan_result.status = 'completed'
                scan_result.total_files = scan_results['total_files']
                scan_result.scanned_files = scan_results['scanned_files']
                scan_result.infected_files = len(scan_results['infected_files'])
                scan_result.suspicious_files = len(scan_results['suspicious_files'])
                scan_result.scan_duration = time.time() - start_time

                # Process results and create alerts if needed
                from backend.app import process_scan_results
                process_scan_results(device, scan_result, scan_results)

                # Emit socket event for scan completion
                socketio.emit('scan_completed', {
                    'device': device.to_dict(),
                    'scan': scan_result.to_dict()
                })

        except Exception as e:
            with self.app.app_context():
                # Handle scan errors
                scan_result.status = 'error'
                scan_result.scan_duration = time.time() - start_time

                alert = Alert(
                    device_id=device.id,
                    scan_id=scan_result.id,
                    alert_type="scan_error",
                    message=f"Error scanning device {device.product_name}: {str(e)}",
                    severity="warning"
                )
                db.session.add(alert)
                db.session.commit()

                # Emit socket event for scan error
                socketio.emit('scan_error', {
                    'device': device.to_dict(),
                    'scan': scan_result.to_dict(),
                    'error': str(e)
                })

# Create and start the USB monitor
monitor = USBMonitor(app)

def start_monitor():
    """Start the USB monitor"""
    monitor.start()

def stop_monitor():
    """Stop the USB monitor"""
    monitor.stop()

if __name__ == "__main__":
    start_monitor()
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_monitor()
