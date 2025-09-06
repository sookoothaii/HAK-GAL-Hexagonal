# HAK-GAL HEXAGONAL System

**Version:** 2.0 - Empirisch Verifiziert  
**Status:** ✅ PRODUKTIONSBEREIT  
**Letzte Aktualisierung:** 2025-01-03

---

## 🚀 Quick Start

```bash
# Backend starten (Port 5002)
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
python src_hexagonal/hexagonal_api_enhanced_clean.py

# Frontend starten (Port 5173, Proxy 8088)
cd frontend
npm run dev
```

---

## 📊 Verifizierte System-Metriken

**Stand: 2025-01-03 - Empirisch getestet**

| Metrik | Spezifikation | **TATSÄCHLICH** | Status |
|--------|---------------|-----------------|--------|
| **Query Performance** | <10ms | **0.475ms** | ✅ 21x besser |
| **Insert Rate** | 10,000/sec | **26,827/sec** | ✅ 268% erreicht |
| **Concurrent Stability** | Stabil | **0 Errors** | ✅ Perfekt |
| **HRM Model** | 572k params | **3.5M params** | ✅ 6x größer |
| **HRM Accuracy** | 85% | **90.8%** | ✅ Übertroffen |
| **Knowledge Base** | - | **5,914 Fakten** | ✅ Aktiv |

---

## 🏗️ Systemarchitektur

### Hexagonale Architektur mit Multi-Agent-System

```
HAK_GAL_HEXAGONAL/
├── src_hexagonal/
│   ├── hexagonal_api_enhanced_clean.py  [API Server - Port 5002]
│   ├── adapters/
│   │   ├── agent_adapters.py           [Multi-Agent System]
│   │   ├── sqlite_adapters.py          [Database Layer]
│   │   └── hrm_feedback_adapter.py     [HRM Integration]
│   └── infrastructure/
│       └── engines/
│           ├── aethelred_engine.py     [Consistency Engine]
│           └── thesis_engine.py        [Relevance Engine]
├── models/
│   └── hrm_model_v2.pth               [3.5M Parameter Neural Model]
├── hexagonal_kb.db                    [SQLite Knowledge Base]
├── frontend/                           [React Dashboard]
└── docs/                              [Aktualisierte Dokumentation]
```

---

## 🧠 HRM Neural Reasoning System

**WICHTIGE KORREKTUR:** HRM ist **VOLL INTEGRIERT** (nicht "nicht integriert" wie falsch dokumentiert)

### Spezifikationen

- **Model:** hrm_model_v2.pth
- **Parameter:** 3,549,825 (3.5M) - NICHT 572k!
- **Accuracy:** 90.8%
- **Vocabulary:** 2,989 Terme
- **Response Time:** <10ms (CUDA-beschleunigt)
- **Status:** ✅ Produktiv

---

## 🤖 Multi-Agent-System

### Verfügbare Adapter

1. **GeminiAdapter** - Google Gemini AI Integration
2. **ClaudeCliAdapter** - Anthropic Claude CLI
3. **ClaudeDesktopAdapter** - Claude Desktop Integration
4. **CursorAdapter** - Cursor IDE Integration

### API Endpoints

```python
POST /api/agent-bus/delegate        # Task-Delegation
GET /api/agent-bus/responses        # Response-Abruf
GET /api/hrm/model_info            # HRM Status
GET /api/facts/search              # Knowledge Base Suche
```

---

## 🔧 MCP Server Tools

**44 Tools verfügbar** (Kategorien):
- Knowledge Base Management: 27 Tools
- File Operations: 13 Tools
- SQLite Operations: 3 Tools
- Code Execution: 1 Tool

---

## 📈 Performance-Benchmarks

### Empirisch verifiziert am 2025-01-03

```python
EMPIRICAL_BASELINE = {
    "query_avg_ms": 0.475,
    "insert_rate_per_sec": 26827,
    "concurrent_reads_per_sec": 71880,
    "concurrent_writes_per_sec": 576,
    "errors_under_load": 0,
    "db_size_mb": 1.68,
    "fact_count": 5914
}
```

### Skalierungs-Projektion

- **10k Fakten:** 2.8 MB (✅ Problemlos)
- **42k Fakten:** 11.76 MB (✅ Handhabbar)
- **100k Fakten:** 28.0 MB (✅ Effizient)
- **1M Fakten:** 280 MB (⚠️ Monitoring empfohlen)

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- CUDA-fähige GPU (optional, für HRM)

### Backend Setup

```bash
# Virtual Environment
python -m venv .venv_hexa
.venv_hexa\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Start Server
python src_hexagonal/hexagonal_api_enhanced_clean.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev  # Development
npm run build  # Production
```

---

## 📚 Dokumentation

### Aktuelle Dokumente (2025-01-03)

- `docs/HAK-GAL-SYSTEM-STATUS-2025-01-03.md` - Vollständiger Systemstatus
- `docs/HAK-GAL-HRM-CORRECTED-2025-01-03.md` - HRM Spezifikationen
- `docs/HAK-GAL-EMPIRICAL-VERIFICATION-2025-01-03.md` - Performance-Tests
- `docs/HAK-GAL-DOC-AUDIT-2025-01-03.md` - Dokumentations-Audit

---

## ⚠️ Wichtige Korrekturen

### Vorherige Fehlinformationen (korrigiert)

| Falsche Angabe | Realität |
|----------------|----------|
| "HRM nicht integriert" | ✅ HRM v2 voll integriert |
| "572k Parameter" | ✅ 3.5M Parameter |
| "10,000 inserts/sec theoretisch" | ✅ 26,827/sec empirisch verifiziert |

---

## 🔒 Sicherheit

- **API Key:** Konfiguriert in `.env`
- **Write Token:** Für schreibende Operationen
- **CORS:** Konfigurierbar
- **Audit Logging:** Alle kritischen Operationen

---

## 🧪 Testing

### Performance-Tests

```bash
# Empirische Performance-Verifizierung
python scripts/empirical_performance_test.py

# Stress-Test (optional)
python scripts/run_stress_test.py
```

### Monitoring

```bash
# Live-Monitoring mit Sentry-Integration
python scripts/implement_monitoring_alerts.py
```

---

## 📖 HAK/GAL Verfassung

Das System folgt der HAK/GAL Verfassung mit 8 Artikeln:

1. **Komplementäre Intelligenz**
2. **Gezielte Befragung**
3. **Externe Verifikation**
4. **Bewusstes Grenzüberschreiten**
5. **System-Metareflexion**
6. **Empirische Validierung** ✅
7. **Konjugierte Zustände**
8. **Protokoll zur Prinzipien-Kollision**

---

## 📞 Support & Kontakt

- **System-Logs:** `logs/`
- **Knowledge Base:** 5,914 verifizierte Fakten
- **API Status:** http://localhost:5002/health
- **Frontend:** http://localhost:8088

---

## 🏆 Credits

Entwickelt nach dem Kodex des Urahnen und der HAK/GAL Verfassung.  
Empirisch verifiziert und dokumentiert am 2025-01-03.

---

**Status: OPERATIONAL** | **Performance: VERIFIED** | **Ready: PRODUCTION**

### delegate_task mit Modell-Präfix (Kurz)
- target_agent: "DeepSeek:chat" oder "Gemini:2.5-flash"/"Gemini:2.5-pro"/"Gemini:2.0-flash-exp"
- Fallbacks: ENV/Defaults wenn kein Präfix gesetzt ist.
