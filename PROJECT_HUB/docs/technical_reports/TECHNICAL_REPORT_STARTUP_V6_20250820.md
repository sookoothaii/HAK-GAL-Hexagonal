# Technischer Start-Report: HAK‑GAL Hexagonal + HRM + V6 (2025‑08‑20)

## Ziel
Kompakte, verlässliche Anleitung, um das System lokal sauber zu starten (Backend 5002, Proxy 8088, Frontend 5173), inkl. ENV, LLM‑Prio (DeepSeek), HRM‑Modell, Socket.IO und Troubleshooting.

## Komponenten & Pfade
- Repo: `D:/MCP Mods/HAK_GAL_HEXAGONAL`
- Datenbank: `D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db`
- HRM‑Modell: `D:/MCP Mods/HAK_GAL_HEXAGONAL/models/hrm_model_v2.pth`
- Backend (Port 5002): `scripts/launch_5002_WRITE.py`
- Proxy (Port 8088): `Caddyfile` + `caddy.exe`
- Frontend (Port 5173): `frontend/` (Vite)

## ENV / .env (LLM‑Prio DeepSeek)
- Empfohlen (PowerShell, vor Backend‑Start):
```powershell
$env:DEEPSEEK_API_KEY="<DEIN_DEEPSEEK_KEY>"
$env:GEMINI_API_KEY=""   # leer → Gemini wird nicht priorisiert/angefragt
$env:MISTRAL_API_KEY=""  # leer
$env:HAKGAL_API_KEY=hg_sk_...   # ohne Anführungszeichen
```
- Optional in `.env` (Projekt/HAK_GAL_HEXAGONAL oder SUITE):
```
DEEPSEEK_API_KEY=<DEIN_DEEPSEEK_KEY>
GEMINI_API_KEY=
MISTRAL_API_KEY=
HAKGAL_API_KEY=hg_sk_...
```

## Backend (5002) starten
```powershell
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
$env:HAKGAL_SQLITE_DB_PATH="D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db"
$env:HAKGAL_PORT="5002"
$env:HRM_MODEL_PATH="D:/MCP Mods/HAK_GAL_HEXAGONAL/models/hrm_model_v2.pth"
& .\.venv_hexa\Scripts\python.exe .\scripts\launch_5002_WRITE.py
```
Erwartete Log‑Zeilen:
- „🧠 Reasoning: NativeReasoningEngine“
- „[HRM] Loaded trained model from …/hrm_model_v2.pth“

## Proxy (Caddy, 8088) Konfiguration & Start
Caddyfile (IPv4‑Upstreams, Socket.IO → 5002, API → 5002, Rest → 5173):
```caddy
{
	admin off
}

:8088 {
	log {
		output stdout
		level INFO
	}
	# Vite / Module
	handle /@vite/client { reverse_proxy 127.0.0.1:5173; header Content-Type "application/javascript" }
	handle /@vite/*      { reverse_proxy 127.0.0.1:5173; header Content-Type "application/javascript" }
	handle /src/*        { reverse_proxy 127.0.0.1:5173; header Content-Type "application/javascript" }
	handle /node_modules/* { reverse_proxy 127.0.0.1:5173 }
	handle_path /*.css   { reverse_proxy 127.0.0.1:5173; header Content-Type "text/css" }
	handle /assets/*     { reverse_proxy 127.0.0.1:5173 }
	# Backend API
	handle /api/*        { reverse_proxy 127.0.0.1:5002 }
	handle /health       { reverse_proxy 127.0.0.1:5002 }
	# Socket.IO (WebSocket) zum Backend
	handle /socket.io/*  { reverse_proxy 127.0.0.1:5002 }
	# Default → Frontend (Vite Dev Server)
	handle               { reverse_proxy 127.0.0.1:5173 }
}
```
Start/Reload:
```powershell
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
Get-Process caddy -ErrorAction SilentlyContinue | Stop-Process -Force
.\caddy.exe run --config . Caddyfile
```

## Frontend (5173)
```powershell
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend"
npm run dev
```
Hinweis: Über Caddy erreichst du das Frontend via `http://localhost:8088/`. Direkt auch via `http://localhost:5173/`.

## Funktionstests
- Backend Health:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5002/health" -Method Get
```
- Socket.IO direkt vom Backend (Polling):
```powershell
Invoke-WebRequest "http://127.0.0.1:5002/socket.io/?EIO=4&transport=polling"
```
- Socket.IO via Proxy (8088):
```powershell
Invoke-WebRequest "http://localhost:8088/socket.io/?EIO=4&transport=polling"
```
- WebSocket (Frontend‑Konsole): Meldung „Using real backend data via WebSocket“ ohne Fehler.

## LLM‑Prio (DeepSeek vor Gemini)
- Ohne Code‑Änderung: Gemini‑Key leer lassen, DeepSeek‑Key setzen (siehe ENV oben). Das Ensemble bleibt mit Fallback; es wird nur die Erstwahl beeinflusst.
- Debug: `debug_llm_env.py` prüfen; bei 429/Timeouts übernimmt DeepSeek.

## HRM / Modell / V6
- HRM‑Modell: `models/hrm_model_v2.pth` (≈3.55M Parameter). Wird beim Backend‑Start automatisch geladen.
- V6 Tools:
  - Autopilot (Minimal‑UX):
    ```powershell
    & .\.venv_hexa\Scripts\python.exe .\v6_autopilot.py
    ```
    – Nur Ziel/Dauer/Episoden/Quelle wählen; Netto‑Zuwachs pro Runde und Summary in `logs/`.
  - Presets (One‑Question):
    ```powershell
    & .\.venv_hexa\Scripts\python.exe .\v6_learning_presets.py
    ```
  - V5‑Style Analyse (ad‑hoc):
    ```powershell
    & .\.venv_hexa\Scripts\python.exe .\v6_safe_boost.py -e 20 --v5
    ```

## Troubleshooting (Kurz)
- 502 via Caddy „dial tcp [::1]:5002 refused“ → Backend 5002 läuft nicht oder IPv6‑Dial. Lösung:
  - Backend starten (s.o.)
  - In Caddyfile 127.0.0.1 Upstreams verwenden (wie oben)
- WS‑Handshake hängt/Timeout:
  - `/socket.io/*` muss auf 5002 gehen (nicht 5173)
  - Backend Health prüfen; Browser neuladen
- ERR_CONNECTION_RESET/REFUSED auf 5002:
  - Backend (5002) läuft nicht oder Firewall blockt; neu starten
- Port 5002 belegt:
  ```powershell
  Get-NetTCPConnection -LocalPort 5002 | Select-Object -First 1 | % { Stop-Process -Id $_.OwningProcess -Force }
  ```
- API‑Key nötig (falls gesetzt):
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:5002/api/command" -Method Post -Headers @{"X-API-Key"="hg_sk_..."} -ContentType "application/json" -Body (@{ command="explain"; query="IsA(Socrates, Philosopher)" } | ConvertTo-Json)
  ```

## Start‑Checkliste (Kurzfassung)
1) ENV setzen (DeepSeek aktiv, Gemini leer, HAKGAL_API_KEY ohne "")
2) Backend 5002 starten
3) Caddy 8088 starten (Caddyfile wie oben)
4) Frontend 5173 starten
5) Tests: `/health`, `/socket.io` (Polling), Frontend lädt ohne WS‑Fehler
6) Optional: V6 Autopilot starten (Shadow/Auto)

– Ende –

