/**
 * Network Animation Initializer
 * Creates an ethical hacking-themed background with network nodes and scanning effects
 */

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create background container if it doesn't exist
    let backgroundContainer = document.querySelector('.background-animation');
    if (!backgroundContainer) {
        backgroundContainer = document.createElement('div');
        backgroundContainer.className = 'background-animation';
        document.body.appendChild(backgroundContainer);
    }

    // Create network nodes
    createNetworkNodes(backgroundContainer);

    // Create scanning lines
    createScanningLines(backgroundContainer);
});

/**
 * Create network nodes and connections with dynamic movement
 */
function createNetworkNodes(container) {
    // Create nodes container
    const nodesContainer = document.createElement('div');
    nodesContainer.className = 'network-nodes';
    container.appendChild(nodesContainer);

    // Number of nodes (reduced for better performance)
    const nodeCount = 15;
    const nodes = [];

    // Create nodes
    for (let i = 0; i < nodeCount; i++) {
        const node = document.createElement('div');
        const nodeType = Math.floor(Math.random() * 3) + 1;
        node.className = `node node-${nodeType}`;

        // Set node index for connection tracking
        node.dataset.index = i.toString();

        // Random position
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        node.style.left = `${x}%`;
        node.style.top = `${y}%`;

        // Random animation delays for pulse and movement
        node.style.animationDelay = `${Math.random() * 3}s, ${Math.random() * 5}s`;

        // Random animation durations for movement (between 20-40s)
        const moveDuration = 20 + Math.random() * 20;
        node.style.animationDuration = `3s, ${moveDuration}s`;

        // Add custom movement path using CSS variables
        // This creates unique movement patterns for each node
        const moveX1 = (Math.random() * 40 - 20); // -20px to +20px
        const moveY1 = (Math.random() * 30 - 15); // -15px to +15px
        const moveX2 = (Math.random() * 40 - 20);
        const moveY2 = (Math.random() * 30 - 15);
        const moveX3 = (Math.random() * 40 - 20);
        const moveY3 = (Math.random() * 30 - 15);

        node.style.setProperty('--move-x1', `${moveX1}px`);
        node.style.setProperty('--move-y1', `${moveY1}px`);
        node.style.setProperty('--move-x2', `${moveX2}px`);
        node.style.setProperty('--move-y2', `${moveY2}px`);
        node.style.setProperty('--move-x3', `${moveX3}px`);
        node.style.setProperty('--move-y3', `${moveY3}px`);

        nodesContainer.appendChild(node);
        nodes.push({
            element: node,
            x: x,
            y: y,
            index: i
        });
    }

    // Create connections between nodes
    for (let i = 0; i < nodes.length; i++) {
        const sourceNode = nodes[i];

        // Connect to 1-3 other nodes
        const connectionCount = Math.floor(Math.random() * 3) + 1;

        for (let j = 0; j < connectionCount; j++) {
            // Find a target node (not the same as source)
            const targetIndex = Math.floor(Math.random() * nodes.length);
            if (targetIndex !== i) {
                const targetNode = nodes[targetIndex];
                createConnection(nodesContainer, sourceNode, targetNode);
            }
        }
    }

    // Update connections periodically to follow node movements
    setInterval(() => {
        updateConnections(nodesContainer, nodes);
    }, 1000); // Update every second
}

/**
 * Create a connection line between two nodes
 */
function createConnection(container, sourceNode, targetNode) {
    const connection = document.createElement('div');
    connection.className = 'connection';
    connection.dataset.sourceIndex = sourceNode.element.dataset.index;
    connection.dataset.targetIndex = targetNode.element.dataset.index;

    // Calculate position and dimensions
    const x1 = sourceNode.x;
    const y1 = sourceNode.y;
    const x2 = targetNode.x;
    const y2 = targetNode.y;

    // Calculate distance and angle
    const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;

    // Set position and dimensions
    connection.style.width = `${distance}%`;
    connection.style.left = `${x1}%`;
    connection.style.top = `${y1}%`;
    connection.style.transform = `rotate(${angle}deg)`;

    container.appendChild(connection);

    return connection;
}

/**
 * Update connections between nodes as they move
 */
function updateConnections(container, nodes) {
    // Get all connections
    const connections = container.querySelectorAll('.connection');

    // Update each connection
    connections.forEach(connection => {
        // Get source and target nodes
        const sourceIndex = parseInt(connection.dataset.sourceIndex);
        const targetIndex = parseInt(connection.dataset.targetIndex);

        if (isNaN(sourceIndex) || isNaN(targetIndex) ||
            sourceIndex >= nodes.length || targetIndex >= nodes.length) {
            return;
        }

        const sourceNode = nodes[sourceIndex];
        const targetNode = nodes[targetIndex];

        // Get current positions from the DOM (to account for CSS animations)
        const sourceRect = sourceNode.element.getBoundingClientRect();
        const targetRect = targetNode.element.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();

        // Calculate relative positions within the container (as percentages)
        const x1 = (sourceRect.left + sourceRect.width/2 - containerRect.left) / containerRect.width * 100;
        const y1 = (sourceRect.top + sourceRect.height/2 - containerRect.top) / containerRect.height * 100;
        const x2 = (targetRect.left + targetRect.width/2 - containerRect.left) / containerRect.width * 100;
        const y2 = (targetRect.top + targetRect.height/2 - containerRect.top) / containerRect.height * 100;

        // Calculate new distance and angle
        const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;

        // Update position and dimensions
        connection.style.width = `${distance}%`;
        connection.style.left = `${x1}%`;
        connection.style.top = `${y1}%`;
        connection.style.transform = `rotate(${angle}deg)`;
    });
}

/**
 * Create scanning lines effect (horizontal only)
 */
function createScanningLines(container) {
    // Create horizontal scan lines
    for (let i = 0; i < 5; i++) {
        const scanLine = document.createElement('div');
        scanLine.className = 'scan-line';
        scanLine.style.top = `${Math.random() * 100}%`;
        scanLine.style.animationDelay = `${Math.random() * 5}s`;
        container.appendChild(scanLine);
    }
}
