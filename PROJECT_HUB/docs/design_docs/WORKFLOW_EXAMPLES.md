---
title: "Workflow Examples"
created: "2025-09-15T00:08:00.994662Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK-GAL Workflow-Sammlung - Praktische Beispiele

## 1. 🔍 Knowledge Base Analyse & Wartung
**Ziel:** Automatische KB-Qualitätsprüfung und Bereinigung

```
[Schedule Trigger: 0 2 * * *] 
    ↓
[Get Facts Count]
    ↓
[Branch: Count > 5000?]
    ├─ YES → [Consistency Check]
    │         ↓
    │     [Analyze Duplicates]
    │         ↓
    │     [Semantic Similarity: threshold=0.95]
    │         ↓
    │     [Delegate Task: Gemini - "Analysiere gefundene Duplikate"]
    │         ↓
    │     [If: Duplikate gefunden?]
    │         ├─ YES → [Bulk Delete: Duplikate]
    │         └─ NO → [No Op]
    │         ↓
    └─ NO → [Comment: "KB noch klein genug"]
    ↓
[DB Vacuum]
    ↓
[DB Checkpoint: TRUNCATE]
    ↓
[Metrics Collector: kb_maintenance_duration]
    ↓
[Add Fact: MaintenanceRun({{timestamp}}, success).]
```

## 2. 🚀 Code Execution Pipeline mit Fehlerbehandlung
**Ziel:** Sicheres Ausführen von User-Code mit Monitoring

```
[HTTP Request: Webhook empfangen]
    ↓
[Extract: code, language aus Payload]
    ↓
[Validate Data: Schema-Check]
    ↓
[Try/Catch Block]
    ├─ TRY:
    │   [Execute Code: {{code}}, {{language}}, timeout=30]
    │       ↓
    │   [Branch: return_code == 0?]
    │       ├─ SUCCESS → [Set Variable: result = stdout]
    │       └─ FAIL → [Set Variable: result = stderr]
    │
    └─ CATCH:
        [Log Error]
        ↓
        [Set Variable: result = "Execution failed"]
    ↓
[Merge Branches]
    ↓
[String Template: "Ergebnis: {{result}}"]
    ↓
[Webhook Send: Ergebnis zurück]
    ↓
[Metrics Collector: code_execution_time]
```

## 3. 🤖 Multi-Agent Research Pipeline
**Ziel:** Komplexe Recherche mit mehreren AI-Agents

```
[Input: Research Topic]
    ↓
[Set Variable: topic = {{input}}]
    ↓
[Parallel Execution:]
    ├─ [Search Knowledge: {{topic}}]
    ├─ [Delegate: Gemini - "Recherchiere: {{topic}}"]
    ├─ [Delegate: DeepSeek - "Technische Details zu {{topic}}"]
    └─ [Execute Code: python web_scraper.py "{{topic}}"]
    ↓
[Wait For All: 60000ms]
    ↓
[Merge Branches: strategy="all"]
    ↓
[Consensus Evaluator: method="semantic_similarity"]
    ↓
[Branch: Konsens > 0.7?]
    ├─ YES → [Create Report]
    │         ↓
    │     [Add Fact: ResearchComplete({{topic}}, {{timestamp}}).]
    │         ↓
    │     [Project Snapshot: "Research_{{topic}}_{{date}}"]
    │
    └─ NO → [Delegation Optimizer]
            ↓
        [Retry with different agents]
```

## 4. 📊 Performance Monitoring & Alerting
**Ziel:** System-Health überwachen und bei Problemen alarmieren

```
[Timer Trigger: interval=300000] // alle 5 Minuten
    ↓
[Workflow Status: current]
    ↓
[Health Check JSON]
    ↓
[Parse JSON]
    ↓
[For Each: metrics]
    ├─ [Evaluate Expression: value > threshold]
    │   ↓
    │   [If: Alert needed?]
    │       ├─ YES → [Rate Limiter: 1 pro Stunde]
    │       │         ↓
    │       │     [String Template: "ALERT: {{metric}} = {{value}}"]
    │       │         ↓
    │       │     [HTTP Request: Slack Webhook]
    │       │         ↓
    │       │     [Sentry Search Issues: query="{{metric}}"]
    │       │
    │       └─ NO → [Metrics Collector: {{metric}}_normal]
    │
    └─ [Continue Loop]
    ↓
[DB Benchmark: rows=1000]
    ↓
[Add Fact: HealthCheck({{timestamp}}, {{performance}}).]
```

