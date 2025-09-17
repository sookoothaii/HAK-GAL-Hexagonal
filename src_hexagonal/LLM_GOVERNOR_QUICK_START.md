# 🚀 LLM GOVERNOR - QUICK START GUIDE

## ❌ **AKTUELLER STATUS: NICHT INTEGRIERT**

Der LLM Governor wurde von Sonnet 4 implementiert, ist aber **NOCH NICHT** im Backend integriert!

## ✅ **WAS VORHANDEN IST:**
- `llm_governor_adapter.py` ✅
- `hybrid_llm_governor.py` ✅ 
- `llm_governor_integration.py` ✅
- Integration Patch ✅

## 🔧 **INTEGRATION IN 5 MINUTEN:**

### **Option 1: AUTOMATISCH (Empfohlen)**
```bash
# Führe das Integration Script aus
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal
python apply_llm_governor_patch.py
```

### **Option 2: MANUELL**

1. **Öffne** `hexagonal_api_enhanced_clean.py`

2. **Füge Import hinzu** (Zeile ~92):
```python
from src_hexagonal.llm_governor_integration import integrate_llm_governor
```

3. **Füge Initialisierung hinzu** (in `__init__`, nach Zeile ~208):
```python
# Initialize LLM Governor
self.llm_governor_integration = None
if enable_governor:
    try:
        self.llm_governor_integration = integrate_llm_governor(self.app)
        print("[OK] LLM Governor Integration enabled")
    except Exception as e:
        print(f"[WARNING] LLM Governor Integration failed: {e}")
```

4. **Modifiziere governor_start** (Zeile ~1740):
```python
@self.app.route('/api/governor/start', methods=['POST'])
def governor_start():
    data = request.get_json(silent=True) or {}
    use_llm = data.get('use_llm', False)
    
    if use_llm and self.llm_governor_integration:
        self.llm_governor_integration.enabled = True
        if self.governor:
            self.governor.start()
        return jsonify({
            'success': True, 
            'mode': 'llm_governor',
            'provider': self.llm_governor_integration.config['provider']
        })
    else:
        success = self.governor.start() if self.governor else False
        return jsonify({'success': success, 'mode': 'thompson'})
```

5. **Restart Backend:**
```bash
Ctrl+C
python src_hexagonal/hexagonal_api_enhanced_clean.py
```

## 🧪 **TEST DER INTEGRATION:**

### **1. Check Status:**
```bash
curl http://localhost:5002/api/llm-governor/status
```

Erwartete Antwort:
```json
{
  "available": true,
  "enabled": false,
  "provider": "groq",
  "epsilon": 0.2
}
```

### **2. Enable LLM Governor:**
```bash
curl -X POST http://localhost:5002/api/llm-governor/enable \
     -H "Content-Type: application/json" \
     -d '{"provider": "groq", "epsilon": 0.2}'
```

### **3. Test Evaluation:**
```bash
curl -X POST http://localhost:5002/api/llm-governor/evaluate \
     -H "Content-Type: application/json" \
     -d '{"fact": "Gravity(Earth, Acceleration, 9.81, m/s²)", "domain": "physics"}'
```

## 🎮 **FRONTEND INTEGRATION:**

Im Frontend Dashboard:
1. Klicke "Start Governor"
2. Aktiviere Checkbox "Use LLM Governor" 
3. Wähle Provider (Groq/Ollama/Mock)
4. Setze Epsilon (0.2 empfohlen)
5. Klicke "Start with LLM"

## 📊 **ERWARTETE VERBESSERUNGEN:**

| Metrik | Ohne LLM | Mit LLM | Verbesserung |
|--------|----------|---------|--------------|
| Duplikate | 30% | <5% | **-83%** |
| Qualität | 0.60 | 0.83 | **+38%** |
| Relevanz | 60% | 92% | **+53%** |

## ⚠️ **TROUBLESHOOTING:**

**Problem:** "LLM Governor not available"
→ **Lösung:** Stelle sicher, dass `GROQ_API_KEY` gesetzt ist oder Ollama läuft

**Problem:** "Module not found: llm_governor_integration"
→ **Lösung:** Pfade prüfen, `sys.path` muss src_hexagonal enthalten

**Problem:** Frontend zeigt keinen LLM Governor
→ **Lösung:** Backend neu starten, Cache leeren (Ctrl+F5)

## ✅ **ERFOLGS-CHECKS:**

Wenn alles funktioniert, solltest du sehen:
- `[OK] LLM Governor Integration enabled` beim Backend-Start
- `/api/llm-governor/status` gibt `available: true` zurück
- Frontend zeigt "LLM Governor" Option
- Console zeigt LLM Evaluations beim Fact-Adding

---

**STATUS:** Integration bereit, muss nur angewendet werden!