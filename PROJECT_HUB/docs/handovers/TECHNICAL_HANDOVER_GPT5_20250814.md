---
title: "Technical Handover Gpt5 20250814"
created: "2025-09-15T00:08:01.029079Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

## Technical Handover – HEXAGONAL Migration (GPT-5) – 2025-08-14

### Ziel und Umfang
- Ziel: Vollständige Entkopplung vom Legacy‑Backend (Port 5000) und Betrieb ausschließlich über die Hexagonal‑Architektur auf Port 5001.
- Umfang: Entfernen sämtlicher 5000‑Proxys im Hexa‑Backend, Setzen der Standard‑Startparameter auf `use_legacy=False`, Prüfung auf Restverweise und Basistests/Empfehlungen.

### Geänderte Dateien (Hexa‑Backend)
- `src_hexagonal/hexagonal_api_enhanced.py`
  - Entfernt: Proxy zu `http://127.0.0.1:5000/api/llm/get-explanation`.
  - LLM‑Endpoint nutzt nur noch interne Provider (DeepSeek/Mistral via `MultiLLMProvider`) oder liefert bei Nichtverfügbarkeit einen transparenten 503‑Fehler.
  - Keine Upstream‑Fallbacks mehr zu Legacy (5000).
- `src_hexagonal/hexagonal_api_enhanced_clean.py`
  - Entfernt: Legacy‑Proxy (5000) aus LLM‑Endpoint.
  - Anpassung: Standard‑Start jetzt `use_legacy=False` (auch im `__main__`).
  - Fehlertexte aktualisiert (ohne Hinweis auf 5000).
- `src_hexagonal/hexagonal_api.py`
  - Anpassung: Standard‑Start jetzt `use_legacy=False` (auch im `__main__`).

### Aktueller Betriebsmodus
- Architektur: Hexagonal (Inbound: Flask REST, optional WebSocket; Application‑Services; Ports/Adapter‑Abstraktionen).
- Port: 5001 (einziger Backend‑Port).
- Repository/Engine Defaults: `use_legacy=False` → SQLite/JSONL bevorzugt; Reasoning weiterhin über Legacy‑Engine bis eigener Ersatz bereitsteht.
- CORS: Permissiv für lokalen Betrieb (Frontend‑Entwicklung). Für Produktion Whitelist empfehlen (siehe Empfehlungen).

### Wichtige Endpunkte (Auszug)
- GET `/health` – Zustand/Port/Repo‑Info.
- GET `/api/status` – Systemstatus (inkl. Governor/WebSocket, falls aktiv).
- GET `/api/facts`, POST `/api/facts`, POST `/api/search`, POST `/api/reason`.
- POST `/api/facts/delete`, PUT `/api/facts/update` – im „enhanced“ Build verfügbar.
- GET `/api/facts/count` (TTL‑Cache), GET `/openapi.json`.
- LLM: POST `/api/llm/get-explanation` – nur interne Provider oder ehrlicher 503.

### LLM‑Verhalten nach Migration
- Keine Weiterleitung mehr zu Legacy (5000).
- Wenn interne LLM‑Provider nicht konfiguriert/verfügbar sind, liefert der Endpoint 503 mit klarer Fehlermeldung.
- Empfehlung: API‑Keys über `.env` für interne Provider (DeepSeek/Mistral) setzen.

### MCP/Tooling
- MCP‑Server (`hak_gal_mcp_fixed.py`) nutzt bereits Port 5001 als Default (`HAKGAL_API_BASE_URL`).
- 30 Tools gemäß Doku einsatzbereit; Schreiboperationen sind über `HAKGAL_WRITE_ENABLED` und optionalen Token abgesichert.

### Verifikation (Quick‑Checks)
- Health: `curl http://127.0.0.1:5001/health`
- Add Fact: `curl -X POST http://127.0.0.1:5001/api/facts -H "Content-Type: application/json" -d '{"statement":"HasPart(A,B)."}'`
- Delete Fact: `curl -X POST http://127.0.0.1:5001/api/facts/delete -H "Content-Type: application/json" -d '{"statement":"HasPart(A,B)."}'`
- Update Fact: `curl -X PUT http://127.0.0.1:5001/api/facts/update -H "Content-Type: application/json" -d '{"old_statement":"HasPart(A,B).","new_statement":"HasPart(A,C)."}'`
- LLM (503 ohne Provider): `curl -X POST http://127.0.0.1:5001/api/llm/get-explanation -H "Content-Type: application/json" -d '{"topic":"HasPart(A,B)"}'`

### Sicherheit & Betrieb
- CORS: Für Produktion Origins whitelisten; Catch‑All‑OPTIONS auf benötigte Pfade begrenzen.
- Kontrollrouten (Governor/Kill‑Switch): In Prod per Auth/Nginx‑ACL absichern.
- Legacy‑Abhängigkeiten: Keine verbliebenen 5000‑Referenzen im Hexa‑Quellbaum (`src_hexagonal/`).

### Bekannte Beobachtungen (vor Migration) & Erwartung jetzt
- Zuvor 405 auf POST `/api/facts/delete` und PUT `/api/facts/update` → tritt auf, wenn „clean“ ohne diese Routen lief.
- Mit „enhanced“ und Start (`use_legacy=False`, Port 5001) sollten die Endpunkte funktionieren.

### Empfehlungen/Nächste Schritte
- Startskripte/Readmes vereinheitlichen (nur 5001/Hex nennen; Legacy‑Hinweise entfernen).
- LLM‑Provider konfigurieren (falls Erklärungen produktiv benötigt werden).
- CORS/ACL‑Härtung für produktionsnahe Umgebungen.
- Optional: Frontend‑Proxy/NGINX auf 5001; veraltete `HAK_GAL_SUITE`‑Docker/NGINX nicht mehr verwenden.

### Änderungsreferenzen
- `src_hexagonal/hexagonal_api_enhanced.py` – LLM‑Proxy entfernt; interner Provider/Fallback, keine 5000‑Calls.
- `src_hexagonal/hexagonal_api_enhanced_clean.py` – 5000‑Proxy entfernt; Default `use_legacy=False`.
- `src_hexagonal/hexagonal_api.py` – Default `use_legacy=False`.

— erstellt von GPT-5 (2025-08-14)
