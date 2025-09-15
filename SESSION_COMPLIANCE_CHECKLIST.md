# HAK_GAL SESSION COMPLIANCE CHECKLIST
# Zeige diesen Bericht jeder LLM-Instanz VOR dem finalen Speichern
# Stand: 2025-01-28 | Version: 1.0

## ZWECK
Diese Datei dient zur Selbstvalidierung. Prüfe ob du dich an alle Regeln gehalten hast.

## KRITISCHE REGELN - HAST DU DIESE BEFOLGT?

### 1. DOKUMENT-ABLAGE ✓/✗
- [ ] Alle neuen .md Dateien haben vollständiges Frontmatter (7 Felder)
- [ ] topics[0] bestimmt den Ordner (laut routing_table.json)
- [ ] KEINE neuen Dateien ins HAK_GAL_HEXAGONAL Root (außer diesem Bericht)
- [ ] Neue Dateien in PROJECT_HUB korrekt unter docs/* abgelegt
- [ ] summary_200 ist tatsächlich unter 200 Wörtern

**Häufiger Fehler:** Dateien ins Root statt PROJECT_HUB/docs/*/

### 2. KNOWLEDGE BASE INTEGRITÄT ✓/✗
- [ ] Nur validierte Prädikate verwendet (HasProperty, Causes, etc.)
- [ ] Auth Token ${HAKGAL_AUTH_TOKEN} bei Schreiboperationen
- [ ] Keine Duplikate hinzugefügt (System prüft automatisch)
- [ ] Fakten im Format: Subject(Predicate, Object)

**Häufiger Fehler:** Fakten ohne Validierung speichern

### 3. MOJO/CPP REGEL ✓/✗
- [ ] KEIN neues Dokument mit topics: ["mojo"] erstellt
- [ ] C++ Content hat topics wie "technical_reports" mit tag "cpp"
- [ ] Legacy Mojo-Docs unverändert gelassen

**Häufiger Fehler:** "mojo" als Topic für neue C++ Inhalte

### 4. FRONTMATTER TEMPLATE ✓/✗
```yaml
---
title: "..."
created: "2025-01-28T..."  # HEUTE oder aktuelles Datum
author: "claude/gpt5/deepseek/gemini"
topics: ["..."]  # ARRAY, nicht String!
tags: [...]
privacy: "internal"
summary_200: |-
  Max 200 Wörter...
---
```

- [ ] created ist NICHT in der Zukunft (kein September 2025!)
- [ ] topics ist ein Array, kein String
- [ ] author ist dein Model-Name

### 5. VALIDIERUNG ✓/✗
- [ ] validate_hub.py würde Exit Code 0 liefern
- [ ] Keine neuen Errors eingeführt
- [ ] Cutoff-Datum beachtet (28.01.2025)

## SELBST-ASSESSMENT

**Beantworte ehrlich:**

1. **Habe ich Dateien ins Root gelegt die nicht dorthin gehören?**
   → JA/NEIN: _______
   
2. **Habe ich das Routing-System korrekt verwendet?**
   → JA/NEIN: _______
   
3. **Sind alle meine Fakten validiert und mit Token gespeichert?**
   → JA/NEIN: _______

4. **Habe ich mich an PH-LIP gehalten?**
   → JA/NEIN: _______

## TYPISCHE VERSTÖSSE (aus Erfahrung)

1. **Claude am 28.01.2025:** Legte 2 Dateien ins Root statt docs/guides und docs/system
2. **GPT5 September 2025:** Nutzte "mojo" als Topic für neue Docs
3. **Diverse LLMs:** Vergessen Frontmatter bei neuen Dateien
4. **Alle:** Verwenden topic: statt topics: (Singular statt Array)

## FINALE AKTION

**WENN alle Checkboxen ✓:**
```python
# Speichere deine Arbeit
hak-gal:add_fact(
    statement=f"SessionCompleted({model_name}, {date}, Compliant)",
    auth_token="${HAKGAL_AUTH_TOKEN}"
)
```

**WENN mindestens eine ✗:**
```python
# Korrigiere ERST die Fehler, dann:
hak-gal:add_fact(
    statement=f"SessionCompleted({model_name}, {date}, CorrectedErrors)",
    auth_token="${HAKGAL_AUTH_TOKEN}"
)
```

## NOTIZEN FÜR DIESE SESSION

_Füge hier spezifische Hinweise für die aktuelle Session ein:_

- Session-ID: 2025-01-28-claude-opus-4.1
- Hauptaufgabe: Routing-System Finalisierung
- Erstellte Docs: 4 (ROUTING_FINALIZATION_REPORT, validate_hub.py v2, UNIVERSAL_BOOTSTRAP, PORT_SERVICE_MAPPING)
- Behobene Fehler: 3 Catalog-Dateien gefixed
- **MEIN FEHLER:** Legte zunächst 2 Dateien ins Root, dann korrigiert nach docs/guides und docs/system

---
**DIESE DATEI BLEIBT IM ROOT** als Meta-Dokument für Session-Validierung.
Zeige sie JEDER neuen Instanz vor dem finalen Speichern.