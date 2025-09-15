# HAK_GAL STARTUP SCRIPTS
================================

## 🚀 VERFÜGBARE START-OPTIONEN

### 1. **START_ALL_SERVICES.ps1** (EMPFOHLEN)
   - Startet ALLE Services in korrekter Reihenfolge
   - Mit Port-Checks und Health-Checks
   - Farbige Ausgabe für jeden Service
   - **Start:** Rechtsklick → "Mit PowerShell ausführen"

### 2. **QUICK_START.ps1** (Flexibel)
   - Interaktive Auswahl der Services
   - Wahl zwischen Dashboard-Versionen
   - Nur gewünschte Services starten
   - **Start:** Rechtsklick → "Mit PowerShell ausführen"

### 3. **START_HAK_GAL.bat** (Einfachste Option)
   - Keine PowerShell nötig
   - Startet alle Services
   - **Start:** Doppelklick

### 4. **STOP_ALL_SERVICES.ps1**
   - Beendet ALLE laufenden Services
   - Zeigt Port-Status nach Shutdown
   - **Start:** Rechtsklick → "Mit PowerShell ausführen"

## 📊 SERVICE-ÜBERSICHT

| Service | Port | Befehl | Verzeichnis | Reihenfolge |
|---------|------|--------|-------------|-------------|
| **API** | 5002 | `python hexagonal_api_enhanced_clean.py` | `src_hexagonal` | 1️⃣ |
| **Caddy Proxy** | 8088 | `.\caddy.exe run --config .\Caddyfile` | Hauptverzeichnis | 2️⃣ |
| **Dashboard** | 5000 | `python hakgal_dashboard_no_psutil.py` | Hauptverzeichnis | 3️⃣ |
| **Prometheus** | 8000 | `python hakgal_prometheus_optimized.py` | Hauptverzeichnis | 4️⃣ |
| **Frontend** | 5173 | `npm run dev` | Hauptverzeichnis | 5️⃣ |

## 🔧 MANUELLE STARTS (Einzeln)

Falls Sie Services einzeln starten möchten:

```powershell
# Aktiviere venv (falls noch nicht aktiv)
.\.venv_hexa\Scripts\Activate.ps1

# 1. API (MUSS ZUERST STARTEN)
cd src_hexagonal
python hexagonal_api_enhanced_clean.py

# 2. Caddy Proxy
cd ..
.\caddy.exe run --config .\Caddyfile

# 3. Dashboard (eine Version wählen)
python hakgal_dashboard_no_psutil.py    # Schneller, ohne psutil
# ODER
python hakgal_dashboard_ultra.py        # Mit allen Features

# 4. Prometheus
python hakgal_prometheus_optimized.py

# 5. Frontend
npm run dev
```

## ⚠️ WICHTIGE HINWEISE

### 1. **IMMER 127.0.0.1 statt localhost verwenden!**
   - Windows hat ein 2-Sekunden-Delay bei `localhost`
   - `127.0.0.1` ist instant
   - Alle URLs sollten `http://127.0.0.1:PORT` verwenden

### 2. **Start-Reihenfolge beachten**
   - API muss ZUERST starten (andere Services hängen davon ab)
   - Caddy Proxy sollte vor Dashboard starten
   - Frontend kann als letztes starten

### 3. **Dashboard-Versionen**
   - `hakgal_dashboard_no_psutil.py` - Schneller, ohne System-Monitoring
   - `hakgal_dashboard_ultra.py` - Volle Features, aber kann langsamer sein

### 4. **Port-Konflikte**
   - Prüfen: `netstat -an | findstr :5000`
   - Alte Prozesse beenden: `STOP_ALL_SERVICES.ps1` ausführen

## 📊 SERVICE-URLs

Nach dem Start sind die Services hier erreichbar:

| Service | URL | Beschreibung |
|---------|-----|--------------|
| Dashboard | http://127.0.0.1:5000 | HAK_GAL Dashboard |
| API | http://127.0.0.1:5002/api/v1/system/status | API Status |
| Frontend | http://127.0.0.1:5173 | React Frontend |
| Prometheus | http://127.0.0.1:8000/metrics | Metriken |
| Proxy | http://127.0.0.1:8088 | Caddy Reverse Proxy |

## 🛠️ TROUBLESHOOTING

### Problem: PowerShell Scripts starten nicht
```powershell
# Als Administrator ausführen:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Port bereits belegt"
1. `STOP_ALL_SERVICES.ps1` ausführen
2. Warten Sie 2-3 Sekunden
3. Erneut starten

### Problem: Frontend startet nicht
- Prüfen Sie ob `npm` installiert ist
- Führen Sie `npm install` im Projektverzeichnis aus

### Problem: Caddy startet nicht
- Prüfen Sie ob `caddy.exe` und `Caddyfile` vorhanden sind
- Stellen Sie sicher dass Port 8088 frei ist

### Problem: API startet nicht
- Prüfen Sie ob das `src_hexagonal` Verzeichnis existiert
- Stellen Sie sicher dass alle Python-Dependencies installiert sind

## 🎯 DESKTOP-VERKNÜPFUNG

Führen Sie `CREATE_SHORTCUTS.ps1` aus um Desktop-Verknüpfungen zu erstellen.

Oder manuell:
1. Rechtsklick auf Desktop → Neu → Verknüpfung
2. Ziel: `powershell.exe -ExecutionPolicy Bypass -File "D:\MCP Mods\HAK_GAL_HEXAGONAL\START_ALL_SERVICES.ps1"`
3. Name: "HAK_GAL Start"

## 💡 TIPPS

- **Entwicklung:** Nutzen Sie `QUICK_START.ps1` um nur benötigte Services zu starten
- **Produktion:** Nutzen Sie `START_ALL_SERVICES.ps1` für vollständigen Start
- **Performance:** Dashboard ohne psutil ist deutlich schneller
- **Monitoring:** Prometheus auf http://127.0.0.1:8000/metrics zeigt alle Metriken

---
Stand: 2025
HAK_GAL Hexagonal Architecture System
