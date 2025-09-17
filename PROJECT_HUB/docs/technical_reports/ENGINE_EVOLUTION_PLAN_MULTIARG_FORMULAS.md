---
title: "Engine Evolution Plan - Multi-Argument & Formula Support"
created: "2025-09-15T20:55:00Z"
author: "claude-opus-4.1"
topics: ["technical_reports"]
tags: ["engines", "evolution", "multi-argument", "formulas", "plan"]
privacy: "internal"
summary_200: |-
  Comprehensive plan to evolve aethelred and thesis engines from simple triple facts
  to support the full capabilities of the extended SQLite schema including multi-argument
  predicates (up to 5+), mathematical formulas, complex relations, and domain-specific
  fact types. The database already supports these features through facts_extended,
  formulas, and fact_arguments tables, but engines only generate simple triples.
---

# ENGINE EVOLUTION PLAN: Multi-Argument & Formula Support

## 📊 CURRENT STATE ANALYSIS

### Database Capabilities (ALREADY IMPLEMENTED)
```sql
✅ facts_extended: 5+ arguments with JSON overflow
✅ formulas: Mathematical expressions with variables
✅ fact_arguments: Flexible role-based arguments
✅ fact_dependencies: Complex relation tracking
✅ facts_v2: JSON-based flexible structures
```

### Engine Limitations (CURRENT)
```python
❌ Aethelred: Only generates Predicate(Subject, Object)
❌ Thesis: Only analyzes 2-argument predicates
❌ No formula generation
❌ No multi-argument support
❌ No domain awareness
```

## 🎯 EVOLUTION OBJECTIVES

### Phase 1: Multi-Argument Support
- Support 3-5 argument predicates
- Implement role-based arguments
- Enable complex fact patterns

### Phase 2: Formula Integration
- Mathematical expression generation
- Physics/Chemistry equations
- Logical formulas

### Phase 3: Domain Awareness
- Domain-specific fact generation
- Contextual complexity scoring
- Cross-domain reasoning

## 📋 DETAILED IMPLEMENTATION PLAN

### PHASE 1: MULTI-ARGUMENT EVOLUTION (Week 1-2)

#### 1.1 Database Integration Layer
```python
class ExtendedFactManager:
    def add_multi_arg_fact(self, predicate, args, roles=None, domain=None):
        """
        Example:
        add_multi_arg_fact(
            "Reaction",
            ["H2", "O2", "H2O", "2:1:2", "combustion"],
            ["reactant1", "reactant2", "product", "ratio", "type"],
            "chemistry"
        )
        """
        # Use facts_extended table
        # Store in args_json if >5 arguments
```

#### 1.2 Aethelred Engine Upgrades
```python
EXTENDED_PATTERNS = [
    # 3-argument patterns
    "Located(Entity, Location, Time)",
    "Transfers(Agent, Object, Recipient)",
    "Causes(Event1, Event2, Probability)",
    
    # 4-argument patterns  
    "Reaction(Reactant1, Reactant2, Product, Conditions)",
    "Transaction(Sender, Receiver, Amount, Timestamp)",
    
    # 5-argument patterns
    "Experiment(Subject, Method, Variable, Result, Confidence)",
    "Route(Origin, Destination, Via, Distance, Duration)"
]
```

#### 1.3 Thesis Engine Analysis Upgrades
```python
def analyze_multi_arg_fact(self, fact_row):
    """Analyze facts_extended entries"""
    arg_count = fact_row['arg_count']
    if arg_count > 2:
        # Extract complex patterns
        # Find n-ary relations
        # Detect role patterns
```

### PHASE 2: FORMULA SUPPORT (Week 3-4)

#### 2.1 Formula Generation Module
```python
class FormulaGenerator:
    DOMAINS = {
        'physics': [
            "F = m * a",
            "E = m * c^2",
            "v = d / t"
        ],
        'chemistry': [
            "pH = -log[H+]",
            "PV = nRT"
        ],
        'mathematics': [
            "a^2 + b^2 = c^2",
            "∑(i=1,n) i = n(n+1)/2"
        ]
    }
    
    def generate_formula_fact(self, domain, complexity):
        # Generate formula
        # Parse variables
        # Store in formulas table
        # Link to facts_v2
```

#### 2.2 LLM Integration for Formula Extraction
```python
FORMULA_PROMPT = """
Given the topic '{topic}', generate mathematical formulas:
1. Standard notation formula
2. List all variables with descriptions
3. Domain classification
4. Example calculation

Format as:
FORMULA: <expression>
VARIABLES: <var1:desc1>, <var2:desc2>
DOMAIN: <domain>
EXAMPLE: <calculation>
"""
```

### PHASE 3: ADVANCED FEATURES (Week 5-6)

#### 3.1 Complex Fact Types
```python
FACT_TYPES = {
    'standard': "Simple predicate logic",
    'formula': "Mathematical equation",
    'rule': "If-then logical rule",
    'constraint': "System constraint",
    'procedure': "Step-by-step process",
    'measurement': "Quantitative observation",
    'hypothesis': "Testable prediction"
}
```

#### 3.2 Domain-Specific Generators

