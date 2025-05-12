import os
import sys
import json
import time
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for demo purposes
devices = [
    {
        "id": 1,
        "device_id": "DUMMY_DEVICE_1",
        "vendor_id": "0781",
        "product_id": "5581",
        "manufacturer": "SanDisk",
        "product_name": "Ultra USB 3.0",
        "serial_number": "SDCZ48-032G-123456",
        "mount_point": "E:",
        "is_connected": True,
        "is_permitted": True,
        "permission_status": "Read Only",
        "has_threats": False,
        "first_connected_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        "last_connected_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        "last_scanned_at": (datetime.now() - timedelta(minutes=55)).isoformat()
    },
    {
        "id": 2,
        "device_id": "DUMMY_DEVICE_2",
        "vendor_id": "1234",
        "product_id": "5678",
        "manufacturer": "Kingston",
        "product_name": "DataTraveler 100 G3",
        "serial_number": "KDT100G3-064G-789012",
        "mount_point": "F:",
        "is_connected": True,
        "is_permitted": False,
        "permission_status": "Blocked",
        "has_threats": True,
        "first_connected_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "last_connected_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "last_scanned_at": (datetime.now() - timedelta(minutes=29)).isoformat()
    },
    {
        "id": 3,
        "device_id": "DUMMY_DEVICE_3",
        "vendor_id": "090c",
        "product_id": "1000",
        "manufacturer": "Samsung",
        "product_name": "Flash Drive FIT Plus",
        "serial_number": "SAMSUNG-FIT-345678",
        "mount_point": "G:",
        "is_connected": True,
        "is_permitted": True,
        "permission_status": "Full Access",
        "has_threats": False,
        "first_connected_at": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "last_connected_at": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "last_scanned_at": (datetime.now() - timedelta(minutes=14)).isoformat()
    }
]

scans = [
    {
        "id": 1,
        "device_id": 1,
        "status": "completed",
        "scan_date": (datetime.now() - timedelta(minutes=55)).isoformat(),
        "total_files": 256,
        "scanned_files": 256,
        "infected_files": 0,
        "suspicious_files": 0,
        "scan_duration": 5.3
    },
    {
        "id": 2,
        "device_id": 2,
        "status": "completed",
        "scan_date": (datetime.now() - timedelta(minutes=29)).isoformat(),
        "total_files": 128,
        "scanned_files": 128,
        "infected_files": 3,
        "suspicious_files": 1,
        "scan_duration": 8.2
    },
    {
        "id": 3,
        "device_id": 3,
        "status": "completed",
        "scan_date": (datetime.now() - timedelta(minutes=14)).isoformat(),
        "total_files": 192,
        "scanned_files": 192,
        "infected_files": 0,
        "suspicious_files": 0,
        "scan_duration": 6.7
    }
]

alerts = [
    {
        "id": 1,
        "device_id": 1,
        "alert_type": "new_connection",
        "message": "New USB device connected: SanDisk Ultra USB 3.0. Set to read-only mode.",
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
        "severity": "info"
    },
    {
        "id": 2,
        "device_id": 2,
        "alert_type": "malware_detected",
        "message": "Malware detected on Kingston DataTraveler 100 G3. Device has been blocked.",
        "timestamp": (datetime.now() - timedelta(minutes=29)).isoformat(),
        "severity": "danger"
    },
    {
        "id": 3,
        "device_id": 3,
        "alert_type": "permission_changed",
        "message": "Permission changed for Samsung Flash Drive FIT Plus: Read Only → Full Access",
        "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
        "severity": "success"
    }
]

# API Routes
@app.route('/')
def index():
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
                "timestamp": datetime.now().isoformat(),
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
            # Simulate scanning
            scan_duration = random.uniform(3.0, 10.0)
            total_files = random.randint(100, 500)
            infected_files = 0
            suspicious_files = 0
            
            # If the device has threats, simulate finding them
            if device['has_threats']:
                infected_files = random.randint(1, 5)
                suspicious_files = random.randint(0, 3)
            
            # Create a new scan record
            new_scan = {
                "id": len(scans) + 1,
                "device_id": device_id,
                "status": "completed",
                "scan_date": datetime.now().isoformat(),
                "total_files": total_files,
                "scanned_files": total_files,
                "infected_files": infected_files,
                "suspicious_files": suspicious_files,
                "scan_duration": round(scan_duration, 1)
            }
            scans.append(new_scan)
            
            # Update device last scanned time
            device['last_scanned_at'] = datetime.now().isoformat()
            
            # Create an alert for the scan
            alert_type = "scan_complete"
            message = f"Scan completed on {device['product_name']}"
            severity = "success"
            
            if infected_files > 0:
                alert_type = "malware_detected"
                message += f" - {infected_files} malicious files detected!"
                severity = "danger"
                device['has_threats'] = True
                device['permission_status'] = "Blocked"
                device['is_permitted'] = False
            elif suspicious_files > 0:
                alert_type = "suspicious_detected"
                message += f" - {suspicious_files} suspicious files detected"
                severity = "warning"
            else:
                message += " - No threats detected"
            
            new_alert = {
                "id": len(alerts) + 1,
                "device_id": device_id,
                "alert_type": alert_type,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            }
            alerts.append(new_alert)
            
            return jsonify({
                "success": True, 
                "scan": new_scan, 
                "device": device,
                "alert": new_alert
            })
    
    return jsonify({"success": False, "message": "Device not found"}), 404

# Run the app
if __name__ == '__main__':
    print("Starting USB Monitoring System Backend...")
    print("API available at http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)
