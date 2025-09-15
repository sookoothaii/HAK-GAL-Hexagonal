---
title: "Architecture Overview"
created: "2025-09-15T00:08:00.978851Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK‑GAL Hexagonal Suite – Architekturüberblick (Initialinfo)

Dieser Leitfaden bündelt den Kernkontext zur HAK‑GAL Hexagonal Suite. Er dient als Startpunkt für neue Sessions und als Anker für den Project‑Hub. Aktualisiere diesen Text bei wesentlichen Architekturänderungen.

## 1) Zielbild
- Saubere Hexagonal‑Architektur (Ports & Adapters): Domänenlogik entkoppelt von Frameworks/Transport.
- Autonomer Betrieb (Port 5001), LLM‑Anbindung über MCP, sichere Write‑Operationen mit Audit & Locking.
- Reproduzierbare Abläufe: klare Endpunkte, stabile MCP‑Toolbox, Project‑Hub für Session‑Handover.

## 2) Verzeichnisstruktur (vereinfacht)
- `src_hexagonal/` – Kern der Applikation (Domäne, Use‑Cases, Ports)
- `infrastructure/` – Adapter/Implementierungen (Persistence, HTTP, MCP etc.)
- `scripts/` – Hilfs‑/Installationsskripte (z. B. Claude‑Config)
- `data/` – Wissensbasis (JSONL: eine Zeile = ein Fakt)
- `PROJECT_HUB/` – Snapshots (Handover KB/Tech, Manifeste, Diffs)

Typische Dateien:
- `src_hexagonal/hexagonal_api_enhanced.py` – zentraler (erweiterter) API‑Layer (Use‑Cases/Ports gebündelt)
- `hak_gal_mcp_fixed.py` – MCP‑Server (STDIO, JSON‑RPC, 29+ Tools)
- `install_mcp_config.py` – setzt die Claude‑Desktop‑Konfiguration
- `MCP_TOOLBOX.md` – Bedienung & Troubleshooting für MCP‑Toolbox

## 3) Hexagonal – Prinzipien
- Domäne spricht in Ports (Interfaces): Use‑Cases definieren Eingänge/Ausgänge.
- Adapter implementieren Ports: HTTP, Files, MCP, Persistenz.
- Frameworks/Transport sind austauschbar; Tests konzentrieren sich auf Use‑Cases.

Vorteile:
- Testbarkeit: Domäne ohne Infrastruktur testen.
- Evolvierbarkeit: neue Adapter ohne Änderung in der Domäne.
- Sicherheit: Policy/Guards an Ports bündelbar.

## 4) Laufzeit & Endpunkte
- HTTP/REST (Port 5001): Health, Facts‑Endpoints, Analysefunktionen, evtl. Socket.IO.
- MCP (STDIO via `hak_gal_mcp_fixed.py`): 29+ Tools (CRUD, Analyse, Graph, Project‑Hub …)
- Wissensbasis: `data/k_assistant.kb.jsonl` – JSON pro Zeile, Feld `statement` im Prädikat‑Format.

## 5) MCP‑Integration (Kurz)
- Protokoll: JSON‑RPC (protocolVersion: "2025-06-18"), `server/ready` → `initialize` → `tools/*`.
- Tools: u. a. `search_knowledge`, `add_fact`, `backup_kb`, `get_knowledge_graph`, `project_snapshot`.
- Write‑Sicherheit: `HAKGAL_WRITE_ENABLED=true`, optional `HAKGAL_WRITE_TOKEN` (ENV). Lock‑Datei + Audit.
- Project‑Hub: Snapshots erzeugen (`SNAPSHOT_TECH.md`, `SNAPSHOT_KB.md`, Manifest/Diff) und per Digest laden.

## 6) Datenflüsse (vereinfacht)
- Read: MCP/HTTP → Use‑Case → Datei (KB) → Antwort.
- Write: MCP → Guard (ENV/Token) → Lock → Datei‑Append/Rewrite → Audit.
- Snapshot: Sammeln von Health/Stats/Audit + Projekt‑Manifest (SHA256), Diff vs. vorherigem Snapshot.

## 7) Konfiguration (wichtigste ENV)
- `HAKGAL_WRITE_ENABLED` (true|false) – Enable Writes
- `HAKGAL_WRITE_TOKEN` – Token für Write‑Tools
- `HAKGAL_HUB_PATH` – Default‑Ordner für Project‑Hub
- `PYTHONIOENCODING` – auf `utf-8`

In Claude‑Desktop (`claude_desktop_config.json`) werden diese unter `mcpServers.hak-gal.env` gesetzt.

## 8) Qualitätsmechanismen
- `validate_facts` – Syntaxcheck (Prädikat(Argumente))
- `analyze_duplicates` / `semantic_similarity` – Duplikate/Ähnlichkeiten
- `consistency_check` – einfache Widerspruchserkennung (`Nicht…` vs. positiv)
- `backup_kb`/`restore_kb` – Sicherung/Wiederherstellung
- `kb_stats`, `growth_stats`, `health_check` – Monitoring

## 9) Project‑Hub – Handover‑Artefakte
Jeder Snapshot erzeugt:
- `SNAPSHOT_TECH.md` – Architekturtrees pro Kernordner, Manifest (SHA256), Diff Added/Removed/Changed
- `SNAPSHOT_KB.md` – Health (Zeilen/Größe/Pfad), Top‑Prädikate, Audit‑Ausschnitte
- `snapshot_kb.json` – strukturierte KB‑Kennzahlen
- `manifest.json` – Datei‑Hashes/Metadaten für Diffs

Ablauf:
- Ende: `project_snapshot(...)`
- Start: `project_hub_digest(...)`

## 10) Entwicklungsrichtlinien (Kurz)
- Domäne zuerst: Ports/Use‑Cases klar halten.
- Adapter minimal koppeln, keine Domänenlogik dort.
- Schreiboperationen immer auditieren; Locking respektieren.
- Große Änderungen: neuen Snapshot erstellen.

## 11) Nächste sinnvolle Schritte
- Validiertere Parser/Prädikatsgrammatik (robustere `statement`‑Analyse)
- Tiefere Konsistenzregeln (Kontraindikatoren, temporale Logik)
- Automatisierte Snapshots bei Release‑Tags

Stand: Initialinfo für den Project‑Hub (manuell pflegbar).
