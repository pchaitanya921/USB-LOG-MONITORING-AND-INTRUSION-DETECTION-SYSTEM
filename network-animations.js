// Network Animations for USB Monitoring System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize network animations
    createNetworkBackground();
    createNetworkNodes();
    createNetworkConnections();
    createDataPackets();
    
    // Apply to all pages
    applyBackgroundToAllPages();
});

// Create Network Background
function createNetworkBackground() {
    const networkBackground = document.createElement('div');
    networkBackground.className = 'network-background';
    networkBackground.id = 'network-background';
    document.body.appendChild(networkBackground);
}

// Create Network Nodes
function createNetworkNodes() {
    const networkBackground = document.getElementById('network-background');
    
    // Create nodes
    for (let i = 0; i < 15; i++) {
        const node = document.createElement('div');
        node.className = 'network-node';
        
        // Random position
        node.style.left = `${Math.random() * 100}%`;
        node.style.top = `${Math.random() * 100}%`;
        
        // Random size
        const size = 4 + Math.random() * 8;
        node.style.width = `${size}px`;
        node.style.height = `${size}px`;
        
        // Random pulse animation
        const animationDuration = 2 + Math.random() * 3;
        node.style.animationDuration = `${animationDuration}s`;
        
        networkBackground.appendChild(node);
    }
}

// Create Network Connections
function createNetworkConnections() {
    const networkBackground = document.getElementById('network-background');
    const nodes = document.querySelectorAll('.network-node');
    
    // Create connections between nodes
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            // Only create connections between some nodes
            if (Math.random() > 0.7) {
                const connection = document.createElement('div');
                connection.className = 'network-connection';
                
                // Position and size will be updated in updateNetworkConnections
                networkBackground.appendChild(connection);
                
                // Store the nodes this connection links
                connection.setAttribute('data-from', i);
                connection.setAttribute('data-to', j);
            }
        }
    }
    
    // Initial update of connections
    updateNetworkConnections();
    
    // Update connections periodically
    setInterval(updateNetworkConnections, 100);
}

// Update Network Connections
function updateNetworkConnections() {
    const nodes = document.querySelectorAll('.network-node');
    const connections = document.querySelectorAll('.network-connection');
    
    connections.forEach(connection => {
        const fromIndex = parseInt(connection.getAttribute('data-from'));
        const toIndex = parseInt(connection.getAttribute('data-to'));
        
        if (fromIndex < nodes.length && toIndex < nodes.length) {
            const fromNode = nodes[fromIndex];
            const toNode = nodes[toIndex];
            
            // Get positions
            const fromRect = fromNode.getBoundingClientRect();
            const toRect = toNode.getBoundingClientRect();
            
            const fromX = fromRect.left + fromRect.width / 2;
            const fromY = fromRect.top + fromRect.height / 2;
            const toX = toRect.left + toRect.width / 2;
            const toY = toRect.top + toRect.height / 2;
            
            // Calculate distance and angle
            const dx = toX - fromX;
            const dy = toY - fromY;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const angle = Math.atan2(dy, dx) * 180 / Math.PI;
            
            // Position the connection
            connection.style.width = `${distance}px`;
            connection.style.left = `${fromX}px`;
            connection.style.top = `${fromY}px`;
            connection.style.transform = `rotate(${angle}deg)`;
            
            // Adjust opacity based on distance
            const opacity = Math.max(0.1, 1 - distance / 1000);
            connection.style.opacity = opacity;
        }
    });
}

// Create Data Packets
function createDataPackets() {
    const networkBackground = document.getElementById('network-background');
    const connections = document.querySelectorAll('.network-connection');
    
    // Create data packets that travel along connections
    setInterval(() => {
        // Only create a packet sometimes
        if (Math.random() > 0.7 && connections.length > 0) {
            // Choose a random connection
            const connection = connections[Math.floor(Math.random() * connections.length)];
            
            const packet = document.createElement('div');
            packet.className = 'data-packet';
            
            // Random color (green, blue, or cyan)
            const colors = ['#0f0', '#0ff', '#00f'];
            packet.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            
            // Position at start of connection
            const fromIndex = parseInt(connection.getAttribute('data-from'));
            const nodes = document.querySelectorAll('.network-node');
            const fromNode = nodes[fromIndex];
            const fromRect = fromNode.getBoundingClientRect();
            
            packet.style.left = `${fromRect.left + fromRect.width / 2}px`;
            packet.style.top = `${fromRect.top + fromRect.height / 2}px`;
            
            // Add to background
            networkBackground.appendChild(packet);
            
            // Animate along connection
            const toIndex = parseInt(connection.getAttribute('data-to'));
            const toNode = nodes[toIndex];
            const toRect = toNode.getBoundingClientRect();
            
            const duration = 0.5 + Math.random() * 1.5;
            packet.style.transition = `all ${duration}s linear`;
            
            // Start animation after a small delay
            setTimeout(() => {
                packet.style.left = `${toRect.left + toRect.width / 2}px`;
                packet.style.top = `${toRect.top + toRect.height / 2}px`;
                
                // Remove after animation completes
                setTimeout(() => {
                    packet.remove();
                }, duration * 1000);
            }, 10);
        }
    }, 300);
}

// Apply background to all pages
function applyBackgroundToAllPages() {
    // Check if we're on a page that needs the background
    const pages = ['index.html', 'dashboard.html', 'devices.html', 'scans.html', 'alerts.html', 'settings.html'];
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    if (pages.includes(currentPage) || currentPage === '') {
        // Add the background animations
        document.body.classList.add('with-network-background');
        
        // Make sure the binary rain is visible
        const existingBinaryRain = document.querySelector('.binary-rain');
        if (existingBinaryRain) {
            existingBinaryRain.style.opacity = '0.3';
        }
        
        // Make sure the matrix background is visible
        const existingMatrix = document.querySelector('.matrix-background');
        if (existingMatrix) {
            existingMatrix.style.opacity = '0.2';
        }
    }
}

// Handle window resize
window.addEventListener('resize', () => {
    // Update network connections when window is resized
    updateNetworkConnections();
});
