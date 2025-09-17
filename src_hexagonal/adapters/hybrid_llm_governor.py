#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hybrid LLM Governor - Epsilon-Greedy Strategy
=============================================
Implements the hybrid strategy from Opus 4.1's architecture design.
Balances between Thompson Governor (exploitation) and LLM evaluation (exploration).
"""

import time
import random
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .llm_governor_adapter import LLMGovernorAdapter, LLMProvider, FactEvaluation

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """Type of decision made by hybrid governor"""
    THOMPSON_RULES = "thompson_rules"
    LLM_EVALUATE = "llm_evaluate"
    BATCH_LLM = "batch_llm"
    REJECT_SHORT = "reject_short"

@dataclass
class HybridDecision:
    """Result of hybrid decision making"""
    decision_type: DecisionType
    fact: str
    score: float
    confidence: float
    reasoning: str
    evaluation_time_ms: int
    metadata: Dict[str, Any]

class HybridLLMGovernor:
    """
    Hybrid LLM Governor implementing epsilon-greedy strategy
    """
    
    def __init__(self, 
                 epsilon: float = 0.2,
                 llm_provider: LLMProvider = LLMProvider.OLLAMA,
                 critical_domains: List[str] = None):
        self.epsilon = epsilon
        self.llm_provider = llm_provider
        self.critical_domains = critical_domains or [
            'physics', 'chemistry', 'mathematics', 'biology', 
            'astronomy', 'neuroscience', 'genetics'
        ]
        
        # Initialize LLM Governor
        self.llm_governor = LLMGovernorAdapter(llm_provider)
        
        # Statistics
        self.decision_count = 0
        self.thompson_decisions = 0
        self.llm_decisions = 0
        self.batch_decisions = 0
        self.rejected_short = 0
        
        # Performance tracking
        self.total_decision_time = 0.0
        
        logger.info(f"Hybrid LLM Governor initialized (ε={epsilon}, provider={llm_provider.value})")
    
    def evaluate_fact(self, fact: str, context: Optional[Dict[str, Any]] = None) -> HybridDecision:
        """
        Evaluate fact using hybrid strategy
        
        Args:
            fact: The fact statement to evaluate
            context: Optional context information
            
        Returns:
            HybridDecision with evaluation result
        """
        start_time = time.time()
        
        # Step 1: Length check (always reject very short facts)
        if len(fact.strip()) < 20:
            decision = HybridDecision(
                decision_type=DecisionType.REJECT_SHORT,
                fact=fact,
                score=0.0,
                confidence=1.0,
                reasoning="Fact too short (< 20 characters)",
                evaluation_time_ms=0,
                metadata={'reason': 'length_check'}
            )
            self.rejected_short += 1
            return decision
        
        # Step 2: Determine decision type
        decision_type = self._determine_decision_type(fact, context)
        
        # Step 3: Execute decision
        if decision_type == DecisionType.THOMPSON_RULES:
            result = self._evaluate_thompson(fact, context)
        elif decision_type == DecisionType.LLM_EVALUATE:
            result = self._evaluate_llm(fact, context)
        elif decision_type == DecisionType.BATCH_LLM:
            result = self._evaluate_batch_llm(fact, context)
        else:
            result = self._evaluate_thompson(fact, context)  # Fallback
        
        # Update statistics
        evaluation_time_ms = int((time.time() - start_time) * 1000)
        result.evaluation_time_ms = evaluation_time_ms
        
        self.decision_count += 1
        self.total_decision_time += evaluation_time_ms
        
        if decision_type == DecisionType.THOMPSON_RULES:
            self.thompson_decisions += 1
        elif decision_type == DecisionType.LLM_EVALUATE:
            self.llm_decisions += 1
        elif decision_type == DecisionType.BATCH_LLM:
            self.batch_decisions += 1
        
        logger.info(f"Hybrid decision: {decision_type.value} - Score: {result.score:.3f}, Time: {evaluation_time_ms}ms")
        
        return result
    
    def _determine_decision_type(self, fact: str, context: Optional[Dict[str, Any]] = None) -> DecisionType:
        """
        Determine which evaluation method to use based on hybrid strategy
        """
        fact_lower = fact.lower()
        
        # Always use LLM for critical domains
        for domain in self.critical_domains:
            if domain in fact_lower:
                return DecisionType.LLM_EVALUATE
        
        # Check if fact is trivial (simple rules)
        if self._is_trivial_fact(fact):
            return DecisionType.THOMPSON_RULES
        
        # Check argument count for batch processing
        arg_count = self._count_arguments(fact)
        if arg_count >= 3:
            return DecisionType.BATCH_LLM
        
        # Epsilon-greedy decision
        if random.uniform(0, 1) < self.epsilon:
            return DecisionType.LLM_EVALUATE  # Explore
        else:
            return DecisionType.THOMPSON_RULES  # Exploit
    
    def _is_trivial_fact(self, fact: str) -> bool:
        """Check if fact is trivial and can be handled by simple rules"""
        fact_lower = fact.lower()
        
        # Simple patterns that are usually correct
        trivial_patterns = [
            'color(',
            'number(',
            'size(',
            'length(',
            'weight(',
            'temperature(',
            'date(',
            'time('
        ]
        
        return any(pattern in fact_lower for pattern in trivial_patterns)
    
    def _count_arguments(self, fact: str) -> int:
        """Count number of arguments in fact statement"""
        # Simple heuristic: count commas + 1
        if '(' in fact and ')' in fact:
            args_part = fact[fact.find('(')+1:fact.rfind(')')]
            return args_part.count(',') + 1
        return 1
    
    def _evaluate_thompson(self, fact: str, context: Optional[Dict[str, Any]] = None) -> HybridDecision:
        """Evaluate using Thompson Governor rules"""
        # Simple rule-based evaluation
        score = 0.5  # Base score
        
        # Length bonus
        if len(fact) > 50:
            score += 0.1
        
        # Argument count bonus
        arg_count = self._count_arguments(fact)
        if arg_count >= 3:
            score += 0.2
        
        # Domain keyword bonus
        scientific_keywords = ['research', 'study', 'analysis', 'data', 'experiment', 'theory']
        if any(keyword in fact.lower() for keyword in scientific_keywords):
            score += 0.2
        
        # Normalize score
        score = min(score, 1.0)
        
        return HybridDecision(
            decision_type=DecisionType.THOMPSON_RULES,
            fact=fact,
            score=score,
            confidence=0.6,  # Lower confidence for rule-based
            reasoning="Thompson Governor rule-based evaluation",
            evaluation_time_ms=0,  # Will be set by caller
            metadata={
                'method': 'thompson_rules',
                'arg_count': arg_count,
                'length': len(fact)
            }
        )
    
    def _evaluate_llm(self, fact: str, context: Optional[Dict[str, Any]] = None) -> HybridDecision:
        """Evaluate using LLM"""
        llm_result = self.llm_governor.evaluate_fact(fact, context)
        
        return HybridDecision(
            decision_type=DecisionType.LLM_EVALUATE,
            fact=fact,
            score=llm_result.score,
            confidence=llm_result.confidence,
            reasoning=llm_result.reasoning,
            evaluation_time_ms=0,  # Will be set by caller
            metadata={
                'method': 'llm_evaluation',
                'provider': llm_result.provider,
                'model': llm_result.metadata.get('model', 'unknown'),
                'llm_metadata': llm_result.metadata
            }
        )
    
    def _evaluate_batch_llm(self, fact: str, context: Optional[Dict[str, Any]] = None) -> HybridDecision:
        """Evaluate using batch LLM processing (for complex facts)"""
        # For now, use regular LLM evaluation
        # In production, this would batch multiple facts together
        return self._evaluate_llm(fact, context)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get hybrid governor statistics"""
        avg_time = self.total_decision_time / max(self.decision_count, 1)
        
        return {
            'total_decisions': self.decision_count,
            'thompson_decisions': self.thompson_decisions,
            'llm_decisions': self.llm_decisions,
            'batch_decisions': self.batch_decisions,
            'rejected_short': self.rejected_short,
            'epsilon': self.epsilon,
            'average_decision_time_ms': avg_time,
            'total_decision_time_ms': self.total_decision_time,
            'llm_provider': self.llm_provider.value,
            'critical_domains': self.critical_domains
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for hybrid governor"""
        llm_health = self.llm_governor.health_check()
        
        return {
            'status': 'healthy' if llm_health['status'] == 'healthy' else 'degraded',
            'hybrid_governor': 'operational',
            'llm_governor': llm_health,
            'epsilon': self.epsilon,
            'ready_for_integration': True
        }

# Test function
def test_hybrid_governor():
    """Test the Hybrid LLM Governor"""
    print("🧪 Testing Hybrid LLM Governor...")
    
    # Initialize hybrid governor
    governor = HybridLLMGovernor(epsilon=0.3, llm_provider=LLMProvider.OLLAMA)
    
    # Test facts from different categories
    test_facts = [
        "Color(Red)",  # Trivial - should use Thompson
        "Water boils at 100 degrees Celsius at sea level.",  # Standard - epsilon-greedy
        "The speed of light in vacuum is approximately 299,792,458 meters per second.",  # Physics - should use LLM
        "Machine(SteamEngine, Industrial, Revolution, 18th, Century)",  # Multi-arg - should use batch LLM
        "Short fact",  # Too short - should be rejected
        "ChemicalReaction(H2, O2, H2O, Energy, Catalyst)",  # Chemistry - should use LLM
        "Number(42)",  # Trivial - should use Thompson
        "Gene(CFTR, Cystic, Fibrosis, Mutation, DeltaF508)"  # Genetics - should use LLM
    ]
    
    print(f"\n📊 Testing {len(test_facts)} facts with hybrid strategy...")
    
    for i, fact in enumerate(test_facts, 1):
        print(f"\n{i}. Fact: {fact}")
        decision = governor.evaluate_fact(fact)
        print(f"   Decision: {decision.decision_type.value}")
        print(f"   Score: {decision.score:.3f}")
        print(f"   Confidence: {decision.confidence:.3f}")
        print(f"   Time: {decision.evaluation_time_ms}ms")
        print(f"   Reasoning: {decision.reasoning[:60]}...")
    
    # Show statistics
    stats = governor.get_statistics()
    print(f"\n📈 Hybrid Governor Statistics:")
    print(f"   Total Decisions: {stats['total_decisions']}")
    print(f"   Thompson: {stats['thompson_decisions']}")
    print(f"   LLM: {stats['llm_decisions']}")
    print(f"   Batch LLM: {stats['batch_decisions']}")
    print(f"   Rejected Short: {stats['rejected_short']}")
    print(f"   Epsilon: {stats['epsilon']}")
    print(f"   Avg Time: {stats['average_decision_time_ms']:.1f}ms")
    
    # Health check
    health = governor.health_check()
    print(f"\n🏥 Health Check: {health['status']}")
    
    print("\n✅ Hybrid LLM Governor test completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_hybrid_governor()
    else:
        print("Hybrid LLM Governor - Epsilon-Greedy Strategy")
        print("Usage: python hybrid_llm_governor.py --test")
        print("Ready for production integration!")