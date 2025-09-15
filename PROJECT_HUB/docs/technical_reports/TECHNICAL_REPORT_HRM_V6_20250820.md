---
title: "Technical Report Hrm V6 20250820"
created: "2025-09-15T00:08:01.127141Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Technischer Report: HRM + V6 Learning Integration (2025-08-20)

## Zusammenfassung
- HRM (ImprovedHRM, ~3.55M Parameter) trainiert, validiert (Best Val Acc ≈ 0.9081) und produktiv integriert.
- API lädt trainiertes Modell automatisch (`NativeReasoningEngine`), Start über `scripts/launch_5002_WRITE.py`.
- V6-Learning-Tools hinzugefügt: sichere, benutzerfreundliche Booster (V5-Style), Presets, interaktive Loops.
- Ziel: Nachhaltiges Lernen (Feedback, Faktenzuwachs), kontrollierte Qualität (Guardrails), klare Bedienung.

## Trainings- und Modelldetails
- Script: `train_hrm_model.py`
- Datenbank: `hexagonal_kb.db` (≈ 4k+ Facts)
- Architektur: Bi-GRU (2 Layer, hidden 256) + Multi-Head Attention (4 Heads), Embeddings 128.
- Parameter: ≈ 3,549,825
- Metriken: Best Validation Accuracy ≈ 0.9081; HRM liefert plausible Confidence (0..1).
- Checkpoint: `models/hrm_model_v2.pth` (CUDA-kompatibel)

## Integration in die API
- Dateien:
  - `src_hexagonal/hexagonal_api_enhanced.py`: Reasoning → `NativeReasoningEngine`
  - `src_hexagonal/hexagonal_api_enhanced_clean.py`: Reasoning → `NativeReasoningEngine`
  - `src_hexagonal/adapters/native_adapters.py`: liest `HRM_MODEL_PATH` (Fallback: `models/hrm_model_v2.pth`)
  - `scripts/launch_5002_WRITE.py`: setzt `HRM_MODEL_PATH` + DB + Port 5002 (WRITE)
- Verifikation:
  - Logs beim Start: „Loaded trained model …“, „🧠 Reasoning: NativeReasoningEngine“
  - API: `/health`, `/api/reason` (Confidence > 0.9 für IsA(Socrates, Philosopher).)

## V6 Learning-Tools (Design)
- `v6_safe_boost.py` (V5-Style UI):
  - Guardrails: strikte Formatvalidierung, Entitäten-Normalisierung, Duplicate-Block, Rate-Limit
  - Scoring: Combined = 0.5*HRM + 0.3*LLM + 0.2*KB (Fallback ohne LLM berücksichtigt)
  - Output: pro Item (V5-ähnlich) + Summary mit Balken + Top-Kandidaten
  - Flags: `-e/--episodes`, `--v5`, `--auto`, `--min`, `--quiet`, `--json`
- `v6_learning_loop.py` (interaktiv):
  - Stunden, Episoden/Zyklus, Threshold, Mode, Intervall, Kandidaten; stündlich/zyklisch; Netto-Zuwachs pro Zyklus; JSON-Summary
- `v6_learning_presets.py` (One-Question UX):
  - Presets A/B/C (sicher, mehr Abdeckung, produktiv) + D (Custom)
  - Eine Eingabe, klare Erklärung; Netto-Zuwachs je Zyklus; JSON-Summary

## Bedienkonzept
- Empfohlene Startdatei (Backend): `scripts/launch_5002_WRITE.py`
- Learning (einfach): `v6_learning_presets.py` starten → Preset wählen → läuft
- Kontrolle (detailliert): `v6_learning_loop.py` interaktiv; V6 direkt für Ad-hoc-Analysen
- Messgrößen:
  - Netto-Zuwachs Facts (`/api/facts/count` vor/nach Zyklus), Duplicates, Invalids, Below-Threshold
  - Durchschnittswerte HRM/LLM/KB/Combined; Zyklusdauer; Logpfad

## Risiken & Gegenmaßnahmen
- Falschpositive (LLM-dominierte Vorschläge):
  - Gegenmaßnahme: hoher Threshold (≥ 0.7), HRM/KB-Anteil sichern, Shadow-Mode im Zweifel nutzen
- DB-Konsistenz (Duplikate/Kontradiktionen):
  - Gegenmaßnahme: Duplicate-Blocker in V6, Kontradiktions-Check (optional ausbaubar)
- Port-Kollision (5002):
  - Gegenmaßnahme: alte Instanz beenden; nur eine Startsequenz gleichzeitig

## Empfehlungen
- Betrieb:
  - Preset A (Shadow) 1h/Tag automatisiert laufen lassen; Vorschläge prüfen; valide Facts einspielen
  - Wöchentlich/monatlich: Retraining + Checkpoint-Versionierung (+ Report)
- Ausbaustufen:
  - LLM-Score aktivieren (API-Keys) → höhere Rescue-Rate, aber Schwelle konservativ halten
  - Kontradiktionsprüfung + semantische Duplikate stärker gewichten (Mojo-Adapter vorhanden)
  - Monitoring-Dashboard (Netto-Zuwachs/Tag, Top-Prädikate, Fehlerquoten)

## Anhang: Beispiele
- Backend-Start:
  ```powershell
  & .\.venv_hexa\Scripts\python.exe .\scripts\launch_5002_WRITE.py
  ```
- Learning Preset (One-Question):
  ```powershell
  & .\.venv_hexa\Scripts\python.exe .\v6_learning_presets.py
  ```
- Ad-hoc Analyse (20 Episoden, V5-Style):
  ```powershell
  & .\.venv_hexa\Scripts\python.exe .\v6_safe_boost.py -e 20 --v5
  ```

