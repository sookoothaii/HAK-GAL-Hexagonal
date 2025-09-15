---
title: "Slack Integration Guide Gpt5 20250814"
created: "2025-09-15T00:08:01.022300Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

### Slack-Integration für HAK-GAL (Cursor + MCP)

Autor: GPT-5 • Datum: 2025-08-14

---

### Zweck
Minimal-Setup, um KB-Status via Slack zu posten und später Slash-Commands nachzurüsten. Keine Abhängigkeit von Port 5000, nur Hexagonal (5001) und MCP.

---

### 1) Einmaliges Setup
- Slack: Incoming Webhook im Ziel-Channel erstellen → URL kopieren
- ENV im Aufruf setzen (kein Repo-Commit von Secrets): `SLACK_WEBHOOK_URL`

---

### 2) Ein-Klick-Run (PowerShell)
```powershell
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\slack
./run_post_kb_status.ps1 -WebhookUrl "https://hooks.slack.com/services/XXX/YYY/ZZZ"
```

---

### 3) Was wird gesendet?
- Health (write_enabled, Zeilen, Größe)
- KB-Stats (Count, Größe, mtime)
- Top-Predicates (Top 10)
- Growth (7 Tage)

---

### 4) Sicherheit
- Keine Slack-Secrets im Repo ablegen
- Write-Gate bleibt geschlossen; Posts verwenden nur Read-Tools

---

### 5) Erweiterungen (optional)
- Slash-Commands: `/hakgal kb_stats`, `/hakgal snapshot`
- Auto-Schedule (Windows Task Scheduler) für tägliche Reports
- Review/Approval-Workflow: Slack → KB (MCP-Write testweise, Write-Gate temporär öffnen)


