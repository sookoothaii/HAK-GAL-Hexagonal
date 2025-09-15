---
title: "Directives"
created: "2025-09-15T00:08:00.947080Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# System Directives (Minimal)

- version: 0.1
- last_updated_utc: 2025-09-15T00:00:00Z
- scope: internal

## Active Directives

### DIR-001: Bootstrap Hardening
- owner: claude
- goal: Remove secrets from docs; fix API notation; stabilize examples.
- steps:
  1) Rotate/revoke any leaked tokens externally.
  2) Apply PATCH to `PROJECT_HUB/HAK_GAL_UNIVERSAL_BOOTSTRAP.md`.
  3) Run verification checklist (grep 0-hits).
- acceptance:
  - No plaintext secrets in repo.
  - No `hak-gal:` or `list_directory` left.
  - Header contains no static KPIs.

### DIR-002: Frontmatter Migration
- owner: gemini
- baseline: 17/372 MD files with frontmatter
- target: 372/372 (100%)
- deliverable: A reusable frontmatter template + a manifest of migrated files (read-only planning; writes only with approval).

## Conventions
- Coordination is file-based (no background tasks by the LLM).
- Use placeholders for secrets, e.g., `${HAKGAL_AUTH_TOKEN}`.