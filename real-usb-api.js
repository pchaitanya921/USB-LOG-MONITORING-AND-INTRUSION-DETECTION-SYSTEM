/**
 * Real USB Monitoring API Client
 * Connects to the real USB monitoring backend for device detection and scanning
 */

// API base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Polling intervals (in milliseconds)
const DEVICE_POLL_INTERVAL = 3000;
const SCAN_POLL_INTERVAL = 5000;
const ALERT_POLL_INTERVAL = 5000;

// Polling timers
let devicePollTimer = null;
let scanPollTimer = null;
let alertPollTimer = null;

// Cache for data
let deviceCache = [];
let scanCache = [];
let alertCache = [];

// Event callbacks
const eventCallbacks = {
    'deviceConnected': [],
    'deviceDisconnected': [],
    'scanStarted': [],
    'scanProgress': [],
    'scanCompleted': [],
    'newAlert': [],
    'error': []
};

/**
 * Initialize the USB monitoring API client
 */
function initUsbMonitoringApi() {
    console.log('Initializing USB Monitoring API Client');
    
    // Start polling for devices
    startDevicePolling();
    
    // Start polling for scans
    startScanPolling();
    
    // Start polling for alerts
    startAlertPolling();
    
    // Add event listener for page unload
    window.addEventListener('beforeunload', () => {
        stopPolling();
    });
}

/**
 * Start polling for USB devices
 */
function startDevicePolling() {
    // Clear existing timer
    if (devicePollTimer) {
        clearInterval(devicePollTimer);
    }
    
    // Initial fetch
    fetchDevices();
    
    // Set up polling
    devicePollTimer = setInterval(fetchDevices, DEVICE_POLL_INTERVAL);
}

/**
 * Start polling for scan results
 */
function startScanPolling() {
    // Clear existing timer
    if (scanPollTimer) {
        clearInterval(scanPollTimer);
    }
    
    // Initial fetch
    fetchScans();
    
    // Set up polling
    scanPollTimer = setInterval(fetchScans, SCAN_POLL_INTERVAL);
}

/**
 * Start polling for alerts
 */
function startAlertPolling() {
    // Clear existing timer
    if (alertPollTimer) {
        clearInterval(alertPollTimer);
    }
    
    // Initial fetch
    fetchAlerts();
    
    // Set up polling
    alertPollTimer = setInterval(fetchAlerts, ALERT_POLL_INTERVAL);
}

/**
 * Stop all polling
 */
function stopPolling() {
    if (devicePollTimer) {
        clearInterval(devicePollTimer);
        devicePollTimer = null;
    }
    
    if (scanPollTimer) {
        clearInterval(scanPollTimer);
        scanPollTimer = null;
    }
    
    if (alertPollTimer) {
        clearInterval(alertPollTimer);
        alertPollTimer = null;
    }
}

/**
 * Fetch USB devices from the API
 */
