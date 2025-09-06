/**
 * Simplified WebSocket Fix
 * Just prevents multiple status force calls
 */

// Prevent multiple status force calls
let statusForced = false;

if (typeof window !== 'undefined') {
  // Reset status forced flag periodically
  setInterval(() => { 
    statusForced = false; 
  }, 10000);
}

export function preventDuplicateStatusForce() {
  if (statusForced) {
    console.log('[WebSocketFix] Status already forced, skipping');
    return true;
  }
  statusForced = true;
  return false;
}

export default {
  preventDuplicateStatusForce
};
