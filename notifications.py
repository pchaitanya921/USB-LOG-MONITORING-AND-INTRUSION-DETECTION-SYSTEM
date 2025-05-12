import smtplib
import os
import logging
import json
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notifications.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("usb_notifications")

# Check if Twilio is available for SMS
HAS_TWILIO = importlib.util.find_spec("twilio") is not None

# Load configuration from .env file if it exists
def load_config():
    config = {
        "EMAIL_ENABLED": False,
        "EMAIL_USERNAME": "",
        "EMAIL_PASSWORD": "",
        "EMAIL_RECIPIENT": "",
        "EMAIL_SERVER": "smtp.gmail.com",
        "EMAIL_PORT": 587,
        
        "SMS_ENABLED": False,
        "TWILIO_ACCOUNT_SID": "",
        "TWILIO_AUTH_TOKEN": "",
        "TWILIO_PHONE_NUMBER": "",
        "ALERT_RECIPIENT_PHONE": ""
    }
    
    # Try to load from .env file
    try:
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip().strip('"\'')
            
            # Convert string values to appropriate types
            config["EMAIL_ENABLED"] = config.get("EMAIL_USERNAME") and config.get("EMAIL_PASSWORD")
            config["EMAIL_PORT"] = int(config.get("EMAIL_PORT", 587))
            config["SMS_ENABLED"] = (HAS_TWILIO and config.get("TWILIO_ACCOUNT_SID") and 
                                    config.get("TWILIO_AUTH_TOKEN") and config.get("TWILIO_PHONE_NUMBER"))
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
    
    # Try to load from notifications.json if it exists
    try:
        if os.path.exists("notifications.json"):
            with open("notifications.json", "r") as f:
                json_config = json.load(f)
                config.update(json_config)
    except Exception as e:
        logger.error(f"Error loading JSON configuration: {str(e)}")
    
    return config

# Save configuration to JSON file
def save_config(config):
    try:
        # Remove sensitive information before saving
        save_config = {k: v for k, v in config.items() if not k.endswith("PASSWORD") and not k.endswith("TOKEN")}
        
        with open("notifications.json", "w") as f:
            json.dump(save_config, f, indent=4)
        
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")
        return False

