# HAK-GAL Suite - Vollständige Technische Architektur-Dokumentation
## Comprehensive Technical Architecture Report

**Dokument-ID:** HAK-GAL-TECH-ARCH-20250830-V1  
**Status:** Kanonisch - Referenzarchitektur  
**Autor:** Claude (Anthropic) - Technische Dokumentation  
**Datum:** 2025-08-30  
**Klassifikation:** Technische Referenz-Dokumentation  

---

## Executive Summary

Die HAK-GAL Suite ist ein fortschrittliches Multi-Agent-Knowledge-System, das auf einer Hexagonal Architecture (Ports & Adapters Pattern) basiert. Das System integriert multiple KI-Agenten, eine SQLite-basierte Wissensdatenbank mit Content-Addressable Storage, ein neurales Reasoning-Modell (HRM) mit 3.5M Parametern und einen umfassenden MCP-Server mit 44 Tools.

---

## 1. Architektur-Übersicht

### 1.1 Grundlegendes Architektur-Pattern: Hexagonal Architecture

Die HAK-GAL Suite implementiert eine **Hexagonal Architecture** (auch bekannt als Ports & Adapters), die folgende Vorteile bietet:

- **Lose Kopplung:** Core-Domain ist unabhängig von externen Systemen
- **Testbarkeit:** Jede Schicht kann isoliert getestet werden
- **Austauschbarkeit:** Adapter können ohne Core-Änderungen ersetzt werden
- **Skalierbarkeit:** Neue Adapter können einfach hinzugefügt werden

### 1.2 Schichten-Architektur

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│                 Frontend (React/Vite:5173)              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     API LAYER (5002)                     │
│           hexagonal_api_enhanced_clean.py               │
│                    Flask + SocketIO                      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                     │
│      FactManagementService | ReasoningService           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      DOMAIN CORE                         │
│         Entities | Value Objects | Domain Logic          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    ADAPTER LAYER                         │
├──────────────┬──────────────┬──────────────┬───────────┤
│   SQLite     │    Agents    │     HRM      │  System   │
│   Adapter    │   Adapters   │   Adapter    │  Monitor  │
└──────────────┴──────────────┴──────────────┴───────────┘
```

---

## 2. Komponenten-Details

### 2.1 Core Domain

#### Entities
- **Fact:** Repräsentiert einen Wissensfakt im Format `Predicate(Subject, Object).`
- **Query:** Suchanfrage mit Text, Limit und Confidence-Threshold
- **ReasoningResult:** Ergebnis einer Reasoning-Operation

#### Services
- **FactManagementService:** CRUD-Operationen für Facts
- **ReasoningService:** Logische Schlussfolgerungen und Inferenz

#### Ports (Interfaces)
- **FactRepository:** Interface für Datenpersistenz
- **ReasoningEngine:** Interface für Reasoning-Operationen
- **AgentCommunicator:** Interface für Multi-Agent-Kommunikation

### 2.2 Adapter-Schicht

#### SQLite Adapter (`sqlite_adapter.py`)
```python
class SQLiteFactRepository:
    - Implementiert Content-Addressable Storage
    - Nutzt statement als Primary Key
    - 5,858 Facts (Stand: 2025-08-30)
    - Tabellen: facts, fact_groups, fact_arguments, etc.
```

#### Agent Adapters (`agent_adapters.py`)
```python
Implementierte Adapter:
1. GeminiAdapter       # Google Gemini AI (gemini-1.5-flash)
2. ClaudeCliAdapter    # Anthropic Claude CLI
3. ClaudeDesktopAdapter # Claude Desktop App
4. CursorAdapter       # Cursor IDE Integration
```

#### HRM Neural Adapter (`hrm_adapter.py`)
```python
class NativeReasoningEngine:
    - Model: 3.5M Parameter GRU-basiert
    - Validation Accuracy: 90.8%
    - Path: models/hrm_model_v2.pth
    - Status: Geladen, sekundär genutzt
```

#### System Monitor (`system_monitor.py`)
```python
class SystemMonitor:
    - CPU/Memory/Disk Monitoring
    - WebSocket Event Broadcasting
    - Real-time Metrics
```

#### Governor Adapter (`governor_adapter.py`)
```python
class GovernorAdapter:
    - Kill Switch Mechanismus
    - Risk Estimation
    - Policy Guard
    - Audit Logging
    - Engines: aethelred_engine.py, thesis_engine.py
