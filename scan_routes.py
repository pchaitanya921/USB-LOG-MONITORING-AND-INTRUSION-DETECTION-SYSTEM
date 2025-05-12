from flask import Blueprint, request, jsonify
from backend.models.db import db
from backend.models.device import USBDevice
from backend.models.scan import ScanResult, InfectedFile
from backend.models.alert import Alert
from backend.utils.scanner import scan_device
from backend.utils.notification import send_malware_notification
import time
from datetime import datetime

scan_bp = Blueprint('scan_bp', __name__)

@scan_bp.route('/', methods=['GET'])
def get_scans():
    """Get all scan results"""
    scans = ScanResult.query.order_by(ScanResult.scan_date.desc()).all()
    return jsonify([scan.to_dict() for scan in scans])

@scan_bp.route('/<int:scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Get a specific scan result by ID"""
    scan = ScanResult.query.get_or_404(scan_id)

    # Get infected files for this scan
    infected_files = InfectedFile.query.filter_by(scan_id=scan.id).all()

    result = scan.to_dict()
    result['infected_files'] = [file.to_dict() for file in infected_files]

    return jsonify(result)

@scan_bp.route('/device/<int:device_id>', methods=['GET'])
def get_device_scans(device_id):
    """Get all scan results for a specific device"""
    device = USBDevice.query.get_or_404(device_id)
    scans = ScanResult.query.filter_by(device_id=device.id).order_by(ScanResult.scan_date.desc()).all()
    return jsonify([scan.to_dict() for scan in scans])

@scan_bp.route('/start/<int:device_id>', methods=['POST'])
def start_scan(device_id):
    """Start a scan for a specific device"""
    device = USBDevice.query.get_or_404(device_id)

    if not device.is_connected:
        return jsonify({"error": "Device is not connected"}), 400

    if not device.is_permitted:
        return jsonify({"error": "Device is not permitted"}), 400

    if not device.mount_point:
        return jsonify({"error": "Device mount point is unknown"}), 400

    # Create a new scan result
    scan_result = ScanResult(
        device_id=device.id,
        status='in_progress',
        scan_date=datetime.utcnow()
    )
    db.session.add(scan_result)
    db.session.commit()

    # Start the scan in a background thread
    # In a real application, this would be done with Celery or a similar task queue
    # For simplicity, we'll do it synchronously here
    start_time = time.time()

    try:
        scan_results = scan_device(device.mount_point)

        # Update scan result
        scan_result.status = 'completed'
        scan_result.total_files = scan_results['total_files']
        scan_result.scanned_files = scan_results['scanned_files']
        scan_result.infected_files = len(scan_results['infected_files'])
        scan_result.suspicious_files = len(scan_results['suspicious_files'])
        scan_result.scan_duration = time.time() - start_time

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

        # Create alerts based on scan results
        if scan_result.infected_files > 0:
            alert_type = "malware_detected"
            severity = "critical"
            message = f"Scan detected {scan_result.infected_files} malicious files on {device.product_name}"
        elif scan_result.suspicious_files > 0:
            alert_type = "suspicious_detected"
            severity = "warning"
            message = f"Scan detected {scan_result.suspicious_files} suspicious files on {device.product_name}"
        else:
            alert_type = "scan_completed"
            severity = "info"
            message = f"Scan completed on {device.product_name} with no threats detected"

        # Create alert record
        alert = Alert(
            device_id=device.id,
            scan_id=scan_result.id,
            alert_type=alert_type,
            message=message,
            severity=severity
        )
        db.session.add(alert)

        # Send notification for all scan results
        send_malware_notification(device, scan_result, alert)

        db.session.commit()

        return jsonify(scan_result.to_dict())

    except Exception as e:
        # Handle scan errors
        scan_result.status = 'error'
        scan_result.scan_duration = time.time() - start_time

        alert = Alert(
            device_id=device.id,
            scan_id=scan_result.id,
            alert_type="scan_error",
            message=f"Error scanning device {device.product_name}: {str(e)}",
            severity="warning"
        )
        db.session.add(alert)
        db.session.commit()

        return jsonify({"error": str(e)}), 500
