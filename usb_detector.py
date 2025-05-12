#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
USB Detector Module
Handles detection of USB devices and monitoring for new connections/disconnections
"""

import os
import platform
import datetime
import ctypes
import string
from PyQt5.QtCore import QObject, pyqtSignal

# Import platform-specific modules
if platform.system() == "Windows":
    import win32com.client
    import wmi
elif platform.system() == "Linux":
    import pyudev

class USBDevice:
    """Class representing a USB device"""
    def __init__(self, device_id, name, drive_letter=None, size=None, free_space=None):
        self.id = device_id
        self.name = name
        self.drive_letter = drive_letter
        self.size = size
        self.free_space = free_space
        self.connection_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.permission = "read_only"  # Default permission
        self.status = "active"
        self.last_scan_time = None
        self.scan_result = None

        # Enhanced device information
        self.vendor_id = ""
        self.product_id = ""
        self.serial_number = ""
        self.manufacturer = ""
        self.product = ""
        self.device_type = "unknown"  # storage, hid, camera, etc.
        self.interface_type = ""      # USB 2.0, USB 3.0, etc.
        self.is_trusted = False
        self.first_seen = self.connection_time
        self.connection_count = 1
        self.last_scan_result = None
        self.hardware_ids = []
        self.compatible_ids = []
        self.file_system = ""
        self.is_encrypted = False
        self.is_write_protected = False
        self.is_removable = True
        self.is_hotpluggable = True
        self.icon_path = ""

    def to_dict(self):
        """Convert device to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "drive_letter": self.drive_letter,
            "size": self.size,
            "free_space": self.free_space,
            "connection_time": self.connection_time,
            "permission": self.permission,
            "status": self.status,
            "last_scan_time": self.last_scan_time,
            "scan_result": self.scan_result,
            "vendor_id": self.vendor_id,
            "product_id": self.product_id,
            "serial_number": self.serial_number,
            "manufacturer": self.manufacturer,
            "product": self.product,
            "device_type": self.device_type,
            "interface_type": self.interface_type,
            "is_trusted": self.is_trusted,
            "first_seen": self.first_seen,
            "connection_count": self.connection_count,
            "hardware_ids": self.hardware_ids,
            "compatible_ids": self.compatible_ids,
            "file_system": self.file_system,
            "is_encrypted": self.is_encrypted,
            "is_write_protected": self.is_write_protected,
            "is_removable": self.is_removable,
            "is_hotpluggable": self.is_hotpluggable
        }

    def get_device_icon(self):
        """Get the appropriate icon for this device type"""
        if self.device_type == "storage":
            return "assets/icons/usb_storage.png"
        elif self.device_type == "hid":
            return "assets/icons/usb_hid.png"
        elif self.device_type == "camera":
            return "assets/icons/usb_camera.png"
        elif self.device_type == "printer":
            return "assets/icons/usb_printer.png"
        elif self.device_type == "audio":
            return "assets/icons/usb_audio.png"
        elif self.device_type == "network":
            return "assets/icons/usb_network.png"
        else:
            return "assets/icons/usb_generic.png"

