#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notifications Utility
Handles sending notifications via desktop, email, and SMS
"""

import os
import platform
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

class NotificationManager:
    """Class for managing notifications"""
    def __init__(self, config=None):
        self.config = config or {}
        self.tray_icon = None

        # Load configuration from file if not provided
        if not config:
            self._load_config()

    def _load_config(self):
        """Load configuration from file"""
        try:
            import json
            import os

            # Get the path to the config file
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                     "config", "notification_config.json")

            # Check if the file exists
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.config = json.load(f)
                print(f"Loaded notification configuration from {config_path}")
            else:
                print(f"Notification configuration file not found at {config_path}")
        except Exception as e:
            print(f"Error loading notification configuration: {str(e)}")

    def setup_tray_icon(self, parent=None):
        """Set up system tray icon"""
        if not self.config.get("system_tray", True):
            return

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(parent)
        self.tray_icon.setIcon(QIcon("assets/icons/app_icon.png"))
        self.tray_icon.setToolTip("USB Monitoring System")

        # Create tray menu
        tray_menu = QMenu()

        # Add actions
        show_action = QAction("Show", parent)
        show_action.triggered.connect(parent.show)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        exit_action = QAction("Exit", parent)
        exit_action.triggered.connect(parent.close)
        tray_menu.addAction(exit_action)

        # Set tray menu
        self.tray_icon.setContextMenu(tray_menu)

        # Show tray icon
        self.tray_icon.show()

    def send_notification(self, title, message, level="info", device_info=None):
        """Send a notification"""
        # Check if notifications are enabled
        if not self.config.get("desktop_notifications", True):
            return

        # Send desktop notification
        self._send_desktop_notification(title, message, level)

        # Send email notification if enabled
        if self.config.get("email_notifications", False):
            # Check notification level
            if (level == "info" and self.config.get("notify_connect", True)) or \
               (level == "warning" and self.config.get("notify_scan", True)) or \
               (level == "critical" and self.config.get("notify_threat", True)):
                # Send in a separate thread to avoid blocking
                threading.Thread(
                    target=self._send_email_notification,
                    args=(title, message, level, device_info),
                    daemon=True
                ).start()

        # Send SMS notification if enabled
        if self.config.get("sms_notifications", False):
            # Always send SMS for scan results and threats
            # Modified to send SMS for all levels, not just critical
            print(f"SMS notification triggered for level: {level}")
            print(f"SMS config: {self.config.get('phone_number')}, Provider: {self.config.get('sms_provider')}")

            # Send in a separate thread to avoid blocking
            threading.Thread(
                target=self._send_sms_notification,
                args=(title, message, level, device_info),
                daemon=True
            ).start()

    def _send_desktop_notification(self, title, message, level="info"):
        """Send a desktop notification"""
        if self.tray_icon and self.tray_icon.supportsMessages():
            # Map level to QSystemTrayIcon.MessageIcon
            icon_map = {
                "info": QSystemTrayIcon.Information,
                "warning": QSystemTrayIcon.Warning,
                "critical": QSystemTrayIcon.Critical
            }
            icon = icon_map.get(level, QSystemTrayIcon.Information)

            # Show message
            self.tray_icon.showMessage(title, message, icon, 5000)
        else:
            # Fallback to platform-specific notification
            system = platform.system()

            if system == "Windows":
                # Windows notification (requires win10toast package)
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(title, message, duration=5, threaded=True)
                except:
                    pass

            elif system == "Darwin":  # macOS
                # macOS notification
                try:
                    os.system(f"""
                        osascript -e 'display notification "{message}" with title "{title}"'
                    """)
                except:
                    pass

            elif system == "Linux":
                # Linux notification (requires notify-send)
                try:
                    os.system(f'notify-send "{title}" "{message}"')
                except:
                    pass

    def _send_email_notification(self, title, message, level="info", device_info=None):
        """Send an email notification"""
        # Check if email is configured
        email_address = self.config.get("email_address", "")
        if not email_address:
            print("Email address not configured, using default")
            email_address = "chaitanyasai401@gmail.com"

        try:
            # Get email configuration with hardcoded defaults
            smtp_server = self.config.get("email_smtp_server", "smtp.gmail.com")
            smtp_port = self.config.get("email_smtp_port", 587)
            email_username = self.config.get("email_username", "chaitanyasai9391@gmail.com")
            email_password = self.config.get("email_password", "vvkdquyanoswsvso")
            email_from = self.config.get("email_from", email_username)

            # Check if credentials are provided
            if not email_username or not email_password:
                print("Email credentials not configured, using defaults")
                email_username = "chaitanyasai9391@gmail.com"
                email_password = "vvkdquyanoswsvso"
                email_from = email_username

            # Print debug info
            print(f"Sending email to {email_address}")
            print(f"Using SMTP server: {smtp_server}:{smtp_port}")
            print(f"Using email account: {email_username}")

            # Create message
            msg = MIMEMultipart("alternative")

            # Use custom SMS message as a base for email subject if available
            if device_info and 'custom_sms' in device_info:
                # Extract the first line for the subject
                first_line = device_info['custom_sms'].split('\n')[0]
                msg["Subject"] = first_line
            else:
                msg["Subject"] = f"USB Monitor: {title}"

            msg["From"] = email_from
            msg["To"] = email_address

            # Create plain text message - use custom SMS message if available
            plain_text = device_info.get('custom_sms', message) if device_info else message

            # Create HTML message with device info
            html_message = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #0078d7; color: white; padding: 10px 20px; }}
                    .content {{ padding: 20px; border: 1px solid #ddd; }}
                    .device-info {{ background-color: #f9f9f9; padding: 15px; margin-top: 20px; border-left: 4px solid #0078d7; }}
                    .footer {{ font-size: 12px; color: #777; margin-top: 20px; }}
                    .alert-info {{ border-left: 4px solid #0078d7; }}
                    .alert-warning {{ border-left: 4px solid #ff9800; }}
                    .alert-critical {{ border-left: 4px solid #f44336; }}
                    .file-list {{ background-color: #f5f5f5; padding: 10px; margin-top: 15px; }}
                    .file-item {{ margin-bottom: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>{title}</h2>
                    </div>
                    <div class="content">
            """

            # Add formatted message based on scan result
            if device_info and 'custom_sms' in device_info:
                # Convert SMS message to HTML paragraphs
                sms_lines = device_info['custom_sms'].split('\n')
                for line in sms_lines:
                    if line.strip():  # Skip empty lines
                        html_message += f"<p>{line}</p>"
            else:
                html_message += f"<p>{message}</p>"

            # Add device info if available
            if device_info:
                html_message += f"""
                        <div class="device-info alert-{level}">
                            <h3>Device Information</h3>
                            <p><strong>Device Name:</strong> {device_info.get('name', 'Unknown')}</p>
                            <p><strong>Device ID:</strong> {device_info.get('id', 'Unknown')}</p>
                """

                # Add manufacturer and serial if available
                if 'manufacturer' in device_info:
                    html_message += f"<p><strong>Manufacturer:</strong> {device_info['manufacturer']}</p>"
                if 'serial_number' in device_info:
                    html_message += f"<p><strong>Serial Number:</strong> {device_info['serial_number']}</p>"

                # Add connection time if available
                if 'connection_time' in device_info:
                    html_message += f"<p><strong>Connection Time:</strong> {device_info['connection_time']}</p>"

                # Add scan details if available
                if 'total_files' in device_info and 'scanned_files' in device_info:
                    html_message += f"<p><strong>Files Scanned:</strong> {device_info['scanned_files']} of {device_info['total_files']}</p>"
                if 'scan_duration' in device_info:
                    formatted_duration = f"{device_info['scan_duration']:.1f}" if isinstance(device_info['scan_duration'], (int, float)) else device_info['scan_duration']
                    html_message += f"<p><strong>Scan Duration:</strong> {formatted_duration} seconds</p>"

                # Add additional device info if available
                if 'device_type' in device_info:
                    html_message += f"<p><strong>Device Type:</strong> {device_info['device_type']}</p>"
                if 'vendor_id' in device_info and 'product_id' in device_info:
                    html_message += f"<p><strong>Hardware ID:</strong> VID_{device_info['vendor_id']}&PID_{device_info['product_id']}</p>"
                if 'size' in device_info:
                    html_message += f"<p><strong>Size:</strong> {device_info['size']}</p>"

                html_message += """
                        </div>
                """

                # Add malicious files list if available
                if 'malicious_files' in device_info and device_info['malicious_files']:
                    html_message += f"""
                        <div class="file-list alert-critical">
                            <h3>Malicious Files Detected</h3>
                    """
                    for file in device_info['malicious_files']:
                        html_message += f'<div class="file-item">• {os.path.basename(file)}</div>'
                    html_message += """
                        </div>
                    """

                # Add suspicious files list if available
                if 'suspicious_files' in device_info and device_info['suspicious_files']:
                    html_message += f"""
                        <div class="file-list alert-warning">
                            <h3>Suspicious Files Detected</h3>
                    """
                    for file in device_info['suspicious_files']:
                        html_message += f'<div class="file-item">• {os.path.basename(file)}</div>'
                    html_message += """
                        </div>
                    """

            # Add footer
            html_message += f"""
                        <div class="footer">
                            <p>This is an automated message from USB Monitoring System. Please do not reply to this email.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Attach parts
            text_part = MIMEText(plain_text, "plain")
            html_part = MIMEText(html_message, "html")
            msg.attach(text_part)
            msg.attach(html_part)

            # Create secure connection and send email
            import ssl
            context = ssl.create_default_context()

            # Connect to SMTP server with detailed logging
            print(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.set_debuglevel(1)  # Enable verbose debug output

            try:
                print("Starting TLS connection")
                server.starttls(context=context)

                print(f"Logging in with username: {email_username}")
                server.login(email_username, email_password)

                print(f"Sending email to {email_address}")
                server.send_message(msg)

                print("Email sent successfully")
                server.quit()
                return True

            except smtplib.SMTPAuthenticationError:
                print("SMTP Authentication Error - Check your username and password")
                # Try with hardcoded credentials as fallback
                try:
                    print("Trying with hardcoded credentials")
                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls(context=context)
                    server.login("chaitanyasai9391@gmail.com", "vvkdquyanoswsvso")
                    server.send_message(msg)
                    server.quit()
                    print("Email sent with hardcoded credentials")
                    return True
                except Exception as fallback_error:
                    print(f"Fallback email attempt failed: {str(fallback_error)}")
                    return False

            except Exception as smtp_error:
                print(f"SMTP Error: {str(smtp_error)}")
                server.quit()
                return False

        except Exception as e:
            print(f"Error preparing email: {str(e)}")

            # Try a very simple email as last resort
            try:
                simple_msg = MIMEMultipart()
                simple_msg["Subject"] = "USB Monitor Alert"
                simple_msg["From"] = "chaitanyasai9391@gmail.com"
                simple_msg["To"] = "chaitanyasai401@gmail.com"
                simple_msg.attach(MIMEText("USB Monitor security alert. Please check your system.", "plain"))

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login("chaitanyasai9391@gmail.com", "vvkdquyanoswsvso")
                server.send_message(simple_msg)
                server.quit()
                print("Simple fallback email sent")
                return True
            except Exception as final_error:
                print(f"Final email sending error: {str(final_error)}")
                return False

    def _send_sms_notification(self, title, message, level="info", device_info=None):
        """Send an SMS notification"""
        # Check if phone number is configured
        phone_number = self.config.get("phone_number", "")
        if not phone_number:
            return

        # Get SMS provider configuration
        sms_provider = self.config.get("sms_provider", "twilio")

        # Use custom SMS message if available, otherwise format a default one
        if device_info and 'custom_sms' in device_info:
            sms_message = device_info['custom_sms']
        else:
            # Format default message
            sms_message = f"USB Monitor: {title} - {message}"

            # Add minimal device info if available
            if device_info:
                device_name = device_info.get('name', 'Unknown device')
                sms_message += f"\nDevice: {device_name}"

                # Add connection time if available
                if 'connection_time' in device_info:
                    sms_message += f"\nTime: {device_info['connection_time']}"

        # Send SMS based on provider
        if sms_provider == "twilio":
            return self._send_twilio_sms(sms_message, phone_number)
        elif sms_provider == "nexmo":
            return self._send_nexmo_sms(sms_message, phone_number)
        else:
            print(f"Unsupported SMS provider: {sms_provider}")
            return False

    def _send_twilio_sms(self, message, recipient_phone):
        """Send SMS using Twilio"""
        try:
            # Force install twilio if not already installed
            try:
                from twilio.rest import Client
            except ImportError:
                print("Twilio SDK not installed. Installing...")
                import subprocess
                subprocess.check_call(["pip", "install", "twilio"])
                from twilio.rest import Client
                print("Twilio installed successfully")

            # Always use hardcoded credentials to ensure they work
            account_sid = "AC94656f2081ae1c98c4cece8dd68ca056"
            auth_token = "70cfd6672bc72163dd2077bc3562ffa9"
            twilio_number = "+19082631380"

            # Always use your phone number
            recipient_phone = "+919944273645"

            # Format phone number if needed
            if not recipient_phone.startswith('+'):
                recipient_phone = '+' + recipient_phone

            print(f"Sending SMS to {recipient_phone} using Twilio")
            print(f"Account SID: {account_sid}")
            print(f"From number: {twilio_number}")
            print(f"Message length: {len(message)}")
            print(f"Message preview: {message[:100]}...")  # Print first 100 chars

            # Create client
            client = Client(account_sid, auth_token)

            # Send message with error handling
            try:
                sms = client.messages.create(
                    body=message,
                    from_=twilio_number,
                    to=recipient_phone
                )
                print(f"SMS notification sent to {recipient_phone} (SID: {sms.sid})")
                print(f"SMS Status: {sms.status}")
                return True
            except Exception as sms_error:
                print(f"Error in Twilio message creation: {str(sms_error)}")

                # Try with a shorter message if the original is too long
                if len(message) > 1000:
                    short_message = message[:900] + "... (message truncated)"
                    print("Trying with shorter message")
                    sms = client.messages.create(
                        body=short_message,
                        from_=twilio_number,
                        to=recipient_phone
                    )
                    print(f"Shortened SMS sent to {recipient_phone} (SID: {sms.sid})")
                    return True
                return False

        except Exception as e:
            print(f"Error sending SMS via Twilio: {str(e)}")

            # Try one more time with a very simple message
            try:
                from twilio.rest import Client
                client = Client("AC94656f2081ae1c98c4cece8dd68ca056", "70cfd6672bc72163dd2077bc3562ffa9")
                simple_message = "USB Monitor Alert: Security notification from your USB monitoring system."
                sms = client.messages.create(
                    body=simple_message,
                    from_="+19082631380",
                    to="+919944273645"
                )
                print(f"Simple SMS sent as fallback (SID: {sms.sid})")
                return True
            except Exception as final_error:
                print(f"Final SMS sending error: {str(final_error)}")
                return False

    def _send_nexmo_sms(self, message, recipient_phone):
        """Send SMS using Nexmo/Vonage"""
        try:
            import vonage

            # Get Nexmo/Vonage credentials
            api_key = self.config.get("nexmo_api_key", "")
            api_secret = self.config.get("nexmo_api_secret", "")
            nexmo_number = self.config.get("nexmo_phone_number", "")

            # Check if credentials are provided
            if not api_key or not api_secret:
                print("Nexmo/Vonage credentials not configured")
                return False

            # Initialize client
            client = vonage.Client(key=api_key, secret=api_secret)
            sms = vonage.Sms(client)

            # Send message
            response = sms.send_message({
                'from': nexmo_number,
                'to': recipient_phone,
                'text': message
            })

            # Check response
            if response["messages"][0]["status"] == "0":
                print(f"SMS notification sent to {recipient_phone}")
                return True
            else:
                error = response["messages"][0]["error-text"]
                print(f"Error sending SMS via Nexmo/Vonage: {error}")
                return False

        except ImportError:
            print("Vonage SDK not installed. Install with: pip install vonage")
            return False
        except Exception as e:
            print(f"Error sending SMS via Nexmo/Vonage: {str(e)}")
            return False

    def send_device_connected_notification(self, device, security_status="secured"):
        """Send notification when a device is connected"""
        # Determine subject and message based on security status
        if security_status == "malicious":
            title = "ALERT: Malicious USB Device Detected"
            message = f"A malicious USB device has been detected and blocked: {device.name}"
            level = "critical"
        elif security_status == "suspicious":
            title = "WARNING: Suspicious USB Device Detected"
            message = f"A suspicious USB device has been detected: {device.name}"
            level = "warning"
        else:
            title = "USB Device Connected"
            message = f"A USB device has been connected: {device.name}"
            level = "info"

        # Get device info
        device_info = device.to_dict() if hasattr(device, 'to_dict') else {
            "id": getattr(device, 'id', 'Unknown'),
            "name": getattr(device, 'name', 'Unknown'),
            "connection_time": getattr(device, 'connection_time', 'Unknown')
        }

        # Send notification
        self.send_notification(title, message, level, device_info)

    def send_device_disconnected_notification(self, device):
        """Send notification when a device is disconnected"""
        title = "USB Device Disconnected"
        message = f"A USB device has been disconnected: {device.name}"
        level = "info"

        # Get device info
        device_info = device.to_dict() if hasattr(device, 'to_dict') else {
            "id": getattr(device, 'id', 'Unknown'),
            "name": getattr(device, 'name', 'Unknown'),
            "connection_time": getattr(device, 'connection_time', 'Unknown')
        }

        # Send notification
        self.send_notification(title, message, level, device_info)

    def send_scan_completed_notification(self, device, scan_result):
        """Send notification when a scan is completed"""
        # Get malicious and suspicious files count
        malicious_files = getattr(scan_result, 'malicious_files', [])
        suspicious_files = getattr(scan_result, 'suspicious_files', [])

        threats_found = len(malicious_files)
        suspicious_found = len(suspicious_files)

        # Get scan details
        scan_duration = getattr(scan_result, 'scan_duration', 0)
        total_files = getattr(scan_result, 'total_files', 0)
        scanned_files = getattr(scan_result, 'scanned_files', 0)

        # Get device details
        device_id = getattr(device, 'id', 'Unknown')
        device_name = getattr(device, 'name', 'Unknown')
        manufacturer = getattr(device, 'manufacturer', 'Unknown')
        serial_number = getattr(device, 'serial_number', 'Unknown')

        # Format duration to one decimal place
        formatted_duration = f"{scan_duration:.1f}" if isinstance(scan_duration, (int, float)) else scan_duration

        if threats_found > 0:
            # Malicious files found
            title = f"ALERT: {threats_found} Threats Found on USB Device"
            message = f"Malware scan detected {threats_found} threats on device: {device_name}"
            level = "critical"

            # Format SMS message for threats found
            sms_message = f"Sent from your Twilio trial account - ALERT: USB device \"{device_name}\" has been scanned and {threats_found} threats were found.\n\n"
            sms_message += f"This device may contain malicious files. The device has been blocked for your security.\n\n"
            sms_message += f"Device ID: {device_id}\n"
            sms_message += f"Device Name: {device_name}\n"
            sms_message += f"Manufacturer: {manufacturer}\n"
            sms_message += f"Serial Number: {serial_number}\n"
            sms_message += f"Files Scanned: {scanned_files} of {total_files}\n"
            sms_message += f"Scan Duration: {formatted_duration} seconds\n"

            # Add malicious files list
            if malicious_files:
                sms_message += f"Infected Files: \n"
                for file in malicious_files[:3]:  # Limit to first 3 files to avoid too long SMS
                    sms_message += f"- {os.path.basename(file)}\n"
                if len(malicious_files) > 3:
                    sms_message += f"... and {len(malicious_files) - 3} more\n"

            # Add suspicious files list if any
            if suspicious_files:
                sms_message += f"Suspicious Files: \n"
                for file in suspicious_files[:2]:  # Limit to first 2 files
                    sms_message += f"- {os.path.basename(file)}\n"
                if len(suspicious_files) > 2:
                    sms_message += f"... and {len(suspicious_files) - 2} more\n"

        elif suspicious_found > 0:
            # Suspicious files found
            title = f"WARNING: {suspicious_found} Suspicious Items Found on USB Device"
            message = f"Malware scan detected {suspicious_found} suspicious items on device: {device_name}"
            level = "warning"

            # Format SMS message for suspicious files
            sms_message = f"Sent from your Twilio trial account - WARNING: USB device \"{device_name}\" has been scanned and {suspicious_found} suspicious items were found.\n\n"
            sms_message += f"This device contains suspicious files. The device has been granted read-only access for your security.\n\n"
            sms_message += f"Device ID: {device_id}\n"
            sms_message += f"Device Name: {device_name}\n"
            sms_message += f"Manufacturer: {manufacturer}\n"
            sms_message += f"Serial Number: {serial_number}\n"
            sms_message += f"Files Scanned: {scanned_files} of {total_files}\n"
            sms_message += f"Scan Duration: {formatted_duration} seconds\n"

            # Add suspicious files list
            if suspicious_files:
                sms_message += f"Suspicious Files: \n"
                for file in suspicious_files[:3]:  # Limit to first 3 files
                    sms_message += f"- {os.path.basename(file)}\n"
                if len(suspicious_files) > 3:
                    sms_message += f"... and {len(suspicious_files) - 3} more\n"

        else:
            # No threats found
            title = "USB Device Scan Completed"
            message = f"Malware scan completed with no threats found on device: {device_name}"
            level = "info"

            # Format SMS message for clean scan
            sms_message = f"Sent from your Twilio trial account - SECURE: USB device \"{device_name}\" has been scanned and no threats were found.\n\n"
            sms_message += f"This device appears to be safe to use. The device has been granted read-only access by default for additional security.\n\n"
            sms_message += f"Device ID: {device_id}\n"
            sms_message += f"Device Name: {device_name}\n"
            sms_message += f"Manufacturer: {manufacturer}\n"
            sms_message += f"Serial Number: {serial_number}\n"
            sms_message += f"Files Scanned: {scanned_files} of {total_files}\n"
            sms_message += f"Scan Duration: {formatted_duration} seconds\n"
            sms_message += f"Infected Files: None\n"
            sms_message += f"Suspicious Files: None\n"

        # Get device info
        device_info = device.to_dict() if hasattr(device, 'to_dict') else {
            "id": device_id,
            "name": device_name,
            "manufacturer": manufacturer,
            "serial_number": serial_number,
            "connection_time": getattr(device, 'connection_time', 'Unknown')
        }

        # Add scan result info
        if hasattr(scan_result, 'to_dict'):
            device_info.update(scan_result.to_dict())

        # Add custom SMS message to device info
        device_info['custom_sms'] = sms_message

        # Send notification
        self.send_notification(title, message, level, device_info)

    def send_security_alert_notification(self, alert_type, device=None, description=None):
        """Send notification for security alerts"""
        title = f"SECURITY ALERT: {alert_type.upper()}"

        if device:
            message = f"Security alert ({alert_type}) for device: {device.name}"
        else:
            message = f"Security alert: {alert_type}"

        if description:
            message += f"\n{description}"

        # Get device info if available
        device_info = None
        if device:
            device_info = device.to_dict() if hasattr(device, 'to_dict') else {
                "id": getattr(device, 'id', 'Unknown'),
                "name": getattr(device, 'name', 'Unknown'),
                "connection_time": getattr(device, 'connection_time', 'Unknown')
            }

        # Send notification
        self.send_notification(title, message, "critical", device_info)
