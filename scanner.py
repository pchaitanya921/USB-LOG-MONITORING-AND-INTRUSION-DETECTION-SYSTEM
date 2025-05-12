import os
import hashlib
import re
import platform
import logging
import datetime
import math
import struct
import binascii
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scanner.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("usb_scanner")

# Check if yara-python is available
HAS_YARA = importlib.util.find_spec("yara") is not None

# Suspicious file patterns (expanded)
SUSPICIOUS_PATTERNS = [
    # Autorun files
    r'autorun\.inf',
    r'autorun\.exe',

    # Executable files
    r'.*\.exe$',
    r'.*\.bat$',
    r'.*\.vbs$',
    r'.*\.ps1$',
    r'.*\.scr$',
    r'.*\.cmd$',
    r'.*\.dll$',
    r'.*\.sys$',

    # Script files
    r'.*\.js$',
    r'.*\.hta$',
    r'.*\.jse$',
    r'.*\.vbe$',
    r'.*\.wsf$',
    r'.*\.wsh$',

    # Installer files
    r'.*\.msi$',
    r'.*\.msp$',
    r'.*\.msc$',

    # Office files with macros
    r'.*\.docm$',
    r'.*\.xlsm$',
    r'.*\.pptm$',

    # Suspicious double extensions
    r'.*\.jpg\.exe$',
    r'.*\.pdf\.exe$',
    r'.*\.doc\.exe$',
    r'.*\.txt\.exe$',

    # Hidden executable extensions
    r'.*\.exe\..+$',  # Hidden by additional extension

    # Suspicious naming patterns
    r'.*crack.*\.exe$',
    r'.*hack.*\.exe$',
    r'.*keygen.*\.exe$',
    r'.*patch.*\.exe$',
    r'.*activate.*\.exe$'
]

# Known malicious file hashes (MD5)
# This is a small sample - in a real application, you would use a larger database
# or connect to services like VirusTotal
MALICIOUS_HASHES = {
    # Common malware samples
    "e44e35b203bbc12486983c8080172d48": "Trojan.Generic",
    "84c82835a5d21bbcf75a61706d8ab549": "Ransomware.WannaCry",
    "5099a161231ae8b639bb98d697c1d279": "Backdoor.Generic",
    "b5c706cae4d9f2e811f9a47254a83c77": "Trojan.Downloader",
    "0a73291ab5607aef7db23863cf8e566e": "Worm.Generic",

    # Additional known malware
    "2f2a8519ccedcc8d85d9f6d91e29e1d7": "Ransomware.Locky",
    "4b1a91c4c81fd5b3f5022c5a53bd3b5c": "Trojan.Emotet",
    "b6f2e008e7d0c920eb2d3042f7a2b478": "Backdoor.Remcos",
    "c0cbe3425d327e834e7c2c5c1f4a3b95": "Ransomware.Ryuk",
    "e57c9d99b02adbe998f3f4a3a2c9d0f5": "Trojan.AgentTesla",
    "a93ee7ea8c0e9a3178d97b23ee6f9d7f": "Worm.Conficker",
    "b3c39aeb14425f137b5bd0fd7c79fc45": "Backdoor.Gh0st"
}

# File signatures for detecting file types regardless of extension
FILE_SIGNATURES = {
    # Executable formats
    b'MZ': "PE/Windows Executable",
    b'\x7FELF': "ELF/Linux Executable",
    b'\xCA\xFE\xBA\xBE': "Mach-O/macOS Executable",

    # Archive formats
    b'PK\x03\x04': "ZIP Archive",
    b'Rar!\x1A\x07': "RAR Archive",
    b'7z\xBC\xAF\x27\x1C': "7-Zip Archive",

    # Office formats
    b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': "MS Office Document",
    b'PK\x03\x04\x14\x00\x06\x00': "Office Open XML Document",

    # Script formats
    b'#!/': "Shell Script",
    b'<?php': "PHP Script",
    b'<%@': "ASP Script",

    # PDF format
    b'%PDF': "PDF Document"
}

# Malicious content patterns (byte sequences found in malware)
MALICIOUS_PATTERNS = [
    # PowerShell obfuscation/execution patterns
    b'powershell.exe -e',
    b'powershell.exe -enc',
    b'powershell.exe -encodedcommand',
    b'hidden -e',
    b'bypass -e',
    b'IEX(',
    b'Invoke-Expression',

    # Command execution
    b'cmd.exe /c',
    b'cmd.exe /k',
    b'wscript.exe',
    b'cscript.exe',

    # Common shellcode patterns
    b'\x90\x90\x90\x90\x90',  # NOP sled

    # Common malware strings
    b'WScript.Shell',
    b'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
    b'CreateObject("Scripting.FileSystemObject")',

    # Suspicious URL patterns
    b'http://bit.ly/',
    b'http://goo.gl/',
    b'http://tinyurl.com/',

    # Suspicious registry operations
    b'RegCreateKeyEx',
    b'RegSetValueEx',

    # Process injection indicators
    b'VirtualAlloc',
    b'WriteProcessMemory',
    b'CreateRemoteThread'
]

