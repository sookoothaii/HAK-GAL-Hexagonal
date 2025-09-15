---
title: "Cursor Auth Guide"
created: "2025-09-15T00:08:01.011292Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Multi-Agent Authentication Guide für Cursor

## API-Key für HAK/GAL Multi-Agent System:
```
HAKGAL_API_KEY=hg_sk_${HAKGAL_AUTH_TOKEN}
```

## Verwendung in Cursor:

### Option 1: Im Tool-Call
```python
delegate_task(
    target_agent='claude_cli',
    task_description='Deine Aufgabe hier...',
    context={'key': 'value'},
    headers={'X-API-Key': 'hg_sk_${HAKGAL_AUTH_TOKEN}'}
)
```

### Option 2: Als Environment Variable
```bash
export HAKGAL_API_KEY=hg_sk_${HAKGAL_AUTH_TOKEN}
```

### Option 3: In der Tool-Konfiguration
Die Tool-Definition muss den API-Key im Header inkludieren.

## Test-Beispiel für Cursor:
```python
# Cursor kann das testen:
result = delegate_task(
    target_agent='claude_cli',
    task_description='Sage: Hallo von Cursor! Multi-Agent funktioniert!',
    context={'sender': 'cursor', 'test': True}
)
```

## Verfügbare Agents:
- `claude_cli` - Funktioniert automatisch (wenn API-Budget vorhanden)
- `claude_desktop` - Öffnet Claude Desktop (manuell)
- `cursor` - Würde zu Cursor selbst zurückkommen (Loop!)
