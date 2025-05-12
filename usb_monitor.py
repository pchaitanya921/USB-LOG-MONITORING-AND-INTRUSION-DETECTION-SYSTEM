import subprocess
import json
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("usb_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("usb_monitor")

# Initialize Flask app
app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes

# Windows-specific USB detection
def get_windows_usb_devices():
    devices = []
    try:
        # Use PowerShell to get USB drive information
        cmd = "Get-WmiObject Win32_DiskDrive | Where-Object {$_.InterfaceType -eq 'USB'} | ForEach-Object {$disk = $_; $partitions = Get-WmiObject -Query \"ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($disk.DeviceID)'} WHERE AssocClass = Win32_DiskDriveToDiskPartition\"; foreach($partition in $partitions) {$volumes = Get-WmiObject -Query \"ASSOCIATORS OF {Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} WHERE AssocClass = Win32_LogicalDiskToPartition\"; foreach($volume in $volumes) {Write-Output \"$($disk.DeviceID)|$($disk.Model)|$($volume.DeviceID)|$($volume.VolumeName)|$($volume.Size)|$($volume.FreeSpace)\"}}} | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)

        if result.returncode == 0 and result.stdout.strip():
            # Parse the output
            lines = json.loads(result.stdout)
            if isinstance(lines, str):  # Handle single device case
                lines = [lines]

            for line in lines:
                parts = line.split('|')
                if len(parts) >= 6:
                    device_id = parts[0].replace('\\', '_').replace('.', '_')
                    model = parts[1].strip()
                    drive_letter = parts[2].strip()
                    volume_name = parts[3].strip() if parts[3].strip() else "USB Drive"
                    size_bytes = int(parts[4]) if parts[4].strip() else 0
                    free_bytes = int(parts[5]) if parts[5].strip() else 0

                    # Format size as GB with 2 decimal places
                    size_gb = round(size_bytes / (1024**3), 2) if size_bytes else 0
                    free_gb = round(free_bytes / (1024**3), 2) if free_bytes else 0
                    used_gb = round(size_gb - free_gb, 2)

                    # Create device entry
                    devices.append({
                        'device_id': device_id,
                        'name': model,
                        'vendor': model.split()[0] if ' ' in model else 'Unknown',
                        'mount_point': drive_letter,
                        'volume_name': volume_name,
                        'capacity': f"{size_gb}GB",
                        'used_space': f"{used_gb}GB",
                        'free_space': f"{free_gb}GB",
                        'status': 'connected'
                    })

        logger.info(f"Found {len(devices)} USB devices")
    except Exception as e:
        logger.error(f"Error getting USB devices: {str(e)}")

    return devices

# API routes
@app.route('/')
def index():
    return send_from_directory('.', 'usb-scan-demo.html')

@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices = get_windows_usb_devices()
    return jsonify(devices)

# Main entry point
if __name__ == '__main__':
    logger.info("Starting USB Monitoring System")
    app.run(host='0.0.0.0', port=5000, debug=True)
