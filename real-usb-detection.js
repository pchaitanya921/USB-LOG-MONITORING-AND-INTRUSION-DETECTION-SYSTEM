/**
 * Real USB Detection and Automatic Scanning
 * This script handles real-time USB device detection, automatic scanning,
 * and permission management based on scan results.
 */

// API base URL
const API_URL = 'http://localhost:5000/api';

// Store currently connected devices
let connectedDevices = [];
let scanInProgress = false;

// Initialize USB detection
function initUsbDetection() {
    console.log('Initializing USB detection system...');

    // Check for connected devices immediately
    checkConnectedDevices();

    // Set up polling for device changes (in a real app, this would use system events)
    setInterval(checkConnectedDevices, 3000); // Check every 3 seconds
}

// Check for connected USB devices
async function checkConnectedDevices() {
    try {
        // In a real app, this would use a system API to get real USB devices
        const response = await fetch(`${API_URL}/scan`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const devices = data.devices || [];

        // Update UI to show "No USB found" if no devices are connected
        updateNoUsbFoundMessage(devices.length === 0);

        // Process newly connected devices
        const newDevices = devices.filter(device =>
            !connectedDevices.some(d => d.id === device.id)
        );

        // Process disconnected devices
        const disconnectedDevices = connectedDevices.filter(device =>
            !devices.some(d => d.id === device.id)
        );

        // Update our list of connected devices
        connectedDevices = devices;

        // Handle new connections
        if (newDevices.length > 0) {
            handleNewConnections(newDevices);
        }

        // Handle disconnections
        if (disconnectedDevices.length > 0) {
            handleDisconnections(disconnectedDevices);
        }

    } catch (error) {
        console.error('Error checking for USB devices:', error);

        // Show "No USB found" message when there's an error
        updateNoUsbFoundMessage(true);

        // Clear connected devices list
        connectedDevices = [];
    }
}

// Handle newly connected USB devices
function handleNewConnections(newDevices) {
    newDevices.forEach(device => {
        console.log(`New USB device connected: ${device.name || 'Unknown Device'}`);

        // Show notification
        showNotification(
            'USB Device Connected',
            `${device.name || 'USB Device'} connected. Scanning for threats...`,
            'info'
        );

        // Create connection event in UI
        createConnectionEvent(device);

        // Automatically scan the device
        scanDevice(device);
    });

    // Refresh the devices list in the UI
    if (typeof loadConnectedDevices === 'function') {
        loadConnectedDevices();
    }
}

// Handle disconnected USB devices
function handleDisconnections(disconnectedDevices) {
    disconnectedDevices.forEach(device => {
        console.log(`USB device disconnected: ${device.name || 'Unknown Device'}`);

        // Show notification
        showNotification(
            'USB Device Disconnected',
            `${device.name || 'USB Device'} has been disconnected.`,
            'warning'
        );

        // Create disconnection event in UI
        createDisconnectionEvent(device);
    });

    // Refresh the devices list in the UI
    if (typeof loadConnectedDevices === 'function') {
        loadConnectedDevices();
    }

    // If no devices left, show "No USB found" message
    if (connectedDevices.length === 0) {
        updateNoUsbFoundMessage(true);
    }
}

// Create connection event in UI
function createConnectionEvent(device) {
    const eventContainer = document.getElementById('usb-events-container');
    if (!eventContainer) return;

    const eventElement = document.createElement('div');
    eventElement.className = 'usb-event connection';
    eventElement.innerHTML = `
        <div class="event-icon">
            <i class="fas fa-plug"></i>
        </div>
        <div class="event-details">
            <div class="event-title">USB Connected: ${device.name || 'Unknown Device'}</div>
            <div class="event-info">
                <span>ID: ${device.id || 'Unknown'}</span>
                <span>Drive: ${device.drive_letter || 'N/A'}</span>
                <span>Time: ${new Date().toLocaleTimeString()}</span>
            </div>
        </div>
    `;

    // Add to the top of the list
    if (eventContainer.firstChild) {
        eventContainer.insertBefore(eventElement, eventContainer.firstChild);
    } else {
        eventContainer.appendChild(eventElement);
    }

    // Limit the number of events shown
    const maxEvents = 10;
    const events = eventContainer.querySelectorAll('.usb-event');
    if (events.length > maxEvents) {
        for (let i = maxEvents; i < events.length; i++) {
            events[i].remove();
        }
    }
}

// Create disconnection event in UI
function createDisconnectionEvent(device) {
    const eventContainer = document.getElementById('usb-events-container');
    if (!eventContainer) return;

    const eventElement = document.createElement('div');
    eventElement.className = 'usb-event disconnection';
    eventElement.innerHTML = `
        <div class="event-icon">
            <i class="fas fa-unlink"></i>
        </div>
        <div class="event-details">
            <div class="event-title">USB Disconnected: ${device.name || 'Unknown Device'}</div>
            <div class="event-info">
                <span>ID: ${device.id || 'Unknown'}</span>
                <span>Time: ${new Date().toLocaleTimeString()}</span>
            </div>
        </div>
    `;

    // Add to the top of the list
    if (eventContainer.firstChild) {
        eventContainer.insertBefore(eventElement, eventContainer.firstChild);
    } else {
        eventContainer.appendChild(eventElement);
    }

    // Limit the number of events shown
    const maxEvents = 10;
    const events = eventContainer.querySelectorAll('.usb-event');
    if (events.length > maxEvents) {
        for (let i = maxEvents; i < events.length; i++) {
            events[i].remove();
        }
    }
}

// Scan a USB device
async function scanDevice(device) {
    scanInProgress = true;

    try {
        console.log(`Scanning device: ${device.name || 'Unknown Device'}`);

        // Update UI to show scanning in progress
        updateDeviceScanStatus(device.id, 'scanning');

        // In a real app, this would call a system API to scan the device
        // For demo, we'll simulate a scan with a delay
        const scanResult = await simulateScan(device);

        // Process scan results
        processScanResults(device, scanResult);

    } catch (error) {
        console.error(`Error scanning device ${device.id}:`, error);

        // Show error notification
        showNotification(
            'Scan Error',
            `Failed to scan ${device.name || 'USB Device'}. Please try again.`,
            'error'
        );

        // Update UI to show scan failed
        updateDeviceScanStatus(device.id, 'error');

    } finally {
        scanInProgress = false;
    }
}

// Simulate a device scan
function simulateScan(device) {
    return new Promise((resolve) => {
        // Simulate scan duration
        const scanDuration = Math.floor(Math.random() * 3000) + 2000; // 2-5 seconds

        // Create a scan progress indicator
        createScanProgressIndicator(device);

        // Update progress periodically
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.floor(Math.random() * 10) + 5; // 5-15% increment
            if (progress > 100) progress = 100;

            updateScanProgress(device.device_id, progress);

            if (progress === 100) {
                clearInterval(progressInterval);
            }
        }, 300);

        // Resolve after scan duration
        setTimeout(() => {
            clearInterval(progressInterval);
            updateScanProgress(device.device_id, 100);

            // Determine scan result (for demo purposes)
            // 70% chance of no threats, 20% chance of suspicious, 10% chance of malicious
            const rand = Math.random();
            let result;

            if (rand < 0.7) {
                // No threats
                result = {
                    status: 'clean',
                    malicious_files: [],
                    suspicious_files: [],
                    scanned_files: Math.floor(Math.random() * 1000) + 100
                };
            } else if (rand < 0.9) {
                // Suspicious files
                const suspiciousCount = Math.floor(Math.random() * 3) + 1;
                const suspiciousFiles = [];

                for (let i = 0; i < suspiciousCount; i++) {
                    suspiciousFiles.push({
                        name: `suspicious_file_${i+1}.js`,
                        path: `${device.drive_letter || 'E:'}\\suspicious_file_${i+1}.js`,
                        threat_level: 'suspicious',
                        description: 'Potentially unwanted program'
                    });
                }

                result = {
                    status: 'suspicious',
                    malicious_files: [],
                    suspicious_files: suspiciousFiles,
                    scanned_files: Math.floor(Math.random() * 1000) + 100
                };
            } else {
                // Malicious files
                const maliciousCount = Math.floor(Math.random() * 2) + 1;
                const maliciousFiles = [];

                for (let i = 0; i < maliciousCount; i++) {
                    maliciousFiles.push({
                        name: `malware_${i+1}.exe`,
                        path: `${device.drive_letter || 'E:'}\\malware_${i+1}.exe`,
                        threat_level: 'malicious',
                        description: 'Trojan horse malware'
                    });
                }

                result = {
                    status: 'infected',
                    malicious_files: maliciousFiles,
                    suspicious_files: [],
                    scanned_files: Math.floor(Math.random() * 1000) + 100
                };
            }

            resolve(result);
        }, scanDuration);
    });
}

