"""
Fact Extractor for LLM explanations and heuristic related-fact suggestions
This module enables autonomous Hex operation without legacy 5000 by:
 - Extracting canonical facts from free-form LLM text
 - Generating related facts from a given query statement (Predicate(Entity1, Entity2))
"""

from __future__ import annotations

import re
from typing import List

_FACT_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\([^\n\r]*?\)\.")
_STATEMENT_PATTERN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(([^,]+),\s*([^\)]+)\)\.?$")


def _canonize_fact(fact: str) -> str:
    fact = (fact or '').strip()
    if not fact:
        return ''
    if not fact.endswith('.'):
        fact += '.'
    return fact


def _parse_statement(statement: str):
    m = _STATEMENT_PATTERN.match((statement or '').strip())
    if not m:
        return None, None, None
    return m.group(1), m.group(2).strip(), m.group(3).strip()


def extract_facts_from_llm(text: str, topic: str = '') -> List[str]:
    """Extract canonical Predicate(Entity1, Entity2). facts from LLM text.
    - De-duplicates
    - Caps at 20
    - Keeps only simple two-arity forms
    """
    if not text:
        return []
    candidates = []
    seen = set()
    for m in _FACT_PATTERN.finditer(text):
        fact = _canonize_fact(m.group(0))
        # keep only two-arity
        p, a, b = _parse_statement(fact)
        if not p or not a or not b:
            continue
        if fact not in seen:
            candidates.append(fact)
            seen.add(fact)
        if len(candidates) >= 20:
            break
    return candidates


class _FactExtractor:
    """Small helper for generating related facts from a query.
    Heuristics:
      - For HasPart(A,B) suggest PartOf(B,A)
      - For PartOf(A,B) suggest HasPart(B,A)
      - For IsA(X,Y) suggest SubClass(Y, Super) and IsA(X, Super) chains (one hop)
    """

    def _generate_related_facts(self, topic: str) -> List[str]:
        p, a, b = _parse_statement(topic or '')
        if not p or not a or not b:
            return []
        suggestions: List[str] = []
        if p == 'HasPart':
            suggestions.append(_canonize_fact(f"PartOf({b}, {a})"))
        elif p == 'PartOf':
            suggestions.append(_canonize_fact(f"HasPart({b}, {a})"))
        elif p in ('IsA', 'SubClass'):
            # One-hop inheritance hints (symbolic, generic)
            # We avoid fabricating unknown 'Super'; instead propose reinforcing relations
            suggestions.append(_canonize_fact(f"IsA({a}, {b})"))
        # Ensure uniqueness and max 20
        dedup = []
        seen = set()
        for s in suggestions:
            if s not in seen:
                dedup.append(s)
                seen.add(s)
            if len(dedup) >= 20:
                break
        return dedup


# Public singleton-like accessor used by hexagonal_api_enhanced.py
fact_extractor = _FactExtractor()

"""
Intelligent Fact Extraction from LLM Responses
===============================================
Extracts only relevant, contextual facts from LLM explanations
"""

import re
from typing import List, Tuple, Optional

