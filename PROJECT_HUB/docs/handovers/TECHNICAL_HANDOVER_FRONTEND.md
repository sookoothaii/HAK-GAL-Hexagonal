# Technisches Handover: HAK-GAL Frontend Dashboard Modernisierung

**Dokument-ID:** HAK-GAL-FRONTEND-HANDOVER-20250819  
**Status:** KRITISCH - Frontend-Integration in Arbeit  
**Autor:** Claude (Anthropic)  
**Datum:** 19.08.2025  
**Snapshot:** `PROJECT_HUB\snapshot_20250819_172844`

---

## EXECUTIVE SUMMARY

Das HAK-GAL System hat ein **modernes Neurosymbolic Dashboard**, das jedoch **noch nicht korrekt integriert** ist. Das Dashboard existiert und ist aktiviert, aber die API-Endpoints sind falsch konfiguriert, was zu 404-Fehlern führt.

### Aktueller Status:
- ✅ **Backend läuft:** Port 5002 (WRITE Mode) 
- ✅ **Frontend läuft:** Port 5173 (Vite Dev Server)
- ✅ **Proxy läuft:** Port 8088 (Caddy)
- ✅ **Dashboard aktiviert:** ProDashboardEnhanced.tsx
- ❌ **API-Integration:** 404-Fehler bei allen Endpoints
- ❌ **Layout:** Dashboard zu groß, erfordert Scrollen

---

## 1. SYSTEM-ARCHITEKTUR

```
HAK-GAL HEXAGONAL ARCHITECTURE
├── Backend (Port 5002)
│   ├── Flask API Server
│   ├── SQLite Database (hexagonal_kb.db)
│   ├── 0 Facts (leer - muss gefüllt werden)
│   └── Write Mode AKTIV
├── Frontend (Port 5173)
│   ├── React 18 + TypeScript
│   ├── Vite Dev Server
│   ├── ProDashboardEnhanced.tsx (aktiv)
│   └── Zustand Store Management
└── Proxy (Port 8088)
    └── Caddy Reverse Proxy
```

---

## 2. KRITISCHE PROBLEME & LÖSUNGEN

### Problem 1: API 404-Fehler
**Symptom:** Alle API-Aufrufe geben 404 zurück  
**Ursache:** Falsche URL-Pfade im Frontend

**LÖSUNG:**
```javascript
// FALSCH (current):
fetch('/health')
fetch('/api/facts/count')

// RICHTIG (sollte sein):
fetch('http://localhost:5002/health')
fetch('http://localhost:5002/api/facts/count')

// ODER mit Proxy:
fetch('/api/health')  // Caddy leitet zu 5002 weiter
```

### Problem 2: Dashboard zu groß (Scrolling erforderlich)
**Symptom:** Dashboard passt nicht auf einen Bildschirm  
**Ursache:** Zu viele große Cards, keine kompakte Ansicht

**LÖSUNG:**
1. Verwende Grid mit kleineren Cards
2. Reduziere Padding und Margins
3. Nutze kompaktere Komponenten
4. Implementiere responsive Design für verschiedene Bildschirmgrößen

---

## 3. VERFÜGBARE API-ENDPOINTS (Port 5002)

```python
# GESUNDHEIT & STATUS
GET /health                        # System Health Check
GET /api/system/status              # Detaillierter System Status

# FACTS & KNOWLEDGE BASE
GET /api/facts/count                # Anzahl der Facts
GET /api/facts                      # Facts abrufen (paginated)
POST /api/facts                     # Neuen Fact hinzufügen
GET /api/knowledge-base/status      # KB Status

# GOVERNOR
GET /api/governor/status            # Governor Status
POST /api/governor/start            # Governor starten
POST /api/governor/stop             # Governor stoppen

# HRM (Neural Reasoning)
GET /api/hrm/status                 # HRM Model Status
POST /api/hrm/reason                # Neural Reasoning Query

# ENGINES
GET /api/engines/status             # Engine Status
POST /api/engines/aethelred/start   # Aethelred Engine starten
POST /api/engines/thesis/start      # Thesis Engine starten
```

---

## 4. FRONTEND-DATEIEN ZUM BEARBEITEN

