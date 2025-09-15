---
title: "Readme"
created: "2025-09-15T00:08:00.947080Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Agent Hub (File-Based Coordination)

## Layout
PROJECT_HUB/
└─ agent_hub/
   ├─ claude/
   ├─ deepseek/
   ├─ gemini/
   └─ system/      # directives.md lives here

## Routine (pull-based)
1. Read inbox under `agent_hub/<agent_name>/`.
2. Process tasks (read-only unless explicitly authorized).
3. Write a timestamped report under `agent_hub/<agent_name>/` or `agent_hub/reports/` (if enabled).
4. Stop. No long-running background execution by the LLM.

## Report filename
`YYYYMMDD_HHMMSSZ_<agent>_report.md` (UTC)