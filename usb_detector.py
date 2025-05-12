import os
import platform
import subprocess
import re
import json

# Import pyudev only on Linux
if platform.system() == 'Linux':
    import pyudev

def get_connected_devices():
    """
    Get information about all connected USB devices.
    Returns a dictionary with device_id as key and device info as value.
    """
    if platform.system() == 'Windows':
        return get_connected_devices_windows()
    elif platform.system() == 'Linux':
        return get_connected_devices_linux()
    elif platform.system() == 'Darwin':  # macOS
        return get_connected_devices_macos()
    else:
        raise NotImplementedError(f"USB detection not implemented for {platform.system()}")

def get_connected_devices_windows():
    """Get connected USB devices on Windows"""
    devices = {}

    try:
        # Use a simpler approach to list drives
        result = subprocess.run(["cmd", "/c", "fsutil fsinfo drives"],
                               capture_output=True, text=True, check=True)

        # Parse the output to find all drives
        output = result.stdout.strip()
        if "Drives: " in output:
            drives = output.split("Drives: ")[1].split()

            for drive in drives:
                # Skip C: drive (system drive)
                if drive.upper() == "C:":
                    continue

                # Get drive type
                try:
                    type_result = subprocess.run(["cmd", "/c", f"fsutil fsinfo drivetype {drive}"],
                                            capture_output=True, text=True, check=True)

                    drive_type = type_result.stdout.strip()

                    # Only include removable drives
                    if "Removable Drive" in drive_type:
                        device_id = f"DRIVE_{drive.replace(':', '')}"

                        # Try to get volume label
                        try:
                            vol_result = subprocess.run(["cmd", "/c", f"vol {drive}"],
                                                capture_output=True, text=True, check=True)
                            vol_output = vol_result.stdout.strip()

                            product_name = "Removable Storage"
                            if "Volume in drive" in vol_output and "is" in vol_output:
                                parts = vol_output.split("is")
                                if len(parts) > 1:
                                    label = parts[1].strip()
                                    if label and label != "":
                                        product_name = label
                        except:
                            product_name = f"Removable Drive ({drive})"

                        device_info = {
                            'device_id': device_id,
                            'vendor_id': None,
                            'product_id': None,
                            'manufacturer': 'USB Device',
                            'product_name': product_name,
                            'serial_number': None,
                            'mount_point': drive
                        }

                        devices[device_id] = device_info
                except:
                    # If we can't get drive type, skip this drive
                    continue

        # Try another method if no devices found
        if not devices:
            try:
                # Use another command to get USB device information
                result = subprocess.run(["cmd", "/c", "wmic diskdrive where InterfaceType='USB' get Model,Size,Status /format:list"],
                                      capture_output=True, text=True, check=True)

                output = result.stdout
                drive_sections = output.strip().split('\n\n')

                for i, section in enumerate(drive_sections):
                    if not section.strip():
                        continue

                    device_info = {
                        'device_id': f"USB_DRIVE_{i}",
                        'vendor_id': None,
                        'product_id': None,
                        'manufacturer': 'USB Device',
                        'product_name': 'USB Storage',
                        'serial_number': None,
                        'mount_point': None
                    }

                    lines = section.strip().split('\n')
                    for line in lines:
                        if '=' not in line:
                            continue

                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'Model' and value:
                            device_info['product_name'] = value
                            # Try to extract manufacturer from model name
                            parts = value.split()
                            if parts:
                                device_info['manufacturer'] = parts[0]

                    if device_info['product_name'] != 'USB Storage':
                        devices[device_info['device_id']] = device_info
            except Exception as e:
                print(f"Error in secondary USB detection: {e}")

    except Exception as e:
        print(f"Error getting USB devices: {e}")

        # Fallback method using a simpler command
        try:
            # List drive letters
            result = subprocess.run(["cmd", "/c", "fsutil fsinfo drives"],
                                capture_output=True, text=True, check=True)

            output = result.stdout.strip()
            if "Drives: " in output:
                drives = output.split("Drives: ")[1].split()

                for i, drive in enumerate(drives):
                    # Skip C: drive (system drive)
                    if drive.upper() == "C:":
                        continue

                    # Get drive type
                    type_result = subprocess.run(["cmd", "/c", f"fsutil fsinfo drivetype {drive}"],
                                            capture_output=True, text=True, check=True)

                    drive_type = type_result.stdout.strip()

                    # Only include removable drives
                    if "Removable Drive" in drive_type:
                        device_info = {
                            'device_id': f"DRIVE_{drive.replace(':', '')}",
                            'vendor_id': None,
                            'product_id': None,
                            'manufacturer': 'USB Device',
                            'product_name': f'Removable Drive ({drive})',
                            'serial_number': None,
                            'mount_point': drive
                        }

                        devices[device_info['device_id']] = device_info

        except Exception as inner_e:
            print(f"Error in fallback USB detection: {inner_e}")

    # If still no devices found, add a dummy device for testing
    if not devices and os.environ.get('DEBUG_MODE') == 'True':
        devices['DUMMY_DEVICE'] = {
            'device_id': 'DUMMY_DEVICE',
            'vendor_id': '0000',
            'product_id': '0000',
            'manufacturer': 'Debug Manufacturer',
            'product_name': 'Debug USB Device',
            'serial_number': 'DEBUG123456',
            'mount_point': 'D:'
        }

    return devices

