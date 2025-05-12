# Real-Time USB Security Notification System

This document provides instructions on how to set up and use the real-time notification system for the USB Security Monitoring application.

## Overview

The notification system allows you to receive real-time alerts via:
1. Browser notifications (works even when the browser is in the background)
2. Email notifications (with fallback to opening your email client)
3. SMS notifications (with fallback to opening your SMS app)

You'll receive alerts for important events such as:
- New USB device connections
- Malware detection on USB devices
- Suspicious activity on USB devices
- Device permission changes

## Notification Types

### Browser Notifications
These notifications appear as system notifications on your desktop or mobile device, even when the browser is minimized or in the background. They require permission from your browser.

### Email Notifications
Email notifications are sent to the email address you specify in the settings. If the server-side email sending fails, the system will offer to open your default email client with the notification pre-filled.

### SMS Notifications
SMS notifications are sent to the phone number you specify in the settings. If the server-side SMS sending fails, the system will offer to open your default SMS app with the notification pre-filled.

## Setup Instructions

### 1. Enable Browser Notifications

When you first load the application, you'll be prompted to allow notifications. Click "Allow" to enable browser notifications.

If you previously denied notifications, you'll need to change your browser settings:
- **Chrome**: Click the lock icon in the address bar > Site Settings > Notifications > Allow
- **Firefox**: Click the lock icon in the address bar > Permissions > Notifications > Allow
- **Safari**: Preferences > Websites > Notifications > Allow for this website

### 2. Configure Email and SMS Notifications

1. Go to the Settings tab
2. In the Alert Settings section:
   - Enable Email Notifications and/or SMS Notifications
   - Enter your email address for email notifications
   - Enter your phone number for SMS notifications (include country code, e.g., +1 for US)
3. Click "Save Settings"
4. Click "Test Notifications" to verify your setup

### 3. Server Setup (Optional)

For full server-side email and SMS functionality:

1. Place the `send_notification.php` file on your web server in the same directory as your HTML files.
2. Ensure PHP is properly configured on your server.
3. For SMS notifications, set up a Twilio account and update the PHP file with your credentials.

## Troubleshooting

### Browser Notifications Not Working

1. Check if notifications are enabled in your browser settings
2. Make sure you're using a modern browser that supports the Notifications API
3. If using HTTPS, make sure your SSL certificate is valid
4. Check the browser console for any error messages

### Email Notifications Not Working

1. Check if you've entered a valid email address in the settings
2. If using the fallback method, make sure you have an email client configured on your device
3. Check the browser console for any error messages

### SMS Notifications Not Working

1. Check if you've entered a valid phone number with country code
2. If using the fallback method, make sure you have an SMS app configured on your device
3. Check the browser console for any error messages

## How It Works

The notification system uses a multi-layered approach:

1. **Service Worker**: A background script that can show notifications even when the browser is not in focus
2. **Web Notifications API**: Used to display system notifications on desktop and mobile
3. **Server-side PHP**: For sending emails and SMS messages (when available)
4. **Fallback Mechanisms**: Opens email/SMS apps directly if server-side sending fails

This ensures that you'll receive notifications through at least one channel, even if some methods are unavailable.

## Security Considerations

- Browser notifications are only visible on the device where the application is running
- Email and SMS notifications can be received on any device
- Consider using HTTPS to protect sensitive information
- Be cautious about entering sensitive information in a local application

## Testing the System

You can test the notification system at any time by:

1. Going to the Settings tab
2. Clicking the "Test Notifications" button in the Alert Settings section

This will send test notifications through all enabled channels.
