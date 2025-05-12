import os
import sys
import time
import json
import logging
import hashlib
import threading
import platform
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger("USB_Scanner")

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
connected_devices = {}
last_scan_results = {}

# Potentially malicious file extensions
MALICIOUS_EXTENSIONS = {
    '.exe', '.dll', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.vbe', '.js', 
    '.jse', '.wsf', '.wsh', '.msc', '.jar', '.ps1', '.reg', '.msi', '.msp', '.hta'
}

# Suspicious file extensions
SUSPICIOUS_EXTENSIONS = {
    '.zip', '.rar', '.7z', '.tar', '.gz', '.iso', '.bin', '.dat', '.db', '.sql',
    '.apk', '.app', '.dmg', '.sys', '.tmp', '.crx', '.xpi'
}

# Known malicious file hashes (MD5) - you would update this with a real database
KNOWN_MALICIOUS_HASHES = {
    '5f4dcc3b5aa765d61d8327deb882cf99',  # Example hash
    'e10adc3949ba59abbe56e057f20f883e',  # Example hash
    '25f9e794323b453885f5181f1b624d0b'   # Example hash
}

def get_drive_type(drive_path):
    """Determine if a drive is removable (likely a USB drive)"""
    if platform.system() == 'Windows':
        import win32file
        drive_type = win32file.GetDriveType(drive_path)
        return drive_type == win32file.DRIVE_REMOVABLE
    elif platform.system() == 'Linux':
        # On Linux, USB drives are typically mounted in /media or /mnt
        return '/media/' in drive_path or '/mnt/' in drive_path
    elif platform.system() == 'Darwin':  # macOS
        # On macOS, USB drives are typically mounted in /Volumes
        return '/Volumes/' in drive_path and drive_path != '/Volumes/Macintosh HD'
    return False

def get_connected_usb_drives():
    """Get all connected USB drives"""
    drives = {}
    
    if platform.system() == 'Windows':
        import win32api
        import wmi
        
        # Get drive letters
        drive_letters = win32api.GetLogicalDriveStrings().split('\000')[:-1]
        
        # Filter for removable drives
        for drive in drive_letters:
            if get_drive_type(drive):
                try:
                    # Get drive information using WMI
                    c = wmi.WMI()
                    for disk in c.Win32_DiskDrive():
                        for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                                if logical_disk.Caption == drive[0]:
                                    drive_info = {
                                        'device_id': disk.DeviceID.replace('\\', '_').replace('.', '_'),
                                        'product_name': disk.Model or 'Unknown Device',
                                        'manufacturer': disk.Manufacturer or 'Unknown',
                                        'serial_number': disk.SerialNumber or 'Unknown',
                                        'mount_point': drive,
                                        'capacity': f"{int(logical_disk.Size) // (1024**3)} GB",
                                        'free_space': f"{int(logical_disk.FreeSpace) // (1024**3)} GB",
                                        'used_space': f"{(int(logical_disk.Size) - int(logical_disk.FreeSpace)) // (1024**3)} GB",
                                        'is_connected': True,
                                        'last_connected': datetime.now().isoformat(),
                                        'status': 'read_only',  # Default to read-only
                                        'has_threats': False
                                    }
                                    drives[drive_info['device_id']] = drive_info
                except Exception as e:
                    logger.error(f"Error getting drive info: {e}")
    
    elif platform.system() == 'Linux':
        # On Linux, check /proc/mounts for USB drives
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) > 1:
                        device, mount_point = parts[0], parts[1]
                        if get_drive_type(mount_point):
                            # Get drive information
                            drive_info = {
                                'device_id': device.replace('/', '_'),
                                'product_name': os.path.basename(device) or 'USB Drive',
                                'manufacturer': 'Unknown',
                                'serial_number': 'Unknown',
                                'mount_point': mount_point,
                                'capacity': 'Unknown',
                                'free_space': 'Unknown',
                                'used_space': 'Unknown',
                                'is_connected': True,
                                'last_connected': datetime.now().isoformat(),
                                'status': 'read_only',  # Default to read-only
                                'has_threats': False
                            }
                            
                            # Try to get more detailed information
                            try:
                                import subprocess
                                result = subprocess.run(['df', '-h', mount_point], capture_output=True, text=True)
                                if result.returncode == 0:
                                    lines = result.stdout.strip().split('\n')
                                    if len(lines) > 1:
                                        parts = lines[1].split()
                                        if len(parts) >= 4:
                                            drive_info['capacity'] = parts[1]
                                            drive_info['used_space'] = parts[2]
                                            drive_info['free_space'] = parts[3]
                            except Exception as e:
                                logger.error(f"Error getting drive details: {e}")
                                
                            drives[drive_info['device_id']] = drive_info
        except Exception as e:
            logger.error(f"Error reading mounts: {e}")
    
    elif platform.system() == 'Darwin':  # macOS
        # On macOS, check /Volumes for USB drives
        try:
            volumes = os.listdir('/Volumes')
            for volume in volumes:
                mount_point = f"/Volumes/{volume}"
                if volume != 'Macintosh HD' and os.path.ismount(mount_point):
                    # Get drive information
                    drive_info = {
                        'device_id': volume.replace(' ', '_'),
                        'product_name': volume,
                        'manufacturer': 'Unknown',
                        'serial_number': 'Unknown',
                        'mount_point': mount_point,
                        'capacity': 'Unknown',
                        'free_space': 'Unknown',
                        'used_space': 'Unknown',
                        'is_connected': True,
                        'last_connected': datetime.now().isoformat(),
                        'status': 'read_only',  # Default to read-only
                        'has_threats': False
                    }
                    
                    # Try to get more detailed information
                    try:
                        import subprocess
                        result = subprocess.run(['df', '-h', mount_point], capture_output=True, text=True)
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                parts = lines[1].split()
                                if len(parts) >= 4:
                                    drive_info['capacity'] = parts[1]
                                    drive_info['used_space'] = parts[2]
                                    drive_info['free_space'] = parts[3]
                    except Exception as e:
                        logger.error(f"Error getting drive details: {e}")
                        
                    drives[drive_info['device_id']] = drive_info
        except Exception as e:
            logger.error(f"Error listing volumes: {e}")
    
    return drives

