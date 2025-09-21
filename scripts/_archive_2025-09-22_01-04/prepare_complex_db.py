#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prepare HAK-GAL Database for Complex Facts
===========================================
Erweitert die DB für:
- Variable Argumentanzahl (2-10 Argumente)
- Mathematische Formeln
- Verschachtelte Strukturen
- Metadaten für Fakten
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")

def extend_database():
    """Erweitere die Datenbank für komplexe Fakten"""
    
    print("🔧 Extending HAK-GAL Database for Complex Facts...")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Erstelle erweiterte Facts-Tabelle (falls nicht existiert)
    print("\n📊 Creating extended facts table...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facts_extended (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        statement TEXT UNIQUE NOT NULL,
        predicate TEXT,
        arg_count INTEGER,
        arg1 TEXT,
        arg2 TEXT,
        arg3 TEXT,
        arg4 TEXT,
        arg5 TEXT,
        args_json TEXT,  -- Für mehr als 5 Argumente
        fact_type TEXT,   -- 'standard', 'formula', 'equation', 'system', etc.
        domain TEXT,      -- 'mathematics', 'physics', 'chemistry', etc.
        complexity INTEGER DEFAULT 1,
        confidence REAL DEFAULT 1.0,
        created_at TEXT DEFAULT (datetime('now')),
        source TEXT
    )
    """)
    
    # 2. Index für Performance
    print("📈 Creating indices...")
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_facts_ext_predicate 
    ON facts_extended(predicate)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_facts_ext_type 
    ON facts_extended(fact_type)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_facts_ext_domain 
    ON facts_extended(domain)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_facts_ext_complexity 
    ON facts_extended(complexity)
    """)
    
    # 3. Formeln-Tabelle für mathematische Ausdrücke
    print("📐 Creating formulas table...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS formulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        expression TEXT NOT NULL,
        latex TEXT,
        variables TEXT,
        domain TEXT,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)
    
    # 4. Fact-Relations für n-stellige Beziehungen
    print("🔗 Creating relations table...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        relation_type TEXT NOT NULL,
        entities TEXT NOT NULL,  -- JSON Array
        strength REAL DEFAULT 1.0,
        context TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)
    
    # 5. Topic-Discovery Tracking
    print("🎯 Creating topic discovery table...")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discovered_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_name TEXT UNIQUE NOT NULL,
        topic_type TEXT,  -- 'cluster', 'gap', 'cross_domain'
        entities_count INTEGER,
        facts_count INTEGER,
        discovered_at TEXT DEFAULT (datetime('now')),
        explored BOOLEAN DEFAULT 0
    )
    """)
    
    # 6. Migrate existing facts to extended format
    print("\n📦 Migrating existing facts...")
    
    # Check if migration needed
    cursor.execute("SELECT COUNT(*) FROM facts")
    total_facts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM facts_extended")
    extended_facts = cursor.fetchone()[0]
    
    if extended_facts < total_facts:
        print(f"  Migrating {total_facts - extended_facts} facts...")
        
        cursor.execute("""
        INSERT OR IGNORE INTO facts_extended (statement, predicate, arg_count, arg1, arg2, fact_type)
        SELECT 
            statement,
            CASE 
                WHEN INSTR(statement, '(') > 0 
                THEN SUBSTR(statement, 1, INSTR(statement, '(') - 1)
                ELSE 'Unknown'
            END as predicate,
            2 as arg_count,  -- Standard facts have 2 arguments
            CASE 
                WHEN INSTR(statement, '(') > 0 AND INSTR(statement, ',') > 0
                THEN TRIM(SUBSTR(statement, 
                    INSTR(statement, '(') + 1,
                    INSTR(statement, ',') - INSTR(statement, '(') - 1
                ))
                ELSE NULL
            END as arg1,
            CASE 
                WHEN INSTR(statement, ',') > 0 AND INSTR(statement, ')') > 0
                THEN TRIM(SUBSTR(statement,
                    INSTR(statement, ',') + 1,
                    INSTR(statement, ')') - INSTR(statement, ',') - 1
                ))
                ELSE NULL
            END as arg2,
            'standard' as fact_type
        FROM facts
        WHERE statement NOT IN (SELECT statement FROM facts_extended)
        """)
        
        conn.commit()
        print(f"  ✅ Migration complete!")
    else:
        print(f"  ✅ Already migrated ({extended_facts} facts)")
    
    # 7. Add sample complex facts
    print("\n🌟 Adding sample complex facts...")
    
    sample_facts = [
        # Formeln
        ("Formula(EinsteinFieldEquation, Rμν-½gμνR+Λgμν=8πGTμν, Rμν_gμν_R_Λ_G_Tμν, GeneralRelativity).", 
         "Formula", 4, "formula", "physics"),
        
        ("Formula(SchrodingerEquation, iℏ∂ψ/∂t=Hψ, ψ_H_t_ℏ, QuantumMechanics).", 
         "Formula", 4, "formula", "physics"),
        
        ("Formula(BlackScholes, ∂V/∂t+½σ²S²∂²V/∂S²+rS∂V/∂S-rV=0, V_S_t_σ_r, Finance).", 
         "Formula", 5, "formula", "economics"),
        
        # Systeme
        ("System(NeuralNetwork, InputLayer, HiddenLayers, OutputLayer, Backpropagation, LossFuction).",
         "System", 5, "system", "computer_science"),
        
        ("Process(ProteinFolding, AminoAcidChain, Folding, SecondaryStructure, TertiaryStructure, FunctionalProtein).",
         "Process", 5, "process", "biology"),
        
        # Komplexe Relationen
        ("Mediates(Enzyme, Substrate, Product).",
         "Mediates", 3, "relation", "biology"),
        
        ("Transform(Energy, Matter, E=mc², Equivalence).",
         "Transform", 4, "relation", "physics"),
    ]
    
    for statement, predicate, arg_count, fact_type, domain in sample_facts:
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO facts_extended 
            (statement, predicate, arg_count, fact_type, domain, complexity)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (statement, predicate, arg_count, fact_type, domain, arg_count - 1))
            print(f"  + {statement[:60]}...")
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
    
    # 8. Statistics
    print("\n📊 Database Statistics:")
    
    cursor.execute("SELECT COUNT(*) FROM facts")
    print(f"  Original facts table: {cursor.fetchone()[0]} facts")
    
    cursor.execute("SELECT COUNT(*) FROM facts_extended")
    print(f"  Extended facts table: {cursor.fetchone()[0]} facts")
    
    cursor.execute("SELECT COUNT(DISTINCT predicate) FROM facts_extended")
    print(f"  Unique predicates: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT fact_type, COUNT(*) FROM facts_extended GROUP BY fact_type")
    for fact_type, count in cursor.fetchall():
        print(f"  {fact_type}: {count} facts")
    
    cursor.execute("SELECT MAX(arg_count) FROM facts_extended")
    max_args = cursor.fetchone()[0]
    print(f"  Max arguments: {max_args}")
    
    # 9. Create Views for easy access
    print("\n🔍 Creating convenience views...")
    
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS complex_facts AS
    SELECT * FROM facts_extended 
    WHERE arg_count > 2 OR fact_type != 'standard'
    """)
    
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS formulas_view AS
    SELECT * FROM facts_extended 
    WHERE fact_type IN ('formula', 'equation')
    """)
    
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS systems_view AS
    SELECT * FROM facts_extended 
    WHERE fact_type IN ('system', 'process')
    """)
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database extension complete!")
    print("=" * 60)
    print("The database is now ready for:")
    print("  • Complex facts with variable arguments")
    print("  • Mathematical formulas and equations")
    print("  • System and process descriptions")
    print("  • Cross-domain knowledge")
    print("=" * 60)

