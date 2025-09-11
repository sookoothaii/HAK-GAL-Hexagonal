#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GOVERNED Thesis Engine - Pattern Analysis with Governance
=========================================================
Nach HAK/GAL Verfassung: Artikel 5 (System-Metareflexion) + Governance v2.2
Analyzes knowledge base to find patterns with strict governance checks
"""

import sys
import os
import re
import time
import random
import argparse
import logging
from typing import List, Set, Dict, Any, Tuple
from collections import defaultdict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infrastructure.engines.base_engine import BaseHexagonalEngine
from application.transactional_governance_engine import (
    TransactionalGovernanceEngine,
    GovernancePerformanceMonitor
)

logger = logging.getLogger(__name__)


class GovernedThesisEngine(BaseHexagonalEngine):
    """
    Governed Thesis Engine - Analyzes knowledge base patterns with governance
    Optimized for large knowledge bases with governance compliance
    """
    
    def __init__(self, port: int = None, max_facts: int = 10000):
        super().__init__(name="GovernedThesis", port=port)
        self.max_facts = max_facts
        
        # Initialize governance
        self.governance_engine = TransactionalGovernanceEngine()
        self.performance_monitor = GovernancePerformanceMonitor(self.governance_engine)
        
        # Analysis structures
        self.facts_by_predicate = defaultdict(list)
        self.facts_by_entity = defaultdict(list)
        self.entity_types = defaultdict(set)
        self.predicate_stats = defaultdict(int)
        
        # Governance batch limits
        self.max_batch_size = 30  # Conservative for meta-facts
        
        logger.info(f"GovernedThesisEngine initialized with governance")
        logger.info(f"Max facts to analyze: {self.max_facts}")
        logger.info(f"Max batch size: {self.max_batch_size}")
    
    def analyze_knowledge_base(self) -> bool:
        """
        Analyze the current knowledge base structure
        
        Returns:
            True if analysis successful
        """
        try:
            # Get all facts from facts_extended
            existing = self.get_existing_facts(force_refresh=True)
            
            if not existing:
                self.logger.warning("No facts in knowledge base")
                return False
            
            self.logger.info(f"Analyzing {len(existing)} facts...")
            
            # Clear previous analysis
            self.facts_by_predicate.clear()
            self.facts_by_entity.clear()
            self.entity_types.clear()
            self.predicate_stats.clear()
            
            # Analyze facts (limited to max_facts)
            facts_to_analyze = list(existing)[:self.max_facts]
            
            for fact in facts_to_analyze:
                self._analyze_single_fact(fact)
            
            self.logger.info(f"Analysis complete:")
            self.logger.info(f"  - {len(self.facts_by_predicate)} unique predicates")
            self.logger.info(f"  - {len(self.facts_by_entity)} unique entities")
            self.logger.info(f"  - Top predicates: {list(self.predicate_stats.keys())[:5]}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error analyzing knowledge base: {e}")
            return False
    
    def _analyze_single_fact(self, fact: str):
        """
        Analyze a single fact statement
        
        Args:
            fact: Fact statement to analyze
        """
        try:
            # Match fact pattern: Predicate(Entity1, Entity2).
            match = re.match(r'^([A-Za-z0-9_]+)\(([^,)]+)(?:,\s*([^)]+))?\)\.$', fact)
            
            if not match:
                return
            
            predicate = match.group(1)
            subject = match.group(2).strip() if match.group(2) else ""
            obj = match.group(3).strip() if match.group(3) else ""
            
            # Validate entities
            if not self._is_valid_entity(subject):
                return
            
            if obj and not self._is_valid_entity(obj):
                return
            
            # Store analysis (with limits to prevent memory issues)
            self.predicate_stats[predicate] += 1
            
            if len(self.facts_by_predicate[predicate]) < 100:
                self.facts_by_predicate[predicate].append((subject, obj))
            
            if len(self.facts_by_entity[subject]) < 50:
                self.facts_by_entity[subject].append((predicate, obj, 'subject'))
            
            if obj and len(self.facts_by_entity[obj]) < 50:
                self.facts_by_entity[obj].append((predicate, subject, 'object'))
            
            # Track type hierarchies
            if predicate == 'IsA':
                self.entity_types[subject].add(obj)
                
        except Exception as e:
            self.logger.debug(f"Could not analyze fact: {fact} - {e}")
    
    def _is_valid_entity(self, entity: str) -> bool:
        """
        Check if entity name is valid
        
        Args:
            entity: Entity name to validate
            
        Returns:
            True if valid
        """
        if not entity or len(entity) < 2 or len(entity) > 100:
            return False
        
        # Check for invalid patterns
        if entity.isdigit():
            return False
        
        invalid_names = ['', 'nd', 'Which', 'ButIt', 'True', 'False', 
                        'None', 'Null', 'undefined', 'unknown']
        if entity in invalid_names:
            return False
        
        # Should not start with number
        if entity and entity[0].isdigit():
            return False
        
        return True
    
    def find_type_hierarchies(self) -> List[str]:
        """
        Find and complete type hierarchies through transitivity
        
        Returns:
            List of inferred type facts
        """
        facts = []
        
        # Get IsA relationships
        isa_facts = self.facts_by_predicate.get('IsA', [])[:100]
        
        # Build type graph
        type_graph = defaultdict(set)
        for subject, obj in isa_facts:
            if obj:
                type_graph[subject].add(obj)
        
        # Find transitive relationships
        for entity in list(type_graph.keys())[:30]:  # Reduced for governance
            direct_types = list(type_graph[entity])[:3]
            
            for dtype in direct_types:
                if dtype in type_graph:
                    # Get indirect types
                    indirect_types = list(type_graph[dtype])[:2]
                    
                    for itype in indirect_types:
                        if itype not in type_graph[entity] and itype != entity:
                            fact = f"IsA({entity}, {itype})."
                            facts.append(fact)
                            
                            if len(facts) >= 15:
                                return facts
        
        return facts
    
    def find_causal_patterns(self) -> List[str]:
        """
        Find causal chains and patterns
        
        Returns:
            List of inferred causal facts
        """
        facts = []
        
        # Analyze Causes relationships
        causes_facts = self.facts_by_predicate.get('Causes', [])[:30]
        
        if not causes_facts:
            return facts
        
        # Build causality graph
        causes_map = defaultdict(set)
        for subject, obj in causes_facts:
            if obj:
                causes_map[subject].add(obj)
        
        # Find causal chains
        for a in list(causes_map.keys())[:15]:
            for b in list(causes_map[a])[:3]:
                if b in causes_map:
                    for c in list(causes_map[b])[:2]:
                        if c not in causes_map[a] and c != a:
                            # Inferred causality (using conservative predicate)
                            fact = f"Causes({a}, {c})."
                            facts.append(fact)
                            
                            if len(facts) >= 10:
                                return facts
        
        return facts
    
    def find_symmetric_relationships(self) -> List[str]:
        """
        Find and complete symmetric relationships
        
        Returns:
            List of symmetric relationship facts
        """
        facts = []
        
        # Predicates that are typically symmetric (using only whitelisted)
        symmetric_predicates = ['IsSimilarTo']
        
        for predicate in symmetric_predicates:
            if predicate not in self.facts_by_predicate:
                continue
            
            pairs = self.facts_by_predicate[predicate][:15]
            
            for subject, obj in pairs:
                if obj and subject != obj:
                    # Check if reverse exists
                    reverse = f"{predicate}({obj}, {subject})."
                    
                    # Only add if not already in KB
                    if reverse not in self.existing_facts:
                        facts.append(reverse)
                        
                        if len(facts) >= 8:
                            return facts
        
        return facts
    
    def generate_meta_facts(self) -> List[str]:
        """
        Generate meta-facts about the knowledge base itself
        
        Returns:
            List of meta-facts
        """
        facts = []
        
        # Knowledge base statistics
        total_facts = len(self.existing_facts)
        total_predicates = len(self.facts_by_predicate)
        total_entities = len(self.facts_by_entity)
        
        # Generate meta-facts (using whitelisted predicates)
        facts.extend([
            f"HasProperty(KnowledgeBase, FactCount{total_facts}).",
            f"HasProperty(KnowledgeBase, PredicateCount{total_predicates}).",
            f"HasProperty(KnowledgeBase, EntityCount{total_entities}).",
            f"GeneratedBy(KnowledgeBase, GovernedThesisEngine).",
            f"LocatedAt(KnowledgeBase, HexagonalSystem)."
        ])
        
        return facts[:10]
    
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
                
                self.logger.info(f"Added {added}/{len(batch)} meta-facts with governance")
                
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
        Generate new facts through knowledge base analysis with governance
        
        Returns:
            List of new fact statements
        """
        all_facts = []
        
        # Analyze current knowledge base
        if not self.analyze_knowledge_base():
            self.logger.warning("KB analysis failed, skipping fact generation")
            return []
        
        # Run different analysis methods
        try:
            # Type hierarchy completion
            type_facts = self.find_type_hierarchies()
            all_facts.extend(type_facts)
            self.logger.info(f"Generated {len(type_facts)} type hierarchy facts")
            
            # Causal pattern analysis
            causal_facts = self.find_causal_patterns()
            all_facts.extend(causal_facts)
            self.logger.info(f"Generated {len(causal_facts)} causal pattern facts")
            
            # Symmetric relationships
            symmetric_facts = self.find_symmetric_relationships()
            all_facts.extend(symmetric_facts)
            self.logger.info(f"Generated {len(symmetric_facts)} symmetric facts")
            
            # Meta-facts about KB
            meta_facts = self.generate_meta_facts()
            all_facts.extend(meta_facts)
            self.logger.info(f"Generated {len(meta_facts)} meta-facts")
                
        except Exception as e:
            self.logger.error(f"Error in fact generation: {e}")
        
        # Filter out existing facts
        new_facts = [f for f in all_facts if f not in self.existing_facts]
        
        # Remove duplicates and limit
        return list(set(new_facts))[:self.max_batch_size]
    
    def run(self, duration_minutes: float = 15):
        """
        Run the Governed Thesis engine for specified duration
        
        Args:
            duration_minutes: How long to run
        """
        self.logger.info(f"Starting Governed Thesis Engine for {duration_minutes} minutes")
        self.logger.info(f"Using HEXAGONAL API on port {self.api_port}")
        self.logger.info(f"Governance: ENABLED with TransactionalGovernanceEngine")
        self.logger.info(f"Max facts to analyze: {self.max_facts}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        facts_added = 0
        rounds = 0
        governance_denials = 0
        
        while time.time() < end_time:
            rounds += 1
            self.logger.info(f"\n=== Analysis Round {rounds} ===")
            
            # Generate thesis facts
            thesis_facts = self.generate_facts()
            self.logger.info(f"Generated {len(thesis_facts)} thesis facts")
            
            # Add facts with governance
            if thesis_facts:
                # Create governance context for meta-analysis
                context = {
                    'engine': 'GovernedThesis',
                    'round': rounds,
                    'meta_analysis': True,
                    'harm_prob': 0.00001,  # Very low harm for meta-facts
                    'sustain_index': 0.99,  # Very high sustainability
                    'externally_legal': True,
                    'operator': 'thesis_engine',
                    'reason': f'Meta-knowledge synthesis round {rounds}',
                    'fact_type': 'meta_knowledge'
                }
                
                added = self.add_facts_with_governance(thesis_facts, context)
                facts_added += added
                
                if added < len(thesis_facts):
                    governance_denials += (len(thesis_facts) - added)
                    self.logger.warning(f"Governance denied {len(thesis_facts) - added} facts")
            
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
            
            # Pause between rounds (longer for analysis)
            if time.time() < end_time:
                time.sleep(15)
        
        # Final report
        total_time = (time.time() - start_time) / 60
        final_rate = facts_added / total_time if total_time > 0 else 0
        
        self.logger.info("=" * 60)
        self.logger.info("GOVERNED THESIS ENGINE COMPLETE")
        self.logger.info(f"Added: {facts_added} facts")
        self.logger.info(f"Denied by governance: {governance_denials} facts")
        self.logger.info(f"Time: {total_time:.1f} minutes")
        self.logger.info(f"Rate: {final_rate:.1f} facts/minute")
        self.logger.info(f"Analysis rounds: {rounds}")
        
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
    parser = argparse.ArgumentParser(description="Governed HEXAGONAL Thesis Engine")
    parser.add_argument("-d", "--duration", type=float, default=0.25,
                       help="Duration in hours (default: 0.25)")
    parser.add_argument("-p", "--port", type=int, default=5001,
                       help="API port (default: 5001)")
    parser.add_argument("--max-facts", type=int, default=10000,
                       help="Max facts to analyze (default: 10000)")
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run engine
    engine = GovernedThesisEngine(port=args.port, max_facts=args.max_facts)
    engine.run(duration_minutes=args.duration * 60)


if __name__ == "__main__":
    main()
