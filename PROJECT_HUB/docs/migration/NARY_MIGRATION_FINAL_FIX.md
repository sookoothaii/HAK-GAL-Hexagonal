# HAK_GAL N-ÄRE FACTS MIGRATION - VOLLSTÄNDIGE DOKUMENTATION
**Session:** 2025-09-19  
**Status:** 90% funktionsfähig - 2 Tools defekt  
**Priorität:** HOCH - Kritische Wissenschafts-Features betroffen

---

## 📋 EXECUTIVE SUMMARY

Die HAK_GAL Knowledge Base wurde erfolgreich von simplen Tripel-Facts (Subject, Predicate, Object) auf wissenschaftliche n-äre Facts (1-∞ Argumente) mit Unsicherheits-Notation Q(value, unit, err_abs?, err_rel?, conf?) migriert. 90% der Tools funktionieren, aber `semantic_similarity` und `consistency_check` liefern keine Ergebnisse trotz erstellter Patches.

---

## 🎯 ZIEL: 100% FUNKTIONALITÄT

### Verbleibende Aufgaben:
1. **semantic_similarity** Tool reparieren (liefert `<none>` statt Ergebnisse)
2. **consistency_check** Tool reparieren (liefert `<none>` statt Ergebnisse)  
3. Patches korrekt in MCP Server integrieren
4. Alte Tripel-Spalten aus DB Schema entfernen (optional)

---

## 📊 AKTUELLER STATUS

### Database:
```
Pfad: D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db
Facts: 255
Multi-Argument (3+): 231 (90.6%)
Mit Q(...) Notation: 44 (17.3%)
Unique Predicates: 70
Top: ElectromagneticWave(48), ParticleInteraction(26), ChemicalReaction(12)
```

### MCP Server:
```
Server 1: hak-gal (Port 3006) - 67 Tools
  Config: ultimate_mcp/hakgal_mcp_patched.py
  Status: ✅ Läuft
  
Server 2: hak-gal-filesystem (Port 3006) - 52 Tools  
  Config: filesystem_mcp/hak_gal_filesystem.py
  Status: ✅ Läuft
```

### Tool Status:
| Kategorie | Funktioniert | Defekt |
|-----------|--------------|---------|
| Fact Tools | 7/9 (78%) | 2 |
| File Tools | 52/52 (100%) | 0 |
| System Tools | 8/8 (100%) | 0 |

---

## 🔴 PROBLEM-DETAILS

### 1. DEFEKTE TOOLS

#### semantic_similarity:
```python
# SYMPTOM:
>>> hak-gal:semantic_similarity(statement="ChemicalReaction(H2, O2, H2O)", limit=5)
<none>  # Sollte ähnliche Facts zurückgeben

# URSACHE:
- Patch wird geladen aber nicht korrekt in Tool-Handler injiziert
- Original-Implementation erwartet Tripel-Format
- Wrapper-Injection greift nicht
```

#### consistency_check:
```python
# SYMPTOM:
>>> hak-gal:consistency_check(limit=10)
<none>  # Sollte Inkonsistenzen finden

# URSACHE:
- Gleiche wie semantic_similarity
- Tools sind im Server registriert aber verwenden alte Implementierung
```

### 2. TECHNISCHE URSACHE

Der Wrapper `hakgal_mcp_patched.py` lädt die Patches:
```python
from mcp_nary_patches import (
    semantic_similarity_nary,
    consistency_check_nary,
    # ...
)
```

ABER: Die Tool-Handler im originalen Server Code überschreiben diese:
```python
# In hakgal_mcp_ultimate.py Zeile ~2900
if name == "semantic_similarity":
    # Verwendet ALTE Implementation, nicht gepatchte Version
    results = search_similar_facts(params['statement'])
```

---

## ✅ BEREITS ERLEDIGTE ARBEITEN

### 1. Erstellte Repair-Dateien:

