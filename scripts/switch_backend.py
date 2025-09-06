#!/usr/bin/env python3
"""
Switch Backend Script - Wechselt zwischen Port 5001 (Python) und 5002 (C++ Mojo)
Nach HAK/GAL Artikel 4: Bewusstes Grenzüberschreiten
"""

import os
import sys
import subprocess
from pathlib import Path

def update_caddyfile(port: int):
    """Aktualisiert die Caddyfile für den gewünschten Backend-Port"""
    
    caddyfile_path = Path("Caddyfile")
    
    if port == 5001:
        # Python Backend
        config = """{
    admin off
}

:8088 {
  # API + Health → 5001 (Python Backend)
  @api path /api/* /health
  reverse_proxy @api 127.0.0.1:5001

  # WebSocket → 5001 (Python Backend)
  @ws path /socket.io* /ws*
  reverse_proxy @ws 127.0.0.1:5001

  # Frontend (Vite)
  @vite_client path /@vite/client
  header @vite_client Content-Type application/javascript
  reverse_proxy @vite_client 127.0.0.1:5173

  @vite_assets path /@vite/* /src/* /node_modules/* /*.js
  header @vite_assets Content-Type application/javascript
  reverse_proxy @vite_assets 127.0.0.1:5173

  # Fallback
  reverse_proxy 127.0.0.1:5173
}"""
        backend_name = "Python (Standard)"
        
    elif port == 5002:
        # C++ Mojo Backend
        config = """{
    admin off
}

:8088 {
  # API + Health → 5002 (C++ Mojo Backend)
  @api path /api/* /health
  reverse_proxy @api 127.0.0.1:5002

  # WebSocket → 5002 (C++ Mojo Backend)
  @ws path /socket.io* /ws*
  reverse_proxy @ws 127.0.0.1:5002

  # Frontend (Vite)
  @vite_client path /@vite/client
  header @vite_client Content-Type application/javascript
  reverse_proxy @vite_client 127.0.0.1:5173

  @vite_assets path /@vite/* /src/* /node_modules/* /*.js
  header @vite_assets Content-Type application/javascript
  reverse_proxy @vite_assets 127.0.0.1:5173

  # Fallback
  reverse_proxy 127.0.0.1:5173
}"""
        backend_name = "C++ Mojo (Performance)"
    else:
        print(f"❌ Ungültiger Port: {port}")
        return False
    
    # Backup erstellen
    if caddyfile_path.exists():
        backup_path = Path(f"Caddyfile.backup_{port}")
        caddyfile_path.rename(backup_path)
        print(f"✅ Backup erstellt: {backup_path}")
    
    # Neue Config schreiben
    with open(caddyfile_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Caddyfile aktualisiert für Port {port} ({backend_name})")
    return True

def kill_process_on_port(port: int):
    """Beendet Prozess auf einem Port"""
    try:
        # Windows: netstat und taskkill
        result = subprocess.run(
            f'for /f "tokens=5" %a in (\'netstat -aon ^| find ":{port}" ^| find "LISTENING"\') do taskkill /F /PID %a',
            shell=True,
            capture_output=True
        )
        print(f"✅ Prozess auf Port {port} beendet (falls vorhanden)")
    except:
        pass

def start_backend(port: int):
    """Startet das gewünschte Backend"""
    
    if port == 5001:
        # Python Backend starten
        print("\n🐍 Starte Python Backend auf Port 5001...")
        cmd = [
            sys.executable,
            "src_hexagonal/hexagonal_api_enhanced.py"
        ]
        
    elif port == 5002:
        # C++ Mojo Backend starten
        print("\n⚡ Starte C++ Mojo Backend auf Port 5002...")
        
        # Check if compiled module exists
        mojo_module = Path("native/mojo_kernels/build/Release/mojo_kernels.cp311-win_amd64.pyd")
        if not mojo_module.exists():
            print(f"❌ C++ Mojo Module nicht gefunden: {mojo_module}")
            print("   Bitte erst kompilieren mit: cd native/mojo_kernels && build.bat")
            return False
        
        cmd = [
            sys.executable,
            "launch_5002_REAL_MOJO.py"
        ]
    else:
        return False
    
    # Starte in neuem Fenster
    if sys.platform == "win32":
        subprocess.Popen(
            ["start", "cmd", "/k"] + cmd,
            shell=True
        )
    else:
        subprocess.Popen(cmd)
    
    return True

def restart_caddy():
    """Neustart Caddy Proxy"""
    print("\n🔄 Restarte Caddy Proxy...")
    
    # Kill existing Caddy
    kill_process_on_port(8088)
    
    # Start Caddy
    if sys.platform == "win32":
        subprocess.Popen(
            ["start", "cmd", "/k", "caddy", "run"],
            shell=True
        )
    else:
        subprocess.Popen(["caddy", "run"])
    
    print("✅ Caddy Proxy neugestartet auf Port 8088")

def main():
    print("=" * 60)
    print("HAK-GAL BACKEND SWITCHER")
    print("Wechselt zwischen Python (5001) und C++ Mojo (5002)")
    print("=" * 60)
    
    print("\nWählen Sie das Backend:")
    print("1. Python Backend (Port 5001) - Standard, vollständige Features")
    print("2. C++ Mojo Backend (Port 5002) - Performance-optimiert")
    print("0. Abbrechen")
    
    choice = input("\nIhre Wahl [1/2/0]: ").strip()
    
    if choice == "1":
        port = 5001
        backend = "Python"
    elif choice == "2":
        port = 5002
        backend = "C++ Mojo"
    elif choice == "0":
        print("Abgebrochen.")
        return
    else:
        print("❌ Ungültige Auswahl")
        return
    
    print(f"\n🎯 Wechsle zu {backend} Backend auf Port {port}...")
    
    # 1. Update Caddyfile
    if not update_caddyfile(port):
        return
    
    # 2. Kill old backends
    print("\n🔪 Beende alte Backends...")
    kill_process_on_port(5001)
    kill_process_on_port(5002)
    
    # 3. Start new backend
    if not start_backend(port):
        return
    
    # 4. Restart Caddy
    restart_caddy()
    
    print("\n" + "=" * 60)
    print(f"✅ ERFOLGREICH ZU {backend.upper()} BACKEND GEWECHSELT!")
    print("=" * 60)
    print(f"\nBackend läuft auf: http://localhost:{port}")
    print(f"Proxy läuft auf: http://localhost:8088")
    print(f"\nTesten Sie mit:")
    print(f"  curl http://localhost:8088/health")
    print(f"  curl http://localhost:8088/api/facts/count")
    
    if port == 5002:
        print(f"\nC++ Mojo spezielle Endpoints:")
        print(f"  http://localhost:8088/api/mojo/flags")
        print(f"  http://localhost:8088/api/quality/metrics")

if __name__ == "__main__":
    main()
