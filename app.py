from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usb_monitor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models and initialize database
from backend.models.db import db
from backend.models.device import USBDevice
from backend.models.scan import ScanResult, InfectedFile
from backend.models.alert import Alert
from backend.models.settings import UserSettings

db.init_app(app)

# Process scan results function for usb_monitor.py
def process_scan_results(device, scan_result, scan_results):
    """Process scan results and create alerts if needed"""
    from backend.models.device import PermissionLevel

    # Add infected files to the database
    for file_info in scan_results['infected_files']:
        infected_file = InfectedFile(
            scan_id=scan_result.id,
            file_path=file_info['file_path'],
            threat_name=file_info['threat_name'],
            threat_type=file_info['threat_type']
        )
        db.session.add(infected_file)

    # Add suspicious files to the database
    for file_info in scan_results['suspicious_files']:
        suspicious_file = InfectedFile(
            scan_id=scan_result.id,
            file_path=file_info['file_path'],
            threat_name=file_info['threat_name'],
            threat_type='suspicious'
        )
        db.session.add(suspicious_file)

    # Set device permission level based on scan results
    has_threats = scan_result.infected_files > 0 or scan_result.suspicious_files > 0
    device.has_threats = has_threats

    # If threats are found, block the device, otherwise set to read-only
    if has_threats:
        device.is_permitted = False  # Block the device
    else:
        device.is_permitted = True   # Allow read-only access

    # Create alerts for infected files
    if has_threats:
        from backend.utils.notification import send_malware_notification

        alert_type = "malware_detected"
        severity = "critical" if scan_result.infected_files > 0 else "warning"

        message = f"Scan detected {scan_result.infected_files} malicious and {scan_result.suspicious_files} suspicious files on {device.product_name}. Device has been blocked."

        alert = Alert(
            device_id=device.id,
            scan_id=scan_result.id,
            alert_type=alert_type,
            message=message,
            severity=severity
        )
        db.session.add(alert)

        # Send notification about malware detection
        send_malware_notification(device, scan_result, alert)
    else:
        # Create an alert for clean scan
        message = f"Scan completed on {device.product_name}. No threats detected. Device set to read-only mode."

        alert = Alert(
            device_id=device.id,
            scan_id=scan_result.id,
            alert_type="scan_completed",
            message=message,
            severity="info"
        )
        db.session.add(alert)

    db.session.commit()

# Import routes
from backend.routes.device_routes import device_bp
from backend.routes.scan_routes import scan_bp
from backend.routes.alert_routes import alert_bp
from backend.routes.settings_routes import settings_bp

# Register blueprints
app.register_blueprint(device_bp, url_prefix='/api/devices')
app.register_blueprint(scan_bp, url_prefix='/api/scans')
app.register_blueprint(alert_bp, url_prefix='/api/alerts')
app.register_blueprint(settings_bp, url_prefix='/api/settings')

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return jsonify({"message": "USB Log Monitoring and Intrusion Detection System API"})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
