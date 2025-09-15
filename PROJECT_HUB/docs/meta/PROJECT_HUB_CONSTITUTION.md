---
doc_id: "PHUB-CONSTITUTION-v1-2025-09"
title: "PROJECT_HUB Constitution (v1.0)"
topics: ["governance","meta"]
tags: ["constitution","ssot","catalog","frontmatter"]
privacy: "internal"
status: "active"
author_agent: "Claude-Opus-4.1"
model: "claude-opus-4-1-20250805"
summary_200: "Die PROJECT_HUB Constitution definiert Ziele, Prinzipien, Struktur, Metadaten-Standards, Katalog-/Snapshot-Pflege, Schreib-/Auditregeln und Konfliktlösungen. Sie macht FS-Zeitstempel kanonisch, verlangt kurze 200-Wort-Abstracts pro Dokument, etabliert eine klare Kapitel-/Ordner-Taxonomie und erlaubt einen pragmatischen, zweistufigen Übergang (Minimal-Frontmatter → Voll-Frontmatter). Historische „Mojo"-Inhalte werden als C++ alias cpp behandelt. Ziel ist eine LLM-geeignete Ordnung, die Menschen intuitiv verstehen."
---

# PROJECT_HUB Constitution (v1.0)

## 1. Zweck & Geltungsbereich
Der `PROJECT_HUB` ist das zentrale Wissens- und Arbeitsverzeichnis für Menschen und LLM-Agenten. Diese Constitution regelt **Ordnung, Benennung, Metadaten, Katalogisierung, Schreib- & Auditregeln** sowie **Konfliktlösungen** – mit Fokus auf **LLM-Tauglichkeit** und **menschliche Verständlichkeit**.

## 2. Grundprinzipien
1. **SSoT-Vorrang:** `ssot.md` hat Vorrang vor allen anderen Dokumenten.
2. **FS-Zeitstempel sind kanonisch:** Originale Dateisystem-Zeitstempel (created/modified) gelten als Quelle der Wahrheit. Datumsangaben im Text können abweichen.
3. **Abstracts ≤ 200 Wörter:** Jedes inhaltliche `*.md` führt eine prägnante `summary_200`.
4. **Datenminimierung & Privacy:** Nur notwendige Inhalte speichern; `privacy` regelt Sichtbarkeit.
5. **Nachvollziehbarkeit:** Änderungen sind auditierbar (Frontmatter, Change-Log, ggf. Tool-Audit).
6. **LLM-Erst, menschlich-klar:** Schema, Sprache und Struktur sind für LLM-Parsing optimiert, bleiben aber für Menschen lesbar.

## 3. Kapitel-/Ordner-Taxonomie
- `docs/design_docs/` – Architektur, Designs, Roadmaps  
- `docs/guides/` – Anleitungen/Setup/How-tos  
- `docs/handovers/` – Übergaben/Protokolle  
- `docs/mcp/` – MCP Tools/Compliance/Status  
- `docs/meta/` – Verfassungen, SSoT, dieses Dokument  
- `docs/migration/` – Migrationen, Pläne, Ergebnisse  
- `docs/mojo/` – **historisch** „Mojo" → als **C++** alias `cpp` behandeln  
- `docs/snapshots/` – Kataloge & Indizes  
- `analysis/` – Audits, Analysen, Statusberichte

**Mojo→C++ Regel:** Bestehende „mojo"-Dateien bleiben; zusätzlich Tag `cpp`. Neue Inhalte nutzen `cpp` statt `mojo`.

## 4. Dateinamen
Empfohlenes Muster:
```
TOPIC_SUBTOPIC[_MODEL][_ID]_YYYYMMDD[_HHMMSS].md
```
Beispiele:  
`MCP_TOOLS_COMPLETE_V2_20250814.md`  
`CPP_PERFORMANCE_ANALYSIS_20250816.md`

## 5. Frontmatter – Minimal vs. Voll
**Minimal (Phase 1 – Quick Wins):**
```yaml
title: "Kurztitel"
topics: ["kapitel1","kapitel2"]
tags: ["schlagwort1","cpp"]
privacy: "internal"      # public|internal|private
summary_200: "Kurzabstract ≤ 200 Wörter."
```

**Voll (Phase 2+):**
```yaml
doc_id: "PHUB-<ulid>"
title: "Kurztitel"
topics: ["..."]
tags: ["..."]
privacy: "internal"
status: "active"         # draft|active|deprecated
author_agent: "GPT5"
model: "gpt-5-thinking"
created_fs: "YYYY-MM-DDThh:mm:ssZ"
modified_fs: "YYYY-MM-DDThh:mm:ssZ"
content_claimed_date: "optional"
related_ids: []
source_files: []
checksum: "<sha256 optional>"
summary_200: "≤ 200 Wörter."
```

## 6. Abstract-Regel (`summary_200`)
* Max. 200 Wörter, vollständiger inhaltlicher Mini-Abstract (Wer/Was/Warum/Wie/Ergebnis).
* Keine Platzhalter und keine TODO-Listen.

## 7. Kataloge & Snapshots
* **Tageskatalog:** `docs/snapshots/catalog_YYYYMMDD.md` (Tabelle mit Path, Title, Summary_200, Topics, Tags, Created_FS, Modified_FS, Doc_ID, Privacy, Status).
* **Index (Maschine):** `docs/snapshots/catalog_index.json`.
* **`catalog_latest.md`** spiegelt den jüngsten Katalog.
* Erstellung: täglich und on-demand nach Massenänderungen.

## 8. Rollen & Verantwortungen
* **Menschen:** Review, Priorisierung, Governance.
* **Orchestrator-Agent:** Katalogpflege, Indizes, Konsistenz, Delegation.
* **Spezial-Agenten:** Inhalte erstellen/aktualisieren gemäß dieser Constitution.

## 9. Schreib- & Auditregeln
* Frontmatter **vor** Inhalt; FS-Zeitstempel pflegen.
* Relevante Fakten → **KB** via Quality-Gate (nicht roh aus LLM-Antworten).
* Change-Log Block im Dokument für wichtige Änderungen.

## 10. Konflikte & Deprecation
* **Merge vor Überschreiben.**
* Deprecation mit `status: deprecated`, statt sofort zu löschen.
* Historische Divergenz (Textdatum ≠ FS): Hinweis im Abstract.

## 11. Übergangsplan (pragmatisch)
1. **Phase 1:** Katalog erzeugen; neue Dateien mit **Minimal-Frontmatter**; Abstracts für neue Inhalte.
2. **Phase 2:** Top-20 Bestandsdokumente nachrüsten (Voll-Frontmatter), `analysis/` konsolidieren, JSON-Index aufbauen.
3. **Phase 3 (optional):** Checksums/Locks bei Bedarf für kritische Dokumente.

*Ende v1.0 – Änderungen an der Constitution erfordern Review.*