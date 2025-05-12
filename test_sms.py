#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test SMS Notification
Sends a test SMS notification using Twilio
"""

import os
from twilio.rest import Client

# Twilio credentials
account_sid = "AC94656f2081ae1c98c4cece8dd68ca056"
auth_token = "70cfd6672bc72163dd2077bc3562ffa9"
twilio_number = "+19082631380"
recipient_number = "+919944273645"

# Create message
message = """Sent from your Twilio trial account - ALERT: USB device "Kingston DataTraveler" has been scanned and 2 malicious files were found.

This device contains malicious files. The device has been blocked for your security.

Device ID: 789
Device Name: Kingston DataTraveler
Manufacturer: Kingston
Serial Number: 1234567890
Files Scanned: 120 of 120
Scan Duration: 2.8 seconds
Infected Files:
- C:/Users/chait/USB/malicious_file.exe
- C:/Users/chait/USB/ransomware.bin
Suspicious Files:
- C:/Users/chait/USB/suspicious_script.js
"""

try:
    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Send message
    sms = client.messages.create(
        body=message,
        from_=twilio_number,
        to=recipient_number
    )

    print(f"SMS sent successfully! SID: {sms.sid}")
    print(f"Status: {sms.status}")

except Exception as e:
    print(f"Error sending SMS: {str(e)}")
