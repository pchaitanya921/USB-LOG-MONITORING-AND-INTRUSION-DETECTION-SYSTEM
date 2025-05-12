from flask import Blueprint, request, jsonify
from backend.models.db import db
from backend.models.settings import UserSettings

settings_bp = Blueprint('settings_bp', __name__)

@settings_bp.route('/', methods=['GET'])
def get_settings():
    """Get user settings"""
    # Get the first settings object or create one if it doesn't exist
    settings = UserSettings.query.first()

    if not settings:
        settings = UserSettings()
        db.session.add(settings)
        db.session.commit()

    return jsonify(settings.to_dict())

@settings_bp.route('/', methods=['PUT'])
def update_settings():
    """Update user settings"""
    settings = UserSettings.query.first()

    if not settings:
        settings = UserSettings()
        db.session.add(settings)

    data = request.get_json()

    # Update settings with provided values
    if 'email_notifications' in data:
        settings.email_notifications = data['email_notifications']

    if 'sms_notifications' in data:
        settings.sms_notifications = data['sms_notifications']

    if 'auto_scan' in data:
        settings.auto_scan = data['auto_scan']

    if 'require_permission' in data:
        settings.require_permission = data['require_permission']

    if 'email' in data:
        settings.email = data['email']

    if 'phone' in data:
        settings.phone = data['phone']

    db.session.commit()

    return jsonify(settings.to_dict())