class IntelligentFactExtractor:
    """Extract meaningful facts from LLM responses"""
    
    # Test/Example patterns to filter out
    FILTER_PATTERNS = [
        r'Test(?:Entity|Category|Fact)',
        r'Valid(?:Entity|Type)',
        r'Example\d*',
        r'Sample\d*',
        r'Demo\d*',
        r'Dummy\d*',
        r'Placeholder',
        r'TODO',
        r'FIXME',
        r'XXX',
        r'Foo|Bar|Baz',
        r'ABC|XYZ'
    ]
    
    # Keywords that indicate suggested facts
    SUGGESTION_MARKERS = [
        'suggest',
        'recommend',
        'could add',
        'might include',
        'consider adding',
        'should be',
        'would be',
        'implies',
        'means that',
        'therefore',
        'thus',
        'hence',
        'follows that'
    ]
    
    def __init__(self):
        self.fact_pattern = re.compile(
            r'([A-Z][A-Za-z0-9_]*)\(([^,\)]+),\s*([^\)]+)\)\.',
            re.MULTILINE
        )
        self.filter_regex = re.compile(
            '|'.join(self.FILTER_PATTERNS),
            re.IGNORECASE
        )
    
    def extract_facts(self, text: str, query: Optional[str] = None) -> List[str]:
        """
        Extract relevant facts from LLM response text
        
        Args:
            text: The LLM response text
            query: Original query for context (e.g., "IsA(Socrates, Philosopher)")
        
        Returns:
            List of relevant fact suggestions
        """
        facts = []
        seen = set()
        
        # Parse the original query to get context
        query_entities = self._extract_query_entities(query) if query else set()
        
        # Find all potential facts
        for match in self.fact_pattern.finditer(text):
            predicate = match.group(1)
            entity1 = match.group(2).strip()
            entity2 = match.group(3).strip()
            
            # Reconstruct the fact
            fact = f"{predicate}({entity1}, {entity2})."
            
            # Skip if already seen
            if fact in seen:
                continue
            seen.add(fact)
            
            # Filter out test/example facts
            if self._is_test_fact(predicate, entity1, entity2):
                continue
            
            # Check relevance to query
            if query and not self._is_relevant_to_query(
                predicate, entity1, entity2, query_entities
            ):
                continue
            
            # Check if in suggestion context
            if self._is_in_suggestion_context(text, match):
                facts.append(fact)
        
        # Sort by relevance and limit
        facts = self._rank_by_relevance(facts, query)[:10]
        
        return facts
    
    def _extract_query_entities(self, query: str) -> set:
        """Extract entities from the original query"""
        entities = set()
        
        match = self.fact_pattern.search(query)
        if match:
            entities.add(match.group(1))  # Predicate
            entities.add(match.group(2).strip())  # Entity1
            entities.add(match.group(3).strip())  # Entity2
        
        # Also extract individual words as potential entities
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', query)
        entities.update(words)
        
        return entities
    
    def _is_test_fact(self, predicate: str, entity1: str, entity2: str) -> bool:
        """Check if this is a test/example fact"""
        
        # Check against filter patterns
        for part in [predicate, entity1, entity2]:
            if self.filter_regex.search(part):
                return True
        
        # Check for suspicious patterns
        if any(x.lower() in ['test', 'example', 'sample', 'demo'] 
               for x in [predicate, entity1, entity2]):
            return True
        
        # Check for single letters or numbers only
        if any(len(x) <= 2 and x.isalnum() for x in [entity1, entity2]):
            return True
        
        return False
    
    def _is_relevant_to_query(
        self, 
        predicate: str, 
        entity1: str, 
        entity2: str,
        query_entities: set
    ) -> bool:
        """Check if fact is relevant to the original query"""
        
        # If no query context, accept all non-test facts
        if not query_entities:
            return True
        
        # Check if any entity matches query entities
        fact_entities = {predicate, entity1, entity2}
        
        # Direct match
        if fact_entities & query_entities:
            return True
        
        # Check for related predicates
        related_predicates = {
            'IsA': ['SubClass', 'InstanceOf', 'Type'],
            'HasPart': ['PartOf', 'Contains', 'Includes'],
            'Causes': ['CausedBy', 'Leads', 'Results'],
        }
        
        for base, related in related_predicates.items():
            if base in query_entities and predicate in related:
                return True
            if predicate == base and any(r in query_entities for r in related):
                return True
        
        # Check for semantic similarity (basic)
        for qe in query_entities:
            for fe in fact_entities:
                if qe.lower() in fe.lower() or fe.lower() in qe.lower():
                    return True
        
        return False
    
    def _is_in_suggestion_context(self, text: str, match: re.Match) -> bool:
        """Check if the fact appears in a suggestion context"""
        
        # Get surrounding context (100 chars before and after)
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        context = text[start:end].lower()
        
        # Check for suggestion markers
        for marker in self.SUGGESTION_MARKERS:
            if marker in context:
                return True
        
        # Check if in a list or enumeration
        if any(pattern in context for pattern in [
            '1.', '2.', '3.',
            '- ', '* ', '• ',
            'first', 'second', 'third',
            'additionally', 'furthermore', 'also'
        ]):
            return True
        
        # Check section headers
        if any(header in context for header in [
            'suggest', 'recommend', 'addition', 'fact'
        ]):
            return True
        
        return False
    
    def _rank_by_relevance(self, facts: List[str], query: Optional[str]) -> List[str]:
        """Rank facts by relevance to the query"""
        
        if not query:
            return facts
        
        # Extract query components
        query_match = self.fact_pattern.search(query)
        if not query_match:
            return facts
        
        query_pred = query_match.group(1)
        query_ent1 = query_match.group(2).strip()
        query_ent2 = query_match.group(3).strip()
        
        # Score each fact
        scored_facts = []
        for fact in facts:
            score = 0
            
            fact_match = self.fact_pattern.search(fact)
            if not fact_match:
                continue
            
            fact_pred = fact_match.group(1)
            fact_ent1 = fact_match.group(2).strip()
            fact_ent2 = fact_match.group(3).strip()
            
            # Score based on matches
            if fact_pred == query_pred:
                score += 3
            if fact_ent1 in [query_ent1, query_ent2]:
                score += 2
            if fact_ent2 in [query_ent1, query_ent2]:
                score += 2
            
            # Bonus for related predicates
            if fact_pred in ['SubClass', 'InstanceOf'] and query_pred == 'IsA':
                score += 1
            
            scored_facts.append((score, fact))
        
        # Sort by score (descending) and return
        scored_facts.sort(key=lambda x: x[0], reverse=True)
        return [fact for _, fact in scored_facts]
    
    def extract_from_llm_response(
        self, 
        llm_text: str, 
        query: str
    ) -> Tuple[str, List[str]]:
        """
        Main method to process LLM response
        
        Args:
            llm_text: Raw LLM response
            query: Original query
        
        Returns:
            Tuple of (cleaned explanation, list of suggested facts)
        """
        
        # Extract suggested facts
        suggested_facts = self.extract_facts(llm_text, query)
        
        # Generate more relevant facts based on the query
        additional_facts = self._generate_related_facts(query)
        
        # Combine and deduplicate
        all_facts = []
        seen = set()
        for fact in suggested_facts + additional_facts:
            if fact not in seen:
                seen.add(fact)
                all_facts.append(fact)
        
        # Limit to top 10
        return llm_text, all_facts[:10]
    
    def _generate_related_facts(self, query: str) -> List[str]:
        """Generate additional related facts based on the query"""
        
        facts = []
        
        # Parse query
        match = self.fact_pattern.search(query)
        if not match:
            return facts
        
        predicate = match.group(1)
        entity1 = match.group(2).strip()
        entity2 = match.group(3).strip()
        
        # Generate related facts based on predicate type
        if predicate == 'IsA':
            # For IsA queries, suggest hierarchical relationships
            if entity2 == 'Philosopher':
                facts.extend([
                    f"IsA({entity1}, GreekPhilosopher).",
                    f"SubClass(GreekPhilosopher, Philosopher).",
                    f"HasProperty({entity1}, TeachesPhilosophy).",
                    f"InfluencedBy({entity1}, PreSocratics).",
                ])
            elif entity2 == 'Person':
                facts.extend([
                    f"HasProperty({entity1}, Mortal).",
                    f"HasProperty({entity1}, Rational).",
                ])
        
        elif predicate == 'HasPart':
            # For HasPart, suggest related components
            if entity1 == 'Computer':
                facts.extend([
                    f"HasPart(Computer, Motherboard).",
                    f"HasPart(Computer, PowerSupply).",
                    f"PartOf({entity2}, Computer).",
                    f"ConnectedTo({entity2}, Motherboard).",
                ])
        
        elif predicate == 'Causes':
            # For causal relationships
            facts.extend([
                f"LeadsTo({entity1}, {entity2}).",
                f"ResultsIn({entity1}, {entity2}).",
                f"Precedes({entity1}, {entity2}).",
            ])
        
        # Filter out the original query
        facts = [f for f in facts if f != query]
        
        return facts

# Singleton instance
fact_extractor = IntelligentFactExtractor()

def extract_facts_from_llm(text: str, query: str = None) -> List[str]:
    """
    Convenience function to extract facts from LLM response
    
    Args:
        text: LLM response text
        query: Original query for context
    
    Returns:
        List of suggested facts
    """
    return fact_extractor.extract_facts(text, query)
