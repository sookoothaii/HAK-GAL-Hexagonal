---
title: "Final Handover"
created: "2025-09-15T00:08:01.103665Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

﻿# HAK-GAL Hexagonal Suite - Final Handover (Autonomous, Scientific, Safe)

This document summarizes the current working state of the Hex Suite (Port 5001): autonomy from the legacy backend, constitution (v2.2) integration, kill switch, direct LLM integration, frontend alignment, MCP read-only MVP, and reproducible test commands.

## 1) System Overview
- Architecture: Hexagonal (ports & adapters), REST + Socket.IO
- Runtime: Port 5001 (autonomous); no dependency on 5000
- LLM: Direct providers (DeepSeek/Mistral) via .env auto-loaded from D:\MCP Mods\HAK_GAL_SUITE\.env
- Deep Explanation: POST /api/llm/get-explanation (uses context_facts)
- Knowledge Base:
  - GET /api/facts (list), POST /api/facts (add, 201/409/422)
  - GET /api/facts/count (TTL cache)
- Safety & Control:
  - Constitution v2.2 (PolicyGuard) in observe mode by default
  - Kill switch (modes: normal|safe) with persistent JSON state

## 2) New/Changed Core Modules
- src_hexagonal/application/policy_guard.py
  - Loads hak_gal_constitution_v2_2.json, computes policy hash
  - check(action, context, externally_legal, sensitivity) -> decision {allowed, gate, metrics, policy_version, policy_hash, decision_id}
  - Mode via POLICY_ENFORCE=observe|strict (default: observe)
- src_hexagonal/application/risk_estimator.py
  - Lightweight estimators: harm_prob, sustain_index
- src_hexagonal/application/universalizability.py
  - Conservative universalizability check
- src_hexagonal/application/kill_switch.py
  - Persistent kill-switch state (kill_switch_state.json), mode normal|safe

## 3) API Changes
- POST /api/facts (write)
  - Policy check (observe: attach metadata only; strict: 403 on deny)
  - Response includes policy footnote and headers:
    - X-Policy-Version: <policy_version>
    - X-Decision-Id: <id>
  - Codes: 201 (added), 409 (exists), 422 (format)
- Kill switch endpoints
  - GET /api/safety/kill-switch -> { mode, state }
  - POST /api/safety/kill-switch/activate -> SAFE
  - POST /api/safety/kill-switch/deactivate -> normal
  - Optional token: KILL_SWITCH_TOKEN -> X-Admin-Token or ?token=
- Graph/emergency write paths: prepared to harden similarly (observe only for now)

## 4) Constitution v2.2 (operational)
- Allowed(a) = ExternallyLegal(a) AND (DefaultEthic(a) OR Override(a))
  - DefaultEthic: Universalizable AND harm_prob <= 0.001 AND sustain_index >= 0.85
  - Override: OperatorOverride AND PeerReviewed AND OverrideDocProvided AND RiskExceptionJustified
  - External illegality cannot be overridden
- observe mode: no blocking; strict mode: 403 for write on deny; read remains free

## 5) LLM Providers (autonomous)
- .env auto-load (does not override existing env): DEEPSEEK_API_KEY, MISTRAL_API_KEY
- Explain uses context_facts for higher quality

## 6) Frontend Alignment
- Uses 5001 end-to-end (reasoning/search/explain)
- Sends context_facts for explain
- Suggested facts: up to 20; 201/409/422 handled
- WebSocket fallback + backoff; KB count via WS/poll
- SAFE badge in header (ProHeader) when kill-switch is active

## 7) MCP MVP (read-only)
- Goal: REST equivalence (query/reason/status/explain) for Claude Desktop
- Plan: STDIO transport, auth/rate/budget in observe, A/B tests REST vs MCP

## 8) Reproducible Test Commands (PowerShell)
# Health / Count / Explain with context
Invoke-RestMethod 'http://127.0.0.1:5001/health'
Invoke-RestMethod 'http://127.0.0.1:5001/api/facts/count'
$payload = @{ topic='IsA(Socrates, Philosopher).'; context_facts=@('IsA(Socrates, GreekPhilosopher).','SubClass(GreekPhilosopher, Philosopher).') } | ConvertTo-Json
Invoke-RestMethod 'http://127.0.0.1:5001/api/llm/get-explanation' -Method Post -ContentType 'application/json' -Body $payload

# Write + Policy headers/footnote
$body = @{ statement='IsA(AlphaEntity, BetaClass).'; context=@{ source='human_verified' } } | ConvertTo-Json
curl.exe -i -X POST "http://127.0.0.1:5001/api/facts" -H "Content-Type: application/json" -d "$body"

# Kill-switch SAFE on/off
Invoke-RestMethod 'http://127.0.0.1:5001/api/safety/kill-switch'
Invoke-RestMethod 'http://127.0.0.1:5001/api/safety/kill-switch/activate' -Method Post -ContentType 'application/json' -Body (@{reason='manual'} | ConvertTo-Json)
$w = @{ statement='IsA(Gamma, Delta).'; context=@{ source='human_verified' } } | ConvertTo-Json
Invoke-WebRequest 'http://127.0.0.1:5001/api/facts' -Method Post -ContentType 'application/json' -Body $w
Invoke-RestMethod 'http://127.0.0.1:5001/api/safety/kill-switch/deactivate' -Method Post

# Strict mode test (optional)
$env:POLICY_ENFORCE='strict'  # restart API; write may 403, read stays free

## 9) Environment Variables
- LLM: DEEPSEEK_API_KEY, MISTRAL_API_KEY
- Policy: POLICY_ENFORCE=observe|strict (default: observe)
- Kill-switch auth (optional): KILL_SWITCH_TOKEN=<secret>

## 10) Risks / Limits / Recommendations
- Policy heuristics are lightweight to keep <=150 ms (SMT/MCMC optional later)
- Harden more write endpoints (graph/engines) in observe first
- Optional append-only audit logger; update OpenAPI (policy/kill-switch fields)

## 11) Rollback
- Kill switch: /api/safety/kill-switch/deactivate or delete kill_switch_state.json
- Policy strict -> observe: POLICY_ENFORCE='observe' (restart API)
- Code: use VCS to revert specific files

Status: verified, stable, minimal-invasive. The Hex Suite is autonomous, scientifically transparent (policy/explain/context), and safe via kill-switch/constitution. Research telemetry can run in observe; strict enforcement is controlled.
