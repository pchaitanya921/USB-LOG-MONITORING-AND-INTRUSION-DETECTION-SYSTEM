#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Email Notifications Only
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

def send_test_email():
    """Send a test email with detailed logging"""
    # Email configuration
    email_username = "chaitanyasai9391@gmail.com"
    email_password = "vvkdquyanoswsvso"
    email_recipient = "chaitanyasai401@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg["Subject"] = "USB Monitor Test Email"
        msg["From"] = email_username
        msg["To"] = email_recipient
        
        # Add text content
        text = """
        This is a test email from the USB Monitoring System.
        
        If you're receiving this email, it means the email notification system is working correctly.
        
        This is an automated message. Please do not reply.
        """
        msg.attach(MIMEText(text, "plain"))
        
        # Add HTML content
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #0078d7; color: white; padding: 10px 20px; }
                .content { padding: 20px; border: 1px solid #ddd; }
                .footer { font-size: 12px; color: #777; margin-top: 20px; }
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
                    <p>This is an automated message. Please do not reply.</p>
                </div>
                <div class="footer">
                    <p>USB Monitor - Secure USB Monitoring System</p>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))
        
        # Connect to SMTP server with detailed logging
        print(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)  # Enable verbose debug output
        
        # Start TLS
        print("Starting TLS")
        context = ssl.create_default_context()
        server.starttls(context=context)
        
        # Login
        print(f"Logging in as {email_username}")
        server.login(email_username, email_password)
        
        # Send email
        print(f"Sending email to {email_recipient}")
        server.send_message(msg)
        
        # Close connection
        server.quit()
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing email notifications...")
    success = send_test_email()
    if success:
        print("Email test completed successfully!")
    else:
        print("Email test failed!")
