# HAK‑GAL Human Reasoning Model (HRM) – Überblick und Betriebsleitfaden

Ziel: Dies ist die Initialinfo für neue Instanzen, um das integrierte Human Reasoning Model (HRM, ~600k Parameter) zielgerichtet zu nutzen. Sie beschreibt Zweck, Einbindung in die Hexagonal‑Architektur, Schnittstellen, Sicherheitsregeln, Metriken sowie bewährte Workflows.

## 1) Zweck und Rolle im System
- Ergänzt die wissensbasierte, symbolische Komponente (Fakten in `statement`‑Form) um leichtgewichtige, begründbare Schlussfolgerungen.
- Dient als „Reihenfolge‑ und Auswahl‑Heuristik“ für:
  - welche Fakten/Beweise zuerst geprüft werden
  - welche MCP‑Tools mit welchen Parametern aufgerufen werden
  - wann eine Konsistenzprüfung sinnvoll ist
- Liefert nachvollziehbare Reasoning‑Spuren (Ketten kurzer, begründeter Schritte), keine „freie Halluzination“.

## 2) Einbettung in die Hexagonale Architektur
- Port: `ReasoningPort` (konzeptionell) – nimmt Eingaben (Ziel, Kontext, Kandidaten) entgegen und produziert geordnete Handlungsvorschläge.
- Adapter: HRM‑Adapter realisiert diesen Port und wird von Use‑Cases aufgerufen (z. B. vor `consistency_check`, `query_related`, `bulk_delete`).
- Datenfluss (vereinfacht):
  1. Kontext sammeln (Project‑Hub Digest, `get_predicates_stats`, `query_related`)
  2. HRM erhält Ziel + verdichteten Kontext
  3. HRM priorisiert Schritte/Tool‑Aufrufe
  4. Ausführung über MCP‑Tools, Validierung, optional Schleife

## 3) Modellcharakteristik (high‑level)
- Größe: ca. 600k Parameter (leichtgewichtig, deterministisch konfigurierbar)
- Fokus: logische Mikro‑Schritte, Heuristiken für Reihenfolge/Abdeckung, Konsistenzwächter
- Output: strukturierte „Reasoning‑Plan“ Artefakte (z. B. JSON mit Schritten, Begründung, erwarteten Ergebnissen)

## 4) Schnittstellen (Input/Output‑Formate)
Input (empfohlen):
- `goal`: natürlichsprachliches Ziel oder formale Zielaussage
- `context_facts`: kleine Menge relevanter Fakten (z. B. aus `query_related`)
- `constraints`: Richtlinien (z. B. „read‑only“, „keine destructive Ops“)
- `resources`: welche MCP‑Tools und Limits erlaubt sind

Output (empfohlen):
- `plan`: geordnete Schritte (Tool, Parameter, Erwartung)
- `justification`: Kurzbegründung/Heuristik pro Schritt
- `stop_conditions`: wann abbrechen/eskalieren

Hinweis: Das HRM erzeugt Vorschläge; die Ausführung erfolgt ausschließlich über MCP‑Tools (Audit‑fähig).

## 5) Sicherheits- und Governance‑Regeln
- Write‑Operationen nur wenn `HAKGAL_WRITE_ENABLED=true` und Token gültig
- HRM‑Pläne dürfen keine direkten Side‑Effects verursachen; Ausführung über Use‑Cases/MCP
- Konsistenz vor Masse: bei Widerspruchsverdacht zuerst `consistency_check`
- Audit: Alle write‑relevanten Folgen werden durch Tools geloggt (`mcp_write_audit.log`)

## 6) Evaluationsmetriken
- Korrektheit: Anteil erfüllter Ziele vs. Fehlversuche
- Konsistenz: keine Widersprüche laut `consistency_check`
- Coverage: Anteil relevanter Fakten, die geprüft wurden
- Effizienz: Schritte bis Ziel, Latenz pro Schritt
- Reproduzierbarkeit: deterministische Pläne bei gleichem Kontext

