"""
Eventlet Socket Fix for HAK_GAL
Prevents BrokenPipeError crashes
"""

import eventlet
import socket as _socket

# Patch eventlet to handle broken pipes gracefully
def patched_send_loop(original_send_loop):
    def wrapper(self, send_method, data, *args):
        try:
            return original_send_loop(self, send_method, data, *args)
        except (BrokenPipeError, ConnectionResetError, _socket.error) as e:
            # Silently ignore broken pipe errors
            if hasattr(e, 'errno'):
                if e.errno in (10053, 10054, 10058):  # Windows socket errors
                    return len(data)  # Pretend we sent it
            return 0
    return wrapper

# Apply patch
try:
    from eventlet.greenio import base
    original = base.GreenSocket._send_loop
    base.GreenSocket._send_loop = patched_send_loop(original)
    print("[EVENTLET PATCH] Applied BrokenPipe protection")
except Exception as e:
    print(f"[EVENTLET PATCH] Failed: {e}")
