---
title: "Snapshot System Hrm V6 20250820"
created: "2025-09-15T00:08:01.076170Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# System Snapshot: HRM + V6 Learning (2025-08-20)

## Übersicht
- Architektur: Hexagonal v2.0 (Ports & Adapters)
- Backend: Flask + Socket.IO (Port 5002, WRITE-Mode)
- Frontend: Vite/React (Port 5173)
- Reasoning: NativeReasoningEngine (lädt trainiertes HRM)
- Wissensbasis: SQLite (`hexagonal_kb.db`)
- Learning-Tools: `v6_safe_boost.py`, `v6_learning_loop.py`, `v6_learning_presets.py`

## Laufender Zustand (letzte Session)
- Port 5002 Start-Log (Auszug):
  - „🧠 Reasoning: NativeReasoningEngine“
  - „[HRM] Loaded trained model from D:/MCP Mods/HAK_GAL_HEXAGONAL/models/hrm_model_v2.pth“
  - Repository: `SQLiteFactRepository`
- Faktenstand:
  - Start-Fact-Count (Beispiel): 5773
  - In einzelnen V6-Zyklen: Zyklus-Differenz gemessen (±0 in Beispiel)

## Modell
- Checkpoint: `D:/MCP Mods/HAK_GAL_HEXAGONAL/models/hrm_model_v2.pth`
- Typ: ImprovedHRM (Bi-GRU + Multi-Head Attention)
- Parameter: ≈ 3,549,825
- Best Validation Accuracy: ≈ 0.9081
- Vokabular: `vocab_size ≈ 2989`, `predicate_count ≈ 75`
- Device: CUDA (z. B. NVIDIA GeForce RTX 3080 Ti Laptop GPU)

## Datenbank
- Datei: `D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db`
- Beispiel-Faktenzahl: 4000–5800+ (je nach Import/Session)

## Startempfehlung
- Empfohlene Startdatei: `scripts/launch_5002_WRITE.py`
  - Setzt: `HAKGAL_SQLITE_DB_PATH`, `HAKGAL_PORT=5002`, `HRM_MODEL_PATH`
  - Start (PowerShell):
    ```powershell
    & .\.venv_hexa\Scripts\python.exe .\scripts\launch_5002_WRITE.py
    ```

## Verifikation
- Health:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:5002/health" -Method Get
  ```
- Reasoning:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:5002/api/reason" -Method Post -ContentType "application/json" -Body (@{ query = "IsA(Socrates, Philosopher)." } | ConvertTo-Json)
  ```
- Erwartet:
  - Confidence > 0.9, `device: cuda`
  - Log zeigt geladenes HRM-Checkpoint

## Learning-Tools (V6)
- `v6_safe_boost.py` (V5-Style UI)
  - Kombinierter Score: 0.5*HRM + 0.3*LLM + 0.2*KB
  - Guardrails: strikte Formatvalidierung, Dedupe, Rate-Limit
  - Beispiele:
    ```powershell
    # 20 Episoden, V5-Stil (nur Anzeige)
    & .\.venv_hexa\Scripts\python.exe .\v6_safe_boost.py -e 20 --v5
    # Auto-Add, Threshold 0.75, nur Summary
    & .\.venv_hexa\Scripts\python.exe .\v6_safe_boost.py -e 40 --auto --min 0.75 --quiet
    ```
- `v6_learning_presets.py` (eine Frage, Presets)
  - Presets A/B/C oder D (Custom), Netto-Zuwachs/zyklus, Summary JSON in `logs/`
  - Start:
    ```powershell
    & .\.venv_hexa\Scripts\python.exe .\v6_learning_presets.py
    ```
- `v6_learning_loop.py` (interaktiv detailliert)
  - Stunden/Episoden/Intervall frei, Netto-Zuwachs/zyklus, Summary JSON in `logs/`

## Hinweise
- Port-Kollision (5002) vermeiden: alte Instanz vor Neustart beenden
- „read_only: true“ in `/health` ist Anzeige-Flag für Port 5002; WRITE-Endpoints sind aktiv, sofern Kill-Switch nicht auf SAFE steht
- LLM-Boost (optional): API-Keys setzen (Gemini/DeepSeek) → höhere Rescue-Quote bei V6

## Nächste Schritte (optional)
- Periodisches Retraining (monatlich/bei N neuen Fakten) mit `train_hrm_model.py`
- Checkpoint-Versionierung + Report im `PROJECT_HUB`
- KPI-Monitoring: Net-Zuwachs/Tag, Duplicate-/Contradiction-Rate, HRM/LLM/KB-Durchschnittswerte

