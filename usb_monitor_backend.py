import os
import sys
import time
import json
import logging
import smtplib
import datetime
import subprocess
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("usb_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("USB_Monitor")

# Twilio configuration
TWILIO_ACCOUNT_SID = "AC94656f2081ae1c98c4cece8dd68ca056"
TWILIO_AUTH_TOKEN = "70cfd6672bc72163dd2077bc3562ffa9"
TWILIO_PHONE_NUMBER = "+19082631380"
ALERT_RECIPIENT_PHONE = "+919944273645"

# Email configuration
EMAIL_USERNAME = "chaitanyasai9391@gmail.com"
EMAIL_PASSWORD = "vvkdquyanoswsvso"
EMAIL_RECIPIENT = "chaitanyasai401@gmail.com"

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for demo purposes
devices = []
scans = []
alerts = []

# USB detection simulation
connected_devices = {}
last_device_id = 0

def send_sms_alert(message):
    """Send SMS alert using Twilio"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=ALERT_RECIPIENT_PHONE
        )
        logger.info(f"SMS sent successfully: {message.sid}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        return False

def send_email_alert(subject, message):
    """Send email alert"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, EMAIL_RECIPIENT, text)
        server.quit()

        logger.info("Email sent successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def generate_device_id():
    """Generate a unique device ID"""
    global last_device_id
    last_device_id += 1
    return last_device_id

def scan_usb_device(device):
    """Scan a USB device for threats"""
    logger.info(f"Scanning device: {device['product_name']} at {device['mount_point']}")

    # Emit scan start event
    socketio.emit('scan_started', {
        'device_id': device['id'],
        'device_name': device['product_name'],
        'timestamp': datetime.datetime.now().isoformat()
    })

    start_time = time.time()
    mount_point = device['mount_point']

    # Check if drive is accessible
    drive_path = f"{mount_point}\\"
    if not os.path.exists(drive_path):
        logger.warning(f"Drive {mount_point} is not accessible")

        # Create scan result for inaccessible drive
        scan_result = {
            "id": len(scans) + 1,
            "device_id": device["id"],
            "status": "completed",
            "scan_date": datetime.datetime.now().isoformat(),
            "total_files": 0,
            "scanned_files": 0,
            "infected_files": 0,
            "suspicious_files": 0,
            "malicious_file_paths": [],
            "suspicious_file_paths": [],
            "scan_duration": 0.1,
            "error": "Drive not accessible"
        }

        # Create alert for scan completion
        new_alert = {
            "id": len(alerts) + 1,
            "device_id": device["id"],
            "alert_type": "scan_complete",
            "message": f"Scan completed on {device['product_name']} - Drive not accessible",
            "timestamp": datetime.datetime.now().isoformat(),
            "severity": "warning"
        }

        # Add to global lists
        scans.append(scan_result)
        alerts.append(new_alert)

        logger.info(f"Scan completed for {device['product_name']}: {new_alert['message']}")
        return scan_result, new_alert

    # Get file count
    try:
        # Use direct file system access to count files
        total_files = 0
        for root, _, files in os.walk(drive_path):
            total_files += len(files)
            # Limit file count to prevent excessive scanning
            if total_files > 1000:
                break

        # Emit file count update
        socketio.emit('scan_progress', {
            'device_id': device['id'],
            'total_files': total_files,
            'scanned_files': 0,
            'status': 'counting',
            'message': f"Found {total_files} files to scan"
        })
    except Exception as e:
        logger.error(f"Error counting files: {str(e)}")
        total_files = 0

        # Emit error update
        socketio.emit('scan_error', {
            'device_id': device['id'],
            'error': str(e),
            'status': 'error',
            'message': f"Error counting files: {str(e)}"
        })

    # Scan for malicious files (in a real system, you would use an antivirus API)
    # For demo, we'll look for suspicious file extensions and patterns
    infected_files = []
    suspicious_files = []
    scanned_files = 0

    try:
        # Define potentially malicious file extensions
        malicious_extensions = ['.exe', '.bat', '.vbs', '.ps1', '.js', '.hta', '.scr']
        suspicious_extensions = ['.dll', '.sys', '.bin', '.tmp', '.dat']

        # Scan files directly using os.walk
        for root, _, files in os.walk(drive_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                # Update scan progress
                scanned_files += 1

                # Emit progress update every 10 files or for suspicious/malicious files
                if scanned_files % 10 == 0:
                    socketio.emit('scan_progress', {
                        'device_id': device['id'],
                        'total_files': total_files,
                        'scanned_files': scanned_files,
                        'percent': min(100, int((scanned_files / max(1, total_files)) * 100)),
                        'status': 'scanning',
                        'current_file': file_path.replace(drive_path, '')
                    })

                if file_ext in malicious_extensions:
                    infected_files.append(file_path)

                    # Emit malicious file found event
                    socketio.emit('malicious_file_found', {
                        'device_id': device['id'],
                        'file_path': file_path.replace(drive_path, ''),
                        'file_name': os.path.basename(file_path),
                        'reason': f"Malicious file extension: {file_ext}"
                    })

                elif file_ext in suspicious_extensions:
                    suspicious_files.append(file_path)

                    # Emit suspicious file found event
                    socketio.emit('suspicious_file_found', {
                        'device_id': device['id'],
                        'file_path': file_path.replace(drive_path, ''),
                        'file_name': os.path.basename(file_path),
                        'reason': f"Suspicious file extension: {file_ext}"
                    })

            # Limit file scanning to prevent excessive scanning
            if len(infected_files) + len(suspicious_files) > 100:
                break

    except Exception as e:
        logger.error(f"Error scanning for malicious files: {str(e)}")

        # Emit error update
        socketio.emit('scan_error', {
            'device_id': device['id'],
            'error': str(e),
            'status': 'error',
            'message': f"Error scanning files: {str(e)}"
        })

    # Calculate scan duration
    scan_duration = round(time.time() - start_time, 1)

    # Create scan result
    scan_result = {
        "id": len(scans) + 1,
        "device_id": device["id"],
        "status": "completed",
        "scan_date": datetime.datetime.now().isoformat(),
        "total_files": total_files,
        "scanned_files": total_files,
        "infected_files": len(infected_files),
        "suspicious_files": len(suspicious_files),
        "malicious_file_paths": infected_files,
        "suspicious_file_paths": suspicious_files,
        "scan_duration": scan_duration
    }

    # Update device status based on scan
    device["last_scanned_at"] = scan_result["scan_date"]

    if scan_result["infected_files"] > 0:
        device["has_threats"] = True
        device["permission_status"] = "Blocked"
        device["is_permitted"] = False

        # Create alert for malicious files
        alert_message = f"Malicious USB detected: {device['product_name']} ({device['manufacturer']}). {scan_result['infected_files']} malicious files found."

        # Create detailed message with file paths
        malicious_files_list = "\n".join([f"- {file}" for file in scan_result["malicious_file_paths"][:10]])
        if len(scan_result["malicious_file_paths"]) > 10:
            malicious_files_list += f"\n- ... and {len(scan_result['malicious_file_paths']) - 10} more files"

        # Send SMS and email alerts
        send_sms_alert(alert_message)
        send_email_alert("ALERT: Malicious USB Detected",
                         f"Malicious USB device detected!\n\n"
                         f"Device: {device['product_name']}\n"
                         f"Manufacturer: {device['manufacturer']}\n"
                         f"Serial: {device['serial_number']}\n"
                         f"Mount Point: {device['mount_point']}\n"
                         f"Infected Files: {scan_result['infected_files']}\n\n"
                         f"Malicious files found:\n{malicious_files_list}\n\n"
                         f"The device has been blocked for your security.")

    elif scan_result["suspicious_files"] > 0:
        device["has_threats"] = False
        device["permission_status"] = "Read Only"
        device["is_permitted"] = True

        # Create alert for suspicious files
        alert_message = f"Suspicious USB detected: {device['product_name']} ({device['manufacturer']}). {scan_result['suspicious_files']} suspicious files found."

        # Create detailed message with file paths
        suspicious_files_list = "\n".join([f"- {file}" for file in scan_result["suspicious_file_paths"][:10]])
        if len(scan_result["suspicious_file_paths"]) > 10:
            suspicious_files_list += f"\n- ... and {len(scan_result['suspicious_file_paths']) - 10} more files"

        # Send SMS and email alerts
        send_sms_alert(alert_message)
        send_email_alert("WARNING: Suspicious USB Detected",
                         f"Suspicious USB device detected!\n\n"
                         f"Device: {device['product_name']}\n"
                         f"Manufacturer: {device['manufacturer']}\n"
                         f"Serial: {device['serial_number']}\n"
                         f"Mount Point: {device['mount_point']}\n"
                         f"Suspicious Files: {scan_result['suspicious_files']}\n\n"
                         f"Suspicious files found:\n{suspicious_files_list}\n\n"
                         f"The device has been set to Read Only mode for your security.")

    else:
        device["has_threats"] = False
        device["permission_status"] = "Read Only"
        device["is_permitted"] = True

        # Create alert for secure device
        alert_message = f"Secured USB connected: {device['product_name']} ({device['manufacturer']}). No threats detected."

        # Send SMS and email alerts
        send_sms_alert(alert_message)
        send_email_alert("NOTIFICATION: Secured USB Connected",
                         f"A secured USB device has been connected.\n\n"
                         f"Device: {device['product_name']}\n"
                         f"Manufacturer: {device['manufacturer']}\n"
                         f"Serial: {device['serial_number']}\n"
                         f"Mount Point: {device['mount_point']}\n\n"
                         f"No threats were detected. The device has been set to Read Only mode by default.")

    # Create alert for scan completion
    message = f"Scan completed on {device['product_name']} - "

    if scan_result['infected_files'] > 0:
        file_list = [os.path.basename(file) for file in scan_result['malicious_file_paths'][:3]]
        file_str = ", ".join(file_list)
        if len(scan_result['malicious_file_paths']) > 3:
            file_str += f" and {len(scan_result['malicious_file_paths']) - 3} more"
        message += f"{scan_result['infected_files']} malicious files detected! ({file_str})"
        severity = "danger"
    elif scan_result['suspicious_files'] > 0:
        file_list = [os.path.basename(file) for file in scan_result['suspicious_file_paths'][:3]]
        file_str = ", ".join(file_list)
        if len(scan_result['suspicious_file_paths']) > 3:
            file_str += f" and {len(scan_result['suspicious_file_paths']) - 3} more"
        message += f"{scan_result['suspicious_files']} suspicious files detected ({file_str})"
        severity = "warning"
    else:
        message += "No threats detected"
        severity = "success"

    new_alert = {
        "id": len(alerts) + 1,
        "device_id": device["id"],
        "alert_type": "scan_complete",
        "message": message,
        "timestamp": datetime.datetime.now().isoformat(),
        "severity": severity,
        "malicious_file_paths": scan_result.get("malicious_file_paths", []),
        "suspicious_file_paths": scan_result.get("suspicious_file_paths", [])
    }

    # Add scan and alert to history
    scans.append(scan_result)
    alerts.append(new_alert)

    # Emit scan complete event
    socketio.emit('scan_complete', {
        'device_id': device['id'],
        'device_name': device['product_name'],
        'total_files': total_files,
        'scanned_files': scanned_files,
        'infected_files': len(infected_files),
        'suspicious_files': len(suspicious_files),
        'scan_duration': scan_duration,
        'status': 'complete',
        'result': severity,
        'message': message,
        'timestamp': datetime.datetime.now().isoformat()
    })

    logger.info(f"Scan completed for {device['product_name']}: {new_alert['message']}")
    return scan_result, new_alert

def get_connected_usb_drives():
    """Get real connected USB drives on Windows using pure Python"""
    try:
        import string
        from ctypes import windll

        # Get all drive letters
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()

        # Check each drive letter
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive_letter = f"{letter}:"
                drive_type = windll.kernel32.GetDriveTypeW(f"{letter}:\\")

                # Drive type 2 is removable (USB drives)
                if drive_type == 2:  # DRIVE_REMOVABLE
                    # Use simple volume name and serial number
                    volume_name = "USB Drive"
                    serial_number = f"USB-{drive_letter}-{int(time.time())}"

                    # Create drive data
                    drive_data = {
                        'DeviceID': drive_letter,
                        'DriveLetter': drive_letter,
                        'VolumeName': volume_name,
                        'Model': 'Removable Storage',
                        'Manufacturer': 'USB Device',
                        'SerialNumber': str(serial_number)
                    }

                    drives.append(drive_data)

            # Shift bitmask to check next drive
            bitmask >>= 1

        return drives
    except Exception as e:
        logger.error(f"Error getting USB drives: {str(e)}")
        return []

def detect_usb_devices():
    """Real USB device detection for Windows"""
    # Keep track of previously detected drives
    previous_drives = set()

    while True:
        try:
            # Get current USB drives
            current_usb_drives = get_connected_usb_drives()

            # Handle case when no drives are returned
            if not current_usb_drives:
                current_usb_drives = []

            # Get current drive letters
            current_drive_letters = set()
            for drive in current_usb_drives:
                if isinstance(drive, dict) and drive.get('DriveLetter'):
                    drive_letter = drive.get('DriveLetter', '').replace(':', '')
                    if drive_letter:
                        current_drive_letters.add(drive_letter)

            # Check for new connections
            for drive in current_usb_drives:
                if not isinstance(drive, dict):
                    continue

                drive_letter = drive.get('DriveLetter', '')
                if not drive_letter:
                    continue

                if drive_letter.replace(':', '') not in previous_drives:
                    # New USB drive detected
                    manufacturer = drive.get('Manufacturer', 'Unknown')
                    if not manufacturer or manufacturer == '':
                        manufacturer = 'Unknown'

                    product_name = drive.get('Model', 'USB Drive')
                    if not product_name or product_name == '':
                        product_name = 'USB Drive'

                    serial_number = drive.get('SerialNumber', '')
                    if not serial_number or serial_number == '':
                        serial_number = f"USB-{drive_letter}-{int(time.time())}"

                    # Create a new device
                    new_device = {
                        "id": generate_device_id(),
                        "device_id": f"USB_DEVICE_{last_device_id}",
                        "vendor_id": "0000",  # Default value
                        "product_id": "0000",  # Default value
                        "manufacturer": manufacturer.strip(),
                        "product_name": product_name.strip(),
                        "serial_number": serial_number.strip(),
                        "mount_point": drive_letter,
                        "is_connected": True,
                        "is_permitted": True,
                        "permission_status": "Read Only",
                        "has_threats": False,
                        "first_connected_at": datetime.datetime.now().isoformat(),
                        "last_connected_at": datetime.datetime.now().isoformat()
                    }

                    # Add to devices list
                    devices.append(new_device)
                    connected_devices[new_device["id"]] = new_device

                    # Create connection alert
                    new_alert = {
                        "id": len(alerts) + 1,
                        "device_id": new_device["id"],
                        "alert_type": "new_connection",
                        "message": f"New USB device connected: {new_device['product_name']} ({new_device['manufacturer']})",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "severity": "info"
                    }
                    alerts.append(new_alert)

                    logger.info(f"New USB device connected: {new_device['product_name']} at {drive_letter}")

                    # Send initial connection notification
                    connection_message = f"New USB device connected: {new_device['product_name']} ({new_device['manufacturer']})"
                    send_sms_alert(connection_message)
                    send_email_alert("USB Device Connected",
                                    f"A new USB device has been connected.\n\n"
                                    f"Device: {new_device['product_name']}\n"
                                    f"Manufacturer: {new_device['manufacturer']}\n"
                                    f"Serial: {new_device['serial_number']}\n"
                                    f"Mount Point: {new_device['mount_point']}\n\n"
                                    f"The device is being scanned for threats...")

                    # Start scanning thread
                    threading.Thread(target=scan_usb_device, args=(new_device,)).start()

            # Check for disconnections
            for device_id in list(connected_devices.keys()):
                device = connected_devices[device_id]
                drive_letter = device["mount_point"].replace(':', '')

                if drive_letter not in current_drive_letters:
                    # Device has been disconnected
                    device["is_connected"] = False

                    # Create disconnection alert
                    new_alert = {
                        "id": len(alerts) + 1,
                        "device_id": device["id"],
                        "alert_type": "disconnection",
                        "message": f"USB device disconnected: {device['product_name']} ({device['manufacturer']})",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "severity": "info"
                    }
                    alerts.append(new_alert)

                    logger.info(f"USB device disconnected: {device['product_name']}")
                    del connected_devices[device_id]

            # Update previous drives
            previous_drives = current_drive_letters

        except Exception as e:
            logger.error(f"Error in USB detection loop: {str(e)}")

        # Sleep for a short interval before checking again
        time.sleep(3)

# API Routes
@app.route('/')
def index():
    return app.send_static_file('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return app.send_static_file('dashboard.html')

@app.route('/devices')
def devices_page():
    return app.send_static_file('devices.html')

@app.route('/scans')
def scans_page():
    return app.send_static_file('scans.html')

@app.route('/alerts')
def alerts_page():
    return app.send_static_file('alerts.html')

@app.route('/settings')
def settings_page():
    return app.send_static_file('settings.html')

@app.route('/api')
def api_index():
    return jsonify({"message": "USB Log Monitoring and Intrusion Detection System API"})

@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(devices)

@app.route('/api/scans', methods=['GET'])
def get_scans():
    return jsonify(scans)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify(alerts)

# API route to change device permissions
@app.route('/api/devices/<int:device_id>/permissions', methods=['POST'])
def update_device_permissions(device_id):
    data = request.json
    permission_status = data.get('permission_status')

    for device in devices:
        if device['id'] == device_id:
            device['permission_status'] = permission_status
            device['is_permitted'] = permission_status != 'Blocked'

            # Add a new alert for permission change
            new_alert = {
                "id": len(alerts) + 1,
                "device_id": device_id,
                "alert_type": "permission_changed",
                "message": f"Permission changed for {device['product_name']}: {permission_status}",
                "timestamp": datetime.datetime.now().isoformat(),
                "severity": "success" if permission_status != 'Blocked' else "warning"
            }
            alerts.append(new_alert)

            return jsonify({"success": True, "device": device, "alert": new_alert})

    return jsonify({"success": False, "message": "Device not found"}), 404

# API route to scan a device
@app.route('/api/devices/<int:device_id>/scan', methods=['POST'])
def scan_device(device_id):
    for device in devices:
        if device['id'] == device_id:
            scan_result, alert = scan_usb_device(device)
            return jsonify({
                "success": True,
                "scan": scan_result,
                "device": device,
                "alert": alert
            })

    return jsonify({"success": False, "message": "Device not found"}), 404

# Initialize the system
def initialize_system():
    logger.info("Initializing USB Monitoring System...")
    # No demo data - we'll use real USB detection

if __name__ == '__main__':
    # Initialize the system
    initialize_system()

    # Start USB detection thread
    detection_thread = threading.Thread(target=detect_usb_devices)
    detection_thread.daemon = True
    detection_thread.start()

    # Run the Flask app with SocketIO
    logger.info("Starting USB Monitoring System Backend...")
    logger.info("API available at http://localhost:5000/")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
