#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Email functionality
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
EMAIL_USERNAME = "chaitanyasai9391@gmail.com"
EMAIL_PASSWORD = "vvkdquyanoswsvso"
EMAIL_RECIPIENT = "chaitanyasai401@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_test_email():
    """Send a test email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = "USB Monitor Test Email"

        # Create message body
        body = """
        This is a test email from the USB Monitoring System.
        
        If you're receiving this email, it means the email notification system is working correctly.
        
        Device: Test Device
        Manufacturer: Test Manufacturer
        Serial Number: TEST123456789
        Status: Test
        
        This is an automated message. Please do not reply.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create HTML version
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0078d7; color: white; padding: 10px 20px; }}
                .content {{ padding: 20px; border: 1px solid #ddd; }}
                .device-info {{ background-color: #f9f9f9; padding: 15px; margin-top: 20px; border-left: 4px solid #0078d7; }}
                .footer {{ font-size: 12px; color: #777; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>USB Monitor Test Email</h2>
                </div>
                <div class="content">
                    <p>This is a test email from the USB Monitoring System.</p>
                    <p>If you're receiving this email, it means the email notification system is working correctly.</p>
                    
                    <div class="device-info">
                        <h3>Device Information</h3>
                        <p><strong>Device Name:</strong> Test Device</p>
                        <p><strong>Manufacturer:</strong> Test Manufacturer</p>
                        <p><strong>Serial Number:</strong> TEST123456789</p>
                        <p><strong>Status:</strong> Test</p>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message from USB Monitoring System. Please do not reply to this email.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Connect to SMTP server
        print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Enable verbose debug output
        
        # Start TLS
        print("Starting TLS")
        server.starttls()
        
        # Login
        print(f"Logging in as {EMAIL_USERNAME}")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        # Send email
        print(f"Sending email to {EMAIL_RECIPIENT}")
        server.send_message(msg)
        
        # Close connection
        server.quit()
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    send_test_email()
