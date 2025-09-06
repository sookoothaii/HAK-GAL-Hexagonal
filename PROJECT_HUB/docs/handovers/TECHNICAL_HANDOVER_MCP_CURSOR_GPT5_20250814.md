### Technisches Handover: Cursor ↔ HAK‑GAL MCP Integration (gelöst)

Autor: GPT‑5 • Datum: 2025‑08‑14

---

### 1) Ziel und Kontext
Dieses Handover beschreibt die zuvor aufgetretenen Integrationsprobleme zwischen dem Cursor‑IDE MCP‑Panel und dem HAK‑GAL MCP‑Server sowie die final umgesetzte, validierte Lösung. Fokus: reproduzierbare Einrichtung in Cursor, sichere Schreibfreigabe (Write‑Gate) mit Token, vollständige Tool‑Validierung (30 Tools), und Betriebsempfehlungen.

---

### 2) Ausgangslage und Symptome
- 30 Tools wurden im Cursor sichtbar, dennoch scheiterten Schreib‑Operationen (add/update/delete) an einem deaktivierten Write‑Gate.
- Teilweise wurde versucht, Backend‑HTTP‑Endpunkte direkt per PowerShell zu testen; das ist nicht erforderlich, wenn die MCP‑Tools genutzt werden sollen (und führte u. a. zu „Method Not Allowed“/Alias‑Verwechslungen von `curl`).
- Versuche, Umgebungsvariablen per Einzeiler in PowerShell zu setzen, produzierten Parser‑Fehler („=true nicht erkannt“) – Ursache: falsche Syntax und Quoting.

---

### 3) Root Causes
- MCP‑Server Start in Cursor ohne notwendige ENV‑Variablen für Schreibrechte: `HAKGAL_WRITE_ENABLED`, `HAKGAL_WRITE_TOKEN`, `PYTHONIOENCODING`, `HAKGAL_HUB_PATH`.
- Missverständnis: Write‑Gate ist absichtlich standardmäßig geschlossen; ohne explizites Enablen und ggf. Token werden MCP‑Schreibtools geblockt.
- Manuelle PowerShell‑Starts in fremder Arbeitsumgebung führten zu fehlerhaften ENV‑Assignments (Quoting/`$env:`‑Syntax).

---

### 4) Finaler Fix (Cursor‑seitig)
In `HAK_GAL_HEXAGONAL/.cursor/mcp.json` wurden die ENV‑Variablen ergänzt, sodass Cursor den MCP‑Server korrekt mit Konfiguration starten kann. Beispiel‑Konfiguration (Lesebetrieb, Write‑Gate zu):

```json
{
  "mcpServers": {
    "hak_gal_hexagonal": {
      "command": ".\\.venv_hexa\\Scripts\\python.exe",
      "args": ["-m", "hak_gal_mcp"],
      "env": {
        "HAKGAL_API_BASE_URL": "http://127.0.0.1:5001",
        "PYTHONUNBUFFERED": "1",
        "HAKGAL_WRITE_ENABLED": "false",
        "HAKGAL_WRITE_TOKEN": "",
        "HAKGAL_HUB_PATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB",
        "PYTHONIOENCODING": "utf-8"
      },
      "disabled": false
    }
  }
}
```

Aktivieren von Writes (nur temporär, z. B. für Migrationen/Tests):
- `HAKGAL_WRITE_ENABLED`: "true"
- `HAKGAL_WRITE_TOKEN`: auf den gültigen Token setzen (bereitgestellt vom Betreiber)
- Nach Änderung: Cursor „Reload Window“ und MCP‑Tools Panel prüfen.

Sicherheitsrückstellung nach Test: Write‑Gate wieder auf `false`, Token leeren, Reload.

---

### 5) Architekturhinweis (MCP ↔ Backend)
- MCP‑Server: `HAK_GAL_HEXAGONAL/hak_gal_mcp_fixed.py`
- Primäre KB für MCP‑Lesefunktionen: JSONL unter `data/k_assistant.kb.jsonl` (schnelle sequentielle Operationen)
- Schreibfunktionen in MCP (add/update/delete) rufen intern die Hexagonal‑API (Port 5001) auf und schreiben damit in SQLite (Source of Truth). Audit‑Spuren schreibt MCP lokal in `mcp_write_audit.log`.
- Relevante ENV:
  - `HAKGAL_API_BASE_URL` (z. B. `http://127.0.0.1:5001`)
  - `HAKGAL_WRITE_ENABLED` (Write‑Gate)
  - `HAKGAL_WRITE_TOKEN` (optional: Tokenpflicht)
  - `HAKGAL_HUB_PATH` (Snapshots/Reports)
  - `PYTHONIOENCODING` (UTF‑8 Stabilität)

---

