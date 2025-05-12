import subprocess
import json
import datetime

def get_windows_usb_devices():
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

if __name__ == "__main__":
    print("Detecting USB devices...")
    devices = get_windows_usb_devices()
    
    if devices:
        print(f"Found {len(devices)} USB devices:")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device['name']} (ID: {device['id'][:30]}...)")
            print(f"   Status: {device['status']}")
            print(f"   Class: {device['class']}")
            print(f"   Connected: {device['connection_time']}")
            print()
    else:
        print("No USB devices found.")
