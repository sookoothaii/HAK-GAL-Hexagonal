---
title: "New Instance Guide"
created: "2025-09-15T00:08:01.014297Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Neue Instanz – Bootstrap und Selbstcheck (SSoT + Nischen-LLM)

Ziel: Jede neue Arbeitsinstanz kennt SSoT, Nischen-Kontexte und MCP-Delegation. ASCII‑sicher, ohne Risiko.

## 1) Voraussetzungen
- Python venv: `.venv_hexa` vorhanden (Windows)
- `.env` in `ultimate_mcp/` mit echten Keys:
  - `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`
- SSoT und Nischen-Dateien:
  - `ssot.md`
  - `gemini_context.md`, `claude_context.md`, `deepseek_context.md`

## 2) Selbstcheck ausführen
PowerShell (ASCII/UTF‑8 erzwungen):
```
Set-Location -LiteralPath 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
$py = '.\.venv_hexa\Scripts\python.exe'
$env:PYTHONUTF8 = '1'
& $py '.\self_check.py'
```
Ergebnis:
- `reports\self_check_report.json`
- Klartextausgabe mit Status pro Abschnitt

## 3) Orchestrator prüfen
```
& $py '.\multi_agent_orchestrator.py' --status
& $py '.\multi_agent_orchestrator.py' --test
& $py '.\multi_agent_orchestrator.py' --consensus "Kurze Architektur-Zusammenfassung von HAK_GAL"
```

## 4) Täglicher Konsensjob (optional)
Einmallauf:
```
& '.\run_consensus_job.bat'
```
Outputs: `reports\orchestrator_status.txt`, `consensus_*.json`, `consensus_summary.json`

## 5) Prinzipien (SSoT + Nische)
- Kontext-Schichten: SSoT (global) + Agent‑Nische (spezifisch)
- Delegation: via MCP `delegate_task` mit Präfixen (`Claude:sonnet`, `DeepSeek:chat`, `Gemini:2.5-flash`)
- Sicherheit: ASCII‑only Ausgaben, keine Systemänderungen ohne expliziten Auftrag




