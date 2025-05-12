# USB Monitoring System - Advanced Features

This document provides instructions for setting up and using the advanced features of the USB Monitoring System.

## 1. Device Whitelisting/Blacklisting

The system now supports device permission management with three levels:

- **Blocked**: USB devices are completely blocked from access
- **Read-Only**: USB devices can be read but not written to
- **Full Access**: USB devices have complete read/write access

### Using Device Permissions

1. **View Device Permissions**:
   - Access the API endpoint: `/api/devices/permissions`
   - This shows all devices with their current permissions

2. **Set Device Permission**:
   - Use the API endpoint: `/api/devices/permission/<device_id>`
   - Send a PUT request with:
     ```json
     {
       "permission": "read_only",
       "name": "Device Name"
     }
     ```
   - Valid permission values: `"blocked"`, `"read_only"`, `"full_access"`

3. **Default Settings**:
   - Use the API endpoint: `/api/devices/settings`
   - You can configure:
     - `default_permission`: Default permission for new devices
     - `auto_block_suspicious`: Automatically block suspicious devices
     - `notify_on_permission_change`: Send notifications when permissions change

### How It Works

1. When a USB device is connected, the system:
   - Checks if the device is already known
   - Applies the appropriate permission (from device list or default)
   - If `auto_block_suspicious` is enabled, suspicious devices are automatically blocked
   - Applies the permissions to the device using Windows security features

2. Permissions are enforced using:
   - Windows ICACLS for file system permissions
   - Registry modifications for device access control

## 2. System Tray Application

The system now includes a system tray application for easy access and monitoring.

### Setting Up the System Tray Application

1. **Install Required Dependencies**:
   ```
   run_system_tray.bat
   ```

2. **Configure Automatic Startup**:
   ```
   setup_tray_autostart.bat
   ```

### Using the System Tray Application

1. **Access the Menu**:
   - Right-click the blue icon in the system tray
   - The menu shows:
     - Current status (active/inactive)
     - Number of connected USB devices
     - Control options

2. **Available Actions**:
   - **Open Dashboard**: Opens the web interface
   - **Start/Stop Monitoring**: Controls USB monitoring
   - **Device Management**: Opens the device management page
   - **Scan All Devices**: Scans all connected USB devices
   - **Exit**: Closes the application

3. **Status Indicators**:
   - The menu shows real-time status information
   - Updates automatically every 5 seconds

## 3. Background Monitoring

The system now includes a background monitoring thread that continuously checks for USB devices.

### Features

1. **Real-time Detection**:
   - Continuously monitors for USB connections/disconnections
   - Automatically applies permissions to new devices
   - Updates the device history in real-time

2. **Automatic Scanning**:
   - Automatically scans new devices (if not blocked)
   - Runs scans in separate threads to avoid blocking
   - Sends notifications if threats are detected

3. **Control API**:
   - `/api/monitoring/status`: Get monitoring status
   - `/api/monitoring/start`: Start monitoring
   - `/api/monitoring/stop`: Stop monitoring

## 4. API Enhancements

The system includes several new API endpoints for advanced functionality:

### Device Management

- `GET /api/devices/permissions`: Get all device permissions
- `GET /api/devices/permission/<device_id>`: Get permission for a specific device
- `PUT /api/devices/permission/<device_id>`: Update permission for a specific device
- `GET /api/devices/settings`: Get device manager settings
- `PUT /api/devices/settings`: Update device manager settings

### Monitoring Control

- `GET /api/monitoring/status`: Get monitoring status
- `POST /api/monitoring/start`: Start monitoring
- `POST /api/monitoring/stop`: Stop monitoring

### Enhanced Status

- `GET /api/status`: Get comprehensive system status including:
  - WMI availability
  - OS information
  - Notification settings
  - Scanner capabilities
  - Device manager statistics
  - Monitoring status

## 5. Installation and Setup

### System Tray Application

1. **Install and Run**:
   ```
   run_system_tray.bat
   ```

2. **Configure Automatic Startup**:
   ```
   setup_tray_autostart.bat
   ```

### Required Dependencies

The system tray application requires:
- Python 3.7 or higher
- pystray
- Pillow (PIL)
- requests

These will be automatically installed by the setup scripts.

## 6. Troubleshooting

### System Tray Issues

- If the icon doesn't appear, check Task Manager for running Python processes
- Try running the script manually: `python system_tray.py`
- Make sure you have administrator privileges

### Permission Issues

- If permissions aren't being applied, make sure you're running as Administrator
- Check the `device_manager.log` file for detailed error messages
- Try manually setting permissions through the API

### Monitoring Issues

- If monitoring isn't working, check if the Flask server is running
- Try restarting the monitoring through the API: `/api/monitoring/start`
- Check for error messages in the console output
