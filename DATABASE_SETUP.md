# Knowledge Base Setup

## WICHTIG: Die Datenbank fehlt!

Die HAK-GAL Knowledge Base (`hexagonal_kb.db`) ist zu groß für Git (7.1 MB).

### Option 1: Download vom Release (Empfohlen)
```bash
# Linux/Mac:
./download_kb.sh

# Windows:
download_kb.bat
```

### Option 2: Manueller Download
1. Gehe zu: https://github.com/sookoothaii/HAK-GAL-Hexagonal/releases
2. Lade `hexagonal_kb.db` herunter
3. Platziere sie im Hauptverzeichnis

### Option 3: Neue DB erstellen
```bash
python scripts/create_database.py
python scripts/import_jsonl_to_sqlite.py creative_facts/all_creative_facts.jsonl
```

## Überprüfung
Die Datei sollte ~7.1 MB groß sein und 6,631 Fakten enthalten.

Ohne diese Datei wird das System NICHT starten!
