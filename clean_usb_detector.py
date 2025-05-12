import os
import platform
import datetime
import json
import ctypes
import string
import importlib.util

# Define a flag to check if WMI is available
# This approach avoids any import errors
HAS_WMI = importlib.util.find_spec("wmi") is not None

def get_windows_drives():
    """Get all drives on Windows."""
    drives = []
    try:
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1
    except Exception:
        pass
    return drives

def get_drive_type(drive_path):
    """Get drive type using Windows API."""
    try:
        return ctypes.windll.kernel32.GetDriveTypeW(drive_path)
    except Exception:
        return 0

def get_drive_info(drive_path):
    """Get drive size information."""
    try:
        free_bytes = ctypes.c_ulonglong(0)
        total_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(drive_path),
            None,
            ctypes.byref(total_bytes),
            ctypes.byref(free_bytes)
        )
        return total_bytes.value, free_bytes.value
    except Exception:
        return None, None

def detect_usb_with_wmi():
    """Detect USB devices using WMI (Windows only)."""
    devices = []
    error = None
    
    # Only attempt to use WMI if it's available
    if not HAS_WMI:
        return [], "WMI module not available"
    
    # We use a local import to avoid errors when WMI is not installed
    # This code will only run if HAS_WMI is True
    try:
        # We use a dynamic import to avoid IDE warnings
        wmi_module = importlib.import_module("wmi")
        c = wmi_module.WMI()
        
        # Get USB drives
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
    
    except Exception as e:
        error = f"Error using WMI: {str(e)}"
    
    return devices, error

def detect_usb_basic_windows():
    """Detect USB devices using basic Windows API (no WMI required)."""
    devices = []
    error = None
    
    try:
        # Get all drives
        for drive_letter in get_windows_drives():
            drive_path = f"{drive_letter}:\\"
            # 2 = DRIVE_REMOVABLE (likely USB)
            if get_drive_type(drive_path) == 2:
                total_bytes, free_bytes = get_drive_info(drive_path)
                
                if total_bytes and free_bytes:
                    # Convert to GB
                    total_gb = total_bytes / (1024**3)
                    free_gb = free_bytes / (1024**3)
                    
                    devices.append({
                        "name": f"Removable Drive ({drive_letter}:)",
                        "id": f"DRIVE_{drive_letter}",
                        "drive_letter": drive_path,
                        "size": f"{total_gb:.1f}GB",
                        "free_space": f"{free_gb:.1f}GB",
                        "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    })
                else:
                    devices.append({
                        "name": f"Removable Drive ({drive_letter}:)",
                        "id": f"DRIVE_{drive_letter}",
                        "drive_letter": drive_path,
                        "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    })
    
    except Exception as e:
        error = f"Error in basic detection: {str(e)}"
    
    return devices, error

def detect_usb_linux():
    """Detect USB devices on Linux."""
    devices = []
    error = None
    
    try:
        # Try to use pyudev if available
        if importlib.util.find_spec("pyudev") is not None:
            pyudev = importlib.import_module("pyudev")
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
                                    total, _, free = shutil.disk_usage(mount_point)
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
        else:
            # Fallback to basic detection using lsblk
            try:
                import subprocess
                result = subprocess.run(['lsblk', '-J'], capture_output=True, text=True)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for device in data.get('blockdevices', []):
                        # Check if it's likely a USB device (not a fixed disk)
                        if device.get('rm') == True:  # Removable flag
                            name = device.get('name', 'Unknown')
                            size = device.get('size', 'Unknown')
                            
                            # Check for mount points
                            mount_point = None
                            for child in device.get('children', []):
                                if child.get('mountpoint'):
                                    mount_point = child.get('mountpoint')
                                    break
                            
                            devices.append({
                                "name": f"Removable Drive ({name})",
                                "id": f"DRIVE_{name}",
                                "drive_letter": mount_point if mount_point else f"/dev/{name}",
                                "size": size,
                                "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                            })
            except:
                # Fallback to simple /dev listing
                for dev in os.listdir('/dev'):
                    if dev.startswith('sd') and len(dev) == 3:
                        devices.append({
                            "name": f"Removable Drive (/dev/{dev})",
                            "id": f"DRIVE_{dev}",
                            "drive_letter": f"/dev/{dev}",
                            "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        })
    
    except Exception as e:
        error = f"Error detecting Linux USB devices: {str(e)}"
    
    return devices, error

def detect_usb_macos():
    """Detect USB devices on macOS."""
    devices = []
    error = None
    
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
        
        # If no devices found, try basic detection using /Volumes
        if not devices:
            volumes = os.listdir('/Volumes')
            for volume in volumes:
                # Skip the main drive
                if volume != "Macintosh HD":
                    volume_path = os.path.join('/Volumes', volume)
                    
                    # Get disk info if possible
                    try:
                        stat = os.statvfs(volume_path)
                        total = stat.f_frsize * stat.f_blocks
                        free = stat.f_frsize * stat.f_bavail
                        
                        # Convert to GB
                        total_gb = total / (1024**3)
                        free_gb = free / (1024**3)
                        
                        devices.append({
                            "name": volume,
                            "id": f"VOLUME_{volume}",
                            "drive_letter": volume_path,
                            "size": f"{total_gb:.1f}GB",
                            "free_space": f"{free_gb:.1f}GB",
                            "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        })
                    except:
                        devices.append({
                            "name": volume,
                            "id": f"VOLUME_{volume}",
                            "drive_letter": volume_path,
                            "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        })
    
    except Exception as e:
        error = f"Error detecting macOS USB devices: {str(e)}"
    
    return devices, error

def get_usb_devices():
    """Get USB devices based on the operating system."""
    system = platform.system()
    
    if system == "Windows":
        # Try WMI method first if available
        if HAS_WMI:
            devices, error = detect_usb_with_wmi()
            if devices or not error:
                return devices, error
        
        # Fall back to basic method if WMI failed or not available
        return detect_usb_basic_windows()
    
    elif system == "Linux":
        return detect_usb_linux()
    
    elif system == "Darwin":  # macOS
        return detect_usb_macos()
    
    else:
        return [], f"Unsupported OS: {system}"

def test_usb_detection():
    """Test USB detection and print results."""
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"WMI module available: {HAS_WMI}")
    print("Detecting USB devices...")
    
    devices, error = get_usb_devices()
    
    if error:
        print(f"Error: {error}")
    
    if devices:
        print(f"Found {len(devices)} USB device(s):")
        for i, device in enumerate(devices, 1):
            print(f"\nDevice {i}:")
            for key, value in device.items():
                print(f"  {key}: {value}")
    else:
        print("No USB devices detected.")

if __name__ == "__main__":
    test_usb_detection()
