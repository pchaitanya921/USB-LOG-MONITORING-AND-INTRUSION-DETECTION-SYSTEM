# USB Monitoring System - Installation Guide

This guide will help you set up the USB Monitoring System with real USB device detection.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Administrator privileges (for USB device detection)

## Step 1: Install Required Dependencies

### Windows

Open Command Prompt as Administrator and run:

```
pip install flask==2.3.3 flask-cors==4.0.0
pip install wmi==1.5.1 pywin32==306
```

### Linux

```
pip install flask==2.3.3 flask-cors==4.0.0
pip install pyudev==0.24.1
```

### macOS

```
pip install flask==2.3.3 flask-cors==4.0.0
pip install pyobjc==7.3
```

## Step 2: Test USB Detection

Run the USB detector script to test if USB detection is working:

```
python usb_detector.py
```

You should see a list of connected USB devices. If you encounter any errors, make sure you've installed the correct dependencies for your operating system.

## Step 3: Run the Application

Start the Flask server:

```
python simple_app.py
```

Open your web browser and navigate to:

```
http://localhost:5000
```

## Troubleshooting

### WMI Module Not Found

If you see an error about the WMI module not being found on Windows:

1. Make sure you've installed both wmi and pywin32:
   ```
   pip install wmi==1.5.1 pywin32==306
   ```

2. If the error persists, try running the Command Prompt as Administrator when installing the packages.

### Port 5000 Already in Use

If port 5000 is already in use, you can change the port in `simple_app.py`:

```python
app.run(debug=True, port=5001)  # Change to a different port
```

### Permission Issues

USB detection may require administrator privileges:

- Windows: Run Command Prompt as Administrator
- Linux: Use `sudo` when running the application
- macOS: Grant necessary permissions when prompted

### No USB Devices Detected

If no USB devices are detected:

1. Make sure you have USB devices connected to your computer
2. Try disconnecting and reconnecting the USB devices
3. Check if the devices are recognized by your operating system
4. Run `python usb_detector.py` to test USB detection separately

## Advanced Configuration

### Changing the Scan Interval

The web interface automatically refreshes every 30 seconds. You can change this in the JavaScript code in `usb_monitor.html`:

```javascript
// Set up auto-refresh every 30 seconds (30000 ms)
autoRefreshInterval = setInterval(scanUsbDevices, 30000);
```

### Adding Custom Malware Signatures

You can add custom malware signatures in `scanner.py` by updating the `MALICIOUS_HASHES` dictionary:

```python
MALICIOUS_HASHES = {
    "e44e35b203bbc12486983c8080172d48": "Trojan.Generic",
    # Add your custom signatures here
    "your_md5_hash_here": "Your.Malware.Name"
}
```

## Next Steps

After successfully setting up the basic USB monitoring system, you can:

1. Implement email and SMS notifications
2. Add user authentication
3. Enhance the malware scanning capabilities
4. Create a database to store historical data
