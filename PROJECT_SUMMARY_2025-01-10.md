# HAK_GAL Knowledge Base - Multi-Argument Facts Enhancement
## Project Snapshot: 2025-01-10

### Zusammenfassung
Transformation der HAK_GAL Wissensdatenbank von einfachen 2-Argument Facts zu einer wissenschaftlichen n-ären (3-10 Argumente) Knowledge Base mit Unsicherheitsquantifizierung und domänenspezifischen Strukturen.

---

## 1. AUSGANGSLAGE

### Problem-Identifikation
- Frontend zeigte nur simple 2-Argument Facts: `IsA(ArtificialIntelligence, Technology)`
- Obwohl Datenbank bereits 161 Multi-Argument Facts (97%) enthielt
- Fact-Extractor generierte irrelevante Facts (z.B. Chemie-Facts bei AI-Queries)
- Fehlende wissenschaftliche Präzision (keine Einheiten, Unsicherheiten)

### Technische Basis
- **Backend**: Flask API (`hexagonal_api_enhanced_clean.py`)
- **Datenbank**: SQLite (`hexagonal_kb.db`)
- **Frontend**: React mit TypeScript
- **Fact-Extractor**: `fact_extractor_universal.py`

---

## 2. IMPLEMENTIERTE LÖSUNGEN

### 2.1 Kontextbezogene Fact-Generierung

**Problem**: Irrelevante Facts (ChemicalReaction bei AI/Consciousness Query)

**Lösung**: Neue `fact_extractor_universal.py` mit:
- Domänen-Erkennung aus Text-Inhalt
- Kontextspezifische Fact-Templates
- Sauberes Query-Parsing ohne ganze Sätze als Entities

**Datei**: `src_hexagonal/adapters/fact_extractor_universal.py`

```python
def _detect_domain(self, text: str, query: str) -> str:
    # Erkennt: consciousness, ai, physics, chemistry, biology
    # Generiert nur passende Facts für erkannte Domäne
```

### 2.2 Wissenschaftliches Schema mit Quantities

**Innovation**: Q(...) Notation für Messwerte mit Unsicherheiten

**Format**: 
```
Q(value, unit, err_abs?, err_rel?, conf?)
```

**Beispiele**:
- `Q(2.3e-4, s^-1, err_rel:5, conf:95)` - Ratenkonstante mit 5% Fehler
- `Q(75.3, kJ/mol, err_abs:2.1)` - Aktivierungsenergie ±2.1 kJ/mol
- `Q(298, K)` - Temperatur ohne Unsicherheit

**Dateien**:
- `quantity_schema.py` - Quantity-Klasse mit Parser
- `chemistry_facts_schema.py` - Chemistry-spezifische Implementierung

### 2.3 Multi-Domain Architektur

**Struktur**: Allgemeine wissenschaftliche KB für alle Domänen

**Implementierte Domänen**:
- Physics (Motion, Energy, Wave, Quantum)
- Chemistry (Reaction, Structure, Equilibrium, Kinetics)
- Biology (Process, Pathway, Expression, Interaction)
- Neuroscience (Neural circuits, Synaptic plasticity)
- Mathematics (Theorem, Proof, Relation)
- Computer Science (Algorithm, Complexity)

**Datei**: `scientific_kb_architecture.py`

### 2.4 Erweiterte Datenbank-Struktur

**Neue Tabellen/Spalten**:
```sql
-- facts Tabelle erweitert
ALTER TABLE facts ADD COLUMN argument_count INTEGER DEFAULT 2;
ALTER TABLE facts ADD COLUMN domain TEXT DEFAULT 'general';

-- Strukturierte Argumente
CREATE TABLE fact_arguments (
    fact_id INTEGER,
    position INTEGER,
    value TEXT,
    type TEXT,
    metadata TEXT -- JSON für SMILES, units etc.
);
```

**Dateien**:
- `chemistry_schema.sql` - SQL Schema
- `chemistry_kb_integration.py` - Python Integration
- `setup_chemistry_kb.py` - Initialisierung

---

## 3. EINGEFÜGTE WISSENSCHAFTLICHE FACTS

### 3.1 Erste Batch (Basis n-äre Facts)
- 10 ChemicalReaction (7 Argumente)
- 5 BiologicalProcess (5 Argumente)
- 1 QuantumState (7 Argumente)

### 3.2 Q(...) Schema Batch (mit Unsicherheiten)

**OrganicReaction** (6 Facts):
```
OrganicReaction(methyl_iodide, CN-, methyl_cyanide, SN2, DMSO, T:Q(298, K), yield:Q(92, %, err_abs:2))
```
- Mechanismen: SN1, SN2, E1, E2, Diels-Alder, Grignard

**ReactionKinetics** (5 Facts):
```
ReactionKinetics(H2O2_decomposition, k:Q(2.3e-4, s^-1, err_rel:5), Ea:Q(75.3, kJ/mol, err_abs:2.1), A:Q(1.2e11, s^-1), T:Q(298, K))
```

**ElectronicTransition** (5 Facts):
```
ElectronicTransition(H, n2_to_n1, wavelength:Q(121.6, nm), energy:Q(10.2, eV), oscillator_strength:Q(0.416, dimensionless), Lyman_alpha)
```

