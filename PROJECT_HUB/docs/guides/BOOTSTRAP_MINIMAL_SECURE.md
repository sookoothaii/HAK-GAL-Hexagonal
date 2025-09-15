---
title: "HAK_GAL Bootstrap Minimal - Security Compliant"
created: "2025-09-15T15:00:00Z"
author: "claude-opus-4.1"
topics: ["guides"]
tags: ["bootstrap", "security", "minimal"]
privacy: "internal"
summary_200: |-
  Minimal, security-compliant bootstrap for HAK_GAL. No exposed secrets, correct API syntax,
  validated functions only. Uses placeholders for sensitive data. Follows both HAK_GAL Constitution
  and PH-LIP protocols. Essential information for productive work without security risks.
---

# HAK_GAL Bootstrap - Minimal Security-Compliant Version

## 1. Critical Values (Use Environment Variables)
```bash
export HAKGAL_AUTH_TOKEN="<YOUR_TOKEN_HERE>"  # Never commit real token
export HAKGAL_DB_PATH="D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
```

## 2. Correct API Syntax
```python
# Knowledge Base Operations (READ)
hak-gal.kb_stats()
hak-gal.search_knowledge(query="topic", limit=10)
hak-gal.get_recent_facts(count=5)

# Knowledge Base Operations (WRITE - requires token)
import os
token = os.environ.get('HAKGAL_AUTH_TOKEN')
hak-gal.add_fact(
    statement="Fact(Subject, Object)",
    auth_token=token  # From environment, not hardcoded
)

# File Operations
hak-gal-filesystem.list_files(path="...", pattern="*.md")
hak-gal-filesystem.read_file(path="...")
hak-gal-filesystem.write_file(
    path="...", 
    content="...",
    auth_token=token
)
```

## 3. System Architecture
- API Port: 5002
- Frontend: 5173
- Database: SQLite (4242+ facts)
- Governance: V3 (Pragmatic)

## 4. Document Routing (per routing_table.json v1.2)
```yaml
topics: ["guides"]     → docs/guides/
topics: ["system"]     → docs/system/
topics: ["analysis"]   → analysis/
topics: ["meta"]       → docs/meta/
```

## 5. Session Management (Required)
```python
# Start of session
session_id = f"{model_name}_{timestamp}"
hak-gal.add_fact(
    statement=f"SessionActive({session_id}, Start)",
    auth_token=token
)

# End of session
hak-gal.add_fact(
    statement=f"SessionCompleted({session_id}, Summary)",
    auth_token=token
)
```

## 6. Validation Commands
```bash
# Ensure no secrets in repo
grep -r "auth_token=" . | grep -v "YOUR_TOKEN_HERE"  # Should return 0
grep -r "hak-gal:" .     # Should return 0 (wrong syntax)
```

---
*Security-compliant version following HAK_GAL Constitution Article 1.1 (No silent failures)*
