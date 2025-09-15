---
title: "Server Start Guide Hexagonal 5001 5002 20250815"
created: "2025-09-15T00:08:01.021301Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Server Start Guide – Hexagonal 5001/5002 (Mojo), Windows/PowerShell

Diese Anleitung zeigt, wie die Backends 5001/5002 (optional 5003) korrekt gestartet, geprüft und bei Bedarf beendet/gerollbackt werden – strikt aus der Projekt‑venv.

## 1) Voraussetzungen
- PowerShell (Windows)
- Projekt‑venv vorhanden: `D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\`
- Pfade mit Leerzeichen immer in Anführungszeichen setzen!

## 2) venv aktivieren (nur einmal pro Konsole)
```powershell
& "D:/MCP Mods/HAK_GAL_HEXAGONAL/.venv_hexa/Scripts/Activate.ps1"
```

## 3) 5001 (Standard‑Backend) starten
- Sichtbar im aktuellen Fenster (minimal):
```powershell
& "D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" -c "import sys; sys.path.insert(0, r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal'); import hexagonal_api_enhanced as m; m.create_app(use_legacy=False, enable_all=True).run(host='127.0.0.1', port=5001, debug=False)"
```
- Test im Browser:
  - http://localhost:5001/health
  - http://localhost:5001/api/facts/count

## 4) 5002 (Mojo‑Backend, Read‑Only) – einfache sichtbare Variante
- Sichtbar in neuem Fenster (Logs live):
```powershell
$env:HAKGAL_PORT='5002'
powershell -NoProfile -NoExit -Command "& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\launch_5002_mojo.py'"
```
- Optional vorher Flags/DB setzen (Read‑Only + Mojo):
```powershell
$env:HAKGAL_SQLITE_DB_PATH='file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared'
$env:HAKGAL_SQLITE_READONLY='true'
$env:MOJO_ENABLED='true'; $env:MOJO_VALIDATE_ENABLED='true'; $env:MOJO_DUPES_ENABLED='true'
```
- Tests im Browser:
  - http://localhost:5002/health
  - http://localhost:5002/api/facts/count
  - http://localhost:5002/api/quality/metrics?sample_limit=5000&sem_threshold=0.95
  - (falls verfügbar) http://localhost:5002/api/analysis/duplicates?sample_limit=2000&threshold=0.95

## 5) 5002 (Mojo) – komfortabler Neustart mit Health/Logs (empfohlen)
- Start/Neustart (Read‑Only + Mojo Validate + Dupes):
```powershell
.\scripts\extensions\restart_5002.ps1 -Mojo -Validate -Dupes -DbUri 'file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared' -Port 5002 -HealthTimeoutSec 120
```
- Eigenschaften:
  - Start strikt aus `.venv_hexa`
  - Health‑Polling, Kill‑Switch aktiv
  - Logs: `logs/server5002.out.txt`, `logs/server5002.err.txt`

## 6) Zweitinstanz auf 5003 (ohne 5002 zu stören)
- Sichtbar (Logs live):
```powershell
$env:HAKGAL_PORT='5003'
powershell -NoProfile -NoExit -Command "& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\launch_5002_mojo.py'"
```
- Test: http://localhost:5003/health

## 7) Admin/Analyse‑Routen (falls mit neuem Build gestartet)
- Flags ansehen: http://localhost:5002/api/mojo/flags
- Golden (Server): http://localhost:5002/api/mojo/golden?limit=5000&threshold=0.95
- Bench (Server): http://localhost:5002/api/mojo/bench?limit=3877&threshold=0.95
- Duplicates Analyse: http://localhost:5002/api/analysis/duplicates?sample_limit=2000&threshold=0.95

Flags per POST setzen (Browser‑Konsole):
```js
fetch('http://localhost:5002/api/mojo/flags', {
  method:'POST', headers:{'Content-Type':'application/json'},
  body: JSON.stringify({enabled:true, validate:true, dupes:true})
}).then(r=>r.json()).then(console.log)
```

## 8) Prozesse beenden (falls Port belegt)
- Prozess auf Port 5002 beenden:
```powershell
$pid = (Get-NetTCPConnection -LocalPort 5002 -State Listen | Select-Object -First 1 -ExpandProperty OwningProcess)
if ($pid) { Stop-Process -Id $pid -Force }
```
- Alternative: sichtbares Startfenster schließen.

## 9) Rollback 5002 (baseline, Read‑Only, ohne Mojo)
```powershell
.\scripts\extensions\rollback_5002.ps1 -Port 5002
```

## 10) Hinweise zu Performance/Modellen
- Modelle (SentenceTransformer etc.) werden je Prozess geladen. Um erneutes Laden zu vermeiden, den Prozess nicht unnötig beenden.
- 5002 ist als Mojo‑Read‑Only‑Instanz gedacht – Legacy‑Reasoning kann dort bei Bedarf deaktiviert werden, um Startzeit zu reduzieren.

---
Diese Datei ist bewusst „copy‑paste‑fähig“. Bei Fragen oder für Automatisierung (Scheduler) bitte melden.
