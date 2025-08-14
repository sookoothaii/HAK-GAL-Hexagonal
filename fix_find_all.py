#!/usr/bin/env python3
"""
Quick Fix for find_all() returning 0 facts
Nach HAK/GAL Verfassung Artikel 4: Bewusstes Grenzüberschreiten
"""

def analyze_find_all_problem():
    """
    Problem: find_all() returns 0 facts despite count() returning 3080
    
    Ursache in legacy_adapters.py:
    - legacy.get_facts() wird aufgerufen
    - Möglicherweise gibt get_facts() leere Liste zurück
    
    Fix-Vorschlag:
    """
    
    fix = '''
    def find_all(self, limit: int = 100) -> List[Fact]:
        """Hole alle Facts vom Legacy System - FIXED VERSION"""
        try:
            # Option 1: Try direct access to K
            if (self.legacy.k_assistant and 
                hasattr(self.legacy.k_assistant, 'core') and 
                hasattr(self.legacy.k_assistant.core, 'K')):
                
                raw_facts = list(self.legacy.k_assistant.core.K)[:limit]
                facts = []
                for fact_obj in raw_facts:
                    # Handle both string facts and fact objects
                    if isinstance(fact_obj, str):
                        fact_str = fact_obj
                    elif hasattr(fact_obj, 'statement'):
                        fact_str = fact_obj.statement
                    else:
                        continue
                    
                    facts.append(Fact(
                        statement=fact_str,
                        confidence=1.0,
                        context={'source': 'legacy'},
                        created_at=datetime.now()
                    ))
                return facts
            
            # Option 2: Fallback to get_facts
            raw_facts = self.legacy.get_facts(limit)
            if raw_facts:
                facts = []
                for fact_str in raw_facts:
                    if isinstance(fact_str, str):
                        facts.append(Fact(
                            statement=fact_str,
                            confidence=1.0,
                            context={'source': 'legacy'},
                            created_at=datetime.now()
                        ))
                return facts
                
        except Exception as e:
            print(f"Error getting all facts: {e}")
        
        return []
    '''
    
    return fix

if __name__ == "__main__":
    print("FIX für find_all() Method:")
    print("=" * 60)
    print(analyze_find_all_problem())
    print("=" * 60)
    print("\nImplementiere in: src_hexagonal/adapters/legacy_adapters.py")
    print("Ersetze die find_all() Methode mit der obigen Version")
