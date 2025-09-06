"""
Refined Fact Extractor for Phi3/Ollama LLM Responses
=====================================================
Extracts only valid Predicate(Entity1, Entity2) facts
Fixed: Better validation and filtering
"""

import re
from typing import List, Set

class RefinedFactExtractor:
    """Extract facts with improved validation and filtering"""
    
    def __init__(self):
        # Main pattern - more flexible format
        self.fact_pattern = re.compile(
            r'\b([A-Za-z][A-Za-z0-9_]*)\s*\(\s*([A-Za-z][A-Za-z0-9_\s\-\.]*?)\s*,\s*([A-Za-z][A-Za-z0-9_\s\-\.]*?)\s*\)\s*\.?',
            re.MULTILINE
        )
        
        # Invalid predicates to exclude
        self.invalid_predicates = {
            'e.g', 'i.e', 'etc', 'vs', 'aka', 'ref',
            'note', 'see', 'cf', 'viz', 'ibid'
        }
        
        # Common false positive patterns
        self.exclude_patterns = [
            r'^(Test|Example|Sample|Demo|Foo|Bar)',
            r'\([^,]*\([^)]*\)',  # Nested parentheses
            r'[0-9]{3,}',  # Years or long numbers in wrong place
        ]
        
    def extract_facts(self, text: str, topic: str = '') -> List[str]:
        """
        Extract valid facts from LLM response
        
        Args:
            text: The LLM response text
            topic: Original topic for context
            
        Returns:
            List of valid, unique facts
        """
        if not text:
            return []
        
        print(f"[FactExtractor] Processing text length: {len(text)} chars")
        print(f"[FactExtractor] First 200 chars: {text[:200]}...")
            
        facts = []
        seen = set()
        
        # Find all potential facts
        matches = list(self.fact_pattern.finditer(text))
        print(f"[FactExtractor] Found {len(matches)} potential fact matches")
        
        for i, match in enumerate(matches):
            predicate = match.group(1).strip()
            entity1 = match.group(2).strip()
            entity2 = match.group(3).strip()
            print(f"[FactExtractor] Match {i+1}: {predicate}({entity1}, {entity2})")
            
            # Skip invalid predicates
            if predicate.lower() in self.invalid_predicates:
                continue
            
            # Skip if predicate is too short (relaxed number check)
            if len(predicate) < 2:
                continue
                
            # Clean and validate entities
            entity1 = self._clean_entity(entity1)
            entity2 = self._clean_entity(entity2)
            
            # Validate fact
            if not self._is_valid_fact(predicate, entity1, entity2):
                print(f"[FactExtractor] Invalid fact: {predicate}({entity1}, {entity2})")
                continue
            
            # Check for false positives
            if self._is_false_positive(predicate, entity1, entity2):
                print(f"[FactExtractor] False positive: {predicate}({entity1}, {entity2})")
                continue
            
            # Format fact properly
            fact = f"{predicate}({entity1}, {entity2})."
            
            # Skip duplicates
            if fact in seen:
                print(f"[FactExtractor] Duplicate: {fact}")
                continue
            seen.add(fact)
            
            print(f"[FactExtractor] Valid fact added: {fact}")
            facts.append(fact)
            
            # Limit results
            if len(facts) >= 20:
                break
        
        print(f"[FactExtractor] Final result: {len(facts)} facts extracted")
        return facts
    
    def _clean_entity(self, entity: str) -> str:
        """Clean entity string"""
        # Remove quotes and extra spaces
        entity = entity.strip('"\'')
        entity = ' '.join(entity.split())
        
        # Remove trailing punctuation
        entity = entity.rstrip('.,;:!?')
        
        # Remove content in parentheses if it makes entity invalid
        if '(' in entity:
            base = entity.split('(')[0].strip()
            if len(base) >= 2:
                entity = base
        
        return entity
    
    def _is_valid_fact(self, predicate: str, entity1: str, entity2: str) -> bool:
        """Validate fact components"""
        
        # Check basic requirements
        if not all([predicate, entity1, entity2]):
            return False
        
        # Length requirements (relaxed)
        if len(predicate) < 2 or len(predicate) > 50:
            return False
        if len(entity1) < 1 or len(entity1) > 100:
            return False
        if len(entity2) < 1 or len(entity2) > 100:
            return False
        
        # Entities should not be just numbers
        if entity1.isdigit() or entity2.isdigit():
            return False
        
        # Check for placeholder patterns
        placeholders = ['X', 'Y', 'A', 'B', 'Entity1', 'Entity2']
        if entity1 in placeholders and entity2 in placeholders:
            return False
        
        # Entities should not contain certain characters (relaxed)
        invalid_chars = ['(', ')', ';', ':', '!', '?']
        for char in invalid_chars:
            if char in entity1 or char in entity2:
                return False
        
        return True
    
    def _is_false_positive(self, predicate: str, entity1: str, entity2: str) -> bool:
        """Check for common false positives"""
        
        # Check for test/example patterns
        test_terms = ['test', 'example', 'sample', 'demo', 'foo', 'bar']
        for term in test_terms:
            if term in predicate.lower() or term in entity1.lower() or term in entity2.lower():
                return True
        
        # Check if entities are too similar (likely parsing error)
        if entity1.lower() == entity2.lower():
            return True
        
        # Check for e.g., i.e., etc. in entities
        if 'e.g' in entity1.lower() or 'e.g' in entity2.lower():
            return True
        if 'i.e' in entity1.lower() or 'i.e' in entity2.lower():
            return True
        
        # Check for common parsing errors
        if entity1.startswith('e.g') or entity2.startswith('e.g'):
            return True
        if entity1.startswith('i.e') or entity2.startswith('i.e'):
            return True
        
        # Check for years in predicates (common error)
        if re.search(r'\d{4}', predicate):
            return True
        
        return False

# Global instance
fact_extractor = RefinedFactExtractor()

def extract_facts_from_llm(text: str, topic: str = '') -> List[str]:
    """
    Main function for API compatibility
    
    Args:
        text: LLM response text
        topic: Query topic for context
        
    Returns:
        List of validated facts
    """
    return fact_extractor.extract_facts(text, topic)

# Additional utility functions
def validate_fact_format(fact: str) -> bool:
    """Check if a string is a valid fact format"""
    pattern = re.compile(
        r'^[A-Z][A-Za-z0-9_]*\([A-Za-z][A-Za-z0-9_\s]*,\s*[A-Za-z][A-Za-z0-9_\s]*\)\.$'
    )
    return bool(pattern.match(fact))

def fix_common_errors(fact: str) -> str:
    """Attempt to fix common formatting errors"""
    fact = fact.strip()
    
    # Add missing period
    if not fact.endswith('.'):
        fact += '.'
    
    # Fix spacing around parentheses
    fact = re.sub(r'\s*\(\s*', '(', fact)
    fact = re.sub(r'\s*\)\s*', ')', fact)
    
    # Fix spacing around comma
    fact = re.sub(r'\s*,\s*', ', ', fact)
    
    return fact
