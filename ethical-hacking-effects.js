// Ethical Hacking Effects for USB Monitoring System

// Apply Termux-style to buttons when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Apply styles to scan buttons
    applyTermuxStyle();
    
    // Create binary rain effect
    createBinaryRain();
    
    // Add event listeners for scan animations
    addScanAnimationListeners();
});

// Apply Termux-style to buttons
function applyTermuxStyle() {
    // Apply to Scan All Devices button
    const scanAllDevicesBtn = document.getElementById('scan-all-devices');
    if (scanAllDevicesBtn) {
        scanAllDevicesBtn.classList.add('termux-button');
        scanAllDevicesBtn.innerHTML = '<span class="terminal-text">[~]$ ./scan_all_devices</span>';
    }
    
    // Apply to Refresh Devices button
    const refreshDevicesBtn = document.getElementById('refresh-devices');
    if (refreshDevicesBtn) {
        refreshDevicesBtn.classList.add('termux-button');
        refreshDevicesBtn.innerHTML = '<span class="terminal-text">[~]$ ./refresh_devices</span>';
    }
    
    // Apply to individual Scan buttons
    const scanButtons = document.querySelectorAll('.scan-button');
    scanButtons.forEach(button => {
        button.classList.add('termux-button');
        button.innerHTML = '<span class="terminal-text">[~]$ ./scan</span>';
    });
}

// Create binary rain effect
function createBinaryRain() {
    // Create binary rain container
    const binaryRainContainer = document.createElement('div');
    binaryRainContainer.className = 'binary-rain';
    document.body.appendChild(binaryRainContainer);
    
    // Generate binary digits
    for (let i = 0; i < 50; i++) {
        createBinaryDigit(binaryRainContainer);
    }
}

// Create a single binary digit for the rain effect
function createBinaryDigit(container) {
    const digit = document.createElement('div');
    digit.className = 'binary-digit';
    digit.textContent = Math.random() > 0.5 ? '1' : '0';
    
    // Random position and animation duration
    const left = Math.random() * 100;
    const animationDuration = 3 + Math.random() * 5;
    const delay = Math.random() * 5;
    
    digit.style.left = `${left}%`;
    digit.style.animationDuration = `${animationDuration}s`;
    digit.style.animationDelay = `${delay}s`;
    
    container.appendChild(digit);
    
    // Remove and recreate digit after animation completes
    setTimeout(() => {
        digit.remove();
        createBinaryDigit(container);
    }, (animationDuration + delay) * 1000);
}

// Add event listeners for scan animations
function addScanAnimationListeners() {
    // Scan All Devices button
    const scanAllDevicesBtn = document.getElementById('scan-all-devices');
    if (scanAllDevicesBtn) {
        scanAllDevicesBtn.addEventListener('click', function() {
            // Show ethical hacking notification
            showEthicalHackingNotification('Initiating system-wide scan...', 'info');
            
            // Add scanning animation to device cards
            const deviceCards = document.querySelectorAll('.device-item');
            deviceCards.forEach(card => {
                card.classList.add('ethical-scan-animation');
                
                // Add scanning progress indicator
                const progressBar = document.createElement('div');
                progressBar.className = 'scanning-progress';
                card.appendChild(progressBar);
                
                // Remove animation after scan completes
                setTimeout(() => {
                    card.classList.remove('ethical-scan-animation');
                    progressBar.remove();
                }, 3000);
            });
        });
    }
    
    // Individual Scan buttons
    const scanButtons = document.querySelectorAll('.scan-button');
    scanButtons.forEach(button => {
        button.addEventListener('click', function() {
            const deviceId = this.getAttribute('data-device-id');
            const deviceCard = this.closest('.device-item');
            
            if (deviceCard) {
                // Show ethical hacking notification
                showEthicalHackingNotification(`Scanning device ${deviceId}...`, 'info');
                
                // Add scanning animation
                deviceCard.classList.add('ethical-scan-animation');
                
                // Add scanning progress indicator
                const progressBar = document.createElement('div');
                progressBar.className = 'scanning-progress';
                deviceCard.appendChild(progressBar);
                
                // Remove animation after scan completes
                setTimeout(() => {
                    deviceCard.classList.remove('ethical-scan-animation');
                    progressBar.remove();
                }, 3000);
            }
        });
    });
    
    // Refresh Devices button
    const refreshDevicesBtn = document.getElementById('refresh-devices');
    if (refreshDevicesBtn) {
        refreshDevicesBtn.addEventListener('click', function() {
            showEthicalHackingNotification('Refreshing device list...', 'info');
        });
    }
}

// Show ethical hacking style notification
function showEthicalHackingNotification(message, type) {
    // Check if notification container exists
    let notificationContainer = document.querySelector('.notification-container');
    
    // Create container if it doesn't exist
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = 'notification ethical-hacking';
    
    // Terminal-style prefix
    const prefix = type === 'error' ? '[ERROR]' : 
                  type === 'warning' ? '[WARNING]' : 
                  type === 'success' ? '[SUCCESS]' : '[INFO]';
    
    notification.innerHTML = `<span class="terminal-text">${prefix} ${message}</span>`;
    
    // Style notification
    notification.style.padding = '10px 15px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '4px';
    notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    notification.style.transition = 'all 0.3s ease';
    notification.style.opacity = '0';
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Remove after delay
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Periodically check for new buttons to apply styles
setInterval(() => {
    // Check for new scan buttons
    const unstyledScanButtons = document.querySelectorAll('.scan-button:not(.termux-button)');
    unstyledScanButtons.forEach(button => {
        button.classList.add('termux-button');
        button.innerHTML = '<span class="terminal-text">[~]$ ./scan</span>';
        
        // Add click event listener
        button.addEventListener('click', function() {
            const deviceId = this.getAttribute('data-device-id');
            const deviceCard = this.closest('.device-item');
            
            if (deviceCard) {
                // Show ethical hacking notification
                showEthicalHackingNotification(`Scanning device ${deviceId}...`, 'info');
                
                // Add scanning animation
                deviceCard.classList.add('ethical-scan-animation');
                
                // Add scanning progress indicator
                const progressBar = document.createElement('div');
                progressBar.className = 'scanning-progress';
                deviceCard.appendChild(progressBar);
                
                // Remove animation after scan completes
                setTimeout(() => {
                    deviceCard.classList.remove('ethical-scan-animation');
                    progressBar.remove();
                }, 3000);
            }
        });
    });
}, 1000);
