import os
import sys
import time
import json
import logging
import datetime
import subprocess
import threading
import re
import hashlib
import platform
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

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

# Email configuration
EMAIL_USERNAME = "chaitanyasai9391@gmail.com"
EMAIL_PASSWORD = "vvkdquyanoswsvso"  # App password, not actual password
EMAIL_RECIPIENT = "chaitanyasai401@gmail.com"

# SMS configuration (using Twilio API)
SMS_ENABLED = False  # Set to True if you have Twilio credentials
try:
    from twilio.rest import Client
    TWILIO_ACCOUNT_SID = "AC94656f2081ae1c98c4cece8dd68ca056"
    TWILIO_AUTH_TOKEN = "70cfd6672bc72163dd2077bc3562ffa9"
    TWILIO_PHONE_NUMBER = "+19082631380"
    ALERT_RECIPIENT_PHONE = "+919944273645"
    SMS_ENABLED = True
except ImportError:
    logger.warning("Twilio not installed. SMS notifications disabled.")

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for all routes

# In-memory storage
devices = []
scans = []
alerts = []
device_id_counter = 1
scan_id_counter = 1
alert_id_counter = 1

# Known malicious file signatures (MD5 hashes)
MALICIOUS_HASHES = [
    "e44e35d5e0a9b55f44a2bb217698eab8",  # EICAR test file
    "44d88612fea8a8f36de82e1278abb02f",  # EICAR test file (another variant)
]

# File extensions that are potentially malicious
MALICIOUS_EXTENSIONS = [
    '.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar', '.py', '.sh'
]

# File extensions that are potentially suspicious
SUSPICIOUS_EXTENSIONS = [
    '.msi', '.reg', '.scr', '.com', '.pif', '.hta', '.cpl', '.msc', '.jse', '.vbe', '.wsf', '.wsh'
]

