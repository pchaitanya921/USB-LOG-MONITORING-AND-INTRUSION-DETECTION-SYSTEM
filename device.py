from datetime import datetime
from .db import db
import enum

class PermissionLevel(enum.Enum):
    BLOCKED = 0
    READ_ONLY = 1
    FULL_ACCESS = 2

class USBDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    vendor_id = db.Column(db.String(10), nullable=True)
    product_id = db.Column(db.String(10), nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    product_name = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    mount_point = db.Column(db.String(255), nullable=True)
    is_permitted = db.Column(db.Boolean, default=False)
    # We'll use is_permitted to determine permission level in the to_dict method
    # permission_level = db.Column(db.Integer, default=PermissionLevel.READ_ONLY.value)
    # has_threats = db.Column(db.Boolean, default=False)
    is_connected = db.Column(db.Boolean, default=False)
    first_connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_disconnected_at = db.Column(db.DateTime, nullable=True)

    # These properties will be used instead of database columns
    _permission_level = PermissionLevel.READ_ONLY.value
    _has_threats = False

    # Relationships
    scan_results = db.relationship('ScanResult', backref='device', lazy=True)
    alerts = db.relationship('Alert', backref='device', lazy=True)

    def __repr__(self):
        return f'<USBDevice {self.product_name} ({self.device_id})>'

    @property
    def permission_level(self):
        """Get the permission level based on is_permitted and _has_threats"""
        if hasattr(self, '_has_threats') and self._has_threats:
            return PermissionLevel.BLOCKED.value
        elif self.is_permitted:
            return PermissionLevel.READ_ONLY.value
        else:
            return PermissionLevel.BLOCKED.value

    @property
    def has_threats(self):
        """Get the has_threats property"""
        if hasattr(self, '_has_threats'):
            return self._has_threats
        return False

    @has_threats.setter
    def has_threats(self, value):
        """Set the has_threats property"""
        self._has_threats = value
        # Update is_permitted based on threats
        if value:
            self.is_permitted = False

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'vendor_id': self.vendor_id,
            'product_id': self.product_id,
            'manufacturer': self.manufacturer,
            'product_name': self.product_name,
            'serial_number': self.serial_number,
            'mount_point': self.mount_point,
            'is_permitted': self.is_permitted,
            'permission_level': self.permission_level,
            'permission_status': self.get_permission_status(),
            'has_threats': self.has_threats,
            'is_connected': self.is_connected,
            'first_connected_at': self.first_connected_at.isoformat() if self.first_connected_at else None,
            'last_connected_at': self.last_connected_at.isoformat() if self.last_connected_at else None,
            'last_disconnected_at': self.last_disconnected_at.isoformat() if self.last_disconnected_at else None
        }

    def get_permission_status(self):
        """Get a human-readable permission status"""
        if self.permission_level == PermissionLevel.BLOCKED.value:
            return "Blocked"
        elif self.permission_level == PermissionLevel.READ_ONLY.value:
            return "Read Only"
        elif self.permission_level == PermissionLevel.FULL_ACCESS.value:
            return "Full Access"
        else:
            return "Unknown"
