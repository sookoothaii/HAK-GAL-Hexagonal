# HAK_GAL_HEXAGONAL — Research Suite (Hexagonal, Port 5001)

Reine Hexagonal‑Architektur (REST/WebSocket) mit SQLite als Source of Truth. JSONL nur als Export/Archiv.

## Quick Start (Backend)
```powershell
# In Projektwurzel
.\.venv_hexa\Scripts\activate
python src_hexagonal\hexagonal_api_enhanced.py
# oder
.\start_native.bat
```
Backend läuft auf `http://127.0.0.1:5001`.

## Frontend
Falls vorhanden: Vite/React im Ordner `frontend/` starten.

## Umgebung / ENV
- Beispiel: `env.example` → nach `.env` kopieren und Variablen setzen
- Wichtige Variablen:
  - `HAKGAL_API_BASE_URL` (default `http://127.0.0.1:5001`)
  - `HEXAGONAL_PORT` (default `5001`)
  - LLM‑Keys (optional): `DEEPSEEK_API_KEY`, `MISTRAL_API_KEY`
  - Engines (optional): `AETHELRED_*` Tuning

## SQLite als SoT
- Laufender Betrieb schreibt in `k_assistant.db`
- Import existierender JSONL:
```powershell
.\.venv_hexa\Scripts\python.exe scripts\import_jsonl_to_sqlite.py
```

## Qualität & Wissensexpansion (safe)
- Integritätsreport:
```powershell
.\.venv_hexa\Scripts\python.exe scripts\generate_integrity_report.py
```
- Kuratierte Kandidaten (review‑first):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\curated_candidate_pipeline.ps1 -Limit 5000
```

## Governor & Engines
- Backend starten → im Frontend „Start Governor“ klicken.
- Engine‑Tuning per ENV (siehe `env.example`). Optionaler Confidence‑Gate (`AETHELRED_STRICT_CONFIDENCE`).

## Entwickeln
- Python 3.11+ empfohlen
- venv: `.venv_hexa` (nicht committen)
- Node (optional): `frontend/`

## Versionierung / Push auf GitHub
- Dieses Repo ist für den Ordner `HAK_GAL_HEXAGONAL/` gedacht.
- `.gitignore` blendet Daten/Backups/venv/Builds aus.
- Nicht versionieren: `k_assistant.db`, `data/*.kb.jsonl`, Modelle/FAISS/DLLs, Backups/Logs.
- Init & Push:
```powershell
git init
git add .
git commit -m "init: HAK_GAL_HEXAGONAL (SQLite SoT, tools, docs)"
git branch -M main
git remote add origin <your_repo>
git push -u origin main
```

## Lizenz
- Trage deine Lizenz in `LICENSE` ein (z. B. MIT/Apache‑2.0).
