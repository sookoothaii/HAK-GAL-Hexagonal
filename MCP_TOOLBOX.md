# HAK-GAL MCP Toolbox – Bedienung, Setup, Troubleshooting

Dieses Dokument beschreibt die komplette MCP-Integration der HAK‑GAL Hexagonal Suite, inkl. Installation, Konfiguration, verfügbaren Tools, Sicherheit, Tests und Fehlersuche.

## Inhalt
- Überblick
- Schnellstart (Claude Desktop)
- Konfiguration (claude_desktop_config.json)
- Sicherheit (Write‑Access, Token, Audit)
- Verfügbare Tools (Parameter, Beispiele)
- Tests und Verifikation
- Logs und Fehlersuche
- Wartung und bekannte Stolpersteine
- Änderungsverlauf (Kurz)

---

## Project Hub (Initialinfo/Session‑Handover)

Ziel: Persistenter, wachsender Projektkontext über Sessions hinweg. Am Ende einer Session wird ein Snapshot abgelegt; zu Beginn einer neuen Session lädt Claude automatisch eine kompakte Zusammenfassung (Digest) aus dem Hub.

Empfohlener Hub‑Ordner
- `D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB`

Tools (3 Projekt-Hub Tools)
- `project_snapshot(title?, description?, hub_path, auth_token)`
  - Legt `snapshot_YYYYMMDD_HHMMSS/` an mit `SNAPSHOT.md` (menschlich) und `snapshot.json` (strukturiert)
  - Inhalt: Health, KB‑Statistiken, Top‑Prädikate, letzte Audit‑Einträge
- `project_list_snapshots(hub_path, limit=20)`
  - Listet neueste Snapshot‑Ordner
- `project_hub_digest(hub_path, limit_files=3, max_chars=20000)`
  - Aggregiert die letzten Snapshots zu einer kompakten Initialinfo (ideal als Einstiegsnachricht)

Empfohlener Workflow
- Session‑Ende (Handover erzeugen):
  - In Claude: „Use hak-gal project_snapshot with title='Handover' and description='…' and hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB' and auth_token='<TOKEN>'.”
- Neue Session (Initialinfo laden):
  - In Claude: „Use hak-gal project_hub_digest with hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB' and limit_files=3.”
  - Ausgabe dient als sofortiger System‑/Projektkontext (Initialinfo) ohne erneutes Erklären

Hinweise
- Für automatisches Schreiben ist `HAKGAL_WRITE_ENABLED=true` (und ggf. `HAKGAL_WRITE_TOKEN`) nötig
- Snapshots sind reine Dateien im Hub; sie können versioniert, geteilt oder archiviert werden
- Digest ist beschränkt über `max_chars` und für schnelle Aufnahme optimiert

---

## Überblick
- MCP‑Server: `hak_gal_mcp_fixed.py` (STDIO, JSON‑RPC, protocolVersion "2025-06-18")
- Venv: `D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe`
- Wissensbasis: `D:\MCP Mods\HAK_GAL_HEXAGONAL\data\k_assistant.kb.jsonl`
- Audit‑Log (Writes): `D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_write_audit.log`
- Server‑Log: `D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_server.log`
- Claude‑Logs: `%APPDATA%\Claude\logs\mcp.log`

---

## Schnellstart (Claude Desktop)
1) Config setzen (automatisch):
   - Skript: `install_mcp_config.py` ausführen
   - Ergebnis: Eintrag `hak-gal` wird erstellt/aktualisiert
2) Claude Desktop komplett beenden und neu starten
3) In Claude testen:
   - „What MCP tools do you have?“
   - „Use hak-gal search_knowledge with query='Kant' and limit=3.“

---

## Konfiguration (claude_desktop_config.json)
Datei: `%APPDATA%\Claude\claude_desktop_config.json`

Wichtige Felder (Beispiel – wird vom Installer gesetzt):
```json
{
  "mcpServers": {
    "hak-gal": {
      "command": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\.venv_hexa\\Scripts\\python.exe",
      "args": ["-u", "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_fixed.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL",
        "HAKGAL_WRITE_ENABLED": "true",
        "HAKGAL_WRITE_TOKEN": "<DEIN_TOKEN>"
      }
    }
  }
}
```

Hinweise:
- `command` MUSS ein String sein; `args` ist ein Array.
- Verwende das venv‑Python, nicht MSYS/CygWin/Global‑Python.
- `-u` erzwingt unbuffered STDIO (wichtig für MCP‑STDIO).

---

## Sicherheit (Write‑Access, Token, Audit)
- Schreiboperationen (add/update/delete/bulk_delete) sind standardmäßig deaktiviert.
- Aktivierung über Umgebungsvariable `HAKGAL_WRITE_ENABLED=true`.
- Optionaler Schutz via `HAKGAL_WRITE_TOKEN` (muss beim Tool‑Aufruf als `auth_token` mitgegeben werden).
- Alle Schreibvorgänge werden nach `mcp_write_audit.log` protokolliert (JSON pro Zeile).
- Dateilock (`*.lock`) sorgt für atomare Writes.