### Hauptdateien:
```
frontend/src/
├── ProApp.tsx                      # ✅ Bereits korrekt (lädt ProDashboardEnhanced)
├── pages/
│   ├── ProDashboardEnhanced.tsx    # ⚠️ MUSS GEFIXT WERDEN (API-URLs)
│   └── ProDashboardCompact.tsx     # 🆕 NEUE KOMPAKTE VERSION (optional)
├── config/
│   └── backends.ts                 # ⚠️ API-URLs konfigurieren
└── stores/
    └── useGovernorStore.ts         # ✅ Store funktioniert
```

---

## 5. QUICK-FIX ANLEITUNG

### Schritt 1: Fix API URLs in ProDashboardEnhanced.tsx

```javascript
// Zeile ~50-60, ersetze fetchWithFallback Funktion:
const API_BASE = 'http://localhost:5002';  // ODER '' wenn Proxy verwendet

const fetchWithFallback = async (url: string, fallback: any = null) => {
  try {
    const response = await fetch(`${API_BASE}${url}`);
    if (response.ok) {
      return await response.json();
    }
    return fallback;
  } catch {
    return fallback;
  }
};
```

### Schritt 2: Kompaktes Layout

```css
/* Reduziere Container Padding */
.container {
  padding: 0.5rem;  /* statt 1.5rem */
}

/* Kleinere Cards */
.card {
  padding: 0.75rem;  /* statt 1.5rem */
}

/* Grid mit mehr Spalten */
.grid {
  grid-template-columns: repeat(4, 1fr);  /* 4 statt 3 Spalten */
}
```

---

## 6. TEST-KOMMANDOS

```bash
# Backend testen
curl http://localhost:5002/health
curl http://localhost:5002/api/facts/count
curl http://localhost:5002/api/governor/status

# Proxy testen
curl http://localhost:8088/api/health

# Frontend neu starten
cd frontend
npm run dev -- --port 5173
```

---

## 7. ERWARTETES ERGEBNIS

Nach den Fixes sollte das Dashboard zeigen:
- **System Trust Score:** 20% (da 0 Facts)
- **Neural Components:** HRM Model 3.5M Parameters
- **Symbolic Components:** 0 Facts (muss gefüllt werden)
- **Self-Learning System:** Governor INACTIVE
- **Keine 404-Fehler** in der Console
- **Alles auf einem Bildschirm** ohne Scrollen

---

## 8. NÄCHSTE SCHRITTE FÜR DIE NEUE INSTANZ

1. **API-URLs fixen** in ProDashboardEnhanced.tsx
2. **Layout kompakter machen** (siehe Schritt 2)
3. **Facts in DB laden** (aktuell 0!)
4. **Governor aktivieren** für Auto-Learning
5. **HRM Model laden** falls nicht aktiv

---

## 9. WICHTIGE DATEIPFADE

```
PROJECT_ROOT: D:\MCP Mods\HAK_GAL_HEXAGONAL

# Frontend
frontend/src/pages/ProDashboardEnhanced.tsx
frontend/src/config/backends.ts

# Backend
src_hexagonal/api/app.py
hexagonal_kb.db

# Start-Scripts
ULTIMATE_DASHBOARD_FIX.bat
START_CLEAN_FRONTEND.bat

# Logs & Debug
mcp-server-Filesystem.log
frontend/node_modules/.vite/
```

---

## 10. BEKANNTE ISSUES & WORKAROUNDS

### Issue: WebSocket verbindet nicht
**Workaround:** Socket.IO läuft auf 5002, nicht auf separatem Port

### Issue: CUDA nicht verfügbar  
**Workaround:** System läuft auch mit CPU, nur langsamer

### Issue: Facts werden nicht gespeichert
**Workaround:** Prüfe ob WRITE Mode aktiv ist (read_only: false)

---

## APPENDIX: Screenshot des aktuellen Dashboards

Das Dashboard zeigt aktuell:
- ✅ Korrekte Komponenten-Struktur
- ✅ Moderne UI mit Dark Theme
- ❌ API 404-Fehler (rote Punkte in Console)
- ❌ Layout zu groß (Scrollbar sichtbar)
- ❌ 0 Facts (DB ist leer)

---

**ENDE DES HANDOVER-DOKUMENTS**

**Nächste Instanz:** Bitte zuerst die API-URLs fixen, dann das Layout optimieren!