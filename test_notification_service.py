#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Notification Service
Sends notifications using the PHP notification service
"""

import requests
import json
import os
import sys

def send_email_notification(email, subject, message):
    """Send an email notification using the PHP service"""
    url = "http://localhost/send_notification.php"
    
    # Prepare data
    data = {
        "type": "email",
        "email": email,
        "subject": subject,
        "message": message
    }
    
    # Send request
    try:
        print(f"Sending email notification to {email}...")
        response = requests.post(url, json=data)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("Email notification sent successfully!")
                return True
            else:
                print(f"Failed to send email notification: {result.get('message')}")
                return False
        else:
            print(f"HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")
        return False

def send_sms_notification(phone, message):
    """Send an SMS notification using the PHP service"""
    url = "http://localhost/send_notification.php"
    
    # Prepare data
    data = {
        "type": "sms",
        "phone": phone,
        "message": message
    }
    
    # Send request
    try:
        print(f"Sending SMS notification to {phone}...")
        response = requests.post(url, json=data)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("SMS notification sent successfully!")
                return True
            else:
                print(f"Failed to send SMS notification: {result.get('message')}")
                return False
        else:
            print(f"HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending SMS notification: {str(e)}")
        return False

def send_direct_email():
    """Send an email directly using SMTP"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Email configuration
    email_username = "chaitanyasai9391@gmail.com"
    email_password = "vvkdquyanoswsvso"
    email_recipient = "chaitanyasai401@gmail.com"
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg["Subject"] = "USB Monitor Direct Email Test"
        msg["From"] = email_username
        msg["To"] = email_recipient
        
        # Add text content
        text = "This is a direct test email from the USB Monitoring System."
        msg.attach(MIMEText(text, "plain"))
        
        # Connect to SMTP server
        print(f"Connecting to SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        
        # Login
        print(f"Logging in as {email_username}")
        server.login(email_username, email_password)
        
        # Send email
        print(f"Sending direct email to {email_recipient}")
        server.send_message(msg)
        
        # Close connection
        server.quit()
        print("Direct email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Error sending direct email: {str(e)}")
        return False

def send_direct_sms():
    """Send an SMS directly using Twilio"""
    try:
        # Try to import twilio
        try:
            from twilio.rest import Client
        except ImportError:
            print("Twilio SDK not installed. Installing...")
            import subprocess
            subprocess.check_call(["pip", "install", "twilio"])
            from twilio.rest import Client
            print("Twilio installed successfully")
        
        # Twilio credentials
        account_sid = "AC94656f2081ae1c98c4cece8dd68ca056"
        auth_token = "70cfd6672bc72163dd2077bc3562ffa9"
        twilio_number = "+19082631380"
        recipient_phone = "+919944273645"
        
        # Message content
        message = "USB Monitor Direct SMS Test: This is a direct test SMS from the USB Monitoring System."
        
        print(f"Sending direct SMS to {recipient_phone} using Twilio")
        
        # Create client
        client = Client(account_sid, auth_token)
        
        # Send message
        sms = client.messages.create(
            body=message,
            from_=twilio_number,
            to=recipient_phone
        )
        
        print(f"Direct SMS sent successfully! SID: {sms.sid}")
        return True
        
    except Exception as e:
        print(f"Error sending direct SMS: {str(e)}")
        return False

def main():
    """Main function"""
    print("USB Notification Service Test")
    print("============================")
    
    # Test options
    print("\nSelect a test option:")
    print("1. Send email via PHP service")
    print("2. Send SMS via PHP service")
    print("3. Send direct email via SMTP")
    print("4. Send direct SMS via Twilio")
    print("5. Run all tests")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == "1":
        email = input("Enter recipient email: ")
        send_email_notification(
            email,
            "USB Monitor Test Notification",
            "This is a test notification from the USB Monitoring System."
        )
    elif choice == "2":
        phone = input("Enter recipient phone number: ")
        send_sms_notification(
            phone,
            "USB Monitor Test: This is a test notification from the USB Monitoring System."
        )
    elif choice == "3":
        send_direct_email()
    elif choice == "4":
        send_direct_sms()
    elif choice == "5":
        print("\nRunning all tests...")
        
        print("\n1. Testing email via PHP service...")
        send_email_notification(
            "chaitanyasai401@gmail.com",
            "USB Monitor Test Notification",
            "This is a test notification from the USB Monitoring System."
        )
        
        print("\n2. Testing SMS via PHP service...")
        send_sms_notification(
            "+919944273645",
            "USB Monitor Test: This is a test notification from the USB Monitoring System."
        )
        
        print("\n3. Testing direct email via SMTP...")
        send_direct_email()
        
        print("\n4. Testing direct SMS via Twilio...")
        send_direct_sms()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
