#!/usr/bin/env python3
"""
EKR (Extended Knowledge Representation) - Practical Implementation
==================================================================
Demonstrates how to work with complex facts in HAK-GAL
"""

import json
import re
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class FactType(Enum):
    BINARY = "binary"      # Current: Predicate(E1, E2)
    NARY = "nary"         # New: Predicate(E1, E2, E3, ...)
    TYPED = "typed"       # New: Predicate(role1:E1, role2:E2)
    FORMULA = "formula"   # New: Mathematical formulas
    GRAPH = "graph"       # New: Graph structures
    TEMPORAL = "temporal" # New: Time-bound facts

@dataclass
class ParsedFact:
    raw: str
    fact_type: FactType
    predicate: str
    arguments: List[Any]
    metadata: Dict[str, Any]

class EKRParser:
    """Extended parser for complex fact formats"""
    
    def parse(self, statement: str) -> ParsedFact:
        """Parse any supported fact format"""
        
        # Clean the statement
        statement = statement.strip()
        if not statement.endswith('.'):
            statement += '.'
        
        # Try parsing as formula first
        if statement.startswith('Formula('):
            return self._parse_formula(statement)
        
        # Try parsing as graph
        if statement.startswith('Graph('):
            return self._parse_graph(statement)
        
        # Try parsing as temporal
        if statement.startswith('Temporal('):
            return self._parse_temporal(statement)
        
        # Check for typed arguments (contains ':')
        if ':' in statement and '(' in statement:
            return self._parse_typed(statement)
        
        # Count arguments to determine if n-ary
        if '(' in statement and ')' in statement:
            content = statement[statement.index('(')+1:statement.rindex(')')]
            args = self._split_arguments(content)
            
            if len(args) == 2:
                return self._parse_binary(statement)
            else:
                return self._parse_nary(statement)
        
        raise ValueError(f"Cannot parse: {statement}")
    
    def _split_arguments(self, content: str) -> List[str]:
        """Split arguments respecting nested structures"""
        args = []
        current = ""
        depth = 0
        
        for char in content:
            if char == ',' and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                if char in '([{':
                    depth += 1
                elif char in ')]}':
                    depth -= 1
                current += char
        
        if current.strip():
            args.append(current.strip())
        
        return args
    
    def _parse_binary(self, statement: str) -> ParsedFact:
        """Parse traditional binary relation"""
        match = re.match(r'^(\w+)\(([^,]+),\s*([^)]+)\)\.$', statement)
        if match:
            return ParsedFact(
                raw=statement,
                fact_type=FactType.BINARY,
                predicate=match.group(1),
                arguments=[match.group(2).strip(), match.group(3).strip()],
                metadata={}
            )
        raise ValueError(f"Invalid binary fact: {statement}")
    
    def _parse_nary(self, statement: str) -> ParsedFact:
        """Parse n-ary relation"""
        match = re.match(r'^(\w+)\(([^)]+)\)\.$', statement)
        if match:
            predicate = match.group(1)
            args = self._split_arguments(match.group(2))
            
            return ParsedFact(
                raw=statement,
                fact_type=FactType.NARY,
                predicate=predicate,
                arguments=args,
                metadata={'arity': len(args)}
            )
        raise ValueError(f"Invalid n-ary fact: {statement}")
    
    def _parse_typed(self, statement: str) -> ParsedFact:
        """Parse typed arguments"""
        match = re.match(r'^(\w+)\(([^)]+)\)\.$', statement)
        if match:
            predicate = match.group(1)
            args_str = match.group(2)
            args = self._split_arguments(args_str)
            
            typed_args = []
            roles = {}
            
            for i, arg in enumerate(args):
                if ':' in arg:
                    role, value = arg.split(':', 1)
                    role = role.strip()
                    value = value.strip()
                    typed_args.append({'role': role, 'value': value})
                    roles[role] = i
                else:
                    typed_args.append({'role': f'arg{i}', 'value': arg.strip()})
            
            return ParsedFact(
                raw=statement,
                fact_type=FactType.TYPED,
                predicate=predicate,
                arguments=typed_args,
                metadata={'roles': roles}
            )
        raise ValueError(f"Invalid typed fact: {statement}")
    
    def _parse_formula(self, statement: str) -> ParsedFact:
        """Parse mathematical formula"""
        # Extract content between Formula( and )
        content = statement[8:-2]  # Remove "Formula(" and ")."
        parts = self._split_arguments(content)
        
        formula_data = {}
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                formula_data[key] = value
        
        return ParsedFact(
            raw=statement,
            fact_type=FactType.FORMULA,
            predicate='Formula',
            arguments=[],
            metadata=formula_data
        )
    
    def _parse_graph(self, statement: str) -> ParsedFact:
        """Parse graph structure"""
        # Extract content
        content = statement[6:-2]  # Remove "Graph(" and ")."
        
        # Parse as pseudo-JSON
        graph_data = {
            'nodes': [],
            'edges': [],
            'properties': {}
        }
        
        # Simple parsing for demo
        if 'nodes:' in content:
            nodes_match = re.search(r'nodes:\[([^\]]+)\]', content)
            if nodes_match:
                nodes_str = nodes_match.group(1)
                graph_data['nodes'] = [n.strip() for n in nodes_str.split(',')]
        
        return ParsedFact(
            raw=statement,
            fact_type=FactType.GRAPH,
            predicate='Graph',
            arguments=[],
            metadata=graph_data
        )
    
    def _parse_temporal(self, statement: str) -> ParsedFact:
        """Parse temporal fact"""
        # Extract content
        content = statement[9:-2]  # Remove "Temporal(" and ")."
        parts = self._split_arguments(content)
        
        temporal_data = {}
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                temporal_data[key.strip()] = value.strip()
        
        return ParsedFact(
            raw=statement,
            fact_type=FactType.TEMPORAL,
            predicate='Temporal',
            arguments=[],
            metadata=temporal_data
        )


