#!/usr/bin/env python3
"""
SEMANTIC_SIMILARITY FIX - Korrigierte Implementation
PROBLEM IDENTIFIZIERT: Threshold zu hoch, Parsing-Logik zu restriktiv
"""

import re
import time
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path

class SemanticSimilarityFixed:
    """Fixed implementation of semantic similarity with debug capabilities"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
    
    def _open_db(self):
        """Open database connection"""
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=FULL;")
            conn.execute("PRAGMA wal_autocheckpoint=1000;")
        except Exception:
            pass
        return conn
    
    def extract_predicate_fixed(self, stmt: str) -> str:
        """FIXED: More robust predicate extraction"""
        if not stmt or not isinstance(stmt, str):
            return None
        
        # Try multiple patterns
        patterns = [
            r'^(\w+)\s*\(',  # Standard: Predicate(
            r'^(\w+)',       # Fallback: Just first word
        ]
        
        for pattern in patterns:
            match = re.match(pattern, stmt.strip())
            if match:
                return match.group(1)
        
        return None
    
    def extract_arguments_fixed(self, stmt: str) -> list:
        """FIXED: More robust argument extraction with better parsing"""
        if not stmt or not isinstance(stmt, str):
            return []
        
        # Remove common prefixes and suffixes
        stmt = stmt.strip().rstrip('.')
        
        # Try to find parentheses content
        match = re.search(r'\((.*?)\)(?:[^)]*)?$', stmt)
        if not match:
            # Fallback: split by common delimiters
            if ',' in stmt:
                return [arg.strip() for arg in stmt.split(',') if arg.strip()]
            return [stmt.strip()]
        
        args_str = match.group(1)
        if not args_str.strip():
            return []
        
        # Simple comma split for now (can be enhanced for nested structures)
        arguments = []
        current_arg = ""
        paren_depth = 0
        
        for char in args_str:
            if char == '(':
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0:
                if current_arg.strip():
                    arguments.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
        
        # Add last argument
        if current_arg.strip():
            arguments.append(current_arg.strip())
        
        return arguments
    
    def extract_entities_fixed(self, stmt: str) -> list:
        """FIXED: Extract entities with better filtering"""
        args = self.extract_arguments_fixed(stmt)
        entities = []
        
        for arg in args:
            # Skip obvious non-entities
            if not arg or len(arg.strip()) == 0:
                continue
            
            # Clean the argument
            cleaned = arg.strip()
            
            # Skip Q() notation and similar
            if cleaned.startswith(('Q(', 'k:Q(', 'T:Q(', 'U:', 'V:')):
                continue
            
            # Remove prefixes like "k:", "T:" etc but keep the content
            if ':' in cleaned and not '(' in cleaned:
                parts = cleaned.split(':', 1)
                if len(parts) > 1:
                    cleaned = parts[1].strip()
            
            # Skip very short or numeric-only entities
            if len(cleaned) < 2 or cleaned.isdigit():
                continue
            
            entities.append(cleaned)
        
        return entities
    
    def calculate_similarity_fixed(self, stmt1: str, stmt2: str) -> float:
        """FIXED: More lenient similarity calculation with multiple approaches"""
        if stmt1 == stmt2:
            return 1.0
        
        # Approach 1: Predicate-based similarity
        pred1 = self.extract_predicate_fixed(stmt1)
        pred2 = self.extract_predicate_fixed(stmt2)
        
        predicate_similarity = 0.0
        if pred1 and pred2:
            if pred1 == pred2:
                predicate_similarity = 1.0
            else:
                predicate_similarity = SequenceMatcher(None, pred1, pred2).ratio()
        
        # Approach 2: Argument-based similarity
        args1 = self.extract_arguments_fixed(stmt1)
        args2 = self.extract_arguments_fixed(stmt2)
        
        argument_similarity = 0.0
        if args1 and args2:
            # Count exact matches
            matches = 0
            for arg1 in args1:
                if arg1 in args2:
                    matches += 1
            
            # Also count partial matches
            partial_matches = 0
            for arg1 in args1:
                for arg2 in args2:
                    if arg1 != arg2:  # Skip exact matches already counted
                        sim = SequenceMatcher(None, arg1, arg2).ratio()
                        if sim > 0.8:  # High similarity threshold for partial matches
                            partial_matches += 0.5  # Weight partial matches less
            
            total_matches = matches + partial_matches
            max_args = max(len(args1), len(args2))
            argument_similarity = total_matches / max_args if max_args > 0 else 0.0
        
        # Approach 3: Entity-based similarity
        entities1 = self.extract_entities_fixed(stmt1)
        entities2 = self.extract_entities_fixed(stmt2)
        
        entity_similarity = 0.0
        if entities1 and entities2:
            entity_matches = 0
            for entity1 in entities1:
                if entity1 in entities2:
                    entity_matches += 1
            
            max_entities = max(len(entities1), len(entities2))
            entity_similarity = entity_matches / max_entities if max_entities > 0 else 0.0
        
        # Approach 4: String-based similarity (fallback)
        string_similarity = SequenceMatcher(None, stmt1.lower(), stmt2.lower()).ratio()
        
        # FIXED: More lenient weighted combination
        final_similarity = (
            0.40 * predicate_similarity +    # Reduced from 50%
            0.25 * argument_similarity +     # Reduced from 30%
            0.15 * entity_similarity +       # Reduced from 20%
            0.20 * string_similarity         # NEW: String similarity component
        )
        
        return min(1.0, final_similarity)  # Cap at 1.0
    
    def find_similar_facts(self, statement: str, threshold: float = 0.1, limit: int = 50) -> dict:
        """FIXED: Find similar facts with comprehensive debugging"""
        start_time = time.time()
        
        # Input validation
        if not statement or not isinstance(statement, str):
            return {
                "error": "Invalid statement parameter",
                "execution_time": f"{time.time() - start_time:.3f}s"
            }
        
        # Parse input statement
        input_predicate = self.extract_predicate_fixed(statement)
        input_args = self.extract_arguments_fixed(statement)
        input_entities = self.extract_entities_fixed(statement)
        
        # Debug info
        debug_info = {
            "input_statement": statement,
            "input_predicate": input_predicate,
            "input_args": input_args,
            "input_entities": input_entities,
            "threshold": threshold
        }
        
        try:
            # Get all facts from database
            conn = self._open_db()
            cursor = conn.execute(
                "SELECT statement FROM facts WHERE statement IS NOT NULL AND length(statement) > 0"
            )
            all_facts = cursor.fetchall()
            conn.close()
            
            debug_info["total_facts_checked"] = len(all_facts)
            
            # Calculate similarities
            results = []
            similarity_distribution = {"0.0-0.1": 0, "0.1-0.3": 0, "0.3-0.5": 0, "0.5-0.7": 0, "0.7-1.0": 0}
            
            for (fact,) in all_facts:
                if fact == statement:
                    continue
                
                similarity = self.calculate_similarity_fixed(statement, fact)
                
                # Track similarity distribution for debugging
                if similarity >= 0.7:
                    similarity_distribution["0.7-1.0"] += 1
                elif similarity >= 0.5:
                    similarity_distribution["0.5-0.7"] += 1
                elif similarity >= 0.3:
                    similarity_distribution["0.3-0.5"] += 1
                elif similarity >= 0.1:
                    similarity_distribution["0.1-0.3"] += 1
                else:
                    similarity_distribution["0.0-0.1"] += 1
                
                if similarity >= threshold:
                    results.append((similarity, fact))
            
            # Sort and limit results
            results.sort(key=lambda x: x[0], reverse=True)
            results = results[:limit]
            
            execution_time = time.time() - start_time
            
            return {
                "results": results,
                "debug_info": debug_info,
                "similarity_distribution": similarity_distribution,
                "execution_time": f"{execution_time:.3f}s",
                "found_count": len(results)
            }
            
        except Exception as e:
            return {
                "error": f"Database error: {str(e)}",
                "debug_info": debug_info,
                "execution_time": f"{time.time() - start_time:.3f}s"
            }

def test_semantic_similarity_fix():
    """Test the fixed semantic similarity implementation"""
    db_path = "D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db"
    
    if not Path(db_path).exists():
        print(f"ERROR: Database not found at {db_path}")
        return
    
    # Create fixed implementation
    semantic = SemanticSimilarityFixed(db_path)
    
    # Test cases
    test_cases = [
        ("electromagnetic", 0.1),
        ("SystemPerformance", 0.1),
        ("water", 0.1),
        ("chemical reaction", 0.1),
        ("LSD molecular structure", 0.1),
    ]
    
    print("=== SEMANTIC SIMILARITY FIX TEST ===")
    
    for statement, threshold in test_cases:
        print(f"\n--- Testing: '{statement}' (threshold: {threshold}) ---")
        
        result = semantic.find_similar_facts(statement, threshold, 5)
        
        if "error" in result:
            print(f"ERROR: {result['error']}")
            continue
        
        print(f"Execution time: {result['execution_time']}")
        print(f"Found {result['found_count']} similar facts")
        print(f"Similarity distribution: {result['similarity_distribution']}")
        
        if result['results']:
            print("Top results:")
            for score, fact in result['results'][:3]:
                print(f"  Score {score:.3f}: {fact[:100]}...")
        else:
            print("No similar facts found above threshold")
        
        # Debug info
        debug = result['debug_info']
        print(f"Debug - Predicate: {debug['input_predicate']}, Args: {len(debug['input_args'])}, Entities: {len(debug['input_entities'])}")

if __name__ == "__main__":
    test_semantic_similarity_fix()
