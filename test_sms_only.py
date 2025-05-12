#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test SMS Notifications Only
"""

def send_test_sms():
    """Send a test SMS with detailed logging"""
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
        message = "USB Monitor Test: This is a test SMS notification from the USB Monitoring System."
        
        print(f"Sending SMS to {recipient_phone} using Twilio")
        print(f"Account SID: {account_sid}")
        print(f"From number: {twilio_number}")
        print(f"Message: {message}")
        
        # Create client
        client = Client(account_sid, auth_token)
        
        # Send message
        sms = client.messages.create(
            body=message,
            from_=twilio_number,
            to=recipient_phone
        )
        
        print(f"SMS sent successfully! SID: {sms.sid}")
        print(f"SMS Status: {sms.status}")
        return True
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        
        # Try with a simpler message
        try:
            print("Trying with a simpler message...")
            from twilio.rest import Client
            client = Client("AC94656f2081ae1c98c4cece8dd68ca056", "70cfd6672bc72163dd2077bc3562ffa9")
            simple_message = "USB Monitor Alert: Test notification"
            sms = client.messages.create(
                body=simple_message,
                from_="+19082631380",
                to="+919944273645"
            )
            print(f"Simple SMS sent successfully! SID: {sms.sid}")
            return True
        except Exception as final_error:
            print(f"Final SMS sending error: {str(final_error)}")
            return False

if __name__ == "__main__":
    print("Testing SMS notifications...")
    success = send_test_sms()
    if success:
        print("SMS test completed successfully!")
    else:
        print("SMS test failed!")
