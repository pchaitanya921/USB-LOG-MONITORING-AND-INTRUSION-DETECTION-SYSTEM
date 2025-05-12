#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Build Installer Script
Creates an installer for the USB Monitoring System
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse

def build_executable():
    """Build executable using PyInstaller"""
    print("Building executable...")
    
    # Create spec file
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='USBMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='USBMonitor',
)
"""
    
    # Write spec file
    with open("USBMonitor.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    subprocess.run(["pyinstaller", "USBMonitor.spec", "--clean"], check=True)
    
    print("Executable built successfully.")
    return True

def create_windows_installer():
    """Create Windows installer using NSIS"""
    print("Creating Windows installer...")
    
    # Create NSIS script
    nsis_script = """
; USB Monitoring System Installer Script
; Created with NSIS

!include "MUI2.nsh"
!include "FileFunc.nsh"

; General
Name "USB Monitoring System"
OutFile "USBMonitorSetup.exe"
InstallDir "$PROGRAMFILES\\USB Monitoring System"
InstallDirRegKey HKLM "Software\\USB Monitoring System" "Install_Dir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "dist\\USBMonitor\\assets\\icons\\app_icon.ico"
!define MUI_UNICON "dist\\USBMonitor\\assets\\icons\\app_icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy files
    File /r "dist\\USBMonitor\\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\USB Monitoring System"
    CreateShortcut "$SMPROGRAMS\\USB Monitoring System\\USB Monitoring System.lnk" "$INSTDIR\\USBMonitor.exe"
    CreateShortcut "$SMPROGRAMS\\USB Monitoring System\\Uninstall.lnk" "$INSTDIR\\Uninstall.exe"
    CreateShortcut "$DESKTOP\\USB Monitoring System.lnk" "$INSTDIR\\USBMonitor.exe"
    
    ; Write registry keys for uninstaller
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\USB Monitoring System" "DisplayName" "USB Monitoring System"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\USB Monitoring System" "UninstallString" '"$INSTDIR\\Uninstall.exe"'
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\USB Monitoring System" "DisplayIcon" "$INSTDIR\\USBMonitor.exe,0"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\USB Monitoring System" "Publisher" "Your Company"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\USB Monitoring System" "DisplayVersion" "1.0.0"
    
    ; Register for startup
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "USB Monitoring System" "$INSTDIR\\USBMonitor.exe"
    
    ; Get size of installation
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\USB Monitoring System" "EstimatedSize" "$0"
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove files and directories
    Delete "$INSTDIR\\Uninstall.exe"
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\USB Monitoring System\\USB Monitoring System.lnk"
    Delete "$SMPROGRAMS\\USB Monitoring System\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\USB Monitoring System"
    Delete "$DESKTOP\\USB Monitoring System.lnk"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\USB Monitoring System"
    DeleteRegValue HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "USB Monitoring System"
    DeleteRegKey HKLM "Software\\USB Monitoring System"
