# HAK/GAL Webscraper

Dieser Webscraper extrahiert Daten von der HAK/GAL Wissensdatenbank über die API.

## Benötigte Bibliotheken

```bash
pip install requests beautifulsoup4 pandas matplotlib
```

## Ausführung

1. Stelle sicher, dass der HAK/GAL MCP Server läuft (Port 5002)
2. Führe den Code aus: `python hak_gal_scraper.py`
3. Die Ergebnisse werden im Ordner `output` gespeichert

## Output-Dateien

- `hak_gal_data.json` - Rohdaten im JSON-Format
- `hak_gal_data.csv` - Rohdaten im CSV-Format
- `statement_counts.png` - Diagramm der Statement-Häufigkeiten
- `tag_counts.png` - Diagramm der Tag-Häufigkeiten
- `report.html` - HTML-Report mit Statistiken
- `scraper.log` - Log-Datei mit detaillierten Informationen

## Funktionen

- **Daten-Extraktion**: Holt Fakten von der HAK/GAL API
- **Datenanalyse**: Analysiert Häufigkeiten von Statements und Tags
- **Visualisierung**: Erstellt Charts mit matplotlib
- **Export**: Speichert Daten in verschiedenen Formaten
- **Reporting**: Generiert HTML-Report

## Anpassungen

Der Code ist für die HAK/GAL API optimiert. Für andere APIs müssen die folgenden Parameter angepasst werden:

- `URL`: API-Endpoint
- `headers`: Authentifizierung
- `scrape_data()`: Daten-Extraktion an API-Response anpassen

## Erstellt von

- **Gemini**: Code-Generierung
- **Cursor**: IDE-Integration und Testing
- **OpenCode**: Live-Validierung
- **Multi-Agent System**: Kollaborative Entwicklung
