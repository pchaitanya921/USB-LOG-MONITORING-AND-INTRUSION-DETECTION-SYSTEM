import os
import sys
import json
import time
import datetime
import subprocess
import re
import platform
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("usb_detection.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("USB_Detector")

# Function to get USB devices on Windows
def get_windows_usb_devices():
    devices = []
    try:
        # Use PowerShell to get USB devices
        powershell_cmd = "Get-PnpDevice -PresentOnly | Where-Object { $_.Class -eq 'USB' -or $_.Class -eq 'DiskDrive' -or $_.Class -eq 'USBDevice' } | Select-Object Status, Class, FriendlyName, InstanceId | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error running PowerShell command: {result.stderr}")
            return devices
        
        # Parse the JSON output
        try:
            ps_devices = json.loads(result.stdout)
            # Handle case where only one device is returned (not in a list)
            if not isinstance(ps_devices, list):
                ps_devices = [ps_devices]
                
            for device in ps_devices:
                # Skip non-removable devices
                if not is_removable_device(device):
                    continue
                    
                device_info = {
                    "name": device.get("FriendlyName", "Unknown Device"),
                    "id": device.get("InstanceId", ""),
                    "status": device.get("Status", ""),
                    "class": device.get("Class", ""),
                    "connection_time": get_device_connection_time(device.get("InstanceId", "")),
                    "drive_letter": get_drive_letter_for_device(device.get("InstanceId", "")),
                    "is_connected": True
                }
                
                # Add drive information if available
                if device_info["drive_letter"]:
                    drive_info = get_drive_info(device_info["drive_letter"])
                    device_info.update(drive_info)
                
                devices.append(device_info)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing PowerShell output: {e}")
            logger.debug(f"PowerShell output: {result.stdout}")
    except Exception as e:
        logger.error(f"Error getting Windows USB devices: {e}")
    
    return devices

# Check if a device is removable
def is_removable_device(device):
    try:
        instance_id = device.get("InstanceId", "")
        friendly_name = device.get("FriendlyName", "").lower()
        
        # Check for keywords that indicate removable devices
        removable_keywords = ["usb", "flash", "removable", "portable", "kingston", "sandisk", "cruzer", "traveler"]
        
        # Check if any keyword is in the friendly name
        if any(keyword in friendly_name for keyword in removable_keywords):
            return True
            
        # For disk drives, check if they're removable
        if device.get("Class") == "DiskDrive":
            # Use PowerShell to check if it's removable
            powershell_cmd = f"Get-Disk | Where-Object {{ $_.Path -like '*{instance_id}*' }} | Select-Object BusType | ConvertTo-Json"
            result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    disk_info = json.loads(result.stdout)
                    if disk_info and disk_info.get("BusType") == "USB":
                        return True
                except:
                    pass
        
        return False
    except Exception as e:
        logger.error(f"Error checking if device is removable: {e}")
        return False

# Get the connection time for a device
def get_device_connection_time(instance_id):
    try:
        # Use PowerShell to get device connection time from event log
        powershell_cmd = f"Get-WinEvent -FilterHashtable @{{LogName='System'; Id=2003}} -MaxEvents 100 | Where-Object {{ $_.Message -like '*{instance_id}*' }} | Select-Object TimeCreated -First 1 | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                event_info = json.loads(result.stdout)
                if event_info and "TimeCreated" in event_info:
                    # Parse the time string
                    time_str = event_info["TimeCreated"]
                    # Convert to datetime object
                    dt = datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    # Format as string
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        # If we couldn't get the time from event log, use current time
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(f"Error getting device connection time: {e}")
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Get drive letter for a device
def get_drive_letter_for_device(instance_id):
    try:
        # Use PowerShell to get the drive letter
        powershell_cmd = f"Get-Disk | Where-Object {{ $_.Path -like '*{instance_id}*' }} | Get-Partition | Get-Volume | Select-Object DriveLetter | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                volume_info = json.loads(result.stdout)
                # Handle case where multiple volumes are returned
                if isinstance(volume_info, list):
                    for vol in volume_info:
                        if vol and "DriveLetter" in vol:
                            return vol["DriveLetter"] + ":"
                # Handle case where only one volume is returned
                elif volume_info and "DriveLetter" in volume_info:
                    return volume_info["DriveLetter"] + ":"
            except:
                pass
        
        # If we couldn't get the drive letter, try another method
        powershell_cmd = "Get-WmiObject Win32_DiskDrive | ForEach-Object {$disk = $_; $partitions = \"ASSOCIATORS OF {Win32_DiskDrive.DeviceID='$($disk.DeviceID)'} WHERE AssocClass = Win32_DiskDriveToDiskPartition\"; Get-WmiObject -Query $partitions | ForEach-Object {$partition = $_; $drives = \"ASSOCIATORS OF {Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} WHERE AssocClass = Win32_LogicalDiskToPartition\"; Get-WmiObject -Query $drives | ForEach-Object {$_ | Add-Member -MemberType NoteProperty -Name DiskModel -Value $disk.Model -PassThru}}} | Where-Object {$_.DiskModel -like '*USB*'} | Select-Object DeviceID, DiskModel | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                drives_info = json.loads(result.stdout)
                # Handle case where multiple drives are returned
                if isinstance(drives_info, list):
                    for drive in drives_info:
                        if drive and "DeviceID" in drive:
                            return drive["DeviceID"]
                # Handle case where only one drive is returned
                elif drives_info and "DeviceID" in drives_info:
                    return drives_info["DeviceID"]
            except:
                pass
        
        return ""
    except Exception as e:
        logger.error(f"Error getting drive letter for device: {e}")
        return ""

# Get drive information
def get_drive_info(drive_letter):
    drive_info = {
        "total_space": "Unknown",
        "free_space": "Unknown",
        "used_space": "Unknown"
    }
    
    try:
        if not drive_letter:
            return drive_info
            
        # Use PowerShell to get drive information
        powershell_cmd = f"Get-Volume -DriveLetter {drive_letter[0]} | Select-Object Size, SizeRemaining | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                volume_info = json.loads(result.stdout)
                if volume_info:
                    # Convert bytes to GB
                    total_bytes = volume_info.get("Size", 0)
                    free_bytes = volume_info.get("SizeRemaining", 0)
                    used_bytes = total_bytes - free_bytes
                    
                    total_gb = total_bytes / (1024**3)
                    free_gb = free_bytes / (1024**3)
                    used_gb = used_bytes / (1024**3)
                    
                    drive_info["total_space"] = f"{total_gb:.2f} GB"
                    drive_info["free_space"] = f"{free_gb:.2f} GB"
                    drive_info["used_space"] = f"{used_gb:.2f} GB"
                    drive_info["capacity"] = f"{total_gb:.2f} GB"
            except:
                pass
    except Exception as e:
        logger.error(f"Error getting drive info: {e}")
    
    return drive_info

# Main function to get all USB devices
def get_usb_devices():
    system = platform.system()
    
    if system == "Windows":
        return get_windows_usb_devices()
    else:
        logger.error(f"Unsupported operating system: {system}")
        return []

# Main entry point
if __name__ == "__main__":
    try:
        # Get USB devices
        devices = get_usb_devices()
        
        # Output as JSON
        print(json.dumps(devices, indent=2))
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(json.dumps({"error": str(e)}))
