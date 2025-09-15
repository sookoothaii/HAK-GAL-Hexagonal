---
title: "Claude Setup Guide"
created: "2025-09-15T00:08:00.994662Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Claude Integration Setup Guide

## Problem Diagnose
Das ursprüngliche `claude_cli_watcher.py` Script hatte zwei Probleme:
1. **Falsche CLI-Verwendung**: Verwendete direkte Argumente statt piped input
2. **Authentifizierungsproblem**: Claude CLI benötigt API-Key oder Credits

## Lösungen

### Lösung 1: Korrigiertes CLI Script
Das aktualisierte `claude_cli_watcher.py` verwendet jetzt die korrekte piped input Methode.

**Voraussetzungen:**
- Claude CLI installiert (`npm install -g @anthropic-ai/claude`)
- API-Key konfiguriert in Claude CLI
- Ausreichende Credits

**Test:**
```bash
# Teste die CLI direkt
echo "Hello Claude" | claude
```

### Lösung 2: API-Integration (Empfohlen)
Das neue `claude_api_watcher.py` Script verwendet die Anthropic API direkt.

**Voraussetzungen:**
- Anthropic API Key
- Internet-Verbindung

**Setup:**
```bash
# API Key als Environment Variable setzen
set ANTHROPIC_API_KEY=your_api_key_here

# Oder in .env Datei
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

**API Key erhalten:**
1. Gehe zu https://console.anthropic.com/
2. Erstelle einen Account
3. Generiere einen API Key
4. Füge Credits hinzu (kostenpflichtig)

## Verwendung

### CLI Version (wenn Credits verfügbar):
```bash
python scripts/claude_cli_watcher.py
```

### API Version (empfohlen):
```bash
python scripts/claude_api_watcher.py
```

## Test der Integration

### 1. Manueller Test:
```bash
# Erstelle eine Test-Task
echo '{"id": "test_123", "task": "Say hello and confirm you are operational", "context": {}}' > claude_cli_exchange/task_test_123.json

# Starte den Watcher
python scripts/claude_api_watcher.py
```

### 2. Über HAK/GAL API:
```bash
curl -X POST "http://127.0.0.1:5002/api/agent-bus/delegate" \
  -H "X-API-Key: hg_sk_${HAKGAL_AUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"target_agent": "claude_cli", "task_description": "Hello Claude", "context": {}}'
```

## Fehlerbehebung

### "Credit balance is too low"
**Ursache:** Nicht genügend Credits in Claude Account
**Lösung:** Füge Credits hinzu oder verwende API Version

### "ANTHROPIC_API_KEY environment variable not set"
**Ursache:** API Key nicht konfiguriert
**Lösung:** Setze ANTHROPIC_API_KEY Environment Variable

### Return Code 1
**Ursache:** CLI-Authentifizierungsproblem
**Lösung:** Verwende API Version oder konfiguriere CLI richtig

## Empfehlung

**Verwende die API-Version (`claude_api_watcher.py`)** für:
- Zuverlässigere Integration
- Bessere Fehlerbehandlung
- Keine Credit-Abhängigkeit von CLI
- Direkte Kontrolle über Model und Parameter

Die API-Version ist die robustere und empfohlene Lösung für die HAK/GAL Integration.