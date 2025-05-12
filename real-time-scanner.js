/**
 * Real-time USB Scanner Module
 * This module provides real-time USB scanning functionality that can be integrated
 * into any page of the USB monitoring system.
 */

// Global variables
let scanInProgress = false;
let currentScanDeviceId = null;
let scanTimers = {};

// Initialize the real-time scanner
function initRealTimeScanner() {
    console.log('Real-time USB scanner initialized');
    
    // Add event delegation for real-time scan buttons
    document.addEventListener('click', (event) => {
        if (event.target.closest('.realtime-scan-btn')) {
            const button = event.target.closest('.realtime-scan-btn');
            const deviceId = button.getAttribute('data-device-id');
            const deviceName = button.getAttribute('data-device-name');
            simulateRealTimeScan(deviceId, deviceName);
        }
    });
}

// Simulate real-time scanning
function simulateRealTimeScan(deviceId, deviceName) {
    if (scanInProgress && currentScanDeviceId === deviceId) {
        showNotification('Scan in Progress', `A scan is already in progress for this device.`, 'warning');
        return;
    }
    
    console.log(`Starting real-time scan for device ${deviceId}: ${deviceName}`);
    scanInProgress = true;
    currentScanDeviceId = deviceId;
    
    showNotification('Real-time Scan', `Starting real-time scan for ${deviceName}...`, 'info');
    createScanProgressContainer(deviceId, deviceName);
    
    // Simulate file counting
    setTimeout(() => {
        const totalFiles = Math.floor(Math.random() * 400) + 100; // Random between 100-500
        updateScanProgress({
            device_id: deviceId,
            total_files: totalFiles,
            scanned_files: 0,
            status: 'counting',
            percent: 0
        });
        
        // Simulate file scanning
        let scannedFiles = 0;
        let maliciousCount = 0;
        let suspiciousCount = 0;
        const scanInterval = setInterval(() => {
            // Increment scanned files
            const batchSize = Math.floor(Math.random() * 10) + 1;
            scannedFiles = Math.min(scannedFiles + batchSize, totalFiles);
            const percent = Math.floor((scannedFiles / totalFiles) * 100);
            
            // Update progress
            updateScanProgress({
                device_id: deviceId,
                total_files: totalFiles,
                scanned_files: scannedFiles,
                status: 'scanning',
                percent: percent
            });
            
            // Update current file
            updateCurrentFile(deviceId, `file_${scannedFiles}.txt`);
            
            // Randomly find malicious or suspicious files
            if (Math.random() < 0.05) { // 5% chance
                maliciousCount++;
                const fileName = `malicious_file_${maliciousCount}.exe`;
                const filePath = `/media/usb/${fileName}`;
                
                // Add to malicious files list
                addToFilesList(deviceId, filePath, 'malicious');
                
                // Show notification
                showNotification('Threat Detected!', `Malicious file found: ${fileName}`, 'danger');
            }
            
            if (Math.random() < 0.1) { // 10% chance
                suspiciousCount++;
                const fileName = `suspicious_file_${suspiciousCount}.dll`;
                const filePath = `/media/usb/${fileName}`;
                
                // Add to suspicious files list
                addToFilesList(deviceId, filePath, 'suspicious');
                
                // Show notification
                showNotification('Warning', `Suspicious file found: ${fileName}`, 'warning');
            }
            
            // Check if scan is complete
            if (scannedFiles >= totalFiles) {
                clearInterval(scanInterval);
                
                // Complete scan
                const scanDuration = (Math.random() * 3 + 2).toFixed(1);
                let result = 'success';
                let message = `Scan completed on ${deviceName} - `;
                
                if (maliciousCount > 0) {
                    result = 'danger';
                    message += `${maliciousCount} malicious files detected!`;
                } else if (suspiciousCount > 0) {
                    result = 'warning';
                    message += `${suspiciousCount} suspicious files detected`;
                } else {
                    message += "No threats detected";
                }
                
                completeScanProgress(deviceId, {
                    infected_files: maliciousCount,
                    suspicious_files: suspiciousCount,
                    scan_duration: scanDuration
                });
                
                // Show notification
                showNotification('Scan Complete', message, result === 'danger' ? 'danger' : (result === 'warning' ? 'warning' : 'success'));
                
                // Update scan status
                scanInProgress = false;
                currentScanDeviceId = null;
                
                // If we're on the scans page, refresh the scan history
                if (typeof loadScanHistory === 'function') {
                    setTimeout(loadScanHistory, 1000);
                }
                
                // If we're on the alerts page, refresh the alerts
                if (typeof loadAlerts === 'function') {
                    setTimeout(loadAlerts, 1000);
                }
                
                // Send email and SMS alerts if threats were found
                if (maliciousCount > 0 || suspiciousCount > 0) {
                    simulateSendAlerts(deviceName, maliciousCount, suspiciousCount);
                }
            }
        }, 200); // Update every 200ms
    }, 1000);
}

