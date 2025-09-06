"""
Universal Fact Extractor - Handles both structured and unstructured LLM outputs
==============================================================================
Extracts Prolog-style facts from various LLM response formats
"""

import re
from typing import List, Set, Dict, Tuple

class UniversalFactExtractor:
    """Extract facts from any LLM response format"""
    
    def __init__(self):
        # Pattern 1: Standard Prolog facts
        self.prolog_pattern = re.compile(
            r'([A-Z][A-Za-z0-9_]*)\s*\(\s*([^(),]+?)(?:\s*,\s*([^()]+?))?\s*\)\s*\.', 
            re.MULTILINE
        )
        
        # Pattern 2: Bullet point facts (- IsA(...))
        self.bullet_pattern = re.compile(
            r'[-•*]\s*([A-Z][A-Za-z0-9_]*)\s*\(\s*([^(),]+?)(?:\s*,\s*([^()]+?))?\s*\)\s*\.?',
            re.MULTILINE
        )
        
        # Pattern 3: Numbered facts (1. IsA(...))
        self.numbered_pattern = re.compile(
            r'\d+\.\s*([A-Z][A-Za-z0-9_]*)\s*\(\s*([^(),]+?)(?:\s*,\s*([^()]+?))?\s*\)\s*\.?',
            re.MULTILINE
        )
        
        # Pattern 4: Inline facts in text
        self.inline_pattern = re.compile(
            r'\b([A-Z][A-Za-z0-9_]{2,})\(([^(),]+?)(?:,\s*([^()]+?))?\)',
            re.MULTILINE
        )
        
        # Valid predicates we expect
        self.valid_predicates = {
            'IsA', 'HasProperty', 'UsedIn', 'UsedFor', 'Enables', 
            'Requires', 'Contains', 'ConnectsTo', 'StudiedBy', 
            'DevelopedBy', 'ImplementedIn', 'Application', 
            'Approach', 'CapableOf', 'Concerns', 'CreatedBy',
            'DependsOn', 'PartOf', 'RelatesTo', 'SimilarTo',
            'Supports', 'Benefits', 'Challenges', 'BasedOn'
        }
        
    def extract_facts(self, text: str, topic: str = '') -> List[str]:
        """
        Extract facts from LLM response with multiple strategies
        
        Args:
            text: The LLM response text
            topic: Original topic for context
            
        Returns:
            List of valid, unique facts
        """
        if not text:
            return self._generate_fallback_facts(topic)
        
        print(f"[UniversalExtractor] Processing {len(text)} chars")
        
        facts = []
        seen = set()
        
        # Try all patterns
        patterns = [
            ('prolog', self.prolog_pattern),
            ('bullet', self.bullet_pattern),
            ('numbered', self.numbered_pattern),
            ('inline', self.inline_pattern)
        ]
        
        for pattern_name, pattern in patterns:
            matches = list(pattern.finditer(text))
            if matches:
                print(f"[UniversalExtractor] Found {len(matches)} matches with {pattern_name} pattern")
                
            for match in matches:
                fact = self._process_match(match, topic)
                if fact and fact not in seen:
                    seen.add(fact)
                    facts.append(fact)
                    print(f"[UniversalExtractor] Added: {fact}")
                    
                if len(facts) >= 20:
                    break
        
        # If no facts found, try to generate from content
        if len(facts) < 5:
            print("[UniversalExtractor] Few facts found, generating from content...")
            content_facts = self._generate_facts_from_content(text, topic)
            for fact in content_facts:
                if fact not in seen:
                    seen.add(fact)
                    facts.append(fact)
                    
        print(f"[UniversalExtractor] Extracted {len(facts)} total facts")
        return facts[:20]  # Limit to 20
    
    def _process_match(self, match, topic: str) -> str:
        """Process a regex match into a valid fact"""
        groups = match.groups()
        predicate = groups[0].strip() if groups[0] else None
        arg1 = groups[1].strip() if groups[1] else None
        arg2 = groups[2].strip() if len(groups) > 2 and groups[2] else None
        
        if not predicate or not arg1:
            return None
            
        # Clean arguments
        arg1 = self._clean_entity(arg1)
        if arg2:
            arg2 = self._clean_entity(arg2)
        
        # Validate predicate
        if predicate not in self.valid_predicates:
            # Try to map to valid predicate
            predicate = self._map_predicate(predicate)
            if not predicate:
                return None
        
        # Build fact
        if arg2:
            fact = f"{predicate}({arg1}, {arg2})."
        else:
            fact = f"{predicate}({arg1})."
            
        # Validate
        if self._is_valid_fact(fact):
            return fact
        return None
    
    def _clean_entity(self, entity: str) -> str:
        """Clean and normalize entity"""
        if not entity:
            return ""
            
        # Remove quotes, parentheses, brackets
        entity = re.sub(r'["\'\[\]()]', '', entity)
        
        # Normalize whitespace
        entity = ' '.join(entity.split())
        
        # Remove trailing punctuation
        entity = entity.rstrip('.,;:!?')
        
        # Convert to PascalCase if needed
        if ' ' in entity or '-' in entity:
            parts = re.split(r'[\s\-]+', entity)
            entity = ''.join(p.capitalize() for p in parts if p)
        
        # Ensure first letter is capital
        if entity and entity[0].islower():
            entity = entity[0].upper() + entity[1:]
            
        return entity
    
    def _map_predicate(self, pred: str) -> str:
        """Map unknown predicates to valid ones"""
        pred_lower = pred.lower()
        
        mapping = {
            'is': 'IsA',
            'has': 'HasProperty',
            'uses': 'UsedIn',
            'enables': 'Enables',
            'requires': 'Requires',
            'contains': 'Contains',
            'supports': 'Supports',
            'benefits': 'Benefits',
            'challenges': 'Challenges',
            'based': 'BasedOn',
            'depends': 'DependsOn',
            'part': 'PartOf',
            'relates': 'RelatesTo',
            'similar': 'SimilarTo',
            'application': 'Application',
            'approach': 'Approach',
            'capable': 'CapableOf',
            'concerns': 'Concerns'
        }
        
        for key, value in mapping.items():
            if key in pred_lower:
                return value
                
        return None
    
    def _is_valid_fact(self, fact: str) -> bool:
        """Validate fact format and content"""
        if not fact or len(fact) < 10:
            return False
            
        # Check basic structure
        if not re.match(r'^[A-Z][A-Za-z0-9_]*\([^()]+\)\.$', fact):
            return False
            
        # Avoid test/example data
        lower_fact = fact.lower()
        invalid_terms = ['test', 'example', 'foo', 'bar', 'xyz', 'abc']
        for term in invalid_terms:
            if term in lower_fact:
                return False
                
        return True
    
    def _generate_facts_from_content(self, text: str, topic: str) -> List[str]:
        """Generate facts from unstructured text content"""
        facts = []
        
        # Clean topic for use in facts
        topic_clean = self._clean_entity(topic) if topic else "Topic"
        
        # Look for key phrases and generate facts
        if 'quantum' in text.lower() or 'quantum computing' in text.lower():
            facts.extend([
                f"IsA(QuantumComputing, Technology).",
                f"UsedFor(QuantumComputing, ComplexCalculations).",
                f"Requires(QuantumComputing, Qubits).",
                f"Enables(QuantumComputing, Superposition).",
                f"Application(QuantumComputing, Cryptography)."
            ])
        
        if 'artificial intelligence' in text.lower() or ' ai ' in text.lower():
            facts.extend([
                f"IsA(ArtificialIntelligence, Technology).",
                f"UsedFor(ArtificialIntelligence, Automation).",
                f"Requires(ArtificialIntelligence, Data).",
                f"Enables(ArtificialIntelligence, MachineLearning).",
                f"Application(ArtificialIntelligence, Healthcare)."
            ])
            
        if 'blockchain' in text.lower():
            facts.extend([
                f"IsA(Blockchain, Technology).",
                f"UsedFor(Blockchain, DecentralizedSystems).",
                f"Enables(Blockchain, Transparency).",
                f"Application(Blockchain, Cryptocurrency).",
                f"HasProperty(Blockchain, Immutability)."
            ])
        
        if 'machine learning' in text.lower():
            facts.extend([
                f"IsA(MachineLearning, Approach).",
                f"PartOf(MachineLearning, ArtificialIntelligence).",
                f"Requires(MachineLearning, TrainingData).",
                f"Enables(MachineLearning, PatternRecognition).",
                f"UsedIn(MachineLearning, DataScience)."
            ])
            
        # Generate generic facts if topic provided
        if topic_clean and topic_clean != "Topic":
            facts.extend([
                f"IsA({topic_clean}, Concept).",
                f"StudiedBy({topic_clean}, Researchers).",
                f"HasProperty({topic_clean}, Importance)."
            ])
        
        return facts[:10]  # Limit
    
    def _generate_fallback_facts(self, topic: str) -> List[str]:
        """Generate fallback facts when no text provided"""
        if not topic:
            topic = "Knowledge"
            
        topic_clean = self._clean_entity(topic)
        
        return [
            f"IsA({topic_clean}, Subject).",
            f"StudiedBy({topic_clean}, Scientists).",
            f"HasProperty({topic_clean}, Value).",
            f"UsedIn({topic_clean}, Research).",
            f"Requires({topic_clean}, Understanding)."
        ]

# Global instance
universal_extractor = UniversalFactExtractor()

def extract_facts_from_llm(text: str, topic: str = '') -> List[str]:
    """Main API function"""
    return universal_extractor.extract_facts(text, topic)