```

---

## 3. Datenbank-Architektur

### 3.1 Content-Addressable Storage Pattern

Die Datenbank verwendet ein **Content-Addressable Storage** Pattern:

```sql
CREATE TABLE facts (
    statement TEXT PRIMARY KEY,  -- Der Inhalt IST die Adresse
    context TEXT DEFAULT '{}',
    fact_metadata TEXT DEFAULT '{}',
    predicate TEXT,
    subject TEXT,
    object TEXT,
    statement_hash TEXT,
    confidence REAL DEFAULT 1.0,
    source TEXT DEFAULT 'system'
)
```

#### Vorteile:
- **Automatische Deduplikation:** Keine doppelten Facts möglich
- **Semantische IDs:** Statement ist selbst-identifizierend
- **Immutability:** Facts sind unveränderlich
- **Speichereffizienz:** Keine zusätzliche ID-Spalte

#### Zugriffsmuster:
```sql
-- Über Statement (Primary Key)
SELECT * FROM facts WHERE statement = 'ConsistsOf(HAK_GAL, REST_API).';

-- Über SQLite ROWID
SELECT rowid, * FROM facts WHERE rowid = 123;

-- Über Prädikat
SELECT * FROM facts WHERE predicate = 'ConsistsOf';
```

### 3.2 Datenbank-Metriken
- **Größe:** 1,761,280 bytes
- **Facts:** 5,858
- **Tabellen:** 7 (facts, fact_groups, fact_arguments, etc.)
- **Indizes:** 4
- **Query-Performance:** < 1ms

---

## 4. API-Schicht

### 4.1 REST API Endpoints

#### Core Endpoints
- `GET /health` - System Health Check
- `GET /api/status` - Detaillierter Systemstatus
- `GET /api/facts` - Facts abrufen
- `POST /api/facts` - Fact hinzufügen
- `DELETE /api/facts` - Fact löschen
- `POST /api/search` - Facts suchen
- `POST /api/reason` - Reasoning durchführen

#### Agent Bus Endpoints
- `POST /api/agent-bus/delegate` - Task an Agent delegieren
- `GET /api/agent-bus/tasks/{task_id}` - Task-Status

#### LLM Endpoints
- `POST /api/llm/get-explanation` - LLM-basierte Erklärung
- `POST /api/graph/generate` - Knowledge Graph generieren

#### HRM Endpoints
- `POST /api/hrm/retrain` - Model retraining
- `GET /api/hrm/model_info` - Model information
- `GET /api/hrm/feedback-stats` - Feedback statistics

### 4.2 WebSocket Events

```javascript
// Client → Server
socket.emit('connect')
socket.emit('cursor_response', {task_id, result})
socket.emit('governor_control', {action})

// Server → Client
socket.emit('fact_added', {statement, success})
socket.emit('reasoning_complete', {query, confidence})
socket.emit('agent_response', {task_id, result})
socket.emit('system_metrics', {cpu, memory, disk})
```

### 4.3 Authentifizierung
- **Method:** API Key
- **Header:** `X-API-Key`
- **Key:** `hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d` (Development)
- **Write Token:** `515f57956e7bd15ddc3817573598f190`

---

## 5. Multi-Agent-System

### 5.1 Agent-Kommunikationsarchitektur

```
User Request
    ↓
Agent Bus (Orchestrator)
    ↓
[Parallel Dispatch]
    ├── Gemini (2-5s)
    ├── Claude CLI (5-30s)
    ├── Claude Desktop (Variable)
    └── Cursor IDE (WebSocket)
    ↓
Response Aggregation
    ↓
Unified Response
```

### 5.2 Agent-Spezifikationen

#### Gemini Adapter
- **Provider:** Google
- **Model:** gemini-1.5-flash (default)
- **Response Time:** 2-5 seconds
- **Communication:** REST API
- **Fallback:** Ollama local

#### Claude CLI Adapter
- **Provider:** Anthropic
- **Interface:** Subprocess
- **Response Time:** 5-30 seconds
- **Commands:** Multiple variants supported

#### Claude Desktop Adapter
- **Communication Methods:**
  - MCP Protocol (Ports: 3000, 3333, 5000, 5555)
  - URL Scheme Integration
  - File Exchange System

#### Cursor Adapter
- **Protocol:** WebSocket + MCP
- **Integration:** IDE-based
- **File Exchange:** Fallback mechanism

### 5.3 Response Logging
```
agent_responses/
├── success/
├── error/
├── by_agent/
│   ├── gemini/
│   ├── cursor/
│   ├── claude_cli/
│   └── claude_desktop/
├── index.json
└── [agent]_latest_response.txt
```

---

## 6. MCP Server Integration

### 6.1 Server-Spezifikationen
- **Version:** HAK_GAL MCP SQLite Full FIXED v3.1
- **Protocol:** stdio-basiert
- **Tools:** 44 verfügbar

### 6.2 Tool-Kategorien

#### Knowledge Base Tools (28)
- Facts Management (add, delete, update, search)
- Analysis (semantic_similarity, consistency_check)
- Statistics (predicates_stats, entities_stats)
- Maintenance (backup, restore, validate)

#### File Operations (13)
- CRUD Operations
- Directory Management
- Search & Grep
- Multi-Edit Support

#### System Tools (3)
- Health Check
- System Status
- Audit Logging

---

## 7. Frontend-Architektur

### 7.1 Technology Stack
- **Framework:** React
- **Bundler:** Vite 7.1.1
- **Styling:** Tailwind CSS
- **State Management:** React Hooks
- **WebSocket:** Socket.IO Client

### 7.2 Komponenten-Struktur
```
frontend/
├── src/
│   ├── components/
│   │   ├── FactManager.jsx
│   │   ├── AgentBus.jsx
│   │   ├── SystemMonitor.jsx
│   │   └── KnowledgeGraph.jsx
│   ├── services/
│   │   ├── api.js
│   │   └── websocket.js
│   └── App.jsx
└── public/
```

---

## 8. Deployment & Infrastructure

### 8.1 System-Anforderungen
- **Python:** 3.11+
- **Node.js:** 18+
- **SQLite:** 3.35+
- **RAM:** Minimum 4GB (8GB empfohlen für HRM)
- **GPU:** Optional (für HRM Acceleration)

### 8.2 Process-Struktur
```bash
# Backend API Server
python src_hexagonal/hexagonal_api_enhanced_clean.py  # Port 5002

