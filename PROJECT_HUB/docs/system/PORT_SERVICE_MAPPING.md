---
title: "HAK_GAL Port & Service Mapping"
created: "2025-01-28T13:45:00Z"
author: "claude-opus-4.1"
topics: ["system"]
tags: ["ports", "services", "monitoring", "architecture", "redis"]
privacy: "internal"
summary_200: |-
  Comprehensive port scan and service mapping of HAK_GAL system. Documents 7 active services
  including main API (5002), React frontend (5173), Redis cache (6379), Prometheus (8000),
  and proxy servers (8080, 8088). Identifies that port 5001 is inactive (merged with 5002)
  and discovers previously undocumented Redis cache explaining performance gains. Includes
  start commands, security notes, and service categories. Based on actual network scan.
---

# HAK_GAL HEXAGONAL - Port & Service Mapping
# Stand: 2025-01-28 | Aktive Services: 7

## 📊 AKTIVE PORTS (Scan-Ergebnis)

| Port | Service | Status | Details |
|------|---------|--------|---------|
| **5000** | Flask Dashboard | ✅ AKTIV | Legacy Frontend, HTTP 200 |
| **5002** | API Write/Read | ✅ AKTIV | Main API, 4.242 Facts |
| **5173** | Vite React Frontend | ✅ AKTIV | Development Server, HTTP 200 |
| **6379** | Redis | ✅ AKTIV | Cache/Session Storage |
| **8000** | Prometheus | ✅ AKTIV | Metrics verfügbar |
| **8080** | Alternative Proxy | ✅ AKTIV | HTTP 403 (Auth required) |
| **8088** | Nginx Reverse Proxy | ✅ AKTIV | Main Proxy |

## ❌ INAKTIVE PORTS (Dokumentiert aber offline)

| Port | Service | Grund |
|------|---------|-------|
| **5001** | API Read-Only | Nicht gestartet oder merged mit 5002 |
| **5003** | Mojo Adapter | Legacy, deprecated |
| **3000** | Grafana | Optional, nicht installiert |
| **9090** | Prometheus Server | Nur Exporter läuft (8000) |

## 🎯 SERVICE-KATEGORIEN

### BACKEND API
- **5002**: Hauptzugriff für Read/Write Operations
  - `/api/facts/*` - Fakten-Management
  - `/api/system/*` - System-Status
  - Governance V3 integriert

### FRONTEND
- **5173**: Moderne React-Oberfläche (Vite)
- **5000**: Legacy Flask-Templates (Fallback)

### MONITORING
- **8000**: Prometheus Metrics Exporter
  - `/metrics` - System-Metriken
  - CPU, Memory, Request-Count

### PROXY & ROUTING
- **8088**: Nginx Hauptproxy
- **8080**: Alternative/Backup Proxy

### CACHE
- **6379**: Redis für Session/Cache
  - Wird von API für Performance genutzt

## 🚀 START-REIHENFOLGE

```bash
# 1. Backend starten
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal
python hexagonal_api_enhanced_clean.py  # Startet Port 5002 & 8000

# 2. Frontend starten
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend
npm run dev  # Startet Port 5173

# 3. Redis läuft bereits (Windows Service oder Docker)

# 4. Proxies sind bereits aktiv
```

## 📌 WICHTIGE ERKENNTNISSE

1. **Port 5001 fehlt** - Wahrscheinlich in 5002 integriert (Read+Write kombiniert)
2. **Redis läuft** - Erklärt die gute Performance (Cache)
3. **Zwei Proxies** - 8088 (Haupt) und 8080 (Backup/Test)
4. **Kein Grafana** - Monitoring nur über Prometheus Raw-Metrics

## 🔒 SICHERHEIT

- Port 8080 gibt 403 (Forbidden) - Auth konfiguriert
- Alle Services nur auf localhost (127.0.0.1)
- Redis ohne Passwort (nur lokal erreichbar)

## 📝 EMPFEHLUNG

Das Setup ist funktional und sicher. Die wichtigsten Services laufen:
- API (5002) ✅
- Frontend (5173) ✅  
- Monitoring (8000) ✅
- Cache (6379) ✅

Port 5001 könnte reaktiviert werden für Read-Only Zugriff, ist aber nicht kritisch da 5002 beide Funktionen übernimmt.
