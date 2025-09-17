---
title: "Technical Handover - Generator Performance and Frontend Status Systems"
topics: ["handovers", "technical", "maintenance"]
tags: ["generator", "frontend", "cuda", "monitoring", "troubleshooting"]
privacy: "internal"
status: "active"
author_agent: "Claude-3-Opus"
model: "claude-3-opus-20240229"
created_fs: "2025-09-17T21:20:00Z"
summary_200: "Technical handover documenting the current state and maintenance requirements of the HAK-GAL fact generation system and dashboard. System generates 800+ facts/min via parallel SimpleFactGenerator independent of Thesis/Aethelred engines. Critical files: simple_fact_generator.py (fact format), llm_governor_generator_parallel.py (parallel execution), ProDashboardEnhanced.tsx (status display). Known issues: Governor can exclude generators, frontend caching delays updates, no automatic recovery from failures. Monitoring: Check facts/min rate, verify predicate distribution, ensure HasProperty <30%. Emergency recovery: Run standalone generator via bypass_thesis.py if main system fails."
---

# Technical Handover - Generator Performance and Frontend Status Systems

## 1. System Overview

### 1.1 Current Operational State
- **Fact Generation Rate**: 800-1000 facts/minute
- **Knowledge Base Size**: 30,000+ facts (growing)
- **Predicate Balance**: HasProperty maintained at ~25%
- **Generator Architecture**: Parallel execution (independent of Thesis)
- **CUDA Status**: Correctly detected and displayed

### 1.2 Critical Components
```
Backend (Port 5002):
├── hexagonal_api_enhanced_clean.py     # Main API
├── simple_fact_generator.py            # Fact generator
├── llm_governor_generator_parallel.py  # Parallel wrapper
└── governor_adapter.py                 # Engine orchestration

Frontend (Port 8088):
├── ProDashboardEnhanced.tsx           # Main dashboard
├── useGovernorStore.ts                # State management
└── useGovernorSocket.ts               # WebSocket connection
```

## 2. Known Issues and Mitigations

### 2.1 Generator Stops Producing Facts

**Symptoms**:
- Dashboard shows facts static
- Learning rate shows 0/min
- Self-Learning badge gray/inactive

**Diagnosis**:
```python
# Check if generator is running
import requests
response = requests.get("http://127.0.0.1:5002/api/llm-governor/status")
data = response.json()
print(f"Generating: {data.get('generating')}")
print(f"Enabled: {data.get('enabled')}")
```

**Recovery**:
```bash
# Option 1: Restart via API
curl -X POST http://localhost:5002/api/governor/stop
curl -X POST http://localhost:5002/api/governor/start -H "Content-Type: application/json" -d '{"use_llm": true}'

# Option 2: Force standalone generator
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
python bypass_thesis.py
```

### 2.2 Frontend Shows Incorrect Status

**Common Issues**:
1. CUDA shows inactive despite GPU usage
2. Learning rate stuck at 0
3. Old data cached

**Solution**:
```javascript
// Force refresh in browser console
localStorage.clear();
location.reload(true);
```

Or rebuild frontend:
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend
npm run build
```

## 3. Monitoring Checklist

### 3.1 Health Indicators
| Indicator | Healthy Range | Alert Threshold | Check Command |
|-----------|---------------|-----------------|---------------|
| Facts/min | 500-1000 | <100 | `curl http://localhost:5002/api/facts/count` |
| HasProperty % | 20-30% | >40% | Check recent facts distribution |
| Predicate Types | 12-15 | <8 | Analyze last 100 facts |
| API Success | >95% | <90% | Monitor 400/409 responses |
| GPU Utilization | 5-20% | >80% | Task Manager / nvidia-smi |

### 3.2 Quick Health Check Script
```python
import requests
import time

def health_check():
    # Get initial count
    r1 = requests.get("http://127.0.0.1:5002/api/facts/count")
    count1 = r1.json()['count']
    
    time.sleep(60)
    
    # Get count after 1 minute
    r2 = requests.get("http://127.0.0.1:5002/api/facts/count")
    count2 = r2.json()['count']
    
    rate = count2 - count1
    
    if rate < 100:
        print(f"⚠️ WARNING: Low generation rate: {rate}/min")
    else:
        print(f"✅ Healthy: {rate} facts/min")
        
    return rate
```

