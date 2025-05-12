from .db import db

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=True)
    auto_scan = db.Column(db.Boolean, default=True)
    require_permission = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<UserSettings {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'auto_scan': self.auto_scan,
            'require_permission': self.require_permission,
            'email': self.email,
            'phone': self.phone
        }
