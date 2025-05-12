// Notification Worker for USB Security Monitor
// This worker handles background notifications when the main page is not in focus

self.addEventListener('install', (event) => {
  console.log('Notification Worker installed');
});

self.addEventListener('activate', (event) => {
  console.log('Notification Worker activated');
});

// Listen for messages from the main page
self.addEventListener('message', (event) => {
  const data = event.data;
  
  if (data.action === 'notify') {
    // Send a notification
    self.registration.showNotification(data.title, {
      body: data.message,
      icon: data.icon || '/favicon.ico',
      badge: data.badge || '/favicon.ico',
      tag: data.tag || 'usb-security-alert',
      requireInteraction: data.requireInteraction || false,
      actions: data.actions || [],
      data: data.data || {}
    });
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  // Focus on the main window or open it if closed
  event.waitUntil(
    clients.matchAll({type: 'window'}).then((clientList) => {
      for (const client of clientList) {
        if (client.url === '/' && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow('/');
      }
    })
  );
});
