---
title: "HAK_GAL Unified Entry Point - Single Source of Truth"
created: "2025-09-15T18:15:00Z"
author: "claude-opus-4.1"
topics: ["meta"]
tags: ["bootstrap", "entry-point", "ssot", "unified", "critical"]
privacy: "internal"
summary_200: |-
  THE single entry point for all LLM agents. Resolves the three-way bootstrap conflict by
  providing clear, unified instructions. Combines PH-LIP's document management with agent_hub
  collaboration. 50 lines of clarity replacing 300+ lines of confusion. This is the ONLY
  bootstrap document agents should read first.
---

# 🎯 HAK_GAL UNIFIED ENTRY POINT
### THE Single Source of Truth for LLM Agents
### Version 2.0 - Resolving the Bootstrap Conflict

---

## ⚡ CRITICAL: Read This First

You have found THE authoritative entry point. Ignore any other "start here" documents.

**Other bootstrap documents are DEPRECATED:**
- ❌ ~~START_HERE_LLM.md~~ (deprecated)
- ⚠️ PH-LIP (now secondary reference)
- ⚠️ UNIVERSAL_BOOTSTRAP (now secondary reference)

---

## 📋 Your 5-Step Initialization

### 1️⃣ IDENTIFY YOURSELF
```python
print(f"Agent {model_name} initializing session {timestamp}")
# Example: "Agent claude-opus-4.1 initializing session 2025-09-15-18:00"
```

### 2️⃣ VERIFY SYSTEM
```python
hak-gal.kb_stats()  # Should return > 4000 facts
hak-gal.get_system_status()  # Should return "Operational"
```

### 3️⃣ UNDERSTAND YOUR WORKSPACE

**For Documents:**
- READ: `docs/meta/routing_table.json` - Where files go
- CHECK: `docs/snapshots/catalog_latest.md` - What exists
- WRITE: Follow routing_table rules (topics[0] = folder)

**For Collaboration:**
- YOUR SPACE: `agent_hub/{your_name}/` - Your work area
- OTHERS: `agent_hub/{other_agents}/` - Their work
- DIRECTIVES: `agent_hub/system/directives.md` - System tasks

### 4️⃣ DETERMINE PRIORITY

Priority order (highest first):
1. **User Request** - Direct user instruction
2. **System Directive** - From agent_hub/system/
3. **Collaboration Request** - From other agents
4. **Maintenance** - Catalog updates, cleanup

### 5️⃣ EXECUTE AND REPORT

```python
# Do your work
result = perform_task()

# Report to your hub
hak-gal-filesystem.write_file(
    path=f"agent_hub/{model_name}/reports/session_{timestamp}.md",
    content=result,
    auth_token="<YOUR_TOKEN_HERE>"
)

# Update catalog if you created documents
# (Automated by report_manager.py - run if available)
```

---

## 🗂️ Quick Reference

### Core Tools
```python
# Read Operations (No token needed)
hak-gal.kb_stats()
hak-gal.search_knowledge(query="...", limit=10)
hak-gal-filesystem.read_file(path="...")
hak-gal-filesystem.list_files(path="...", pattern="*.md")

# Write Operations (Token required)
hak-gal.add_fact(statement="...", auth_token="<YOUR_TOKEN_HERE>")
hak-gal-filesystem.write_file(path="...", content="...", auth_token="<YOUR_TOKEN_HERE>")
```

### Routing Rules (from routing_table.json)
- `topics: ["guides"]` → `docs/guides/`
- `topics: ["meta"]` → `docs/meta/`
- `topics: ["analysis"]` → `analysis/`
- `topics: ["technical_reports"]` → `docs/technical_reports/`

### Frontmatter Template
```yaml
---
title: "Descriptive Title"
created: "2025-09-15T18:00:00Z"
author: "your-model-name"
topics: ["primary_topic"]  # Array! First determines folder
tags: ["relevant", "tags"]
privacy: "internal"
summary_200: |-
  Concise summary under 200 words...
---
```

---

## 🚨 Common Pitfalls to Avoid

1. **DON'T** read deprecated bootstrap documents
2. **DON'T** use `hak-gal:` syntax (use `hak-gal.`)
3. **DON'T** expose tokens (use placeholders)
4. **DON'T** put files in root (use PROJECT_HUB subdirs)
5. **DON'T** skip frontmatter (all new docs need it)

---

## 📚 Secondary References

After initialization, these provide depth:
- **Document Management:** PH-LIP sections on routing
- **Agent Collaboration:** UNIVERSAL_BOOTSTRAP agent_hub section
- **Governance:** PROJECT_HUB_CONSTITUTION.md
- **Tool Details:** MCP_TOOLS_COMPLETE_V2.md

---

## ✅ Initialization Complete

You are now properly initialized. Your next step:
1. Check for user requests (highest priority)
2. Check `agent_hub/system/directives.md` for tasks
3. Begin productive work

**Remember:** This document is THE single source of truth for bootstrap.

---

*Unified Entry Point v2.0 - Ending the bootstrap wars, establishing peace.*
