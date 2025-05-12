import os
import sys
import subprocess
import threading
import time
import json
import webbrowser
import requests
from datetime import datetime

# Check if required modules are available
try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("Required modules not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pystray", "pillow"])
    import pystray
    from PIL import Image, ImageDraw

# Flask server URL
SERVER_URL = "http://localhost:5000"
FLASK_PROCESS = None

def create_icon():
    """Create a system tray icon."""
    # Create a simple icon (a colored circle)
    width = 64
    height = 64
    color = (0, 128, 255)  # Blue
    
    image = Image.new('RGB', (width, height), color=(0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((5, 5, width-5, height-5), fill=color)
    
    return image

def get_status():
    """Get status from the Flask server."""
    try:
        response = requests.get(f"{SERVER_URL}/api/status", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_device_count():
    """Get count of connected USB devices."""
    try:
        response = requests.get(f"{SERVER_URL}/api/scan", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return len(data.get("devices", []))
        return 0
    except:
        return 0

def start_flask_server():
    """Start the Flask server as a subprocess."""
    global FLASK_PROCESS
    
    if FLASK_PROCESS is None or FLASK_PROCESS.poll() is not None:
        # Server not running, start it
        try:
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Start the Flask server
            FLASK_PROCESS = subprocess.Popen(
                [sys.executable, "clean_app.py"],
                cwd=script_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window
            )
            
            # Wait for server to start
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error starting Flask server: {str(e)}")
            return False
    
    return True  # Server already running

def stop_flask_server():
    """Stop the Flask server."""
    global FLASK_PROCESS
    
    if FLASK_PROCESS is not None and FLASK_PROCESS.poll() is None:
        try:
            # Try to stop monitoring first
            try:
                requests.post(f"{SERVER_URL}/api/monitoring/stop", timeout=2)
            except:
                pass
            
            # Kill the process
            FLASK_PROCESS.terminate()
            FLASK_PROCESS.wait(timeout=5)
            FLASK_PROCESS = None
            return True
        except Exception as e:
            print(f"Error stopping Flask server: {str(e)}")
            try:
                FLASK_PROCESS.kill()
                FLASK_PROCESS = None
            except:
                pass
            return False
    
    return True  # Server not running

def update_menu(icon):
    """Update the system tray menu with current status."""
    status = get_status()
    device_count = get_device_count()
    
    # Create menu items
    menu_items = []
    
    # Status information
    if status:
        monitoring_active = status.get("monitoring", {}).get("active", False)
        status_text = f"Status: {'Active' if monitoring_active else 'Inactive'}"
        menu_items.append(pystray.MenuItem(status_text, lambda: None, enabled=False))
        
        devices_text = f"Connected USB Devices: {device_count}"
        menu_items.append(pystray.MenuItem(devices_text, lambda: None, enabled=False))
        
        # Add separator
        menu_items.append(pystray.Menu.SEPARATOR)
    
    # Control actions
    menu_items.append(pystray.MenuItem("Open Dashboard", open_dashboard))
    
    if status:
        monitoring_active = status.get("monitoring", {}).get("active", False)
        if monitoring_active:
            menu_items.append(pystray.MenuItem("Stop Monitoring", stop_monitoring))
        else:
            menu_items.append(pystray.MenuItem("Start Monitoring", start_monitoring))
    
    # Add separator
    menu_items.append(pystray.Menu.SEPARATOR)
    
    # Add device management
    menu_items.append(pystray.MenuItem("Device Management", open_device_management))
    menu_items.append(pystray.MenuItem("Scan All Devices", scan_all_devices))
    
    # Add separator
    menu_items.append(pystray.Menu.SEPARATOR)
    
    # Exit option
    menu_items.append(pystray.MenuItem("Exit", exit_app))
    
    # Update the menu
    icon.menu = pystray.Menu(*menu_items)

def open_dashboard(icon, item):
    """Open the web dashboard."""
    webbrowser.open(SERVER_URL)

def open_device_management(icon, item):
    """Open the device management page."""
    webbrowser.open(f"{SERVER_URL}/devices.html")

def start_monitoring(icon, item):
    """Start USB monitoring."""
    try:
        response = requests.post(f"{SERVER_URL}/api/monitoring/start", timeout=2)
        if response.status_code == 200:
            # Update menu after a short delay
            threading.Timer(1, lambda: update_menu(icon)).start()
    except:
        pass

def stop_monitoring(icon, item):
    """Stop USB monitoring."""
    try:
        response = requests.post(f"{SERVER_URL}/api/monitoring/stop", timeout=2)
        if response.status_code == 200:
            # Update menu after a short delay
            threading.Timer(1, lambda: update_menu(icon)).start()
    except:
        pass

def scan_all_devices(icon, item):
    """Scan all connected USB devices."""
    try:
        # Get connected devices
        response = requests.get(f"{SERVER_URL}/api/scan", timeout=2)
        if response.status_code == 200:
            data = response.json()
            devices = data.get("devices", [])
            
            # Scan each device with a drive letter
            for device in devices:
                if "drive_letter" in device:
                    drive_path = device["drive_letter"]
                    requests.post(
                        f"{SERVER_URL}/api/scan-device",
                        json={"drive_path": drive_path},
                        timeout=2
                    )
    except:
        pass

def exit_app(icon, item):
    """Exit the application."""
    icon.stop()
    stop_flask_server()

def setup_tray():
    """Set up the system tray icon and menu."""
    # Create the icon
    icon = pystray.Icon("usb_monitor", create_icon(), "USB Monitoring System")
    
    # Set up initial menu
    update_menu(icon)
    
    # Start a thread to periodically update the menu
    def update_thread():
        while True:
            try:
                update_menu(icon)
                time.sleep(5)  # Update every 5 seconds
            except:
                time.sleep(10)  # On error, wait longer
    
    threading.Thread(target=update_thread, daemon=True).start()
    
    # Start the Flask server
    start_flask_server()
    
    # Run the icon
    icon.run()

if __name__ == "__main__":
    setup_tray()
