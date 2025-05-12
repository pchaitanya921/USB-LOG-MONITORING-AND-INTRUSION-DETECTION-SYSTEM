# Real-Time USB Security Notification System

This document provides instructions on how to set up and use the real-time notification system for the USB Security Monitoring application.

## Overview

The notification system allows you to receive real-time alerts via email and SMS when important events occur, such as:
- New USB device connections
- Malware detection on USB devices
- Suspicious activity on USB devices
- Device permission changes

## Requirements

### For Email Notifications
- A web server with PHP support (Apache, Nginx, etc.)
- PHP mail() function configured properly on your server
- Valid email address to receive notifications

### For SMS Notifications
- A Twilio account (for production use)
- Twilio Account SID, Auth Token, and phone number
- Valid phone number to receive SMS notifications

## Setup Instructions

### 1. Server Setup

1. Place the `send_notification.php` file on your web server in the same directory as your HTML files.
2. Ensure PHP is properly configured on your server.
3. For email notifications, make sure the PHP mail() function is working correctly.

### 2. Twilio Setup (for SMS notifications in production)

1. Sign up for a Twilio account at https://www.twilio.com/
2. Get your Account SID and Auth Token from the Twilio dashboard
3. Purchase a Twilio phone number for sending SMS
4. Uncomment and update the Twilio code in `send_notification.php` with your credentials:

```php
require_once 'vendor/autoload.php'; // Twilio PHP SDK

$account_sid = 'YOUR_TWILIO_ACCOUNT_SID';
$auth_token = 'YOUR_TWILIO_AUTH_TOKEN';
$twilio_number = 'YOUR_TWILIO_PHONE_NUMBER';

$client = new Twilio\Rest\Client($account_sid, $auth_token);

try {
    $message = $client->messages->create(
        $phone,
        [
            'from' => $twilio_number,
            'body' => $message
        ]
    );
    
    $response['success'] = true;
    $response['sms_sent'] = true;
    $response['message'] = 'SMS notification sent successfully';
} catch (Exception $e) {
    $response['message'] = 'Failed to send SMS notification: ' . $e->getMessage();
}
```

5. Install the Twilio PHP SDK using Composer:
```
composer require twilio/sdk
```

### 3. Configure Notification Settings in the Application

1. Open the USB Security Monitoring application in your browser
2. Go to the Settings tab
3. In the Alert Settings section:
   - Enable Email Notifications and/or SMS Notifications
   - Enter your email address for email notifications
   - Enter your phone number for SMS notifications (include country code, e.g., +1 for US)
4. Click "Save Settings"
5. Click "Test Notifications" to verify your setup

## Troubleshooting

### Email Notifications Not Working

1. Check if your server's PHP mail() function is working correctly
2. Verify that you've entered a valid email address in the settings
3. Check your spam/junk folder for the test notification
4. Look at the browser console for any error messages

### SMS Notifications Not Working

1. Verify that you've entered a valid phone number with country code
2. Check if your Twilio account is active and has sufficient credits
3. Verify that your Twilio credentials are correct in the PHP file
4. Look at the browser console for any error messages
5. Check the `sms_log.txt` file on your server for logged SMS attempts

## Security Considerations

- The current implementation uses a simple PHP script for sending notifications
- For production use, consider implementing proper authentication and rate limiting
- Ensure your server uses HTTPS to protect sensitive information
- Consider encrypting email addresses and phone numbers in storage

## Customizing Notification Templates

You can customize the email and SMS templates by modifying the `send_notification.php` file:

- For email templates, modify the HTML in the `$html_message` variable
- For SMS templates, modify the message format in the Twilio send function

## Support

If you encounter any issues with the notification system, please check the browser console for error messages and review the server logs for more information.
