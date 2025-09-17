#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Domain Classifier Service
=========================
Classifies facts into domains and provides domain balance analysis.
Ready for integration with real ML models when Opus 4.1 design is complete.
"""

import time
import logging
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import re

logger = logging.getLogger(__name__)

@dataclass
class DomainClassification:
    """Result of domain classification"""
    fact: str
    primary_domain: str
    confidence: float
    all_domains: List[Tuple[str, float]]
    classification_time_ms: int
    metadata: Dict[str, Any]

class DomainClassifier:
    """
    Domain Classifier for facts
    Currently implements rule-based classification, ready for ML model integration
    """
    
    def __init__(self, db_path: str = "hexagonal_kb.db"):
        self.db_path = db_path
        self.classification_count = 0
        self.total_classification_time = 0.0
        
        # 44 Domains from the extended fact manager
        self.domains = {
            # Core Sciences
            'astronomy': ['star', 'planet', 'galaxy', 'solar', 'orbit', 'cosmic', 'celestial', 'universe'],
            'geology': ['rock', 'mineral', 'earth', 'crust', 'tectonic', 'volcano', 'earthquake', 'fossil'],
            'psychology': ['behavior', 'mental', 'cognitive', 'personality', 'emotion', 'brain', 'mind'],
            'neuroscience': ['neuron', 'brain', 'synapse', 'neural', 'cortex', 'cerebral', 'nervous'],
            'sociology': ['society', 'social', 'culture', 'group', 'community', 'population', 'demographic'],
            'linguistics': ['language', 'word', 'syntax', 'grammar', 'phoneme', 'semantic', 'linguistic'],
            
            # Arts & Humanities
            'philosophy': ['philosophy', 'ethical', 'moral', 'existential', 'metaphysical', 'logical'],
            'art': ['art', 'painting', 'sculpture', 'aesthetic', 'creative', 'artistic', 'visual'],
            'music': ['music', 'melody', 'harmony', 'rhythm', 'instrument', 'musical', 'composition'],
            'literature': ['literature', 'novel', 'poetry', 'writing', 'author', 'book', 'text'],
            'history': ['history', 'historical', 'ancient', 'medieval', 'century', 'era', 'period'],
            'architecture': ['architecture', 'building', 'structure', 'design', 'construction', 'roof', 'foundation'],
            
            # Engineering & Tech
            'engineering': ['engineering', 'machine', 'mechanical', 'structural', 'civil', 'electrical'],
            'robotics': ['robot', 'robotic', 'automation', 'artificial', 'machine', 'automated'],
            'computer_science': ['computer', 'algorithm', 'programming', 'software', 'data', 'computing'],
            'ai': ['artificial', 'intelligence', 'machine', 'learning', 'neural', 'algorithm'],
            'cryptography': ['cryptography', 'encryption', 'security', 'cipher', 'cryptographic'],
            'environmental_science': ['environment', 'ecological', 'sustainable', 'climate', 'pollution'],
            
            # Life Sciences
            'genetics': ['gene', 'genetic', 'dna', 'chromosome', 'mutation', 'heredity'],
            'immunology': ['immune', 'antibody', 'antigen', 'immunity', 'vaccine', 'pathogen'],
            'pharmacology': ['drug', 'medicine', 'pharmaceutical', 'therapeutic', 'treatment'],
            'surgery': ['surgery', 'surgical', 'operation', 'procedure', 'medical', 'treatment'],
            'ecology': ['ecology', 'ecosystem', 'species', 'habitat', 'biodiversity', 'environmental'],
            'climate': ['climate', 'weather', 'temperature', 'atmospheric', 'global', 'warming'],
            
            # Business & Law
            'finance': ['finance', 'financial', 'money', 'investment', 'banking', 'economic'],
            'marketing': ['marketing', 'advertising', 'brand', 'customer', 'market', 'sales'],
            'management': ['management', 'leadership', 'organization', 'business', 'strategy'],
            'entrepreneurship': ['entrepreneur', 'startup', 'business', 'innovation', 'venture'],
            'politics': ['politics', 'political', 'government', 'policy', 'democracy', 'election'],
            'law': ['law', 'legal', 'court', 'justice', 'legislation', 'constitutional'],
            
            # Earth & Ancient
            'ethics': ['ethics', 'ethical', 'moral', 'right', 'wrong', 'value', 'principle'],
            'anthropology': ['anthropology', 'human', 'culture', 'society', 'evolution', 'behavior'],
            'archaeology': ['archaeology', 'archaeological', 'artifact', 'ancient', 'excavation'],
            'paleontology': ['paleontology', 'fossil', 'dinosaur', 'prehistoric', 'evolution'],
            'meteorology': ['meteorology', 'weather', 'atmosphere', 'climate', 'storm', 'precipitation'],
            'oceanography': ['ocean', 'marine', 'sea', 'water', 'aquatic', 'oceanographic']
        }
        
        # Domain statistics
        self.domain_counts = Counter()
        self.classification_cache = {}
        
        logger.info(f"Domain Classifier initialized with {len(self.domains)} domains")
    
    def classify_fact(self, fact: str) -> DomainClassification:
        """
        Classify a fact into domains using rule-based approach
        
        Args:
            fact: The fact statement to classify
            
        Returns:
            DomainClassification with primary domain and confidence
        """
        start_time = time.time()
        
        # Check cache first
        if fact in self.classification_cache:
            cached_result = self.classification_cache[fact]
            cached_result.classification_time_ms = int((time.time() - start_time) * 1000)
            return cached_result
        
        fact_lower = fact.lower()
        domain_scores = {}
        
        # Calculate scores for each domain
        for domain, keywords in self.domains.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword in fact_lower:
                    matches += 1
                    # Weight by keyword length (longer keywords are more specific)
                    score += len(keyword) * 2
            
            # Normalize score by number of keywords in domain
            if len(keywords) > 0:
                domain_scores[domain] = score / len(keywords)
            else:
                domain_scores[domain] = 0
        
        # Find primary domain
        if domain_scores:
            primary_domain = max(domain_scores, key=domain_scores.get)
            max_score = domain_scores[primary_domain]
            
            # Calculate confidence based on score and uniqueness
            sorted_scores = sorted(domain_scores.values(), reverse=True)
            if len(sorted_scores) > 1:
                confidence = (sorted_scores[0] - sorted_scores[1]) / max(sorted_scores[0], 1)
            else:
                confidence = 1.0
            
            # Normalize confidence to 0-1 range
            confidence = min(max(confidence, 0.0), 1.0)
            
        else:
            primary_domain = 'unknown'
            max_score = 0
            confidence = 0.0
        
        # Get all domains with scores
        all_domains = [(domain, score) for domain, score in domain_scores.items() if score > 0]
        all_domains.sort(key=lambda x: x[1], reverse=True)
        
        classification_time_ms = int((time.time() - start_time) * 1000)
        
        result = DomainClassification(
            fact=fact,
            primary_domain=primary_domain,
            confidence=confidence,
            all_domains=all_domains,
            classification_time_ms=classification_time_ms,
            metadata={
                'max_score': max_score,
                'total_domains_matched': len(all_domains),
                'classification_method': 'rule_based'
            }
        )
        
        # Cache result
        self.classification_cache[fact] = result
        
        # Update statistics
        self.classification_count += 1
        self.total_classification_time += classification_time_ms
        self.domain_counts[primary_domain] += 1
        
        logger.info(f"Fact classified: {fact[:50]}... Domain: {primary_domain}, Confidence: {confidence:.2f}")
        
        return result
    
    def batch_classify_facts(self, facts: List[str]) -> List[DomainClassification]:
        """Classify multiple facts"""
        results = []
        
        for fact in facts:
            result = self.classify_fact(fact)
            results.append(result)
        
        return results
    
    def get_domain_statistics(self) -> Dict[str, Any]:
        """Get domain distribution statistics"""
        total_facts = sum(self.domain_counts.values())
        
        if total_facts == 0:
            return {
                'total_facts': 0,
                'domain_distribution': {},
                'balance_score': 1.0,
                'most_common_domain': None,
                'least_common_domain': None
            }
        
        # Calculate distribution percentages
        domain_distribution = {}
        for domain, count in self.domain_counts.items():
            domain_distribution[domain] = {
                'count': count,
                'percentage': (count / total_facts) * 100
            }
        
        # Calculate balance score (entropy-based)
        import math
        entropy = 0
        for count in self.domain_counts.values():
            if count > 0:
                p = count / total_facts
                entropy -= p * math.log2(p)
        
        max_entropy = math.log2(len(self.domains))
        balance_score = entropy / max_entropy if max_entropy > 0 else 1.0
        
        return {
            'total_facts': total_facts,
            'domain_distribution': domain_distribution,
            'balance_score': balance_score,
            'most_common_domain': self.domain_counts.most_common(1)[0] if self.domain_counts else None,
            'least_common_domain': self.domain_counts.most_common()[-1] if self.domain_counts else None,
            'total_domains': len(self.domains),
            'domains_used': len(self.domain_counts)
        }
    
    def analyze_database_domains(self, limit: int = 1000) -> Dict[str, Any]:
        """Analyze domain distribution in the database"""
        facts = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT statement FROM facts 
                    ORDER BY rowid DESC 
                    LIMIT ?
                """, (limit,))
                
                facts = [row[0] for row in cursor.fetchall()]
                logger.info(f"Analyzing {len(facts)} facts from database")
                
        except Exception as e:
            logger.error(f"Failed to load facts from database: {e}")
            return {'error': str(e)}
        
        # Classify all facts
        results = self.batch_classify_facts(facts)
        
        # Get statistics
        stats = self.get_domain_statistics()
        
        return {
            'facts_analyzed': len(facts),
            'classification_results': results,
            'statistics': stats
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get classification statistics"""
        avg_time = self.total_classification_time / max(self.classification_count, 1)
        
        return {
            'classification_count': self.classification_count,
            'total_classification_time_ms': self.total_classification_time,
            'average_classification_time_ms': avg_time,
            'cache_size': len(self.classification_cache),
            'domains_available': len(self.domains),
            'domains_used': len(self.domain_counts)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the domain classifier"""
        return {
            'status': 'healthy',
            'domains_loaded': len(self.domains),
            'classifications_performed': self.classification_count,
            'ready_for_integration': True
        }

# Test function for development
def test_domain_classifier():
    """Test the Domain Classifier"""
    print("🧪 Testing Domain Classifier...")
    
    # Initialize classifier
    classifier = DomainClassifier()
    
    # Test facts from different domains
    test_facts = [
        "Water boils at 100 degrees Celsius at sea level.",  # Chemistry/Physics
        "The Earth orbits around the Sun in approximately 365.25 days.",  # Astronomy
        "Shakespeare wrote Romeo and Juliet in the 16th century.",  # Literature/History
        "The human brain contains approximately 86 billion neurons.",  # Neuroscience
        "Photosynthesis converts sunlight into chemical energy.",  # Biology
        "The Great Wall of China was built over several dynasties.",  # History/Architecture
        "Machine learning algorithms can recognize patterns in data.",  # AI/Computer Science
        "The stock market experienced volatility due to economic uncertainty.",  # Finance
        "Climate change affects global weather patterns.",  # Climate/Environmental
        "The legal system ensures justice and fairness in society."  # Law
    ]
    
    print(f"\n📊 Classifying {len(test_facts)} test facts...")
    
    for i, fact in enumerate(test_facts, 1):
        print(f"\n{i}. Fact: {fact}")
        classification = classifier.classify_fact(fact)
        print(f"   Primary Domain: {classification.primary_domain}")
        print(f"   Confidence: {classification.confidence:.2f}")
        print(f"   Top Domains: {[d[0] for d in classification.all_domains[:3]]}")
        print(f"   Time: {classification.classification_time_ms}ms")
    
    # Show domain statistics
    stats = classifier.get_domain_statistics()
    print(f"\n📈 Domain Statistics:")
    print(f"   Total Facts: {stats['total_facts']}")
    print(f"   Balance Score: {stats['balance_score']:.2f}")
    print(f"   Most Common: {stats['most_common_domain']}")
    print(f"   Domains Used: {stats['domains_used']}/{stats['total_domains']}")
    
    # Show classification statistics
    class_stats = classifier.get_statistics()
    print(f"\n📊 Classification Statistics:")
    print(f"   Classifications: {class_stats['classification_count']}")
    print(f"   Avg Time: {class_stats['average_classification_time_ms']:.1f}ms")
    print(f"   Cache Size: {class_stats['cache_size']}")
    
    # Health check
    health = classifier.health_check()
    print(f"\n🏥 Health Check: {health['status']}")
    
    print("\n✅ Domain Classifier test completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_domain_classifier()
    else:
        print("Domain Classifier - Rule-based Implementation")
        print("Usage: python domain_classifier_service.py --test")
        print("Ready for integration with Opus 4.1 design!")