## 4. Critical File Locations

### 4.1 Generator System
```
D:\MCP Mods\HAK_GAL_HEXAGONAL\
├── src_hexagonal\
│   ├── infrastructure\
│   │   └── engines\
│   │       ├── simple_fact_generator.py          # Core generator
│   │       ├── thesis_engine.py                  # Can interfere
│   │       └── aethelred_engine.py              # Can interfere
│   ├── llm_governor_generator.py                # Original (may fail)
│   └── llm_governor_generator_parallel.py       # Fixed version
```

### 4.2 Frontend Dashboard
```
D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend\
├── src\
│   └── pages\
│       └── ProDashboardEnhanced.tsx            # Main dashboard
```

## 5. Common Fixes

### 5.1 Generator Not Running
```python
# Direct activation
from simple_fact_generator import SimpleFactGenerator
gen = SimpleFactGenerator()
gen.run(duration_minutes=60)
```

### 5.2 Wrong Fact Format
Ensure all facts use functional notation:
```python
# CORRECT:
fact = f"Predicate(Arg1, Arg2)."

# WRONG:
fact = f"Arg1 Predicate Arg2."
```

### 5.3 CUDA Not Detected
Backend must return in `/api/status`:
```json
{
  "cuda": {"available": true},
  "monitoring": {"gpu_available": true}
}
```

Frontend reads via:
```typescript
const isCudaActive = backendStatus.cuda?.available || 
                     backendStatus.monitoring?.gpu_available;
```

## 6. Emergency Recovery Procedures

### 6.1 Complete System Restart
```bash
# 1. Stop everything
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# 2. Clear Python cache
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

# 3. Start backend
python hexagonal_api_enhanced_clean.py

# 4. Start frontend
cd ..\frontend
npm run dev

# 5. Force generator start
curl -X POST http://localhost:5002/api/governor/start -d "{\"use_llm\": true}"
```

### 6.2 Database Recovery
If KB corrupted:
```python
import sqlite3
conn = sqlite3.connect("hexagonal_kb.db")
conn.execute("PRAGMA integrity_check")
conn.execute("VACUUM")
conn.close()
```

## 7. Performance Optimization Tips

1. **Batch Size**: Generator uses 20 facts/batch (optimal)
2. **Delay**: 20ms between facts prevents API overload
3. **Duplicate Check**: In-memory cache for recent 1000 facts
4. **Predicate Weights**: Adjust in `simple_fact_generator.py` if needed

## 8. Testing Procedures

### 8.1 Verify Fact Generation
```python
def test_generation():
    from simple_fact_generator import SimpleFactGenerator
    gen = SimpleFactGenerator()
    
    # Test format
    fact, meta = gen.generate_fact()
    assert '(' in fact and ')' in fact
    assert fact.endswith('.')
    
    # Test API acceptance
    success = gen.add_fact(fact)
    assert success == True
    
    print("✅ All tests passed")
```

### 8.2 Verify Dashboard Updates
1. Open http://localhost:8088/
2. Note current fact count
3. Wait 30 seconds
4. Fact count should increase by 400-500

## 9. Contact Points

- **System Architecture**: See `project_hub/docs/design_docs/ARCHITECTURE_OVERVIEW.md`
- **API Documentation**: See `configs/OPENAPI_HEXAGONAL_20250814.yaml`
- **Previous Fixes**: See `project_hub/analysis/` directory
- **Governor Logic**: See `project_hub/docs/technical_reports/LLM_GOVERNOR_ARCHITECTURE_DESIGN.md`

## 10. Final Notes

The system is currently stable but requires monitoring. The parallel generator architecture is a workaround, not a permanent solution. Future refactoring should properly integrate all engines into a unified scheduler.

**Critical Success Factors**:
1. Generator must run continuously
2. Fact format must be `Predicate(Arg1, Arg2).`
3. Frontend must poll `/api/status` for updates
4. HasProperty should stay below 30%

---
*Handover prepared by Claude-3-Opus on 2025-09-17*
*System operational at time of handover*
*KB growing at 800+ facts/minute*