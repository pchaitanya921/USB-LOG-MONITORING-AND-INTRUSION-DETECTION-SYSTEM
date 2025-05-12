// Termux-style Popup Notifications for USB Monitoring System

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Apply Termux styling to existing notifications
    applyTermuxStylingToNotifications();

    // Override the default notification system
    overrideNotificationSystem();

    // Create a MutationObserver to watch for new notifications
    createNotificationObserver();
});

// Apply Termux styling to existing notifications
function applyTermuxStylingToNotifications() {
    // Find all existing notifications
    const notifications = document.querySelectorAll('.notification');

    notifications.forEach(notification => {
        convertToTermuxNotification(notification);
    });
}

// Override the default notification system
function overrideNotificationSystem() {
    // Check if the showNotification function exists in the global scope
    if (window.showNotification) {
        // Store the original function
        const originalShowNotification = window.showNotification;

        // Override the function
        window.showNotification = function(message, type = 'info') {
            // Call the original function
            originalShowNotification(message, type);

            // Find the notification that was just created
            setTimeout(() => {
                const notifications = document.querySelectorAll('.notification:not(.termux-notification)');
                if (notifications.length > 0) {
                    const latestNotification = notifications[notifications.length - 1];
                    convertToTermuxNotification(latestNotification);
                }
            }, 10);
        };
    }

    // Override toast notifications if react-toastify is used
    if (window.toast) {
        // Add Termux styling to toast container
        const toastContainer = document.querySelector('.Toastify__toast-container');
        if (toastContainer) {
            toastContainer.style.fontFamily = "'Fira Code', monospace";
        }
    }
}

// Create a MutationObserver to watch for new notifications
function createNotificationObserver() {
    // Create a new observer
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Check each added node
                mutation.addedNodes.forEach((node) => {
                    // If it's a notification
                    if (node.nodeType === 1 && (
                        node.classList.contains('notification') ||
                        node.classList.contains('Toastify__toast') ||
                        node.classList.contains('popup-notification')
                    )) {
                        // Convert it to Termux style if it's not already
                        if (!node.classList.contains('termux-notification')) {
                            convertToTermuxNotification(node);
                        }
                    }
                });
            }
        });
    });

    // Start observing the document body
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Convert a notification to Termux style
function convertToTermuxNotification(notification) {
    // Skip if already converted
    if (notification.classList.contains('termux-notification')) {
        return;
    }

    // Add Termux class
    notification.classList.add('termux-notification');

    // Determine notification type
    let type = 'info';
    if (notification.classList.contains('notification-success') || notification.classList.contains('Toastify__toast--success')) {
        type = 'success';
        notification.classList.add('success');
    } else if (notification.classList.contains('notification-warning') || notification.classList.contains('Toastify__toast--warning')) {
        type = 'warning';
        notification.classList.add('warning');
    } else if (notification.classList.contains('notification-error') || notification.classList.contains('Toastify__toast--error')) {
        type = 'error';
        notification.classList.add('error');
    } else {
        notification.classList.add('info');
    }

    // Get the notification content
    let content = notification.textContent;

    // If it's a toast notification
    if (notification.classList.contains('Toastify__toast')) {
        // Get the toast body
        const toastBody = notification.querySelector('.Toastify__toast-body');
        if (toastBody) {
            content = toastBody.textContent;

            // Clear the toast body
            toastBody.innerHTML = '';

            // Create terminal-style content
            createTerminalContent(toastBody, content, type);
        }
    } else {
        // Clear the notification
        notification.innerHTML = '';

        // Create terminal-style content
        createTerminalContent(notification, content, type);
    }

    // Add binary background
    addBinaryBackground(notification);

    // Add scanning animation class if it's a scanning notification
    if (content.toLowerCase().includes('scan')) {
        notification.classList.add('scanning');
    }
}

// Create terminal-style content for a notification
function createTerminalContent(container, content, type) {
    // Create header
    const header = document.createElement('div');
    header.className = 'termux-notification-header';

    // Add timestamp
    const timestamp = document.createElement('span');
    timestamp.className = 'termux-notification-timestamp';
    timestamp.textContent = getCurrentTimestamp();
    header.appendChild(timestamp);

    // Add close button
    const closeButton = document.createElement('button');
    closeButton.className = 'termux-notification-close';
    closeButton.textContent = 'x';
    closeButton.addEventListener('click', () => {
        container.parentNode.classList.add('termux-notification-closing');
        setTimeout(() => {
            if (container.parentNode) {
                container.parentNode.remove();
            } else {
                container.remove();
            }
        }, 300);
    });
    header.appendChild(closeButton);

    // Add header to container
    container.appendChild(header);

    // Create content
    const contentElement = document.createElement('div');
    contentElement.className = 'termux-notification-content';

    // Add terminal prompt
    const prompt = document.createElement('span');
    prompt.className = 'termux-prompt';

    // Set prompt based on notification type
    switch (type) {
        case 'success':
            prompt.textContent = '[SUCCESS]';
            break;
        case 'warning':
            prompt.textContent = '[WARNING]';
            break;
        case 'error':
            prompt.textContent = '[ERROR]';
            break;
        default:
            prompt.textContent = '[INFO]';
    }

    contentElement.appendChild(prompt);

    // Add message
    const message = document.createTextNode(content);
    contentElement.appendChild(message);

    // Add blinking cursor
    const cursor = document.createElement('span');
    cursor.className = 'termux-cursor';
    contentElement.appendChild(cursor);

    // Add content to container
    container.appendChild(contentElement);
}

// Add binary background to a notification
function addBinaryBackground(notification) {
    // Create binary background
    const binaryBackground = document.createElement('div');
    binaryBackground.className = 'termux-notification-binary';

    // Add binary digits
    for (let i = 0; i < 20; i++) {
        const digit = document.createElement('div');
        digit.className = 'binary-digit';
        digit.textContent = Math.random() > 0.5 ? '1' : '0';

        // Random position
        digit.style.left = `${Math.random() * 100}%`;
        digit.style.top = `${Math.random() * 100}%`;

        // Random animation duration
        const duration = 2 + Math.random() * 3;
        digit.style.animationDuration = `${duration}s`;

        // Random animation delay
        const delay = Math.random() * 2;
        digit.style.animationDelay = `${delay}s`;

        binaryBackground.appendChild(digit);
    }

    // Add binary background to notification
    notification.appendChild(binaryBackground);
}

// Get current timestamp in terminal format
function getCurrentTimestamp() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `[${hours}:${minutes}:${seconds}]`;
}

// Override the default toast notifications
function overrideToastNotifications() {
    // Check if toast is available (react-toastify)
    if (typeof toast !== 'undefined') {
        // Store original toast functions
        const originalToast = toast;
        const originalSuccess = toast.success;
        const originalError = toast.error;
        const originalInfo = toast.info;
        const originalWarning = toast.warning;

        // Override toast functions - removed [~]$ prefix
        toast = function(message, options) {
            return originalToast(`${message}`, options);
        };

        toast.success = function(message, options) {
            return originalSuccess(`[SUCCESS] ${message}`, options);
        };

        toast.error = function(message, options) {
            return originalError(`[ERROR] ${message}`, options);
        };

        toast.info = function(message, options) {
            return originalInfo(`[INFO] ${message}`, options);
        };

        toast.warning = function(message, options) {
            return originalWarning(`[WARNING] ${message}`, options);
        };
    }
}

// Call this function when the page loads
overrideToastNotifications();
