#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GOVERNED Aethelred Engine - Fact Generation with Governance
===========================================================
Nach HAK/GAL Verfassung: Artikel 2 (Gezielte Befragung) + Governance v2.2
Generates new facts through targeted LLM interrogation with strict governance
"""

import sys
import os
import re
import time
import random
import argparse
import logging
from typing import List, Set, Dict, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infrastructure.engines.base_engine import BaseHexagonalEngine
from application.transactional_governance_engine import (
    TransactionalGovernanceEngine,
    GovernancePerformanceMonitor
)

logger = logging.getLogger(__name__)

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
    "uses": "Uses",
    "requires": "Requires",
    "has": "HasProperty",
    "depends on": "DependsOn",
    "causes": "Causes",
    "reduces": "Reduces",
    "relates to": "RelatesTo"
}


class GovernedAethelredEngine(BaseHexagonalEngine):
    """
    Governed Aethelred Engine - Generates facts through LLM exploration with governance
    """
    
    def __init__(self, port: int = None):
        super().__init__(name="GovernedAethelred", port=port)
        self.topics = ALL_TOPICS.copy()
        
        # Initialize governance
        self.governance_engine = TransactionalGovernanceEngine()
        self.performance_monitor = GovernancePerformanceMonitor(self.governance_engine)
        
        # Configuration from environment
        try:
            self.facts_per_topic_limit = int(os.environ.get('AETHELRED_FACTS_PER_TOPIC', '30'))
        except Exception:
            self.facts_per_topic_limit = 30
        
        # Governance batch limits
        self.max_batch_size = 50  # Half of governance limit for safety
        
        logger.info(f"GovernedAethelredEngine initialized with governance")
        logger.info(f"Max batch size: {self.max_batch_size}")
    
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
        Extract facts from explanation text with governance validation
        
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
        
        for sentence in sentences[:30]:  # Reduced limit for governance
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
        
        # Optional metadata facts
        if os.environ.get('AETHELRED_INCLUDE_META', '1') not in ('0','false','False'):
            facts.extend([
                f"IsA({topic_clean}, ResearchTopic).",
                f"StudiedBy({topic_clean}, GovernedAethelredEngine).",
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
        llm_response = self.get_llm_explanation(topic, timeout=30)
        
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
    
    def add_facts_with_governance(self, facts: List[str], context: Dict[str, Any]) -> int:
        """
        Add facts with governance checks using TransactionalGovernanceEngine
        
        Args:
            facts: List of facts to add
            context: Governance context
            
        Returns:
            Number of facts added
        """
        if not facts:
            return 0
        
        # Respect batch limits
        total_added = 0
        
        for i in range(0, len(facts), self.max_batch_size):
            batch = facts[i:i+self.max_batch_size]
            
            try:
                # Use governance engine for atomic add
                added = self.performance_monitor.monitored_add_facts(batch, context)
                total_added += added
                
                self.logger.info(f"Added {added}/{len(batch)} facts with governance")
                
                # Check performance metrics
                metrics = self.performance_monitor.get_metrics()
                if metrics['slo_violations'] > 0:
                    self.logger.warning(f"SLO violations detected: {metrics['slo_violations']}")
                
            except Exception as e:
                self.logger.error(f"Governance check failed: {e}")
                # Continue with next batch
        
        return total_added
    
    def generate_facts(self) -> List[str]:
        """
        Generate new facts through topic processing with governance
        
        Returns:
            List of new fact statements
        """
        # Get existing facts from facts_extended
        existing = self.get_existing_facts()
        
        # Select only 1-2 topics per round for better performance
        num_topics = min(2, len(self.topics))
        selected_topics = random.sample(self.topics, num_topics)
        
        all_new_facts = []
        
        # Process topics sequentially
        for topic in selected_topics:
            self.logger.info(f"Processing topic: {topic}")
            try:
                facts = self.process_topic(topic)
                # Filter out existing facts
                new_facts = [f for f in facts if f not in existing]
                all_new_facts.extend(new_facts)
                self.logger.info(f"Generated {len(new_facts)} new facts for {topic}")
                
            except Exception as e:
                self.logger.error(f"Error processing {topic}: {e}")
        
        # Remove duplicates
        return list(set(all_new_facts))
    
    def run(self, duration_minutes: float = 15):
        """
        Run the Governed Aethelred engine for specified duration
        
        Args:
            duration_minutes: How long to run
        """
        self.logger.info(f"Starting Governed Aethelred Engine for {duration_minutes} minutes")
        self.logger.info(f"Using HEXAGONAL API on port {self.api_port}")
        self.logger.info(f"Governance: ENABLED with TransactionalGovernanceEngine")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        facts_added = 0
        rounds = 0
        governance_denials = 0
        
        while time.time() < end_time:
            rounds += 1
            self.logger.info(f"\n=== Round {rounds} ===")
            
            # Generate new facts
            new_facts = self.generate_facts()
            self.logger.info(f"Generated {len(new_facts)} new facts")
            
            # Add facts with governance
            if new_facts:
                # Create governance context
                context = {
                    'engine': 'GovernedAethelred',
                    'round': rounds,
                    'topic_generation': True,
                    'harm_prob': 0.0001,  # Low harm for knowledge generation
                    'sustain_index': 0.95,  # High sustainability
                    'externally_legal': True,
                    'operator': 'aethelred_engine',
                    'reason': f'Knowledge generation round {rounds}'
                }
                
                added = self.add_facts_with_governance(new_facts, context)
                facts_added += added
                
                if added < len(new_facts):
                    governance_denials += (len(new_facts) - added)
                    self.logger.warning(f"Governance denied {len(new_facts) - added} facts")
            
            # Progress report
            elapsed = (time.time() - start_time) / 60
            rate = facts_added / elapsed if elapsed > 0 else 0
            self.logger.info(f"Progress: {facts_added} facts, Rate: {rate:.1f} facts/min")
            self.logger.info(f"Governance denials: {governance_denials}")
            
            # Get performance metrics
            metrics = self.performance_monitor.get_metrics()
            self.logger.info(f"Governance metrics: {metrics['successful_commits']} commits, "
                           f"{metrics['failed_transactions']} failures, "
                           f"Avg latency: {metrics['avg_latency_ms']:.2f}ms")
            
            # Pause between rounds
            if time.time() < end_time:
                time.sleep(5)
        
        # Final report
        total_time = (time.time() - start_time) / 60
        final_rate = facts_added / total_time if total_time > 0 else 0
        
        self.logger.info("=" * 60)
        self.logger.info("GOVERNED AETHELRED ENGINE COMPLETE")
        self.logger.info(f"Added: {facts_added} facts")
        self.logger.info(f"Denied by governance: {governance_denials} facts")
        self.logger.info(f"Time: {total_time:.1f} minutes")
        self.logger.info(f"Rate: {final_rate:.1f} facts/minute")
        self.logger.info(f"Rounds: {rounds}")
        
        # Final governance metrics
        final_metrics = self.performance_monitor.get_metrics()
        self.logger.info(f"Final governance stats:")
        self.logger.info(f"  - Total requests: {final_metrics['total_requests']}")
        self.logger.info(f"  - Successful commits: {final_metrics['successful_commits']}")
        self.logger.info(f"  - Failed transactions: {final_metrics['failed_transactions']}")
        self.logger.info(f"  - Avg latency: {final_metrics['avg_latency_ms']:.2f}ms")
        self.logger.info(f"  - Max latency: {final_metrics['max_latency_ms']:.2f}ms")
        self.logger.info(f"  - SLO violations: {final_metrics['slo_violations']}")
        self.logger.info("=" * 60)


def main():
    """Main entry point for standalone execution"""
    parser = argparse.ArgumentParser(description="Governed HEXAGONAL Aethelred Engine")
    parser.add_argument("-d", "--duration", type=float, default=0.25,
                       help="Duration in hours (default: 0.25)")
    parser.add_argument("-p", "--port", type=int, default=5001,
                       help="API port (default: 5001)")
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run engine
    engine = GovernedAethelredEngine(port=args.port)
    engine.run(duration_minutes=args.duration * 60)


if __name__ == "__main__":
    main()
