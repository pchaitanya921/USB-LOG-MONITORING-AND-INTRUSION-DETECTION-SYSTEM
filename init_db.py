import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app and models
from app import app, db
from models.settings import UserSettings

def init_database():
    """Initialize the database and create default settings"""
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if settings already exist
        settings = UserSettings.query.first()

        if not settings:
            # Create default settings
            settings = UserSettings(
                email_notifications=True,
                sms_notifications=True,
                auto_scan=True,
                require_permission=True,
                email=os.environ.get('EMAIL_RECIPIENT'),
                phone=os.environ.get('ALERT_RECIPIENT_PHONE')
            )

            db.session.add(settings)
            db.session.commit()

            print("Database initialized with default settings")
        else:
            print("Database already initialized")

if __name__ == "__main__":
    init_database()
