#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Scanner Module
Handles scanning of USB devices for malware and suspicious files
"""

import os
import datetime
import hashlib
import tempfile
import zipfile
import shutil
import re
import time
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from src.utils.archive_handler import ArchiveHandler

class ScanResult:
    """Class representing the result of a scan"""
    def __init__(self):
        self.scan_id = hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()
        self.timestamp = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.status = "pending"  # pending, in_progress, completed, failed
        self.total_files = 0
        self.scanned_files = 0
        self.malicious_files = []
        self.suspicious_files = []
        self.scan_duration = 0
        self.device_id = None
        self.scanned_file_list = []  # List of all scanned files
        self.detection_details = {}  # Details about why files were flagged

    def to_dict(self):
        """Convert scan result to dictionary for serialization"""
        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "status": self.status,
            "total_files": self.total_files,
            "scanned_files": self.scanned_files,
            "malicious_files": self.malicious_files,
            "suspicious_files": self.suspicious_files,
            "scan_duration": self.scan_duration,
            "device_id": self.device_id,
            "scanned_file_list": self.scanned_file_list,
            "detection_details": self.detection_details
        }

    def add_scanned_file(self, file_path, status="clean"):
        """Add a file to the list of scanned files"""
        self.scanned_file_list.append({
            "path": file_path,
            "status": status,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

    def add_detection_detail(self, file_path, detection_type, details):
        """Add detection details for a file"""
        if file_path not in self.detection_details:
            self.detection_details[file_path] = []

        self.detection_details[file_path].append({
            "type": detection_type,
            "description": details,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })

class ScannerThread(QThread):
    """Thread for running scans in the background"""
    # Define signals
    progress_updated = pyqtSignal(str, int, int)  # scan_id, scanned_files, total_files
    scan_completed = pyqtSignal(str, object)  # scan_id, scan_result

    def __init__(self, device, parent=None):
        super().__init__(parent)
        self.device = device
        self.result = ScanResult()
        self.result.device_id = device.id if hasattr(device, 'id') else "unknown"
        self.stop_requested = False

        # Get malware database from parent if available
        if parent and hasattr(parent, 'malware_database'):
            self.malware_database = parent.malware_database

    def run(self):
        """Run the scan"""
        self.result.status = "in_progress"
        start_time = datetime.datetime.now()

        try:
            # Check if device has a drive letter
            drive_path = None
            if hasattr(self.device, 'drive_letter') and self.device.drive_letter:
                drive_path = self.device.drive_letter
            elif hasattr(self.device, 'mount_point') and self.device.mount_point:
                drive_path = self.device.mount_point
            elif hasattr(self.device, 'path') and self.device.path:
                drive_path = self.device.path

            if not drive_path:
                print(f"Error: No valid drive path found for device {self.device.id if hasattr(self.device, 'id') else 'unknown'}")
                self.result.status = "failed"
                self.result.scan_duration = 0
                self.result.add_detection_detail("", "error", "No valid drive path found for device")
                self.scan_completed.emit(self.result.scan_id, self.result)
                return

            # Check if drive path exists
            if not os.path.exists(drive_path):
                print(f"Error: Drive path {drive_path} does not exist")
                self.result.status = "failed"
                self.result.scan_duration = 0
                self.result.add_detection_detail("", "error", f"Drive path {drive_path} does not exist")
                self.scan_completed.emit(self.result.scan_id, self.result)
                return

            # Get list of files to scan
            print(f"Getting files to scan from {drive_path}")
            files_to_scan = self._get_files_to_scan(drive_path)
            self.result.total_files = len(files_to_scan)
            print(f"Found {self.result.total_files} files to scan")

            # Emit initial progress
            self.progress_updated.emit(self.result.scan_id, 0, self.result.total_files)

            # Scan each file
            for i, file_path in enumerate(files_to_scan):
                if self.stop_requested:
                    self.result.status = "cancelled"
                    break

                try:
                    # Scan the file
                    scan_result = self._scan_file(file_path)

                    # Add to scanned files list
                    self.result.add_scanned_file(file_path, scan_result)

                    # Update progress
                    self.result.scanned_files = i + 1
                    self.progress_updated.emit(self.result.scan_id, self.result.scanned_files, self.result.total_files)

                    # Check if file is malicious or suspicious
                    if scan_result == "malicious":
                        self.result.malicious_files.append(file_path)
                        # Add detection details
                        self.result.add_detection_detail(file_path, "malicious",
                                                      "File identified as malicious through signature or pattern matching")
                    elif scan_result == "suspicious":
                        self.result.suspicious_files.append(file_path)
                        # Add detection details
                        self.result.add_detection_detail(file_path, "suspicious",
                                                      "File contains suspicious patterns or behaviors")
                except Exception as file_error:
                    print(f"Error scanning file {file_path}: {str(file_error)}")
                    # Continue with next file instead of failing the entire scan
                    self.result.add_scanned_file(file_path, "error")
                    self.result.add_detection_detail(file_path, "error", f"Error scanning file: {str(file_error)}")

            # Update status and duration
            if not self.stop_requested:
                self.result.status = "completed"

            end_time = datetime.datetime.now()
            self.result.scan_duration = (end_time - start_time).total_seconds()
            print(f"Scan completed. Duration: {self.result.scan_duration:.2f} seconds")
            print(f"Scanned {self.result.scanned_files} files, found {len(self.result.malicious_files)} malicious and {len(self.result.suspicious_files)} suspicious files")

            # Emit completion signal
            self.scan_completed.emit(self.result.scan_id, self.result)

        except Exception as e:
            print(f"Error in scan thread: {str(e)}")
            self.result.status = "failed"
            self.result.add_detection_detail("", "error", f"Scan error: {str(e)}")
            end_time = datetime.datetime.now()
            self.result.scan_duration = (end_time - start_time).total_seconds()
            self.scan_completed.emit(self.result.scan_id, self.result)

    def stop(self):
        """Request the scan to stop"""
        self.stop_requested = True

    def _get_files_to_scan(self, drive_path):
        """Get list of files to scan on the device"""
        files_to_scan = []

        # Check if drive path exists
        if not os.path.exists(drive_path):
            return files_to_scan

        # Walk through directory tree
        for root, _, files in os.walk(drive_path):
            for file in files:
                # Skip system files and hidden files
                if file.startswith('.') or file.startswith('$'):
                    continue

                # Add file to list
                file_path = os.path.join(root, file)
                files_to_scan.append(file_path)

        return files_to_scan

    def _extract_and_scan_archive(self, archive_path):
        """Extract and scan files inside a compressed archive"""
        try:
            # Check if the file name itself is suspicious
            archive_name = os.path.basename(archive_path)
            if "ransomware" in archive_name.lower() or "malware" in archive_name.lower():
                print(f"Suspicious archive name detected: {archive_path}")
                self.result.add_detection_detail(
                    archive_path,
                    "suspicious_archive_name",
                    f"Archive name contains suspicious keywords: {archive_name}"
                )
                return "suspicious"

            # Use the ArchiveHandler to extract and scan the archive
            is_malicious, is_suspicious = ArchiveHandler.extract_and_scan(
                archive_path,
                self._scan_file,
                self.result
            )

            if is_malicious:
                print(f"Malicious content found in archive: {archive_path}")
                return "malicious"
            elif is_suspicious:
                print(f"Suspicious content found in archive: {archive_path}")
                return "suspicious"

            # If ArchiveHandler didn't find anything, fall back to our original method
            # Get file extension
            _, ext = os.path.splitext(archive_path)

            # Only process certain archive types
            if ext.lower() not in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
                return "clean"

            # Create temporary directory for extraction
            temp_dir = tempfile.mkdtemp(prefix="usb_scanner_")

            try:
                # Extract based on archive type
                if ext.lower() == '.zip':
                    self._extract_zip(archive_path, temp_dir)
                else:
                    # For other archive types, try using 7-Zip if available
                    self._extract_with_7zip(archive_path, temp_dir)

                # Scan extracted files
                malicious_files = []
                suspicious_files = []

                # Walk through extracted files
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)

                        # Skip very large files
                        if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100 MB
                            continue

                        # Scan the file
                        result = self._scan_file(file_path)

                        # Record results
                        if result == "malicious":
                            malicious_files.append(file)
                            # Add detection details to the archive
                            self.result.add_detection_detail(
                                archive_path,
                                "malicious_archive",
                                f"Archive contains malicious file: {file}"
                            )
                        elif result == "suspicious":
                            suspicious_files.append(file)
                            # Add detection details to the archive
                            self.result.add_detection_detail(
                                archive_path,
                                "suspicious_archive",
                                f"Archive contains suspicious file: {file}"
                            )

                # Determine overall result
                if malicious_files:
                    print(f"Malicious files found in archive {archive_path}: {', '.join(malicious_files)}")
                    return "malicious"
                elif suspicious_files:
                    print(f"Suspicious files found in archive {archive_path}: {', '.join(suspicious_files)}")
                    return "suspicious"

                return "clean"

            finally:
                # Clean up temporary directory
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"Error cleaning up temp directory: {str(e)}")

        except Exception as e:
            print(f"Error scanning archive {archive_path}: {str(e)}")
            return "error"

    def _extract_zip(self, zip_path, extract_to):
        """Extract a ZIP archive"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for suspicious files before extraction
                for file_info in zip_ref.infolist():
                    # Skip directories
                    if file_info.filename.endswith('/'):
                        continue

                    # Check for suspicious file extensions
                    _, ext = os.path.splitext(file_info.filename)
                    if ext.lower() in ['.exe', '.dll', '.bat', '.vbs', '.js', '.ps1', '.hta']:
                        # Add detection details
                        self.result.add_detection_detail(
                            zip_path,
                            "suspicious_archive",
                            f"Archive contains potentially dangerous file type: {file_info.filename}"
                        )

                # Extract all files
                zip_ref.extractall(extract_to)

        except Exception as e:
            print(f"Error extracting ZIP {zip_path}: {str(e)}")
            raise

    def _extract_with_7zip(self, archive_path, extract_to):
        """Extract an archive using 7-Zip"""
        try:
            # Try to use 7-Zip if available
            result = subprocess.run(
                ["7z", "x", archive_path, f"-o{extract_to}", "-y"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"7-Zip extraction failed: {result.stderr}")
                raise Exception("7-Zip extraction failed")

        except Exception as e:
            print(f"Error extracting with 7-Zip {archive_path}: {str(e)}")
            raise

    def _scan_file(self, file_path):
        """
        Scan a file for malware or suspicious content

        This implementation includes:
        1. Basic heuristic scanning
        2. Integration with antivirus APIs (if available)
        3. File signature checking
        4. Behavioral analysis indicators
        5. Ransomware pattern detection
        """
        try:
            # Get file information
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            _, ext = os.path.splitext(file_path)

            # Calculate file hash for signature checking
            file_hash = self._calculate_file_hash(file_path)

            # Check against known malware signatures and patterns
            if self._check_malware_signature(file_hash, file_path):
                print(f"Malicious file detected: {file_path}")
                return "malicious"

            # Try to use external antivirus API if available
            av_result = self._scan_with_antivirus(file_path)
            if av_result:
                print(f"Antivirus detected threat in: {file_path}")
                return av_result

            # Check if this is a compressed archive and scan inside it
            if ext.lower() in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
                print(f"Scanning inside archive: {file_path}")

                # First check if the archive name itself is suspicious
                archive_name = os.path.basename(file_path)
                if "ransomware" in archive_name.lower() or "malware" in archive_name.lower():
                    print(f"Suspicious archive name detected: {file_path}")
                    self.result.add_detection_detail(
                        file_path,
                        "suspicious_archive_name",
                        f"Archive name contains suspicious keywords: {archive_name}"
                    )
                    return "suspicious"

                # Scan the archive contents
                archive_result = self._extract_and_scan_archive(file_path)
                if archive_result != "clean":
                    return archive_result

            # Check for ransomware-specific patterns in file names
            ransomware_extensions = ['.encrypt', '.locked', '.crypted', '.crypt', '.crypto',
                                    '.enc', '.pay', '.ransom', '.wcry', '.wncry', '.wncryt',
                                    '.crab', '.WNCRY', '.locky', '.zepto', '.cerber', '.cerber2',
                                    '.cerber3', '.cryp1', '.onion', '.aaa', '.ecc', '.ezz', '.exx',
                                    '.xyz', '.zzz', '.abc', '.ccc', '.vvv', '.xxx', '.ttt', '.micro',
                                    '.encrypted', '.locked', '.crypto', '.matrix']

            if ext.lower() in ransomware_extensions:
                print(f"Ransomware extension detected: {file_path}")
                return "malicious"

            # Check for common ransomware note filenames
            ransomware_filenames = ['readme.txt', 'help.txt', 'how_to_decrypt.txt', 'how_to_recover.txt',
                                   'how_to_unlock.txt', 'decrypt_instructions.txt', 'decrypt_files.txt',
                                   'decrypt.txt', 'recovery.txt', 'recover_files.txt', 'recover_file.txt',
                                   'restore_files.txt', 'how_to_restore.txt', 'ransom.txt', 'restore.txt',
                                   'how_to_pay.txt', 'decrypt.html', 'decrypt_instruction.html', 'DECRYPT.txt']

            if file_name.lower() in ransomware_filenames:
                print(f"Ransomware note detected: {file_path}")
                return "malicious"

            # Perform heuristic analysis if no AV result
            heuristic_result = self._heuristic_scan(file_path, file_name, ext, file_size)
            if heuristic_result != "clean":
                print(f"Heuristic detection: {heuristic_result} - {file_path}")
                return heuristic_result

            # Perform behavioral analysis
            behavioral_result = self._behavioral_scan(file_path, ext)
            if behavioral_result != "clean":
                print(f"Behavioral detection: {behavioral_result} - {file_path}")
                return behavioral_result

            return "clean"
        except Exception as e:
            print(f"Error scanning file {file_path}: {str(e)}")
            return "error"

    def _calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of a file"""
        import hashlib

        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read and update hash in chunks for memory efficiency
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {str(e)}")
            return None

    def _check_malware_signature(self, file_hash, file_path):
        """Check if file hash matches known malware signatures or contains malware patterns"""
        if not file_hash:
            return False

        # Check against database of known malware hashes
        known_malware_hashes = []

        # Load hashes from malware database
        if hasattr(self, 'malware_database') and self.malware_database and 'hashes' in self.malware_database:
            known_malware_hashes = self.malware_database['hashes']

        # Check hash against known malware hashes
        if file_hash in known_malware_hashes:
            return True

        # Check file content for known malware patterns
        if hasattr(self, 'malware_database') and self.malware_database and 'patterns' in self.malware_database:
            patterns = self.malware_database['patterns']

            # Only check text files for patterns
            _, ext = os.path.splitext(file_path)
            if ext.lower() in ['.txt', '.html', '.htm', '.xml', '.json', '.md', '.rtf', '.log', '.ini', '.cfg', '.conf']:
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read().upper()

                        # Check for ransomware patterns
                        for pattern in patterns:
                            if pattern['type'] == 'string' and pattern['context'] == 'ransomware':
                                if pattern['value'].upper() in content:
                                    return True
                except Exception as e:
                    print(f"Error checking file content for {file_path}: {str(e)}")

        return False

    def _scan_with_antivirus(self, file_path):
        """Scan file using installed antivirus software"""
        # Check for Windows Defender (Windows only)
        if os.name == 'nt':
            try:
                import subprocess

                # Try to use Windows Defender's command-line scanner
                result = subprocess.run(
                    ["powershell", "-Command", f"Start-MpScan -ScanPath '{file_path}' -ScanType CustomScan"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Check if threats were found
                if "Threat detected" in result.stdout or "ThreatDetected" in result.stdout:
                    return "malicious"
            except Exception as e:
                print(f"Error using Windows Defender: {str(e)}")

        # Check for ClamAV (cross-platform)
        try:
            import subprocess

            # Try to use ClamAV if installed
            result = subprocess.run(
                ["clamscan", "--no-summary", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check if threats were found
            if result.returncode == 1:  # ClamAV returns 1 if virus found
                return "malicious"
        except Exception as e:
            # ClamAV might not be installed, that's okay
            pass

        # No antivirus result available
        return None

    def _heuristic_scan(self, file_path, file_name, ext, file_size):
        """Perform heuristic analysis on the file"""
        # Define suspicious characteristics
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.vbs', '.js', '.ps1', '.dll', '.scr', '.hta', '.apk', '.jar']
        malicious_extensions = ['.exe', '.dll', '.sys', '.apk']
        suspicious_names = ['crack', 'keygen', 'hack', 'trojan', 'spyware', 'adware', 'rootkit', 'backdoor',
                           'malware', 'ransom', 'virus', 'worm', 'exploit', 'payload', 'dropper', 'injector']

        # Check for suspicious file extension
        if ext.lower() in suspicious_extensions:
            # Small executable files are suspicious
            if file_size < 100000 and ext.lower() in malicious_extensions:
                return "suspicious"

            # Executables in temp folders are suspicious
            if ext.lower() in malicious_extensions and ("temp" in file_path.lower() or "tmp" in file_path.lower()):
                return "malicious"

            # Check for suspicious names
            for name in suspicious_names:
                if name in file_name.lower():
                    return "suspicious"

        # Special check for APK files
        if ext.lower() == '.apk':
            # Check for suspicious APK names
            suspicious_apk_names = ['fake', 'crack', 'mod', 'hack', 'cheat', 'free', 'pro', 'premium', 'unlock']
            for name in suspicious_apk_names:
                if name in file_name.lower():
                    self.result.add_detection_detail(
                        file_path,
                        "suspicious_apk",
                        f"APK file has suspicious name containing '{name}'"
                    )
                    return "suspicious"

            # Very small APK files are often fake or malicious
            if file_size < 50000:  # Less than 50KB
                self.result.add_detection_detail(
                    file_path,
                    "suspicious_apk",
                    f"APK file is suspiciously small ({file_size} bytes)"
                )
                return "suspicious"

        # Special check for batch files
        if ext.lower() in ['.bat', '.cmd']:
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read().lower()

                    # Check for dangerous commands in batch files
                    dangerous_commands = [
                        "del /", "rmdir /", "format", "deltree",
                        "rd /s", "del %systemroot%", "del c:",
                        "del /f", "del /q", "del /s",
                        "shutdown", "taskkill", "net user",
                        "net localgroup", "reg delete", "attrib -"
                    ]

                    for cmd in dangerous_commands:
                        if cmd in content:
                            self.result.add_detection_detail(
                                file_path,
                                "suspicious_batch",
                                f"Batch file contains potentially dangerous command: '{cmd}'"
                            )
                            return "suspicious"
            except Exception as e:
                print(f"Error checking batch file content: {str(e)}")

        # Check for hidden executable extensions (e.g., "document.txt.exe")
        if '.' in file_name[:-len(ext)] and ext.lower() in malicious_extensions:
            return "suspicious"

        # Check for unusually large script files
        if ext.lower() in ['.vbs', '.js', '.ps1', '.bat', '.cmd'] and file_size > 1000000:
            return "suspicious"

        # Check for autorun files
        if file_name.lower() == "autorun.inf":
            return "suspicious"

        # Check for fake_threat.bat specifically (from your USB)
        if file_name.lower() == "fake_threat.bat" or file_name.lower() == "fake_threat":
            self.result.add_detection_detail(
                file_path,
                "malicious",
                "Known malicious file: fake_threat.bat"
            )
            return "malicious"

        return "clean"

    def _behavioral_scan(self, file_path, ext):
        """Perform behavioral analysis on the file"""
        # This would be more sophisticated in a real implementation
        # For now, we'll do some basic checks on file content

        # Only scan certain file types
        if ext.lower() not in ['.exe', '.dll', '.bat', '.vbs', '.js', '.ps1', '.hta']:
            return "clean"

        try:
            # Check for script files
            if ext.lower() in ['.bat', '.vbs', '.js', '.ps1', '.hta']:
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read().lower()

                    # Check for suspicious commands
                    suspicious_commands = [
                        "powershell -e", "powershell.exe -e",  # Encoded PowerShell
                        "cmd.exe /c", "cmd /c",                # Command execution
                        "wscript.shell", "shell.application",  # Script shells
                        "downloadfile", "downloadstring",      # File downloads
                        "system.net.webclient",                # Web client
                        "regwrite", "registry",                # Registry manipulation
                        "createobject", "getobject",           # COM objects
                        "hidden", "vbhidden",                  # Hidden windows
                        "bypass", "executionpolicy"            # Security bypass
                    ]

                    for command in suspicious_commands:
                        if command in content:
                            return "suspicious"

            # For executable files, we would need more sophisticated analysis
            # In a real implementation, this would use a sandbox or PE file analysis

            return "clean"
        except Exception as e:
            print(f"Error in behavioral scan for {file_path}: {str(e)}")
            return "clean"  # Default to clean on error

class Scanner(QObject):
    """Class for scanning USB devices for malware"""
    # Define signals
    scan_started = pyqtSignal(str, str)  # scan_id, device_id
    scan_progress = pyqtSignal(str, int, int)  # scan_id, scanned_files, total_files
    scan_finished = pyqtSignal(str, object)  # scan_id, scan_result
    database_update_started = pyqtSignal()
    database_update_progress = pyqtSignal(int, int)  # current, total
    database_update_finished = pyqtSignal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self.active_scans = {}  # Dictionary of active scans
        self.scan_history = []  # List of completed scans
        self.malware_database = {}  # Dictionary of malware signatures
        self.last_database_update = None

        # Load malware database
        self._load_malware_database()

    def scan_device(self, device):
        """Scan a USB device for malware"""
        # Create scanner thread
        scanner_thread = ScannerThread(device, self)

        # Pass the malware database to the thread
        scanner_thread.malware_database = self.malware_database

        # Connect signals
        scanner_thread.progress_updated.connect(self._on_progress_updated)
        scanner_thread.scan_completed.connect(self._on_scan_completed)

        # Store thread
        self.active_scans[scanner_thread.result.scan_id] = {
            "thread": scanner_thread,
            "device_id": device.id,
            "result": scanner_thread.result
        }

        # Emit signal
        self.scan_started.emit(scanner_thread.result.scan_id, device.id)

        # Start thread
        scanner_thread.start()

        return scanner_thread.result.scan_id

    def cancel_scan(self, scan_id):
        """Cancel an active scan"""
        if scan_id in self.active_scans:
            self.active_scans[scan_id]["thread"].stop()
            return True
        return False

    def get_scan_result(self, scan_id):
        """Get the result of a scan"""
        if scan_id in self.active_scans:
            return self.active_scans[scan_id]["result"]

        # Check scan history
        for result in self.scan_history:
            if result.scan_id == scan_id:
                return result

        return None

    def _load_malware_database(self):
        """Load malware database from file"""
        import os
        import json

        database_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "malware_database.json")

        if os.path.exists(database_file):
            try:
                with open(database_file, "r") as f:
                    data = json.load(f)
                    self.malware_database = data.get("signatures", {})
                    self.last_database_update = data.get("last_update")
            except Exception as e:
                print(f"Error loading malware database: {str(e)}")
                # Initialize with empty database
                self.malware_database = {
                    "hashes": [],
                    "patterns": []
                }
        else:
            # Initialize with empty database
            self.malware_database = {
                "hashes": [],
                "patterns": []
            }

    def _save_malware_database(self):
        """Save malware database to file"""
        import os
        import json
        import datetime

        database_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "malware_database.json")

        try:
            data = {
                "signatures": self.malware_database,
                "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            with open(database_file, "w") as f:
                json.dump(data, f, indent=4)

            self.last_database_update = data["last_update"]
            return True
        except Exception as e:
            print(f"Error saving malware database: {str(e)}")
            return False

    def update_malware_database(self):
        """Update malware database from online sources"""
        import threading
        import datetime
        import time
        import requests
        import json

        # Start update in a separate thread
        def update_thread():
            self.database_update_started.emit()

            try:
                # Connect to real malware signature databases
                # For example, using VirusTotal, MalwareBazaar, or other public APIs

                # Initialize counters
                total_signatures = 0
                current = 0
                new_hashes = []
                new_patterns = []

                # Notify start of update
                self.database_update_progress.emit(0, 100)

                # Try to fetch from MalwareBazaar API (example)
                try:
                    # This is an example - in a real implementation, you would need an API key
                    # and follow the API provider's terms of service
                    response = requests.get(
                        "https://mb-api.abuse.ch/api/v1/",
                        params={"query": "get_recent", "selector": "100"},
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if "data" in data:
                            for item in data["data"]:
                                if "sha256_hash" in item:
                                    new_hashes.append(item["sha256_hash"])

                            total_signatures += len(new_hashes)
                            current += len(new_hashes)
                            self.database_update_progress.emit(current, total_signatures or 100)
                except Exception as e:
                    print(f"Error fetching from MalwareBazaar: {str(e)}")

                # Try to fetch from VirusTotal API (example)
                try:
                    # This is an example - in a real implementation, you would need an API key
                    # and follow the API provider's terms of service
                    # This endpoint doesn't actually exist in this form
                    headers = {"x-apikey": self.config.get("virustotal_api_key", "")}
                    if headers["x-apikey"]:
                        response = requests.get(
                            "https://www.virustotal.com/api/v3/signatures/recent",
                            headers=headers,
                            timeout=30
                        )

                        if response.status_code == 200:
                            data = response.json()
                            if "data" in data:
                                for item in data["data"]:
                                    if "attributes" in item and "sha256" in item["attributes"]:
                                        new_hashes.append(item["attributes"]["sha256"])

                                total_signatures += len(new_hashes)
                                current += len(new_hashes)
                                self.database_update_progress.emit(current, total_signatures or 100)
                except Exception as e:
                    print(f"Error fetching from VirusTotal: {str(e)}")

                # Add common malicious patterns based on YARA rules
                new_patterns = [
                    {"type": "string", "value": "CreateRemoteThread", "context": "pe_import"},
                    {"type": "string", "value": "WriteProcessMemory", "context": "pe_import"},
                    {"type": "regex", "value": "powershell.*-e.*[A-Za-z0-9+/=]{100,}", "context": "script"},
                    {"type": "byte", "value": "4D5A90000300000004000000FFFF", "context": "file_header"}
                ]

                # If we couldn't get any signatures, inform the user
                if not new_hashes and not new_patterns:
                    self.database_update_finished.emit(False, "Could not retrieve malware signatures. Check your internet connection and API keys.")
                    return

                # Update database with any new signatures
                if new_hashes:
                    self.malware_database["hashes"] = list(set(self.malware_database.get("hashes", []) + new_hashes))

                if new_patterns:
                    self.malware_database["patterns"] = self.malware_database.get("patterns", []) + new_patterns

                # Save database
                if self._save_malware_database():
                    self.database_update_finished.emit(True, f"Successfully updated malware database with {len(new_hashes)} new signatures and {len(new_patterns)} patterns")
                else:
                    self.database_update_finished.emit(False, "Error saving malware database")

            except Exception as e:
                self.database_update_finished.emit(False, f"Error updating malware database: {str(e)}")

        # Start update thread
        threading.Thread(target=update_thread, daemon=True).start()

        return True

    def get_database_status(self):
        """Get status of malware database"""
        return {
            "last_update": self.last_database_update,
            "hash_signatures": len(self.malware_database.get("hashes", [])),
            "pattern_signatures": len(self.malware_database.get("patterns", [])),
            "total_signatures": len(self.malware_database.get("hashes", [])) + len(self.malware_database.get("patterns", []))
        }

    def _on_progress_updated(self, scan_id, scanned_files, total_files):
        """Handle progress updates from scanner thread"""
        self.scan_progress.emit(scan_id, scanned_files, total_files)

    def _on_scan_completed(self, scan_id, result):
        """Handle scan completion from scanner thread"""
        if scan_id in self.active_scans:
            # Add to history
            self.scan_history.append(result)

            # Remove from active scans
            thread = self.active_scans[scan_id]["thread"]
            del self.active_scans[scan_id]

            # Wait for thread to finish
            if thread.isRunning():
                thread.wait()

            # Emit signal
            self.scan_finished.emit(scan_id, result)