#### `/scripts/fix_nary_tools.py` (Kern-Bibliothek)
```python
class NaryFactParser:
    """Parser für n-äre Facts mit Q(...) Support"""
    def extract_predicate(statement): ...
    def extract_arguments(statement): ...  # Berücksichtigt Q(...)
    def extract_entities(statement): ...

class FixedNaryTools:
    def semantic_similarity(statement, threshold, limit): ...
    def consistency_check(limit): ...
    def validate_facts(limit): ...
    def inference_chain(start_fact, max_depth): ...
```

#### `/scripts/mcp_nary_patches.py` (MCP Integration)
```python
async def semantic_similarity_nary(statement, limit, threshold):
    # Wrapper für MCP Tool
    results = fixed_tools.semantic_similarity(statement, threshold, limit)
    return format_for_mcp(results)
```

#### `/ultimate_mcp/hakgal_mcp_patched.py` (Wrapper)
```python
# Lädt Patches und startet Original-Server
# PROBLEM: Patches werden überschrieben
```

### 2. Funktionierende Features:
- ✅ N-ärer Parser extrahiert korrekt Argumente
- ✅ Q(...) Notation wird korrekt geparst
- ✅ Test-Suite beweist Funktionalität der reparierten Tools
- ✅ 90% der Tools arbeiten bereits mit n-ären Facts

---

## 🛠️ LÖSUNGSANSÄTZE

### OPTION 1: Direkte Server-Modifikation (Empfohlen)

**Datei:** `ultimate_mcp/hakgal_mcp_ultimate.py`

**Finde** (ca. Zeile 2900-3000):
```python
elif name == "semantic_similarity":
    # Original Implementation
    statement = params.get('statement')
    limit = params.get('limit', 50)
    threshold = params.get('threshold', 0.8)
    # ... alte Tripel-basierte Logik
```

**Ersetze mit:**
```python
elif name == "semantic_similarity":
    # N-äre kompatible Version
    import sys
    sys.path.append(r'D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts')
    from fix_nary_tools import FixedNaryTools
    
    tools = FixedNaryTools()
    results = tools.semantic_similarity(
        params.get('statement'),
        params.get('threshold', 0.8),
        params.get('limit', 50)
    )
    
    # Formatiere für MCP
    if results:
        output = f"Gefundene {len(results)} ähnliche Facts:\n"
        for score, fact in results:
            output += f"  Score {score:.3f}: {fact}\n"
        return output
    return "Keine ähnlichen Facts gefunden"
```

**Gleiche Änderung für consistency_check:**
```python
elif name == "consistency_check":
    # N-äre kompatible Version
    import sys
    sys.path.append(r'D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts')
    from fix_nary_tools import FixedNaryTools
    
    tools = FixedNaryTools()
    inconsistencies = tools.consistency_check(params.get('limit', 1000))
    
    if inconsistencies:
        output = f"Gefundene {len(inconsistencies)} Inkonsistenzen:\n"
        for fact1, fact2, reason in inconsistencies[:10]:
            output += f"\n{reason}:\n  1. {fact1}\n  2. {fact2}\n"
        return output
    return "Keine Inkonsistenzen gefunden"
```

### OPTION 2: Monkey-Patching (Alternative)

**Neue Datei:** `ultimate_mcp/hakgal_mcp_ultimate_fixed.py`
```python
# Lade Original
with open('hakgal_mcp_ultimate.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Ersetze Tool-Handler Section
code = code.replace(
    'elif name == "semantic_similarity":',
    '''elif name == "semantic_similarity":
        # INJECTED N-ARY PATCH
        from scripts.fix_nary_tools import FixedNaryTools
        tools = FixedNaryTools()
        # ... rest of patched code
    '''
)

# Execute modified code
exec(code)
```

### OPTION 3: Tool Registration Override

**In** `hakgal_mcp_ultimate.py` **nach Tool-Definitionen:**
```python
# Override Tool Implementations
def override_tools():
    global tools_registry  # oder wie auch immer Tools gespeichert sind
    
    from scripts.fix_nary_tools import FixedNaryTools
    fixed = FixedNaryTools()
    
    # Finde und ersetze
    for tool in tools_registry:
        if tool['name'] == 'semantic_similarity':
            tool['handler'] = lambda p: fixed.semantic_similarity(
                p.get('statement'), 
                p.get('threshold', 0.8),
                p.get('limit', 50)
            )
        elif tool['name'] == 'consistency_check':
            tool['handler'] = lambda p: fixed.consistency_check(
                p.get('limit', 1000)
            )

override_tools()
```

