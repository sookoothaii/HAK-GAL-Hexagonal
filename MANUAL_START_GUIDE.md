# MANUELLE START-ANLEITUNG
================================

Falls die automatischen Scripts nicht funktionieren, starten Sie die Services manuell:

## SCHRITT 1: Öffnen Sie 5 separate CMD/PowerShell-Fenster

## SCHRITT 2: In jedem Fenster einzeln ausführen:

### FENSTER 1 - API (MUSS ZUERST STARTEN!)
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal"
D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe hexagonal_api_enhanced_clean.py
```

### FENSTER 2 - Caddy Proxy
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
caddy.exe run --config Caddyfile
```

### FENSTER 3 - Dashboard
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py
```

### FENSTER 4 - Prometheus
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py
```

### FENSTER 5 - Frontend
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
npm run dev
```

## ALTERNATIVE: Mit aktivierter venv

### In jedem Fenster erst venv aktivieren:
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
.venv_hexa\Scripts\activate
```

### Dann die Services starten:
```cmd
# Fenster 1 (API):
cd src_hexagonal
python hexagonal_api_enhanced_clean.py

# Fenster 2 (Caddy):
.\caddy.exe run --config .\Caddyfile

# Fenster 3 (Dashboard):
python hakgal_dashboard_no_psutil.py

# Fenster 4 (Prometheus):
python hakgal_prometheus_optimized.py

# Fenster 5 (Frontend):
npm run dev
```

## TROUBLESHOOTING

### Problem: "python nicht gefunden"
Lösung: Verwenden Sie den absoluten Pfad:
```
D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe
```

### Problem: "Modul nicht gefunden"
Lösung: Installieren Sie fehlende Pakete:
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
.venv_hexa\Scripts\pip install flask prometheus-client
```

### Problem: API startet nicht
Lösung: Stellen Sie sicher, dass Sie im src_hexagonal Ordner sind:
```cmd
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal"
```

## URLS NACH DEM START

- Dashboard:  http://127.0.0.1:5000
- API:        http://127.0.0.1:5002/api/v1/system/status
- Frontend:   http://127.0.0.1:5173
- Prometheus: http://127.0.0.1:8000/metrics
- Proxy:      http://127.0.0.1:8088

WICHTIG: Verwenden Sie 127.0.0.1 statt localhost!
