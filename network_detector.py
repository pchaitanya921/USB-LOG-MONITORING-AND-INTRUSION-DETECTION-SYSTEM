#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Network Detector Module
Detects and monitors network devices
"""

import os
import time
import json
import socket
import platform
import threading
import datetime
import ipaddress
from PyQt5.QtCore import QObject, pyqtSignal

class NetworkDevice:
    """Class representing a network device"""
    def __init__(self, device_id, ip_address, mac_address=None, hostname=None, device_type=None):
        self.id = device_id
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.hostname = hostname
        self.device_type = device_type or "unknown"
        self.connection_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.last_seen = self.connection_time
        self.status = "active"
        self.is_trusted = False
        self.vendor = ""
        self.os_type = ""
        self.open_ports = []
        self.services = []
        self.last_scan_time = None
        self.scan_result = None
        self.connection_count = 1
        self.first_seen = self.connection_time
    
    def to_dict(self):
        """Convert device to dictionary for serialization"""
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "hostname": self.hostname,
            "device_type": self.device_type,
            "connection_time": self.connection_time,
            "last_seen": self.last_seen,
            "status": self.status,
            "is_trusted": self.is_trusted,
            "vendor": self.vendor,
            "os_type": self.os_type,
            "open_ports": self.open_ports,
            "services": self.services,
            "last_scan_time": self.last_scan_time,
            "scan_result": self.scan_result,
            "connection_count": self.connection_count,
            "first_seen": self.first_seen
        }
    
    def get_device_icon(self):
        """Get the appropriate icon for this device type"""
        if self.device_type == "router":
            return "assets/icons/network_router.png"
        elif self.device_type == "switch":
            return "assets/icons/network_switch.png"
        elif self.device_type == "server":
            return "assets/icons/network_server.png"
        elif self.device_type == "printer":
            return "assets/icons/network_printer.png"
        elif self.device_type == "camera":
            return "assets/icons/network_camera.png"
        elif self.device_type == "mobile":
            return "assets/icons/network_mobile.png"
        elif self.device_type == "iot":
            return "assets/icons/network_iot.png"
        else:
            return "assets/icons/network_device.png"

class NetworkDetector(QObject):
    """Class for detecting and monitoring network devices"""
    # Define signals
    device_connected = pyqtSignal(str)  # device_id
    device_disconnected = pyqtSignal(str)  # device_id
    device_updated = pyqtSignal(str)  # device_id
    scan_started = pyqtSignal(str)  # network_id
    scan_progress = pyqtSignal(str, int, int)  # network_id, scanned_devices, total_devices
    scan_finished = pyqtSignal(str, object)  # network_id, scan_result
    
    def __init__(self):
        super().__init__()
        self.devices = {}  # Dictionary of connected devices
        self.monitoring = False
        self.monitoring_thread = None
        self.scan_thread = None
        self.is_scanning = False
        self.local_ip = self._get_local_ip()
        self.network_prefix = self._get_network_prefix()
        
        # Load device history
        self._load_device_history()
    
    def _get_local_ip(self):
        """Get local IP address"""
        try:
            # Create a socket to determine the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def _get_network_prefix(self):
        """Get network prefix (e.g., 192.168.1)"""
        ip_parts = self.local_ip.split('.')
        if len(ip_parts) == 4:
            return '.'.join(ip_parts[:3])
        return "192.168.1"
    
    def _load_device_history(self):
        """Load device history from file"""
        history_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "network_history.json")
        
        self.device_history = {}
        
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    self.device_history = json.load(f)
            except Exception as e:
                print(f"Error loading network device history: {str(e)}")
    
    def _save_device_history(self):
        """Save device history to file"""
        history_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "network_history.json")
        
        try:
            with open(history_file, "w") as f:
                json.dump(self.device_history, f, indent=4)
        except Exception as e:
            print(f"Error saving network device history: {str(e)}")
    
    def _update_device_history(self, device):
        """Update device history with new device information"""
        if device.id not in self.device_history:
            # New device
            self.device_history[device.id] = {
                "ip_address": device.ip_address,
                "mac_address": device.mac_address,
                "hostname": device.hostname,
                "device_type": device.device_type,
                "first_seen": device.connection_time,
                "last_seen": device.last_seen,
                "connection_count": 1,
                "is_trusted": device.is_trusted,
                "vendor": device.vendor,
                "os_type": device.os_type
            }
        else:
            # Update existing device
            self.device_history[device.id]["last_seen"] = device.last_seen
            self.device_history[device.id]["connection_count"] += 1
            
            # Update device information if available
            if device.hostname:
                self.device_history[device.id]["hostname"] = device.hostname
            if device.mac_address:
                self.device_history[device.id]["mac_address"] = device.mac_address
            if device.device_type != "unknown":
                self.device_history[device.id]["device_type"] = device.device_type
            if device.vendor:
                self.device_history[device.id]["vendor"] = device.vendor
            if device.os_type:
                self.device_history[device.id]["os_type"] = device.os_type
            
            # Update trusted status
            self.device_history[device.id]["is_trusted"] = device.is_trusted
        
        # Save history
        self._save_device_history()
    
    def start_monitoring(self):
        """Start monitoring for network device changes"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_thread)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring for network device changes"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
            self.monitoring_thread = None
    
    def _monitoring_thread(self):
        """Thread function for monitoring network devices"""
        while self.monitoring:
            try:
                # Scan for devices
                current_devices = self._scan_network()
                
                # Check for new and updated devices
                for device_id, device in current_devices.items():
                    if device_id not in self.devices:
                        # New device
                        self.devices[device_id] = device
                        self._update_device_history(device)
                        self.device_connected.emit(device_id)
                    else:
                        # Update existing device
                        existing_device = self.devices[device_id]
                        existing_device.last_seen = device.last_seen
                        
                        # Update device information if available
                        if device.hostname and not existing_device.hostname:
                            existing_device.hostname = device.hostname
                        if device.mac_address and not existing_device.mac_address:
                            existing_device.mac_address = device.mac_address
                        
                        self._update_device_history(existing_device)
                        self.device_updated.emit(device_id)
                
                # Check for disconnected devices
                for device_id in list(self.devices.keys()):
                    if device_id not in current_devices:
                        # Device disconnected
                        self.devices[device_id].status = "disconnected"
                        self._update_device_history(self.devices[device_id])
                        self.device_disconnected.emit(device_id)
                        del self.devices[device_id]
            
            except Exception as e:
                print(f"Error in network monitoring thread: {str(e)}")
            
            # Sleep for a while
            time.sleep(60)  # Check every minute
    
    def _scan_network(self):
        """Scan network for devices"""
        devices = {}
        
        try:
            # Get network interface information
            if platform.system() == "Windows":
                devices = self._scan_network_windows()
            elif platform.system() == "Darwin":  # macOS
                devices = self._scan_network_macos()
            elif platform.system() == "Linux":
                devices = self._scan_network_linux()
            else:
                # Fallback to basic ping scan
                devices = self._scan_network_ping()
        
        except Exception as e:
            print(f"Error scanning network: {str(e)}")
        
        return devices
    
    def _scan_network_windows(self):
        """Scan network on Windows"""
        devices = {}
        
        try:
            # Use ARP to get network devices
            import subprocess
            
            # Run ARP command
            output = subprocess.check_output("arp -a", shell=True).decode('utf-8')
            
            # Parse output
            for line in output.splitlines():
                if "dynamic" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        ip_address = parts[0]
                        mac_address = parts[1]
                        
                        # Create device ID from MAC address
                        device_id = f"NET_{mac_address.replace('-', ':')}"
                        
                        # Try to get hostname
                        hostname = None
                        try:
                            hostname = socket.gethostbyaddr(ip_address)[0]
                        except:
                            pass
                        
                        # Create device
                        device = NetworkDevice(
                            device_id=device_id,
                            ip_address=ip_address,
                            mac_address=mac_address,
                            hostname=hostname
                        )
                        
                        # Determine device type based on MAC address
                        device.device_type = self._determine_device_type(mac_address)
                        
                        # Determine vendor based on MAC address
                        device.vendor = self._determine_vendor(mac_address)
                        
                        # Add to devices
                        devices[device_id] = device
        
        except Exception as e:
            print(f"Error scanning Windows network: {str(e)}")
        
        return devices
    
    def _scan_network_macos(self):
        """Scan network on macOS"""
        devices = {}
        
        try:
            # Use ARP to get network devices
            import subprocess
            
            # Run ARP command
            output = subprocess.check_output("arp -a", shell=True).decode('utf-8')
            
            # Parse output
            for line in output.splitlines():
                if ")" in line and "(" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        hostname = parts[0].split(".")[0]
                        ip_address = parts[1].strip("()")
                        mac_address = parts[3]
                        
                        # Create device ID from MAC address
                        device_id = f"NET_{mac_address}"
                        
                        # Create device
                        device = NetworkDevice(
                            device_id=device_id,
                            ip_address=ip_address,
                            mac_address=mac_address,
                            hostname=hostname
                        )
                        
                        # Determine device type based on MAC address
                        device.device_type = self._determine_device_type(mac_address)
                        
                        # Determine vendor based on MAC address
                        device.vendor = self._determine_vendor(mac_address)
                        
                        # Add to devices
                        devices[device_id] = device
        
        except Exception as e:
            print(f"Error scanning macOS network: {str(e)}")
        
        return devices
    
    def _scan_network_linux(self):
        """Scan network on Linux"""
        devices = {}
        
        try:
            # Use ARP to get network devices
            import subprocess
            
            # Run ARP command
            output = subprocess.check_output("arp -a", shell=True).decode('utf-8')
            
            # Parse output
            for line in output.splitlines():
                if "ether" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        hostname = parts[0]
                        ip_address = parts[1].strip("()")
                        mac_address = parts[3]
                        
                        # Create device ID from MAC address
                        device_id = f"NET_{mac_address}"
                        
                        # Create device
                        device = NetworkDevice(
                            device_id=device_id,
                            ip_address=ip_address,
                            mac_address=mac_address,
                            hostname=hostname
                        )
                        
                        # Determine device type based on MAC address
                        device.device_type = self._determine_device_type(mac_address)
                        
                        # Determine vendor based on MAC address
                        device.vendor = self._determine_vendor(mac_address)
                        
                        # Add to devices
                        devices[device_id] = device
        
        except Exception as e:
            print(f"Error scanning Linux network: {str(e)}")
        
        return devices
    
    def _scan_network_ping(self):
        """Scan network using ping (fallback method)"""
        devices = {}
        
        try:
            # Ping all IP addresses in the local network
            for i in range(1, 255):
                ip = f"{self.network_prefix}.{i}"
                
                # Skip local IP
                if ip == self.local_ip:
                    continue
                
                # Ping IP
                if self._ping(ip):
                    # Create device ID from IP address
                    device_id = f"NET_{ip.replace('.', '_')}"
                    
                    # Try to get hostname
                    hostname = None
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        pass
                    
                    # Create device
                    device = NetworkDevice(
                        device_id=device_id,
                        ip_address=ip,
                        hostname=hostname
                    )
                    
                    # Add to devices
                    devices[device_id] = device
        
        except Exception as e:
            print(f"Error scanning network with ping: {str(e)}")
        
        return devices
    
    def _ping(self, ip):
        """Ping an IP address"""
        try:
            # Use platform-specific ping command
            if platform.system() == "Windows":
                ping_cmd = f"ping -n 1 -w 1000 {ip}"
            else:
                ping_cmd = f"ping -c 1 -W 1 {ip}"
            
            # Run ping command
            return os.system(ping_cmd) == 0
        
        except:
            return False
    
    def _determine_device_type(self, mac_address):
        """Determine device type based on MAC address"""
        # In a real implementation, this would use a database of MAC address prefixes
        # For demo purposes, we'll return a random device type
        import random
        
        device_types = ["router", "switch", "server", "printer", "camera", "mobile", "iot", "unknown"]
        return random.choice(device_types)
    
    def _determine_vendor(self, mac_address):
        """Determine vendor based on MAC address"""
        # In a real implementation, this would use a database of MAC address prefixes
        # For demo purposes, we'll return a random vendor
        import random
        
        vendors = ["Cisco", "HP", "Dell", "Apple", "Samsung", "Netgear", "D-Link", "TP-Link", "Asus", "Unknown"]
        return random.choice(vendors)
    
    def get_connected_devices(self):
        """Get all connected network devices"""
        return self.devices
    
    def get_device(self, device_id):
        """Get a specific network device"""
        return self.devices.get(device_id)
    
    def scan_device(self, device_id):
        """Scan a specific network device"""
        if device_id not in self.devices:
            return False, "Device not found"
        
        if self.is_scanning:
            return False, "Scan already in progress"
        
        # Start scan in a separate thread
        self.scan_thread = threading.Thread(target=self._scan_device_thread, args=(device_id,))
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        return True, "Scan started"
    
    def _scan_device_thread(self, device_id):
        """Thread function for scanning a network device"""
        self.is_scanning = True
        self.scan_started.emit(device_id)
        
        try:
            device = self.devices[device_id]
            
            # Scan open ports
            open_ports = self._scan_ports(device.ip_address)
            device.open_ports = open_ports
            
            # Determine services based on open ports
            device.services = self._determine_services(open_ports)
            
            # Try to determine OS type
            device.os_type = self._determine_os_type(device.ip_address)
            
            # Update device
            device.last_scan_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            device.scan_result = "completed"
            
            # Update device history
            self._update_device_history(device)
            
            # Emit signal
            self.scan_finished.emit(device_id, device)
        
        except Exception as e:
            print(f"Error scanning device {device_id}: {str(e)}")
            self.scan_finished.emit(device_id, None)
        
        finally:
            self.is_scanning = False
    
    def _scan_ports(self, ip_address):
        """Scan open ports on a device"""
        open_ports = []
        
        # Common ports to scan
        common_ports = [21, 22, 23, 25, 53, 80, 110, 115, 135, 139, 143, 194, 443, 445, 1433, 3306, 3389, 5900, 8080]
        
        for port in common_ports:
            try:
                # Create socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                
                # Try to connect
                result = s.connect_ex((ip_address, port))
                
                # Check if port is open
                if result == 0:
                    open_ports.append(port)
                
                # Close socket
                s.close()
            
            except:
                pass
        
        return open_ports
    
    def _determine_services(self, open_ports):
        """Determine services based on open ports"""
        services = []
        
        # Common port to service mapping
        port_services = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            115: "SFTP",
            135: "RPC",
            139: "NetBIOS",
            143: "IMAP",
            194: "IRC",
            443: "HTTPS",
            445: "SMB",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5900: "VNC",
            8080: "HTTP-Proxy"
        }
        
        for port in open_ports:
            if port in port_services:
                services.append(port_services[port])
            else:
                services.append(f"Unknown ({port})")
        
        return services
    
    def _determine_os_type(self, ip_address):
        """Determine OS type of a device"""
        # In a real implementation, this would use OS fingerprinting techniques
        # For demo purposes, we'll return a random OS
        import random
        
        os_types = ["Windows", "Linux", "macOS", "iOS", "Android", "Embedded", "Unknown"]
        return random.choice(os_types)
    
    def scan_network(self):
        """Scan entire network"""
        if self.is_scanning:
            return False, "Scan already in progress"
        
        # Start scan in a separate thread
        self.scan_thread = threading.Thread(target=self._scan_network_thread)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
        return True, "Network scan started"
    
    def _scan_network_thread(self):
        """Thread function for scanning the entire network"""
        self.is_scanning = True
        network_id = f"NET_SCAN_{int(time.time())}"
        self.scan_started.emit(network_id)
        
        try:
            # Scan IP range
            network = ipaddress.IPv4Network(f"{self.network_prefix}.0/24", strict=False)
            total_ips = 254  # Excluding network and broadcast addresses
            
            # Scan each IP
            scanned = 0
            for ip in network.hosts():
                ip_str = str(ip)
                
                # Skip local IP
                if ip_str == self.local_ip:
                    continue
                
                # Update progress
                scanned += 1
                self.scan_progress.emit(network_id, scanned, total_ips)
                
                # Ping IP
                if self._ping(ip_str):
                    # Try to get hostname
                    hostname = None
                    try:
                        hostname = socket.gethostbyaddr(ip_str)[0]
                    except:
                        pass
                    
                    # Try to get MAC address
                    mac_address = self._get_mac_address(ip_str)
                    
                    # Create device ID
                    if mac_address:
                        device_id = f"NET_{mac_address.replace(':', '_')}"
                    else:
                        device_id = f"NET_{ip_str.replace('.', '_')}"
                    
                    # Check if device already exists
                    if device_id in self.devices:
                        # Update existing device
                        device = self.devices[device_id]
                        device.last_seen = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        
                        # Update hostname if available
                        if hostname and not device.hostname:
                            device.hostname = hostname
                        
                        # Update MAC address if available
                        if mac_address and not device.mac_address:
                            device.mac_address = mac_address
                        
                        # Update device history
                        self._update_device_history(device)
                        self.device_updated.emit(device_id)
                    else:
                        # Create new device
                        device = NetworkDevice(
                            device_id=device_id,
                            ip_address=ip_str,
                            mac_address=mac_address,
                            hostname=hostname
                        )
                        
                        # Determine device type based on MAC address
                        if mac_address:
                            device.device_type = self._determine_device_type(mac_address)
                            device.vendor = self._determine_vendor(mac_address)
                        
                        # Add to devices
                        self.devices[device_id] = device
                        self._update_device_history(device)
                        self.device_connected.emit(device_id)
            
            # Scan completed
            self.scan_finished.emit(network_id, {"status": "completed", "devices_found": len(self.devices)})
        
        except Exception as e:
            print(f"Error scanning network: {str(e)}")
            self.scan_finished.emit(network_id, {"status": "failed", "error": str(e)})
        
        finally:
            self.is_scanning = False
    
    def _get_mac_address(self, ip_address):
        """Get MAC address for an IP address"""
        try:
            # Use ARP to get MAC address
            if platform.system() == "Windows":
                import subprocess
                
                # Run ARP command
                output = subprocess.check_output(f"arp -a {ip_address}", shell=True).decode('utf-8')
                
                # Parse output
                for line in output.splitlines():
                    if ip_address in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1].replace('-', ':')
            
            elif platform.system() == "Darwin" or platform.system() == "Linux":
                import subprocess
                
                # Run ARP command
                output = subprocess.check_output(f"arp -n {ip_address}", shell=True).decode('utf-8')
                
                # Parse output
                for line in output.splitlines():
                    if ip_address in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        
        except:
            pass
        
        return None
    
    def set_device_trusted(self, device_id, trusted=True):
        """Set a device as trusted or untrusted"""
        if device_id in self.devices:
            self.devices[device_id].is_trusted = trusted
            self._update_device_history(self.devices[device_id])
            self.device_updated.emit(device_id)
            return True
        
        # Check device history
        if device_id in self.device_history:
            self.device_history[device_id]["is_trusted"] = trusted
            self._save_device_history()
            return True
        
        return False
    
    def get_device_history(self):
        """Get the history of all devices"""
        return self.device_history