---

## Verfügbare Tools (29 Tools insgesamt)

### Übersicht
- **Basis-Tools:** 7
- **Analyse-Tools:** 8
- **Verwaltungs-Tools:** 7
- **Erweiterte Tools:** 4
- **Projekt-Hub Tools:** 3
- **GESAMT:** 29 MCP-Tools (empirisch verifiziert am 2025-08-13)

### Detaillierte Auflistung

Basis
- search_knowledge
  - params: `query` (string), `limit` (int, default 10)
  - Beispiel: „Use hak-gal search_knowledge with query='Kant' and limit=3.“
- get_system_status
  - params: –
- list_recent_facts
  - params: `count` (int, default 5)

CRUD
- add_fact
  - params: `statement` (string, required), `source` (string), `tags` (string[]), `auth_token` (string)
- update_fact
  - params: `old_statement` (string), `new_statement` (string), `auth_token` (string)
- delete_fact
  - params: `statement` (string), `auth_token` (string)
- bulk_delete
  - params: `statements` (string[]), `auth_token` (string)

Monitoring/Utility
- kb_stats
  - params: –
- list_audit
  - params: `limit` (int, default 20)
- export_facts
  - params: `count` (int, default 50), `direction` ("tail"|"head")

Analyse (8 Tools)
- semantic_similarity
  - params: `statement` (string), `threshold` (float, default 0.8), `limit` (int, default 50)
- consistency_check
  - params: `limit` (int, default 1000)
- validate_facts
  - params: `limit` (int, default 1000)
- get_entities_stats
  - params: `min_occurrences` (int, default 2)
- search_by_predicate
  - params: `predicate` (string), `limit` (int, default 100)
- get_predicates_stats
  - params: –
- query_related
  - params: `entity` (string), `limit` (int, default 100)
- analyze_duplicates
  - params: `threshold` (float, default 0.9), `max_pairs` (int, default 200)

Erweiterte Tools (4 Tools)
- find_isolated_facts
  - params: `limit` (int, default 50)
- inference_chain
  - params: `start_fact` (string), `max_depth` (int, default 5)
- get_knowledge_graph
  - params: `entity` (string), `depth` (int, default 2), `format` ("json"|"dot")
- get_fact_history
  - params: `statement` (string), `limit` (int, default 50)

Verwaltung/Backup (7 Tools)
- backup_kb
  - params: `description` (string), `auth_token` (string)
- restore_kb
  - params: `backup_id` (string) oder `path` (string), `auth_token` (string)
- growth_stats
  - params: `days` (int, default 30)
- health_check
  - params: –

---

## Tests und Verifikation
- Lokale Tests (optional): `py -3 D:\MCP Mods\HAK_GAL_HEXAGONAL\test_mcp_v2.py`
- Claude‑Flow (typisch): initialize → tools/list → tools/call
- Erfolgskriterien:
  - `mcp.log` zeigt `[hak-gal]` initialize, tools/list, Tool‑Antworten
  - Keine „Server transport closed unexpectedly“ nach initialize

---

## Logs und Fehlersuche
- Orchestrierung: `%APPDATA%\Claude\logs\mcp.log`
- HAK‑GAL Server: `D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_server.log`
- Audit (Writes): `D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_write_audit.log`

Typische Probleme & Lösungen
- Falscher Interpreter (msys/cygwin): Auf venv‑Python pinnen (siehe Config oben).
- `command` als Array: Claude erwartet String → korrigieren.
- Kein Output/Timeout: `-u` sicherstellen; Logging auf stderr (stdout bleibt JSON‑RPC).
- Windows‑MCP „spawn uv ENOENT“: optional `uv` installieren (hat keinen Einfluss auf HAK‑GAL).

---

## Wartung
- Config skriptgesteuert aktualisieren: `install_mcp_config.py`
- Backup/Restore der KB (empfohlen, noch optional als MCP‑Tools auszubauen)
- Versionsupdate der Toolbox: Server neu starten und `mcp.log` prüfen

---

## Änderungsverlauf
- **2025-08-13:** Dokumentation auf 29 Tools korrigiert (empirisch verifiziert)
- MCP‑Handshake korrigiert (`server/ready`, `protocolVersion`) und STDIO gehärtet
- Alle 29 Tools implementiert und getestet:
  - 7 Basis-Tools
  - 8 Analyse-Tools  
  - 7 Verwaltungs-Tools
  - 4 Erweiterte Tools
  - 3 Projekt-Hub Tools
- Schreibschutz via ENV + Token, Locking + Audit
- Config‑Installer und venv‑Pinning
- Vollständige Dokumentation in MCP_TOOLS_COMPLETE.md

---

**Status:** Alle 29 Tools sind implementiert, getestet und dokumentiert. Siehe MCP_TOOLS_COMPLETE.md für detaillierte Referenz.


