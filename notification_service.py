import os
import json
import smtplib
import datetime
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Twilio configuration
TWILIO_ACCOUNT_SID = "AC94656f2081ae1c98c4cece8dd68ca056"
TWILIO_AUTH_TOKEN = "70cfd6672bc72163dd2077bc3562ffa9"
TWILIO_PHONE_NUMBER = "+19082631380"
ALERT_RECIPIENT_PHONE = "+919944273645"

# Email configuration
EMAIL_USERNAME = "chaitanyasai9391@gmail.com"
EMAIL_PASSWORD = "vvkdquyanoswsvso"
EMAIL_RECIPIENT = "chaitanyasai401@gmail.com"  # Default recipient

def send_sms(to_number, message_body):
    """Send SMS using Twilio"""
    logger.info(f"Attempting to send SMS to {to_number}")
    try:
        # Validate phone number format
        if not to_number or not to_number.startswith('+'):
            logger.warning(f"Invalid phone number format: {to_number}")
            return {
                "success": False,
                "error": "Invalid phone number format. Must start with '+' followed by country code."
            }

        logger.debug(f"SMS message: {message_body}")
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        logger.info(f"Creating Twilio message from {TWILIO_PHONE_NUMBER} to {to_number}")
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )

        logger.info(f"SMS sent successfully. SID: {message.sid}, Status: {message.status}")
        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status
        }
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

def send_email(subject, message_body, to_email=None):
    """Send email using SMTP"""
    logger.info(f"Attempting to send email to {to_email if to_email else EMAIL_RECIPIENT}")
    try:
        # Validate email
        recipient = to_email if to_email else EMAIL_RECIPIENT
        logger.info(f"Email recipient resolved to: {recipient}")

        if not recipient or '@' not in recipient:
            logger.warning(f"Invalid email format: {recipient}")
            return {
                "success": False,
                "error": "Invalid email format"
            }

        logger.debug(f"Email subject: {subject}")
        logger.debug(f"Email message: {message_body}")

        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject

        # Convert plain text to HTML for better formatting
        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0f172a; color: white; padding: 10px 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9fafb; }}
                .footer {{ font-size: 12px; text-align: center; margin-top: 20px; color: #6b7280; }}
                .alert {{ padding: 10px; margin-bottom: 15px; border-radius: 4px; }}
                .alert-danger {{ background-color: #fee2e2; border-left: 4px solid #ef4444; color: #b91c1c; }}
                .alert-warning {{ background-color: #fef3c7; border-left: 4px solid #f59e0b; color: #b45309; }}
                .alert-success {{ background-color: #d1fae5; border-left: 4px solid #10b981; color: #047857; }}
                .details {{ background-color: #e5e7eb; padding: 10px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>USB Security Monitor</h2>
                </div>
                <div class="content">
        """

        # Determine alert type and add appropriate styling
        if "MALICIOUS" in message_body:
            html_message += f'<div class="alert alert-danger"><strong>⚠️ SECURITY ALERT:</strong> Malicious USB device detected!</div>'
        elif "SUSPICIOUS" in message_body:
            html_message += f'<div class="alert alert-warning"><strong>⚠️ WARNING:</strong> Suspicious USB device detected!</div>'
        else:
            html_message += f'<div class="alert alert-success"><strong>✅ SECURE:</strong> Safe USB device connected.</div>'

        # Format the message body
        message_parts = message_body.split('\n\n')
        main_message = message_parts[0]
        details = message_parts[1] if len(message_parts) > 1 else ""

        html_message += f"""
                    <p>{main_message}</p>
                    <h3>Device Details:</h3>
                    <div class="details">{details}</div>
                    <p>Please take appropriate security measures if needed.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from your USB Security Monitoring System.</p>
                    <p>© {datetime.datetime.now().year} USB Security Monitor</p>
                </div>
            </div>
        </body>
        </html>
        """

        logger.debug("Attaching HTML message to email")
        msg.attach(MIMEText(html_message, 'html'))

        logger.info("Connecting to SMTP server")
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.set_debuglevel(1)  # Enable verbose debug output
            logger.info("SMTP connection established")

            logger.info("Starting TLS")
            server.starttls()
            logger.info("TLS started successfully")

            logger.info(f"Logging in as {EMAIL_USERNAME}")
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            logger.info("Login successful")

            text = msg.as_string()
            logger.info(f"Sending email from {EMAIL_USERNAME} to {recipient}")
            server.sendmail(EMAIL_USERNAME, recipient, text)
            logger.info("Email sent via SMTP")

            server.quit()
            logger.info("SMTP connection closed")
        except smtplib.SMTPException as smtp_error:
            logger.error(f"SMTP Error: {str(smtp_error)}")
            raise

        logger.info("Email sent successfully")
        return {
            "success": True,
            "message": "Email sent successfully"
        }
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@app.route('/notify', methods=['POST'])
@app.route('/api/notify', methods=['POST'])
def notify():
    """API endpoint to send notifications"""
    logger.info("Received notification request")
    try:
        data = request.json
        logger.debug(f"Request data: {data}")

        notification_type = data.get('type', 'all')
        subject = data.get('subject', 'USB Security Alert')
        message = data.get('message', 'No message provided')
        phone = data.get('phone', ALERT_RECIPIENT_PHONE)
        email = data.get('email', EMAIL_RECIPIENT)

        logger.info(f"Sending {notification_type} notification to phone: {phone}, email: {email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message: {message}")

        response = {
            "sms": None,
            "email": None
        }

        if notification_type in ['sms', 'all']:
            logger.info(f"Sending SMS to {phone}")
            response["sms"] = send_sms(phone, message)
            logger.info(f"SMS result: {response['sms']}")

        if notification_type in ['email', 'all']:
            logger.info(f"Sending email to {email}")
            response["email"] = send_email(subject, message, email)
            logger.info(f"Email result: {response['email']}")

        logger.info(f"Notification response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in notify endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-notifications', methods=['POST'])
def test_notifications():
    """API endpoint to test notifications"""
    logger.info("Received test notification request")
    try:
        data = request.json
        logger.debug(f"Test request data: {data}")

        phone = data.get('phone', ALERT_RECIPIENT_PHONE)
        email = data.get('email', EMAIL_RECIPIENT)

        logger.info(f"Sending test notifications to phone: {phone}, email: {email}")

        sms_result = send_sms(
            phone,
            "This is a test notification from USB Security Monitor. Your notification system is working correctly."
        )
        logger.info(f"Test SMS result: {sms_result}")

        email_result = send_email(
            "USB Security Monitor - Test Notification",
            """This is a test notification from your USB Security Monitor.

Your notification system is working correctly.
If you did not request this test, please check your system security.
            """,
            email
        )
        logger.info(f"Test email result: {email_result}")

        response = {
            "sms": sms_result,
            "email": email_result
        }

        logger.info(f"Test notification response: {response}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in test-notifications endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """API endpoint to check if service is running"""
    logger.info("Health check requested")
    return jsonify({
        "status": "ok",
        "service": "USB Security Monitor Notification Service",
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for basic connectivity test"""
    logger.info("Root endpoint accessed")
    return jsonify({
        "message": "USB Log Monitoring and Intrusion Detection System API"
    })

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint that returns all routes"""
    logger.info("Test endpoint accessed")
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": str(rule)
        })
    return jsonify({
        "message": "Test endpoint",
        "routes": routes
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
