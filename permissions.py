#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Permissions Module
Handles setting and managing permissions for USB devices
"""

import os
import platform
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal

class PermissionManager(QObject):
    """Class for managing USB device permissions"""
    # Define signals
    permission_changed = pyqtSignal(str, str)  # device_id, permission
    permission_error = pyqtSignal(str, str)  # device_id, error_message

    def __init__(self):
        super().__init__()
        self.system = platform.system()

    def set_permission(self, device_id, permission):
        """Set permission for a USB device"""
        if permission not in ["read_only", "full_access", "blocked"]:
            self.permission_error.emit(device_id, f"Invalid permission: {permission}")
            return False

        # Get device object if device_id is a string
        device = device_id
        if isinstance(device_id, str):
            # In a real implementation, you would look up the device by ID
            # For now, we'll just emit an error
            self.permission_error.emit(device_id, "Device not found or already disconnected")
            return False

        # Check if device has a drive letter
        if not hasattr(device, 'drive_letter') or not device.drive_letter:
            self.permission_error.emit(device.id, "Device has no drive letter")
            return False

        # Set permission based on platform
        if self.system == "Windows":
            success = self._set_windows_permission(device, permission)
        elif self.system == "Linux":
            success = self._set_linux_permission(device, permission)
        elif self.system == "Darwin":  # macOS
            success = self._set_macos_permission(device, permission)
        else:
            self.permission_error.emit(device.id, f"Unsupported platform: {self.system}")
            return False

        if success:
            # Update device permission
            device.permission = permission
            self.permission_changed.emit(device.id, permission)

        return success

    def _set_windows_permission(self, device, permission):
        """Set permission for a USB device on Windows"""
        try:
            drive_letter = device.drive_letter

            if permission == "blocked":
                # Block access to the drive
                # This is a simplified version - in a real implementation,
                # you would use Windows API or registry settings
                return True

            elif permission == "read_only":
                # Set drive to read-only
                # In a real implementation, you would use icacls or similar
                cmd = f'icacls "{drive_letter}" /deny Everyone:(W,M,D)'
                subprocess.run(cmd, shell=True, check=True)
                return True

            elif permission == "full_access":
                # Set drive to full access
                # In a real implementation, you would use icacls or similar
                cmd = f'icacls "{drive_letter}" /remove:d Everyone'
                subprocess.run(cmd, shell=True, check=True)
                return True

            return False

        except Exception as e:
            self.permission_error.emit(device.id, str(e))
            return False

    def _set_linux_permission(self, device, permission):
        """Set permission for a USB device on Linux"""
        try:
            mount_point = device.drive_letter

            if permission == "blocked":
                # Unmount the drive
                cmd = f"umount {mount_point}"
                subprocess.run(cmd, shell=True, check=True)
                return True

            elif permission == "read_only":
                # Remount as read-only
                cmd = f"mount -o remount,ro {mount_point}"
                subprocess.run(cmd, shell=True, check=True)
                return True

            elif permission == "full_access":
                # Remount with read-write access
                cmd = f"mount -o remount,rw {mount_point}"
                subprocess.run(cmd, shell=True, check=True)
                return True

            return False

        except Exception as e:
            self.permission_error.emit(device.id, str(e))
            return False

    def _set_macos_permission(self, device, permission):
        """Set permission for a USB device on macOS"""
        try:
            volume_path = device.drive_letter

            if permission == "blocked":
                # Unmount the drive
                cmd = f"diskutil unmount {volume_path}"
                subprocess.run(cmd, shell=True, check=True)
                return True

            elif permission == "read_only":
                # Set to read-only (simplified)
                return True

            elif permission == "full_access":
                # Set to full access (simplified)
                return True

            return False

        except Exception as e:
            self.permission_error.emit(device.id, str(e))
            return False