### 6) Verifikation (empirisch durchgeführt)
Status vor Write‑Test:
- Tools sichtbar: 30
- `health_check`: OK, `write_enabled: False`
- `kb_stats`: 3.776 Zeilen, Größe 354.607 Bytes

Write‑Smoke‑Test (nur MCP‑Tools; Write‑Gate temporär auf „true“ + Token):
- `add_fact`: `TestFact(MCP_WriteTest, Run1).` → OK (SQLite Append via API)
- `update_fact`: → `TestFact(MCP_WriteTest, Updated).` → OK (updated=1)
- `delete_fact`: Run1 → removed 0; Updated → removed 1 → OK
- `list_audit`: Einträge vorhanden (add → update → delete) mit Zeitstempeln

Sicherheitsrückstellung nach Test:
- Write‑Gate wieder `false`, Token aus `.cursor/mcp.json` entfernt.
- `health_check`: write_enabled: False

---

### 7) Bedienung in Cursor (Kurz‑Runbook)
1. Tools‑Panel anzeigen: Strg+Shift+P → „Reload Window“; Strg+, → nach „MCP“ suchen → Tools Panel aktivieren; links auf „Tools/MCP“ klicken.
2. Verbindung prüfen:
   - `health_check` (erwartet: OK, Lines/Size, write_enabled)
   - `kb_stats` (erwartet: Count/Size/mtime)
3. Lesen (Smoke): `search_knowledge`, `get_predicates_stats`, `get_system_status`, `project_list_snapshots`, `project_hub_digest`.
4. Schreiben (temporär, nur wenn freigegeben): `add_fact` → `update_fact` → `delete_fact`.
5. Nach Schreibvorgängen: Write‑Gate wieder schließen (ENV zurücksetzen, Reload).

---

### 8) Häufige Fehler und Abhilfe
- PowerShell setzt ENV‑Variablen nicht korrekt: In Cursor unnötig; Konfiguration erfolgt in `.cursor/mcp.json`. Falls manuell nötig: `$env:NAME='wert'` Syntax verwenden.
- `curl` in PowerShell ist Alias für `Invoke-WebRequest`: Kann zu „Method Not Allowed“ führen. Für MCP‑Tests ausschließlich Tools im Cursor nutzen.
- Panel nicht sichtbar / keine Verbindung: „Reload Window“, MCP‑Panel aktivieren, Logs im Terminal prüfen (Server sendet `server/ready`).
- Schreibversuch geblockt: `health_check` prüfen → `write_enabled: False`; ENV anpassen, Reload.

---

### 9) Sicherheitsrichtlinie (Write‑Gate)
- Standard: Write‑Gate zu (`HAKGAL_WRITE_ENABLED=false`).
- Temporäres Enablen nur für geplante Operationen, mit explizitem Token.
- Nach Abschluss unmittelbar Disable + Token entfernen.
- Audit trail: `mcp_write_audit.log` wird fortgeschrieben (Nachvollziehbarkeit).

---

### 10) Akzeptanzkriterien (erfüllt)
- 30 MCP‑Tools in Cursor sichtbar und ausführbar.
- Read‑Tools: erfolgreich validiert (Health, Stats, Suche, Graph, Export, Snapshots).
- Write‑Tools: erfolgreich validiert (add/update/delete) mit anschließendem Clean‑up.
- Sicherheitszustand danach wieder hergestellt (Write‑Gate zu, Token entfernt).

---

### 11) Wartungsempfehlungen
- Regel: Nur MCP‑Tools im Cursor verwenden (keine gemischten direkten HTTP‑Tests nötig).
- Regelmäßiger Snapshot über MCP‑Tool `project_snapshot` (wenn Write‑Gate temporär offen) oder nur `project_list_snapshots`/`project_hub_digest` lesen.
- Tokenverwaltung: pro Session/Benutzer; keine langfristige Ablage im Repo.
- Optional: Separaten, kurzlebigen „Session‑Token“ etablieren; Automatisierung eines „Write‑Toggle“-Tools in MCP erwägen.

---

### 12) Aktueller Systemstand (empirisch)
- Architektur: Pure Hexagonal (Port 5001)
- MCP‑Server: operational, Tools: 30
- KB (JSONL, lesend): 3.776 Zeilen
- SQLite: Source of Truth für Schreib‑Operationen (über Hexagonal API)
- Write‑Gate aktuell: geschlossen

---

### 13) Anhänge / Referenzen
- Konfig: `HAK_GAL_HEXAGONAL/.cursor/mcp.json`
- Server: `HAK_GAL_HEXAGONAL/hak_gal_mcp_fixed.py`
- KB (JSONL): `HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl`
- Audit: `HAK_GAL_HEXAGONAL/mcp_write_audit.log`
- Hub: `HAK_GAL_HEXAGONAL/PROJECT_HUB/`


