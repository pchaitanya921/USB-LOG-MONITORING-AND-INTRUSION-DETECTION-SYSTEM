import os
import time
import threading
import platform
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Routes for static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

def get_connected_usb_drives():
    """Get all connected USB drives on Windows"""
    drives = {}

    # Get all drive letters
    available_drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]

    for drive in available_drives:
        # Check if it's a removable drive (USB)
        try:
            import win32file
            if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                # Get drive information
                drive_info = {
                    'device_id': f"USB_{drive[0]}",
                    'product_name': f"USB Drive ({drive[0]}:)",
                    'manufacturer': 'Unknown',
                    'serial_number': f"SN_{drive[0]}",
                    'mount_point': drive,
                    'capacity': 'Unknown',
                    'free_space': 'Unknown',
                    'used_space': 'Unknown',
                    'is_connected': True,
                    'last_connected': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    'status': 'read_only',  # Default to read-only
                    'has_threats': False
                }

                # Try to get more detailed information
                try:
                    total, used, free = get_drive_space(drive)
                    drive_info['capacity'] = f"{total} GB"
                    drive_info['free_space'] = f"{free} GB"
                    drive_info['used_space'] = f"{used} GB"

                    # Try to get volume name
                    import win32api
                    volume_info = win32api.GetVolumeInformation(drive)
                    volume_name = volume_info[0]
                    if volume_name:
                        drive_info['product_name'] = f"{volume_name} ({drive[0]}:)"
                except Exception as e:
                    logger.error(f"Error getting drive details: {e}")

                drives[drive_info['device_id']] = drive_info
        except Exception as e:
            logger.error(f"Error checking drive {drive}: {e}")

    return drives

def get_drive_space(drive):
    """Get drive space information"""
    try:
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        total_bytes = ctypes.c_ulonglong(0)
        available_bytes = ctypes.c_ulonglong(0)

        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(drive),
            ctypes.byref(available_bytes),
            ctypes.byref(total_bytes),
            ctypes.byref(free_bytes)
        )

        total_gb = total_bytes.value / (1024**3)
        free_gb = free_bytes.value / (1024**3)
        used_gb = total_gb - free_gb

        return round(total_gb, 1), round(used_gb, 1), round(free_gb, 1)
    except Exception as e:
        logger.error(f"Error getting drive space: {e}")
        return 0, 0, 0

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
        'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    })

    start_time = time.time()

    # Initialize scan results
    scan_result = {
        'device_id': device_id,
        'status': 'in_progress',
        'scan_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'total_files': 0,
        'scanned_files': 0,
        'malicious_files': [],
        'suspicious_files': [],
        'scan_duration': 0
    }

    try:
        # Count files first (limit to 1000 for speed)
        total_files = 0
        for root, _, files in os.walk(mount_point):
            total_files += len(files)
            if total_files >= 1000:  # Limit file count for performance
                break
            # Emit progress update
            if total_files % 50 == 0:
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

                # Limit scan to 1000 files for performance
                if scanned_files >= 1000:
                    break

            # Limit scan to 1000 files for performance
            if scanned_files >= 1000:
                break

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
            'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
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
            for device_id in list(connected_devices.keys()):
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
        time.sleep(2)

# API Routes
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
    logger.info("Starting Simple USB Scanner Server...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
