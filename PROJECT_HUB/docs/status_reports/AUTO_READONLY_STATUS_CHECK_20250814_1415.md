---
title: "Auto Readonly Status Check 20250814 1415"
created: "2025-09-15T00:08:01.082284Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Auto Read-Only Status Check (2025-08-14 14:15)

Empirische, sichere Checks:

- Health: operational, hexagonal, repo=SQLite, mojo.flag=false
- Status (light): operational
- Facts count: 3865 (cached)
- Top predicates: HasPart 768, HasPurpose 714, Causes 601, HasProperty 580, IsDefinedAs 389, IsSimilarTo 203, IsTypeOf 203, HasLocation 106, ConsistsOf 88, WasDevelopedBy 66
- Quality metrics: invalid 5, duplicates 0, isolated 1808, contradictions 0

Hinweise:
- Alle Aufrufe GET; keine Schreibpfade berührt.
- Mojo projektseitig vorbereitet; Aktivierung per Flag+Neustart möglich, ohne API-Änderung.
