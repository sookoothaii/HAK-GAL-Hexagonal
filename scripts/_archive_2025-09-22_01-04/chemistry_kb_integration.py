"""
Integration der Chemistry Facts in HAK_GAL System
==================================================
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from chemistry_facts_schema import ChemistryFactGenerator, ChemicalCompound, ReactionConditions

class ChemistryKnowledgeBase:
    """Erweiterte KB für chemische n-äre Facts"""
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.conn = sqlite3.connect(db_path)
        self.generator = ChemistryFactGenerator()
        self._init_schema()
    
    def _init_schema(self):
        """Initialisiere erweiterte Tabellen"""
        cursor = self.conn.cursor()
        
        # Prüfe ob facts Tabelle die neuen Spalten hat
        cursor.execute("PRAGMA table_info(facts)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'argument_count' not in columns:
            cursor.execute("ALTER TABLE facts ADD COLUMN argument_count INTEGER DEFAULT 2")
        if 'argument_types' not in columns:
            cursor.execute("ALTER TABLE facts ADD COLUMN argument_types TEXT")
        if 'domain' not in columns:
            cursor.execute("ALTER TABLE facts ADD COLUMN domain TEXT DEFAULT 'general'")
        
        # Erstelle fact_arguments Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fact_arguments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                value TEXT NOT NULL,
                type TEXT,
                metadata TEXT,
                FOREIGN KEY (fact_id) REFERENCES facts(id),
                UNIQUE(fact_id, position)
            )
        """)
        
        self.conn.commit()
    
    def add_chemistry_fact(self, fact_str: str, structured_args: List[Dict[str, Any]] = None) -> int:
        """
        Füge einen Chemistry Fact mit strukturierten Argumenten hinzu
        
        Args:
            fact_str: Der Fact als String, z.B. "ChemicalReaction(H2, O2, H2O)."
            structured_args: Liste von Argument-Dictionaries mit 'value', 'type', 'metadata'
        
        Returns:
            ID des eingefügten Facts
        """
        cursor = self.conn.cursor()
        
        # Parse Fact
        if not fact_str.endswith('.'):
            fact_str += '.'
        
        # Zähle Argumente
        arg_count = fact_str.count(',') + 1
        
        # Füge Fact ein
        cursor.execute("""
            INSERT INTO facts (statement, argument_count, domain, confidence)
            VALUES (?, ?, 'chemistry', 0.9)
        """, (fact_str, arg_count))
        
        fact_id = cursor.lastrowid
        
        # Füge strukturierte Argumente ein wenn vorhanden
        if structured_args:
            for i, arg in enumerate(structured_args, 1):
                cursor.execute("""
                    INSERT INTO fact_arguments (fact_id, position, value, type, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    fact_id,
                    i,
                    arg.get('value', ''),
                    arg.get('type', 'unknown'),
                    json.dumps(arg.get('metadata', {}))
                ))
        
        self.conn.commit()
        return fact_id
    
    def search_chemistry_facts(self, 
                              compound: Optional[str] = None,
                              reaction_type: Optional[str] = None,
                              min_args: int = 3) -> List[Dict[str, Any]]:
        """
        Suche nach Chemistry Facts
        
        Args:
            compound: Suche nach Compound (Name oder Formel)
            reaction_type: Typ der Reaktion
            min_args: Minimum Anzahl Argumente
        
        Returns:
            Liste von gefundenen Facts mit Metadaten
        """
        cursor = self.conn.cursor()
        
        query = """
            SELECT 
                f.id,
                f.statement,
                f.argument_count,
                f.confidence,
                GROUP_CONCAT(
                    json_object(
                        'position', fa.position,
                        'value', fa.value,
                        'type', fa.type,
                        'metadata', fa.metadata
                    )
                ) as args_json
            FROM facts f
            LEFT JOIN fact_arguments fa ON f.id = fa.fact_id
            WHERE f.domain = 'chemistry'
            AND f.argument_count >= ?
        """
        
        params = [min_args]
        
        if compound:
            query += " AND (f.statement LIKE ? OR fa.value LIKE ?)"
            params.extend([f'%{compound}%', f'%{compound}%'])
        
        if reaction_type:
            query += " AND f.statement LIKE ?"
            params.append(f'{reaction_type}%')
        
        query += " GROUP BY f.id ORDER BY f.argument_count DESC, f.confidence DESC"
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            fact = {
                'id': row[0],
                'statement': row[1],
                'argument_count': row[2],
                'confidence': row[3],
                'arguments': []
            }
            
            if row[4]:  # args_json
                # Parse concatenated JSON
                args_str = f'[{row[4]}]'
                try:
                    fact['arguments'] = json.loads(args_str)
                except:
                    pass
            
            results.append(fact)
        
        return results
    
    def add_reaction(self,
                    reactants: List[ChemicalCompound],
                    products: List[ChemicalCompound],
                    conditions: Optional[ReactionConditions] = None,
                    catalyst: Optional[str] = None) -> int:
        """
        Füge eine chemische Reaktion mit allen Details hinzu
        """
        # Generiere Fact String
        fact_str = self.generator.generate_reaction_fact(
            reactants, products, conditions, catalyst
        )
        
        # Erstelle strukturierte Argumente
        structured_args = []
        
        # Reactants
        for i, reactant in enumerate(reactants, 1):
            structured_args.append({
                'value': reactant.name,
                'type': 'reactant',
                'metadata': {
                    'formula': reactant.formula,
                    'smiles': reactant.smiles,
                    'position': i
                }
            })
        
        # Products
        for i, product in enumerate(products, 1):
            structured_args.append({
                'value': product.name,
                'type': 'product',
                'metadata': {
                    'formula': product.formula,
                    'smiles': product.smiles,
                    'position': i + len(reactants)
                }
            })
        
        # Conditions
        if conditions:
            structured_args.append({
                'value': conditions.to_fact_arg(),
                'type': 'conditions',
                'metadata': {
                    'temperature_k': conditions.temperature_k,
                    'pressure_pa': conditions.pressure_pa,
                    'solvent': conditions.solvent
                }
            })
        
        # Catalyst
        if catalyst:
            structured_args.append({
                'value': catalyst,
                'type': 'catalyst',
                'metadata': {}
            })
        
        return self.add_chemistry_fact(fact_str, structured_args)

# Beispiel-Nutzung
if __name__ == "__main__":
    kb = ChemistryKnowledgeBase("test_chemistry.db")
    
    # Füge Haber-Bosch Prozess hinzu
    n2 = ChemicalCompound("nitrogen", "N2", "N#N")
    h2 = ChemicalCompound("hydrogen", "H2", "[H][H]")
    nh3 = ChemicalCompound("ammonia", "NH3", "N")
    
    conditions = ReactionConditions(
        temperature_k=773,
        pressure_pa=20000000
    )
    
    fact_id = kb.add_reaction(
        reactants=[n2, h2],
        products=[nh3],
        conditions=conditions,
        catalyst="Fe"
    )
    
    print(f"Added Haber-Bosch reaction with ID: {fact_id}")
    
    # Suche nach Nitrogen-bezogenen Facts
    results = kb.search_chemistry_facts(compound="nitrogen", min_args=3)
    
    print("\nFound Chemistry Facts:")
    for fact in results:
        print(f"- [{fact['argument_count']} args] {fact['statement']}")
        if fact['arguments']:
            for arg in fact['arguments']:
                if isinstance(arg, dict):
                    print(f"  Position {arg.get('position')}: {arg.get('value')} ({arg.get('type')})")
