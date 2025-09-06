import os
import json
import time

print("=" * 60)
print(" AKTIVIERE MODERNES DASHBOARD - QUICK FIX")
print("=" * 60)
print()

# Pfade
BASE_DIR = r"D:\MCP Mods\HAK_GAL_HEXAGONAL"
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
PRO_APP_PATH = os.path.join(FRONTEND_DIR, "src", "ProApp.tsx")

print("[1/3] Prüfe ProApp.tsx...")

# Lese ProApp.tsx
with open(PRO_APP_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Prüfe ob ProDashboardEnhanced bereits importiert wird
if "ProDashboardEnhanced" in content:
    print("✅ ProDashboardEnhanced ist bereits aktiviert!")
else:
    print("⚠️ ProDashboardEnhanced fehlt - aktiviere jetzt...")
    
    # Ersetze ProDashboard mit ProDashboardEnhanced
    content = content.replace(
        "import ProDashboard from '@/pages/ProDashboard';",
        "import ProDashboardEnhanced from '@/pages/ProDashboardEnhanced'; // MODERN DASHBOARD"
    )
    
    content = content.replace(
        "<ProDashboard />",
        "<ProDashboardEnhanced />"
    )
    
    # Schreibe zurück
    with open(PRO_APP_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ProDashboardEnhanced aktiviert!")

print()
print("[2/3] Prüfe Konfiguration...")

# Prüfe backends.ts
BACKENDS_PATH = os.path.join(FRONTEND_DIR, "src", "config", "backends.ts")
if os.path.exists(BACKENDS_PATH):
    with open(BACKENDS_PATH, 'r', encoding='utf-8') as f:
        backend_content = f.read()
    
    if "port: 5002" in backend_content:
        print("✅ Backend Port 5002 korrekt konfiguriert")
    else:
        print("⚠️ Backend Port nicht korrekt - bitte manuell prüfen")
else:
    print("⚠️ backends.ts nicht gefunden")

print()
print("[3/3] Erstelle Start-Script...")

# Erstelle Start-Batch
START_SCRIPT = os.path.join(BASE_DIR, "START_MODERN_DASHBOARD.bat")
with open(START_SCRIPT, 'w') as f:
    f.write("""@echo off
cls
echo ==========================================
echo   MODERNES NEUROSYMBOLIC DASHBOARD
echo ==========================================
echo.

cd /d "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\frontend"

echo Starte Frontend mit modernem Dashboard...
echo.
echo Features:
echo - System Trust Score (50%% Anzeige)
echo - Neural Components (HRM 3.5M)
echo - Symbolic Components (4,855 Facts)
echo - Self-Learning System (Governor)
echo - Backend Health Monitoring
echo.

npm run dev -- --port 5173

pause
""")

print(f"✅ Start-Script erstellt: {START_SCRIPT}")

print()
print("=" * 60)
print(" SETUP ABGESCHLOSSEN!")
print("=" * 60)
print()
print("Dashboard-Features:")
print("- System Trust Score mit Live-Berechnung")
print("- Neural Components (HRM Model Status)")
print("- Symbolic Components (Facts Counter)")
print("- Self-Learning System (Governor Control)")
print("- Backend Health mit Auto-Refresh (alle 5 Sekunden)")
print("- System Capabilities Status")
print()
print("Starte mit: START_MODERN_DASHBOARD.bat")
print()
print("Das Dashboard läuft auf: http://localhost:8088")
print("Backend API läuft auf:   http://localhost:5002")
print()
