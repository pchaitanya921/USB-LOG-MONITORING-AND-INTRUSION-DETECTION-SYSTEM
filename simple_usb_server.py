from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import subprocess
import time
import datetime
import platform
import random

# Initialize Flask app
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # Enable CORS for all routes

# In-memory storage
devices = []
scans = []
alerts = []

# Initialize with some demo data
def initialize_demo_data():
    global devices, scans, alerts
    
    # Demo devices
    devices = [
        {
            "id": 1,
            "device_id": "USB_DEVICE_1",
            "product_name": "Kingston DataTraveler 3.0",
            "manufacturer": "Kingston",
            "serial_number": "KT12345678",
            "drive_letter": "E:",
            "is_connected": True,
            "last_connected": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "read_only",
            "is_permitted": True,
            "capacity": "16 GB",
            "used_space": "4.2 GB",
            "free_space": "11.8 GB"
        },
        {
            "id": 2,
            "device_id": "USB_DEVICE_2",
            "product_name": "SanDisk Ultra",
            "manufacturer": "SanDisk",
            "serial_number": "SDCZ48-032G",
            "drive_letter": "F:",
            "is_connected": True,
            "last_connected": (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "blocked",
            "is_permitted": False,
            "capacity": "32 GB",
            "used_space": "12.7 GB",
            "free_space": "19.3 GB"
        }
    ]
    
    # Demo scans
    scans = [
        {
            "id": 1,
            "device_id": 1,
            "status": "completed",
            "scan_date": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": 1245,
            "scanned_files": 1245,
            "infected_files": 0,
            "suspicious_files": 3,
            "scan_duration": 12.5
        },
        {
            "id": 2,
            "device_id": 2,
            "status": "completed",
            "scan_date": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": 567,
            "scanned_files": 567,
            "infected_files": 2,
            "suspicious_files": 0,
            "scan_duration": 8.2
        }
    ]
    
    # Demo alerts
    alerts = [
        {
            "id": 1,
            "device_id": 1,
            "alert_type": "new_connection",
            "message": f"New USB device connected: Kingston DataTraveler 3.0. Set to read-only mode.",
            "severity": "info",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": False
        },
        {
            "id": 2,
            "device_id": 1,
            "scan_id": 1,
            "alert_type": "scan_result",
            "message": f"Scan completed on Kingston DataTraveler 3.0 - 3 suspicious files detected",
            "severity": "warning",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": False
        },
        {
            "id": 3,
            "device_id": 2,
            "alert_type": "new_connection",
            "message": f"New USB device connected: SanDisk Ultra. Set to read-only mode.",
            "severity": "info",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": False
        },
        {
            "id": 4,
            "device_id": 2,
            "scan_id": 2,
            "alert_type": "scan_result",
            "message": f"Scan completed on SanDisk Ultra - 2 malicious files detected!",
            "severity": "danger",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": False
        }
    ]

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
    # Simulate real-time changes
    simulate_device_changes()
    return jsonify(devices)

@app.route('/api/scans', methods=['GET'])
def get_scans():
    return jsonify(scans)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    return jsonify(alerts)

# Simulate real-time device changes
def simulate_device_changes():
    global devices, alerts
    
    # Randomly connect/disconnect devices
    if random.random() < 0.1:  # 10% chance of a device change
        for device in devices:
            if random.random() < 0.5:  # 50% chance to toggle connection state
                old_state = device["is_connected"]
                device["is_connected"] = not old_state
                
                if device["is_connected"]:  # Device was reconnected
                    device["last_connected"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Create alert for reconnection
                    alert_id = len(alerts) + 1
                    
                    alert = {
                        "id": alert_id,
                        "device_id": device["id"],
                        "alert_type": "reconnection",
                        "message": f"USB device reconnected: {device['product_name']}",
                        "severity": "info",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "is_read": False
                    }
                    
                    # Add alert to history
                    alerts.append(alert)
                else:  # Device was disconnected
                    # Create alert for disconnection
                    alert_id = len(alerts) + 1
                    
                    alert = {
                        "id": alert_id,
                        "device_id": device["id"],
                        "alert_type": "disconnection",
                        "message": f"USB device disconnected: {device['product_name']}",
                        "severity": "info",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "is_read": False
                    }
                    
                    # Add alert to history
                    alerts.append(alert)

if __name__ == '__main__':
    # Initialize demo data
    initialize_demo_data()
    
    # Run the Flask app
    print("Starting USB Monitoring System Server...")
    print("API available at http://localhost:5000/")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
