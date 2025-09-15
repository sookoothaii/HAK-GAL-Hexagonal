#!/usr/bin/env python3
"""
PRODUCTION SERVER - Verwendet Gunicorn statt Flask Dev Server
"""

import subprocess
import sys
import os

def install_gunicorn():
    """Installiere Gunicorn falls nicht vorhanden"""
    try:
        import gunicorn
        print("✅ Gunicorn bereits installiert")
    except ImportError:
        print("📦 Installiere Gunicorn...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])
        print("✅ Gunicorn installiert")

def start_production_server():
    """Starte Production Server mit Gunicorn"""
    print("🚀 Starting Production Server with Gunicorn")
    print("=" * 50)
    
    # Installiere Gunicorn
    install_gunicorn()
    
    # Gunicorn-Konfiguration
    cmd = [
        "gunicorn",
        "--bind", "127.0.0.1:5000",
        "--workers", "4",
        "--threads", "2",
        "--worker-class", "sync",
        "--worker-connections", "1000",
        "--timeout", "30",
        "--keep-alive", "2",
        "--max-requests", "1000",
        "--max-requests-jitter", "100",
        "--preload",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "hakgal_dashboard_ultra:app"
    ]
    
    print("🔧 Gunicorn Configuration:")
    print(f"  Workers: 4")
    print(f"  Threads: 2")
    print(f"  Timeout: 30s")
    print(f"  Keep-Alive: 2s")
    print(f"  Max Requests: 1000")
    print("=" * 50)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    start_production_server()