def test_complex_queries():
    """Teste komplexe Abfragen"""
    print("\n🧪 Testing complex queries...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test 1: Finde alle Formeln
    cursor.execute("""
    SELECT statement FROM facts_extended 
    WHERE fact_type = 'formula'
    LIMIT 5
    """)
    formulas = cursor.fetchall()
    if formulas:
        print("\n📐 Found formulas:")
        for (formula,) in formulas:
            print(f"  • {formula}")
    
    # Test 2: Finde komplexe Fakten
    cursor.execute("""
    SELECT statement, arg_count FROM facts_extended 
    WHERE arg_count > 2
    ORDER BY arg_count DESC
    LIMIT 5
    """)
    complex_facts = cursor.fetchall()
    if complex_facts:
        print("\n🔗 Complex facts (>2 arguments):")
        for statement, count in complex_facts:
            print(f"  • [{count} args] {statement[:70]}...")
    
    conn.close()

def main():
    """Main entry point"""
    extend_database()
    test_complex_queries()
    
    print("\n💡 Next steps:")
    print("1. Run the advanced growth engine:")
    print("   python advanced_growth_engine.py")
    print("\n2. Analyze knowledge clusters:")
    print("   python advanced_growth_engine.py --analyze-only")
    print("\n3. Monitor with:")
    print("   python trusted_monitor.py")

if __name__ == "__main__":
    main()
