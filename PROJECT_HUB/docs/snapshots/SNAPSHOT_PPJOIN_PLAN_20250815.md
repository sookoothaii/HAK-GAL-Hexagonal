---
title: "Snapshot Ppjoin Plan 20250815"
created: "2025-09-15T00:08:01.075169Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# SNAPSHOT – PPJoin(+) Plan und Mojo‑Ausbau (2025‑08‑15)

Dieser Snapshot dokumentiert die Erweiterungen zur maximalen Mojo‑Nutzung im read‑only Backend (5002):

## Änderungen
- ENV ergänzt: `MOJO_PPJOIN_ENABLED` (geplanter read‑only Pfad 5002)
- Geplanter Endpoint: `GET /api/analysis/dupes-ppjoin?sample_limit=2000&threshold=0.9&top_k=100`
- Handover aktualisiert: Abschnitt 4.1 (Endpunkte) mit Geplant‑Block; Appendix 16.5 präzisiert (PPJoin+/LSH/HNSW, Golden‑Suite, Bench‑Methodik)

## Aktueller 5002‑Stand (Kurz)
- Mojo native: `validate_facts_batch`, `find_duplicates` (Golden = 0 Mismatches)
- Bench (1000/0.95): Validate ~0–2.3 ms; Duplicates ~117–191 ms
- Read‑only enforced; Writes auf 5001 mit Gating

## Nächste Schritte
- PPJoin(+): Inverted‑Index + Prefix/Längen/Positions‑Filter nativ (SIMD/Threading)
- Golden‑Suite um Unicode‑Normalisierung/Homoglyphen/defekte UTF‑8 erweitert
- Bench: P50/P95, Input‑Mix, Filter‑Statistiken reporten

## Referenzen (Kern)
- PPJoin/PPJoin+: Xiao, Wang, Lin. SIGMOD’08
- MinHash/LSH: Broder (1997/1998); Indyk & Motwani (1998)
- HNSW: Malkov & Yashunin (2018)
