---
title: "Mcp Tool Implementation Plan"
created: "2025-09-15T00:08:01.041612Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# 🛠️ MCP TOOL IMPLEMENTIERUNGS-PLAN - SCALE_TO_MILLION WRAPPER

**Dokument-ID:** HAK-GAL-TOOL-IMPL-20250829  
**Priorität:** HOCH - Sofort umsetzbar  
**Basis:** Existierende Python-Scripts  

---

## 📦 NEUE MCP TOOLS (Wrapper für existierende Scripts)

### Tool 1: `optimize_database`
```python
{
    "name": "optimize_database",
    "description": "Optimiert SQLite für 100k+ Facts (WAL, Cache, Indizes)",
    "inputSchema": {
        "type": "object",
        "properties": {
            "apply_wal": {"type": "boolean", "default": true},
            "cache_size_mb": {"type": "integer", "default": 128},
            "create_indexes": {"type": "boolean", "default": true},
            "analyze": {"type": "boolean", "default": true}
        }
    }
}

# Implementation:
elif tool_name == "optimize_database":
    import subprocess
    script_path = Path("SCALE_TO_MILLION/optimize_now.py")
    result = subprocess.run(["python", str(script_path)], 
                          capture_output=True, text=True)
    return {"status": "completed", "output": result.stdout}
```

### Tool 2: `performance_benchmark`
```python
{
    "name": "performance_benchmark",
    "description": "Testet Performance mit synthetischen Daten",
    "inputSchema": {
        "type": "object",
        "properties": {
            "test_size": {"type": "integer", "enum": [10000, 50000, 100000, 500000]},
            "test_type": {"type": "string", "enum": ["insert", "query", "full"]},
            "duration_seconds": {"type": "integer", "default": 60}
        },
        "required": ["test_size"]
    }
}

# Implementation:
elif tool_name == "performance_benchmark":
    script_path = Path("SCALE_TO_MILLION/sqlite_optimization.py")
    # Modifiziere Script-Parameter basierend auf tool_args
    # Führe aus und parse Ergebnisse
```

### Tool 3: `scale_monitor`
```python
{
    "name": "scale_monitor",
    "description": "Überwacht Performance-Metriken in Echtzeit",
    "inputSchema": {
        "type": "object",
        "properties": {
            "duration_seconds": {"type": "integer", "default": 60},
            "metrics": {
                "type": "array",
                "items": {"type": "string", "enum": ["insert_rate", "query_time", "memory", "cpu"]},
                "default": ["insert_rate", "query_time", "memory"]
            },
            "output_format": {"type": "string", "enum": ["json", "text", "chart"], "default": "json"}
        }
    }
}

# Implementation:
elif tool_name == "scale_monitor":
    # Startet monitor.py als subprocess
    # Sammelt Metriken für duration_seconds
    # Gibt strukturierte Daten zurück
```

---

## 🔧 INTEGRATION IN hak_gal_mcp_sqlite_full.py

### Schritt 1: Tool-Definitionen hinzufügen (Zeile ~600)
```python
# Nach Tool 45 (execute_code) einfügen:
# Scaling & Optimization Tools (Tools 46-48)
{
    "name": "optimize_database",
    # ... (siehe oben)
},
{
    "name": "performance_benchmark",
    # ... (siehe oben)
},
{
    "name": "scale_monitor",
    # ... (siehe oben)
}
```

### Schritt 2: Handler implementieren (Zeile ~1400)
```python
# Nach execute_code handler:
elif tool_name == "optimize_database":
    try:
        script_path = Path(__file__).parent / "SCALE_TO_MILLION" / "optimize_now.py"
        if not script_path.exists():
            return {"content": [{"type": "text", "text": "Error: optimize_now.py not found"}]}
        
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "content": [{
                "type": "text",
                "text": f"✅ Database optimized!\n{result.stdout}"
            }]
        }
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {e}"}]}
```

---

## ⏱️ ZEITAUFWAND

- **Tool-Definitionen:** 10 Minuten
- **Handler-Implementation:** 30 Minuten  
- **Testing:** 20 Minuten
- **GESAMT:** 1 Stunde

---

## 🎯 VORTEILE DIESER LÖSUNG

1. **Sofort einsatzbereit** - Scripts existieren bereits
2. **Keine Abhängigkeiten** - Nutzt vorhandene Infrastruktur
3. **Empirisch validiert** - Scripts wurden getestet
4. **Wartungsarm** - Wrapper-Pattern ist simpel
5. **Erweiterbar** - Weitere Scripts leicht integrierbar

---

## ✅ CHECKLISTE FÜR IMPLEMENTIERUNG

- [ ] Tool-Definitionen zu handle_list_tools() hinzufügen
- [ ] Handler in handle_tool_call() implementieren
- [ ] Import-Statements ergänzen (subprocess, Path)
- [ ] Error-Handling für fehlende Scripts
- [ ] Timeout-Handling für lange Benchmarks
- [ ] Test mit kleinen Datenmengen
- [ ] Test mit 100k synthetischen Facts
- [ ] Dokumentation aktualisieren
- [ ] Knowledge Base Fakten hinzufügen

---

**EMPFEHLUNG:** Diese 3 Tools lösen AKUTE Bedürfnisse und nutzen EXISTIERENDE, GETESTETE Infrastruktur!