class USBDetector(QObject):
    """Class for detecting and monitoring USB devices"""
    # Define signals
    device_connected = pyqtSignal(USBDevice)
    device_disconnected = pyqtSignal(str)  # device_id

    def __init__(self):
        super().__init__()
        self.devices = {}  # Dictionary of connected devices
        self.system = platform.system()

    def get_connected_devices(self):
        """Get list of currently connected USB devices"""
        if self.system == "Windows":
            return self._get_windows_devices()
        elif self.system == "Linux":
            return self._get_linux_devices()
        elif self.system == "Darwin":  # macOS
            return self._get_macos_devices()
        else:
            return []

    def _get_windows_devices(self):
        """Get USB devices on Windows with enhanced information"""
        devices = []
        device_history = self._load_device_history()

        try:
            # Try using WMI first
            c = wmi.WMI()

            # Get all USB controllers to determine USB version
            usb_controllers = {}
            for controller in c.Win32_USBController():
                usb_controllers[controller.DeviceID] = controller.Name

            # Get USB drives
            for disk in c.Win32_DiskDrive():
                if "USB" in disk.InterfaceType:
                    device_id = disk.PNPDeviceID

                    # Create basic device
                    device = USBDevice(
                        device_id=device_id,
                        name=disk.Model.strip() if disk.Model else "Unknown USB Storage",
                    )

                    # Set device type
                    device.device_type = "storage"

                    # Get more details about the device
                    try:
                        for partition in c.Win32_DiskPartition():
                            if partition.DiskIndex == disk.Index:
                                try:
                                    for logical_disk in c.Win32_LogicalDiskToPartition():
                                        try:
                                            antecedent_parts = logical_disk.Antecedent.split('=')
                                            if len(antecedent_parts) > 1:
                                                antecedent_value = antecedent_parts[1].strip('"\'')
                                                if antecedent_value == partition.DeviceID:
                                                    dependent_parts = logical_disk.Dependent.split('=')
                                                    if len(dependent_parts) > 1:
                                                        drive_letter = dependent_parts[1].strip('"\'')

                                                        # Get drive information
                                                        for drive in c.Win32_LogicalDisk():
                                                            if drive.DeviceID == drive_letter:
                                                                # Convert bytes to GB
                                                                size = int(drive.Size) / (1024**3) if drive.Size else 0
                                                                free_space = int(drive.FreeSpace) / (1024**3) if drive.FreeSpace else 0

                                                                device.drive_letter = drive_letter
                                                                device.size = f"{size:.1f}GB"
                                                                device.free_space = f"{free_space:.1f}GB"
                                                                device.file_system = drive.FileSystem
                                        except Exception as e:
                                            # Skip this logical disk if there's an error
                                            continue
                                except Exception as e:
                                    # Skip this partition's logical disks if there's an error
                                    continue
                    except Exception as e:
                        # Skip partition processing if there's an error
                        print(f"Error processing partitions: {str(e)}")

                    # Get USB device details from PnP entity
                    for pnp_entity in c.Win32_PnPEntity():
                        if pnp_entity.DeviceID == device_id:
                            # Extract vendor and product IDs from device ID
                            if "VID_" in device_id and "PID_" in device_id:
                                vid_start = device_id.find("VID_") + 4
                                pid_start = device_id.find("PID_") + 4
                                device.vendor_id = device_id[vid_start:vid_start+4]
                                device.product_id = device_id[pid_start:pid_start+4]

                            # Get manufacturer and product name
                            device.manufacturer = pnp_entity.Manufacturer if pnp_entity.Manufacturer else ""
                            device.product = pnp_entity.Name if pnp_entity.Name else ""

                            # Get hardware IDs
                            if pnp_entity.HardwareID:
                                device.hardware_ids = list(pnp_entity.HardwareID)

                            # Get compatible IDs
                            if pnp_entity.CompatibleID:
                                device.compatible_ids = list(pnp_entity.CompatibleID)

                            # Determine USB version from controller
                            for controller_id, controller_name in usb_controllers.items():
                                if controller_id in device_id:
                                    if "3.0" in controller_name:
                                        device.interface_type = "USB 3.0"
                                    elif "2.0" in controller_name:
                                        device.interface_type = "USB 2.0"
                                    else:
                                        device.interface_type = "USB"
                                    break

                    # Check if device is write-protected
                    device.is_write_protected = not disk.Capabilities or 4 not in disk.Capabilities

                    # Update device history information
                    if device_id in device_history:
                        history = device_history[device_id]
                        device.first_seen = history.get("first_seen", device.connection_time)
                        device.connection_count = history.get("connection_count", 0) + 1
                        device.is_trusted = history.get("is_trusted", False)

                    devices.append(device)

            # Get all USB devices (not just storage)
            if not devices:
                # Get USB hubs and controllers
                for usb in c.Win32_USBHub():
                    # Skip root hubs
                    if "ROOT_HUB" in usb.DeviceID:
                        continue

                    device = USBDevice(
                        device_id=usb.DeviceID,
                        name=usb.Description.strip() if usb.Description else "USB Device"
                    )

                    # Extract vendor and product IDs from device ID
                    if "VID_" in usb.DeviceID and "PID_" in usb.DeviceID:
                        vid_start = usb.DeviceID.find("VID_") + 4
                        pid_start = usb.DeviceID.find("PID_") + 4
                        device.vendor_id = usb.DeviceID[vid_start:vid_start+4]
                        device.product_id = usb.DeviceID[pid_start:pid_start+4]

                    # Determine device type based on class codes
                    for pnp_entity in c.Win32_PnPEntity():
                        if pnp_entity.DeviceID == usb.DeviceID:
                            # Get hardware IDs
                            if pnp_entity.HardwareID:
                                device.hardware_ids = list(pnp_entity.HardwareID)

                                # Determine device type from hardware ID
                                hw_id = device.hardware_ids[0] if device.hardware_ids else ""
                                if "USB\\Class_03" in hw_id:
                                    device.device_type = "hid"
                                elif "USB\\Class_06" in hw_id:
                                    device.device_type = "camera"
                                elif "USB\\Class_07" in hw_id:
                                    device.device_type = "printer"
                                elif "USB\\Class_08" in hw_id:
                                    device.device_type = "storage"
                                elif "USB\\Class_01" in hw_id:
                                    device.device_type = "audio"
                                elif "USB\\Class_09" in hw_id:
                                    device.device_type = "hub"
                                elif "USB\\Class_0E" in hw_id:
                                    device.device_type = "video"
                                elif "USB\\Class_0A" in hw_id:
                                    device.device_type = "cdc"
                                elif "USB\\Class_02" in hw_id:
                                    device.device_type = "network"
                                else:
                                    device.device_type = "unknown"

                            # Get compatible IDs
                            if pnp_entity.CompatibleID:
                                device.compatible_ids = list(pnp_entity.CompatibleID)

                            # Get manufacturer and product name
                            device.manufacturer = pnp_entity.Manufacturer if pnp_entity.Manufacturer else ""
                            device.product = pnp_entity.Name if pnp_entity.Name else ""

                    # Update device history information
                    if usb.DeviceID in device_history:
                        history = device_history[usb.DeviceID]
                        device.first_seen = history.get("first_seen", device.connection_time)
                        device.connection_count = history.get("connection_count", 0) + 1
                        device.is_trusted = history.get("is_trusted", False)

                    devices.append(device)

        except Exception as e:
            print(f"Error in WMI detection: {str(e)}")
            # Fallback to basic method
            try:
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
                            # Check if drive is accessible
                            if not os.path.exists(drive_path):
                                continue

                            # Get drive info using GetDiskFreeSpaceEx
                            free_bytes = ctypes.c_ulonglong(0)
                            total_bytes = ctypes.c_ulonglong(0)
                            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                                ctypes.c_wchar_p(drive_path),
                                None,
                                ctypes.byref(total_bytes),
                                ctypes.byref(free_bytes)
                            )

                            # Get volume information
                            volume_name_buffer = ctypes.create_unicode_buffer(1024)
                            file_system_name_buffer = ctypes.create_unicode_buffer(1024)
                            ctypes.windll.kernel32.GetVolumeInformationW(
                                ctypes.c_wchar_p(drive_path),
                                volume_name_buffer,
                                ctypes.sizeof(volume_name_buffer),
                                None,
                                None,
                                None,
                                file_system_name_buffer,
                                ctypes.sizeof(file_system_name_buffer)
                            )

                            # Convert to GB
                            total_gb = total_bytes.value / (1024**3)
                            free_gb = free_bytes.value / (1024**3)

                            device_id = f"DRIVE_{drive}"
                            device_name = volume_name_buffer.value if volume_name_buffer.value else f"Removable Drive ({drive}:)"

                            device = USBDevice(
                                device_id=device_id,
                                name=device_name,
                                drive_letter=drive_path,
                                size=f"{total_gb:.1f}GB",
                                free_space=f"{free_gb:.1f}GB"
                            )

                            device.device_type = "storage"
                            device.file_system = file_system_name_buffer.value

                            # Update device history information
                            if device_id in device_history:
                                history = device_history[device_id]
                                device.first_seen = history.get("first_seen", device.connection_time)
                                device.connection_count = history.get("connection_count", 0) + 1
                                device.is_trusted = history.get("is_trusted", False)

                            devices.append(device)
                        except Exception as e:
                            print(f"Error getting drive info: {str(e)}")
                            # If we can't get size info, just add the drive
                            device_id = f"DRIVE_{drive}"
                            device = USBDevice(
                                device_id=device_id,
                                name=f"Removable Drive ({drive}:)",
                                drive_letter=drive_path
                            )
                            device.device_type = "storage"

                            # Update device history information
                            if device_id in device_history:
                                history = device_history[device_id]
                                device.first_seen = history.get("first_seen", device.connection_time)
                                device.connection_count = history.get("connection_count", 0) + 1
                                device.is_trusted = history.get("is_trusted", False)

                            devices.append(device)
            except Exception as e:
                print(f"Error in basic detection: {str(e)}")

        # Update device history
        self._update_device_history(devices)

        return devices

    def _get_linux_devices(self):
        """Get USB devices on Linux"""
        devices = []

        try:
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

                                    usb_device = USBDevice(
                                        device_id=device_id,
                                        name=name,
                                        drive_letter=mount_point,
                                        size=f"{total_gb:.1f}GB",
                                        free_space=f"{free_gb:.1f}GB"
                                    )
                                    devices.append(usb_device)
                                except:
                                    usb_device = USBDevice(
                                        device_id=device_id,
                                        name=name,
                                        drive_letter=mount_point
                                    )
                                    devices.append(usb_device)
                    else:
                        usb_device = USBDevice(
                            device_id=device_id,
                            name=name
                        )
                        devices.append(usb_device)
        except Exception:
            pass

        return devices

    def _get_macos_devices(self):
        """Get USB devices on macOS"""
        devices = []

        try:
            # Basic detection using /Volumes
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

                        usb_device = USBDevice(
                            device_id=f"VOLUME_{volume}",
                            name=volume,
                            drive_letter=volume_path,
                            size=f"{total_gb:.1f}GB",
                            free_space=f"{free_gb:.1f}GB"
                        )
                        devices.append(usb_device)
                    except:
                        usb_device = USBDevice(
                            device_id=f"VOLUME_{volume}",
                            name=volume,
                            drive_letter=volume_path
                        )
                        devices.append(usb_device)
        except Exception:
            pass

        return devices

    def start_monitoring(self):
        """Start monitoring for USB device changes"""
        import threading
        import time

        # Get initial devices
        current_devices = self.get_connected_devices()

        # Store current devices
        for device in current_devices:
            self.devices[device.id] = device

        # Start monitoring thread
        def monitor_thread():
            while True:
                try:
                    # Get current devices
                    new_devices = self.get_connected_devices()

                    # Check for new devices
                    new_device_ids = [device.id for device in new_devices]
                    for device in new_devices:
                        if device.id not in self.devices:
                            # New device connected
                            self.devices[device.id] = device
                            self.device_connected.emit(device)

                    # Check for disconnected devices
                    for device_id in list(self.devices.keys()):
                        if device_id not in new_device_ids:
                            # Device disconnected
                            self.device_disconnected.emit(device_id)
                            del self.devices[device_id]

                    # Sleep for a bit
                    time.sleep(2)
                except Exception as e:
                    print(f"Error in USB monitoring: {str(e)}")
                    time.sleep(5)  # Sleep longer on error

        # Start thread
        self.monitoring_thread = threading.Thread(target=monitor_thread, daemon=True)
        self.monitoring_thread.start()

        return current_devices

    def stop_monitoring(self):
        """Stop monitoring for USB device changes"""
        # The thread is a daemon, so it will stop when the program exits
        pass

    def update_device_permission(self, device_id, permission):
        """Update the permission for a device"""
        if device_id in self.devices:
            self.devices[device_id].permission = permission
            # Update device history
            self._update_device_history([self.devices[device_id]])
            return True
        return False

    def _load_device_history(self):
        """Load device history from file"""
        import os
        import json

        history_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "device_history.json")

        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading device history: {str(e)}")

        return {}

    def _save_device_history(self, history):
        """Save device history to file"""
        import os
        import json

        history_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "device_history.json")

        try:
            with open(history_file, "w") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"Error saving device history: {str(e)}")

    def _update_device_history(self, devices):
        """Update device history with new device information"""
        history = self._load_device_history()

        for device in devices:
            # Create or update history entry
            if device.id not in history:
                history[device.id] = {
                    "first_seen": device.connection_time,
                    "connection_count": 1,
                    "is_trusted": device.is_trusted,
                    "name": device.name,
                    "vendor_id": device.vendor_id,
                    "product_id": device.product_id,
                    "manufacturer": device.manufacturer,
                    "product": device.product,
                    "device_type": device.device_type,
                    "last_connected": device.connection_time
                }
            else:
                # Update existing entry
                history[device.id]["connection_count"] += 1
                history[device.id]["last_connected"] = device.connection_time
                history[device.id]["is_trusted"] = device.is_trusted

                # Update device information if available
                if device.name:
                    history[device.id]["name"] = device.name
                if device.vendor_id:
                    history[device.id]["vendor_id"] = device.vendor_id
                if device.product_id:
                    history[device.id]["product_id"] = device.product_id
                if device.manufacturer:
                    history[device.id]["manufacturer"] = device.manufacturer
                if device.product:
                    history[device.id]["product"] = device.product
                if device.device_type != "unknown":
                    history[device.id]["device_type"] = device.device_type

        # Save updated history
        self._save_device_history(history)

    def set_device_trusted(self, device_id, trusted=True):
        """Set a device as trusted or untrusted"""
        if device_id in self.devices:
            self.devices[device_id].is_trusted = trusted
            # Update device history
            self._update_device_history([self.devices[device_id]])
            return True

        # Check device history
        history = self._load_device_history()
        if device_id in history:
            history[device_id]["is_trusted"] = trusted
            self._save_device_history(history)
            return True

        return False

    def get_device_history(self):
        """Get the history of all devices"""
        return self._load_device_history()

    def get_trusted_devices(self):
        """Get a list of trusted devices"""
        history = self._load_device_history()
        trusted_devices = []

        for device_id, device_info in history.items():
            if device_info.get("is_trusted", False):
                trusted_devices.append({
                    "id": device_id,
                    "name": device_info.get("name", "Unknown Device"),
                    "first_seen": device_info.get("first_seen", "Unknown"),
                    "last_connected": device_info.get("last_connected", "Unknown"),
                    "connection_count": device_info.get("connection_count", 0),
                    "device_type": device_info.get("device_type", "unknown")
                })

        return trusted_devices

    def identify_device(self, device_id):
        """Identify a device based on its hardware IDs"""
        # This would be expanded with a database of known devices
        # For now, we'll just return basic information

        if device_id in self.devices:
            device = self.devices[device_id]
            return {
                "id": device.id,
                "name": device.name,
                "vendor_id": device.vendor_id,
                "product_id": device.product_id,
                "manufacturer": device.manufacturer,
                "product": device.product,
                "device_type": device.device_type,
                "is_trusted": device.is_trusted
            }

        # Check device history
        history = self._load_device_history()
        if device_id in history:
            return {
                "id": device_id,
                "name": history[device_id].get("name", "Unknown Device"),
                "vendor_id": history[device_id].get("vendor_id", ""),
                "product_id": history[device_id].get("product_id", ""),
                "manufacturer": history[device_id].get("manufacturer", ""),
                "product": history[device_id].get("product", ""),
                "device_type": history[device_id].get("device_type", "unknown"),
                "is_trusted": history[device_id].get("is_trusted", False)
            }

        return None
