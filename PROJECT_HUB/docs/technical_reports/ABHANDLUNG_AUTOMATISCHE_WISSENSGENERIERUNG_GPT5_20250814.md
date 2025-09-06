# Abhandlung: HAK‑GAL HEXAGONAL – Eine verlässliche Suite zur automatischen Wissensgenerierung

Datum: 2025‑08‑14
Autor: GPT‑5
Zielgruppe: Wissenschaftliche Leitung/Professorat

## 1. Executive Summary
Die HAK‑GAL‑Suite (aktuell in der Variante HAK_GAL_HEXAGONAL) ist ein forschungsgetriebenes System zur strukturierten, nachvollziehbaren und reproduzierbaren Wissensgenerierung. Nach der jüngsten Modernisierung läuft sie als reine Hexagonal‑Architektur auf Port 5001 und hat sich vom Legacy‑Backend (Port 5000) vollständig gelöst. Der Fokus liegt auf:
- zuverlässiger Wissensextraktion in Form logischer Aussagen (Fakten),
- strenger Validierung (syntaktisch, statistisch, heuristisch),
- erklärbarer Ableitung (Reasoning + LLM‑gestützte Erklärungen),
- reproduzierbarer Orchestrierung über ein standardisiertes Tool‑Interface (MCP, 30 Tools),
- empirischer Arbeitsweise gemäß HAK/GAL‑Verfassung (keine Spekulation, nur validierte Aussagen).

Die Datenhaltung erfolgt primär in SQLite (Source of Truth); JSONL wird als Archiv/Exportformat genutzt. Das System stellt eine Web‑API (REST, optional WebSocket) bereit und wird durch umfassende Monitoring‑, Snapshot‑ und Backup‑Prozesse gestützt.

## 2. Historischer Kontext und Motivation
Wissenssysteme leiden häufig unter Intransparenz („Black‑Box“), mangelnder Reproduzierbarkeit und unklarer Datenherkunft. HAK‑GAL adressiert diese Schwächen:
- Jede Aussage liegt als formalisiertes Faktum `Predicate(Entity1, Entity2).` vor.
- Werkzeuge zur Suche, Konsistenzprüfung, Duplikat‑ und Ähnlichkeitsanalyse liegen standardisiert vor.
- Erklärungen werden als eigener Schritt behandelt (Reasoning/LLM), klar getrennt von den Fakten.
- Alle Operationen sind über MCP‑Tools und HTTP‑Endpunkte reproduzierbar orchestrierbar.

Die aktuelle Hexagonal‑Variante wurde entwickelt, um die Domänenlogik von Infrastrukturdetails zu entkoppeln (Ports & Adapters) und die Suite skalierbar, testbar und wartbar zu machen.

## 3. Systemübersicht: HAK_GAL_HEXAGONAL
- Architektur: Hexagonal (Inbound: REST/WebSocket; Application‑Services; Outbound‑Adapter: SQLite, Monitoring, Governor).
- Port: 5001 (einzige Backendschnittstelle).
- Datenquelle: `k_assistant.db` (SQLite) als Primärspeicher. JSONL (`data/k_assistant.kb.jsonl`) als Export/Archiv.
- Orchestrierung: 30 MCP‑Tools (Basis, Analyse, Verwaltung, Erweiterte, Projekt‑Hub).
- Validierte Migration: 99,7% deutschsprachiger Prädikate → englische Syntax zur internationalen Interoperabilität.

## 4. Architektur und Komponenten
### 4.1 Inbound Adapter – REST API (Flask)
- Endpunkte (Auszug):
  - Core: `/health`, `/api/status`, `/api/facts` (GET/POST), `/api/search`, `/api/reason`
  - CRUD: `/api/facts/delete` (POST), `/api/facts/update` (PUT)
  - Analytics: `/api/facts/count`, `/api/predicates/top`, `/api/quality/metrics`, `/openapi.json`
  - Erklärungen: `/api/llm/get-explanation` (nur interne Provider; sonst 503 mit klarer Meldung)
