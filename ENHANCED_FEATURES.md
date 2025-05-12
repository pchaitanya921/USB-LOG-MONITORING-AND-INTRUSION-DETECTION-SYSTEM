# USB Monitoring System - Enhanced Features

This document provides instructions for setting up and using the enhanced features of the USB Monitoring System.

## 1. Enhanced Malware Scanning

The malware scanning capabilities have been significantly improved with the following features:

### New Detection Methods

- **File Signature Analysis**: Detects file types regardless of extension
- **Pattern Matching**: Scans for malicious byte patterns in files
- **Entropy Analysis**: Detects encrypted/packed malware
- **YARA Rules Integration**: Uses powerful pattern matching for malware detection
- **Extension Mismatch Detection**: Identifies files with misleading extensions

### Setting Up YARA for Advanced Detection

YARA provides powerful pattern matching capabilities for malware detection. To install YARA:

1. Run the `install_yara.bat` script as Administrator:
   ```
   install_yara.bat
   ```

2. If the installation is successful, the system will automatically use YARA rules for enhanced detection.

### Custom Malware Signatures

You can add your own malware signatures by editing the `scanner.py` file:

1. Open `scanner.py`
2. Find the `MALICIOUS_HASHES` dictionary
3. Add your own MD5 hashes and threat names:
   ```python
   "your_md5_hash_here": "Your.Malware.Name"
   ```

### Custom YARA Rules

You can add your own YARA rules by editing the `YARA_RULES_STR` variable in `scanner.py`:

1. Open `scanner.py`
2. Find the `YARA_RULES_STR` string
3. Add your own YARA rules following the existing format

## 2. Email and SMS Notifications

The system now supports real-time notifications via email and SMS when:
- USB devices are connected
- Malware is detected during scanning

### Setting Up Email Notifications

1. Create a `.env` file in the root directory (use `.env.example` as a template)
2. Add your email settings:
   ```
   EMAIL_USERNAME = "your_email@gmail.com"
   EMAIL_PASSWORD = "your_app_password"
   EMAIL_RECIPIENT = "recipient_email@example.com"
   EMAIL_SERVER = "smtp.gmail.com"
   EMAIL_PORT = 587
   ```

3. For Gmail, you need to use an App Password:
   - Go to your Google Account settings
   - Select Security
   - Under "Signing in to Google," select App Passwords
   - Select "Mail" as the app and "Windows Computer" as the device
   - Click Generate
   - Use the generated 16-character password

### Setting Up SMS Notifications (Twilio)

1. Create a Twilio account at [twilio.com](https://www.twilio.com)
2. Get your Account SID, Auth Token, and a Twilio phone number
3. Add these to your `.env` file:
   ```
   TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
   TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
   TWILIO_PHONE_NUMBER = "+1234567890"
   ALERT_RECIPIENT_PHONE = "+1234567890"
   ```

4. Install the Twilio Python package:
   ```
   pip install twilio
   ```

### Testing Notifications

You can test your notification settings using the API endpoint:

```
http://localhost:5000/api/notifications/test
```

This will send test notifications to your configured email and SMS.

## 3. Automatic Startup

You can configure the USB Monitoring System to start automatically when you log in to Windows.

### Setting Up Automatic Startup

1. Run the `setup_autostart.bat` script as Administrator:
   ```
   setup_autostart.bat
   ```

2. This will:
   - Create a startup script in the current directory
   - Create a shortcut in the Windows Startup folder
   - Configure the application to run minimized at startup

### Removing Automatic Startup

To remove the automatic startup:

1. Delete the shortcut from the Windows Startup folder:
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\USB Monitoring System.lnk
   ```

## 4. API Endpoints

The system provides several API endpoints for integration with other applications:

### USB Detection

- `GET /api/scan` - Scan for connected USB devices
- `GET /api/history` - Get USB connection history

### Malware Scanning

- `POST /api/scan-device` - Scan a specific USB device for malware
- `GET /api/scan-results` - Get results of previous scans

### Notifications

- `GET /api/notifications/test` - Test email and SMS notifications
- `GET /api/notifications/config` - Get current notification settings
- `POST /api/notifications/config` - Update notification settings

### System Status

- `GET /api/status` - Get system status information

## 5. Troubleshooting

### Malware Scanning Issues

- If YARA installation fails, the system will still work but without YARA scanning
- Large files (>10MB) are only partially scanned to avoid performance issues
- Check the `scanner.log` file for detailed error messages

### Notification Issues

- For email notifications, make sure your email provider allows SMTP access
- For Gmail, you must use an App Password, not your regular password
- For SMS notifications, make sure your Twilio account is active and funded
- Check the `notifications.log` file for detailed error messages

### Automatic Startup Issues

- Make sure you run `setup_autostart.bat` as Administrator
- If the application doesn't start automatically, check the Windows Task Manager for any errors
- Try running `start_usb_monitor.bat` manually to check for issues
