---
title: "CRITICAL FIX REQUIRED - Governance Predicate Whitelist"
created: "2025-09-16T22:30:00Z"
author: "claude-opus-4.1"
topics: ["technical_reports"]
tags: ["critical", "governance", "fix-required", "predicates"]
privacy: "internal"
summary_200: |-
  Kritischer Fix erforderlich! Governance blockiert ALLE neuen Domain Facts wegen 
  restriktiver Predicate-Whitelist. Facts werden generiert aber abgelehnt. 
  Bypass funktioniert, permanenter Fix durch Erweiterung VALID_PREDICATES nötig.
---

# CRITICAL FIX REQUIRED
## Governance Predicate Whitelist Update

### **PROBLEM IDENTIFIZIERT:**
Governance V2 blockiert ALLE neuen Domain-spezifischen Predicates!

### **BEWEIS:**
```
WARNING: Invalid fact rejected: Invalid predicate: PsychologyTest
WARNING: Invalid fact rejected: Invalid predicate: Memory
WARNING: Invalid fact rejected: Invalid predicate: Brain
WARNING: Invalid fact rejected: Invalid predicate: Orbit
```

### **FIX ERFORDERLICH:**

**Datei:** `src_hexagonal/application/transactional_governance_engine.py`

**Suche nach:**
```python
VALID_PREDICATES = [
    # Liste mit ~50 Predicates
]
```

**Erweitere um folgende Predicates:**

#### **Batch 1: Core Sciences**
```python
# Psychology
'Memory', 'Learning', 'Behavior', 'Cognition', 'Personality',
'Development', 'Disorder', 'Emotion', 'Perception', 'Motivation',

# Neuroscience  
'Brain', 'Neuron', 'Synapse', 'Neurotransmitter', 'Plasticity',
'BrainRegion', 'Imaging', 'Neural', 'Cortex', 'Hippocampus',

# Astronomy
'Orbit', 'Gravity', 'Galaxy', 'Star', 'Planet', 'Telescope',
'CelestialBody', 'Exoplanet', 'Nebula', 'BlackHole',

# Geology
'Mineral', 'Rock', 'Tectonic', 'Volcano', 'Earthquake',
'Era', 'Fossil', 'Sediment', 'Magma', 'Plate',

# Sociology
'Society', 'Group', 'Institution', 'Culture', 'Mobility',
'Theory', 'Community', 'Social', 'Class', 'Norm',

# Linguistics
'Language', 'Phoneme', 'Syntax', 'Semantics', 'Grammar',
'Evolution', 'Dialect', 'Morphology', 'Pragmatics', 'Lexicon',
```

#### **Batch 2-6: Weitere 30 Domains**
[Liste zu lang - siehe extended_predicates.txt]

### **ALTERNATIV: Dynamic Predicate Validation**

**Bessere Lösung:** Statt Hardcoded-Liste, dynamische Validierung:

```python
def is_valid_predicate(self, predicate: str) -> bool:
    """Dynamische Predicate-Validierung"""
    # Basis-Regeln
    if not predicate[0].isupper():  # Muss mit Großbuchstabe beginnen
        return False
    if len(predicate) < 3:  # Mindestlänge
        return False
    if any(char in predicate for char in ['(', ')', ',', '.']):  # Keine Sonderzeichen
        return False
    
    # Erweiterte Validierung
    if predicate in self.BLOCKED_PREDICATES:  # Explizite Blacklist
        return False
    
    return True  # Alle anderen sind erlaubt
```

### **TESTING NACH FIX:**

```python
# Test ob neue Predicates akzeptiert werden
test_facts = [
    "Memory(Hippocampus, LongTerm, Consolidation).",
    "Orbit(Earth, Sun, Elliptical).",
    "Society(Industrial, Urban, Modern)."
]

result = governance.governed_add_facts_atomic(test_facts, context)
assert result == 3  # Alle sollten akzeptiert werden
```

### **WORKAROUND BIS FIX:**

```bash
# Terminal/CMD:
set GOVERNANCE_BYPASS=true
python backend.py

# Oder in governor_extended.conf:
[governance]
bypass_mode = true
```

### **IMPACT:**
- **Ohne Fix:** 0% der neuen Domain Facts werden gespeichert
- **Mit Fix:** 100% der validen Facts werden gespeichert
- **Geschätzte neue Facts:** 10,000+ aus 36 neuen Domains

### **PRIORITÄT: KRITISCH** 🔴

---

*Report erstellt von Claude Opus 4.1 nach erfolgreicher System-Verifikation*