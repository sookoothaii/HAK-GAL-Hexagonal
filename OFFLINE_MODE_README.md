# HAK_GAL Offline-Modus Optimierung

## Zusammenfassung der Änderungen

Die LLM-Provider wurden für schnelle Offline-Erkennung optimiert:

### 1. **Schnellere Offline-Erkennung (300ms statt 2s)**
- DNS-basierte Prüfung mit 300ms Timeout
- Keine HTTP-Requests mehr für Connectivity-Check
- Sofortige Umschaltung auf Ollama bei Offline-Status

### 2. **Dynamische Fehlerbehandlung**
- Nach 2 Verbindungsfehlern automatisch zu Ollama wechseln
- Erkennung von Connection-Errors während der Laufzeit
- Keine weiteren Online-Provider-Versuche nach erkanntem Offline-Status

### 3. **Verbesserte Fehlererkennung**
- Erweiterte Liste von Verbindungsfehler-Indikatoren
- Unterscheidung zwischen API-Fehlern und Verbindungsfehlern
- Automatisches Fallback bei Netzwerkproblemen

## Verwendung

### Manueller Offline-Modus:
```bash
export HAK_GAL_OFFLINE_MODE=true
python main.py
```

### Automatische Erkennung:
- System erkennt automatisch fehlende Internetverbindung
- DNS-Check in 300ms entscheidet über Online/Offline-Status
- Bei Verbindungsfehlern während Laufzeit: Auto-Switch zu Ollama

## Performance-Verbesserung

**Vorher:** 
- Bei Offline: ~51 Sekunden (alle Provider durchprobieren)
- Jeder Provider-Timeout: 10-30 Sekunden

**Nachher:**
- Bei Offline: <1 Sekunde bis Ollama startet
- DNS-Check: 300ms
- Automatisches Fallback nach 2 Fehlern

## Konfigurationsoptionen

1. `HAK_GAL_OFFLINE_MODE=true` - Erzwingt Offline-Modus
2. `OLLAMA_MODEL=qwen2.5:7b` - Wählt Ollama-Modell
3. Ohne API-Keys: Automatisch Offline-Modus

## Testing

```bash
# Test Offline-Modus
export HAK_GAL_OFFLINE_MODE=true
curl -X POST http://localhost:5000/api/llm/get-explanation -H "Content-Type: application/json" -d '{"query":"test"}'

# Test mit simuliertem Netzwerkausfall
# (Internetverbindung trennen und testen)
```