def get_device_info_windows(device_id):
    """Get detailed information about a USB device on Windows"""
    try:
        # Get device details using PowerShell
        cmd = f"Get-PnpDeviceProperty -InstanceId '{device_id}' | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", cmd],
                               capture_output=True, text=True, check=True)

        # Parse the JSON output
        properties = json.loads(result.stdout)

        # Extract relevant information
        device_info = {
            'device_id': device_id,
            'vendor_id': None,
            'product_id': None,
            'manufacturer': None,
            'product_name': None,
            'serial_number': None,
            'mount_point': None
        }

        # If only one property is returned, it won't be in a list
        if not isinstance(properties, list):
            properties = [properties]

        for prop in properties:
            key = prop.get("KeyName", "")
            data = prop.get("Data")

            if key == "DEVPKEY_Device_Manufacturer":
                device_info['manufacturer'] = data
            elif key == "DEVPKEY_Device_FriendlyName":
                device_info['product_name'] = data
            elif key == "DEVPKEY_Device_HardwareIds":
                # Extract vendor and product IDs from hardware ID
                if isinstance(data, list) and len(data) > 0:
                    match = re.search(r'VID_([0-9A-F]{4})&PID_([0-9A-F]{4})', data[0])
                    if match:
                        device_info['vendor_id'] = match.group(1)
                        device_info['product_id'] = match.group(2)

        # Get drive letter for USB storage devices
        cmd = "Get-WmiObject -Class Win32_DiskDrive | Where-Object {$_.InterfaceType -eq 'USB'} | " + \
              "ForEach-Object {$drive = $_; Get-WmiObject -Class Win32_DiskDriveToDiskPartition | " + \
              "Where-Object {$_.Antecedent -eq $drive.Path.Path} | " + \
              "ForEach-Object {$partition = $_; Get-WmiObject -Class Win32_LogicalDiskToPartition | " + \
              "Where-Object {$_.Antecedent -eq $partition.Dependent} | " + \
              "ForEach-Object {$disk = $_; Get-WmiObject -Class Win32_LogicalDisk | " + \
              "Where-Object {$_.Path.Path -eq $disk.Dependent}}}} | ConvertTo-Json"

        result = subprocess.run(["powershell", "-Command", cmd],
                               capture_output=True, text=True, check=False)

        try:
            drives = json.loads(result.stdout)

            # If only one drive is returned, it won't be in a list
            if not isinstance(drives, list):
                drives = [drives]

            for drive in drives:
                if drive and 'DeviceID' in drive:
                    device_info['mount_point'] = drive['DeviceID']
                    break
        except:
            pass

        return device_info

    except Exception as e:
        print(f"Error getting device info: {e}")
        return None