# Get USB drives based on operating system
def get_connected_usb_drives():
    """Get all connected USB drives"""
    system = platform.system()
    drives = []
    
    try:
        if system == "Windows":
            # Windows implementation
            import win32file
            import win32api
            
            drive_types = {
                0: "Unknown",
                1: "No Root Directory",
                2: "Removable Disk",
                3: "Local Disk",
                4: "Network Drive",
                5: "Compact Disc",
                6: "RAM Disk"
            }
            
            drive_letters = win32api.GetLogicalDriveStrings().split('\000')[:-1]
            
            for letter in drive_letters:
                try:
                    drive_type = win32file.GetDriveType(letter)
                    if drive_type == 2:  # Removable disk
                        try:
                            volume_name = win32api.GetVolumeInformation(letter)[0]
                            total_bytes = win32file.GetDiskFreeSpaceEx(letter)[1]
                            free_bytes = win32file.GetDiskFreeSpaceEx(letter)[2]
                            used_bytes = total_bytes - free_bytes
                            
                            # Format sizes
                            total_gb = total_bytes / (1024**3)
                            used_gb = used_bytes / (1024**3)
                            free_gb = free_bytes / (1024**3)
                            
                            # Get device details
                            device_info = {
                                "drive_letter": letter,
                                "volume_name": volume_name if volume_name else "USB Drive",
                                "total_space": f"{total_gb:.2f} GB",
                                "used_space": f"{used_gb:.2f} GB",
                                "free_space": f"{free_gb:.2f} GB",
                                "capacity": f"{total_gb:.2f} GB"
                            }
                            
                            drives.append(device_info)
                        except Exception as e:
                            logger.error(f"Error getting drive info for {letter}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing drive {letter}: {str(e)}")
                    
        elif system == "Linux":
            # Linux implementation
            try:
                # Get list of mounted devices
                with open('/proc/mounts', 'r') as f:
                    mounts = f.readlines()
                
                for mount in mounts:
                    parts = mount.split()
                    if len(parts) >= 2:
                        device_path = parts[0]
                        mount_point = parts[1]
                        
                        # Check if it's a removable device (USB)
                        if device_path.startswith('/dev/sd') and not mount_point.startswith('/boot'):
                            try:
                                # Get device information
                                df_output = subprocess.check_output(['df', '-h', mount_point]).decode('utf-8')
                                df_lines = df_output.strip().split('\n')
                                if len(df_lines) >= 2:
                                    df_parts = df_lines[1].split()
                                    if len(df_parts) >= 5:
                                        total_space = df_parts[1]
                                        used_space = df_parts[2]
                                        free_space = df_parts[3]
                                        
                                        # Try to get volume name
                                        volume_name = "USB Drive"
                                        try:
                                            lsblk_output = subprocess.check_output(['lsblk', '-o', 'LABEL', device_path]).decode('utf-8')
                                            lsblk_lines = lsblk_output.strip().split('\n')
                                            if len(lsblk_lines) >= 2 and lsblk_lines[1].strip():
                                                volume_name = lsblk_lines[1].strip()
                                        except:
                                            pass
                                        
                                        device_info = {
                                            "drive_letter": device_path,
                                            "mount_point": mount_point,
                                            "volume_name": volume_name,
                                            "total_space": total_space,
                                            "used_space": used_space,
                                            "free_space": free_space,
                                            "capacity": total_space
                                        }
                                        
                                        drives.append(device_info)
                            except Exception as e:
                                logger.error(f"Error getting info for {mount_point}: {str(e)}")
            except Exception as e:
                logger.error(f"Error reading mounts: {str(e)}")
                
        elif system == "Darwin":  # macOS
            # macOS implementation
            try:
                # Get list of volumes
                df_output = subprocess.check_output(['df', '-h']).decode('utf-8')
                df_lines = df_output.strip().split('\n')
                
                for line in df_lines[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 6:
                        device_path = parts[0]
                        mount_point = parts[5]
                        
                        # Check if it's a removable device (USB)
                        if device_path.startswith('/dev/disk') and mount_point.startswith('/Volumes/'):
                            try:
                                # Get device information
                                total_space = parts[1]
                                used_space = parts[2]
                                free_space = parts[3]
                                
                                # Get volume name from mount point
                                volume_name = os.path.basename(mount_point)
                                
                                device_info = {
                                    "drive_letter": device_path,
                                    "mount_point": mount_point,
                                    "volume_name": volume_name,
                                    "total_space": total_space,
                                    "used_space": used_space,
                                    "free_space": free_space,
                                    "capacity": total_space
                                }
                                
                                drives.append(device_info)
                            except Exception as e:
                                logger.error(f"Error getting info for {mount_point}: {str(e)}")
            except Exception as e:
                logger.error(f"Error getting volumes: {str(e)}")
    except Exception as e:
        logger.error(f"Error detecting USB drives: {str(e)}")
    
    return drives

# Send email alert
def send_email_alert(subject, message):
    """Send an email alert"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email alert sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email alert: {str(e)}")
        return False

# Send SMS alert
def send_sms_alert(message):
    """Send an SMS alert using Twilio"""
    if not SMS_ENABLED:
        logger.warning("SMS notifications disabled. Skipping SMS alert.")
        return False
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=ALERT_RECIPIENT_PHONE
        )
        
        logger.info(f"SMS alert sent: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS alert: {str(e)}")
        return False

# Calculate MD5 hash of a file
def calculate_md5(file_path):
    """Calculate MD5 hash of a file"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating MD5 for {file_path}: {str(e)}")
        return None

