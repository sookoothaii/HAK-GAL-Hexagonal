# Multi-Agent Authentication Guide für Cursor

## API-Key für HAK/GAL Multi-Agent System:
```
HAKGAL_API_KEY=hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d
```

## Verwendung in Cursor:

### Option 1: Im Tool-Call
```python
delegate_task(
    target_agent='claude_cli',
    task_description='Deine Aufgabe hier...',
    context={'key': 'value'},
    headers={'X-API-Key': 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d'}
)
```

### Option 2: Als Environment Variable
```bash
export HAKGAL_API_KEY=hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d
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