SectionEnd
"""
    
    # Create LICENSE.txt if it doesn't exist
    if not os.path.exists("LICENSE.txt"):
        with open("LICENSE.txt", "w") as f:
            f.write("USB Monitoring System License\n\n")
            f.write("Copyright (c) 2023 Your Company\n\n")
            f.write("Permission is hereby granted, free of charge, to any person obtaining a copy\n")
            f.write("of this software and associated documentation files (the \"Software\"), to deal\n")
            f.write("in the Software without restriction, including without limitation the rights\n")
            f.write("to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n")
            f.write("copies of the Software, and to permit persons to whom the Software is\n")
            f.write("furnished to do so, subject to the following conditions:\n\n")
            f.write("The above copyright notice and this permission notice shall be included in all\n")
            f.write("copies or substantial portions of the Software.\n\n")
            f.write("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n")
            f.write("IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n")
            f.write("FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n")
            f.write("AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n")
            f.write("LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n")
            f.write("OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n")
            f.write("SOFTWARE.\n")
    
    # Create app icon if it doesn't exist
    if not os.path.exists("assets/icons/app_icon.ico"):
        # Convert PNG to ICO
        try:
            from PIL import Image
            img = Image.open("assets/icons/app_icon.png")
            img.save("assets/icons/app_icon.ico")
        except:
            print("Warning: Could not create app_icon.ico. Please create it manually.")
    
    # Write NSIS script
    with open("installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Run NSIS
    try:
        subprocess.run(["makensis", "installer.nsi"], check=True)
        print("Windows installer created successfully.")
        return True
    except FileNotFoundError:
        print("Error: NSIS not found. Please install NSIS and add it to your PATH.")
        print("Download NSIS from: https://nsis.sourceforge.io/Download")
        return False
    except subprocess.CalledProcessError:
        print("Error: Failed to create Windows installer.")
        return False

def create_macos_installer():
    """Create macOS installer using DMG"""
    print("Creating macOS installer...")
    
    # Create DMG
    try:
        # Create app bundle
        app_path = "dist/USBMonitor.app"
        os.makedirs(f"{app_path}/Contents/MacOS", exist_ok=True)
        os.makedirs(f"{app_path}/Contents/Resources", exist_ok=True)
        
        # Copy executable
        shutil.copy("dist/USBMonitor/USBMonitor", f"{app_path}/Contents/MacOS/")
        
        # Copy resources
        shutil.copytree("dist/USBMonitor/assets", f"{app_path}/Contents/Resources/assets")
        
        # Create Info.plist
        info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>USBMonitor</string>
    <key>CFBundleIconFile</key>
    <string>app_icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.yourcompany.usbmonitor</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>USB Monitoring System</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
"""
        with open(f"{app_path}/Contents/Info.plist", "w") as f:
            f.write(info_plist)
        
        # Convert PNG to ICNS
        try:
            from PIL import Image
            img = Image.open("assets/icons/app_icon.png")
            img.save(f"{app_path}/Contents/Resources/app_icon.icns")
        except:
            print("Warning: Could not create app_icon.icns. Please create it manually.")
        
        # Create DMG
        subprocess.run([
            "hdiutil", "create", "-volname", "USB Monitoring System", 
            "-srcfolder", "dist/USBMonitor.app", 
            "-ov", "-format", "UDZO", 
            "dist/USBMonitoringSystem.dmg"
        ], check=True)
        
        print("macOS installer created successfully.")
        return True
    except Exception as e:
        print(f"Error creating macOS installer: {str(e)}")
        return False

def create_linux_installer():
    """Create Linux installer using AppImage"""
    print("Creating Linux installer...")
    
    # Create AppDir
    app_dir = "dist/AppDir"
    os.makedirs(f"{app_dir}/usr/bin", exist_ok=True)
    os.makedirs(f"{app_dir}/usr/share/applications", exist_ok=True)
    os.makedirs(f"{app_dir}/usr/share/icons/hicolor/256x256/apps", exist_ok=True)
    
    # Copy executable
    shutil.copy("dist/USBMonitor/USBMonitor", f"{app_dir}/usr/bin/")
    
    # Copy resources
    shutil.copytree("dist/USBMonitor/assets", f"{app_dir}/usr/share/usbmonitor/assets")
    
    # Create desktop file
    desktop_file = """[Desktop Entry]
Name=USB Monitoring System
Comment=Monitor and secure USB devices
Exec=USBMonitor
Icon=usbmonitor
Terminal=false
Type=Application
Categories=Utility;Security;
"""
    with open(f"{app_dir}/usr/share/applications/usbmonitor.desktop", "w") as f:
        f.write(desktop_file)
    
    # Copy icon
    shutil.copy("assets/icons/app_icon.png", f"{app_dir}/usr/share/icons/hicolor/256x256/apps/usbmonitor.png")
    
    # Create AppRun script
    app_run = """#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/USBMonitor" "$@"
"""
    with open(f"{app_dir}/AppRun", "w") as f:
        f.write(app_run)
    os.chmod(f"{app_dir}/AppRun", 0o755)
    
    # Create AppImage
    try:
        subprocess.run([
            "appimagetool", app_dir, "dist/USBMonitoringSystem.AppImage"
        ], check=True)
        
        print("Linux installer created successfully.")
        return True
    except FileNotFoundError:
        print("Error: appimagetool not found. Please install it.")
        print("Download appimagetool from: https://github.com/AppImage/AppImageKit/releases")
        return False
    except subprocess.CalledProcessError:
        print("Error: Failed to create Linux installer.")
        return False

def create_auto_updater():
    """Create auto-updater functionality"""
    print("Creating auto-updater...")
    
    # Create updater script
    updater_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
Auto-Updater for USB Monitoring System
Checks for updates and installs them automatically
\"\"\"

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
import platform
import urllib.request
import hashlib
import zipfile