// Create or update scan progress container
function createScanProgressContainer(deviceId, deviceName) {
    // Check if container already exists
    let scanContainer = document.getElementById(`scan-progress-${deviceId}`);
    
    if (!scanContainer) {
        // Create new container
        scanContainer = document.createElement('div');
        scanContainer.id = `scan-progress-${deviceId}`;
        scanContainer.className = 'scan-progress-container terminal-window';
        
        // Create container content
        scanContainer.innerHTML = `
            <div class="terminal-header">
                <span>Real-time Scan: ${deviceName}</span>
                <button class="close-btn" onclick="closeScanProgress('${deviceId}')">×</button>
            </div>
            <div class="terminal-content">
                <div class="scan-status">Initializing scan...</div>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progress-bar-${deviceId}" style="width: 0%"></div>
                </div>
                <div class="scan-details">
                    <div class="scan-stats">
                        <span id="scanned-files-${deviceId}">0</span> / 
                        <span id="total-files-${deviceId}">0</span> files
                    </div>
                    <div class="scan-time" id="scan-time-${deviceId}">00:00</div>
                </div>
                <div class="current-file" id="current-file-${deviceId}">Preparing to scan...</div>
                <div class="files-found">
                    <div class="files-header">Detected Files:</div>
                    <div class="malicious-files" id="malicious-files-${deviceId}" style="display: none;">
                        <div class="files-subheader">Malicious Files (0):</div>
                        <ul class="file-list" id="malicious-files-list-${deviceId}"></ul>
                    </div>
                    <div class="suspicious-files" id="suspicious-files-${deviceId}" style="display: none;">
                        <div class="files-subheader">Suspicious Files (0):</div>
                        <ul class="file-list" id="suspicious-files-list-${deviceId}"></ul>
                    </div>
                </div>
            </div>
        `;
        
        // Add to page
        const notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            // Create container if it doesn't exist
            const container = document.createElement('div');
            container.id = 'notification-container';
            document.body.appendChild(container);
            container.appendChild(scanContainer);
        } else {
            notificationContainer.appendChild(scanContainer);
        }
        
        // Start scan timer
        startScanTimer(deviceId);
    }
}

// Update scan progress
function updateScanProgress(data) {
    const progressBar = document.getElementById(`progress-bar-${data.device_id}`);
    const scannedFiles = document.getElementById(`scanned-files-${data.device_id}`);
    const totalFiles = document.getElementById(`total-files-${data.device_id}`);
    const scanStatus = document.querySelector(`#scan-progress-${data.device_id} .scan-status`);
    
    if (progressBar && scannedFiles && totalFiles && scanStatus) {
        // Update progress bar
        progressBar.style.width = `${data.percent || 0}%`;
        
        // Update file counts
        scannedFiles.textContent = data.scanned_files || 0;
        totalFiles.textContent = data.total_files || 0;
        
        // Update status
        if (data.status === 'counting') {
            scanStatus.textContent = 'Counting files...';
        } else if (data.status === 'scanning') {
            scanStatus.textContent = 'Scanning files...';
        }
    }
}

// Update current file being scanned
function updateCurrentFile(deviceId, filePath) {
    const currentFile = document.getElementById(`current-file-${deviceId}`);
    
    if (currentFile) {
        currentFile.textContent = `Scanning: ${filePath}`;
        
        // Add typing animation
        currentFile.classList.remove('typing-animation');
        void currentFile.offsetWidth; // Trigger reflow
        currentFile.classList.add('typing-animation');
    }
}

