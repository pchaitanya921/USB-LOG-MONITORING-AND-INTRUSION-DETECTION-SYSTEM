import os
import json
import logging
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("device_manager.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("device_manager")

# Permission levels
PERMISSION_BLOCKED = "blocked"
PERMISSION_READ_ONLY = "read_only"
PERMISSION_FULL_ACCESS = "full_access"

# Default settings
DEFAULT_SETTINGS = {
    "default_permission": PERMISSION_READ_ONLY,
    "auto_block_suspicious": True,
    "notify_on_permission_change": True
}

class DeviceManager:
    def __init__(self):
        self.devices = {}
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_devices()
        self.load_settings()
    
    def load_devices(self):
        """Load device permissions from file."""
        try:
            if os.path.exists("device_permissions.json"):
                with open("device_permissions.json", "r") as f:
                    self.devices = json.load(f)
                logger.info(f"Loaded {len(self.devices)} device permissions")
            else:
                logger.info("No device permissions file found, using empty list")
        except Exception as e:
            logger.error(f"Error loading device permissions: {str(e)}")
    
    def save_devices(self):
        """Save device permissions to file."""
        try:
            with open("device_permissions.json", "w") as f:
                json.dump(self.devices, f, indent=4)
            logger.info(f"Saved {len(self.devices)} device permissions")
            return True
        except Exception as e:
            logger.error(f"Error saving device permissions: {str(e)}")
            return False
    
    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists("device_settings.json"):
                with open("device_settings.json", "r") as f:
                    settings = json.load(f)
                    # Update settings, keeping defaults for missing keys
                    for key, value in settings.items():
                        self.settings[key] = value
                logger.info("Loaded device manager settings")
            else:
                logger.info("No settings file found, using defaults")
                self.save_settings()  # Create default settings file
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open("device_settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Saved device manager settings")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            return False
    
    def update_settings(self, new_settings):
        """Update device manager settings."""
        for key, value in new_settings.items():
            if key in self.settings:
                self.settings[key] = value
        
        return self.save_settings()
    
    def get_device_permission(self, device_id):
        """Get permission level for a device."""
        if device_id in self.devices:
            return self.devices[device_id]["permission"]
        return self.settings["default_permission"]
    
    def set_device_permission(self, device_id, device_name, permission):
        """Set permission level for a device."""
        if permission not in [PERMISSION_BLOCKED, PERMISSION_READ_ONLY, PERMISSION_FULL_ACCESS]:
            logger.error(f"Invalid permission level: {permission}")
            return False
        
        # Create or update device entry
        if device_id in self.devices:
            old_permission = self.devices[device_id]["permission"]
            self.devices[device_id]["permission"] = permission
            self.devices[device_id]["last_updated"] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            
            # Add to history
            if "history" not in self.devices[device_id]:
                self.devices[device_id]["history"] = []
            
            self.devices[device_id]["history"].append({
                "old_permission": old_permission,
                "new_permission": permission,
                "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            })
            
            # Limit history to last 10 entries
            if len(self.devices[device_id]["history"]) > 10:
                self.devices[device_id]["history"] = self.devices[device_id]["history"][-10:]
        else:
            self.devices[device_id] = {
                "id": device_id,
                "name": device_name,
                "permission": permission,
                "added": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                "last_updated": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                "history": [{
                    "old_permission": self.settings["default_permission"],
                    "new_permission": permission,
                    "timestamp": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                }]
            }
        
        return self.save_devices()
    
    def remove_device(self, device_id):
        """Remove a device from the permissions list."""
        if device_id in self.devices:
            del self.devices[device_id]
            return self.save_devices()
        return False
    
    def get_all_devices(self):
        """Get all devices with their permissions."""
        return self.devices
    
    def get_whitelist(self):
        """Get all whitelisted devices (full access)."""
        return {k: v for k, v in self.devices.items() if v["permission"] == PERMISSION_FULL_ACCESS}
    
    def get_blacklist(self):
        """Get all blacklisted devices (blocked)."""
        return {k: v for k, v in self.devices.items() if v["permission"] == PERMISSION_BLOCKED}
    
    def handle_new_device(self, device_info):
        """Handle a newly connected device."""
        device_id = device_info.get("id")
        device_name = device_info.get("name", "Unknown Device")
        
        # If device is already known, return its permission
        if device_id in self.devices:
            return self.devices[device_id]["permission"]
        
        # Apply default permission
        permission = self.settings["default_permission"]
        
        # Auto-block suspicious devices if enabled
        if self.settings["auto_block_suspicious"] and device_info.get("suspicious", False):
            permission = PERMISSION_BLOCKED
            logger.warning(f"Auto-blocking suspicious device: {device_name} ({device_id})")
        
        # Save the new device
        self.set_device_permission(device_id, device_name, permission)
        
        return permission
    
    def apply_permissions(self, device_info):
        """Apply permissions to a device (platform-specific implementation)."""
        device_id = device_info.get("id")
        drive_letter = device_info.get("drive_letter")
        permission = self.get_device_permission(device_id)
        
        if not drive_letter:
            logger.warning(f"Cannot apply permissions: No drive letter for device {device_id}")
            return False
        
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                import subprocess
                import ctypes
                
                if permission == PERMISSION_BLOCKED:
                    # Block access to the drive
                    logger.info(f"Blocking access to drive {drive_letter}")
                    # Use icacls to deny all access
                    subprocess.run(["icacls", drive_letter, "/deny", "Everyone:(OI)(CI)F"], 
                                  capture_output=True, text=True, check=False)
                    return True
                
                elif permission == PERMISSION_READ_ONLY:
                    # Set drive to read-only
                    logger.info(f"Setting drive {drive_letter} to read-only")
                    # First reset permissions
                    subprocess.run(["icacls", drive_letter, "/reset"], 
                                  capture_output=True, text=True, check=False)
                    # Then set read-only
                    subprocess.run(["icacls", drive_letter, "/deny", "Everyone:(OI)(CI)W"], 
                                  capture_output=True, text=True, check=False)
                    return True
                
                elif permission == PERMISSION_FULL_ACCESS:
                    # Grant full access
                    logger.info(f"Granting full access to drive {drive_letter}")
                    # Reset permissions to default
                    subprocess.run(["icacls", drive_letter, "/reset"], 
                                  capture_output=True, text=True, check=False)
                    return True
            
            else:
                logger.warning(f"Permission application not implemented for {system}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying permissions to {drive_letter}: {str(e)}")
            return False
        
        return False

# Example usage
if __name__ == "__main__":
    manager = DeviceManager()
    
    # Test with a sample device
    device = {
        "id": "TEST_DEVICE_001",
        "name": "Test USB Drive",
        "drive_letter": "E:\\"
    }
    
    # Set permission
    manager.set_device_permission(device["id"], device["name"], PERMISSION_READ_ONLY)
    
    # Get permission
    permission = manager.get_device_permission(device["id"])
    print(f"Permission for {device['name']}: {permission}")
    
    # Get all devices
    all_devices = manager.get_all_devices()
    print(f"All devices: {json.dumps(all_devices, indent=2)}")
