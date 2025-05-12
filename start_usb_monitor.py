import os
import sys
import subprocess
import webbrowser
import time
import threading

def start_backend():
    """Start the USB monitoring backend server"""
    print("Starting USB Monitoring System Backend...")
    try:
        # Run the backend server
        subprocess.run([sys.executable, "usb_monitor_backend.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting backend: {e}")
    except KeyboardInterrupt:
        print("Backend server stopped by user")

def open_dashboard():
    """Open the dashboard in the default web browser"""
    print("Opening dashboard in web browser...")
    # Wait for the backend to start
    time.sleep(3)
    # Get the absolute path to the dashboard HTML file
    dashboard_path = os.path.abspath("simple-dashboard.html")
    # Convert to file URL
    dashboard_url = f"file:///{dashboard_path.replace(os.sep, '/')}"
    # Open in browser
    webbrowser.open(dashboard_url)

if __name__ == "__main__":
    print("USB Monitoring System Launcher")
    print("==============================")
    
    # Start the backend server in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Open the dashboard
    open_dashboard()
    
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down USB Monitoring System...")
