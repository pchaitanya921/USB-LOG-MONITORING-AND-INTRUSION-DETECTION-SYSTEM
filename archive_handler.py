#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Archive Handler Module
Handles extraction and scanning of compressed archives
"""

import os
import zipfile
import tempfile
import shutil
import hashlib
import datetime

class ArchiveHandler:
    """Class for handling compressed archives"""
    
    @staticmethod
    def is_archive(file_path):
        """Check if file is a supported archive format"""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
    
    @staticmethod
    def extract_and_scan(file_path, scanner_callback, result_obj):
        """
        Extract archive and scan its contents
        
        Args:
            file_path: Path to the archive file
            scanner_callback: Function to call for scanning each extracted file
            result_obj: ScanResult object to update with findings
        
        Returns:
            Tuple of (is_malicious, is_suspicious)
        """
        _, ext = os.path.splitext(file_path)
        
        # Currently only supporting ZIP files
        if ext.lower() != '.zip':
            return False, False
        
        # Create temporary directory for extraction
        temp_dir = tempfile.mkdtemp(prefix="usb_monitor_scan_")
        
        try:
            # Check if the archive name itself contains suspicious patterns
            archive_name = os.path.basename(file_path)
            if ArchiveHandler._check_suspicious_archive_name(archive_name):
                result_obj.add_detection_detail(file_path, "suspicious", 
                                              "Archive name contains suspicious patterns")
                return True, False
            
            # Try to extract the archive
            if ext.lower() == '.zip':
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        # Check file names before extraction
                        malicious_found = False
                        suspicious_found = False
                        
                        # Check for suspicious or malicious file names in the archive
                        for zip_info in zip_ref.infolist():
                            file_name = zip_info.filename
                            
                            # Skip directories
                            if file_name.endswith('/'):
                                continue
                                
                            # Check if the file name is suspicious
                            if ArchiveHandler._check_malicious_file_name(file_name):
                                malicious_found = True
                                result_obj.add_detection_detail(
                                    f"{file_path}:{file_name}", 
                                    "malicious", 
                                    f"Archive contains file with malicious name: {file_name}"
                                )
                                result_obj.malicious_files.append(f"{file_path}:{file_name}")
                            elif ArchiveHandler._check_suspicious_file_name(file_name):
                                suspicious_found = True
                                result_obj.add_detection_detail(
                                    f"{file_path}:{file_name}", 
                                    "suspicious", 
                                    f"Archive contains file with suspicious name: {file_name}"
                                )
                                result_obj.suspicious_files.append(f"{file_path}:{file_name}")
                        
                        # If we already found malicious content, no need to extract
                        if malicious_found:
                            return True, suspicious_found
                            
                        # Extract for deeper scanning (limited to small archives to prevent zip bombs)
                        if zip_ref.infolist() and sum(zip_info.file_size for zip_info in zip_ref.infolist()) < 100 * 1024 * 1024:  # 100MB limit
                            zip_ref.extractall(temp_dir)
                            
                            # Scan extracted files
                            for root, _, files in os.walk(temp_dir):
                                for file_name in files:
                                    extracted_path = os.path.join(root, file_name)
                                    relative_path = os.path.relpath(extracted_path, temp_dir)
                                    
                                    # Add to scanned files list
                                    result_obj.add_scanned_file(f"{file_path}:{relative_path}", "scanning")
                                    
                                    # Scan the extracted file
                                    scan_result = scanner_callback(extracted_path)
                                    
                                    # Update scan result
                                    result_obj.add_scanned_file(f"{file_path}:{relative_path}", scan_result)
                                    
                                    if scan_result == "malicious":
                                        malicious_found = True
                                        result_obj.malicious_files.append(f"{file_path}:{relative_path}")
                                        result_obj.add_detection_detail(
                                            f"{file_path}:{relative_path}", 
                                            "malicious", 
                                            "Malicious file found inside archive"
                                        )
                                    elif scan_result == "suspicious":
                                        suspicious_found = True
                                        result_obj.suspicious_files.append(f"{file_path}:{relative_path}")
                                        result_obj.add_detection_detail(
                                            f"{file_path}:{relative_path}", 
                                            "suspicious", 
                                            "Suspicious file found inside archive"
                                        )
                except zipfile.BadZipFile:
                    # If we can't extract, mark as suspicious
                    result_obj.add_detection_detail(file_path, "suspicious", "Corrupted or password-protected ZIP file")
                    result_obj.suspicious_files.append(file_path)
                    return False, True
                    
            return malicious_found, suspicious_found
                
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @staticmethod
    def _check_malicious_file_name(file_name):
        """Check if file name indicates malicious content"""
        file_name_lower = file_name.lower()
        
        # Known ransomware extensions
        ransomware_extensions = [
            '.encrypt', '.locked', '.crypted', '.crypt', '.crypto', 
            '.enc', '.pay', '.ransom', '.wcry', '.wncry', '.wncryt', 
            '.crab', '.locky', '.zepto', '.cerber', '.cerber2', 
            '.cerber3', '.cryp1', '.onion', '.aaa', '.ecc', '.ezz', '.exx', 
            '.xyz', '.zzz', '.abc', '.ccc', '.vvv', '.xxx', '.ttt', '.micro', 
            '.encrypted', '.locked', '.crypto', '.matrix'
        ]
        
        # Check for ransomware extensions
        for ext in ransomware_extensions:
            if file_name_lower.endswith(ext):
                return True
        
        # Check for known malware names
        malware_names = [
            'wannacry', 'petya', 'notpetya', 'locky', 'cryptolocker', 
            'teslacrypt', 'cerber', 'jigsaw', 'cryptxxx', 'cryptowall',
            'ransomware', 'trojan', 'backdoor', 'rootkit', 'keylogger',
            'spyware', 'adware', 'worm', 'virus', 'exploit'
        ]
        
        for name in malware_names:
            if name in file_name_lower:
                return True
                
        return False
    
    @staticmethod
    def _check_suspicious_file_name(file_name):
        """Check if file name indicates suspicious content"""
        file_name_lower = file_name.lower()
        
        # Suspicious file names
        suspicious_names = [
            'crack', 'keygen', 'patch', 'serial', 'warez', 'nulled',
            'hack', 'leaked', 'stolen', 'password', 'credentials',
            'admin', 'root', 'login', 'bank', 'credit', 'card',
            'ssn', 'social', 'security', 'tax', 'financial'
        ]
        
        for name in suspicious_names:
            if name in file_name_lower:
                return True
                
        # Suspicious extensions for executables with double extensions
        if '.' in file_name_lower[:-4] and file_name_lower.endswith(('.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.js')):
            return True
            
        return False
    
    @staticmethod
    def _check_suspicious_archive_name(archive_name):
        """Check if archive name indicates suspicious content"""
        archive_name_lower = archive_name.lower()
        
        # Suspicious archive names
        suspicious_names = [
            'ransomware', 'malware', 'virus', 'trojan', 'exploit',
            'hack', 'crack', 'keygen', 'patch', 'warez', 'stolen',
            'leaked', 'password', 'credentials', 'sensitive'
        ]
        
        for name in suspicious_names:
            if name in archive_name_lower:
                return True
                
        return False