// Add file to malicious or suspicious files list
function addToFilesList(deviceId, filePath, type) {
    const listId = type === 'malicious' ? 
        `malicious-files-list-${deviceId}` : 
        `suspicious-files-list-${deviceId}`;
    
    const headerId = type === 'malicious' ? 
        `malicious-files-${deviceId}` : 
        `suspicious-files-${deviceId}`;
    
    const list = document.getElementById(listId);
    const header = document.querySelector(`#${headerId} .files-subheader`);
    
    if (list && header) {
        // Create new list item
        const item = document.createElement('li');
        item.className = 'file-item typing-animation';
        item.textContent = filePath;
        
        // Add to list
        list.appendChild(item);
        
        // Update count in header
        const count = list.children.length;
        const typeText = type === 'malicious' ? 'Malicious' : 'Suspicious';
        header.textContent = `${typeText} Files (${count}):`;
        
        // Show the section
        document.getElementById(headerId).style.display = 'block';
    }
}

// Complete scan progress
function completeScanProgress(deviceId, data) {
    const progressBar = document.getElementById(`progress-bar-${deviceId}`);
    const scanStatus = document.querySelector(`#scan-progress-${data.device_id} .scan-status`);
    
    if (progressBar && scanStatus) {
        // Update progress bar to 100%
        progressBar.style.width = '100%';
        
        // Update status
        let statusText = 'Scan completed successfully!';
        let statusClass = 'status-success';
        
        if (data.infected_files > 0) {
            statusText = `Scan completed - ${data.infected_files} malicious files found!`;
            statusClass = 'status-danger';
        } else if (data.suspicious_files > 0) {
            statusText = `Scan completed - ${data.suspicious_files} suspicious files found`;
            statusClass = 'status-warning';
        }
        
        scanStatus.textContent = statusText;
        scanStatus.className = `scan-status ${statusClass}`;
        
        // Stop timer
        stopScanTimer(deviceId);
        
        // Add completion time
        const scanTime = document.getElementById(`scan-time-${deviceId}`);
        if (scanTime) {
            scanTime.textContent = `Total time: ${data.scan_duration}s`;
        }
    }
}

// Start scan timer
function startScanTimer(deviceId) {
    const scanTime = document.getElementById(`scan-time-${deviceId}`);
    if (!scanTime) return;
    
    let seconds = 0;
    const timerId = setInterval(() => {
        seconds++;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        scanTime.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }, 1000);
    
    // Store timer ID
    scanTimers[deviceId] = timerId;
}

// Stop scan timer
function stopScanTimer(deviceId) {
    if (scanTimers[deviceId]) {
        clearInterval(scanTimers[deviceId]);
        delete scanTimers[deviceId];
    }
}

// Close scan progress container
function closeScanProgress(deviceId) {
    const scanContainer = document.getElementById(`scan-progress-${deviceId}`);
    if (scanContainer) {
        // Stop timer
        stopScanTimer(deviceId);
        
        // Remove container with animation
        scanContainer.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            scanContainer.remove();
            
            // Reset scan status if this was the active scan
            if (currentScanDeviceId === deviceId) {
                scanInProgress = false;
                currentScanDeviceId = null;
            }
        }, 300);
    }
}

// Simulate sending email and SMS alerts
function simulateSendAlerts(deviceName, maliciousCount, suspiciousCount) {
    console.log(`Simulating sending alerts for ${deviceName}`);
    
    let alertType = maliciousCount > 0 ? 'Malicious' : 'Suspicious';
    let alertMessage = `${alertType} USB detected: ${deviceName} with `;
    
    if (maliciousCount > 0) {
        alertMessage += `${maliciousCount} malicious files`;
        if (suspiciousCount > 0) {
            alertMessage += ` and ${suspiciousCount} suspicious files`;
        }
    } else {
        alertMessage += `${suspiciousCount} suspicious files`;
    }
    
    // Show notification about alerts being sent
    showNotification('Alerts Sent', `Email and SMS alerts have been sent: ${alertMessage}`, 'info');
}

// Show notification if not already defined
if (typeof showNotification !== 'function') {
    function showNotification(title, message, type = 'success') {
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <div>
                    <div>${title}</div>
                    <div class="notification-message">${message}</div>
                </div>
            </div>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; cursor: pointer;">×</button>
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
        
        // Remove notification after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', initRealTimeScanner);