## 5. 🔄 Backup & Disaster Recovery
**Ziel:** Automatische Backups mit Integritätsprüfung

```
[Cron Validator: "0 3 * * *"]
    ↓
[Schedule Trigger: Täglich 3 Uhr]
    ↓
[DB Get PRAGMA]
    ↓
[Branch: WAL-Mode aktiv?]
    ├─ NO → [DB Enable WAL]
    └─ YES → [No Op]
    ↓
[KB Stats]
    ↓
[Set Variable: kb_size = {{size}}]
    ↓
[DB Backup Now]
    ↓
[Get File Info: backup_path]
    ↓
[Evaluate Expression: backup_size >= kb_size * 0.9]
    ↓
[If: Backup valid?]
    ├─ YES → [DB Backup Rotate: keep_last=7]
    │         ↓
    │     [Project Snapshot: "Daily_Backup_{{date}}"]
    │         ↓
    │     [Comment: "Backup erfolgreich"]
    │
    └─ NO → [Error Transform]
            ↓
        [Circuit Breaker: Alert Admin]
            ↓
        [Fallback Chain: Alternative Backup]
```

## 6. 🎯 Intelligente Task-Delegation
**Ziel:** Aufgaben optimal an verfügbare Agents verteilen

```
[Input: Complex Task]
    ↓
[Split In Batches: size=5]
    ↓
[For Each: sub_task]
    ├─ [Analyze Task Complexity]
    │   ↓
    │   [Delegation Optimizer: available_tools=[Gemini, Claude, DeepSeek]]
    │   ↓
    │   [Switch/Case: best_agent]
    │       ├─ Gemini → [Delegate: Gemini]
    │       ├─ Claude → [Delegate: Claude CLI]  
    │       └─ DeepSeek → [Delegate: DeepSeek]
    │   ↓
    │   [Timeout Handler: 30000ms]
    │   ↓
    │   [Reliability Checker: tool={{agent}}]
    │   ↓
    │   [If: Reliability < 0.8]
    │       └─ YES → [Bias Detector]
    │                 ↓
    │             [Retry with Backoff]
    │
    └─ [Continue Loop]
    ↓
[Merge Data: mode="append"]
    ↓
[Filter Items: success == true]
    ↓
[Sort Items: by="quality_score"]
    ↓
[Save Report]
```

## 7. 🔧 Entwicklungs-Workflow
**Ziel:** Code-Änderungen testen und deployen

```
[Git Webhook: Push Event]
    ↓
[Read File: changed_files.json]
    ↓
[For Each: file]
    ├─ [Grep: pattern="TODO|FIXME|HACK"]
    │   ↓
    │   [If: Found?]
    │       └─ YES → [Comment: "Technical Debt gefunden"]
    │   ↓
    │   [Socket DepScore: extract dependencies]
    │   ↓
    │   [Branch: Score < 7?]
    │       └─ YES → [Break: "Unsichere Dependencies"]
    │
    └─ [Continue]
    ↓
[Execute Code: pytest tests/]
    ↓
[Assert Condition: all tests passed]
    ↓
[Multi-Edit: Version bump]
    ↓
[Create File: CHANGELOG.md update]
    ↓
[HTTP Request: Deploy to staging]
```

## 📈 Diese Workflows zeigen:

1. **Komplexe Logik:** Branches, Loops, Error Handling
2. **Multi-Agent Orchestrierung:** Parallele AI-Aufrufe
3. **Datenverarbeitung:** JSON parsing, String manipulation
4. **Systemintegration:** HTTP, Webhooks, File operations
5. **Monitoring:** Metrics, Health checks, Alerts
6. **Automation:** Schedules, Triggers, Backups
7. **Intelligente Features:** Konsens-Evaluation, Bias-Detection

Das HAK-GAL System kann bereits:
- ✅ Komplexe Workflows mit 50+ Nodes
- ✅ Parallele Ausführung
- ✅ Fehlerbehandlung & Recovery
- ✅ Multi-Agent Koordination
- ✅ Zeitgesteuerte Automation
- ✅ Datenbank-Wartung
- ✅ Performance-Monitoring
