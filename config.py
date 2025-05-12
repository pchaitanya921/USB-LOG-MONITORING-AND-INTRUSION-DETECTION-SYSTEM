#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration Utility
Handles loading and saving application configuration
"""

import os
import json
from PyQt5.QtCore import QSettings

def get_default_config():
    """Get default configuration"""
    return {
        # General settings
        "start_with_system": False,
        "start_minimized": False,
        "theme": "System",
        "language": "English",

        # Scanning settings
        "scan_on_connect": True,
        "block_on_threat": True,
        "scan_depth": "Quick Scan",
        "scan_interval": 0,
        "scan_executables": True,
        "scan_documents": True,
        "scan_archives": True,
        "scan_all_files": False,

        # Permissions settings
        "default_permission": "Read Only",
        "trusted_devices": True,

        # Notifications settings
        "desktop_notifications": True,
        "email_notifications": False,
        "email_address": "",
        "email_from": "",
        "email_smtp_server": "smtp.gmail.com",
        "email_smtp_port": 587,
        "email_username": "",
        "email_password": "",
        "email_use_tls": True,
        "sms_notifications": False,
        "phone_number": "",
        "sms_provider": "twilio",
        "twilio_account_sid": "",
        "twilio_auth_token": "",
        "twilio_phone_number": "",
        "nexmo_api_key": "",
        "nexmo_api_secret": "",
        "nexmo_phone_number": "",
        "notify_connect": True,
        "notify_disconnect": False,
        "notify_scan": True,
        "notify_threat": True,

        # Advanced settings
        "enable_logging": True,
        "log_level": "Info",
        "log_path": "logs",
        "system_tray": True,
        "minimize_to_tray": True,
        "close_to_tray": True
    }

def load_config():
    """Load configuration from settings"""
    config = get_default_config()

    # Try to load from QSettings
    settings = QSettings("USBMonitor", "USBMonitoringSystem")
    if settings.contains("config"):
        stored_config = settings.value("config")
        if isinstance(stored_config, dict):
            # Update config with stored values
            for key, value in stored_config.items():
                if key in config:
                    config[key] = value

    # Try to load from JSON file as fallback
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                stored_config = json.load(f)
                if isinstance(stored_config, dict):
                    # Update config with stored values
                    for key, value in stored_config.items():
                        if key in config:
                            config[key] = value
        except:
            pass

    return config

def save_config(config):
    """Save configuration to settings"""
    # Save to QSettings
    settings = QSettings("USBMonitor", "USBMonitoringSystem")
    settings.setValue("config", config)

    # Save to JSON file as backup
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    except:
        pass

    return True