function fetchDevices() {
    fetch(`${API_BASE_URL}/devices`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(devices => {
            // Check for new or disconnected devices
            checkForDeviceChanges(devices);
            
            // Update cache
            deviceCache = devices;
            
            // Update UI if needed
            if (typeof updateDeviceList === 'function') {
                updateDeviceList(devices);
            }
            
            // Update dashboard if needed
            if (typeof updateDashboardDevices === 'function') {
                updateDashboardDevices(devices);
            }
        })
        .catch(error => {
            console.error('Error fetching devices:', error);
            triggerEvent('error', { message: 'Failed to fetch USB devices', error });
        });
}

/**
 * Check for device changes (new connections or disconnections)
 */
function checkForDeviceChanges(newDevices) {
    // Check for new devices
    for (const device of newDevices) {
        const cachedDevice = deviceCache.find(d => d.id === device.id);
        
        if (!cachedDevice) {
            // New device
            triggerEvent('deviceConnected', device);
            
            // Show notification
            if (typeof showNotification === 'function') {
                showNotification(
                    'USB Device Connected',
                    `${device.product_name} has been connected and set to ${device.status} mode.`,
                    'info'
                );
            }
        } else if (cachedDevice.is_connected !== device.is_connected) {
            if (device.is_connected) {
                // Device reconnected
                triggerEvent('deviceConnected', device);
                
                // Show notification
                if (typeof showNotification === 'function') {
                    showNotification(
                        'USB Device Connected',
                        `${device.product_name} has been reconnected and set to ${device.status} mode.`,
                        'info'
                    );
                }
            } else {
                // Device disconnected
                triggerEvent('deviceDisconnected', device);
                
                // Show notification
                if (typeof showNotification === 'function') {
                    showNotification(
                        'USB Device Disconnected',
                        `${device.product_name} has been disconnected.`,
                        'info'
                    );
                }
            }
        }
    }
    
    // Check for disconnected devices
    for (const cachedDevice of deviceCache) {
        const stillExists = newDevices.some(d => d.id === cachedDevice.id);
        
        if (!stillExists && cachedDevice.is_connected) {
            // Device was removed from the system
            triggerEvent('deviceDisconnected', cachedDevice);
            
            // Show notification
            if (typeof showNotification === 'function') {
                showNotification(
                    'USB Device Disconnected',
                    `${cachedDevice.product_name} has been disconnected.`,
                    'info'
                );
            }
        }
    }
}

/**
 * Fetch scan results from the API
 */
function fetchScans() {
    fetch(`${API_BASE_URL}/scans`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(scans => {
            // Check for new or updated scans
            checkForScanChanges(scans);
            
            // Update cache
            scanCache = scans;
            
            // Update UI if needed
            if (typeof updateScanList === 'function') {
                updateScanList(scans);
            }
            
            // Update dashboard if needed
            if (typeof updateDashboardScans === 'function') {
                updateDashboardScans(scans);
            }
        })
        .catch(error => {
            console.error('Error fetching scans:', error);
            triggerEvent('error', { message: 'Failed to fetch scan results', error });
        });
}

/**
 * Check for scan changes (new or updated scans)
 */
function checkForScanChanges(newScans) {
    // Check for new or updated scans
    for (const scan of newScans) {
        const cachedScan = scanCache.find(s => s.id === scan.id);
        
        if (!cachedScan) {
            // New scan
            if (scan.status === 'in_progress') {
                triggerEvent('scanStarted', scan);
                
                // Show notification
                if (typeof showNotification === 'function') {
                    const device = deviceCache.find(d => d.id === scan.device_id);
                    const deviceName = device ? device.product_name : `Device ${scan.device_id}`;
                    
                    showNotification(
                        'Scan Started',
                        `Scanning ${deviceName} for threats...`,
                        'info'
                    );
                }
            } else if (scan.status === 'completed') {
                triggerEvent('scanCompleted', scan);
                
                // Show notification
                if (typeof showNotification === 'function') {
                    const device = deviceCache.find(d => d.id === scan.device_id);
                    const deviceName = device ? device.product_name : `Device ${scan.device_id}`;
                    
                    let message = `Scan completed on ${deviceName}`;
                    let type = 'success';
                    
                    if (scan.infected_files > 0) {
                        message += ` - ${scan.infected_files} malicious files detected!`;
                        type = 'danger';
                    } else if (scan.suspicious_files > 0) {
                        message += ` - ${scan.suspicious_files} suspicious files detected`;
                        type = 'warning';
                    } else {
                        message += ' - No threats found';
                    }
                    
                    showNotification('Scan Complete', message, type);
                }
            }
        } else if (cachedScan.status !== scan.status) {
            // Scan status changed
            if (scan.status === 'completed') {
                triggerEvent('scanCompleted', scan);
                
                // Show notification
                if (typeof showNotification === 'function') {
                    const device = deviceCache.find(d => d.id === scan.device_id);
                    const deviceName = device ? device.product_name : `Device ${scan.device_id}`;
                    
                    let message = `Scan completed on ${deviceName}`;
                    let type = 'success';
                    
                    if (scan.infected_files > 0) {
                        message += ` - ${scan.infected_files} malicious files detected!`;
                        type = 'danger';
                    } else if (scan.suspicious_files > 0) {
                        message += ` - ${scan.suspicious_files} suspicious files detected`;
                        type = 'warning';
                    } else {
                        message += ' - No threats found';
                    }
                    
                    showNotification('Scan Complete', message, type);
                }
            } else if (scan.status === 'error') {
                triggerEvent('error', { message: 'Scan failed', scan });
                
                // Show notification
                if (typeof showNotification === 'function') {
                    const device = deviceCache.find(d => d.id === scan.device_id);
                    const deviceName = device ? device.product_name : `Device ${scan.device_id}`;
                    
                    showNotification(
                        'Scan Failed',
                        `Failed to scan ${deviceName}: ${scan.error || 'Unknown error'}`,
                        'danger'
                    );
                }
            }
        } else if (cachedScan.scanned_files !== scan.scanned_files) {
            // Scan progress updated
            triggerEvent('scanProgress', scan);
        }
    }
}

/**
 * Fetch alerts from the API
 */
function fetchAlerts() {
    fetch(`${API_BASE_URL}/alerts`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(alerts => {
            // Check for new alerts
            checkForNewAlerts(alerts);
            
            // Update cache
            alertCache = alerts;
            
            // Update UI if needed
            if (typeof updateAlertList === 'function') {
                updateAlertList(alerts);
            }
            
            // Update dashboard if needed
            if (typeof updateDashboardAlerts === 'function') {
                updateDashboardAlerts(alerts);
            }
        })
        .catch(error => {
            console.error('Error fetching alerts:', error);
            triggerEvent('error', { message: 'Failed to fetch alerts', error });
        });
}

/**
 * Check for new alerts
 */
function checkForNewAlerts(newAlerts) {
    // Check for new alerts
    for (const alert of newAlerts) {
        const cachedAlert = alertCache.find(a => a.id === alert.id);
        
        if (!cachedAlert) {
            // New alert
            triggerEvent('newAlert', alert);
            
            // Show notification for important alerts
            if (typeof showNotification === 'function' && alert.severity !== 'info') {
                const device = deviceCache.find(d => d.id === alert.device_id);
                const deviceName = device ? device.product_name : `Device ${alert.device_id}`;
                
                showNotification(
                    'New Alert',
                    alert.message,
                    alert.severity
                );
            }
        }
    }
}

/**
 * Scan a USB device
 * @param {number} deviceId - The ID of the device to scan
 * @returns {Promise} - A promise that resolves with the scan result
 */
function scanDevice(deviceId) {
    return fetch(`${API_BASE_URL}/devices/${deviceId}/scan`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Show notification
                if (typeof showNotification === 'function') {
                    showNotification(
                        'Scan Started',
                        `Scanning ${data.device.product_name} for threats...`,
                        'info'
                    );
                }
                
                // Trigger event
                triggerEvent('scanStarted', data.scan);
                
                return data;
            } else {
                throw new Error(data.message || 'Failed to start scan');
            }
        })
        .catch(error => {
            console.error('Error scanning device:', error);
            triggerEvent('error', { message: 'Failed to scan device', error });
            
            // Show notification
            if (typeof showNotification === 'function') {
                const device = deviceCache.find(d => d.id === deviceId);
                const deviceName = device ? device.product_name : `Device ${deviceId}`;
                
                showNotification(
                    'Scan Failed',
                    `Failed to scan ${deviceName}: ${error.message}`,
                    'danger'
                );
            }
            
            throw error;
        });
}

/**
 * Change device permissions
 * @param {number} deviceId - The ID of the device
 * @param {string} permissionStatus - The new permission status ('read_only', 'full_access', or 'blocked')
 * @returns {Promise} - A promise that resolves with the updated device
 */
function changeDevicePermissions(deviceId, permissionStatus) {
    return fetch(`${API_BASE_URL}/devices/${deviceId}/permissions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ permission_status: permissionStatus })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Show notification
                if (typeof showNotification === 'function') {
                    showNotification(
                        'Permissions Updated',
                        `${data.device.product_name} permissions set to ${permissionStatus}`,
                        'success'
                    );
                }
                
                // Update device in cache
                const deviceIndex = deviceCache.findIndex(d => d.id === deviceId);
                if (deviceIndex !== -1) {
                    deviceCache[deviceIndex] = data.device;
                }
                
                return data;
            } else {
                throw new Error(data.message || 'Failed to update permissions');
            }
        })
        .catch(error => {
            console.error('Error changing device permissions:', error);
            triggerEvent('error', { message: 'Failed to change device permissions', error });
            
            // Show notification
            if (typeof showNotification === 'function') {
                const device = deviceCache.find(d => d.id === deviceId);
                const deviceName = device ? device.product_name : `Device ${deviceId}`;
                
                showNotification(
                    'Permission Change Failed',
                    `Failed to change permissions for ${deviceName}: ${error.message}`,
                    'danger'
                );
            }
            
            throw error;
        });
}

/**
 * Get all USB devices
 * @returns {Array} - Array of device objects
 */
function getDevices() {
    return deviceCache;
}

/**
 * Get a specific USB device by ID
 * @param {number} deviceId - The ID of the device
 * @returns {Object|null} - The device object or null if not found
 */
function getDeviceById(deviceId) {
    return deviceCache.find(device => device.id === deviceId) || null;
}

/**
 * Get all scan results
 * @returns {Array} - Array of scan objects
 */
function getScans() {
    return scanCache;
}

/**
 * Get scan results for a specific device
 * @param {number} deviceId - The ID of the device
 * @returns {Array} - Array of scan objects for the device
 */
function getScansForDevice(deviceId) {
    return scanCache.filter(scan => scan.device_id === deviceId);
}

/**
 * Get all alerts
 * @returns {Array} - Array of alert objects
 */
function getAlerts() {
    return alertCache;
}

/**
 * Get alerts for a specific device
 * @param {number} deviceId - The ID of the device
 * @returns {Array} - Array of alert objects for the device
 */
function getAlertsForDevice(deviceId) {
    return alertCache.filter(alert => alert.device_id === deviceId);
}

/**
 * Register an event callback
 * @param {string} event - The event name
 * @param {Function} callback - The callback function
 */
function onEvent(event, callback) {
    if (eventCallbacks[event]) {
        eventCallbacks[event].push(callback);
    } else {
        console.warn(`Unknown event: ${event}`);
    }
}

/**
 * Trigger an event
 * @param {string} event - The event name
 * @param {*} data - The event data
 */
function triggerEvent(event, data) {
    if (eventCallbacks[event]) {
        for (const callback of eventCallbacks[event]) {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in ${event} event callback:`, error);
            }
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', initUsbMonitoringApi);
