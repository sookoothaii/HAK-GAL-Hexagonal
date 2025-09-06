// frontend/src/utils/consoleSuppressor.ts
// Minimaler Fix - Unterdrückt nervige Console-Fehler

export function suppressConsoleErrors() {
  if (typeof window === 'undefined') return;
  
  // Save original methods
  const originalError = console.error;
  const originalWarn = console.warn;
  
  // Patterns to suppress
  const suppressPatterns = [
    'WebSocket connection to',
    'WebSocket is closed before',
    'React Router Future Flag Warning',
    'Download the React DevTools',
    'Failed to load resource',
    'ERR_FAILED',
    'socket.io',
    'v7_startTransition',
    'v7_relativeSplatPath'
  ];
  
  // Override console.error
  console.error = (...args) => {
    const message = args.join(' ');
    const shouldSuppress = suppressPatterns.some(pattern => 
      message.includes(pattern)
    );
    
    if (!shouldSuppress) {
      originalError.apply(console, args);
    }
  };
  
  // Override console.warn
  console.warn = (...args) => {
    const message = args.join(' ');
    const shouldSuppress = suppressPatterns.some(pattern => 
      message.includes(pattern)
    );
    
    if (!shouldSuppress) {
      originalWarn.apply(console, args);
    }
  };
  
  // Limit WebSocket reconnection attempts
  if (window.io) {
    const originalIo = window.io;
    window.io = (url, options) => {
      return originalIo(url, {
        ...options,
        reconnectionAttempts: 3,  // Max 3 attempts instead of infinite
        reconnectionDelay: 2000,
        transports: ['polling'],  // Use polling instead of websocket
      });
    };
  }
}

// Auto-apply on import
suppressConsoleErrors();