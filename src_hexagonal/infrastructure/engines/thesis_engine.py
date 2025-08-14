#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HEXAGONAL Thesis Engine - Pattern Analysis and Knowledge Synthesis
==================================================================
Nach HAK/GAL Verfassung: Artikel 5 (System-Metareflexion)
Analyzes knowledge base to find patterns and generate meta-knowledge
"""

import sys
import os
import re
import time
import random
import argparse
from typing import List, Set, Dict, Any, Tuple
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infrastructure.engines.base_engine import BaseHexagonalEngine


class ThesisEngine(BaseHexagonalEngine):
    """
    Thesis Engine - Analyzes knowledge base patterns and generates meta-facts
    Optimized for large knowledge bases (6000+ facts)
    """
    
    def __init__(self, port: int = None, max_facts: int = 10000):
        super().__init__(name="Thesis", port=port)
        self.max_facts = max_facts
        
        # Analysis structures
        self.facts_by_predicate = defaultdict(list)
        self.facts_by_entity = defaultdict(list)
        self.entity_types = defaultdict(set)
        self.predicate_stats = defaultdict(int)
        
    def analyze_knowledge_base(self) -> bool:
        """
        Analyze the current knowledge base structure
        
        Returns:
            True if analysis successful
        """
        try:
            # Get all facts
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
        for entity in list(type_graph.keys())[:50]:
            direct_types = list(type_graph[entity])[:5]
            
            for dtype in direct_types:
                if dtype in type_graph:
                    # Get indirect types
                    indirect_types = list(type_graph[dtype])[:3]
                    
                    for itype in indirect_types:
                        if itype not in type_graph[entity] and itype != entity:
                            fact = f"IsA({entity}, {itype})."
                            facts.append(fact)
                            
                            if len(facts) >= 20:
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
        causes_facts = self.facts_by_predicate.get('Causes', [])[:50]
        
        if not causes_facts:
            return facts
        
        # Build causality graph
        causes_map = defaultdict(set)
        for subject, obj in causes_facts:
            if obj:
                causes_map[subject].add(obj)
        
        # Find causal chains
        for a in list(causes_map.keys())[:20]:
            for b in list(causes_map[a])[:5]:
                if b in causes_map:
                    for c in list(causes_map[b])[:3]:
                        if c not in causes_map[a] and c != a:
                            # Inferred causality
                            fact = f"MayCause({a}, {c})."
                            facts.append(fact)
                            
                            if len(facts) >= 15:
                                return facts
        
        return facts
    
    def find_symmetric_relationships(self) -> List[str]:
        """
        Find and complete symmetric relationships
        
        Returns:
            List of symmetric relationship facts
        """
        facts = []
        
        # Predicates that are typically symmetric
        symmetric_predicates = ['RelatesTo', 'ConnectsTo', 'SharesProperty', 
                               'SimilarTo', 'EquivalentTo', 'ParallelTo']
        
        for predicate in symmetric_predicates:
            if predicate not in self.facts_by_predicate:
                continue
            
            pairs = self.facts_by_predicate[predicate][:20]
            
            for subject, obj in pairs:
                if obj and subject != obj:
                    # Check if reverse exists
                    reverse = f"{predicate}({obj}, {subject})."
                    
                    # Only add if not already in KB
                    if reverse not in self.existing_facts:
                        facts.append(reverse)
                        
                        if len(facts) >= 10:
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
        
        # Generate meta-facts
        facts.extend([
            f"HasProperty(KnowledgeBase, FactCount{total_facts}).",
            f"HasProperty(KnowledgeBase, PredicateCount{total_predicates}).",
            f"HasProperty(KnowledgeBase, EntityCount{total_entities}).",
            f"GeneratedBy(KnowledgeBase, ThesisEngine).",
            f"LocatedAt(KnowledgeBase, HexagonalSystem)."
        ])
        
        # Top predicates
        top_predicates = sorted(self.predicate_stats.items(), 
                               key=lambda x: x[1], reverse=True)[:5]
        
        for pred, count in top_predicates:
            facts.append(f"HasFrequency({pred}, Count{count}).")
        
        # Well-connected entities
        well_connected = [(e, len(rels)) for e, rels in self.facts_by_entity.items()]
        well_connected.sort(key=lambda x: x[1], reverse=True)
        
        for entity, conn_count in well_connected[:5]:
            facts.append(f"HasConnections({entity}, Count{conn_count}).")
        
        return facts[:20]
    
    def find_missing_relationships(self) -> List[str]:
        """
        Identify potential missing relationships between entities
        
        Returns:
            List of potential relationship facts
        """
        facts = []
        
        # Find well-defined entities (with multiple relationships)
        well_defined = [e for e, rels in self.facts_by_entity.items() 
                       if 5 < len(rels) < 30][:20]
        
        # Look for potential connections
        for i, e1 in enumerate(well_defined):
            for e2 in well_defined[i+1:i+5]:  # Limit connections
                # Check if they're not already connected
                e1_connections = {rel[1] for rel in self.facts_by_entity[e1]}
                
                if e2 not in e1_connections:
                    # Check if they share common connections (indirect relationship)
                    e2_connections = {rel[1] for rel in self.facts_by_entity[e2]}
                    common = e1_connections & e2_connections
                    
                    if common:
                        facts.append(f"PotentiallyRelatedTo({e1}, {e2}).")
                        
                        if len(facts) >= 10:
                            return facts
        
        return facts
    
    def generate_facts(self) -> List[str]:
        """
        Generate new facts through knowledge base analysis
        
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
            
            # Missing relationships
            if len(self.existing_facts) < 5000:  # Only for smaller KBs
                missing_facts = self.find_missing_relationships()
                all_facts.extend(missing_facts)
                self.logger.info(f"Generated {len(missing_facts)} relationship facts")
                
        except Exception as e:
            self.logger.error(f"Error in fact generation: {e}")
        
        # Filter out existing facts
        new_facts = [f for f in all_facts if f not in self.existing_facts]
        
        # Remove duplicates and limit
        return list(set(new_facts))[:50]
    
    def run(self, duration_minutes: float = 15):
        """
        Run the Thesis engine for specified duration
        
        Args:
            duration_minutes: How long to run
        """
        self.logger.info(f"Starting Thesis Engine for {duration_minutes} minutes")
        self.logger.info(f"Using HEXAGONAL API on port {self.port}")
        self.logger.info(f"Max facts to analyze: {self.max_facts}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        facts_added = 0
        rounds = 0
        
        while time.time() < end_time:
            rounds += 1
            self.logger.info(f"\n=== Analysis Round {rounds} ===")
            
            # Generate thesis facts
            thesis_facts = self.generate_facts()
            self.logger.info(f"Generated {len(thesis_facts)} thesis facts")
            
            # Add facts to knowledge base
            if thesis_facts:
                # Add in smaller batches
                for i in range(0, len(thesis_facts), 10):
                    batch = thesis_facts[i:i+10]
                    added = self.add_facts_batch(batch)
                    facts_added += added
                    
                    if added > 0:
                        self.logger.info(f"Added {added} facts to knowledge base")
            
            # Progress report
            elapsed = (time.time() - start_time) / 60
            rate = facts_added / elapsed if elapsed > 0 else 0
            self.logger.info(f"Progress: {facts_added} facts, Rate: {rate:.1f} facts/min")
            
            # Pause between rounds (longer pause for analysis)
            if time.time() < end_time:
                time.sleep(15)
        
        # Final report
        total_time = (time.time() - start_time) / 60
        final_rate = facts_added / total_time if total_time > 0 else 0
        
        self.logger.info("=" * 60)
        self.logger.info("THESIS ENGINE COMPLETE")
        self.logger.info(f"Added: {facts_added} facts")
        self.logger.info(f"Time: {total_time:.1f} minutes")
        self.logger.info(f"Rate: {final_rate:.1f} facts/minute")
        self.logger.info(f"Analysis rounds: {rounds}")
        self.logger.info("=" * 60)


def main():
    """Main entry point for standalone execution"""
    parser = argparse.ArgumentParser(description="HEXAGONAL Thesis Engine")
    parser.add_argument("-d", "--duration", type=float, default=0.25,
                       help="Duration in hours (default: 0.25)")
    parser.add_argument("-p", "--port", type=int, default=5001,
                       help="API port (default: 5001)")
    parser.add_argument("--max-facts", type=int, default=10000,
                       help="Max facts to analyze (default: 10000)")
    args = parser.parse_args()
    
    # Create and run engine
    engine = ThesisEngine(port=args.port, max_facts=args.max_facts)
    engine.run(duration_minutes=args.duration * 60)


if __name__ == "__main__":
    main()