# Scan a USB device for malicious files
def scan_usb_device(device):
    """Scan a USB device for malicious files"""
    global scan_id_counter, alert_id_counter
    
    logger.info(f"Scanning device: {device['volume_name']} at {device.get('mount_point', device.get('drive_letter', ''))}")
    
    # Create scan result
    scan_id = scan_id_counter
    scan_id_counter += 1
    
    scan_result = {
        "id": scan_id,
        "device_id": device["id"],
        "status": "in_progress",
        "scan_date": datetime.datetime.now().isoformat(),
        "total_files": 0,
        "scanned_files": 0,
        "infected_files": 0,
        "suspicious_files": 0,
        "malicious_file_paths": [],
        "suspicious_file_paths": [],
        "scan_duration": 0
    }
    
    # Add scan to history
    scans.append(scan_result)
    
    # Get drive path
    drive_path = device.get('mount_point', device.get('drive_letter', ''))
    if not drive_path:
        logger.error(f"No valid drive path for device {device['id']}")
        scan_result["status"] = "error"
        scan_result["error"] = "No valid drive path"
        return scan_result, None
    
    start_time = time.time()
    infected_files = []
    suspicious_files = []
    
    try:
        # Count files first
        total_files = 0
        for root, _, files in os.walk(drive_path):
            total_files += len(files)
            # Limit file count to prevent excessive scanning
            if total_files > 10000:
                break
        
        scan_result["total_files"] = total_files
        
        # Scan files
        scanned_files = 0
        for root, _, files in os.walk(drive_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Update scan progress
                scanned_files += 1
                scan_result["scanned_files"] = scanned_files
                
                try:
                    # Check file extension
                    if file_ext in MALICIOUS_EXTENSIONS:
                        # For potentially malicious extensions, check hash
                        file_hash = calculate_md5(file_path)
                        if file_hash in MALICIOUS_HASHES:
                            infected_files.append(file_path)
                        elif file_ext in ['.exe', '.dll', '.bat', '.cmd']:
                            # These are higher risk, so mark as suspicious
                            suspicious_files.append(file_path)
                    elif file_ext in SUSPICIOUS_EXTENSIONS:
                        suspicious_files.append(file_path)
                except Exception as e:
                    logger.error(f"Error scanning file {file_path}: {str(e)}")
                
                # Limit scanning to prevent excessive time
                if len(infected_files) + len(suspicious_files) > 100:
                    break
            
            # Check if we've hit limits
            if scanned_files >= total_files or len(infected_files) + len(suspicious_files) > 100:
                break
    except Exception as e:
        logger.error(f"Error scanning device: {str(e)}")
        scan_result["status"] = "error"
        scan_result["error"] = str(e)
        scan_duration = time.time() - start_time
        scan_result["scan_duration"] = round(scan_duration, 1)
        return scan_result, None
    
    # Calculate scan duration
    scan_duration = time.time() - start_time
    scan_result["scan_duration"] = round(scan_duration, 1)
    scan_result["infected_files"] = len(infected_files)
    scan_result["suspicious_files"] = len(suspicious_files)
    scan_result["malicious_file_paths"] = infected_files
    scan_result["suspicious_file_paths"] = suspicious_files
    scan_result["status"] = "completed"
    
    # Create alert if needed
    alert = None
    if infected_files:
        severity = "danger"
        message = f"Malicious files detected on {device['volume_name']}. Device set to blocked."
        device["status"] = "blocked"
        device["is_permitted"] = False
        
        # Send alerts
        email_subject = "ALERT: Malicious USB Detected"
        email_message = f"A malicious USB device has been detected.\n\n" \
                        f"Device: {device['volume_name']}\n" \
                        f"Drive: {drive_path}\n" \
                        f"Malicious Files: {len(infected_files)}\n" \
                        f"Suspicious Files: {len(suspicious_files)}\n\n" \
                        f"The device has been blocked for security."
        
        send_email_alert(email_subject, email_message)
        send_sms_alert(f"Malicious USB detected: {device['volume_name']} with {len(infected_files)} malicious files. Device blocked.")
    elif suspicious_files:
        severity = "warning"
        message = f"Suspicious files detected on {device['volume_name']}. Device set to read-only."
        device["status"] = "read_only"
        device["is_permitted"] = True
        
        # Send alerts
        email_subject = "WARNING: Suspicious USB Detected"
        email_message = f"A suspicious USB device has been detected.\n\n" \
                        f"Device: {device['volume_name']}\n" \
                        f"Drive: {drive_path}\n" \
                        f"Suspicious Files: {len(suspicious_files)}\n\n" \
                        f"The device has been set to read-only mode for safety."
        
        send_email_alert(email_subject, email_message)
        send_sms_alert(f"Suspicious USB detected: {device['volume_name']} with {len(suspicious_files)} suspicious files. Set to read-only.")
    else:
        severity = "success"
        message = f"No threats detected on {device['volume_name']}. Device set to read-only."
        device["status"] = "read_only"
        device["is_permitted"] = True
        
        # Send notification
        email_subject = "NOTIFICATION: Secured USB Connected"
        email_message = f"A secured USB device has been connected.\n\n" \
                        f"Device: {device['volume_name']}\n" \
                        f"Drive: {drive_path}\n\n" \
                        f"No threats were detected. The device has been set to Read Only mode by default."
        
        send_email_alert(email_subject, email_message)
        send_sms_alert(f"Secured USB connected: {device['volume_name']}. No threats detected.")
    
    # Create alert
    alert_id = alert_id_counter
    alert_id_counter += 1
    
    alert = {
        "id": alert_id,
        "device_id": device["id"],
        "scan_id": scan_id,
        "alert_type": "scan_result",
        "message": message,
        "severity": severity,
        "timestamp": datetime.datetime.now().isoformat(),
        "is_read": False
    }
    
    # Add alert to history
    alerts.append(alert)
    
    return scan_result, alert

# USB detection thread
def detect_usb_devices():
    """Thread to detect USB devices"""
    global device_id_counter, alert_id_counter
    
    logger.info("Starting USB detection thread")
    last_devices = {}
    
    while True:
        try:
            # Get current USB drives
            current_drives = get_connected_usb_drives()
            current_devices = {}
            
            for drive in current_drives:
                drive_id = drive.get('drive_letter', '')
                if not drive_id:
                    continue
                
                current_devices[drive_id] = drive
                
                # Check if this is a new device
                if drive_id not in last_devices:
                    logger.info(f"New USB device detected: {drive['volume_name']} at {drive_id}")
                    
                    # Create device object
                    device = {
                        "id": device_id_counter,
                        "device_id": f"USB_{device_id_counter}",
                        "product_name": drive['volume_name'],
                        "manufacturer": "Unknown",
                        "serial_number": f"SN{device_id_counter:08d}",
                        "mount_point": drive.get('mount_point', drive.get('drive_letter', '')),
                        "is_connected": True,
                        "last_connected": datetime.datetime.now().isoformat(),
                        "status": "read_only",  # Default to read-only
                        "is_permitted": True,
                        "capacity": drive.get('capacity', 'Unknown'),
                        "used_space": drive.get('used_space', 'Unknown'),
                        "free_space": drive.get('free_space', 'Unknown'),
                        "drive_letter": drive.get('drive_letter', '')
                    }
                    
                    device_id_counter += 1
                    
                    # Add to devices list
                    devices.append(device)
                    
                    # Create alert for new device
                    alert_id = alert_id_counter
                    alert_id_counter += 1
                    
                    alert = {
                        "id": alert_id,
                        "device_id": device["id"],
                        "alert_type": "new_connection",
                        "message": f"New USB device connected: {device['product_name']}. Set to read-only mode.",
                        "severity": "info",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "is_read": False
                    }
                    
                    # Add alert to history
                    alerts.append(alert)
                    
                    # Send notification
                    email_subject = "NOTIFICATION: New USB Connected"
                    email_message = f"A new USB device has been connected.\n\n" \
                                    f"Device: {device['product_name']}\n" \
                                    f"Drive: {device['mount_point']}\n\n" \
                                    f"The device has been set to Read Only mode by default."
                    
                    send_email_alert(email_subject, email_message)
                    send_sms_alert(f"New USB connected: {device['product_name']}. Set to read-only mode.")
                    
                    # Auto-scan the device
                    scan_result, scan_alert = scan_usb_device(device)
            
            # Check for disconnected devices
            for drive_id, device_info in last_devices.items():
                if drive_id not in current_devices:
                    logger.info(f"USB device disconnected: {drive_id}")
                    
                    # Find the device in our list
                    for device in devices:
                        if device.get('drive_letter') == drive_id and device['is_connected']:
                            device['is_connected'] = False
                            device['last_disconnected'] = datetime.datetime.now().isoformat()
                            
                            # Create alert for disconnection
                            alert_id = alert_id_counter
                            alert_id_counter += 1
                            
                            alert = {
                                "id": alert_id,
                                "device_id": device["id"],
                                "alert_type": "disconnection",
                                "message": f"USB device disconnected: {device['product_name']}",
                                "severity": "info",
                                "timestamp": datetime.datetime.now().isoformat(),
                                "is_read": False
                            }
                            
                            # Add alert to history
                            alerts.append(alert)
                            break
            
            # Update last devices
            last_devices = current_devices
            
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
    
    if not permission_status:
        return jsonify({"success": False, "message": "Permission status is required"}), 400
    
    for device in devices:
        if device['id'] == device_id:
            device['status'] = permission_status
            
            if permission_status == 'blocked':
                device['is_permitted'] = False
            else:
                device['is_permitted'] = True
            
            # Create alert for permission change
            global alert_id_counter
            alert_id = alert_id_counter
            alert_id_counter += 1
            
            alert = {
                "id": alert_id,
                "device_id": device_id,
                "alert_type": "permission_change",
                "message": f"Device permission changed: {device['product_name']} set to {permission_status}",
                "severity": "info",
                "timestamp": datetime.datetime.now().isoformat(),
                "is_read": False
            }
            
            # Add alert to history
            alerts.append(alert)
            
            return jsonify({
                "success": True,
                "device": device,
                "alert": alert
            })
    
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

if __name__ == '__main__':
    # Initialize the system
    initialize_system()
    
    # Start USB detection thread
    detection_thread = threading.Thread(target=detect_usb_devices)
    detection_thread.daemon = True
    detection_thread.start()
    
    # Run the Flask app
    logger.info("Starting USB Monitoring System Backend...")
    logger.info("API available at http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
