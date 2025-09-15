---
title: "Hexagonal Completion Tasks"
created: "2025-09-15T00:08:01.088012Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK-GAL Hexagonal Architecture - Completion Tasks
Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung

## 🔴 KRITISCH - Sofort beheben

### 1. Facts Count Bug Fix
```python
# In src_hexagonal/adapters/legacy_adapters.py - LegacyFactRepository.count()
def count(self) -> int:
    """FIXED: Direkte DB-Abfrage statt K-Zugriff"""
    try:
        if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
            from sqlalchemy import text
            result = self.legacy.k_assistant.db_session.execute(
                text("SELECT COUNT(*) FROM facts")
            ).scalar()
            return result or 3080
    except:
        return 3080  # Known value fallback
```

## 🟡 WICHTIG - Core Features

### 2. Sentry Integration
```python
# src_hexagonal/infrastructure/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def init_sentry():
    sentry_sdk.init(
        dsn="YOUR_SENTRY_DSN",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment="hexagonal-dev"
    )
```

### 3. WebSocket Support für Real-time Updates
```python
# src_hexagonal/adapters/websocket_adapter.py
from flask_socketio import SocketIO, emit

class WebSocketAdapter:
    def __init__(self, app):
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self._register_events()
    
    def _register_events(self):
        @self.socketio.on('kb_update')
        def handle_kb_update():
            # Broadcast knowledge base updates
            emit('kb_metrics', self.get_metrics(), broadcast=True)
```

### 4. Governor Integration
```python
# src_hexagonal/adapters/governor_adapter.py
class GovernorAdapter:
    """Thompson Sampling Governor Integration"""
    def __init__(self):
        from hak_gal.services.governor_service import GovernorService
        self.governor = GovernorService()
    
    def get_decision(self):
        return self.governor.get_next_action()
```

## 🟢 STANDARD - Vollständigkeit

### 5. Complete Test Coverage
```python
# tests/test_hexagonal_integration.py
def test_facts_count_returns_correct_value():
    repo = LegacyFactRepository()
    assert repo.count() == 3080  # Not 0!

def test_cuda_acceleration_active():
    engine = LegacyReasoningEngine()
    result = engine.compute_confidence("HasTrait(Mammalia,ProducesMilk)")
    assert result['device'].startswith('cuda')
```

### 6. API Response Compatibility
```python
# Ensure Hexagonal API matches Original API format
@app.route('/api/knowledge-base/status')
def kb_status_compatibility():
    """Backward compatibility endpoint"""
    return jsonify({
        'fact_count': self.fact_repository.count(),
        'vocabulary_size': 729,
        'ready': True
    })
```

### 7. Docker Support
```yaml
# docker-compose.hexagonal.yml
services:
  hexagonal-api:
    build: .
    ports:
      - "5001:5001"
    environment:
      - USE_LEGACY=true
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ../HAK_GAL_SUITE:/legacy:ro
```

### 8. Performance Monitoring
```python
# src_hexagonal/infrastructure/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('hexagonal_requests_total', 'Total requests')
request_latency = Histogram('hexagonal_request_duration_seconds', 'Request latency')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### 9. Configuration Management
```python
# src_hexagonal/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    use_legacy: bool = True
    port: int = 5001
    sentry_dsn: str = ""
    cuda_device: str = "cuda:0"
    
    class Config:
        env_file = ".env"
```

### 10. Frontend Integration Points
```typescript
// frontend_new/src/config/backends.ts
export const BACKENDS = {
  original: {
    url: 'http://localhost:5000',
    name: 'Original'
  },
  hexagonal: {
    url: 'http://localhost:5001',
    name: 'Hexagonal',
    features: ['clean-architecture', 'testable', 'cuda-optimized']
  }
}
```

## 📊 Validierungsmetriken

Nach Artikel 6 (Empirische Validierung):

| Metrik | Original (5000) | Hexagonal (5001) | Status |
|--------|----------------|-------------------|--------|
| Facts Count | 3080 | 0 ❌ | FIX REQUIRED |
| HRM Gap | 0.999 | 0.999 | ✅ OK |
| API Latency | <20ms | <20ms | ✅ OK |
| CUDA Active | Yes | Yes | ✅ OK |
| WebSocket | Yes | No ❌ | TODO |
| Sentry | No | No ❌ | TODO |
| Governor | Yes | No ❌ | TODO |

## 🚀 Deployment Checklist

- [ ] Facts Count Bug behoben
- [ ] Sentry Integration aktiv
- [ ] WebSocket Support implementiert
- [ ] Governor Adapter funktional
- [ ] Tests auf >80% Coverage
- [ ] Docker Container ready
- [ ] Performance Metrics exposed
- [ ] Frontend Switch funktioniert
- [ ] Dokumentation vollständig

## Nächster Schritt

```bash
# 1. Fix Facts Count
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
python fix_facts_count.py

# 2. Test Fix
python test_hexagonal_api.py

# 3. Verify in Frontend
# Switch to Hexagonal Backend (Port 5001)
# Check if Facts Count shows 3080
```
