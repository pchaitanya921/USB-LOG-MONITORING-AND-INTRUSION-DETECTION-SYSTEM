// Real-time USB Scanner with Socket.IO
let socket;
let scanInProgress = false;
let currentScanDeviceId = null;

// Initialize the real-time scanner
function initRealTimeScanner() {
    // Connect to Socket.IO server
    socket = io.connect(window.location.origin);
    
    // Set up event listeners
    setupSocketEvents();
    
    console.log('Real-time USB scanner initialized');
}

// Set up Socket.IO event listeners
function setupSocketEvents() {
    // Listen for scan started event
    socket.on('scan_started', function(data) {
        console.log('Scan started:', data);
        scanInProgress = true;
        currentScanDeviceId = data.device_id;
        
        // Show scan started notification
        showNotification('Scan Started', `Scanning ${data.device_name} for threats...`, 'info');
        
        // Create or update scan progress container
        createScanProgressContainer(data.device_id, data.device_name);
    });
    
    // Listen for scan progress updates
    socket.on('scan_progress', function(data) {
        console.log('Scan progress:', data);
        
        // Update progress bar
        updateScanProgress(data);
        
        // Update current file being scanned
        if (data.current_file) {
            updateCurrentFile(data.device_id, data.current_file);
        }
    });
    
    // Listen for malicious file found
    socket.on('malicious_file_found', function(data) {
        console.log('Malicious file found:', data);
        
        // Show malicious file notification
        showNotification('Threat Detected!', `Malicious file found: ${data.file_name}`, 'danger');
        
        // Add to malicious files list
        addToFilesList(data.device_id, data.file_path, 'malicious');
    });
    
    // Listen for suspicious file found
    socket.on('suspicious_file_found', function(data) {
        console.log('Suspicious file found:', data);
        
        // Show suspicious file notification
        showNotification('Warning', `Suspicious file found: ${data.file_name}`, 'warning');
        
        // Add to suspicious files list
        addToFilesList(data.device_id, data.file_path, 'suspicious');
    });
    
    // Listen for scan complete
    socket.on('scan_complete', function(data) {
        console.log('Scan complete:', data);
        scanInProgress = false;
        
        // Show scan complete notification
        let notificationType = 'success';
        if (data.infected_files > 0) {
            notificationType = 'danger';
        } else if (data.suspicious_files > 0) {
            notificationType = 'warning';
        }
        
        showNotification('Scan Complete', data.message, notificationType);
        
        // Update scan progress to 100%
        completeScanProgress(data.device_id, data);
        
        // Refresh device list after scan
        if (typeof loadConnectedDevices === 'function') {
            setTimeout(loadConnectedDevices, 1000);
        }
    });
    
    // Listen for scan errors
    socket.on('scan_error', function(data) {
        console.log('Scan error:', data);
        scanInProgress = false;
        
        // Show error notification
        showNotification('Scan Error', `Error scanning device: ${data.error}`, 'danger');
        
        // Update scan progress to show error
        updateScanProgressError(data.device_id, data.error);
    });
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
                    <div class="malicious-files" id="malicious-files-${deviceId}">
                        <div class="files-subheader">Malicious Files (0):</div>
                        <ul class="file-list" id="malicious-files-list-${deviceId}"></ul>
                    </div>
                    <div class="suspicious-files" id="suspicious-files-${deviceId}">
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
    const scanStatus = document.querySelector(`#scan-progress-${deviceId} .scan-status`);
    
    if (progressBar && scanStatus) {
        // Update progress bar to 100%
        progressBar.style.width = '100%';
        
        // Update status
        let statusText = 'Scan completed successfully!';
        let statusClass = 'success';
        
        if (data.infected_files > 0) {
            statusText = `Scan completed - ${data.infected_files} malicious files found!`;
            statusClass = 'danger';
        } else if (data.suspicious_files > 0) {
            statusText = `Scan completed - ${data.suspicious_files} suspicious files found`;
            statusClass = 'warning';
        }
        
        scanStatus.textContent = statusText;
        scanStatus.className = `scan-status status-${statusClass}`;
        
        // Stop timer
        stopScanTimer(deviceId);
        
        // Add completion time
        const scanTime = document.getElementById(`scan-time-${deviceId}`);
        if (scanTime) {
            scanTime.textContent = `Total time: ${data.scan_duration}s`;
        }
    }
}

// Update scan progress to show error
function updateScanProgressError(deviceId, errorMessage) {
    const scanStatus = document.querySelector(`#scan-progress-${deviceId} .scan-status`);
    const currentFile = document.getElementById(`current-file-${deviceId}`);
    
    if (scanStatus) {
        // Update status
        scanStatus.textContent = 'Scan failed!';
        scanStatus.className = 'scan-status status-danger';
    }
    
    if (currentFile) {
        currentFile.textContent = `Error: ${errorMessage}`;
        currentFile.className = 'current-file error';
    }
    
    // Stop timer
    stopScanTimer(deviceId);
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
    scanTime.dataset.timerId = timerId;
}

// Stop scan timer
function stopScanTimer(deviceId) {
    const scanTime = document.getElementById(`scan-time-${deviceId}`);
    if (!scanTime) return;
    
    const timerId = scanTime.dataset.timerId;
    if (timerId) {
        clearInterval(parseInt(timerId));
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
        }, 300);
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', initRealTimeScanner);