def get_connected_devices_linux():
    """Get connected USB devices on Linux using pyudev"""
    devices = {}

    try:
        context = pyudev.Context()

        # Get all USB devices
        for device in context.list_devices(subsystem='usb', DEVTYPE='usb_device'):
            device_id = device.get('DEVPATH', '').split('/')[-1]

            # Skip USB hubs
            if device.get('ID_MODEL', '').lower().find('hub') != -1:
                continue

            device_info = {
                'device_id': device_id,
                'vendor_id': device.get('ID_VENDOR_ID'),
                'product_id': device.get('ID_MODEL_ID'),
                'manufacturer': device.get('ID_VENDOR'),
                'product_name': device.get('ID_MODEL'),
                'serial_number': device.get('ID_SERIAL_SHORT'),
                'mount_point': None
            }

            # Try to find mount point for storage devices
            for child in device.children:
                if child.subsystem == 'block' and child.device_type == 'disk':
                    for partition in child.children:
                        if partition.device_type == 'partition':
                            mount_info = subprocess.run(['findmnt', '-n', '-o', 'TARGET', partition.device_node],
                                                      capture_output=True, text=True)
                            if mount_info.returncode == 0 and mount_info.stdout.strip():
                                device_info['mount_point'] = mount_info.stdout.strip()
                                break

            devices[device_id] = device_info

    except Exception as e:
        print(f"Error getting USB devices: {e}")

    return devices

def get_connected_devices_macos():
    """Get connected USB devices on macOS"""
    devices = {}

    try:
        # Use system_profiler to get USB devices
        cmd = ["system_profiler", "SPUSBDataType", "-json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the JSON output
        usb_data = json.loads(result.stdout)

        # Process USB devices
        for controller in usb_data.get('SPUSBDataType', []):
            process_macos_usb_device(controller, devices)

    except Exception as e:
        print(f"Error getting USB devices: {e}")

    return devices

def process_macos_usb_device(device, devices, parent_name=None):
    """Process a USB device from macOS system_profiler output"""
    # Skip USB hubs
    if 'Hub' in device.get('_name', ''):
        # But process its children
        for child in device.get('_items', []):
            process_macos_usb_device(child, devices, device.get('_name'))
        return

    # Generate a unique device ID
    device_id = device.get('_name', '') + '_' + device.get('serial_num', '')
    if not device_id or device_id == '_':
        return

    # Extract vendor and product IDs
    vendor_id = None
    product_id = None
    vendor_product = device.get('vendor_id', '')
    if vendor_product:
        match = re.search(r'(0x[0-9a-f]{4}) (0x[0-9a-f]{4})', vendor_product, re.IGNORECASE)
        if match:
            vendor_id = match.group(1)[2:]  # Remove '0x' prefix
            product_id = match.group(2)[2:]

    device_info = {
        'device_id': device_id,
        'vendor_id': vendor_id,
        'product_id': product_id,
        'manufacturer': device.get('manufacturer', ''),
        'product_name': device.get('_name', ''),
        'serial_number': device.get('serial_num', ''),
        'mount_point': None
    }

    # Try to find mount point for storage devices
    if 'Media' in device:
        for media in device['Media']:
            if 'volumes' in media:
                for volume in media['volumes']:
                    if 'mount_point' in volume:
                        device_info['mount_point'] = volume['mount_point']
                        break

    devices[device_id] = device_info

    # Process child devices
    for child in device.get('_items', []):
        process_macos_usb_device(child, devices, device.get('_name'))

def get_device_info(device_id):
    """Get detailed information about a USB device"""
    devices = get_connected_devices()
    return devices.get(device_id)
