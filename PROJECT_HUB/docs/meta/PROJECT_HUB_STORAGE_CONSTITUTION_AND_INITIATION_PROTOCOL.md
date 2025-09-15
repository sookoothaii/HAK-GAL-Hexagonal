---
doc_id: "PHUB-STORAGE-INIT-v1-2025-09"
title: "Project Hub Storage Constitution & Initiation Protocol (v1.0)"
topics: ["governance","meta","snapshots"]
tags: ["initiation","catalog","frontmatter","cpp-alias"]
privacy: "internal"
status: "active"
author_agent: "Claude-Opus-4.1"
model: "claude-opus-4-1-20250805"
summary_200: "Operative Regeln für LLM-freundliche Ablage, Katalogisierung und Initialisierung neuer Agenten. Definiert Frontmatter (Minimal/Voll), Abstract-Pflicht, FS-Zeitstempel als kanonische Quelle, Tageskatalog & JSON-Index, Mojo→C++ Alias, Konfliktbehandlung und einen klaren Schritt-für-Schritt-Start („Initiationsprotokoll") für neue LLM-Instanzen."
---

# Project Hub Storage Constitution & Initiation Protocol (v1.0)

## 1) Leitprinzipien
1. **SSoT Vorrang:** `ssot.md` dominiert bei Konflikten.  
2. **Kanonisch:** `created_fs`/`modified_fs` aus dem Dateisystem.  
3. **Abstracts:** Jedes Inhalts-Markdown mit `summary_200` (≤ 200 Wörter).  
4. **Mojo→C++ Alias:** Historische „mojo"-Dokumente zusätzlich mit Tag `cpp`; neue Inhalte nutzen `cpp`.  
5. **Privacy by Design:** `privacy: public|internal|private`.

## 2) Ordner & Themen
Siehe Constitution §3. Zusätzlich:
- `analysis/` für Audits/Statusberichte.
- `docs/snapshots/` für Tageskataloge & Indizes.

**Thematische Tags (Auszug):** `architecture`, `mcp`, `agents`, `kb`, `data`, `devops`, `sentry`, `migration`, `cpp`, `frontend`, `cursor`, `research`, `strategy`, `handovers`, `governance`, `snapshots`, `meta`.

## 3) Frontmatter-Standards
**Minimal (Phase 1):**
```yaml
title: "Kurztitel"
topics: ["kapitel"]
tags: ["stichwort","cpp"]
privacy: "internal"
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

## 4) Kataloge & Indizes

### 4.1 Tageskatalog (Markdown)
Pfad: `docs/snapshots/catalog_YYYYMMDD.md`
Tabellenkopf:
```
| Path | Title | Summary_200 | Topics | Tags | Created_FS | Modified_FS | Doc_ID | Privacy | Status |
```

### 4.2 JSON-Index (maschinell)
Pfad: `docs/snapshots/catalog_index.json`
Schema (informell):
```json
[
  {
    "path": "D:/.../ARCHITECTURE_OVERVIEW.md",
    "title": "ARCHITECTURE OVERVIEW",
    "topics": ["architecture"],
    "tags": ["overview"],
    "privacy": "internal",
    "status": "active",
    "doc_id": "PHUB-01H...",
    "created_fs": "2025-08-16T10:15:00Z",
    "modified_fs": "2025-08-16T12:20:00Z",
    "summary_200": "…"
  }
]
```

`catalog_latest.md` spiegelt den jüngsten Katalog.

### 4.3 Rotation
Mindestens 30 Tageskataloge aufbewahren; ältere bei Bedarf archivieren.

## 5) Schreib- & Update-Pflichtpfad (LLM/Skripte)
1. **Preflight:** `ssot.md` + dieses Protokoll lesen; `catalog_latest.md` prüfen.
2. **Lokalisieren:** Relevante Kapitel/Topics im Katalog/Index finden.
3. **Erstellen:** Neues Dokument mit **Minimal-Frontmatter** (oder Voll, wenn möglich) + `summary_200`.
4. **Aktualisieren:** Inhalt pflegen; FS-Zeitstempel respektieren; Change-Log Abschnitt ergänzen.
5. **Katalogpflege:** Katalogeintrag & JSON-Index aktualisieren/erzeugen.
6. **Faktenableitung:** Verifizierbare Aussagen in die KB (Quality-Gate, Audit).

## 6) Konflikte & Locks
* **Merge bevorzugt;** keine stillen Überschreibungen.
* Bei Bedarf leichter Lock-Hinweis: `.locks/{doc_id}.lock` (optional, aufzuräumen).
* Divergenzen (Textdatum vs. FS) im Abstract knapp erwähnen.

## 7) Qualitätskriterien `summary_200`
* Max. 200 Wörter, prägnant (Wer/Was/Warum/Wie/Ergebnis).
* Keine Floskeln, keine TODO-Listen.
* Für historische Files: 1-Satz Hinweis bei Datumsmismatch.

## 8) Beispiel-Skelett für neue Dokumente
```markdown
---
title: "ARCHITECTURE OVERVIEW (v2)"
topics: ["architecture"]
tags: ["overview"]
privacy: "internal"
summary_200: "Dieses Dokument fasst die Architektur … (≤ 200 Wörter)."
---

# Architektur – Überblick
(…)
```

## 9) Initiationsprotokoll für neue LLM-Instanzen
1. **Handshake:** Melde `agent_name`, `model_id`, `session_id`.
2. **Kanon laden:** `ssot.md`, **diese Datei**, `docs/snapshots/catalog_latest.md`.
3. **Index prüfen/erzeugen:** Falls `catalog_index.json` fehlt oder alt ist, neu erzeugen.
4. **Scope wählen:** Nur relevante Kapitel/Topics laden.
5. **Arbeiten & Schreiben:** Ergebnisse als Markdown mit Frontmatter + `summary_200` im passenden Kapitel.
6. **Katalogpflege:** Katalog & Index aktualisieren.
7. **Fakten persistieren:** Nur geprüfte Fakten in DB (Quality-Gate/Audit).
8. **Abschluss:** Kurzreport unter `analysis/` (mit Links/IDs).

## 10) Pragmatiker-Modus (Sanfte Einführung)
* **Phase 1:** Katalog generieren; neue Inhalte mit Minimal-Frontmatter; Abstracts nur für neue Dateien.
* **Phase 2:** Top-20 Bestandsdokumente nachrüsten (Voll-Frontmatter), `analysis/` konsolidieren, JSON-Index aufbauen.
* **Phase 3 (optional):** Checksums/Locking für kritische Dokumente.

## 11) Sicherheit & Compliance
* Privacy beachten (`public|internal|private`).
* Keine sensiblen Daten ohne Freigabe.
* Backups/Kataloge priorisiert sichern.

*Ende v1.0 – Änderungen erfordern Review.*