from flask import Blueprint, request, jsonify
from backend.models.db import db
from backend.models.alert import Alert

alert_bp = Blueprint('alert_bp', __name__)

@alert_bp.route('/', methods=['GET'])
def get_alerts():
    """Get all alerts, with optional filtering"""
    # Get query parameters
    is_read = request.args.get('is_read')
    severity = request.args.get('severity')
    alert_type = request.args.get('alert_type')
    limit = request.args.get('limit', default=100, type=int)

    # Build query
    query = Alert.query

    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        query = query.filter_by(is_read=is_read_bool)

    if severity:
        query = query.filter_by(severity=severity)

    if alert_type:
        query = query.filter_by(alert_type=alert_type)

    # Get results
    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()

    return jsonify([alert.to_dict() for alert in alerts])

@alert_bp.route('/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Get a specific alert by ID"""
    alert = Alert.query.get_or_404(alert_id)
    return jsonify(alert.to_dict())

@alert_bp.route('/<int:alert_id>/read', methods=['POST'])
def mark_read(alert_id):
    """Mark an alert as read"""
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    return jsonify(alert.to_dict())

@alert_bp.route('/read-all', methods=['POST'])
def mark_all_read():
    """Mark all alerts as read"""
    Alert.query.update({Alert.is_read: True})
    db.session.commit()
    return jsonify({"message": "All alerts marked as read"})

@alert_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """Get the count of unread alerts"""
    count = Alert.query.filter_by(is_read=False).count()
    return jsonify({"unread_count": count})