**Gesamt**: 199 Facts in KB (Stand: 2025-01-10)

---

## 4. KRITISCHE ERKENNTNISSE

### 4.1 GPT-5 Plan Bewertung
**Vorschlag**: RDF-Quadstore, SHACL, PROV-O, komplette Neuarchitektur

**Unsere Bewertung**: Akademisch korrekt aber praktisch übertrieben

**Pragmatischer Ansatz**:
- SQLite erweitern statt ersetzen ✓
- JSON für Metadaten statt RDF ✓
- Iterative Entwicklung statt Komplettumbau ✓

### 4.2 Cache-Probleme
Python `.pyc` Cache-Dateien verhinderten Updates
→ Lösung: `__pycache__` löschen nach Änderungen

### 4.3 LLM-Unabhängigkeit
Problem lag nicht am lokalen 14B Modell (Qwen 2.5) sondern an der Nachverarbeitung
→ Beide LLMs (Qwen und Claude) generierten gute Antworten

---

## 5. AUFGABENTEILUNG (Claude vs GPT-5/Max)

### Claude (Technische Implementation)
- SQLite Datenbank-Management ✓
- Schema für n-äre Facts ✓
- Frontend-Integration (pending)
- Query-Optimierung ✓
- Strukturierung & Speicherung ✓

### GPT-5/Max (Wissenschaftliche Expertise)
- Generierung wissenschaftlich korrekter Facts
- Validierung gegen aktuelle Literatur
- Cross-Domain Verbindungen
- Fact-Expansion (2-arg → n-arg)

**Dokumentiert in**: `GPT5_TASKS.md`

---

## 6. OFFENE PUNKTE & NÄCHSTE SCHRITTE

### Sofort machbar
1. **Frontend-Anpassung** für n-äre Facts Darstellung
2. **Backend-Neustart** erforderlich nach Schema-Änderungen
3. **Weitere domänenspezifische Batches** einfügen

### Mittelfristig
1. **SMILES/InChI Integration** für eindeutige Molekül-IDs
2. **Validierung**: Stöchiometrie, Ladungsbilanz
3. **Visualisierung**: 2D Molekül-Rendering

### Langfristig
1. **RDKit Integration** für Chemie-Validierung
2. **Provenienz-Tracking** mit Literatur-Referenzen
3. **API für externe Tools**

---

## 7. DATEIEN-ÜBERSICHT

### Kern-Dateien (modifiziert)
- `src_hexagonal/adapters/fact_extractor_universal.py` - Kontextbezogene Fact-Generierung
- `hexagonal_api_enhanced_clean.py` - Backend API

### Neue Dateien (erstellt)
- `quantity_schema.py` - Q(...) Notation Implementation
- `chemistry_facts_schema.py` - Chemistry-spezifische Facts
- `scientific_kb_architecture.py` - Multi-Domain Architektur
- `chemistry_kb_integration.py` - DB Integration
- `setup_chemistry_kb.py` - DB Initialisierung
- `chemistry_schema.sql` - SQL Schema Erweiterung
- `GPT5_TASKS.md` - Aufgaben für GPT-5/Max
- `test_multi_arg_facts.py` - Test-Script

---

## 8. TESTING & VALIDIERUNG

### Test-Commands
```python
# Test Q(...) Schema
python quantity_schema.py

# Test Chemistry KB
python setup_chemistry_kb.py

# Test Multi-Arg Facts
python test_multi_arg_facts.py
```

### Validierungs-Kriterien
- ✓ Mindestens 3, maximal 10 Argumente
- ✓ Einheiten nach UCUM/QUDT Standard
- ✓ Unsicherheiten wo relevant
- ✓ Keine null-Werte (explizite Marker)
- ✓ Domänen-Relevanz

---

## 9. TECHNISCHE SPEZIFIKATIONEN

### Fact-Format
```
Predicate(arg1, arg2, ..., argN).
```

### Mit Quantities
```
ReactionKinetics(name, k:Q(value, unit, error), Ea:Q(...), A:Q(...), T:Q(...)).
```

### Stöchiometrie
```
reactants:[H2:3,N2:1], products:[NH3:2]
```

### Explizite Marker
```
catalyst:none, solvent:none, byproduct:none
```

---

## 10. ZUSAMMENFASSUNG FÜR NÄCHSTE INSTANZ

### Was funktioniert
- N-äre Facts (3-10 Args) ✓
- Q(...) Schema mit Unsicherheiten ✓
- Multi-Domain Support ✓
- Kontextbezogene Generierung ✓

### Was zu tun ist
1. **Backend neustarten** (wichtig!)
2. **Frontend anpassen** für n-äre Darstellung
3. **Weitere Facts einfügen** nach Templates
4. **Validierung implementieren** (Stöchiometrie etc.)

### Kritische Files
- Hauptlogik: `fact_extractor_universal.py`
- Schema: `quantity_schema.py`
- Integration: `chemistry_kb_integration.py`

### Performance
- KB: 199 Facts
- Durchschnitt: 5+ Argumente pro Fact
- Domänen: 6 aktiv

---

**Erstellt**: 2025-01-10
**Version**: 1.0
**Status**: Funktionsfähig, erweiterbar
**Nächster Checkpoint**: Nach Frontend-Integration
