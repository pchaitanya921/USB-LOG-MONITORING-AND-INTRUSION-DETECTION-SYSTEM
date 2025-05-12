import os
import sys
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the Flask app
from backend.app import app, socketio
from backend.usb_monitor import start_monitor, stop_monitor

def run_app():
    """Run the Flask application with SocketIO"""
    # Start the USB monitor in a separate thread
    monitor_thread = threading.Thread(target=start_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    try:
        # Run the Flask app with SocketIO
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        # Stop the USB monitor when the app is stopped
        stop_monitor()

if __name__ == "__main__":
    run_app()
