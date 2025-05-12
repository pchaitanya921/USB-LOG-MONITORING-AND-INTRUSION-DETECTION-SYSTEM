"""
Enhanced Notification Service for USB Monitor
Provides improved SMS notifications with detailed file information,
customizable formats, multiple recipients, and better error handling.
"""

import os
import logging
import time
import json
import socket
import platform
import threading
import queue
from datetime import datetime
from twilio.rest import Client
import vonage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("notification_service.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("notification_service")

# Default configuration
DEFAULT_CONFIG = {
    "sms_enabled": True,
    "sms_provider": "twilio",
    "phone_numbers": [],
    "twilio_account_sid": "",
    "twilio_auth_token": "",
    "twilio_phone_number": "",
    "nexmo_api_key": "",
    "nexmo_api_secret": "",
    "nexmo_phone_number": "",
    "notification_levels": {
        "connect": True,
        "disconnect": False,
        "scan_start": False,
        "scan_complete": True,
        "threat_detected": True,
        "suspicious_detected": True,
        "system_error": True
    },
    "message_format": "standard",  # brief, standard, detailed
    "include_file_details": True,
    "include_location": True,
    "max_files_in_sms": 5,
    "retry_attempts": 3,
    "retry_delay": 60,  # seconds
    "rate_limit": 5,    # max messages per minute
    "batch_notifications": False,
    "batch_interval": 300  # seconds
}

# Threat level definitions
THREAT_LEVELS = {
    "critical": {
        "name": "CRITICAL",
        "description": "Confirmed malicious file that poses immediate danger",
        "action": "Disconnect device immediately and quarantine"
    },
    "high": {
        "name": "HIGH",
        "description": "Likely malicious file with high confidence",
        "action": "Disconnect device and investigate"
    },
    "medium": {
        "name": "MEDIUM",
        "description": "Suspicious file that may be malicious",
        "action": "Use caution and scan with additional tools"
    },
    "low": {
        "name": "LOW",
        "description": "Potentially unwanted program or suspicious behavior",
        "action": "Monitor and investigate if necessary"
    },
    "info": {
        "name": "INFO",
        "description": "Informational detection, not necessarily malicious",
        "action": "No immediate action required"
    }
}

class EnhancedNotificationService:
    """Enhanced notification service with improved SMS capabilities"""
    
    def __init__(self, config_path=None):
        """Initialize the notification service"""
        self.config = DEFAULT_CONFIG.copy()
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        # Initialize clients
        self.twilio_client = None
        self.vonage_client = None
        
        # Initialize notification queue and worker thread
        self.notification_queue = queue.Queue()
        self.worker_thread = None
        self.stop_event = threading.Event()
        
        # Initialize rate limiting
        self.message_timestamps = []
        self.message_lock = threading.Lock()
        
        # Initialize clients based on configuration
        self._initialize_clients()
        
        # Start worker thread if enabled
        if self.config["sms_enabled"]:
            self._start_worker()
    
    def _initialize_clients(self):
        """Initialize SMS provider clients"""
        if self.config["sms_provider"] == "twilio":
            if self.config["twilio_account_sid"] and self.config["twilio_auth_token"]:
                try:
                    self.twilio_client = Client(
                        self.config["twilio_account_sid"],
                        self.config["twilio_auth_token"]
                    )
                    logger.info("Twilio client initialized")
                except Exception as e:
                    logger.error(f"Error initializing Twilio client: {str(e)}")
        
        elif self.config["sms_provider"] == "nexmo":
            if self.config["nexmo_api_key"] and self.config["nexmo_api_secret"]:
                try:
                    self.vonage_client = vonage.Client(
                        key=self.config["nexmo_api_key"],
                        secret=self.config["nexmo_api_secret"]
                    )
                    self.vonage_sms = vonage.Sms(self.vonage_client)
                    logger.info("Vonage/Nexmo client initialized")
                except Exception as e:
                    logger.error(f"Error initializing Vonage/Nexmo client: {str(e)}")
    
    def _start_worker(self):
        """Start the notification worker thread"""
        if self.worker_thread and self.worker_thread.is_alive():
            return
        
        self.stop_event.clear()
        self.worker_thread = threading.Thread(
            target=self._notification_worker,
            daemon=True
        )
        self.worker_thread.start()
        logger.info("Notification worker thread started")
    
    def _notification_worker(self):
        """Worker thread to process notification queue"""
        while not self.stop_event.is_set():
            try:
                # Get notification from queue with timeout
                try:
                    notification = self.notification_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process notification
                self._process_notification(notification)
                
                # Mark task as done
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in notification worker: {str(e)}")
        
        logger.info("Notification worker thread stopped")
    
    def _process_notification(self, notification):
        """Process a notification from the queue"""
        notification_type = notification.get("type")
        
        # Check if this notification type is enabled
        if not self.config["notification_levels"].get(notification_type, False):
            logger.debug(f"Notification type {notification_type} is disabled")
            return
        
        # Apply rate limiting
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded, delaying notification")
            # Put back in queue with delay
            threading.Timer(
                self.config["retry_delay"],
                lambda: self.notification_queue.put(notification)
            ).start()
            return
        
        # Send notification based on provider
        if self.config["sms_provider"] == "twilio":
            self._send_twilio_sms(notification)
        elif self.config["sms_provider"] == "nexmo":
            self._send_vonage_sms(notification)
    
    def _check_rate_limit(self):
        """Check if we're within rate limits"""
        with self.message_lock:
            current_time = time.time()
            
            # Remove timestamps older than 1 minute
            self.message_timestamps = [
                ts for ts in self.message_timestamps
                if current_time - ts < 60
            ]
            
            # Check if we're at the limit
            if len(self.message_timestamps) >= self.config["rate_limit"]:
                return False
            
            # Add current timestamp
            self.message_timestamps.append(current_time)
            return True
    
    def _send_twilio_sms(self, notification):
        """Send SMS using Twilio"""
        if not self.twilio_client:
            logger.error("Twilio client not initialized")
            return False
        
        message_body = notification.get("message", "")
        recipients = notification.get("recipients", self.config["phone_numbers"])
        
        if not recipients:
            logger.warning("No recipients specified for SMS")
            return False
        
        success = True
        
        for recipient in recipients:
            # Validate phone number format
            if not recipient or not recipient.startswith('+'):
                logger.warning(f"Invalid phone number format: {recipient}")
                success = False
                continue
            
            # Send message with retry
            for attempt in range(self.config["retry_attempts"]):
                try:
                    message = self.twilio_client.messages.create(
                        body=message_body,
                        from_=self.config["twilio_phone_number"],
                        to=recipient
                    )
                    
                    logger.info(f"SMS sent to {recipient} (SID: {message.sid}, Status: {message.status})")
                    break
                    
                except Exception as e:
                    logger.error(f"Error sending SMS to {recipient} (attempt {attempt+1}): {str(e)}")
                    
                    if attempt < self.config["retry_attempts"] - 1:
                        logger.info(f"Retrying in {self.config['retry_delay']} seconds...")
                        time.sleep(self.config["retry_delay"])
                    else:
                        logger.error(f"Failed to send SMS to {recipient} after {self.config['retry_attempts']} attempts")
                        success = False
        
        return success
    
    def _send_vonage_sms(self, notification):
        """Send SMS using Vonage/Nexmo"""
        if not self.vonage_client or not self.vonage_sms:
            logger.error("Vonage/Nexmo client not initialized")
            return False
        
        message_body = notification.get("message", "")
        recipients = notification.get("recipients", self.config["phone_numbers"])
        
        if not recipients:
            logger.warning("No recipients specified for SMS")
            return False
        
        success = True
        
        for recipient in recipients:
            # Validate phone number format
            if not recipient or not recipient.startswith('+'):
                logger.warning(f"Invalid phone number format: {recipient}")
                success = False
                continue
            
            # Send message with retry
            for attempt in range(self.config["retry_attempts"]):
                try:
                    response = self.vonage_sms.send_message({
                        'from': self.config["nexmo_phone_number"],
                        'to': recipient,
                        'text': message_body
                    })
                    
                    if response["messages"][0]["status"] == "0":
                        logger.info(f"SMS sent to {recipient} (ID: {response['messages'][0]['message-id']})")
                        break
                    else:
                        error = response["messages"][0]["error-text"]
                        logger.error(f"Error sending SMS to {recipient}: {error}")
                        
                        if attempt < self.config["retry_attempts"] - 1:
                            logger.info(f"Retrying in {self.config['retry_delay']} seconds...")
                            time.sleep(self.config["retry_delay"])
                        else:
                            logger.error(f"Failed to send SMS to {recipient} after {self.config['retry_attempts']} attempts")
                            success = False
                            
                except Exception as e:
                    logger.error(f"Error sending SMS to {recipient} (attempt {attempt+1}): {str(e)}")
                    
                    if attempt < self.config["retry_attempts"] - 1:
                        logger.info(f"Retrying in {self.config['retry_delay']} seconds...")
                        time.sleep(self.config["retry_delay"])
                    else:
                        logger.error(f"Failed to send SMS to {recipient} after {self.config['retry_attempts']} attempts")
                        success = False
        
        return success
    
    def _get_system_info(self):
        """Get system information for location data"""
        system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "username": os.getlogin(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Try to get IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            system_info["ip_address"] = s.getsockname()[0]
            s.close()
        except:
            system_info["ip_address"] = "Unknown"
        
        return system_info
    
    def _format_message(self, notification_type, device_info, scan_results=None, custom_message=None):
        """Format message based on notification type and format preference"""
        message_format = self.config["message_format"]
        
        # Get system info if location is enabled
        system_info = self._get_system_info() if self.config["include_location"] else None
        
        # Start with the prefix (remove "Sent from your Twilio trial account - " in production)
        message = "Sent from your Twilio trial account - "
        
        # Add notification type header
        if notification_type == "connect":
            message += "USB CONNECTED: "
        elif notification_type == "disconnect":
            message += "USB DISCONNECTED: "
        elif notification_type == "scan_start":
            message += "SCAN STARTED: "
        elif notification_type == "scan_complete":
            if scan_results and scan_results.get("malicious_files"):
                message += "ALERT: "
            elif scan_results and scan_results.get("suspicious_files"):
                message += "WARNING: "
            else:
                message += "SECURE: "
        elif notification_type == "threat_detected":
            message += "ALERT: "
        elif notification_type == "suspicious_detected":
            message += "WARNING: "
        elif notification_type == "system_error":
            message += "SYSTEM ERROR: "
        
        # Add custom message if provided
        if custom_message:
            message += custom_message
        else:
            # Add device information
            device_name = device_info.get("name", "Unknown device")
            
            if notification_type == "connect":
                message += f"USB device \"{device_name}\" has been connected."
            elif notification_type == "disconnect":
                message += f"USB device \"{device_name}\" has been disconnected."
            elif notification_type == "scan_start":
                message += f"Scanning USB device \"{device_name}\"."
            elif notification_type == "scan_complete":
                if scan_results:
                    malicious_count = len(scan_results.get("malicious_files", []))
                    suspicious_count = len(scan_results.get("suspicious_files", []))
                    
                    if malicious_count > 0:
                        message += f"USB device \"{device_name}\" has been scanned and {malicious_count} threats were found."
                        if suspicious_count > 0:
                            message += f" Additionally, {suspicious_count} suspicious files were detected."
                    elif suspicious_count > 0:
                        message += f"USB device \"{device_name}\" has been scanned and {suspicious_count} suspicious items were found."
                    else:
                        message += f"USB device \"{device_name}\" has been scanned and no threats were found."
            elif notification_type == "threat_detected":
                message += f"Malicious files detected on USB device \"{device_name}\"."
            elif notification_type == "suspicious_detected":
                message += f"Suspicious files detected on USB device \"{device_name}\"."
            elif notification_type == "system_error":
                message += f"Error occurred while processing USB device \"{device_name}\"."
        
        # Add a line break
        message += "\n\n"
        
        # Add security status message
        if notification_type == "scan_complete" or notification_type == "threat_detected" or notification_type == "suspicious_detected":
            if scan_results:
                malicious_count = len(scan_results.get("malicious_files", []))
                suspicious_count = len(scan_results.get("suspicious_files", []))
                
                if malicious_count > 0:
                    message += "This device may contain malicious files. The device has been blocked for your security."
                elif suspicious_count > 0:
                    message += "This device contains suspicious files. The device has been granted read-only access for your security."
                else:
                    message += "This device appears to be safe to use. The device has been granted read-only access by default for additional security."
            
            # Add a line break
            message += "\n\n"
        
        # Add device details
        if device_info:
            # Always include basic device info
            device_id = device_info.get("id", "Unknown")
            device_name = device_info.get("name", "Unknown")
            manufacturer = device_info.get("manufacturer", "Unknown")
            serial_number = device_info.get("serial_number", "Unknown")
            
            message += f"Device ID: {device_id}\n"
            message += f"Device Name: {device_name}\n"
            message += f"Manufacturer: {manufacturer}\n"
            message += f"Serial Number: {serial_number}\n"
            
            # Add scan details if available
            if scan_results:
                scanned_files = scan_results.get("scanned_files", 0)
                total_files = scan_results.get("total_files", scanned_files)
                scan_duration = scan_results.get("scan_duration", 0)
                
                # Format duration to one decimal place
                formatted_duration = f"{scan_duration:.1f}" if isinstance(scan_duration, (int, float)) else scan_duration
                
                message += f"Files Scanned: {scanned_files} of {total_files}\n"
                message += f"Scan Duration: {formatted_duration} seconds\n"
        
        # Add file details if available and enabled
        if scan_results and self.config["include_file_details"]:
            malicious_files = scan_results.get("malicious_files", [])
            suspicious_files = scan_results.get("suspicious_files", [])
            
            # Add malicious files
            if malicious_files:
                message += "Infected Files:\n"
                
                # Limit the number of files based on config
                max_files = self.config["max_files_in_sms"]
                
                for i, file_info in enumerate(malicious_files[:max_files]):
                    # Handle both string paths and dictionaries
                    if isinstance(file_info, str):
                        file_path = file_info
                        detection_type = "Unknown"
                        threat_level = "critical"
                    else:
                        file_path = file_info.get("path", "Unknown")
                        detection_type = file_info.get("detection_type", "Unknown")
                        threat_level = file_info.get("threat_level", "critical")
                    
                    # Get threat level info
                    threat_info = THREAT_LEVELS.get(threat_level, THREAT_LEVELS["critical"])
                    
                    # Format file path - use full path for detailed format, basename otherwise
                    if message_format == "detailed":
                        formatted_path = file_path
                    else:
                        formatted_path = os.path.basename(file_path)
                    
                    # Add file info
                    message += f"- {formatted_path}"
                    
                    # Add detection details for detailed format
                    if message_format == "detailed":
                        message += f" ({detection_type}, {threat_info['name']})"
                    
                    message += "\n"
                
                # Add ellipsis if there are more files
                if len(malicious_files) > max_files:
                    message += f"... and {len(malicious_files) - max_files} more\n"
            else:
                message += "Infected Files: None\n"
            
            # Add suspicious files
            if suspicious_files:
                message += "Suspicious Files:\n"
                
                # Limit the number of files based on config
                max_files = self.config["max_files_in_sms"]
                
                for i, file_info in enumerate(suspicious_files[:max_files]):
                    # Handle both string paths and dictionaries
                    if isinstance(file_info, str):
                        file_path = file_info
                        detection_type = "Unknown"
                        threat_level = "medium"
                    else:
                        file_path = file_info.get("path", "Unknown")
                        detection_type = file_info.get("detection_type", "Unknown")
                        threat_level = file_info.get("threat_level", "medium")
                    
                    # Get threat level info
                    threat_info = THREAT_LEVELS.get(threat_level, THREAT_LEVELS["medium"])
                    
                    # Format file path - use full path for detailed format, basename otherwise
                    if message_format == "detailed":
                        formatted_path = file_path
                    else:
                        formatted_path = os.path.basename(file_path)
                    
                    # Add file info
                    message += f"- {formatted_path}"
                    
                    # Add detection details for detailed format
                    if message_format == "detailed":
                        message += f" ({detection_type}, {threat_info['name']})"
                    
                    message += "\n"
                
                # Add ellipsis if there are more files
                if len(suspicious_files) > max_files:
                    message += f"... and {len(suspicious_files) - max_files} more\n"
            else:
                message += "Suspicious Files: None\n"
        
        # Add location information if enabled
        if system_info and self.config["include_location"] and message_format == "detailed":
            message += f"\nLocation: {system_info['hostname']} ({system_info['ip_address']})"
            message += f"\nUser: {system_info['username']}"
            message += f"\nTime: {system_info['timestamp']}"
        
        # Add recommended action for threats
        if notification_type in ["threat_detected", "suspicious_detected"] or (
            notification_type == "scan_complete" and (
                scan_results and (
                    scan_results.get("malicious_files") or 
                    scan_results.get("suspicious_files")
                )
            )
        ):
            message += "\nRECOMMENDED ACTION: "
            
            if scan_results and scan_results.get("malicious_files"):
                message += THREAT_LEVELS["critical"]["action"]
            elif scan_results and scan_results.get("suspicious_files"):
                message += THREAT_LEVELS["medium"]["action"]
        
        return message
    
    def send_notification(self, notification_type, device_info, scan_results=None, custom_message=None, recipients=None):
        """Send a notification"""
        # Check if SMS is enabled
        if not self.config["sms_enabled"]:
            logger.info("SMS notifications are disabled")
            return False
        
        # Check if this notification type is enabled
        if not self.config["notification_levels"].get(notification_type, False):
            logger.info(f"Notifications for {notification_type} are disabled")
            return False
        
        # Format message
        message = self._format_message(notification_type, device_info, scan_results, custom_message)
        
        # Use provided recipients or default from config
        if not recipients:
            recipients = self.config["phone_numbers"]
        
        # Check if we have recipients
        if not recipients:
            logger.warning("No recipients configured for SMS notifications")
            return False
        
        # Create notification object
        notification = {
            "type": notification_type,
            "message": message,
            "recipients": recipients,
            "device_info": device_info,
            "scan_results": scan_results,
            "timestamp": time.time()
        }
        
        # Add to queue
        self.notification_queue.put(notification)
        logger.info(f"Notification queued: {notification_type}")
        
        return True
    
    def stop(self):
        """Stop the notification service"""
        self.stop_event.set()
        
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)
            logger.info("Notification worker thread stopped")
    
    def update_config(self, new_config):
        """Update the configuration"""
        self.config.update(new_config)
        
        # Reinitialize clients if provider changed
        self._initialize_clients()
        
        # Restart worker if needed
        if self.config["sms_enabled"] and (not self.worker_thread or not self.worker_thread.is_alive()):
            self._start_worker()
        
        logger.info("Configuration updated")
        return True
    
    def add_phone_number(self, phone_number):
        """Add a phone number to the recipients list"""
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        if phone_number not in self.config["phone_numbers"]:
            self.config["phone_numbers"].append(phone_number)
            logger.info(f"Added phone number: {phone_number}")
            return True
        
        return False
    
    def remove_phone_number(self, phone_number):
        """Remove a phone number from the recipients list"""
        if phone_number in self.config["phone_numbers"]:
            self.config["phone_numbers"].remove(phone_number)
            logger.info(f"Removed phone number: {phone_number}")
            return True
        
        return False
    
    def test_notification(self, recipient=None):
        """Send a test notification"""
        # Use provided recipient or first from config
        if not recipient and self.config["phone_numbers"]:
            recipient = self.config["phone_numbers"][0]
        
        if not recipient:
            logger.warning("No recipient for test notification")
            return False
        
        # Create test device info
        device_info = {
            "id": "TEST-123",
            "name": "Test Device",
            "manufacturer": "Test Manufacturer",
            "serial_number": "TEST-SN-123456"
        }
        
        # Create test scan results
        scan_results = {
            "scanned_files": 100,
            "total_files": 100,
            "scan_duration": 2.5,
            "malicious_files": [],
            "suspicious_files": []
        }
        
        # Send test notification
        return self.send_notification(
            "scan_complete",
            device_info,
            scan_results,
            "This is a test notification from USB Monitor.",
            [recipient]
        )

# Example usage
if __name__ == "__main__":
    # Create notification service
    notification_service = EnhancedNotificationService()
    
    # Update configuration with Twilio credentials
    notification_service.update_config({
        "sms_enabled": True,
        "sms_provider": "twilio",
        "phone_numbers": ["+919944273645"],
        "twilio_account_sid": "AC94656f2081ae1c98c4cece8dd68ca056",
        "twilio_auth_token": "70cfd6672bc72163dd2077bc3562ffa9",
        "twilio_phone_number": "+19082631380",
        "message_format": "detailed",
        "include_file_details": True,
        "include_location": True
    })
    
    # Send a test notification
    notification_service.test_notification()
    
    # Wait for notifications to be sent
    time.sleep(5)
    
    # Stop the service
    notification_service.stop()