# YARA rules as strings (will be compiled if yara-python is available)
YARA_RULES_STR = """
rule SuspiciousPowerShell {
    strings:
        $enc1 = "encodedcommand" nocase
        $enc2 = "-e " nocase
        $enc3 = "-enc " nocase
        $enc4 = "-EncodedCommand" nocase
        $enc5 = "FromBase64String" nocase
        $bypass = "-ExecutionPolicy bypass" nocase
        $hidden = "-w hidden" nocase
        $iex1 = "iex(" nocase
        $iex2 = "Invoke-Expression" nocase
    condition:
        any of them
}

rule SuspiciousExecutables {
    strings:
        $autorun = "autorun.inf" nocase
        $vbsrun = "wscript" nocase
        $cmdrun = "cmd.exe /c" nocase
        $regrun = "CurrentVersion\\Run" nocase
        $regrun2 = "CurrentVersion\\RunOnce" nocase
    condition:
        any of them
}

rule PotentialRansomware {
    strings:
        $str1 = "Your files have been encrypted" nocase
        $str2 = "pay the ransom" nocase
        $str3 = "bitcoin" nocase
        $str4 = "decrypt your files" nocase
        $str5 = "your important files encryption produced" nocase
        $ext1 = ".encrypted" nocase
        $ext2 = ".locked" nocase
        $ext3 = ".crypt" nocase
        $ext4 = ".crypted" nocase
        $ext5 = ".cerber" nocase
        $ext6 = ".locky" nocase
    condition:
        any of them
}
"""

