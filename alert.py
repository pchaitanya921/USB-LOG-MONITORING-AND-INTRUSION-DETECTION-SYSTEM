from datetime import datetime
from .db import db

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('usb_device.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'connection', 'malware', 'permission_denied', etc.
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    severity = db.Column(db.String(20), nullable=False, default='info')  # 'info', 'warning', 'critical'
    
    # Optional reference to a scan result
    scan_id = db.Column(db.Integer, db.ForeignKey('scan_result.id'), nullable=True)
    scan = db.relationship('ScanResult', backref=db.backref('alerts', lazy=True))
    
    # Notification status
    sms_sent = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Alert {self.id} - {self.alert_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alert_type': self.alert_type,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'is_read': self.is_read,
            'severity': self.severity,
            'scan_id': self.scan_id,
            'sms_sent': self.sms_sent,
            'email_sent': self.email_sent
        }
