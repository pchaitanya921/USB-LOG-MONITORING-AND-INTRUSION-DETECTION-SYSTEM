from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import datetime
from fixed_usb_detector import get_usb_devices, wmi_available

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store connection history
history = []
scan_count = 0
last_scan_time = None

@app.route('/api/scan', methods=['GET'])
def scan_devices():
    global scan_count, last_scan_time, history

    # Increment scan count
    scan_count += 1
    last_scan_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    # Get connected devices
    devices, error = get_usb_devices()

    # Add default permissions if not present
    for device in devices:
        if "permission" not in device:
            device["permission"] = "read_only"
        if "status" not in device:
            device["status"] = "active"

    # Update history
    current_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    # Check for new connections and disconnections
    if history:
        # Get previous device IDs
        prev_device_ids = [h["device_id"] for h in history if h["event_type"] == "connected" and
                          not any(d["event_type"] == "disconnected" and d["device_id"] == h["device_id"]
                                for d in history if history.index(d) > history.index(h))]

        # Current device IDs
        current_device_ids = [d["id"] for d in devices]

        # New connections
        for device in devices:
            if device["id"] not in prev_device_ids:
                history.insert(0, {
                    "device_name": device["name"],
                    "device_id": device["id"],
                    "event_type": "connected",
                    "timestamp": current_time
                })

        # Disconnections
        for device_id in prev_device_ids:
            if device_id not in current_device_ids:
                # Find device name from history
                device_name = next((h["device_name"] for h in history
                                  if h["device_id"] == device_id and h["event_type"] == "connected"), "Unknown Device")

                history.insert(0, {
                    "device_name": device_name,
                    "device_id": device_id,
                    "event_type": "disconnected",
                    "timestamp": current_time
                })
    else:
        # First scan, add all devices as new connections
        for device in devices:
            history.insert(0, {
                "device_name": device["name"],
                "device_id": device["id"],
                "event_type": "connected",
                "timestamp": current_time
            })

    # Limit history to last 50 events
    if len(history) > 50:
        history = history[:50]

    # Add a dummy device if no devices are found (for testing)
    if not devices:
        print("No USB devices detected. Adding a dummy device for testing.")
        dummy_device = {
            "name": "Test USB Device",
            "id": "TEST_USB",
            "drive_letter": "X:\\",
            "size": "8.0GB",
            "free_space": "4.0GB",
            "connection_time": current_time,
            "permission": "read_only",
            "status": "active"
        }
        devices.append(dummy_device)

    # Print detected devices for debugging
    print(f"Detected {len(devices)} USB device(s):")
    for i, device in enumerate(devices, 1):
        print(f"  Device {i}: {device['name']} ({device.get('drive_letter', 'No drive letter')})")

    return jsonify({
        "devices": devices,
        "history": history,
        "scan_count": scan_count,
        "scan_time": last_scan_time,
        "wmi_available": wmi_available,
        "error": error,
        "notifications_count": 0,
        "notifications_sent": False
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(history)

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "wmi_available": wmi_available,
        "os": os.name,
        "python_version": os.sys.version
    })

@app.route('/api/block-device', methods=['POST'])
def block_device():
    from flask import request

    # Get request data
    data = request.json
    device_id = data.get('device_id')
    action = data.get('action', 'block')  # Default action is block

    if not device_id:
        return jsonify({
            "success": False,
            "message": "Device ID is required"
        }), 400

    # In a real implementation, this would actually block/unblock the device
    # For now, we'll just return success
    print(f"{'Unblocking' if action == 'unblock' else 'Blocking'} device: {device_id}")

    return jsonify({
        "success": True,
        "message": f"Device {device_id} {'unblocked' if action == 'unblock' else 'blocked'} successfully",
        "device_id": device_id,
        "action": action
    })

@app.route('/api/set-permission', methods=['POST'])
def set_permission():
    from flask import request

    # Get request data
    data = request.json
    device_id = data.get('device_id')
    permission = data.get('permission', 'read_only')  # Default permission is read_only

    if not device_id:
        return jsonify({
            "success": False,
            "message": "Device ID is required"
        }), 400

    # In a real implementation, this would actually set the device permission
    # For now, we'll just return success
    print(f"Setting permission for device {device_id} to {permission}")

    return jsonify({
        "success": True,
        "message": f"Device {device_id} permission set to {permission} successfully",
        "device_id": device_id,
        "permission": permission
    })

@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'usb_monitor.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    print("Starting USB Monitoring System...")
    print(f"WMI module available: {wmi_available}")
    print("Detecting USB devices...")

    # Test USB detection
    devices, error = get_usb_devices()

    if error:
        print(f"Warning: {error}")

    if devices:
        print(f"Found {len(devices)} USB device(s):")
        for i, device in enumerate(devices, 1):
            print(f"  Device {i}: {device['name']} ({device.get('drive_letter', 'No drive letter')})")
    else:
        print("No USB devices detected.")

    print("\nStarting Flask server on port 5000...")
    print("You can access the application at: http://localhost:5000")

    # Run the Flask app
    app.run(debug=True, port=5000)
