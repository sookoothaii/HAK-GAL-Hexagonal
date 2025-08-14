// Debug Helper for HAK-GAL Frontend
// Paste this in the browser console to see what's happening

// Check store state
const store = window.useGovernorStore?.getState();
if (store) {
  console.log('=== STORE STATE ===');
  console.log('Connected:', store.isConnected);
  console.log('KB Metrics:', store.kb?.metrics);
  console.log('Categories:', store.kb?.categories);
  console.log('Full KB State:', store.kb);
  console.log('Full Store:', store);
} else {
  console.log('Store not found!');
}

// Check WebSocket
const ws = window.wsService;
if (ws) {
  console.log('=== WEBSOCKET ===');
  console.log('WebSocket Service exists');
  
  // Try to request data manually
  ws.emit('request_initial_data');
  console.log('Requested initial data...');
  
  // Also try specific KB request
  ws.emit('request_kb_metrics');
  console.log('Requested KB metrics...');
} else {
  console.log('WebSocket service not found!');
}