class EKRDatabase:
    """Extended database for complex facts"""
    
    def __init__(self, db_path: str = "ekr_knowledge.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
        self.parser = EKRParser()
    
    def _init_schema(self):
        """Initialize extended schema"""
        
        # Main facts table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS facts_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement TEXT NOT NULL,
                fact_type TEXT NOT NULL,
                fact_json TEXT,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 2
            )
        """)
        
        # Arguments for n-ary relations
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_arguments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id INTEGER,
                position INTEGER,
                role TEXT,
                value TEXT,
                value_type TEXT,
                FOREIGN KEY (fact_id) REFERENCES facts_v2(id)
            )
        """)
        
        # Dependencies between facts
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS fact_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_fact_id INTEGER,
                child_fact_id INTEGER,
                dependency_type TEXT,
                strength REAL,
                FOREIGN KEY (parent_fact_id) REFERENCES facts_v2(id),
                FOREIGN KEY (child_fact_id) REFERENCES facts_v2(id)
            )
        """)
        
        # Formulas
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS formulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                expression TEXT,
                domain TEXT,
                variables TEXT,
                constants TEXT,
                fact_id INTEGER,
                FOREIGN KEY (fact_id) REFERENCES facts_v2(id)
            )
        """)
        
        self.conn.commit()
    
    def add_fact(self, statement: str, source: str = "user") -> int:
        """Add a fact of any complexity"""
        
        # Parse the fact
        parsed = self.parser.parse(statement)
        
        # Store in main table
        cursor = self.conn.execute("""
            INSERT INTO facts_v2 (statement, fact_type, fact_json, source)
            VALUES (?, ?, ?, ?)
        """, (
            parsed.raw,
            parsed.fact_type.value,
            json.dumps({
                'predicate': parsed.predicate,
                'arguments': parsed.arguments,
                'metadata': parsed.metadata
            }),
            source
        ))
        
        fact_id = cursor.lastrowid
        
        # Store arguments if n-ary or typed
        if parsed.fact_type in [FactType.NARY, FactType.TYPED]:
            for i, arg in enumerate(parsed.arguments):
                if isinstance(arg, dict):  # Typed argument
                    self.conn.execute("""
                        INSERT INTO fact_arguments (fact_id, position, role, value, value_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (fact_id, i, arg.get('role'), arg.get('value'), 'typed'))
                else:  # Simple argument
                    self.conn.execute("""
                        INSERT INTO fact_arguments (fact_id, position, role, value, value_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (fact_id, i, f'arg{i}', arg, 'simple'))
        
        # Store formula if applicable
        if parsed.fact_type == FactType.FORMULA:
            self.conn.execute("""
                INSERT INTO formulas (name, expression, domain, fact_id)
                VALUES (?, ?, ?, ?)
            """, (
                parsed.metadata.get('name'),
                parsed.metadata.get('expr'),
                parsed.metadata.get('domain'),
                fact_id
            ))
        
        self.conn.commit()
        return fact_id
    
    def query_by_type(self, fact_type: FactType) -> List[Dict]:
        """Query facts by type"""
        cursor = self.conn.execute("""
            SELECT * FROM facts_v2 WHERE fact_type = ?
        """, (fact_type.value,))
        
        return [dict(row) for row in cursor]
    
    def query_nary_by_arity(self, min_arity: int) -> List[Dict]:
        """Find n-ary relations with at least min_arity arguments"""
        cursor = self.conn.execute("""
            SELECT f.*, COUNT(a.id) as arity
            FROM facts_v2 f
            LEFT JOIN fact_arguments a ON f.id = a.fact_id
            WHERE f.fact_type = 'nary'
            GROUP BY f.id
            HAVING arity >= ?
        """, (min_arity,))
        
        return [dict(row) for row in cursor]
    
    def query_formulas_by_domain(self, domain: str) -> List[Dict]:
        """Query formulas by domain"""
        cursor = self.conn.execute("""
            SELECT f.*, fm.name, fm.expression, fm.domain
            FROM facts_v2 f
            JOIN formulas fm ON f.id = fm.fact_id
            WHERE fm.domain = ?
        """, (domain,))
        
        return [dict(row) for row in cursor]
    
    def add_dependency(self, parent_id: int, child_id: int, 
                      dep_type: str = "requires", strength: float = 1.0):
        """Add dependency between facts"""
        self.conn.execute("""
            INSERT INTO fact_dependencies (parent_fact_id, child_fact_id, dependency_type, strength)
            VALUES (?, ?, ?, ?)
        """, (parent_id, child_id, dep_type, strength))
        self.conn.commit()
    
    def trace_dependencies(self, fact_id: int, max_depth: int = 5) -> List[List[int]]:
        """Trace dependency chains from a fact"""
        chains = []
        visited = set()
        
        def trace(fid: int, path: List[int], depth: int):
            if depth > max_depth or fid in visited:
                return
            
            visited.add(fid)
            path = path + [fid]
            
            cursor = self.conn.execute("""
                SELECT child_fact_id FROM fact_dependencies
                WHERE parent_fact_id = ?
            """, (fid,))
            
            children = [row['child_fact_id'] for row in cursor]
            
            if not children:
                chains.append(path)
            else:
                for child in children:
                    trace(child, path, depth + 1)
        
        trace(fact_id, [], 0)
        return chains


def demo_extended_facts():
    """Demonstrate extended fact capabilities"""
    
    print("🚀 EKR (Extended Knowledge Representation) Demo")
    print("=" * 60)
    
    # Create database
    db = EKRDatabase("demo_ekr.db")
    
    # Example facts of increasing complexity
    examples = [
        # Traditional binary
        "IsA(Socrates, Philosopher).",
        
        # N-ary relation
        "Connects(Berlin, Paris, Railway, 1054km, 8hours).",
        
        # Typed arguments
        "Reaction(catalyst:Platinum, substrate:H2, product:H2O, temp:25°C, pressure:1atm).",
        
        # Mathematical formula
        'Formula(name:EinsteinEnergy, expr:"E=mc^2", domain:Physics, constraints:["c=299792458m/s"]).',
        
        # Graph structure (simplified)
        "Graph(nodes:[A,B,C], edges:[AtoB,BtoC], properties:{type:directed}).",
        
        # Temporal fact
        "Temporal(fact:IsPresident(Biden,USA), time:2021-2025, duration:4years)."
    ]
    
    print("\n📝 Adding extended facts:")
    for i, fact in enumerate(examples, 1):
        try:
            fact_id = db.add_fact(fact, source="demo")
            parsed = db.parser.parse(fact)
            print(f"\n{i}. Type: {parsed.fact_type.value}")
            print(f"   Statement: {fact[:60]}...")
            print(f"   Predicate: {parsed.predicate}")
            print(f"   Arguments: {len(parsed.arguments)}")
            print(f"   ✅ Added with ID: {fact_id}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Query examples
    print("\n" + "=" * 60)
    print("📊 Querying extended facts:")
    
    # Find n-ary facts with 4+ arguments
    print("\n1. N-ary facts with 4+ arguments:")
    nary_facts = db.query_nary_by_arity(4)
    for fact in nary_facts:
        print(f"   - {fact['statement'][:60]}... (arity: {fact.get('arity', 'N/A')})")
    
    # Find formulas in Physics
    print("\n2. Formulas in Physics domain:")
    physics_formulas = db.query_formulas_by_domain("Physics")
    for formula in physics_formulas:
        print(f"   - {formula['name']}: {formula['expression']}")
    
    # Find typed facts
    print("\n3. Facts with typed arguments:")
    typed_facts = db.query_by_type(FactType.TYPED)
    for fact in typed_facts:
        data = json.loads(fact['fact_json'])
        roles = [arg['role'] for arg in data['arguments'] if isinstance(arg, dict)]
        print(f"   - {fact['statement'][:40]}...")
        print(f"     Roles: {', '.join(roles)}")
    
    print("\n" + "=" * 60)
    print("✅ EKR Demo Complete!")
    print("\nThis extended architecture enables:")
    print("• Complex multi-entity relationships")
    print("• Mathematical formula storage")
    print("• Temporal reasoning")
    print("• Graph-based knowledge")
    print("• Typed and role-based arguments")
    print("• Dependency tracking")


if __name__ == "__main__":
    demo_extended_facts()
