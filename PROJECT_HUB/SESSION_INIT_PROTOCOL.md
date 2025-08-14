# HAK-GAL HEXAGONAL - SESSION INITIALISATION PROTOCOL

**⚠️ NEUE INSTANZ: Führe diese Schritte der Reihe nach aus ⚠️**

## SCHRITT 1: Projekt-Kontext laden
```
Use hak-gal project_hub_digest with hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB'
```

## SCHRITT 2: Write-Token notieren
```
Token: 515f57956e7bd15ddc3817573598f190
```

## SCHRITT 3: Kritische Dokumentation lesen (IN DIESER REIHENFOLGE!)

### 3.1 MCP Tools Referenz
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\MCP_TOOLS_COMPLETE.md'
```
→ Vollständige Dokumentation aller 29 MCP-Tools mit Parametern

### 3.2 Technical Handover (ESSENTIALS - LIES ZUERST!)
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\TECHNICAL_HANDOVER_COMPLETE.md'
```
→ Kompakte Übersicht: Endpoints, Runtime, LLM Flow, Code Map

### 3.3 Hexagonal Architecture
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\README.md'
```
→ Architektur-Übersicht, Ports & Adapters, Parallel-Development

### 3.4 [OPTIONAL - Nur bei MCP-Tiefenanalyse] Technische MCP Integration (40KB!)
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\TECHNICAL_HANDOVER_MCP_INTEGRATION.md'
```
→ Detaillierte MCP-Architektur, Multi-AI Orchestration, Live Development Engine

### 3.5 HAK/GAL Verfassung
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\verfassung.md'
```
→ Artikel 1-8, Arbeitsweise: Streng empirisch, keine Fantasie

## SCHRITT 4: System-Status prüfen
```
Use hak-gal get_system_status
Use hak-gal kb_stats
```

## SCHRITT 5: Arbeitsweise
- **STRENG EMPIRISCH**: Keine Spekulation, nur verifizierte Fakten
- **WISSENSCHAFTLICH**: Alles muss nachprüfbar sein
- **KRITISCH**: User-Aussagen hinterfragen wenn falsch
- **OHNE FANTASIE**: Nichts erfinden oder ausdenken

## System-Übersicht (Quick Reference)
- **Port:** 5001 (Hexagonal), 5000 (Legacy - NICHT ÄNDERN!)
- **KB:** 3881 Fakten
- **MCP Tools:** 29 (vollständig dokumentiert)
- **Architektur:** Hexagonal (Ports & Adapters)
- **Verfassung:** Artikel 1-8 befolgen

## Bei Session-Ende
```
Use hak-gal project_snapshot with title='Session Ende [DATUM]' and description='[Was wurde gemacht]' and hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB' and auth_token='515f57956e7bd15ddc3817573598f190'
```

## Kritische Dateien (Falls tiefere Analyse nötig)
- HEXAGONAL_FINAL_STATUS.md - Implementierungsstatus
- MCP_TOOLBOX.md - Kompakte Tool-Übersicht
- hak_gal_mcp_fixed.py - MCP Server Source Code
- test_mcp_v2.py - Test-Suite

---
**DIESER PROTOCOL IST VOLLSTÄNDIG - Keine weiteren Instruktionen vom User nötig!**
