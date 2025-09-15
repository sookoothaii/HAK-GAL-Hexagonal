---
title: "Fix Backup Kb Bug"
created: "2025-09-15T00:08:01.103665Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Fix für backup_kb Bug
## Problem
Die backup_kb Funktion in hak_gal_mcp_sqlite_full.py wirft einen Fehler:
`cannot access local variable 're' where it is not associated with a value`

## Ursache
Obwohl `re` global importiert ist (Zeile 16), ist es in der backup_kb Funktion nicht verfügbar.
Dies kann in bestimmten Python-Ausführungskontexten passieren.

## Lösung
Import `re` direkt in der backup_kb Funktion (Zeile ~1260):

```python
elif tool_name == "backup_kb":
    desc = str(tool_args.get("description", "")).strip()
    auth_token = tool_args.get("auth_token", "")
    if not self._is_write_allowed(auth_token):
        result = {"content": [{"type": "text", "text": "Write disabled."}]}
    else:
        import re  # FIX: Import re locally to fix scope issue
        ts = time.strftime("%Y%m%d%H%M%S")
        # Rest des Codes...
```

## Anwendung
1. Fix wurde bereits angewendet in hak_gal_mcp_sqlite_full.py
2. **MCP Server muss neu gestartet werden** für die Änderung
3. Nach Neustart funktioniert backup_kb mit Beschreibungen

## Workaround (ohne Neustart)
Nutze backup_kb OHNE description Parameter:
```python
backup_kb(auth_token="<YOUR_TOKEN_HERE>")
# Statt: backup_kb(description="test", auth_token="...")
```
