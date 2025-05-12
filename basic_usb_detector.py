import os
import platform
import datetime
import string
import ctypes
import subprocess
import json

def get_windows_drives():
    """Get all drives on Windows."""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives

def get_drive_type(drive_path):
    """Get drive type using Windows API."""
    return ctypes.windll.kernel32.GetDriveTypeW(drive_path)

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
    except:
        return None, None

def get_usb_devices():
    """Get USB devices using basic methods."""
    system = platform.system()
    devices = []
    
    if system == "Windows":
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
    
    elif system == "Linux":
        # Basic Linux detection using /dev/sd* devices
        try:
            # List all block devices
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
            try:
                for dev in os.listdir('/dev'):
                    if dev.startswith('sd') and len(dev) == 3:
                        devices.append({
                            "name": f"Removable Drive (/dev/{dev})",
                            "id": f"DRIVE_{dev}",
                            "drive_letter": f"/dev/{dev}",
                            "connection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        })
            except:
                pass
    
    elif system == "Darwin":  # macOS
        # Basic macOS detection using /Volumes
        try:
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
        except:
            pass
    
    return devices

if __name__ == "__main__":
    print(f"Operating System: {platform.system()} {platform.release()}")
    print("Detecting USB devices...")
    
    devices = get_usb_devices()
    
    if devices:
        print(f"Found {len(devices)} USB device(s):")
        for i, device in enumerate(devices, 1):
            print(f"\nDevice {i}:")
            for key, value in device.items():
                print(f"  {key}: {value}")
    else:
        print("No USB devices detected.")