# Configuration
UPDATE_URL = "https://example.com/updates/usbmonitor"
VERSION_FILE = "version.json"
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def get_current_version():
    \"\"\"Get current version from local version file\"\"\"
    version_path = os.path.join(APP_DIR, VERSION_FILE)
    
    if os.path.exists(version_path):
        try:
            with open(version_path, "r") as f:
                data = json.load(f)
                return data.get("version", "0.0.0")
        except:
            return "0.0.0"
    else:
        return "0.0.0"

def get_latest_version():
    \"\"\"Get latest version from update server\"\"\"
    try:
        with urllib.request.urlopen(f"{UPDATE_URL}/version.json") as response:
            data = json.loads(response.read().decode())
            return data.get("version", "0.0.0"), data
    except:
        return "0.0.0", {}

def download_update(version_data):
    \"\"\"Download update package\"\"\"
    system = platform.system().lower()
    
    if system == "windows":
        url = version_data.get("windows_url")
        filename = "USBMonitorSetup.exe"
    elif system == "darwin":
        url = version_data.get("macos_url")
        filename = "USBMonitoringSystem.dmg"
    elif system == "linux":
        url = version_data.get("linux_url")
        filename = "USBMonitoringSystem.AppImage"
    else:
        print(f"Unsupported system: {system}")
        return None
    
    if not url:
        print(f"No update URL for {system}")
        return None
    
    try:
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, filename)
        
        print(f"Downloading update from {url}...")
        urllib.request.urlretrieve(url, temp_file)
        
        # Verify checksum
        if "checksum" in version_data:
            with open(temp_file, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            if file_hash != version_data["checksum"]:
                print("Checksum verification failed")
                return None
        
        return temp_file
    except Exception as e:
        print(f"Error downloading update: {str(e)}")
        return None

def install_update(update_file):
    \"\"\"Install the update\"\"\"
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Run installer
            subprocess.Popen([update_file, "/SILENT"])
            return True
        elif system == "darwin":
            # Open DMG
            subprocess.Popen(["open", update_file])
            return True
        elif system == "linux":
            # Make AppImage executable
            os.chmod(update_file, 0o755)
            
            # Copy to application directory
            app_path = os.path.join(APP_DIR, "USBMonitoringSystem.AppImage")
            shutil.copy(update_file, app_path)
            
            return True
        else:
            print(f"Unsupported system: {system}")
            return False
    except Exception as e:
        print(f"Error installing update: {str(e)}")
        return False

def check_for_updates():
    \"\"\"Check for updates and install if available\"\"\"
    current_version = get_current_version()
    latest_version, version_data = get_latest_version()
    
    print(f"Current version: {current_version}")
    print(f"Latest version: {latest_version}")
    
    if latest_version > current_version:
        print("Update available!")
        
        update_file = download_update(version_data)
        if update_file:
            print("Installing update...")
            if install_update(update_file):
                print("Update installed successfully")
                return True
            else:
                print("Failed to install update")
                return False
        else:
            print("Failed to download update")
            return False
    else:
        print("No updates available")
        return False

if __name__ == "__main__":
    check_for_updates()
"""
    
    # Write updater script
    with open("updater.py", "w") as f:
        f.write(updater_script)
    
    # Create version file
    version_data = {
        "version": "1.0.0",
        "release_date": time.strftime("%Y-%m-%d"),
        "release_notes": "Initial release"
    }
    
    with open("version.json", "w") as f:
        json.dump(version_data, f, indent=4)
    
    print("Auto-updater created successfully.")
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Build USB Monitoring System installer")
    parser.add_argument("--executable", action="store_true", help="Build executable only")
    parser.add_argument("--installer", action="store_true", help="Build installer only")
    parser.add_argument("--updater", action="store_true", help="Create auto-updater only")
    parser.add_argument("--all", action="store_true", help="Build everything")
    
    args = parser.parse_args()
    
    # Default to --all if no arguments provided
    if not (args.executable or args.installer or args.updater):
        args.all = True
    
    # Build executable
    if args.executable or args.all:
        build_executable()
    
    # Create installer
    if args.installer or args.all:
        system = platform.system()
        if system == "Windows":
            create_windows_installer()
        elif system == "Darwin":
            create_macos_installer()
        elif system == "Linux":
            create_linux_installer()
        else:
            print(f"Unsupported system: {system}")
    
    # Create auto-updater
    if args.updater or args.all:
        create_auto_updater()
    
    print("Build completed successfully.")

if __name__ == "__main__":
    main()
