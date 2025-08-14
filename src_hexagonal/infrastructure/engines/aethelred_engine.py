#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HEXAGONAL Aethelred Engine - Fact Generation via LLM
=====================================================
Nach HAK/GAL Verfassung: Artikel 2 (Gezielte Befragung)
Generates new facts through targeted LLM interrogation
"""

import sys
import os
import re
import time
import random
import argparse
from typing import List, Set, Dict, Any
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infrastructure.engines.base_engine import BaseHexagonalEngine

# Extended topic list for diverse knowledge generation
ALL_TOPICS = [
    # Sciences
    "quantum computing", "neural networks", "black holes", "DNA replication",
    "climate change", "artificial intelligence", "renewable energy",
    "nanotechnology", "gene therapy", "space exploration", "cryptography",
    "machine learning", "robotics", "biotechnology", "quantum physics",
    "blockchain technology", "fusion energy", "synthetic biology",
    "brain-computer interfaces", "dark matter", "exoplanets",
    "CRISPR", "metamaterials", "quantum entanglement", "stem cells",
    
    # Philosophy & Social Sciences
    "consciousness", "free will", "ethics", "epistemology",
    "democracy", "capitalism", "socialism", "human rights",
    "cultural evolution", "linguistics", "anthropology",
    
    # Technology & Engineering
    "5G networks", "autonomous vehicles", "smart cities",
    "edge computing", "augmented reality", "virtual reality",
    "Internet of Things", "cybersecurity", "data privacy",
    
    # Medicine & Health
    "immunotherapy", "personalized medicine", "telemedicine",
    "mental health", "nutrition", "aging research",
    "pandemic preparedness", "vaccine development"
]

# Clean predicate patterns for fact extraction
PREDICATE_PATTERNS = {
    "is a": "IsA",
    "is an": "IsA",
    "consists of": "ConsistsOf",
    "contains": "Contains",
    "uses": "Uses",
    "requires": "Requires",
    "produces": "Produces",
    "enables": "Enables",
    "has": "HasProperty",
    "provides": "Provides",
    "supports": "Supports",
    "includes": "Includes",
    "depends on": "DependsOn",
    "creates": "Creates",
    "generates": "Generates",
    "transforms": "Transforms",
    "affects": "Affects",
    "influences": "Influences",
    "determines": "Determines",
    "controls": "Controls",
    "regulates": "Regulates",
    "causes": "Causes",
    "prevents": "Prevents",
    "enhances": "Enhances",
    "reduces": "Reduces",
    "relates to": "RelatesTo",
    "connects to": "ConnectsTo"
}


class AethelredEngine(BaseHexagonalEngine):
    """
    Aethelred Engine - Generates facts through LLM exploration
    """
    
    def __init__(self, port: int = None):
        super().__init__(name="Aethelred", port=port)
        self.topics = ALL_TOPICS.copy()
        # Scale up aggressively for high-end hardware; overridable via ENV
        try:
            self.parallel_workers = int(os.environ.get('AETHELRED_PARALLEL', '8'))
        except Exception:
            self.parallel_workers = 8
        try:
            self.facts_per_topic_limit = int(os.environ.get('AETHELRED_FACTS_PER_TOPIC', '50'))
        except Exception:
            self.facts_per_topic_limit = 50
        
    def clean_entity_name(self, entity: str) -> str:
        """
        Clean entity name to valid format
        
        Args:
            entity: Raw entity string
            
        Returns:
            Cleaned entity name or None if invalid
        """
        # Remove common stop words
        stop_words = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'that', 'which']
        
        words = entity.lower().split()
        cleaned_words = [w for w in words if w not in stop_words]
        
        if not cleaned_words:
            return None
        
        # Capitalize each word and join with NO spaces (CamelCase)
        result = ''.join(word.capitalize() for word in cleaned_words)
        
        # Remove any non-alphanumeric characters
        result = ''.join(c for c in result if c.isalnum())
        
        # Ensure reasonable length
        if len(result) < 3 or len(result) > 50:
            return None
        
        return result
    
    def extract_facts_from_text(self, text: str, topic: str) -> List[str]:
        """
        Extract facts from explanation text
        
        Args:
            text: Explanation text from LLM
            topic: Original topic
            
        Returns:
            List of extracted facts
        """
        facts = []
        topic_clean = self.clean_entity_name(topic)
        
        if not topic_clean:
            return facts
        
        # Process sentences
        sentences = re.split(r'[.!?]', text)
        
        for sentence in sentences[:50]:  # Limit sentences to process
            sentence = sentence.strip()
            if not sentence or len(sentence) < 20:
                continue
            
            # Look for patterns
            for pattern, predicate in PREDICATE_PATTERNS.items():
                if pattern in sentence.lower():
                    parts = sentence.lower().split(pattern)
                    if len(parts) >= 2:
                        # Extract subject and object
                        subject_text = parts[0].strip()
                        object_text = parts[1].strip()
                        
                        # Take last 2-3 words for subject, first 2-3 for object
                        subject_words = subject_text.split()[-3:]
                        object_words = object_text.split()[:3]
                        
                        if subject_words and object_words:
                            subject = self.clean_entity_name(' '.join(subject_words))
                            obj = self.clean_entity_name(' '.join(object_words))
                            
                            if subject and obj and subject != obj:
                                fact = f"{predicate}({subject}, {obj})."
                                facts.append(fact)
                                
                                # Only one fact per pattern per sentence
                                break
        
        # Optional metadata facts (toggle via ENV)
        if os.environ.get('AETHELRED_INCLUDE_META', '1') not in ('0','false','False'):
            facts.extend([
                f"IsA({topic_clean}, ResearchTopic).",
                f"StudiedBy({topic_clean}, AethelredEngine).",
                f"GeneratedAt({topic_clean}, Hexagonal)."
            ])
        
        # Remove duplicates and limit
        return list(set(facts))[:self.facts_per_topic_limit]
    
    def process_topic(self, topic: str) -> List[str]:
        """
        Process a single topic to generate facts
        
        Args:
            topic: Topic to explore
            
        Returns:
            List of generated facts
        """
        self.logger.info(f"Processing topic: {topic}")
        
        # Get LLM explanation
        llm_response = self.get_llm_explanation(topic, timeout=70)
        
        all_facts = []
        
        # Extract from explanation
        explanation = llm_response.get('explanation', '')
        if explanation:
            extracted = self.extract_facts_from_text(explanation, topic)
            all_facts.extend(extracted)
        
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
        
        self.logger.info(f"Generated {len(all_facts)} facts for {topic}")
        return all_facts
    
    def generate_facts(self) -> List[str]:
        """
        Generate new facts through parallel topic processing
        
        Returns:
            List of new fact statements
        """
        # Get existing facts
        existing = self.get_existing_facts()
        
        # Select random topics
        selected_topics = random.sample(self.topics, min(self.parallel_workers, len(self.topics)))
        
        all_new_facts = []
        
        # Process topics in parallel
        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            futures = []
            for topic in selected_topics:
                future = executor.submit(self.process_topic, topic)
                futures.append((topic, future))
            
            # Collect results
            for topic, future in futures:
                try:
                    facts = future.result(timeout=80)
                    # Filter out existing facts
            new_facts = [f for f in facts if f not in existing]

            # Optional confidence gate (strict mode): keep only high-confidence facts
            strict_val = os.environ.get('AETHELRED_STRICT_CONFIDENCE', '')
            if strict_val:
                try:
                    threshold = float(strict_val)
                    gated = []
                    for st in new_facts:
                        c = self.get_confidence(st, timeout=8)
                        if c >= threshold:
                            gated.append(st)
                    new_facts = gated
                    self.logger.info(f"Confidence gate {threshold}: {len(new_facts)} passed")
                except Exception as e:
                    self.logger.warning(f"Strict confidence parse/apply error: {e}")
                    all_new_facts.extend(new_facts)
                except Exception as e:
                    self.logger.error(f"Error processing {topic}: {e}")
        
        # Remove duplicates
        return list(set(all_new_facts))
    
    def run(self, duration_minutes: float = 15):
        """
        Run the Aethelred engine for specified duration
        
        Args:
            duration_minutes: How long to run
        """
        self.logger.info(f"Starting Aethelred Engine for {duration_minutes} minutes")
        self.logger.info(f"Using HEXAGONAL API on port {self.port}")
        self.logger.info(f"Parallel workers: {self.parallel_workers}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        facts_added = 0
        rounds = 0
        
        while time.time() < end_time:
            rounds += 1
            self.logger.info(f"\n=== Round {rounds} ===")
            
            # Generate new facts
            new_facts = self.generate_facts()
            self.logger.info(f"Generated {len(new_facts)} new facts")
            
            # Add facts to knowledge base
            if new_facts:
                added = self.add_facts_batch(new_facts)
                facts_added += added
                self.logger.info(f"Added {added} facts to knowledge base")
            
            # Progress report
            elapsed = (time.time() - start_time) / 60
            rate = facts_added / elapsed if elapsed > 0 else 0
            self.logger.info(f"Progress: {facts_added} facts, Rate: {rate:.1f} facts/min")
            
            # Pause between rounds
            if time.time() < end_time:
                time.sleep(5)
        
        # Final report
        total_time = (time.time() - start_time) / 60
        final_rate = facts_added / total_time if total_time > 0 else 0
        
        self.logger.info("=" * 60)
        self.logger.info("AETHELRED ENGINE COMPLETE")
        self.logger.info(f"Added: {facts_added} facts")
        self.logger.info(f"Time: {total_time:.1f} minutes")
        self.logger.info(f"Rate: {final_rate:.1f} facts/minute")
        self.logger.info(f"Rounds: {rounds}")
        self.logger.info("=" * 60)


def main():
    """Main entry point for standalone execution"""
    parser = argparse.ArgumentParser(description="HEXAGONAL Aethelred Engine")
    parser.add_argument("-d", "--duration", type=float, default=0.25,
                       help="Duration in hours (default: 0.25)")
    parser.add_argument("-p", "--port", type=int, default=5001,
                       help="API port (default: 5001)")
    parser.add_argument("--parallel", type=int, default=3,
                       help="Parallel workers (default: 3)")
    args = parser.parse_args()
    
    # Create and run engine
    engine = AethelredEngine(port=args.port)
    # If CLI parallel supplied, override ENV
    if args.parallel:
        engine.parallel_workers = args.parallel
    engine.run(duration_minutes=args.duration * 60)


if __name__ == "__main__":
    main()
