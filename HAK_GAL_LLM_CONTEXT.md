# HAK-GAL LLM Kontext

## Architekturprinzipien
- **HAK/GAL Verfassung Artikel 1–8:**
  1. Komplementäre Intelligenz: Trennung von Mensch (UI) und KI (Backend)
  2. Gezielte Befragung: Präzise, nachvollziehbare Schnittstellen
  3. Externe Verifikation: Testabdeckung, Benchmarks, Monitoring
  4. Bewusstes Grenzüberschreiten: Von monolithisch zu hexagonal, von synchron zu asynchron
  5. System-Metareflexion: Monitoring, Metriken, Selbstbeobachtung
  6. Empirische Validierung: Alle Aussagen durch Messungen und Tests belegt
  7. Konjugierte Zustände: Symbolische und neuronale Intelligenz kombiniert
  8. Protokoll zur Kollision: Fallback-Mechanismen, Fehlerbehandlung

## Systemstatus (Stand: 11.08.2025)
- **CUDA:** RTX 3080 Ti, 16GB, aktiv
- **PyTorch:** 2.7.1+cu118
- **Fakten:** 3080 (Knowledge Base)
- **Governor:** Constitutional HRM, Article 1-8 compliant
- **WebSocket:** aktiv (Events: kb_update, system_status, governor_update, reasoning_result, fact_added, llm_status)
- **Monitoring:** Prometheus vorbereitet, Sentry aktiv (Original), Hexagonal: vorbereitet
- **Frontend:** React 18, Zustand, Vite, shadcn/ui, Backend-Switcher

## Wichtige Fixes
- Bulk-Fact-API: `trigger_graph_update`-Argument ergänzt (siehe k_assistant_thread_safe_v2.py)
- Vocabulary-Mismatch im HRM: Frontend-Tests und Model-Vocabulary synchronisiert
- Graph-Update: Race-Condition in KnowledgeGraphVisualization.tsx behoben
- Vite-Cache-Probleme: fix_vite_cache.bat eingeführt

## Lessons Learned
- **API-Kompatibilität:** Argumente und Signaturen müssen zwischen Hexagonal und Original synchron bleiben
- **Vocabulary:** Model, Datenbank und Tests müssen identisches Vocabulary nutzen
- **Testing:** Echte Daten statt Mock-Werte verwenden
- **Monitoring:** Frühzeitig Prometheus/Sentry einbinden

## Links & Ressourcen
- HEXAGONAL_COMPLETION_STATUS.md
- HEXAGONAL_FINAL_STATUS.md
- HEXAGONAL_COMPLETION_TASKS.md
- GEMINI.md (operative Direktiven)
- fakten2.pdf (Faktenbasis)
- src_hexagonal/hexagonal_api.py (Entry Point)
- src/hak_gal/api.py (Original Entry Point)
- frontend_new/src/ProApp.tsx (Frontend Main)

---

*Diese Datei dient als zentraler Kontext für LLMs und Entwickler. Bitte regelmäßig aktualisieren!*