Empfohlener Mini‑Benchmark (on‑demand):
- 10 Syllogismen, 10 Implikationen, 10 Negationen, 10 Kant‑Faktenketten – protokolliere Erfolgsquote und Schritte

## 7) Konfiguration (ENV, empfohlen)
- `HAKGAL_HUB_PATH` – Project‑Hub Ordner (Digest/Snapshots als Startkontext)
- `HAKGAL_WRITE_ENABLED`, `HAKGAL_WRITE_TOKEN` – Gate für Write‑Folgen von HRM‑Plänen (indirekt über Tools)
- Optional: `HAKGAL_AUTO_DIGEST_ON_INIT` – Digest automatisch laden und als Kontext an HRM/Use‑Case geben

## 8) Bewährte Workflows
A) Session‑Start („Kontext aufbauen“)
1. `project_hub_digest` laden (letzte Snapshots)
2. `get_predicates_stats`, `query_related(entity='ImmanuelKant')` für Fokus
3. HRM mit `goal` + kondensiertem Kontext füttern → Plan erzeugen
4. Plan schrittweise via MCP‑Tools ausführen; nach jedem Schritt validieren

B) KB‑Pflege („Qualität sichern“)
1. `validate_facts` → Fehler beheben
2. `analyze_duplicates`/`semantic_similarity` → Kandidaten prüfen
3. HRM‑Plan für konfliktarme Löschung/Updates → `bulk_delete`/`update_fact`

C) Handover („Session dokumentieren“)
1. `project_snapshot(title, description)`
2. Optional HRM‑Plan (als JSON/Markdown) in Snapshot‑Ordner ablegen

## 9) Interaktion mit bestehenden Tools
- Vor‐Filter: HRM priorisiert, welche `query_related`/`search_by_predicate` zuerst laufen
- Nachkontrolle: HRM schlägt `consistency_check` an kritischen Punkten vor
- Monitoring‑Hinweise: Bei wachsender KB `growth_stats` periodisch prüfen

## 10) Limitierungen und Leitplanken
- Kein Ersatz für formale Beweise; HRM ist Heuristik, nicht Beweiser
- Keine direkten Datei‑/KB‑Side‑Effects – immer über MCP‑Tools gehen
- Kontextfenster begrenzen (Digest/verdichtete Fakten statt Voll‑Dump)

## 11) Beispieleingaben (Startbausteine)
- „Ziel: Finde alle Kernbeziehungen zu Immanuel Kant und prüfe Duplikate.“
- Kontext: `project_hub_digest` (letzte 2 Snapshots) + `query_related('ImmanuelKant', limit=50)`
- HRM‑Plan (Beispielstruktur):
```json
{
  "plan": [
    {"step": 1, "tool": "query_related", "args": {"entity": "ImmanuelKant", "limit": 50}, "why": "Kontext sammeln"},
    {"step": 2, "tool": "semantic_similarity", "args": {"statement": "HatTeil(ImmanuelKant, DingAnSich)", "threshold": 0.85}, "why": "Ähnliche Aussagen gruppieren"},
    {"step": 3, "tool": "analyze_duplicates", "args": {"threshold": 0.9, "max_pairs": 200}, "why": "Duplikate prüfen"},
    {"step": 4, "tool": "consistency_check", "args": {"limit": 1000}, "why": "Widersprüche vermeiden"}
  ]
}
```

## 12) Was eine neue Instanz sofort tun kann
- „Use hak-gal project_hub_digest.“ – kompakten Kontext laden
- „Use hak-gal get_predicates_stats.“ – Strukturüberblick
- „Use hak-gal query_related with entity='ImmanuelKant' and limit=50.“ – Fokusbereich
- Danach: HRM mit Ziel+Kontext speisen und Plan ausführen

Hinweis: Dieses Dokument ist bewusst pragmatisch; technische Tiefen (Implementierung, Parameter‑Tuning) können im Snapshot‑Ordner `SNAPSHOT_TECH.md` verlinkt oder als separate Spezifikation ergänzt werden.
