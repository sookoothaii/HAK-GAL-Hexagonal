#!/usr/bin/env python3
"""
DNS Health Monitor for HAK_GAL
Überwacht DNS-Auflösung und warnt bei Problemen
"""

import socket
import time
import subprocess
import sys
from datetime import datetime

# Kritische Domains für HAK_GAL
CRITICAL_DOMAINS = [
    'api.anthropic.com',
    'api.groq.com', 
    'api.deepseek.com',
    'generativelanguage.googleapis.com',
    'o4509639807205376.ingest.de.sentry.io'
]

def test_dns(domain, timeout=5):
    """Test DNS resolution for a domain"""
    try:
        start = time.time()
        socket.setdefaulttimeout(timeout)
        ip = socket.gethostbyname(domain)
        elapsed = time.time() - start
        return True, ip, elapsed
    except Exception as e:
        return False, str(e), timeout

def fix_dns_windows():
    """Apply Windows DNS fixes"""
    fixes_applied = []
    
    # 1. Flush DNS
    try:
        subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
        fixes_applied.append("DNS cache flushed")
    except:
        pass
    
    # 2. Reset Winsock (requires admin)
    try:
        subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True)
        fixes_applied.append("Winsock reset")
    except:
        pass
    
    return fixes_applied

def monitor_loop():
    """Main monitoring loop"""
    print("="*60)
    print("HAK_GAL DNS HEALTH MONITOR")
    print("="*60)
    print(f"Monitoring {len(CRITICAL_DOMAINS)} critical domains")
    print("Press Ctrl+C to stop\n")
    
    failures = {}
    check_count = 0
    
    while True:
        check_count += 1
        print(f"\n[Check #{check_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*40)
        
        all_ok = True
        for domain in CRITICAL_DOMAINS:
            success, result, elapsed = test_dns(domain)
            
            if success:
                print(f"✓ {domain:<40} → {result:<15} ({elapsed:.2f}s)")
                # Clear failure count
                if domain in failures:
                    del failures[domain]
            else:
                all_ok = False
                failures[domain] = failures.get(domain, 0) + 1
                print(f"✗ {domain:<40} → FAILED ({result})")
                
                # If failed 3 times, try to fix
                if failures[domain] >= 3:
                    print(f"\n⚠️ {domain} failed {failures[domain]} times!")
                    print("Attempting automatic DNS fix...")
                    fixes = fix_dns_windows()
                    for fix in fixes:
                        print(f"  - {fix}")
                    failures[domain] = 0  # Reset counter
        
        if all_ok:
            print("\n✅ All DNS resolutions successful")
        else:
            print(f"\n⚠️ {len(failures)} domains failing")
            
        # Sleep before next check
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    try:
        # Set global timeout
        socket.setdefaulttimeout(10)
        monitor_loop()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
