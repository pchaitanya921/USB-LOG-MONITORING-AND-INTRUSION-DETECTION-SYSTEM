from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import subprocess
import time
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("usb_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("USB_Server")

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

# Function to run the USB detection script
def run_usb_detection():
    try:
        result = subprocess.run(["python", "detect_usb_devices.py"], capture_output=True, text=True)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                logger.error(f"Error parsing USB detection output: {result.stdout}")
        else:
            logger.error(f"Error running USB detection script: {result.stderr}")
    except Exception as e:
        logger.error(f"Exception running USB detection: {e}")
    
    return []

# USB detection thread
def detect_usb_devices():
    global devices, device_id_counter, alert_id_counter
    
    logger.info("Starting USB detection thread")
    
    while True:
        try:
            # Get current USB devices
            current_devices_raw = run_usb_detection()
            current_devices = {}
            
            for device_raw in current_devices_raw:
                device_id = device_raw.get('id', '')
                if not device_id:
                    continue
                
                current_devices[device_id] = device_raw
                
                # Check if this is a new device
                existing_device = next((d for d in devices if d.get('device_id') == device_id), None)
                
                if not existing_device:
                    logger.info(f"New USB device detected: {device_raw.get('name')} at {device_raw.get('drive_letter', '')}")
                    
                    # Create device object
                    device = {
                        "id": device_id_counter,
                        "device_id": device_id,
                        "product_name": device_raw.get('name', 'Unknown Device'),
                        "manufacturer": device_raw.get('class', 'Unknown'),
                        "serial_number": f"SN{device_id_counter:08d}",
                        "drive_letter": device_raw.get('drive_letter', ''),
                        "is_connected": True,
                        "last_connected": device_raw.get('connection_time', time.strftime("%Y-%m-%d %H:%M:%S")),
                        "status": "read_only",  # Default to read-only
                        "is_permitted": True,
                        "capacity": device_raw.get('capacity', 'Unknown'),
                        "used_space": device_raw.get('used_space', 'Unknown'),
                        "free_space": device_raw.get('free_space', 'Unknown')
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
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_read": False
                    }
                    
                    # Add alert to history
                    alerts.append(alert)
                elif not existing_device['is_connected']:
                    # Device was reconnected
                    existing_device['is_connected'] = True
                    existing_device['last_connected'] = device_raw.get('connection_time', time.strftime("%Y-%m-%d %H:%M:%S"))
                    
                    # Create alert for reconnection
                    alert_id = alert_id_counter
                    alert_id_counter += 1
                    
                    alert = {
                        "id": alert_id,
                        "device_id": existing_device["id"],
                        "alert_type": "reconnection",
                        "message": f"USB device reconnected: {existing_device['product_name']}",
                        "severity": "info",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_read": False
                    }
                    
                    # Add alert to history
                    alerts.append(alert)
            
            # Check for disconnected devices
            for device in devices:
                device_id = device.get('device_id', '')
                if device['is_connected'] and device_id not in current_devices:
                    logger.info(f"USB device disconnected: {device['product_name']}")
                    
                    device['is_connected'] = False
                    device['last_disconnected'] = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Create alert for disconnection
                    alert_id = alert_id_counter
                    alert_id_counter += 1
                    
                    alert = {
                        "id": alert_id,
                        "device_id": device["id"],
                        "alert_type": "disconnection",
                        "message": f"USB device disconnected: {device['product_name']}",
                        "severity": "info",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_read": False
                    }
                    
                    # Add alert to history
                    alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error in USB detection loop: {e}")
        
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
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
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
    global scan_id_counter, alert_id_counter
    
    for device in devices:
        if device['id'] == device_id:
            # Create scan result
            scan_id = scan_id_counter
            scan_id_counter += 1
            
            # Simulate scan result
            import random
            total_files = random.randint(100, 1000)
            infected_files = random.randint(0, 3) if random.random() < 0.3 else 0
            suspicious_files = random.randint(0, 5) if random.random() < 0.5 else 0
            scan_duration = round(random.uniform(2.0, 15.0), 1)
            
            scan_result = {
                "id": scan_id,
                "device_id": device_id,
                "status": "completed",
                "scan_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_files": total_files,
                "scanned_files": total_files,
                "infected_files": infected_files,
                "suspicious_files": suspicious_files,
                "scan_duration": scan_duration
            }
            
            # Add scan to history
            scans.append(scan_result)
            
            # Create alert based on scan result
            alert_id = alert_id_counter
            alert_id_counter += 1
            
            if infected_files > 0:
                severity = "danger"
                message = f"Scan completed on {device['product_name']} - {infected_files} malicious files detected!"
                device["status"] = "blocked"
                device["is_permitted"] = False
            elif suspicious_files > 0:
                severity = "warning"
                message = f"Scan completed on {device['product_name']} - {suspicious_files} suspicious files detected"
                device["status"] = "read_only"
                device["is_permitted"] = True
            else:
                severity = "success"
                message = f"Scan completed on {device['product_name']} - No threats detected"
                device["status"] = "read_only"
                device["is_permitted"] = True
            
            alert = {
                "id": alert_id,
                "device_id": device_id,
                "scan_id": scan_id,
                "alert_type": "scan_result",
                "message": message,
                "severity": severity,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "is_read": False
            }
            
            # Add alert to history
            alerts.append(alert)
            
            return jsonify({
                "success": True,
                "scan": scan_result,
                "device": device,
                "alert": alert
            })
    
    return jsonify({"success": False, "message": "Device not found"}), 404

if __name__ == '__main__':
    # Start USB detection thread
    detection_thread = threading.Thread(target=detect_usb_devices)
    detection_thread.daemon = True
    detection_thread.start()
    
    # Run the Flask app
    logger.info("Starting USB Monitoring System Server...")
    logger.info("API available at http://localhost:5000/")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