- CORS: Dev‑freundlich, für Produktion per Whitelist härtbar.
- WebSocket (optional): Live‑Events für Status, Reasoning‑Ergebnisse und Notfallroutinen.

### 4.2 Application‑Schicht
- FactManagementService: Hinzufügen, Suchen, Auflisten von Fakten (Business‑Regeln: Endpunkt, Formatregex, Idempotenz).
- ReasoningService: Berechnung einer Konfidenz, Erzeugung erklärender Begriffe (reasoning terms), Einbettung von Geräte‑/Laufzeitmetadaten.

### 4.3 Outbound Adapter – Daten & Infrastruktur
- SQLite‑Adapter: Primäre Persistenz; Schema `facts(statement TEXT PRIMARY KEY, context TEXT, fact_metadata TEXT)`; unterstützt `save`, `find_*`, `exists`, `count`, `delete_by_statement`, `update_statement`.
- JSONL‑Adapter: Append‑only‑Datei (Lesen/Speichern/Scannen). Hinweis: kein `delete/update` – dient primär als Export/Archiv.
- Monitoring/Sentry (optional), Governor (strategische Steuerung), WebSocket‑Adapter (Echtzeit).

## 5. Datenmodell und Datenqualität
- Faktformat: `Predicate(Entity1, Entity2).` – standardisierte Syntax fördert Eindeutigkeit und Auswertbarkeit.
- Kontext: zu jedem Fakt strukturierte Metadaten (`context`, `fact_metadata`) zur Herkunft/Begründung.
- Qualitätsmetriken (Beispiele): Anzahl Fakten, Prädikatsverteilungen, Duplicate‑Rate, „isolated facts“, Widerspruchsindikatoren (Nicht/Not‑Paare).
- Validierung: Syntaktische Prüfung, Heuristiken (Ähnlichkeit, Konsistenz), Empirie (Statistik, Sampling, Trendanalyse).

## 6. Reasoning und Erklärbarkeit
- HRM (Human Reasoning Model, ~600k Parameter) liefert interpretierbare Konfidenzen für Aussagen.
- LLM‑gestützte Erklärungen: separates Endpoint mit strikter Fehlerbehandlung (503, wenn nicht konfiguriert), keine Vermischung von Faktgenerierung und Erklärung.
- Prinzip: Fakten bleiben knapp und atomar; Erklärungen sind narrativ und werden als Hilfsinstrument genutzt (z. B. Vorschläge für neue Fakten).

## 7. Orchestrierung über MCP (30 Tools)
Die Suite stellt 30 Tools in fünf Kategorien bereit (Basis, Analyse, Verwaltung, Erweiterte, Projekt‑Hub). Beispiele:
- Basis: `search_knowledge`, `get_system_status`, `add_fact`, `kb_stats`.
- Analyse: `semantic_similarity`, `consistency_check`, `analyze_duplicates`, `get_predicates_stats`.
- Verwaltung: `list_audit`, `export_facts`, `growth_stats`, `backup_kb`, `restore_kb`.
- Erweiterte: `find_isolated_facts`, `inference_chain`, `get_knowledge_graph`, `bulk_translate_predicates` (mit Enterprise‑Features wie `exclude_predicates`, `limit_mode='changes'`, `sample_strategy`).
- Projekt‑Hub: `project_snapshot`, `project_list_snapshots`, `project_hub_digest`.

Die MCP‑Orchestrierung ermöglicht reproduzierbare, skriptbare Workflows (z. B. Kontext sammeln → Ähnlichkeit prüfen → Duplikate analysieren → Konsistenzcheck → Bericht schreiben).

