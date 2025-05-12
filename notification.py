import requests
from dotenv import load_dotenv
from backend.models.db import db
from backend.models.settings import UserSettings

# Load environment variables
load_dotenv()

# Notification service URL
NOTIFICATION_SERVICE_URL = "http://localhost:5001/notify"

def send_connection_notification(device, alert_type):
    """
    Send notification about USB device connection/disconnection

    Args:
        device: USBDevice object
        alert_type: Type of alert (new_connection, disconnection, permission_granted, permission_denied)
    """
    # Get user settings
    settings = UserSettings.query.first()
    if not settings:
        return

    # Prepare notification message
    device_name = device.product_name or "Unknown Device"

    if alert_type == "new_connection":
        subject = "USB Security Alert: New Device Connected"
        message = f"A new USB device '{device_name}' has been connected to your system.\n\n"
        message += f"Device Details:\n"
        message += f"- Manufacturer: {device.manufacturer or 'Unknown'}\n"
        message += f"- Serial Number: {device.serial_number or 'Unknown'}\n"
        message += f"- Mount Point: {device.mount_point or 'Unknown'}\n\n"
        message += "Please check your USB Monitor Dashboard for more details."

    elif alert_type == "disconnection":
        subject = "USB Security Alert: Device Disconnected"
        message = f"USB device '{device_name}' has been disconnected from your system."

    elif alert_type == "permission_granted":
        subject = "USB Security Alert: Device Access Granted"
        message = f"Access has been granted to USB device '{device_name}'."

    elif alert_type == "permission_denied":
        subject = "USB Security Alert: Device Access Denied"
        message = f"Access has been denied to USB device '{device_name}'."

    else:
        return

    # Send email notification if enabled
    if settings.email_notifications and settings.email:
        send_email(settings.email, subject, message)

    # Send SMS notification if enabled
    if settings.sms_notifications and settings.phone:
        send_sms(settings.phone, f"{subject}: {device_name}")

def send_malware_notification(device, scan_result, alert=None):
    """
    Send notification about scan results

    Args:
        device: USBDevice object
        scan_result: ScanResult object
        alert: Alert object (optional)
    """
    # Get user settings
    settings = UserSettings.query.first()
    if not settings:
        return

    # Prepare notification message
    device_name = device.product_name or "Unknown Device"
    device_id = device.id
    device_serial = device.serial_number or "Unknown"
    device_manufacturer = device.manufacturer or "Unknown"

    # Create detailed device information
    device_details = (
        f"Device ID: {device_id}\n"
        f"Device Name: {device_name}\n"
        f"Manufacturer: {device_manufacturer}\n"
        f"Serial Number: {device_serial}\n"
        f"Files Scanned: {scan_result.scanned_files} of {scan_result.total_files}\n"
        f"Scan Duration: {scan_result.scan_duration:.2f} seconds\n"
        f"Infected Files: {scan_result.infected_files}\n"
        f"Suspicious Files: {scan_result.suspicious_files}"
    )

    # Determine notification type based on scan results
    if scan_result.infected_files > 0:
        subject = "MALICIOUS USB DETECTED"
        message = f"⚠️ SECURITY ALERT: Malicious files detected on USB device '{device_name}'.\n\nThis device may contain harmful software that could damage your system or compromise your data. Please disconnect the device immediately and contact your security team.\n\n{device_details}"
        sms_message = f"MALICIOUS USB DETECTED: {device_name} contains malicious files. BE SECURE - disconnect device immediately!"
    elif scan_result.suspicious_files > 0:
        subject = "SUSPICIOUS USB DETECTED"
        message = f"⚠️ WARNING: Suspicious files detected on USB device '{device_name}'.\n\nThis device contains files that exhibit unusual behavior. Exercise caution when using this device and avoid opening suspicious files.\n\n{device_details}"
        sms_message = f"SUSPICIOUS USB DETECTED: {device_name} contains suspicious files. BE SECURE - use with caution!"
    else:
        subject = "SECURE USB CONNECTED"
        message = f"✅ SECURE: USB device '{device_name}' has been scanned and no threats were found.\n\nThis device appears to be safe to use. The device has been granted read-only access by default for additional security.\n\n{device_details}"
        sms_message = f"Sent from your Twilio trial account - SECURE: USB device \"{device_name}\" has been scanned and no threats were found.\n\nThis device appears to be safe to use. The device has been granted read-only access by default for additional security.\n\nDevice ID: {device_id}\nDevice Name: {device_name}\nManufacturer: {device_manufacturer}\nSerial Number: {device_serial}\nFiles Scanned: {scan_result.scanned_files} of {scan_result.total_files}\nScan Duration: {scan_result.scan_duration:.2f} seconds\nInfected Files: {scan_result.infected_files}\nSuspicious Files: {scan_result.suspicious_files}"

    # Send email notification if enabled
    if settings.email_notifications and settings.email:
        email_sent = send_email(settings.email, subject, message)
        if alert and email_sent:
            alert.email_sent = True

    # Send SMS notification if enabled
    if settings.sms_notifications and settings.phone:
        sms_sent = send_sms(settings.phone, sms_message)
        if alert and sms_sent:
            alert.sms_sent = True

    if alert:
        db.session.commit()

def send_email(recipient, subject, message):
    """
    Send an email notification

    Args:
        recipient: Email address of the recipient
        subject: Email subject
        message: Email message
    """
    try:
        # Use direct SMTP instead of notification service
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Email configuration
        EMAIL_USERNAME = "chaitanyasai9391@gmail.com"
        EMAIL_PASSWORD = "vvkdquyanoswsvso"

        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject

        # Add message body
        msg.attach(MIMEText(message, 'plain'))

        # Connect to SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_USERNAME, recipient, text)
        server.quit()

        print(f"Email notification sent directly to {recipient}")
        return True

    except Exception as e:
        print(f"Error sending email notification: {e}")
        return False

def send_sms(recipient, message):
    """
    Send an SMS notification using Twilio

    Args:
        recipient: Phone number of the recipient
        message: SMS message
    """
    try:
        # Use the notification service to send SMS
        payload = {
            "type": "sms",
            "message": message,
            "phone": recipient
        }

        response = requests.post(NOTIFICATION_SERVICE_URL, json=payload)
        response_data = response.json()

        if response.status_code == 200 and response_data.get('sms', {}).get('success'):
            print(f"SMS notification sent to {recipient}")
            return True
        else:
            error = response_data.get('sms', {}).get('error', 'Unknown error')
            print(f"Error sending SMS notification: {error}")
            return False

    except Exception as e:
        print(f"Error sending SMS notification: {e}")
        return False
