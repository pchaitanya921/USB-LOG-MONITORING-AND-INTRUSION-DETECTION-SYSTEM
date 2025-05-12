// This script will override the scan popup to always show "No threats detected"
document.addEventListener('DOMContentLoaded', () => {
    // Override the simulateRealTimeScan function to never show malicious files
    window.simulateRealTimeScan = function(deviceId, deviceName) {
        console.log(`Starting real-time scan for device ${deviceId}: ${deviceName}`);

        showNotification('Real-time Scan', `Starting real-time scan for ${deviceName}...`, 'info');
        
        // Create a clean scan popup
        createCleanScanPopup(deviceId, deviceName);
        
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

                // Check if scan is complete
                if (scannedFiles >= totalFiles) {
                    clearInterval(scanInterval);

                    // Complete scan with no threats
                    const scanDuration = (Math.random() * 3 + 2).toFixed(1);
                    completeScanProgress(deviceId, {
                        infected_files: 0,
                        suspicious_files: 0,
                        scan_duration: scanDuration
                    });

                    // Show notification
                    showNotification('Scan Complete', `Scan completed on ${deviceName} - No threats detected`, 'success');
                }
            }, 200); // Update every 200ms
        }, 1000);
    };

    // Create a clean scan popup with no threats
    function createCleanScanPopup(deviceId, deviceName) {
        // Check if container already exists
        let scanContainer = document.getElementById(`scan-progress-${deviceId}`);

        if (!scanContainer) {
            // Create new container
            scanContainer = document.createElement('div');
            scanContainer.id = `scan-progress-${deviceId}`;
            scanContainer.className = 'scan-progress-container terminal-window';

            // Create container content with no threats
            scanContainer.innerHTML = `
                <div class="terminal-header">
                    <span>REAL-TIME SCAN: ${deviceName.toUpperCase()}</span>
                    <span class="close-popup" onclick="closeScanProgress('${deviceId}')">&times;</span>
                </div>
                <div class="scan-progress-container">
                    <div class="scan-progress-bar" id="scan-progress-${deviceId}"></div>
                </div>
                <div class="scan-status" id="scan-status-${deviceId}">
                    Initializing scan...
                </div>
                <div class="scan-details">
                    <span id="scan-files-${deviceId}">0 / 0 files</span>
                    <span id="scan-time-${deviceId}">00:00</span>
                </div>
                <div class="scan-message">Preparing to scan...</div>
                <div class="detected-files-container">
                    <h4>Detected Files:</h4>
                    <div class="detected-files-section">
                        <h5>Malicious Files (0):</h5>
                        <div class="file-list" id="malicious-files-${deviceId}">
                            <div class="no-files">No malicious files detected</div>
                        </div>
                    </div>
                    <div class="detected-files-section">
                        <h5>Suspicious Files (0):</h5>
                        <div class="file-list" id="suspicious-files-${deviceId}">
                            <div class="no-files">No suspicious files detected</div>
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
});
