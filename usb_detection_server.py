from flask import Flask, jsonify
from flask_cors import CORS
import subprocess
import json
import datetime
import platform
import os
import time

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Store USB device history
device_history = []
scan_count = 0

def get_windows_usb_devices():
    """Get USB devices on Windows using PowerShell"""
    try:
        # Use PowerShell to get USB devices
        powershell_cmd = "Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'USB' -or $_.Class -eq 'DiskDrive' -or $_.Class -eq 'USBDevice' } | Select-Object Status, Class, FriendlyName, InstanceId | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error running PowerShell command: {result.stderr}")
            return []
        
        # Parse the JSON output
        try:
            ps_devices = json.loads(result.stdout)
            
            # Handle case where only one device is returned (not in a list)
            if not isinstance(ps_devices, list):
                ps_devices = [ps_devices]
            
            # Format the output
            devices = []
            for device in ps_devices:
                device_info = {
                    "name": device.get("FriendlyName", "Unknown Device"),
                    "id": device.get("InstanceId", ""),
                    "status": device.get("Status", ""),
                    "class": device.get("Class", ""),
                    "connection_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                devices.append(device_info)
            
            return devices
        except json.JSONDecodeError as e:
            print(f"Error parsing PowerShell output: {e}")
            print(f"PowerShell output: {result.stdout}")
            return []
    except Exception as e:
        print(f"Error getting Windows USB devices: {e}")
        return []

def get_usb_drives():
    """Get USB drives with additional information"""
    try:
        # Use PowerShell to get USB drives
        powershell_cmd = "Get-WmiObject Win32_DiskDrive | Where-Object {$_.InterfaceType -eq 'USB'} | ForEach-Object {$disk = $_; $partitions = \"ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($disk.DeviceID)'} WHERE AssocClass = Win32_DiskDriveToDiskPartition\"; Get-WmiObject -Query $partitions | ForEach-Object {$partition = $_; $drives = \"ASSOCIATORS OF {Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} WHERE AssocClass = Win32_LogicalDiskToPartition\"; Get-WmiObject -Query $drives | ForEach-Object {$_ | Add-Member -MemberType NoteProperty -Name DiskModel -Value $disk.Model -PassThru}}} | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error running PowerShell command: {result.stderr}")
            return []
        
        # Parse the JSON output
        try:
            if not result.stdout.strip():
                return []
                
            drives_data = json.loads(result.stdout)
            
            # Handle case where only one drive is returned (not in a list)
            if not isinstance(drives_data, list):
                drives_data = [drives_data]
            
            # Format the output
            drives = []
            for drive in drives_data:
                drive_info = {
                    "name": drive.get("DiskModel", "Unknown Drive"),
                    "id": drive.get("DeviceID", ""),
                    "drive_letter": drive.get("DeviceID", ""),
                    "volume_name": drive.get("VolumeName", ""),
                    "size": str(round(int(drive.get("Size", 0)) / (1024**3), 2)) + " GB",
                    "free_space": str(round(int(drive.get("FreeSpace", 0)) / (1024**3), 2)) + " GB",
                    "connection_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                drives.append(drive_info)
            
            return drives
        except json.JSONDecodeError as e:
            print(f"Error parsing PowerShell output: {e}")
            print(f"PowerShell output: {result.stdout}")
            return []
    except Exception as e:
        print(f"Error getting USB drives: {e}")
        return []

def update_device_history(devices):
    """Update device history with new devices and detect disconnections"""
    global device_history
    
    # Get current time
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Get IDs of currently connected devices
    current_device_ids = [device["id"] for device in devices]
    
    # Check for disconnections
    for history_entry in device_history:
        if history_entry["event_type"] == "connected" and history_entry["device_id"] not in current_device_ids:
            # This device was connected but is now gone
            if not any(h["device_id"] == history_entry["device_id"] and h["event_type"] == "disconnected" and h["timestamp"] > history_entry["timestamp"] for h in device_history):
                # Add disconnection event if not already recorded
                device_history.append({
                    "device_id": history_entry["device_id"],
                    "device_name": history_entry["device_name"],
                    "event_type": "disconnected",
                    "timestamp": now_str
                })
    
    # Check for new connections
    for device in devices:
        # Check if this is a new connection
        if not any(h["device_id"] == device["id"] and h["event_type"] == "connected" for h in device_history):
            # Add connection event
            device_history.append({
                "device_id": device["id"],
                "device_name": device["name"],
                "event_type": "connected",
                "timestamp": now_str
            })
    
    # Sort history by timestamp (newest first)
    device_history.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Limit history to last 50 entries
    if len(device_history) > 50:
        device_history = device_history[:50]

@app.route('/')
def index():
    return app.send_static_file('usb_monitor.html')

@app.route('/api/scan', methods=['GET'])
def scan_usb_devices():
    """Scan for USB devices and return the results"""
    global scan_count
    scan_count += 1
    
    # Get current time
    now = datetime.datetime.now()
    scan_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Get USB devices
    devices = []
    
    if platform.system() == 'Windows':
        # Get general USB devices
        usb_devices = get_windows_usb_devices()
        devices.extend(usb_devices)
        
        # Get USB drives with more details
        usb_drives = get_usb_drives()
        
        # Add drives if they're not already in the list
        for drive in usb_drives:
            if not any(device["id"] == drive["id"] for device in devices):
                devices.append(drive)
    else:
        # Not implemented for other platforms
        pass
    
    # Update device history
    update_device_history(devices)
    
    # Return the results
    return jsonify({
        "scan_time": scan_time,
        "scan_count": scan_count,
        "devices": devices,
        "history": device_history
    })

if __name__ == '__main__':
    print("Starting USB Detection Server...")
    print("Open http://localhost:5000/ in your browser")
    app.run(debug=False, host='0.0.0.0', port=5000)