class NotificationManager:
    def __init__(self):
        self.config = load_config()
        self.twilio_client = None
        
        # Initialize Twilio client if available
        if self.config["SMS_ENABLED"]:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(
                    self.config["TWILIO_ACCOUNT_SID"],
                    self.config["TWILIO_AUTH_TOKEN"]
                )
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Twilio client: {str(e)}")
                self.config["SMS_ENABLED"] = False
    
    def update_config(self, new_config):
        """Update notification configuration."""
        self.config.update(new_config)
        
        # Update derived settings
        self.config["EMAIL_ENABLED"] = bool(self.config.get("EMAIL_USERNAME") and self.config.get("EMAIL_PASSWORD"))
        self.config["SMS_ENABLED"] = (HAS_TWILIO and self.config.get("TWILIO_ACCOUNT_SID") and 
                                     self.config.get("TWILIO_AUTH_TOKEN") and self.config.get("TWILIO_PHONE_NUMBER"))
        
        # Reinitialize Twilio client if needed
        if self.config["SMS_ENABLED"] and not self.twilio_client:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(
                    self.config["TWILIO_ACCOUNT_SID"],
                    self.config["TWILIO_AUTH_TOKEN"]
                )
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Twilio client: {str(e)}")
                self.config["SMS_ENABLED"] = False
        
        # Save configuration
        save_config(self.config)
        
        return self.config
    
    def send_email(self, subject, message):
        """Send email notification."""
        if not self.config["EMAIL_ENABLED"]:
            logger.warning("Email notifications are not enabled")
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config["EMAIL_USERNAME"]
            msg["To"] = self.config["EMAIL_RECIPIENT"]
            msg["Subject"] = subject
            
            msg.attach(MIMEText(message, "plain"))
            
            server = smtplib.SMTP(self.config["EMAIL_SERVER"], self.config["EMAIL_PORT"])
            server.starttls()
            server.login(self.config["EMAIL_USERNAME"], self.config["EMAIL_PASSWORD"])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {self.config['EMAIL_RECIPIENT']}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_sms(self, message):
        """Send SMS notification."""
        if not self.config["SMS_ENABLED"] or not self.twilio_client:
            logger.warning("SMS notifications are not enabled")
            return False
        
        try:
            sms = self.twilio_client.messages.create(
                body=message,
                from_=self.config["TWILIO_PHONE_NUMBER"],
                to=self.config["ALERT_RECIPIENT_PHONE"]
            )
            
            logger.info(f"SMS sent successfully to {self.config['ALERT_RECIPIENT_PHONE']}, SID: {sms.sid}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    def notify_usb_connected(self, device_info):
        """Send notification when USB device is connected."""
        try:
            # Create notification messages
            subject = "USB Security Alert: New USB Device Connected"
            
            message = f"""
USB Security Alert: New USB Device Connected

Device Details:
- Name: {device_info.get('name', 'Unknown')}
- Drive: {device_info.get('drive_letter', 'N/A')}
- Size: {device_info.get('size', 'Unknown')}
- Connection Time: {device_info.get('connection_time', datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))}

This is an automated notification from your USB Monitoring System.
            """
            
            sms_message = f"USB ALERT: {device_info.get('name', 'Unknown device')} connected at {device_info.get('connection_time', 'now')}. Drive: {device_info.get('drive_letter', 'N/A')}"
            
            # Send notifications
            email_sent = False
            sms_sent = False
            
            if self.config["EMAIL_ENABLED"]:
                email_sent = self.send_email(subject, message)
            
            if self.config["SMS_ENABLED"]:
                sms_sent = self.send_sms(sms_message)
            
            return email_sent or sms_sent
        
        except Exception as e:
            logger.error(f"Error sending USB connected notification: {str(e)}")
            return False
    
    def notify_malware_detected(self, scan_results):
        """Send notification when malware is detected."""
        try:
            if not scan_results.get("malicious_files") and not scan_results.get("suspicious_files"):
                return False
            
            # Create notification messages
            subject = "USB Security Alert: Malware Detected"
            
            message = f"""
USB Security Alert: Malware Detected

Scan Details:
- Scan Time: {scan_results.get('start_time', 'Unknown')}
- Files Scanned: {scan_results.get('scanned_files', 0)}
- Malicious Files: {len(scan_results.get('malicious_files', []))}
- Suspicious Files: {len(scan_results.get('suspicious_files', []))}

"""
            
            # Add details of malicious files
            if scan_results.get("malicious_files"):
                message += "Malicious Files:\n"
                for file in scan_results["malicious_files"][:5]:  # Limit to first 5 files
                    message += f"- {file.get('path', 'Unknown')}: {file.get('threat', 'Unknown threat')}\n"
                
                if len(scan_results["malicious_files"]) > 5:
                    message += f"... and {len(scan_results['malicious_files']) - 5} more\n"
                
                message += "\n"
            
            # Add details of suspicious files
            if scan_results.get("suspicious_files"):
                message += "Suspicious Files:\n"
                for file in scan_results["suspicious_files"][:5]:  # Limit to first 5 files
                    message += f"- {file.get('path', 'Unknown')}: {file.get('reason', 'Unknown reason')}\n"
                
                if len(scan_results["suspicious_files"]) > 5:
                    message += f"... and {len(scan_results['suspicious_files']) - 5} more\n"
            
            message += "\nThis is an automated notification from your USB Monitoring System."
            
            # Create SMS message (shorter)
            malicious_count = len(scan_results.get('malicious_files', []))
            suspicious_count = len(scan_results.get('suspicious_files', []))
            
            sms_message = f"USB SECURITY ALERT: {malicious_count} malicious and {suspicious_count} suspicious files detected during scan at {scan_results.get('start_time', 'now')}."
            
            # Send notifications
            email_sent = False
            sms_sent = False
            
            if self.config["EMAIL_ENABLED"]:
                email_sent = self.send_email(subject, message)
            
            if self.config["SMS_ENABLED"]:
                sms_sent = self.send_sms(sms_message)
            
            return email_sent or sms_sent
        
        except Exception as e:
            logger.error(f"Error sending malware detected notification: {str(e)}")
            return False
    
    def test_notifications(self):
        """Test both email and SMS notifications."""
        results = {
            "email": {"enabled": self.config["EMAIL_ENABLED"], "success": False, "error": None},
            "sms": {"enabled": self.config["SMS_ENABLED"], "success": False, "error": None}
        }
        
        # Test email
        if self.config["EMAIL_ENABLED"]:
            try:
                success = self.send_email(
                    "USB Monitoring System - Test Notification",
                    "This is a test notification from your USB Monitoring System. If you received this, email notifications are working correctly."
                )
                results["email"]["success"] = success
            except Exception as e:
                results["email"]["error"] = str(e)
        
        # Test SMS
        if self.config["SMS_ENABLED"]:
            try:
                success = self.send_sms(
                    "USB Monitoring System - Test notification. If you received this, SMS notifications are working correctly."
                )
                results["sms"]["success"] = success
            except Exception as e:
                results["sms"]["error"] = str(e)
        
        return results

# Example usage
if __name__ == "__main__":
    notification_manager = NotificationManager()
    
    # Test notifications
    test_results = notification_manager.test_notifications()
    print(json.dumps(test_results, indent=4))