# Frontend Dev Server
cd frontend && npm run dev  # Port 5173

# MCP Server (stdio)
python hakgal_mcp_v31_REPAIRED.py

# Optional: WebSocket Bridge
python websocket_bridge.py  # Port 8765
```

### 8.3 Verzeichnisstruktur
```
HAK_GAL_HEXAGONAL/
├── src_hexagonal/          # Hexagonal Architecture Implementation
│   ├── adapters/          # Alle Adapter-Implementierungen
│   ├── application/       # Application Services
│   ├── core/             # Domain Core
│   └── infrastructure/   # Infrastructure Services
├── models/                # Neural Network Models
│   └── hrm_model_v2.pth  # 3.5M Parameter Model
├── frontend/              # React Frontend
├── backups/              # Database Backups
├── agent_responses/      # Agent Response Logs
├── PROJECT_HUB/          # Documentation
└── hexagonal_kb.db       # SQLite Database
```

---

## 9. Performance-Metriken

### 9.1 Response-Zeiten
| Operation | Zeit | Details |
|-----------|------|---------|
| API Call (local) | < 100ms | Flask endpoint |
| DB Query | < 1ms | SQLite indexed |
| Gemini Response | 2-5s | Cloud API |
| Claude CLI | 5-30s | Subprocess |
| HRM Inference | < 10ms | GPU accelerated |
| WebSocket Event | < 50ms | Eventlet |

### 9.2 Kapazitäten
- **Concurrent Connections:** Unbegrenzt (Thread Pool)
- **Facts Limit:** Praktisch unbegrenzt (SQLite)
- **Agent Parallel Calls:** 4 (konfigurierbar)
- **WebSocket Clients:** 1000+ (Eventlet)

### 9.3 Ressourcen-Nutzung
- **API Server RAM:** ~200MB
- **HRM Model RAM:** ~500MB
- **SQLite Cache:** 64MB
- **CPU Usage:** 5-15% (idle), 50-80% (active)

---

## 10. Sicherheit & Governance

### 10.1 Sicherheitsfeatures
- **API Key Authentication**
- **Write Token für Schreibzugriffe**
- **CORS Policy (konfigurierbar)**
- **SQL Injection Prevention**
- **Rate Limiting (optional)**

### 10.2 Governor System
- **Kill Switch:** Notfall-Stop aller Operationen
- **Risk Estimator:** Bewertung kritischer Operationen
- **Policy Guard:** Regelbasierte Zugriffskontrolle
- **Audit Logger:** Vollständige Aktivitätsprotokollierung

### 10.3 Monitoring
- **Sentry Integration:** Error Tracking (optional)
- **System Monitor:** CPU, Memory, Disk
- **Response Logging:** Alle Agent-Interaktionen
- **Audit Trail:** Kritische Operationen

---

## 11. HAK/GAL Verfassung

Das System folgt der HAK/GAL Verfassung mit 8 Artikeln:

1. **Komplementäre Intelligenz:** Menschliche und KI-Agenten ergänzen sich
2. **Gezielte Befragung:** Präzise Anfragen für optimale Ergebnisse
3. **Externe Verifikation:** Unabhängige Validierung von Hypothesen
4. **Bewusstes Grenzüberschreiten:** Lernen durch kontrollierte Fehler
5. **System-Metareflexion:** Selbstbeobachtung und -analyse
6. **Empirische Validierung:** Quantitative Datenvalidierung
7. **Konjugierte Zustände:** Balance zwischen Präzision und Kreativität
8. **Prinzipien-Kollision:** Protokoll für Konfliktauflösung

---

## 12. Aktuelle System-Konfiguration

### 12.1 Produktions-Status (2025-08-30)
```python
SYSTEM_CONFIG = {
    'version': '3.1',
    'database': {
        'path': 'hexagonal_kb.db',
        'facts': 5858,
        'size_mb': 1.76,
        'integrity': 'OK'
    },
    'api': {
        'port': 5002,
        'framework': 'Flask',
        'async': 'Eventlet'
    },
    'frontend': {
        'port': 5173,
        'framework': 'React',
        'bundler': 'Vite'
    },
    'agents': {
        'active': ['gemini', 'claude_cli', 'claude_desktop', 'cursor'],
        'primary': 'gemini'
    },
    'hrm': {
        'model': 'hrm_model_v2.pth',
        'parameters': '3.5M',
        'accuracy': 0.908,
        'status': 'loaded_secondary'
    },
    'mcp': {
        'version': 'v3.1',
        'tools': 44,
        'protocol': 'stdio'
    }
}
```

### 12.2 Environment Variables
```bash
HAKGAL_API_KEY=hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d
HAKGAL_WRITE_TOKEN=515f57956e7bd15ddc3817573598f190
HAKGAL_PORT=5002
GEMINI_API_KEY=[configured]
ANTHROPIC_API_KEY=[configured]
```

---

## 13. Entwicklungs-Roadmap

### 13.1 Abgeschlossene Features ✅
- Hexagonal Architecture Implementation
- Multi-Agent System
- Content-Addressable Storage
- WebSocket Support
- HRM Neural Reasoning
- Governor System
- MCP Server Integration

### 13.2 In Entwicklung 🚧
- SQLite3 Full Migration (15 Tabellen)
- Enhanced Agent Orchestration
- GraphQL API Layer
- Distributed Deployment

### 13.3 Geplante Features 📋
- Vector Database Integration
- Kubernetes Deployment
- Enhanced ML Pipeline
- Real-time Collaboration
- Advanced Visualization

---

## 14. Bekannte Limitierungen

1. **Content-Addressable Storage:**
   - Keine traditionelle ID-Spalte
   - Updates erfordern Delete+Insert
   - Längere Primary Keys

2. **Multi-Agent Latenz:**
   - Cloud-APIs haben variable Latenz
   - Keine garantierten Response-Zeiten

3. **HRM Model:**
   - Begrenzt auf trainiertes Vokabular
   - Nicht primär in Produktion genutzt

4. **Skalierung:**
   - Single-Node SQLite Limitation
   - Keine horizontale Skalierung

---

## 15. Zusammenfassung

Die HAK-GAL Suite repräsentiert eine fortschrittliche Implementation einer Hexagonal Architecture mit Multi-Agent-Orchestrierung, neuraler Reasoning-Komponente und robuster Wissensverwaltung. Das System ist produktionsreif, wartbar und erweiterbar, mit klaren Architekturgrenzen und definierten Schnittstellen.

**Kernstärken:**
- ✅ Saubere Architektur-Trennung
- ✅ Multiple AI-Integration
- ✅ Robuste Datenpersistenz
- ✅ Echtzeit-Kommunikation
- ✅ Umfassende Tool-Suite

**Optimierungspotenzial:**
- ⚠️ Horizontale Skalierung
- ⚠️ Response-Zeit-Garantien
- ⚠️ Erweiterte ML-Features

---

## Anhang A: Wichtige Dateien

| Datei | Zweck |
|-------|-------|
| `hexagonal_api_enhanced_clean.py` | Haupt-API-Server |
| `sqlite_adapter.py` | Datenbank-Adapter |
| `agent_adapters.py` | Multi-Agent-System |
| `hrm_model_v2.pth` | Neural Reasoning Model |
| `hexagonal_kb.db` | Wissensdatenbank |
| `hakgal_mcp_v31_REPAIRED.py` | MCP Server |

---

## Anhang B: Kommandos für Entwickler

```bash
# System starten
cd HAK_GAL_HEXAGONAL
python -m venv .venv_hexa
.venv_hexa\Scripts\activate  # Windows
source .venv_hexa/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Backend starten
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Frontend starten
cd frontend
npm install
npm run dev

# Tests ausführen
python comprehensive_db_test.py
python test_system.py

# Backup erstellen
sqlite3 hexagonal_kb.db ".backup backups/db_$(date +%Y%m%d_%H%M%S).db"
```

---

**Ende des Technischen Architekturberichts**

*Dokument-Version: 1.0*  
*Letzte Aktualisierung: 2025-08-30*  
*Nächste Review: 2025-09-30*

---

*Dieser Bericht ist Teil der HAK-GAL technischen Dokumentation und sollte bei allen Architektur-Entscheidungen als Referenz dienen.*