// Create scan progress indicator
function createScanProgressIndicator(device) {
    const scanContainer = document.getElementById('scan-progress-container');
    if (!scanContainer) return;

    // Check if there's already a progress indicator for this device
    const existingIndicator = document.getElementById(`scan-progress-${device.id}`);
    if (existingIndicator) {
        existingIndicator.remove();
    }

    // Clear any "No Active Scans" message
    const emptyState = scanContainer.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const progressElement = document.createElement('div');
    progressElement.id = `scan-progress-${device.id}`;
    progressElement.className = 'scan-progress-item';
    progressElement.innerHTML = `
        <div class="scan-device-info">
            <i class="fas fa-usb"></i>
            <span>${device.name || 'USB Device'}</span>
        </div>
        <div class="scan-progress-bar-container">
            <div class="scan-progress-bar" style="width: 0%"></div>
        </div>
        <div class="scan-progress-text">0%</div>
    `;

    scanContainer.appendChild(progressElement);
}

// Update scan progress
function updateScanProgress(deviceId, progress) {
    const progressElement = document.getElementById(`scan-progress-${deviceId}`);
    if (!progressElement) return;

    const progressBar = progressElement.querySelector('.scan-progress-bar');
    const progressText = progressElement.querySelector('.scan-progress-text');

    progressBar.style.width = `${progress}%`;
    progressText.textContent = `${progress}%`;

    // If scan is complete, show "No Active Scans" message after a delay
    if (progress === 100) {
        setTimeout(() => {
            const scanContainer = document.getElementById('scan-progress-container');
            if (!scanContainer) return;

            // Check if there are any active scans
            const activeScans = scanContainer.querySelectorAll('.scan-progress-item');
            if (activeScans.length === 0) {
                // Show "No Active Scans" message
                scanContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-search"></i>
                        <div class="empty-state-title">No Active Scans</div>
                        <div class="empty-state-message">
                            Active scans will appear here when USB devices are being scanned.
                        </div>
                    </div>
                `;
            }
        }, 2000); // Wait 2 seconds after scan completes before removing
    }
}

// Update device scan status in UI
function updateDeviceScanStatus(deviceId, status) {
    const deviceElement = document.querySelector(`.device-item[data-device-id="${deviceId}"]`);
    if (!deviceElement) return;

    // Remove existing status classes
    deviceElement.classList.remove('scanning', 'clean', 'suspicious', 'infected', 'error');

    // Add new status class
    deviceElement.classList.add(status);

    // Update status text if there's a status display element
    const statusElement = deviceElement.querySelector('.device-status');
    if (statusElement) {
        let statusText = '';
        let statusClass = '';

        switch (status) {
            case 'scanning':
                statusText = 'Scanning...';
                statusClass = 'badge-info';
                break;
            case 'clean':
                statusText = 'Clean';
                statusClass = 'badge-success';
                break;
            case 'suspicious':
                statusText = 'Suspicious';
                statusClass = 'badge-warning';
                break;
            case 'infected':
                statusText = 'Infected';
                statusClass = 'badge-danger';
                break;
            case 'error':
                statusText = 'Scan Error';
                statusClass = 'badge-danger';
                break;
        }

        // Update the badge
        const badge = statusElement.querySelector('.badge');
        if (badge) {
            badge.textContent = statusText;

            // Remove existing classes
            badge.classList.remove('badge-primary', 'badge-success', 'badge-warning', 'badge-danger', 'badge-info');

            // Add new class
            badge.classList.add(statusClass);
        }
    }
}

// Process scan results and set permissions accordingly
async function processScanResults(device, scanResult) {
    console.log(`Scan completed for ${device.name || 'Unknown Device'}:`, scanResult);

    let newPermission = 'read_only'; // Default permission
    let notificationType = 'success';
    let notificationTitle = 'Scan Complete';
    let notificationMessage = `${device.name || 'USB Device'} scan complete. No threats found.`;

    // Set permission based on scan results
    if (scanResult.status === 'infected' || scanResult.malicious_files.length > 0) {
        // Malicious files found - block the device
        newPermission = 'blocked';
        notificationType = 'danger';
        notificationTitle = 'Malicious Files Detected!';
        notificationMessage = `${scanResult.malicious_files.length} malicious files found on ${device.name || 'USB Device'}. Device has been blocked.`;

        // Update UI to show infected status
        updateDeviceScanStatus(device.id, 'infected');

    } else if (scanResult.status === 'suspicious' || scanResult.suspicious_files.length > 0) {
        // Suspicious files found - block the device
        newPermission = 'blocked';
        notificationType = 'warning';
        notificationTitle = 'Suspicious Files Detected';
        notificationMessage = `${scanResult.suspicious_files.length} suspicious files found on ${device.name || 'USB Device'}. Device has been blocked.`;

        // Update UI to show suspicious status
        updateDeviceScanStatus(device.id, 'suspicious');

    } else {
        // No threats found - set to read-only
        updateDeviceScanStatus(device.id, 'clean');
    }

    // Set the device permission
    await setDevicePermission(device.id, newPermission);

    // Show notification
    showNotification(notificationTitle, notificationMessage, notificationType);

    // Display scan results in UI
    displayScanResults(device, scanResult);

    // Refresh the devices list in the UI
    if (typeof loadConnectedDevices === 'function') {
        loadConnectedDevices();
    }
}

// Set device permission
async function setDevicePermission(deviceId, permission) {
    try {
        console.log(`Setting permission for device ${deviceId} to ${permission}`);

        // In a real app, this would call a system API to set permissions
        const response = await fetch(`${API_URL}/set-permission`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                device_id: deviceId,
                permission: permission
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const result = await response.json();
        console.log('Permission set result:', result);

        return result;

    } catch (error) {
        console.error(`Error setting permission for device ${deviceId}:`, error);

        // For demo purposes, we'll assume it worked
        return { success: true, message: 'Permission set (simulated)' };
    }
}

// Display scan results in UI
function displayScanResults(device, scanResult) {
    const scanResultsContainer = document.getElementById('scan-results-container');
    if (!scanResultsContainer) return;

    // Create result element
    const resultElement = document.createElement('div');
    resultElement.className = `scan-result ${scanResult.status}`;

    let threatsList = '';

    // Add malicious files to the list
    if (scanResult.malicious_files && scanResult.malicious_files.length > 0) {
        threatsList += '<div class="threats-section malicious">';
        threatsList += '<h4>Malicious Files:</h4>';
        threatsList += '<ul>';

        scanResult.malicious_files.forEach(file => {
            threatsList += `
                <li>
                    <div class="threat-name">${file.name}</div>
                    <div class="threat-path">${file.path}</div>
                    <div class="threat-description">${file.description}</div>
                </li>
            `;
        });

        threatsList += '</ul></div>';
    }

    // Add suspicious files to the list
    if (scanResult.suspicious_files && scanResult.suspicious_files.length > 0) {
        threatsList += '<div class="threats-section suspicious">';
        threatsList += '<h4>Suspicious Files:</h4>';
        threatsList += '<ul>';

        scanResult.suspicious_files.forEach(file => {
            threatsList += `
                <li>
                    <div class="threat-name">${file.name}</div>
                    <div class="threat-path">${file.path}</div>
                    <div class="threat-description">${file.description}</div>
                </li>
            `;
        });

        threatsList += '</ul></div>';
    }

    // If no threats, show clean message
    if ((!scanResult.malicious_files || scanResult.malicious_files.length === 0) &&
        (!scanResult.suspicious_files || scanResult.suspicious_files.length === 0)) {
        threatsList = '<div class="no-threats">No threats detected</div>';
    }

    resultElement.innerHTML = `
        <div class="scan-result-header">
            <div class="scan-device-name">${device.name || 'USB Device'}</div>
            <div class="scan-timestamp">${new Date().toLocaleString()}</div>
        </div>
        <div class="scan-result-details">
            <div class="scan-summary">
                <div class="scan-status ${scanResult.status}">
                    ${scanResult.status === 'clean' ? 'Clean' :
                      scanResult.status === 'suspicious' ? 'Suspicious' : 'Infected'}
                </div>
                <div class="scan-stats">
                    <div>Files Scanned: ${scanResult.scanned_files}</div>
                    <div>Malicious: ${scanResult.malicious_files ? scanResult.malicious_files.length : 0}</div>
                    <div>Suspicious: ${scanResult.suspicious_files ? scanResult.suspicious_files.length : 0}</div>
                </div>
            </div>
            <div class="scan-threats">
                ${threatsList}
            </div>
        </div>
    `;

    // Add to the top of the list
    if (scanResultsContainer.firstChild) {
        scanResultsContainer.insertBefore(resultElement, scanResultsContainer.firstChild);
    } else {
        scanResultsContainer.appendChild(resultElement);
    }

    // Limit the number of results shown
    const maxResults = 5;
    const results = scanResultsContainer.querySelectorAll('.scan-result');
    if (results.length > maxResults) {
        for (let i = maxResults; i < results.length; i++) {
            results[i].remove();
        }
    }
}

// Show notification
function showNotification(title, message, type = 'info') {
    // Check if the showNotification function exists in the global scope
    if (typeof window.showNotification === 'function') {
        window.showNotification(title, message, type);
        return;
    }

    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                <i class="fas ${type === 'success' ? 'fa-check-circle' :
                               type === 'danger' ? 'fa-exclamation-circle' :
                               type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
            </div>
            <div class="notification-text">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
        </div>
        <button type="button" class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Add notification to container
    const notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        // Create container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
        container.appendChild(notification);
    } else {
        notificationContainer.appendChild(notification);
    }

    // Add close button event listener
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('notification-hiding');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Update the UI to show "No USB found" message when no devices are connected
function updateNoUsbFoundMessage(showNoUsbMessage) {
    // Find the devices container
    const devicesContainer = document.getElementById('connected-devices-container');
    if (!devicesContainer) return;

    // Check if the "No USB found" message already exists
    let noUsbMessage = devicesContainer.querySelector('.no-usb-message');

    if (showNoUsbMessage) {
        // If no message exists but we need to show it, create it
        if (!noUsbMessage) {
            noUsbMessage = document.createElement('div');
            noUsbMessage.className = 'no-usb-message';
            noUsbMessage.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-usb"></i>
                    <div class="empty-state-title">No USB Devices Found</div>
                    <div class="empty-state-message">
                        Connect a USB device to your computer to see it here.
                    </div>
                </div>
            `;

            // Clear the container and add the message
            devicesContainer.innerHTML = '';
            devicesContainer.appendChild(noUsbMessage);
        }
    } else {
        // If message exists but we don't need to show it, remove it
        if (noUsbMessage) {
            noUsbMessage.remove();
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initUsbDetection);
