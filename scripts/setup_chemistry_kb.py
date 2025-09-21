"""
Setup Script für Chemistry Knowledge Base
==========================================
Erstellt alle notwendigen Tabellen für n-äre Chemistry Facts
"""
import sqlite3
import sys
sys.path.append(r'D:\MCP Mods\HAK_GAL_HEXAGONAL')

from chemistry_facts_schema import ChemicalCompound, ReactionConditions, ChemistryFactGenerator

def create_chemistry_kb(db_path: str = "chemistry_kb.db"):
    """Erstelle komplette Chemistry KB von Grund auf"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Erstelle Chemistry Knowledge Base Schema...")
    
    # 1. Haupt-Facts Tabelle (kompatibel mit HAK_GAL)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT NOT NULL UNIQUE,
            confidence REAL DEFAULT 0.7,
            source TEXT DEFAULT 'generated',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            argument_count INTEGER DEFAULT 2,
            argument_types TEXT,
            domain TEXT DEFAULT 'general'
        )
    """)
    
    # 2. Strukturierte Argumente
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_arguments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            value TEXT NOT NULL,
            type TEXT,
            metadata TEXT,
            FOREIGN KEY (fact_id) REFERENCES facts(id) ON DELETE CASCADE,
            UNIQUE(fact_id, position)
        )
    """)
    
    # 3. Chemical Compounds Registry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            formula TEXT NOT NULL,
            smiles TEXT,
            inchi TEXT,
            inchi_key TEXT UNIQUE,
            cas_number TEXT,
            molecular_weight REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 4. Reactions Registry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            reaction_type TEXT,
            fact_id INTEGER,
            temperature_k REAL,
            pressure_pa REAL,
            solvent TEXT,
            catalyst TEXT,
            yield_percent REAL,
            FOREIGN KEY (fact_id) REFERENCES facts(id)
        )
    """)
    
    # 5. Indices für Performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_domain ON facts(domain)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_argcount ON facts(argument_count)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_compounds_formula ON compounds(formula)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_compounds_smiles ON compounds(smiles)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reactions_type ON reactions(reaction_type)")
    
    # 6. Views für einfachen Zugriff
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS chemistry_facts_view AS
        SELECT 
            f.id,
            f.statement,
            f.argument_count,
            f.confidence,
            f.domain,
            r.name as reaction_name,
            r.reaction_type,
            r.temperature_k,
            r.pressure_pa,
            r.catalyst
        FROM facts f
        LEFT JOIN reactions r ON r.fact_id = f.id
        WHERE f.domain = 'chemistry'
        ORDER BY f.argument_count DESC, f.confidence DESC
    """)
    
    conn.commit()
    print("✓ Schema erstellt")
    
    # Füge Beispiel-Facts hinzu
    print("\nFüge Beispiel-Chemistry-Facts hinzu...")
    
    generator = ChemistryFactGenerator()
    
    # 1. Wasser-Synthese (3 args)
    cursor.execute("""
        INSERT INTO facts (statement, argument_count, domain, confidence)
        VALUES (?, 3, 'chemistry', 0.95)
    """, ("ChemicalReaction(H2, O2, H2O).",))
    
    # 2. Haber-Bosch (7 args)
    cursor.execute("""
        INSERT INTO facts (statement, argument_count, domain, confidence)
        VALUES (?, 7, 'chemistry', 0.98)
    """, ("ChemicalEquilibrium(HaberBosch, N2, 3H2, 2NH3, empty, Keq:2.0, Conditions[T:773K,P:20MPa,Cat:Fe]).",))
    
    # 3. Photosynthese (7 args)
    cursor.execute("""
        INSERT INTO facts (statement, argument_count, domain, confidence)
        VALUES (?, 7, 'chemistry', 0.92)
    """, ("BiologicalProcess(Photosynthesis, 6CO2, 6H2O, C6H12O6, 6O2, chlorophyll, light).",))
    
    # 4. Säure-Base (4 args)
    cursor.execute("""
        INSERT INTO facts (statement, argument_count, domain, confidence)
        VALUES (?, 4, 'chemistry', 0.99)
    """, ("AcidBaseReaction(HCl, NaOH, NaCl, H2O).",))
    
    # 5. Molekül-Geometrie (6 args)
    cursor.execute("""
        INSERT INTO facts (statement, argument_count, domain, confidence)
        VALUES (?, 6, 'chemistry', 0.96)
    """, ("MolecularGeometry(CH4, C, 4H, tetrahedral, sp3, 109.5deg).",))
    
    # 6. Spektroskopie (5 args)
    cursor.execute("""
        INSERT INTO facts (statement, argument_count, domain, confidence)
        VALUES (?, 5, 'chemistry', 0.88)
    """, ("Spectroscopy(benzene, NMR, 7.36ppm, singlet, aromatic_H).",))
    
    conn.commit()
    
    # Zeige Statistik
    cursor.execute("""
        SELECT 
            COUNT(*) as total_facts,
            AVG(argument_count) as avg_args,
            MAX(argument_count) as max_args,
            MIN(argument_count) as min_args
        FROM facts
        WHERE domain = 'chemistry'
    """)
    
    stats = cursor.fetchone()
    print(f"\n✓ {stats[0]} Chemistry Facts hinzugefügt")
    print(f"  - Durchschnittliche Argumente: {stats[1]:.1f}")
    print(f"  - Maximum Argumente: {stats[2]}")
    print(f"  - Minimum Argumente: {stats[3]}")
    
    # Zeige Facts nach Argument-Anzahl
    cursor.execute("""
        SELECT argument_count, COUNT(*) as count
        FROM facts
        WHERE domain = 'chemistry'
        GROUP BY argument_count
        ORDER BY argument_count
    """)
    
    print("\nVerteilung nach Argument-Anzahl:")
    for row in cursor.fetchall():
        print(f"  {row[0]} Argumente: {row[1]} Facts")
    
    conn.close()
    return db_path

if __name__ == "__main__":
    db_path = create_chemistry_kb("chemistry_kb.db")
    print(f"\n✅ Chemistry Knowledge Base erstellt: {db_path}")
    
    # Test-Abfrage
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("Beispiel-Facts aus der Chemistry KB:")
    cursor.execute("""
        SELECT statement, argument_count 
        FROM facts 
        WHERE domain = 'chemistry'
        ORDER BY argument_count DESC
        LIMIT 5
    """)
    
    for fact, args in cursor.fetchall():
        print(f"[{args} args] {fact}")
    
    conn.close()