**Chemistry Engine Extension:**
```python
def generate_chemistry_facts(self):
    return [
        "Reaction(2H2, O2, 2H2O, 'combustion', 'exothermic')",
        "BoilingPoint(H2O, 100, 'Celsius', '1atm')",
        "Molecule(C6H12O6, 'glucose', 180.156, 'g/mol')"
    ]
```

**Physics Engine Extension:**
```python
def generate_physics_facts(self):
    return [
        "Force(object1, 10, 'N', 'downward', 'gravity')",
        "Energy(system, 500, 'J', 'kinetic', 't=0')",
        "Wave(light, 650, 'nm', 'red', 'visible')"
    ]
```

### PHASE 4: INTEGRATION & OPTIMIZATION (Week 7-8)

#### 4.1 Unified Fact Interface
```python
class UnifiedFactEngine:
    def generate_fact(self, complexity_level):
        if complexity_level == 1:
            return self.simple_triple()
        elif complexity_level == 2:
            return self.multi_argument()
        elif complexity_level == 3:
            return self.formula()
        elif complexity_level == 4:
            return self.complex_relation()
```

#### 4.2 Performance Optimization
- Batch inserts for multi-argument facts
- Prepared statements for formulas
- Index optimization for complex queries
- Cache frequently used patterns

## 🔧 TECHNICAL REQUIREMENTS

### Database Schema Usage
```sql
-- Multi-argument facts
INSERT INTO facts_extended (
    statement, predicate, arg_count,
    arg1, arg2, arg3, arg4, arg5, args_json,
    fact_type, domain, complexity
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

-- Formulas
INSERT INTO formulas (
    name, expression, domain, variables, constants, fact_id
) VALUES (?, ?, ?, ?, ?, ?)

-- Flexible arguments
INSERT INTO fact_arguments (
    fact_id, position, role, value, value_type
) VALUES (?, ?, ?, ?, ?)
```

### API Endpoints to Add
```python
POST /api/facts/multi      # Multi-argument facts
POST /api/facts/formula    # Mathematical formulas
POST /api/facts/complex    # Complex relations
GET  /api/facts/by-domain  # Domain-specific queries
```

## 📊 SUCCESS METRICS

### Quantitative Goals
- Support 3-5 argument facts: **100%**
- Formula generation rate: **10+ per minute**
- Domain coverage: **5+ domains**
- Complex fact ratio: **30% of new facts**

### Quality Metrics
- Semantic correctness: **>90%**
- Formula validity: **>95%**
- Argument role accuracy: **>85%**
- Cross-domain linking: **>20%**

## 🚀 IMPLEMENTATION TIMELINE

### Week 1-2: Multi-Argument Foundation
- [ ] ExtendedFactManager class
- [ ] Aethelred multi-arg patterns
- [ ] Thesis multi-arg analysis
- [ ] Database integration tests

### Week 3-4: Formula Support
- [ ] FormulaGenerator module
- [ ] Domain-specific formulas
- [ ] LLM formula extraction
- [ ] Formula validation

### Week 5-6: Advanced Features
- [ ] Complex fact types
- [ ] Domain generators
- [ ] Cross-domain reasoning
- [ ] Procedural facts

### Week 7-8: Integration & Testing
- [ ] Unified interface
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Documentation

## 🔬 TESTING STRATEGY

### Unit Tests
```python
def test_multi_argument_fact():
    fact = "Located(Berlin, Germany, Europe, '52.5200N,13.4050E')"
    result = manager.add_multi_arg_fact(fact)
    assert result.arg_count == 4
    assert result.domain == "geography"
```

### Integration Tests
```python
def test_formula_generation():
    formula = generator.create_physics_formula()
    assert "=" in formula.expression
    assert len(formula.variables) > 0
    assert formula.domain in VALID_DOMAINS
```

### Performance Tests
- Multi-argument insert speed: **<10ms**
- Formula parsing time: **<50ms**
- Complex query response: **<100ms**

## 💡 KEY INNOVATIONS

### 1. Progressive Complexity
Start with simple, gradually increase complexity based on success rate

### 2. Domain Bridges
Facts that connect multiple domains for richer knowledge

### 3. Formula-Fact Linking
Mathematical formulas linked to conceptual facts

### 4. Role-Based Arguments
Named argument roles for better semantic understanding

## ⚠️ RISK MITIGATION

### Data Quality
- Validation layers for each complexity level
- Rollback mechanism for bad batches
- Confidence scoring for complex facts

### Performance
- Gradual rollout of features
- Database optimization before launch
- Monitoring and alerting

### Backward Compatibility
- Maintain simple fact support
- Versioning for fact types
- Migration tools for existing data

## 📝 NEXT STEPS

1. **Review & Approve Plan**
2. **Create Feature Branches**
3. **Implement Phase 1 MVP**
4. **Test with Small Dataset**
5. **Iterate Based on Results**

## 🎯 EXPECTED OUTCOMES

After implementation:
- **10x richer fact representation**
- **Domain-specific intelligence**
- **Mathematical reasoning capability**
- **Complex relationship modeling**
- **Scientific knowledge representation**

---

*This plan transforms HAK_GAL from a simple triple store to a sophisticated multi-dimensional knowledge system capable of representing complex scientific, mathematical, and procedural knowledge.*