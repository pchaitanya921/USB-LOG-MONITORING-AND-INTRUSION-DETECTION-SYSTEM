from datetime import datetime
from .db import db

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('usb_device.id'), nullable=False)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # 'clean', 'infected', 'suspicious', 'error'
    total_files = db.Column(db.Integer, default=0)
    scanned_files = db.Column(db.Integer, default=0)
    infected_files = db.Column(db.Integer, default=0)
    suspicious_files = db.Column(db.Integer, default=0)
    scan_duration = db.Column(db.Float, default=0.0)  # in seconds

    def __repr__(self):
        return f'<ScanResult {self.id} for device {self.device_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'scan_date': self.scan_date.isoformat(),
            'status': self.status,
            'total_files': self.total_files,
            'scanned_files': self.scanned_files,
            'infected_files': self.infected_files,
            'suspicious_files': self.suspicious_files,
            'scan_duration': self.scan_duration
        }

class InfectedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan_result.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    threat_name = db.Column(db.String(100), nullable=False)
    threat_type = db.Column(db.String(50), nullable=False)  # 'malware', 'ransomware', 'suspicious_script', etc.
    detection_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    scan = db.relationship('ScanResult')

    def __repr__(self):
        return f'<InfectedFile {self.file_path} ({self.threat_name})>'

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'file_path': self.file_path,
            'threat_name': self.threat_name,
            'threat_type': self.threat_type,
            'detection_date': self.detection_date.isoformat()
        }
