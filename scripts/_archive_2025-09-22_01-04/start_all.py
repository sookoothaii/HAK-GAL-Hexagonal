#!/usr/bin/env python3
"""
HAK_GAL STARTUP - Python Version
Startet alle Services ohne PowerShell/Batch
"""
import subprocess
import time
import os
from pathlib import Path

def print_header():
    print("\n" + "="*50)
    print("    🚀 HAK_GAL STARTUP - Python Version")
    print("="*50 + "\n")

def start_service(name, command, cwd, color_code):
    """Startet einen Service in neuem Fenster"""
    print(f"\033[{color_code}m[{name}] Starting...\033[0m")
    
    # Windows: Neues CMD-Fenster
    cmd = f'start "{name}" cmd /k "{command}"'
    subprocess.Popen(cmd, shell=True, cwd=cwd)
    
def main():
    print_header()
    
    base_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL")
    os.chdir(base_dir)
    
    # Service-Definitionen
    services = [
        {
            "name": "API :5002",
            "command": r"..\.venv_hexa\Scripts\python.exe hexagonal_api_enhanced_clean.py",
            "cwd": base_dir / "src_hexagonal",
            "wait": 3,
            "color": "94"  # Blue
        },
        {
            "name": "Caddy :8088",
            "command": r".\caddy.exe run --config .\Caddyfile",
            "cwd": base_dir,
            "wait": 1,
            "color": "95"  # Magenta
        },
        {
            "name": "Dashboard :5000",
            "command": r".\.venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py",
            "cwd": base_dir,
            "wait": 1,
            "color": "92"  # Green
        },
        {
            "name": "Prometheus :8000",
            "command": r".\.venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py",
            "cwd": base_dir,
            "wait": 1,
            "color": "93"  # Yellow
        },
        {
            "name": "Frontend :5173",
            "command": "npm run dev",
            "cwd": base_dir,
            "wait": 0,
            "color": "96"  # Cyan
        }
    ]
    
    # Starte Services
    for i, service in enumerate(services, 1):
        print(f"[{i}/{len(services)}] ", end="")
        start_service(
            service["name"],
            service["command"],
            service["cwd"],
            service["color"]
        )
        if service["wait"] > 0:
            time.sleep(service["wait"])
    
    print("\n" + "="*50)
    print("✅ ALL SERVICES STARTED!")
    print("="*50)
    
    print("\n📊 Service URLs:")
    print("  Dashboard:  http://127.0.0.1:5000")
    print("  API:        http://127.0.0.1:5002/api/v1/system/status")
    print("  Frontend:   http://127.0.0.1:5173")
    print("  Prometheus: http://127.0.0.1:8000/metrics")
    print("  Proxy:      http://127.0.0.1:8088")
    
    print("\n⚠️ WICHTIG: Verwenden Sie 127.0.0.1 statt localhost!")
    print("           (localhost hat 2-Sekunden-Delay in Windows)\n")
    
    input("Drücken Sie Enter zum Beenden...")

if __name__ == "__main__":
    main()
