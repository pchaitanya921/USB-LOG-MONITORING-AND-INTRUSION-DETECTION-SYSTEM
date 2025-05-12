from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import platform
import datetime
import json
import os
import time
import importlib.util
import ctypes
import string
from scanner import USBScanner

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Check if WMI is available
HAS_WMI = importlib.util.find_spec("wmi") is not None

# Store connection history and scan results
history = []
scan_count = 0
last_scan_time = None
scan_results = []
scanner = USBScanner()

# Function to detect USB devices based on the operating system
def get_usb_devices():
    system = platform.system()
    devices = []
    devices = []

    if system == "Windows":
        try:
            # Try to use WMI if available
            if HAS_WMI:
                try:
                    # Use dynamic import to avoid IDE warnings
                    wmi_module = importlib.import_module("wmi")
                    c = wmi_module.WMI()

                    # Get USB devices using WMI
                    for disk in c.Win32_DiskDrive():
                        if "USB" in disk.InterfaceType:
                            device_id = disk.PNPDeviceID

                            # Get more details about the device
                            for partition in c.Win32_DiskPartition():
                                if partition.DiskIndex == disk.Index:
                                    for logical_disk in c.Win32_LogicalDiskToPartition():
                                        if logical_disk.Antecedent.split('=')[1].strip('"\'') == partition.DeviceID:
                                            drive_letter = logical_disk.Dependent.split('=')[1].strip('"\'')

                                            # Get drive information
                                            for drive in c.Win32_LogicalDisk():
                                                if drive.DeviceID == drive_letter:
                                                    # Convert bytes to GB
                                                    size = int(drive.Size) / (1024**3) if drive.Size else 0
                                                    free_space = int(drive.FreeSpace) / (1024**3) if drive.FreeSpace else 0

                                                    devices.append({
                                                        "name": disk.Model.strip(),
                                                        "id": device_id,
                                                        "drive_letter": drive_letter,
                                                        "size": f"{size:.1f}GB",
                                                        "free_space": f"{free_space:.1f}GB",
                                                        "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                                                    })

                    # If no USB drives found, try to get USB devices without drive letters
                    if not devices:
                        for usb in c.Win32_USBHub():
                            devices.append({
                                "name": usb.Description.strip() if usb.Description else "Unknown USB Device",
                                "id": usb.DeviceID,
                                "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                            })

                    # If we successfully got devices using WMI, return them
                    if devices:
                        return devices
                except Exception:
                    # If WMI fails, fall back to basic detection
                    pass

            # Fallback to using simple drive detection if WMI is not available or failed
            # Use ctypes for Windows API calls

            # Get available drives
            drives = []
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(letter)
                bitmask >>= 1

            # Check if drives are removable (likely USB)
            for drive in drives:
                drive_path = f"{drive}:\\"
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
                # 2 = DRIVE_REMOVABLE
                if drive_type == 2:
                    try:
                        # Get drive info using GetDiskFreeSpaceEx
                        free_bytes = ctypes.c_ulonglong(0)
                        total_bytes = ctypes.c_ulonglong(0)
                        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                            ctypes.c_wchar_p(drive_path),
                            None,
                            ctypes.byref(total_bytes),
                            ctypes.byref(free_bytes)
                        )

                        # Convert to GB
                        total_gb = total_bytes.value / (1024**3)
                        free_gb = free_bytes.value / (1024**3)

                        devices.append({
                            "name": f"Removable Drive ({drive}:)",
                            "id": f"DRIVE_{drive}",
                            "drive_letter": drive_path,
                            "size": f"{total_gb:.1f}GB",
                            "free_space": f"{free_gb:.1f}GB",
                            "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        })
                    except Exception:
                        # If we can't get size info, just add the drive
                        devices.append({
                            "name": f"Removable Drive ({drive}:)",
                            "id": f"DRIVE_{drive}",
                            "drive_letter": drive_path,
                            "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        })

                # If no devices found, return an empty list
                # We'll show "No USB found" in the UI

        except Exception as e:
            # Log the error but don't add simulated devices
            print(f"Error detecting USB devices: {str(e)}")
            # Return empty list - we'll show "No USB found" in the UI

    elif system == "Linux":
        try:
            import pyudev
            context = pyudev.Context()

            for device in context.list_devices(subsystem='block', DEVTYPE='disk'):
                if device.get('ID_BUS') == 'usb':
                    name = device.get('ID_MODEL', 'Unknown USB Device')
                    device_id = device.get('ID_SERIAL', 'Unknown ID')

                    # Try to get partition information
                    partitions = [p for p in context.list_devices(subsystem='block', DEVTYPE='partition')
                                 if p.parent == device]

                    if partitions:
                        for part in partitions:
                            # Try to get mount point
                            mount_point = None
                            try:
                                with open('/proc/mounts', 'r') as f:
                                    for line in f:
                                        if part.device_node in line:
                                            mount_point = line.split()[1]
                                            break
                            except:
                                pass

                            # If mounted, get size information
                            if mount_point:
                                try:
                                    import shutil
                                    total, _, free = shutil.disk_usage(mount_point)  # Ignore the 'used' value
                                    total_gb = total / (1024**3)
                                    free_gb = free / (1024**3)

                                    devices.append({
                                        "name": name,
                                        "id": device_id,
                                        "drive_letter": mount_point,
                                        "size": f"{total_gb:.1f}GB",
                                        "free_space": f"{free_gb:.1f}GB",
                                        "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                                    })
                                except:
                                    devices.append({
                                        "name": name,
                                        "id": device_id,
                                        "drive_letter": mount_point,
                                        "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                                    })
                    else:
                        devices.append({
                            "name": name,
                            "id": device_id,
                            "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        })

        except ImportError:
            devices.append({
                "name": "pyudev module not available",
                "id": "error",
                "error": "Please install pyudev module: pip install pyudev"
            })

    elif system == "Darwin":  # macOS
        try:
            # Use system_profiler to get USB devices
            import subprocess
            result = subprocess.run(['system_profiler', 'SPUSBDataType', '-json'],
                                   capture_output=True, text=True)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                usb_items = data.get('SPUSBDataType', [])

                for usb in usb_items:
                    # Process USB devices recursively
                    def process_usb_device(device, parent_name=""):
                        device_name = device.get('_name', 'Unknown USB Device')
                        full_name = f"{parent_name} {device_name}".strip()

                        # Only add storage devices
                        if 'Media' in device:
                            for media in device['Media']:
                                size = media.get('size', 'Unknown')
                                size_gb = float(size.replace(',', '')) / (1000**3) if size.replace(',', '').isdigit() else 0

                                devices.append({
                                    "name": full_name,
                                    "id": device.get('serial_num', 'Unknown ID'),
                                    "size": f"{size_gb:.1f}GB",
                                    "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                                })

                        # Process child devices
                        if '_items' in device:
                            for child in device['_items']:
                                process_usb_device(child, full_name)

                    # Start processing from top level
                    process_usb_device(usb)

        except Exception as e:
            devices.append({
                "name": "Error detecting macOS USB devices",
                "id": "error",
                "error": str(e)
            })

    else:
        devices.append({
            "name": f"Unsupported OS: {system}",
            "id": "error",
            "error": "USB detection not implemented for this operating system"
        })

    return devices

# API Routes
@app.route('/api/scan', methods=['GET'])
def scan_devices():
    global scan_count, last_scan_time

    # Increment scan count
    scan_count += 1
    last_scan_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

    # Get connected devices
    devices = get_usb_devices()

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

    return jsonify({
        "devices": devices,
        "history": history,
        "scan_count": scan_count,
        "scan_time": last_scan_time
    })

@app.route('/api/scan-device', methods=['POST'])
def scan_usb_device():
    global scan_results

    try:
        data = request.json
        drive_path = data.get('drive_path')

        if not drive_path:
            return jsonify({
                "status": "error",
                "message": "Drive path is required"
            }), 400

        # Check if drive exists
        if not os.path.exists(drive_path):
            return jsonify({
                "status": "error",
                "message": f"Drive path does not exist: {drive_path}"
            }), 400

        # Perform the scan
        result = scanner.scan_drive(drive_path)

        # Add to scan results
        scan_results.insert(0, {
            "drive_path": drive_path,
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            "result": result
        })

        # Limit scan results to last 20
        if len(scan_results) > 20:
            scan_results = scan_results[:20]

        return jsonify({
            "status": "success",
            "scan_result": result
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/scan-results', methods=['GET'])
def get_scan_results():
    return jsonify(scan_results)

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(history)

@app.route('/api/block-device', methods=['POST'])
def block_device():
    try:
        data = request.json
        device_id = data.get('device_id')

        if not device_id:
            return jsonify({
                "success": False,
                "message": "Device ID is required"
            }), 400

        # In a real app, this would call a system API to block the device
        # For now, we'll just update our internal state

        # Find the device in our list
        devices = get_usb_devices()
        device = next((d for d in devices if d.get('id') == device_id), None)

        if not device:
            return jsonify({
                "success": False,
                "message": f"Device with ID {device_id} not found"
            }), 404

        # Add to history
        history.insert(0, {
            "device_name": device.get('name', 'Unknown Device'),
            "device_id": device_id,
            "event_type": "blocked",
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        })

        return jsonify({
            "success": True,
            "message": f"Device {device_id} has been blocked",
            "device_id": device_id,
            "status": "blocked",
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/set-permission', methods=['POST'])
def set_permission():
    try:
        data = request.json
        device_id = data.get('device_id')
        permission = data.get('permission')

        if not device_id or not permission:
            return jsonify({
                "success": False,
                "message": "Device ID and permission are required"
            }), 400

        # Validate permission
        valid_permissions = ['read_only', 'full_access', 'blocked']
        if permission not in valid_permissions:
            return jsonify({
                "success": False,
                "message": f"Invalid permission. Must be one of: {', '.join(valid_permissions)}"
            }), 400

        # In a real app, this would call a system API to set the permission
        # For now, we'll just update our internal state

        # Find the device in our list
        devices = get_usb_devices()
        device = next((d for d in devices if d.get('id') == device_id), None)

        if not device:
            return jsonify({
                "success": False,
                "message": f"Device with ID {device_id} not found"
            }), 404

        # Add to history
        history.insert(0, {
            "device_name": device.get('name', 'Unknown Device'),
            "device_id": device_id,
            "event_type": f"permission_changed_{permission}",
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        })

        return jsonify({
            "success": True,
            "message": f"Device {device_id} permission set to {permission}",
            "device_id": device_id,
            "permission": permission,
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# Serve static files
@app.route('/', methods=['GET'])
def index():
    # Check if real_dashboard.html exists, otherwise fall back to usb_monitor.html
    if os.path.exists('real_dashboard.html'):
        return send_from_directory('.', 'real_dashboard.html')
    else:
        return app.send_static_file('usb_monitor.html')

@app.route('/<path:path>')
def static_files(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    try:
        print("Starting USB Monitoring System...")

        # Create static folder if it doesn't exist
        if not os.path.exists('static'):
            os.makedirs('static')
            print("Created static folder")

        # Copy HTML, CSS, and JS files to static folder
        for file in ['usb_monitor.html', 'styles.css', 'horizontal-scan.css']:
            if os.path.exists(file):
                try:
                    with open(file, 'r') as src:
                        with open(os.path.join('static', file), 'w') as dst:
                            dst.write(src.read())
                    print(f"Copied {file} to static folder")
                except Exception as e:
                    print(f"Error copying {file}: {str(e)}")

        # Initialize empty devices list (will be populated by real USB detection)
        devices = []

        print("Starting Flask server on port 5000...")
        # Run the Flask app
        app.run(debug=True, port=5000, host='0.0.0.0')
    except Exception as e:
        print(f"Error starting server: {str(e)}")

        # Create a simple HTML file with error information
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>USB Monitoring System - Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #1e293b; color: white; }}
                .error-container {{ max-width: 800px; margin: 0 auto; background-color: #0f172a; padding: 20px; border-radius: 8px; }}
                h1 {{ color: #ef4444; }}
                pre {{ background-color: #334155; padding: 10px; border-radius: 4px; overflow-x: auto; }}
                .button {{ display: inline-block; background-color: #3b82f6; color: white; padding: 10px 20px;
                          text-decoration: none; border-radius: 4px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>Error Starting USB Monitoring System</h1>
                <p>There was an error starting the server:</p>
                <pre>{str(e)}</pre>

                <h2>Troubleshooting Steps:</h2>
                <ol>
                    <li>Make sure you have all required dependencies installed:<br>
                        <pre>pip install -r requirements.txt</pre>
                    </li>
                    <li>Check if port 5000 is already in use by another application</li>
                    <li>Try running the application with administrator privileges</li>
                    <li>Check the console output for more detailed error messages</li>
                </ol>

                <h2>Fallback Mode</h2>
                <p>You can still use the application with simulated data:</p>
                <a href="usb_monitor.html" class="button">Open USB Monitor (Simulated Mode)</a>
            </div>
        </body>
        </html>
        """

        with open("error.html", "w") as f:
            f.write(error_html)

        print("Created error.html with troubleshooting information")
        print("You can open error.html in your browser for more information")


