"""
Optimized Fact Extractor for Phi3/Ollama LLM Responses
=======================================================
Extracts Predicate(Entity1, Entity2) facts from LLM text
Optimized for Phi3's output format
"""

import re
from typing import List, Set

class OptimizedFactExtractor:
    """Extract facts from Phi3/Ollama responses with improved pattern matching"""
    
    def __init__(self):
        # More flexible pattern - allows lowercase and various formats
        self.fact_patterns = [
            # Standard format: Predicate(Entity1, Entity2)
            re.compile(r'([A-Za-z][A-Za-z0-9_]*)\s*\(\s*([^,\)]+?)\s*,\s*([^\)]+?)\s*\)\.?', re.MULTILINE),
            # With quotes: Predicate("Entity1", "Entity2") 
            re.compile(r'([A-Za-z][A-Za-z0-9_]*)\s*\(\s*"?([^",\)]+?)"?\s*,\s*"?([^"\)]+?)"?\s*\)\.?', re.MULTILINE),
            # Inline mentions: "Predicate(Entity1,Entity2)"
            re.compile(r'"([A-Za-z][A-Za-z0-9_]*)\s*\(\s*([^,\)]+?)\s*,\s*([^\)]+?)\s*\)"', re.MULTILINE),
        ]
        
        # Test/Example patterns to exclude
        self.exclude_patterns = [
            r'^Test', r'^Example', r'^Sample', r'^Demo',
            r'^e\.g\.', r'^i\.e\.', r'^Foo', r'^Bar'
        ]
        self.exclude_regex = re.compile('|'.join(self.exclude_patterns), re.IGNORECASE)
    
    def extract_facts(self, text: str, topic: str = '') -> List[str]:
        """
        Extract facts from LLM response text
        
        Args:
            text: The LLM response text
            topic: Original topic/query for context
            
        Returns:
            List of unique, cleaned facts
        """
        if not text:
            return []
            
        facts = []
        seen = set()
        
        # Try all patterns
        for pattern in self.fact_patterns:
            for match in pattern.finditer(text):
                predicate = match.group(1).strip()
                entity1 = match.group(2).strip()
                entity2 = match.group(3).strip()
                
                # Clean entities
                entity1 = self._clean_entity(entity1)
                entity2 = self._clean_entity(entity2)
                
                # Skip invalid facts
                if not self._is_valid_fact(predicate, entity1, entity2):
                    continue
                
                # Format fact
                fact = f"{predicate}({entity1}, {entity2})."
                
                # Skip duplicates
                if fact in seen:
                    continue
                seen.add(fact)
                
                facts.append(fact)
                
                # Limit to prevent spam
                if len(facts) >= 20:
                    break
            
            if len(facts) >= 20:
                break
        
        return facts
    
    def _clean_entity(self, entity: str) -> str:
        """Clean and normalize entity string"""
        # Remove quotes, parentheses, extra spaces
        entity = entity.strip('"\'() \t\n\r')
        
        # Remove trailing punctuation except underscore
        entity = entity.rstrip('.,;:!?')
        
        # Replace multiple spaces with single space
        entity = ' '.join(entity.split())
        
        return entity
    
    def _is_valid_fact(self, predicate: str, entity1: str, entity2: str) -> bool:
        """Check if fact is valid and not a test/example"""
        
        # Check minimum requirements
        if not predicate or not entity1 or not entity2:
            return False
        
        # Check minimum length
        if len(predicate) < 2 or len(entity1) < 2 or len(entity2) < 2:
            return False
        
        # Check for test/example patterns
        for part in [predicate, entity1, entity2]:
            if self.exclude_regex.match(part):
                return False
        
        # Check for placeholder values
        placeholders = ['X', 'Y', 'A', 'B', 'Entity1', 'Entity2', 
                       'Subject', 'Object', 'Arg1', 'Arg2']
        if entity1 in placeholders or entity2 in placeholders:
            # Unless it's in a real context (e.g., "France")
            if len(entity1) <= 10 and len(entity2) <= 10:
                return False
        
        # Check for overly long entities (likely errors)
        if len(entity1) > 100 or len(entity2) > 100:
            return False
        
        return True
    
    def generate_related_facts(self, statement: str) -> List[str]:
        """Generate related facts based on a statement"""
        facts = []
        
        # Parse the statement
        for pattern in self.fact_patterns:
            match = pattern.match(statement.strip())
            if match:
                predicate = match.group(1)
                entity1 = self._clean_entity(match.group(2))
                entity2 = self._clean_entity(match.group(3))
                
                # Generate inverse/related facts
                if predicate == 'HasPart':
                    facts.append(f"PartOf({entity2}, {entity1}).")
                elif predicate == 'PartOf':
                    facts.append(f"HasPart({entity2}, {entity1}).")
                elif predicate == 'IsA':
                    facts.append(f"InstanceOf({entity1}, {entity2}).")
                elif predicate == 'Causes':
                    facts.append(f"CausedBy({entity2}, {entity1}).")
                elif predicate == 'Before':
                    facts.append(f"After({entity2}, {entity1}).")
                    
                break
        
        return facts[:5]  # Limit related facts

# Global instance
fact_extractor = OptimizedFactExtractor()

def extract_facts_from_llm(text: str, topic: str = '') -> List[str]:
    """
    Main function called by the API
    
    Args:
        text: LLM response text
        topic: Original query/topic for context
        
    Returns:
        List of extracted facts
    """
    return fact_extractor.extract_facts(text, topic)

def generate_related_facts(statement: str) -> List[str]:
    """
    Generate related facts from a statement
    
    Args:
        statement: A fact statement
        
    Returns:
        List of related facts
    """
    return fact_extractor.generate_related_facts(statement)
