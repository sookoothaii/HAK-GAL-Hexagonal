"""
FIX für 2-Sekunden-Verzögerung in der API
"""

import requests
import time

print("TEST: API ohne Eventlet direkt")
print("=" * 60)

# Direkter Test ohne Eventlet-Probleme
def direct_test():
    # Test 10 schnelle Requests
    times = []
    for i in range(10):
        start = time.time()
        try:
            r = requests.get("http://localhost:5002/health", timeout=0.5)
            duration = time.time() - start
            times.append(duration)
            print(f"  Request {i+1}: {duration*1000:.1f}ms")
        except requests.Timeout:
            print(f"  Request {i+1}: TIMEOUT")
        except Exception as e:
            print(f"  Request {i+1}: ERROR - {e}")
    
    if times:
        avg = sum(times) / len(times)
        print(f"\nDurchschnitt: {avg*1000:.1f}ms")
        print(f"Performance: {1/avg:.1f} req/s")

direct_test()

print("\n" + "=" * 60)
print("LÖSUNG: Eventlet-Konfiguration in hexagonal_api_enhanced_clean.py ändern!")
print("Ändern Sie Zeile 17 von:")
print("  eventlet.monkey_patch(thread=True, time=True, socket=False, select=False)")
print("Zu:")
print("  eventlet.monkey_patch()")  # Patch alles, nicht selective
print("=" * 60)
