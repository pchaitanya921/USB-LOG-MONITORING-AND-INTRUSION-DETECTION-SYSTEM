# USB Monitoring System - Desktop Application

A desktop application for monitoring and securing USB devices.

## Features

- Real-time USB device detection
- Malware scanning for connected USB devices
- Permission management (Read Only, Full Access, Blocked)
- Security alerts and notifications
- Detailed scan reports
- Email and SMS notifications
- System tray integration

## Requirements

- Python 3.6+
- PyQt5
- Windows, macOS, or Linux operating system

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/usb_monitor_desktop.git
cd usb_monitor_desktop
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python main.py
```

## Usage

### Dashboard

The dashboard provides an overview of connected USB devices and system status. It displays:

- Number of connected devices
- Total devices detected
- Total scans performed
- Detected threats
- Connected USB devices
- Recent alerts

### Devices

The devices page shows detailed information about connected USB devices:

- Device name and ID
- Drive letter and size
- Connection time
- Current permission status

You can perform the following actions:
- Scan a device
- Change device permissions
- Block/unblock a device

### Scans

The scans page shows the history of scan operations:

- Scan ID and timestamp
- Device scanned
- Scan status
- Files scanned
- Threats found

You can view detailed scan results and export them to a file.

### Alerts

The alerts page shows security alerts and notifications:

- Severity level
- Alert title and message
- Timestamp
- Actions (resolve, delete)

You can also configure notification settings:
- Email notifications
- SMS notifications
- Desktop notifications

### Settings

The settings page allows you to configure the application:

- General settings (startup, theme, language)
- Scanning settings (scan depth, file types)
- Permissions settings (default permissions)
- Notifications settings
- Advanced settings (logging, system integration)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- PyQt5 for the GUI framework
- WMI for Windows device detection
- PyUdev for Linux device detection
