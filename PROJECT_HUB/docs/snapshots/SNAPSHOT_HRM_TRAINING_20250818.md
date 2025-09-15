---
title: "Snapshot Hrm Training 20250818"
created: "2025-09-15T00:08:01.074170Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Snapshot: HRM Training & Integration (2025-08-18)

- Status: Erfolgreich trainiert und integriert
- Empfohlene Startdatei: `scripts/launch_5002_WRITE.py`
- Reasoning Engine: `NativeReasoningEngine` (lädt trainiertes HRM)
- Modellpfad: `D:/MCP Mods/HAK_GAL_HEXAGONAL/models/hrm_model_v2.pth`
- Datenbank: `D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db`
- Port: 5002 (Schreibmodus)
- Metriken:
  - Best Validation Accuracy: 0.9081
  - Parameter: 3,549,825
  - Vocab Size: ~2989, Predicates: ~75
- Verifikation:
  - Logs: "[HRM] Loaded trained model from .../models/hrm_model_v2.pth"
  - API: `POST /api/reason` → echte Confidence (z. B. 1.0 für IsA(Socrates, Philosopher).)
- Start (PowerShell): `& .\.venv_hexa\Scripts\python.exe .\scripts\launch_5002_WRITE.py`

