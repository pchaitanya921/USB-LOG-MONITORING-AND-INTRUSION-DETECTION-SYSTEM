import os
import time
import subprocess
import re
import hashlib
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suspicious file extensions and patterns
SUSPICIOUS_EXTENSIONS = [
    '.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.js', '.jar', '.hta',
    '.scr', '.pif', '.reg', '.vbe', '.wsf', '.wsh', '.msi', '.com'
]

SUSPICIOUS_PATTERNS = [
    rb'powershell -e', rb'cmd.exe /c', rb'rundll32', rb'regsvr32',
    rb'wscript.exe', rb'cscript.exe', rb'mshta.exe', rb'certutil -urlcache',
    rb'bitsadmin /transfer', rb'Invoke-Expression', rb'iex ', rb'Invoke-WebRequest',
    rb'wget ', rb'curl ', rb'Net.WebClient', rb'DownloadFile', rb'DownloadString',
    rb'shell_exec', rb'exec(', rb'eval(', rb'system(', rb'passthru', rb'base64_decode'
]

def scan_device(mount_point):
    """
    Scan a USB device for malware and suspicious files
    
    Args:
        mount_point: The mount point of the USB device
        
    Returns:
        dict: Scan results including total files, scanned files, and infected files
    """
    if not os.path.exists(mount_point):
        raise ValueError(f"Mount point {mount_point} does not exist")
    
    results = {
        'total_files': 0,
        'scanned_files': 0,
        'infected_files': [],
        'suspicious_files': []
    }
    
    # Try to use ClamAV if available
    has_clamav = check_clamav_available()
    
    # Walk through all files on the USB
    for root, dirs, files in os.walk(mount_point):
        results['total_files'] += len(files)
        
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                # Skip files that are too large (> 100MB)
                if os.path.getsize(file_path) > 100 * 1024 * 1024:
                    continue
                
                results['scanned_files'] += 1
                
                # Check with ClamAV if available
                if has_clamav:
                    scan_result = scan_with_clamav(file_path)
                    if scan_result:
                        results['infected_files'].append({
                            'file_path': file_path,
                            'threat_name': scan_result,
                            'threat_type': 'malware'
                        })
                        continue
                
                # Check with VirusTotal API if configured
                if 'VIRUSTOTAL_API_KEY' in os.environ:
                    vt_result = scan_with_virustotal(file_path)
                    if vt_result and vt_result['positives'] > 0:
                        results['infected_files'].append({
                            'file_path': file_path,
                            'threat_name': vt_result['threat_name'],
                            'threat_type': 'malware'
                        })
                        continue
                
                # Check for suspicious files based on extension and content
                if is_suspicious_file(file_path):
                    results['suspicious_files'].append({
                        'file_path': file_path,
                        'threat_name': 'Suspicious file',
                        'threat_type': 'suspicious'
                    })
            
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
    
    return results

def check_clamav_available():
    """Check if ClamAV is available on the system"""
    try:
        result = subprocess.run(['clamscan', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def scan_with_clamav(file_path):
    """
    Scan a file with ClamAV
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        str: Threat name if infected, None otherwise
    """
    try:
        result = subprocess.run(['clamscan', '--no-summary', file_path], 
                              capture_output=True, text=True, timeout=30)
        
        # Check if the file is infected
        if result.returncode == 1:
            # Extract the threat name
            match = re.search(r': ([^:]+) FOUND', result.stdout)
            if match:
                return match.group(1)
    except:
        pass
    
    return None

def scan_with_virustotal(file_path):
    """
    Scan a file with VirusTotal API
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        dict: Scan results if infected, None otherwise
    """
    api_key = os.environ.get('VIRUSTOTAL_API_KEY')
    if not api_key:
        return None
    
    try:
        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Check if the file is already known to VirusTotal
        url = f'https://www.virustotal.com/api/v3/files/{file_hash}'
        headers = {'x-apikey': api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if the file is malicious
            stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
            positives = stats.get('malicious', 0) + stats.get('suspicious', 0)
            
            if positives > 0:
                # Get the most common threat name
                scans = data.get('data', {}).get('attributes', {}).get('last_analysis_results', {})
                threat_names = [result['result'] for result in scans.values() if result['result']]
                
                # Count occurrences of each threat name
                threat_counts = {}
                for name in threat_names:
                    if name in threat_counts:
                        threat_counts[name] += 1
                    else:
                        threat_counts[name] = 1
                
                # Get the most common threat name
                threat_name = max(threat_counts.items(), key=lambda x: x[1])[0] if threat_counts else 'Unknown threat'
                
                return {
                    'positives': positives,
                    'threat_name': threat_name
                }
        
        # If the file is not known to VirusTotal or not malicious
        return None
    
    except Exception as e:
        print(f"Error scanning with VirusTotal: {e}")
        return None

def is_suspicious_file(file_path):
    """
    Check if a file is suspicious based on extension and content
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        bool: True if the file is suspicious, False otherwise
    """
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    if ext in SUSPICIOUS_EXTENSIONS:
        # For executable files, check the content for suspicious patterns
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024 * 1024)  # Read up to 1MB
                
                for pattern in SUSPICIOUS_PATTERNS:
                    if pattern in content:
                        return True
        except:
            pass
    
    return False
