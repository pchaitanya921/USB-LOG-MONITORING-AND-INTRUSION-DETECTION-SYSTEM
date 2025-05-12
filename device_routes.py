from flask import Blueprint, request, jsonify
from backend.models.db import db
from backend.models.device import USBDevice
from backend.models.alert import Alert
from backend.utils.usb_detector import get_connected_devices, get_device_info
from backend.utils.notification import send_connection_notification
from datetime import datetime
import json

device_bp = Blueprint('device_bp', __name__)

@device_bp.route('/', methods=['GET'])
def get_devices():
    """Get all USB devices"""
    devices = USBDevice.query.all()
    return jsonify([device.to_dict() for device in devices])

@device_bp.route('/connected', methods=['GET'])
def get_connected():
    """Get currently connected USB devices"""
    devices = USBDevice.query.filter_by(is_connected=True).all()
    return jsonify([device.to_dict() for device in devices])

@device_bp.route('/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get a specific USB device by ID"""
    device = USBDevice.query.get_or_404(device_id)
    return jsonify(device.to_dict())

@device_bp.route('/permission/<int:device_id>', methods=['POST'])
def set_permission(device_id):
    """Set permission for a USB device"""
    device = USBDevice.query.get_or_404(device_id)
    data = request.get_json()

    if 'is_permitted' not in data:
        return jsonify({"error": "Missing is_permitted field"}), 400

    device.is_permitted = data['is_permitted']

    # Create an alert for the permission change
    alert_type = "permission_granted" if device.is_permitted else "permission_denied"
    message = f"USB device {device.product_name} ({device.device_id}) has been {'permitted' if device.is_permitted else 'denied'}"

    alert = Alert(
        device_id=device.id,
        alert_type=alert_type,
        message=message,
        severity="info"
    )

    db.session.add(alert)
    db.session.commit()

    # Send notification about permission change
    send_connection_notification(device, alert_type)

    return jsonify(device.to_dict())

@device_bp.route('/refresh', methods=['GET'])
def refresh_devices():
    """Refresh the list of connected USB devices"""
    connected_devices = get_connected_devices()

    # Update database with connected devices
    for device_id, device_info in connected_devices.items():
        device = USBDevice.query.filter_by(device_id=device_id).first()

        if device:
            # Update existing device
            device.is_connected = True
            device.last_connected_at = datetime.utcnow()
            if not device.mount_point and 'mount_point' in device_info:
                device.mount_point = device_info['mount_point']
        else:
            # Create new device
            device = USBDevice(
                device_id=device_id,
                vendor_id=device_info.get('vendor_id'),
                product_id=device_info.get('product_id'),
                manufacturer=device_info.get('manufacturer'),
                product_name=device_info.get('product_name'),
                serial_number=device_info.get('serial_number'),
                mount_point=device_info.get('mount_point'),
                is_connected=True
            )
            db.session.add(device)

            # Create an alert for the new device
            alert = Alert(
                device_id=device.id,
                alert_type="new_connection",
                message=f"New USB device connected: {device_info.get('product_name', 'Unknown Device')}",
                severity="warning"
            )
            db.session.add(alert)

            # Send notification about new connection
            send_connection_notification(device, "new_connection")

    # Mark disconnected devices
    all_devices = USBDevice.query.filter_by(is_connected=True).all()
    for device in all_devices:
        if device.device_id not in connected_devices:
            device.is_connected = False
            device.last_disconnected_at = datetime.utcnow()

            # Create an alert for the disconnection
            alert = Alert(
                device_id=device.id,
                alert_type="disconnection",
                message=f"USB device disconnected: {device.product_name or 'Unknown Device'}",
                severity="info"
            )
            db.session.add(alert)

    db.session.commit()

    return jsonify({"message": "Devices refreshed successfully"})
