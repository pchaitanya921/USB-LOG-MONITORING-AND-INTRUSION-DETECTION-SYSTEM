#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
System Integration Module
Handles system integration tasks like startup registration and context menu integration
"""

import os
import sys
import platform
import subprocess
import shutil
import tempfile
from PyQt5.QtCore import QSettings

class SystemIntegration:
    """Class for system integration tasks"""
    def __init__(self):
        self.system = platform.system()
        self.app_name = "USB Monitoring System"
        self.executable_path = self._get_executable_path()
    
    def _get_executable_path(self):
        """Get path to executable"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as script
            return os.path.abspath(sys.argv[0])
    
    def register_startup(self, enable=True):
        """Register application to run at startup"""
        if self.system == "Windows":
            return self._register_startup_windows(enable)
        elif self.system == "Darwin":  # macOS
            return self._register_startup_macos(enable)
        elif self.system == "Linux":
            return self._register_startup_linux(enable)
        else:
            return False, f"Unsupported system: {self.system}"
    
    def _register_startup_windows(self, enable=True):
        """Register application to run at startup on Windows"""
        try:
            # Use Windows registry
            settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", QSettings.NativeFormat)
            
            if enable:
                settings.setValue(self.app_name, f'"{self.executable_path}"')
                return True, "Application registered for startup"
            else:
                settings.remove(self.app_name)
                return True, "Application removed from startup"
        except Exception as e:
            return False, f"Error registering startup: {str(e)}"
    
    def _register_startup_macos(self, enable=True):
        """Register application to run at startup on macOS"""
        try:
            # Create launch agent plist
            plist_dir = os.path.expanduser("~/Library/LaunchAgents")
            plist_path = os.path.join(plist_dir, "com.yourcompany.usbmonitor.plist")
            
            if enable:
                # Create directory if it doesn't exist
                os.makedirs(plist_dir, exist_ok=True)
                
                # Create plist file
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourcompany.usbmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>{self.executable_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
                with open(plist_path, "w") as f:
                    f.write(plist_content)
                
                # Load launch agent
                subprocess.run(["launchctl", "load", plist_path], check=True)
                
                return True, "Application registered for startup"
            else:
                # Unload launch agent
                if os.path.exists(plist_path):
                    subprocess.run(["launchctl", "unload", plist_path], check=True)
                    os.remove(plist_path)
                
                return True, "Application removed from startup"
        except Exception as e:
            return False, f"Error registering startup: {str(e)}"
    
    def _register_startup_linux(self, enable=True):
        """Register application to run at startup on Linux"""
        try:
            # Create desktop file
            autostart_dir = os.path.expanduser("~/.config/autostart")
            desktop_path = os.path.join(autostart_dir, "usbmonitor.desktop")
            
            if enable:
                # Create directory if it doesn't exist
                os.makedirs(autostart_dir, exist_ok=True)
                
                # Create desktop file
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=USB Monitoring System
Exec={self.executable_path}
Terminal=false
X-GNOME-Autostart-enabled=true
"""
                with open(desktop_path, "w") as f:
                    f.write(desktop_content)
                
                # Make executable
                os.chmod(desktop_path, 0o755)
                
                return True, "Application registered for startup"
            else:
                # Remove desktop file
                if os.path.exists(desktop_path):
                    os.remove(desktop_path)
                
                return True, "Application removed from startup"
        except Exception as e:
            return False, f"Error registering startup: {str(e)}"
    
    def add_context_menu(self, enable=True):
        """Add context menu integration"""
        if self.system == "Windows":
            return self._add_context_menu_windows(enable)
        elif self.system == "Darwin":  # macOS
            return self._add_context_menu_macos(enable)
        elif self.system == "Linux":
            return self._add_context_menu_linux(enable)
        else:
            return False, f"Unsupported system: {self.system}"
    
    def _add_context_menu_windows(self, enable=True):
        """Add context menu integration on Windows"""
        try:
            import winreg
            
            if enable:
                # Add context menu for drives
                key_path = r"Drive\\shell\\usbmonitor"
                
                # Create main key
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Scan with USB Monitor")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.executable_path)
                winreg.CloseKey(key)
                
                # Create command key
                key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path + "\\command")
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{self.executable_path}" --scan "%1"')
                winreg.CloseKey(key)
                
                return True, "Context menu integration added"
            else:
                # Remove context menu
                try:
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Drive\\shell\\usbmonitor\\command")
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Drive\\shell\\usbmonitor")
                except:
                    pass
                
                return True, "Context menu integration removed"
        except Exception as e:
            return False, f"Error adding context menu: {str(e)}"
    
    def _add_context_menu_macos(self, enable=True):
        """Add context menu integration on macOS"""
        try:
            # Create Automator workflow
            workflow_dir = os.path.expanduser("~/Library/Services")
            workflow_path = os.path.join(workflow_dir, "Scan with USB Monitor.workflow")
            
            if enable:
                # Create directory if it doesn't exist
                os.makedirs(workflow_dir, exist_ok=True)
                
                # Create temporary directory for workflow
                temp_dir = tempfile.mkdtemp()
                
                # Create workflow structure
                os.makedirs(os.path.join(temp_dir, "Contents"), exist_ok=True)
                
                # Create Info.plist
                info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>Scan with USB Monitor</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSRequiredContext</key>
            <dict>
                <key>NSApplicationIdentifier</key>
                <string>com.apple.finder</string>
            </dict>
            <key>NSSendFileTypes</key>
            <array>
                <string>public.volume</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
"""
                with open(os.path.join(temp_dir, "Contents", "Info.plist"), "w") as f:
                    f.write(info_plist)
                
                # Create document.wflow
                document_wflow = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>492</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>1.0.2</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>path</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>for f in "$@"
do
    "{self.executable_path}" --scan "$f"
done</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.RunShellScript</string>
                <key>CFBundleVersion</key>
                <string>1.0.2</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunShellScriptAction</string>
                <key>InputUUID</key>
                <string>4F5CCBCB-5F97-4484-8D96-E4E3D477A585</string>
                <key>Keywords</key>
                <array>
                    <string>Shell</string>
                    <string>Script</string>
                    <string>Command</string>
                    <string>Run</string>
                    <string>Unix</string>
                </array>
                <key>OutputUUID</key>
                <string>D2C19B3A-F8CE-4C5D-AE4E-374A989B0B0D</string>
                <key>UUID</key>
                <string>5A3CE543-9AA9-4D7D-A742-FD9058C94014</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict>
                    <key>0</key>
                    <dict>
                        <key>default value</key>
                        <string>/bin/sh</string>
                        <key>name</key>
                        <string>shell</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>0</string>
                    </dict>
                    <key>1</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>COMMAND_STRING</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>1</string>
                    </dict>
                    <key>2</key>
                    <dict>
                        <key>default value</key>
                        <integer>0</integer>
                        <key>name</key>
                        <string>inputMethod</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>2</string>
                    </dict>
                    <key>3</key>
                    <dict>
                        <key>default value</key>
                        <string></string>
                        <key>name</key>
                        <string>source</string>
                        <key>required</key>
                        <string>0</string>
                        <key>type</key>
                        <string>0</string>
                        <key>uuid</key>
                        <string>3</string>
                    </dict>
                </dict>
                <key>isViewVisible</key>
                <true/>
                <key>location</key>
                <string>309.000000:253.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <true/>
        </dict>
    </array>
    <key>connectors</key>
    <dict/>
    <key>workflowMetaData</key>
    <dict>
        <key>serviceInputTypeIdentifier</key>
        <string>com.apple.Automator.fileSystemObject.volume</string>
        <key>serviceOutputTypeIdentifier</key>
        <string>com.apple.Automator.nothing</string>
        <key>serviceProcessesInput</key>
        <integer>1</integer>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.service</string>
    </dict>
</dict>
</plist>
"""
                
                os.makedirs(os.path.join(temp_dir, "Contents", "document.wflow"), exist_ok=True)
                with open(os.path.join(temp_dir, "Contents", "document.wflow"), "w") as f:
                    f.write(document_wflow)
                
                # Copy workflow to services directory
                if os.path.exists(workflow_path):
                    shutil.rmtree(workflow_path)
                shutil.copytree(temp_dir, workflow_path)
                
                # Clean up
                shutil.rmtree(temp_dir)
                
                return True, "Context menu integration added"
            else:
                # Remove workflow
                if os.path.exists(workflow_path):
                    shutil.rmtree(workflow_path)
                
                return True, "Context menu integration removed"
        except Exception as e:
            return False, f"Error adding context menu: {str(e)}"
    
    def _add_context_menu_linux(self, enable=True):
        """Add context menu integration on Linux"""
        try:
            # Create Nautilus script
            scripts_dir = os.path.expanduser("~/.local/share/nautilus/scripts")
            script_path = os.path.join(scripts_dir, "Scan with USB Monitor")
            
            if enable:
                # Create directory if it doesn't exist
                os.makedirs(scripts_dir, exist_ok=True)
                
                # Create script
                script_content = f"""#!/bin/bash
# Scan with USB Monitor
for arg in "$@"; do
    "{self.executable_path}" --scan "$arg"
done
"""
                with open(script_path, "w") as f:
                    f.write(script_content)
                
                # Make executable
                os.chmod(script_path, 0o755)
                
                return True, "Context menu integration added"
            else:
                # Remove script
                if os.path.exists(script_path):
                    os.remove(script_path)
                
                return True, "Context menu integration removed"
        except Exception as e:
            return False, f"Error adding context menu: {str(e)}"