class USBScanner:
    def __init__(self):
        self.system = platform.system()
        self.scan_results = {
            "malicious_files": [],
            "suspicious_files": [],
            "scanned_files": 0,
            "start_time": None,
            "end_time": None,
            "status": "not_started"
        }

        # Initialize YARA rules if available
        self.yara_rules = None
        if HAS_YARA:
            try:
                import yara
                self.yara_rules = yara.compile(source=YARA_RULES_STR)
                logger.info("YARA rules compiled successfully")
            except Exception as e:
                logger.error(f"Error compiling YARA rules: {str(e)}")

    def _calculate_md5(self, file_path):
        """Calculate MD5 hash of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating MD5 for {file_path}: {str(e)}")
            return None

    def _is_suspicious_filename(self, filename):
        """Check if filename matches suspicious patterns."""
        for pattern in SUSPICIOUS_PATTERNS:
            if re.match(pattern, filename, re.IGNORECASE):
                return True
        return False

    def _is_hidden_file(self, file_path):
        """Check if file is hidden."""
        if self.system == "Windows":
            import ctypes
            try:
                attrs = ctypes.windll.kernel32.GetFileAttributesW(file_path)
                return attrs != -1 and bool(attrs & 2)  # 2 is FILE_ATTRIBUTE_HIDDEN
            except:
                return False
        else:
            return os.path.basename(file_path).startswith('.')

    def _check_file_signature(self, file_path):
        """Check file signature to detect file type regardless of extension."""
        try:
            with open(file_path, "rb") as f:
                header = f.read(16)  # Read first 16 bytes for signature

            for signature, file_type in FILE_SIGNATURES.items():
                if header.startswith(signature):
                    return file_type

            return None
        except Exception as e:
            logger.error(f"Error checking file signature for {file_path}: {str(e)}")
            return None

    def _check_malicious_patterns(self, file_path):
        """Check for malicious byte patterns in file."""
        try:
            # Only scan files smaller than 10MB to avoid performance issues
            if os.path.getsize(file_path) > 10 * 1024 * 1024:
                return None

            with open(file_path, "rb") as f:
                content = f.read()

            for pattern in MALICIOUS_PATTERNS:
                if pattern in content:
                    return f"Contains malicious pattern: {pattern.decode('utf-8', errors='ignore')}"

            return None
        except Exception as e:
            logger.error(f"Error checking malicious patterns for {file_path}: {str(e)}")
            return None

    def _calculate_entropy(self, file_path):
        """Calculate Shannon entropy of file to detect encryption/packing."""
        try:
            # Only calculate entropy for files smaller than 10MB
            if os.path.getsize(file_path) > 10 * 1024 * 1024:
                return 0

            with open(file_path, "rb") as f:
                data = f.read()

            if not data:
                return 0

            # Count byte frequency
            byte_count = {}
            for byte in data:
                byte_count[byte] = byte_count.get(byte, 0) + 1

            # Calculate entropy
            entropy = 0
            for count in byte_count.values():
                probability = count / len(data)
                entropy -= probability * math.log2(probability)

            return entropy
        except Exception as e:
            logger.error(f"Error calculating entropy for {file_path}: {str(e)}")
            return 0

    def _check_extension_mismatch(self, file_path):
        """Check if file extension matches actual file type."""
        try:
            actual_type = self._check_file_signature(file_path)
            if not actual_type:
                return False

            filename = os.path.basename(file_path).lower()

            # Check for mismatches
            if "executable" in actual_type.lower() and not any(filename.endswith(ext) for ext in ['.exe', '.dll', '.sys']):
                return True

            if "office" in actual_type.lower() and not any(filename.endswith(ext) for ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
                return True

            if "archive" in actual_type.lower() and not any(filename.endswith(ext) for ext in ['.zip', '.rar', '.7z']):
                return True

            return False
        except Exception as e:
            logger.error(f"Error checking extension mismatch for {file_path}: {str(e)}")
            return False

    def _scan_with_yara(self, file_path):
        """Scan file with YARA rules if available."""
        if not self.yara_rules:
            return None

        try:
            # Only scan files smaller than 10MB
            if os.path.getsize(file_path) > 10 * 1024 * 1024:
                return None

            matches = self.yara_rules.match(file_path)
            if matches:
                return [match.rule for match in matches]
            return None
        except Exception as e:
            logger.error(f"Error scanning with YARA for {file_path}: {str(e)}")
            return None

    def _scan_file(self, file_path):
        """Scan a single file for threats using multiple detection methods."""
        try:
            # Skip directories
            if os.path.isdir(file_path):
                return

            self.scan_results["scanned_files"] += 1
            detection_reasons = []

            # Basic checks
            is_hidden = self._is_hidden_file(file_path)
            if is_hidden:
                detection_reasons.append("Hidden file")

            filename = os.path.basename(file_path)
            is_suspicious_name = self._is_suspicious_filename(filename)
            if is_suspicious_name:
                detection_reasons.append("Suspicious filename")

            # Advanced checks
            # 1. File signature check
            file_type = self._check_file_signature(file_path)
            extension_mismatch = self._check_extension_mismatch(file_path)
            if extension_mismatch:
                detection_reasons.append(f"Extension mismatch (actual type: {file_type})")

            # 2. Entropy check (high entropy may indicate encryption or packing)
            entropy = self._calculate_entropy(file_path)
            if entropy > 7.5:  # Threshold for high entropy
                detection_reasons.append(f"High entropy ({entropy:.2f}/8.0)")

            # 3. Malicious pattern check
            malicious_pattern = self._check_malicious_patterns(file_path)
            if malicious_pattern:
                detection_reasons.append(malicious_pattern)

            # 4. YARA rules check
            yara_matches = self._scan_with_yara(file_path)
            if yara_matches:
                detection_reasons.append(f"YARA matches: {', '.join(yara_matches)}")

            # 5. Hash check
            file_hash = None
            is_executable = any(filename.lower().endswith(ext) for ext in ['.exe', '.dll', '.sys', '.bat', '.vbs', '.ps1', '.js'])

            # Always check hash for executables or if other suspicious indicators were found
            if is_executable or detection_reasons:
                file_hash = self._calculate_md5(file_path)
                if file_hash in MALICIOUS_HASHES:
                    self.scan_results["malicious_files"].append({
                        "path": file_path,
                        "threat": MALICIOUS_HASHES[file_hash],
                        "hash": file_hash,
                        "detection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                        "additional_info": detection_reasons
                    })
                    return  # No need to add to suspicious files if it's already marked as malicious

            # Add to suspicious files if any detection reasons were found
            if detection_reasons:
                self.scan_results["suspicious_files"].append({
                    "path": file_path,
                    "reason": " | ".join(detection_reasons),
                    "hash": file_hash,
                    "detection_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                })

        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")

    def scan_drive(self, drive_path):
        """Scan an entire drive for threats."""
        try:
            self.scan_results = {
                "malicious_files": [],
                "suspicious_files": [],
                "scanned_files": 0,
                "start_time": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                "end_time": None,
                "status": "in_progress",
                "scan_methods": {
                    "hash_checking": True,
                    "pattern_matching": True,
                    "entropy_analysis": True,
                    "file_signature_analysis": True,
                    "yara_rules": HAS_YARA
                }
            }

            logger.info(f"Starting scan of {drive_path}")

            # Check if path exists
            if not os.path.exists(drive_path):
                logger.error(f"Path does not exist: {drive_path}")
                self.scan_results["status"] = "error"
                self.scan_results["error"] = f"Path does not exist: {drive_path}"
                return self.scan_results

            # Walk through all files in the drive
            for root, _, files in os.walk(drive_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self._scan_file(file_path)

            self.scan_results["end_time"] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            self.scan_results["status"] = "completed"

            logger.info(f"Scan completed. Scanned {self.scan_results['scanned_files']} files, "
                       f"found {len(self.scan_results['malicious_files'])} malicious and "
                       f"{len(self.scan_results['suspicious_files'])} suspicious files.")

            return self.scan_results

        except Exception as e:
            logger.error(f"Error scanning drive {drive_path}: {str(e)}")
            self.scan_results["status"] = "error"
            self.scan_results["error"] = str(e)
            return self.scan_results

# Example usage
if __name__ == "__main__":
    scanner = USBScanner()

    # Example: Scan a specific drive
    if platform.system() == "Windows":
        results = scanner.scan_drive("D:\\")
    else:
        results = scanner.scan_drive("/media/usb")

    print(f"Scan completed. Results: {results}")