---

## 📝 TEST-PROZEDUR

### 1. Nach Implementation testen:
```python
# Test semantic_similarity
>>> hak-gal:semantic_similarity(
      statement="ChemicalReaction(test, A, B, C, D)",
      threshold=0.3,
      limit=5
    )
# SOLLTE AUSGEBEN:
# Gefundene 5 ähnliche Facts:
#   Score 0.4: ChemicalReaction(...)
#   Score 0.4: ChemicalReaction(...)
#   ...

# Test consistency_check  
>>> hak-gal:consistency_check(limit=100)
# SOLLTE AUSGEBEN:
# Gefundene X Inkonsistenzen:
#   Widersprüchliche Werte:
#     1. Fact A
#     2. Fact B
```

### 2. Verifiziere mit Test-Script:
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts
python -c "from fix_nary_tools import test_fixed_tools; test_fixed_tools()"
```

---

## 🎯 ERFOLGSKRITERIEN

1. ✅ `semantic_similarity` liefert Score-basierte Ergebnisse für n-äre Facts
2. ✅ `consistency_check` findet Widersprüche in n-ären Facts
3. ✅ Alle 119 Tools funktionieren ohne Fehler
4. ✅ Server-Start zeigt: "N-ary patches activated"
5. ✅ Keine `<none>` Responses mehr

---

## 📂 WICHTIGE DATEIEN

### Zu modifizieren:
```
D:\MCP Mods\HAK_GAL_HEXAGONAL\
├── ultimate_mcp\
│   ├── hakgal_mcp_ultimate.py     # Hauptserver - Tool-Handler ca. Zeile 2900
│   └── hakgal_mcp_patched.py      # Wrapper (funktioniert teilweise)
└── scripts\
    ├── fix_nary_tools.py           # ✅ Kern-Bibliothek (funktioniert)
    └── mcp_nary_patches.py         # ✅ MCP Integration (funktioniert)
```

### Backup vorhanden:
```
backups\nary_fix_20250919_073954\hakgal_mcp_ultimate.py
```

---

## ⚠️ KRITISCHE HINWEISE

1. **Python Cache löschen** vor jedem Test:
   ```powershell
   Get-ChildItem -Path "D:\MCP Mods\HAK_GAL_HEXAGONAL" -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force
   ```

2. **Server neu starten** nach jeder Änderung:
   ```powershell
   # Stoppe mit Ctrl+C, dann:
   npx @srbhptl39/mcp-superassistant-proxy@latest --config ./combined-mcp.sse.config.json --outputTransport sse
   ```

3. **Auth Token** für Tests: `515f57956e7bd15ddc3817573598f190`

4. **Encoding** beachten: Alle Files sind UTF-8

---

## 🏁 QUICK FIX (5 Minuten)

Wenn Zeit kritisch ist, hier der schnellste Weg:

1. Öffne `D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\hakgal_mcp_ultimate.py`
2. Suche: `elif name == "semantic_similarity":`
3. Ersetze den gesamten elif-Block mit dem Code aus "OPTION 1" oben
4. Wiederhole für `elif name == "consistency_check":`
5. Speichern, Cache löschen, Server neustarten
6. Testen mit den Commands aus "TEST-PROZEDUR"

---

## 📞 SUPPORT

Bei Fragen zur Implementation:
- Alle Reparatur-Tools sind getestet und funktionieren standalone
- Das Problem liegt NUR in der Integration in den MCP Server
- Die Tool-Handler müssen die gepatchten Versionen aufrufen

**Geschätzter Aufwand:** 15-30 Minuten für vollständige Reparatur

---

*Dokument erstellt: 2025-09-19 07:50 UTC*  
*Nächste Instanz kann direkt mit OPTION 1 beginnen*