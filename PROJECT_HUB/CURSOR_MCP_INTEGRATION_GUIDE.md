# Cursor + HAK-GAL MCP Integration Guide (Port 5001)

Status: Ready • Server läuft lokal via `.venv_hexa` • Pure Hexagonal Backend

## Voraussetzungen
- Backend (Flask) läuft auf `http://127.0.0.1:5001`
- MCP Server gestartet: `.\.venv_hexa\Scripts\python.exe -m hak_gal_mcp`
- Cursor nutzt `.cursor/mcp.json` (bereits angelegt)

## In Cursor nutzen
1) Projekt `HAK_GAL_HEXAGONAL` öffnen
2) Cursor neu laden (damit `.cursor/mcp.json` erkannt wird)
3) MCP-Seitenleiste öffnen → Server „HAK_GAL MCP“ auswählen
4) Tools stehen bereit (30 Stück), z.B. `kb_stats`, `project_snapshot`, `add_fact`

## Quick Actions (empfohlen)
- Systemstatus prüfen:
  - `health_check`
  - `kb_stats` (zeigt Count/Größe/Zeitstempel)
- Snapshot erstellen:
  - `project_snapshot` → legt Verzeichnis `PROJECT_HUB/snapshot_YYYYMMDD_HHMMSS/` an
- Faktenpflege:
  - `add_fact` → `Predicate(Entity1, Entity2).`
  - `delete_fact` / `update_fact`
- Analyse:
  - `consistency_check`
  - `validate_facts`
  - `semantic_similarity`
- Projekt-Hub:
  - `list_snapshots`, `digest`

## Beispiel-Workflows
### 1) Täglicher Snapshot
1. `kb_stats` ausführen (Zahlen notieren)
2. `project_snapshot` (Titel/Descr.)
3. `digest` (Kurzbericht in Snapshot ablegen)

### 2) Kuratierter Import
1. `validate_facts` auf Liste anwenden
2. `add_fact` in Bulk (small batches)
3. `consistency_check` und `kb_stats`

### 3) Untersuchung Diskrepanz
1. `kb_stats` (Live)
2. Frontend: `/knowledge/stats` prüfen
3. Export: `/api/facts/export?limit=100&format=jsonl`
4. `project_snapshot` + Notiz im Hub

## Troubleshooting
- MCP nicht sichtbar: Cursor neu starten, Projekt-Root offen, `.cursor/mcp.json` vorhanden
- Serverport falsch: `.cursor/mcp.json` → `HAKGAL_API_BASE_URL`
- Rechte/Schreiben blockiert: Kill-Switch prüfen `/api/killswitch/status`

## Sicherheit & Governance
- Schreib-Tools sind write-gated (ENV)
- Audit-Log aktiv (Schreiboperationen)
- Lokaler Betrieb (keine externen Keys notwendig)

## Nächste Schritte (optional)
- ENV Keys für LLMs in `.env` setzen (nur wenn benötigt)
- OpenAPI/Swagger veröffentlichen
- Docker-Profil für MCP + Backend

—
Version: 2025-08-14 • Maintainer: GPT‑5
