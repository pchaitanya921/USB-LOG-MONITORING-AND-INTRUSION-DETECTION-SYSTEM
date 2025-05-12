import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

# Load environment variables
load_dotenv()

# Initialize the database
print("Initializing database...")
try:
    from init_db import init_database
    init_database()
    print("Database initialized successfully.")
except Exception as e:
    print(f"Error initializing database: {e}")
    sys.exit(1)

# Start the USB monitor and Flask app
print("Starting USB Monitor and Flask app...")
try:
    from app import app, socketio
    from usb_monitor import start_monitor

    # Start the USB monitor
    start_monitor()

    # Run the Flask app
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
