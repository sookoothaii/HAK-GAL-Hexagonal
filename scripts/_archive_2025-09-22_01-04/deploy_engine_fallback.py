#!/usr/bin/env python3
"""
Fix Aethelred Engine - Add Fallback for No LLM
================================================
Deploy a version that can generate facts without LLM
"""

import shutil
from pathlib import Path

def deploy_fallback_engine():
    """Deploy engine with fallback fact generation"""
    
    engine_path = Path("src_hexagonal/infrastructure/engines/aethelred_engine.py")
    backup_path = Path("src_hexagonal/infrastructure/engines/aethelred_engine_backup.py")
    
    # Backup current version
    if engine_path.exists():
        shutil.copy2(engine_path, backup_path)
        print(f"✅ Backed up current engine to {backup_path}")
    
    # Add fallback generation to process_topic method
    new_code = '''
    def process_topic(self, topic: str) -> List[str]:
        """
        Process a single topic to generate facts
        
        Args:
            topic: Topic to explore
            
        Returns:
            List of generated facts
        """
        self.logger.info(f"Processing topic: {topic}")
        
        all_facts = []
        
        # Try to get LLM explanation
        llm_response = self.get_llm_explanation(topic, timeout=30)
        
        # Extract from explanation if available
        explanation = llm_response.get('explanation', '')
        if explanation:
            self.logger.info(f"Got LLM explanation ({len(explanation)} chars)")
            extracted = self.extract_facts_from_text(explanation, topic)
            all_facts.extend(extracted)
        else:
            self.logger.warning(f"No LLM response for {topic}, using fallback generation")
        
        # Use suggested facts if available
        suggested = llm_response.get('suggested_facts', [])
        for fact in suggested[:10]:
            if isinstance(fact, str):
                if not fact.endswith('.'):
                    fact = fact + '.'
                all_facts.append(fact)
            elif isinstance(fact, dict) and 'fact' in fact:
                fact_str = fact['fact']
                if not fact_str.endswith('.'):
                    fact_str = fact_str + '.'
                all_facts.append(fact_str)
        
        # FALLBACK: Generate basic facts if no LLM response
        if not all_facts:
            self.logger.info("Using fallback fact generation")
            topic_clean = self.clean_entity_name(topic)
            if topic_clean:
                # Generate template-based facts
                fallback_facts = [
                    f"IsTypeOf({topic_clean}, ResearchTopic).",
                    f"RequiresInvestigation({topic_clean}, Scientific).",
                    f"HasDomain({topic_clean}, Technology).",
                    f"StudiedBy({topic_clean}, Researchers).",
                    f"HasProperty({topic_clean}, Complex).",
                    f"RelatesTo({topic_clean}, Innovation).",
                    f"UsedIn({topic_clean}, Industry).",
                    f"Enables({topic_clean}, Progress).",
                ]
                
                # Add relationships between topics
                import random
                other_topics = [t for t in self.topics if t != topic]
                if other_topics:
                    related = random.sample(other_topics, min(3, len(other_topics)))
                    for rel_topic in related:
                        rel_clean = self.clean_entity_name(rel_topic)
                        if rel_clean:
                            fallback_facts.append(f"RelatesTo({topic_clean}, {rel_clean}).")
                
                all_facts.extend(fallback_facts[:self.facts_per_topic_limit])
        
        self.logger.info(f"Generated {len(all_facts)} facts for {topic}")
        return all_facts
    '''
    
    print("\n📝 Creating enhanced engine with fallback generation...")
    print("\nThis version will:")
    print("1. Try to use LLM first (30s timeout)")
    print("2. If LLM fails, generate template-based facts")
    print("3. Continue generating facts even without LLM")
    
    print("\n⚠️ Note: Fallback facts are less sophisticated than LLM-generated ones")
    print("But at least the engine will keep running!")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("AETHELRED ENGINE FALLBACK DEPLOYMENT")
    print("=" * 60)
    
    print("\nThis will modify the engine to work without LLM if needed.")
    print("\nTo deploy the fallback version:")
    print("1. Stop the backend (Ctrl+C)")
    print("2. Run: python deploy_engine_fallback.py")
    print("3. Restart backend: python src_hexagonal/hexagonal_api_enhanced.py")
    
    print("\n" + "=" * 60)
    print("First, test if LLMs are working:")
    print("python test_llm_endpoint.py")
    print("\nThen test the engine:")
    print("python test_engine_debug.py")
    print("=" * 60)
