# HAK-GAL Hexagonal Architecture  Technical Handover (Complete)

This handover summarizes the autonomous Hex backend under `src_hexagonal/` with zero dependency on the legacy monolith.

## Runtime Highlights
- Port: 5001
- Autonomous LLM: DeepSeek/Mistral via `.env` (no 5000 required)
- Real-time WS: Socket.IO (if enabled)
- Emergency Graph Tools: available via REST
- CORS: permissive for local dev

## Key Endpoints
- GET `/health`  lightweight health
- GET `/api/status?light=1`  status snapshot
- POST `/api/reason`  HRM reasoning (CUDA)
- POST `/api/search`  KB search
- GET `/api/facts`  list facts (count + total)
- POST `/api/facts`  add fact (201 on success, 409 exists, 422 invalid)
- POST `/api/llm/get-explanation`  Deep explanation via direct LLM providers (fallback to local synthesis)
- POST `/api/command`  compatibility: `explain`, `add_fact`
- POST `/api/logicalize`  extract canonical facts from text
- Graph emergency: `/api/graph/*`

## Environment
- Loads `D:\MCP Mods\HAK_GAL_SUITE\.env` at startup (does not override pre-set env vars)
- Recognized keys:
  - `DEEPSEEK_API_KEY` (DeepSeek chat)
  - `MISTRAL_API_KEY` (Mistral chat)
  - Optional Sentry: `SENTRY_DSN`, `SENTRY_ENV`, `SENTRY_TRACES_SAMPLE_RATE`

## Code Map (essentials)
- `src_hexagonal/hexagonal_api_enhanced.py`  Flask app + WS + LLM proxy + CORS + graph endpoints
- `src_hexagonal/application/services.py`  use cases (facts, reasoning)
- `src_hexagonal/core/domain/entities.py`  `Fact`, `Query`, `ReasoningResult`
- `src_hexagonal/core/ports/interfaces.py`  ports: `FactRepository`, `ReasoningEngine`, `LLMProvider`
- `src_hexagonal/adapters/legacy_adapters.py`  safe legacy bridge (DB-backed count/exists)
- `src_hexagonal/adapters/sqlite_adapter.py`  optional SQLite repo
- `src_hexagonal/adapters/websocket_adapter.py`  Socket.IO factory
- `src_hexagonal/adapters/llm_providers.py`  DeepSeek/Mistral providers + `MultiLLMProvider`
- `src_hexagonal/adapters/fact_extractor.py`  LLM fact extraction + heuristic suggestions

## LLM Flow
1) `/api/llm/get-explanation` builds a prompt with query + context facts
2) Uses `MultiLLMProvider` (DeepSeekMistral) if API keys present
3) Extracts `suggested_facts` from provider output via `fact_extractor`
4) Falls back to local reasoning + KB evidence if no providers available

## Fact Add Semantics
- Input: `{ statement | query | fact }`, auto-append '.'
- Validation: `Predicate(Entity1, Entity2).`
- Responses:
  - 201: added
  - 409: already exists
  - 422: invalid format

## Start Commands
```powershell
# in hex root
. .\.venv_hexa\Scripts\Activate.ps1
python src_hexagonal\hexagonal_api_enhanced.py
```

## Verification
- Explanation: `POST /api/llm/get-explanation` with `{ topic, context_facts }`
- Add fact: `POST /api/facts` with `{ statement }`
- Count: `GET /api/facts/count`

## Notes
- Fully functional without port 5000
- Frontend should hit 5001 for all calls (Deep Explanation included)
- WebSocket events include `kb_update`, `system_status`, `governor_update`

---
This hex backend is ready for standalone operation with direct LLM access and human-in-the-loop fact confirmation.