def calculate_file_hash(file_path):
    """Calculate MD5 hash of a file"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return None

def scan_file(file_path):
    """Scan a single file for threats"""
    try:
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        
        # Check if it's a known malicious file extension
        if ext in MALICIOUS_EXTENSIONS:
            return {
                'status': 'malicious',
                'reason': f"Potentially malicious file extension: {ext}"
            }
        
        # Check if it's a suspicious file extension
        if ext in SUSPICIOUS_EXTENSIONS:
            return {
                'status': 'suspicious',
                'reason': f"Suspicious file extension: {ext}"
            }
        
        # For executable files, check hash against known malicious hashes
        if ext in ['.exe', '.dll', '.sys']:
            file_hash = calculate_file_hash(file_path)
            if file_hash and file_hash in KNOWN_MALICIOUS_HASHES:
                return {
                    'status': 'malicious',
                    'reason': f"File hash matches known malicious hash: {file_hash}"
                }
        
        # File passed all checks
        return {
            'status': 'safe',
            'reason': "No threats detected"
        }
    except Exception as e:
        logger.error(f"Error scanning file {file_path}: {e}")
        return {
            'status': 'error',
            'reason': f"Error scanning file: {str(e)}"
        }

def scan_usb_drive(device_id, mount_point):
    """Scan a USB drive for malicious files"""
    logger.info(f"Starting scan of device {device_id} at {mount_point}")
    
    # Emit scan started event
    socketio.emit('scan_started', {
        'device_id': device_id,
        'device_name': connected_devices[device_id]['product_name'],
        'timestamp': datetime.now().isoformat()
    })
    
    start_time = time.time()
    
    # Initialize scan results
    scan_result = {
        'device_id': device_id,
        'status': 'in_progress',
        'scan_date': datetime.now().isoformat(),
        'total_files': 0,
        'scanned_files': 0,
        'malicious_files': [],
        'suspicious_files': [],
        'scan_duration': 0
    }
    
    try:
        # Count files first
        total_files = 0
        for root, _, files in os.walk(mount_point):
            total_files += len(files)
            # Emit progress update
            if total_files % 100 == 0:
                socketio.emit('scan_progress', {
                    'device_id': device_id,
                    'total_files': total_files,
                    'scanned_files': 0,
                    'status': 'counting',
                    'message': f"Found {total_files} files to scan"
                })
        
        scan_result['total_files'] = total_files
        
        # Emit file count update
        socketio.emit('scan_progress', {
            'device_id': device_id,
            'total_files': total_files,
            'scanned_files': 0,
            'status': 'counting',
            'message': f"Found {total_files} files to scan"
        })
        
        # Scan files
        scanned_files = 0
        for root, _, files in os.walk(mount_point):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Update scan progress
                scanned_files += 1
                percent = int((scanned_files / max(1, total_files)) * 100)
                
                # Emit progress update every 10 files
                if scanned_files % 10 == 0:
                    socketio.emit('scan_progress', {
                        'device_id': device_id,
                        'total_files': total_files,
                        'scanned_files': scanned_files,
                        'percent': percent,
                        'status': 'scanning',
                        'current_file': file_path.replace(mount_point, '')
                    })
                
                # Scan the file
                scan_result['scanned_files'] = scanned_files
                
                try:
                    file_scan_result = scan_file(file_path)
                    
                    if file_scan_result['status'] == 'malicious':
                        scan_result['malicious_files'].append({
                            'file_path': file_path.replace(mount_point, ''),
                            'file_name': os.path.basename(file_path),
                            'reason': file_scan_result['reason']
                        })
                        
                        # Emit malicious file found event
                        socketio.emit('malicious_file_found', {
                            'device_id': device_id,
                            'file_path': file_path.replace(mount_point, ''),
                            'file_name': os.path.basename(file_path),
                            'reason': file_scan_result['reason']
                        })
                    
                    elif file_scan_result['status'] == 'suspicious':
                        scan_result['suspicious_files'].append({
                            'file_path': file_path.replace(mount_point, ''),
                            'file_name': os.path.basename(file_path),
                            'reason': file_scan_result['reason']
                        })
                        
                        # Emit suspicious file found event
                        socketio.emit('suspicious_file_found', {
                            'device_id': device_id,
                            'file_path': file_path.replace(mount_point, ''),
                            'file_name': os.path.basename(file_path),
                            'reason': file_scan_result['reason']
                        })
                except Exception as e:
                    logger.error(f"Error scanning file {file_path}: {e}")
        
        # Calculate scan duration
        scan_duration = round(time.time() - start_time, 1)
        scan_result['scan_duration'] = scan_duration
        scan_result['status'] = 'completed'
        
        # Update device threat status
        if scan_result['malicious_files']:
            connected_devices[device_id]['has_threats'] = True
            connected_devices[device_id]['status'] = 'blocked'
            severity = 'danger'
            message = f"Scan completed on {connected_devices[device_id]['product_name']} - {len(scan_result['malicious_files'])} malicious files detected!"
        elif scan_result['suspicious_files']:
            connected_devices[device_id]['has_threats'] = True
            severity = 'warning'
            message = f"Scan completed on {connected_devices[device_id]['product_name']} - {len(scan_result['suspicious_files'])} suspicious files detected"
        else:
            connected_devices[device_id]['has_threats'] = False
            severity = 'success'
            message = f"Scan completed on {connected_devices[device_id]['product_name']} - No threats detected"
        
        # Store scan result
        last_scan_results[device_id] = scan_result
        
        # Emit scan complete event
        socketio.emit('scan_complete', {
            'device_id': device_id,
            'device_name': connected_devices[device_id]['product_name'],
            'total_files': total_files,
            'scanned_files': scanned_files,
            'infected_files': len(scan_result['malicious_files']),
            'suspicious_files': len(scan_result['suspicious_files']),
            'scan_duration': scan_duration,
            'status': 'complete',
            'result': severity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Scan completed for {connected_devices[device_id]['product_name']}: {message}")
        return scan_result
    
    except Exception as e:
        logger.error(f"Error scanning device {device_id}: {e}")
        
        # Update scan result
        scan_result['status'] = 'error'
        scan_result['scan_duration'] = round(time.time() - start_time, 1)
        scan_result['error'] = str(e)
        
        # Emit scan error event
        socketio.emit('scan_error', {
            'device_id': device_id,
            'error': str(e),
            'status': 'error',
            'message': f"Error scanning device: {str(e)}"
        })
        
        return scan_result

def detect_usb_devices():
    """Continuously detect USB devices"""
    global connected_devices
    
    logger.info("Starting USB detection thread")
    
    while True:
        try:
            # Get currently connected USB drives
            current_devices = get_connected_usb_drives()
            
            # Check for new devices
            for device_id, device_info in current_devices.items():
                if device_id not in connected_devices:
                    logger.info(f"New USB device detected: {device_info['product_name']} at {device_info['mount_point']}")
                    connected_devices[device_id] = device_info
                    
                    # Emit device connected event
                    socketio.emit('usb_connected', {
                        'device': device_info
                    })
            
            # Check for disconnected devices
            disconnected_devices = []
            for device_id in connected_devices:
                if device_id not in current_devices:
                    logger.info(f"USB device disconnected: {connected_devices[device_id]['product_name']}")
                    connected_devices[device_id]['is_connected'] = False
                    
                    # Emit device disconnected event
                    socketio.emit('usb_disconnected', {
                        'device': connected_devices[device_id]
                    })
                    
                    disconnected_devices.append(device_id)
            
            # Remove disconnected devices
            for device_id in disconnected_devices:
                del connected_devices[device_id]
        
        except Exception as e:
            logger.error(f"Error in USB detection loop: {e}")
        
        # Sleep for a short interval before checking again
        time.sleep(3)

# API Routes
@app.route('/')
def index():
    return send_from_directory('.', 'usb-scan-demo.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(list(connected_devices.values()))

@app.route('/api/scan/<device_id>', methods=['POST'])
def start_scan(device_id):
    if device_id in connected_devices and connected_devices[device_id]['is_connected']:
        # Start scan in a background thread
        threading.Thread(
            target=scan_usb_drive,
            args=(device_id, connected_devices[device_id]['mount_point'])
        ).start()
        
        return jsonify({
            "success": True,
            "message": f"Scan started for {connected_devices[device_id]['product_name']}"
        })
    
    return jsonify({
        "success": False,
        "message": "Device not found or not connected"
    }), 404

@app.route('/api/devices/<device_id>/permissions', methods=['POST'])
def update_device_permissions(device_id):
    if device_id in connected_devices:
        data = request.json
        permission_status = data.get('permission_status')
        
        if permission_status in ['read_only', 'full_access', 'blocked']:
            connected_devices[device_id]['status'] = permission_status
            
            return jsonify({
                "success": True,
                "message": f"Device {device_id} set to {permission_status}",
                "device": connected_devices[device_id]
            })
    
    return jsonify({
        "success": False,
        "message": "Device not found or invalid permission status"
    }), 404

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('start_scan')
def handle_start_scan(data):
    device_id = data.get('device_id')
    
    if device_id in connected_devices and connected_devices[device_id]['is_connected']:
        # Start scan in a background thread
        threading.Thread(
            target=scan_usb_drive,
            args=(device_id, connected_devices[device_id]['mount_point'])
        ).start()
        
        return {
            "success": True,
            "message": f"Scan started for {connected_devices[device_id]['product_name']}"
        }
    
    return {
        "success": False,
        "message": "Device not found or not connected"
    }

if __name__ == '__main__':
    # Check for required dependencies
    try:
        if platform.system() == 'Windows':
            import win32api
            import win32file
            import wmi
    except ImportError as e:
        logger.error(f"Missing required dependency: {e}")
        logger.error("On Windows, please install: pip install pywin32 wmi")
        sys.exit(1)
    
    # Start USB detection thread
    detection_thread = threading.Thread(target=detect_usb_devices)
    detection_thread.daemon = True
    detection_thread.start()
    
    # Run the Flask app with SocketIO
    logger.info("Starting USB Scanner Backend...")
    logger.info("Web interface available at http://localhost:5000/")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
