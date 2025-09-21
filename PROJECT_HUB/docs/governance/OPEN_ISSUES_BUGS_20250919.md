---
title: "Open Issues & Known Bugs - Post Migration Status"
created: "2025-09-19T23:55:00Z"
author: "claude-opus-4.1"
topics: ["governance", "issues", "bugs"]
tags: ["duplicate-facts", "sentry-config", "cache-issues", "todo"]
privacy: "internal"
summary_200: |-
  Dokumentation offener Issues nach N-ärer Migration. Hauptprobleme: Duplicate 
  TemplateLearningSystem Facts in KB, Sentry DSN Configuration invalid, Python 
  Cache blockiert Updates ohne manuelles Löschen. Minor Issues: Zähldiskrepanz 
  zwischen Agenten (Sonnet meldet 12, tatsächlich 15), generische Facts ohne 
  Mehrwert. Performance OK aber Skalierung bei 1000+ Facts unklar. Alle Issues 
  haben Workarounds, keine sind kritisch für Betrieb.
rationale: "Issue tracking required for system maintenance and handover"
---

# OPEN ISSUES & KNOWN BUGS
**Stand:** 2025-09-19 23:55 UTC  
**Severity Levels:** 🔴 Critical | 🟡 Major | 🟢 Minor  
**System Impact:** Operational (keine kritischen Blockierungen)

---

## 1. DATABASE ISSUES

### 1.1 Duplicate Facts 🟡
**Issue:** TemplateLearningSystem existiert 2x in Knowledge Base
```sql
-- Beide Versionen:
TemplateLearningSystem(...) -- ohne activation_date
TemplateLearningSystem(..., activation_date:2025-09-19) -- mit date
```

**Impact:** 
- Verwirrung bei Queries
- Inkonsistente Zählungen
- Speicherplatz-Verschwendung

**Workaround:**
```python
# Find duplicates
hak-gal:analyze_duplicates(threshold=0.95, max_pairs=100)
```

**Fix Required:**
```sql
DELETE FROM facts 
WHERE statement LIKE 'TemplateLearningSystem%' 
AND created_at < '2025-09-19'
```

### 1.2 Fact Count Diskrepanz 🟢
**Issue:** Agenten melden unterschiedliche Zahlen
- Opus 4.1: +94 Facts added
- Sonnet 4: +12 Facts added  
- Tatsächlich: +15 seit Sonnet

**Impact:** Minimal (nur Reporting-Problem)

**Root Cause:** Möglicherweise parallele Processes oder Zählfehler

---

## 2. CONFIGURATION ISSUES

### 2.1 Sentry DSN Invalid 🟢
**Issue:** Sentry Error Tracking nicht funktional
```python
SENTRY_DSN = "https://invalid@sentry.io/project"  # Invalid
```

**Impact:** 
- Keine automatische Fehlererfassung
- Keine Performance-Metriken an Sentry

**Workaround:** 
- Logging funktioniert lokal
- Errors in engine_logs/ sichtbar

**Fix:** Neuen DSN von Sentry.io generieren oder deaktivieren

### 2.2 Python Cache Persistence 🟡
**Issue:** `__pycache__` Directories blockieren Code-Updates

**Impact:**
- Änderungen werden nicht übernommen
- Tool-Reparaturen greifen nicht
- Verwirrende Debug-Sessions

**Current Workaround:**
```powershell
# Muss manuell nach jeder Code-Änderung ausgeführt werden
Get-ChildItem -Path "." -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force
```

**Permanent Fix Needed:** 
- Auto-clear bei Server-Start
- Oder Python mit `-B` Flag starten

---

## 3. TOOL ISSUES

### 3.1 Handler Inkonsistenz 🟡
**Issue:** Manche Tools nutzen `tool_name ==`, andere `name ==`

**Status:** 
- ✅ BEHOBEN für semantic_similarity
- ✅ BEHOBEN für consistency_check  
- ❓ Andere Tools nicht überprüft

**Potential Impact:** Weitere Tools könnten still fehlschlagen

**Action Required:**
```python
# Audit all handlers
grep -n "elif.*name.*==" hakgal_mcp_ultimate.py
grep -n "elif.*tool_name.*==" hakgal_mcp_ultimate.py
```

---

## 4. PERFORMANCE CONCERNS

### 4.1 Skalierung bei 1000+ Facts 🟢
**Issue:** Performance bei großen Fact-Mengen ungetestet

**Current Stats:**
- 455 Facts: <100ms Response ✅
- 1000 Facts: Unknown
- 10000 Facts: Unknown

**Concerns:**
- Semantic similarity O(n²) Komplexität
- Memory Usage könnte explodieren
- SQLite Limits?

**Testing Required:**
```python
# Stress test with generated facts
for i in range(1000):
    hak-gal:add_fact(f"TestFact_{i}(arg1, arg2, arg3)")
```

### 4.2 WebSocket Stability 🟢
**Issue:** WebSocket Connection nicht validiert

**Claimed:** Enabled and functional
**Verified:** Nein

**Test Required:**
```javascript
// Frontend test
const ws = new WebSocket('ws://localhost:5002/socket.io/');
ws.onmessage = (e) => console.log(e.data);
```

---

## 5. DOCUMENTATION GAPS

### 5.1 Generische Facts 🟢
**Issue:** Einige Facts zu allgemein
```
ScientificDomainCoverage(..., domains:7)  # Welche 7?
```

**Impact:** Wenig Nutzwert für Automation

**Fix:** Spezifischere Facts mit Details

### 5.2 Installation Guide Fehlt 🟡
**Issue:** Trotz 95% Automation keine Step-by-Step Anleitung

**Impact:** Neue User wissen nicht wo anfangen

**Required Document:**
- INSTALLATION_GUIDE.md
- Mit Facts-basierten Schritten
- Fallback für manuelle Installation

---

## 6. MULTI-AGENT ISSUES

### 6.1 Keine Agent-Koordination Protokolle 🟢
**Issue:** Agenten arbeiten unkoordiniert

**Example:** Opus und Sonnet injizierten möglicherweise Duplikate

**Solution Needed:**
- Agent-Lock Mechanismus
- Oder Transaction-basierte Injection

---

## 7. SECURITY CONCERNS

### 7.1 Auth Token Hardcoded 🟡
**Issue:** Token `515f57956e7bd15ddc3817573598f190` überall sichtbar

**Risk:** 
- Keine Rotation möglich
- In Git History forever

**Mitigation:**
- Environment Variable nutzen
- Token Rotation implementieren

---

## 8. PRIORITY MATRIX

### Sofort (Next Session)
1. 🟡 Duplicate Facts bereinigen
2. 🟡 Python Cache Auto-Clear
3. 🟡 Installation Guide schreiben

### Kurzfristig (This Week)  
4. 🟡 Handler Audit durchführen
5. 🟢 WebSocket Tests
6. 🟢 Sentry konfigurieren

### Mittelfristig (This Month)
7. 🟢 Performance Tests 1000+ Facts
8. 🟢 Agent Koordination
9. 🟡 Security Review

---

## 9. WORKAROUND SUMMARY

Alle Issues haben funktionsfähige Workarounds:
- **Duplicates:** Ignorieren oder manuell löschen
- **Cache:** Manuell clearen nach Changes
- **Sentry:** Lokale Logs nutzen
- **Performance:** Unter 500 Facts bleiben

**System bleibt voll operational trotz dieser Issues.**

---

**Dokument erstellt für Transparenz und Handover.**  
**Keine Issues blockieren aktuell die Kernfunktionalität.**