## 8. Monitoring, Validierung und Project‑Hub
- Snapshots: Regelmäßig generierte Zustandsabbilder im `PROJECT_HUB/` (inkl. TECH/KM‑Berichte und Manifeste).
- Nightly Monitoring: Trendanalysen (Faktenwachstum, Prädikatverteilungen, Konsistenz).
- Reports: Technische Übergaben („Handover“), Migrations‑ und Validierungsberichte, Discrepancy‑Analysen (BE↔FE, SQLite↔JSONL).
- Backups: Skript mit GUI (PowerShell) für Full/Incremental‑Sicherungen inkl. Manifest und Scheduling.

## 9. Ziel: Automatische Wissensgenerierung, auf die man sich verlassen kann
Das System verfolgt die Maxime wissenschaftlicher Zuverlässigkeit:
- Streng empirisch: Keine unbelegten Aussagen; jede Änderung muss validierbar sein.
- Reproduzierbar: Standardisierte Endpunkte/Tools; Snapshots und Manifeste.
- Erklärbar: Reasoning/LLM getrennt von Fakten; transparente Konfidenzen.
- Governed: Werkzeuge zur Qualitätssicherung (Konsistenz, Duplikate, Isolation) und gesicherte Schreibpfade (Tokens/Policies/Write‑Gates).
- International: Einheitliche, englische Prädikatssyntax.

## 10. Abgrenzung Legacy vs. Hexagonal
- Legacy‑Backend (Port 5000): nicht mehr erforderlich; alle Proxys entfernt.
- Hexagonal (Port 5001): saubere Ports‑&‑Adapters‑Trennung; klare Datenquellen; leichter zu testen und zu härten.

## 11. Betrieb, Sicherheit, Prozesse
- Betrieb: Startskripte (Port 5001), Health‑Checks, Facts‑Zähler, Reasoning‑Smoke‑Tests.
- Sicherheit: Optionaler Token‑Schutz für Control‑Routen; CORS‑Härtung; OpenAPI nur in Dev exponieren.
- Prozesse: Backups (Full/Incremental), Nightly Snapshots, Berichte im Hub, LLM‑Keys via `.env`.

## 12. Grenzen und Forschungsfragen
- LLM‑Abhängigkeit: Erklärungen optional; ohne Schlüssel bewusster 503‑Fail (klar kommuniziert).
- Wissensmodell: Binäre Prädikate sind bewusst minimalistisch – Mehrstellige Relationen und temporale Aspekte sind ein Forschungsthema.
- Semantische Normalisierung: Einheitliche Entitäten/Prädikate (Synonyme, Ontology‑Mapping) sind Gegenstand geplanter Erweiterungen.

## 13. Roadmap (Auszug)
- Stärkerer Fokus auf deklarative Konsistenzregeln (z. B. logische Schlussregeln, Integrity Constraints).
- Ausbau der „Enterprise Features“ (Sampling/Reporting) in kontinuierliche Qualitätssicherung.
- Optionaler Graph‑Speicher und Visualisierungspipeline für Subgraph‑Analysen.
- Verbesserte FE‑UX für LLM‑Fehlerszenarien (klare Handlungsvorschläge, Retrys, menschliche Verifikation).

## 14. Fazit
HAK_GAL_HEXAGONAL stellt eine robuste, nachvollziehbare und skalierbare Plattform zur verlässlichen, automatischen Wissensgenerierung dar. Durch die klare Trennung der Architektur, die strengen Validierungsprozesse und die reproduzierbare Orchestrierung über MCP ist die Suite nicht nur technisch fortgeschritten, sondern auch wissenschaftlich belastbar. Die Abkehr vom Legacy‑Backend und die Konzentration auf Port 5001/Hexagonal schaffen die Grundlage für nachhaltige Forschung und evidenzbasierte Wissensproduktion.

---

Hinweise/Referenzen:
- TECH Handover: `PROJECT_HUB/TECHNICAL_HANDOVER_GPT5_20250814.md`
- BE–FE‑Analyse: `PROJECT_HUB/BE_FE_DISCREPANCY_ANALYSIS_GPT5_20250814.md`
- Status/Protokoll: `PROJECT_HUB/SESSION_INIT_PROTOCOL2.md`
