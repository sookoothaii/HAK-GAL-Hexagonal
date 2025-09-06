#!/usr/bin/env python3
"""
HAK-GAL LLM Confidence Booster
===============================
Validiert 0% Facts durch LLM und hebt Confidence an
Perfekte Ergänzung zu V4 MEGA TURBO

Nach HAK/GAL Verfassung:
- Artikel 1: Komplementäre Intelligenz (HRM + LLM)
- Artikel 3: Externe Verifikation (LLM als Validator)
"""

import requests
import json
import time
from typing import List, Dict, Tuple
from dataclasses import dataclass

BACKEND_URL = 'http://localhost:5002'

@dataclass
class FactValidation:
    """Repräsentiert eine LLM-Validierung"""
    fact: str
    original_confidence: float
    llm_confidence: float
    reasoning: str
    should_add: bool

class LLMConfidenceBooster:
    """
    Nutzt LLM um schwache Facts zu validieren und verbessern
    """
    
    def __init__(self):
        self.failed_facts = []  # Facts mit 0% vom HRM
        self.validated_facts = []  # LLM-validierte Facts
        self.stats = {
            'total_validated': 0,
            'boosted': 0,
            'rejected': 0,
            'added_to_kb': 0,
            'avg_boost': 0.0
        }
    
    def collect_failed_facts(self, facts: List[Tuple[str, float]]):
        """Sammelt Facts mit niedriger Confidence"""
        self.failed_facts = [(f, c) for f, c in facts if c < 0.3]
        print(f"\n📊 Collected {len(self.failed_facts)} low-confidence facts for validation")
    
    def validate_with_llm(self, fact: str, original_confidence: float) -> FactValidation:
        """
        Validiert einen Fact mit LLM
        """
        # Erstelle intelligenten Validation-Prompt
        validation_prompt = f"""
        Analyze this logical fact and determine if it's plausible and meaningful:
        
        FACT: {fact}
        
        Consider:
        1. Is the relationship logically sound?
        2. Are the entities properly matched to the predicate?
        3. Would this be useful knowledge?
        4. Is it factually plausible?
        
        Respond with:
        - CONFIDENCE: 0.0-1.0 (how confident are you this is valid)
        - REASONING: Brief explanation
        - IMPROVED_FACT: If you can improve it, provide better version
        
        Examples of good facts:
        - Requires(Computer, Electricity) - concrete dependency
        - Creates(Sun, Light) - causal relationship
        - LocatedIn(Berlin, Germany) - geographical fact
        
        Examples of bad facts:
        - Requires(Philosophy, Understanding) - too abstract
        - BornIn(Renaissance, Technology) - category mismatch
        """
        
        try:
            # LLM API Call
            response = requests.post(
                f"{BACKEND_URL}/api/llm/analyze-fact",
                json={
                    'fact': fact,
                    'prompt': validation_prompt,
                    'context': {
                        'original_confidence': original_confidence,
                        'validation_type': 'semantic'
                    }
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                
                # Parse LLM Response
                llm_confidence = data.get('confidence', 0.0)
                reasoning = data.get('reasoning', 'No reasoning provided')
                improved_fact = data.get('improved_fact', fact)
                
                # Entscheide ob wir den Fact hinzufügen
                should_add = llm_confidence > 0.5
                
                return FactValidation(
                    fact=improved_fact if improved_fact else fact,
                    original_confidence=original_confidence,
                    llm_confidence=llm_confidence,
                    reasoning=reasoning,
                    should_add=should_add
                )
            
            else:
                # Fallback wenn LLM nicht verfügbar
                return FactValidation(
                    fact=fact,
                    original_confidence=original_confidence,
                    llm_confidence=0.0,
                    reasoning="LLM validation failed",
                    should_add=False
                )
                
        except Exception as e:
            print(f"  ❌ LLM validation error: {e}")
            return FactValidation(
                fact=fact,
                original_confidence=original_confidence,
                llm_confidence=0.0,
                reasoning=f"Error: {e}",
                should_add=False
            )
    
    def boost_confidence_batch(self, limit: int = 10):
        """
        Validiert und boosted eine Batch von Facts
        """
        print("\n" + "="*60)
        print("🤖 LLM CONFIDENCE BOOSTING")
        print("="*60)
        
        if not self.failed_facts:
            print("No failed facts to validate")
            return
        
        facts_to_validate = self.failed_facts[:limit]
        print(f"Validating {len(facts_to_validate)} facts with LLM...")
        
        for i, (fact, orig_conf) in enumerate(facts_to_validate, 1):
            print(f"\n[{i}/{len(facts_to_validate)}] Validating: {fact[:60]}...")
            print(f"  Original HRM confidence: {orig_conf:.1%}")
            
            # LLM Validation
            validation = self.validate_with_llm(fact, orig_conf)
            self.validated_facts.append(validation)
            self.stats['total_validated'] += 1
            
            # Visualisierung
            if validation.llm_confidence > 0.7:
                print(f"  ✅ LLM confidence: {validation.llm_confidence:.1%}")
                print(f"  💡 Reasoning: {validation.reasoning[:100]}...")
                self.stats['boosted'] += 1
                
                # Füge zur KB hinzu mit LLM-Confidence
                if validation.should_add:
                    self._add_to_kb_with_boost(validation)
                    
            elif validation.llm_confidence > 0.3:
                print(f"  ⚠️ LLM confidence: {validation.llm_confidence:.1%}")
                print(f"  💡 Reasoning: {validation.reasoning[:100]}...")
                
            else:
                print(f"  ❌ LLM rejected: {validation.llm_confidence:.1%}")
                print(f"  💡 Reasoning: {validation.reasoning[:100]}...")
                self.stats['rejected'] += 1
            
            time.sleep(0.5)  # Rate limiting
        
        # Zusammenfassung
        self._print_boost_summary()
    
    def _add_to_kb_with_boost(self, validation: FactValidation):
        """Fügt validierten Fact mit geboosteter Confidence zur KB hinzu"""
        try:
            # Kombiniere HRM und LLM Confidence
            combined_confidence = (validation.original_confidence + validation.llm_confidence) / 2
            
            # Mindestens LLM confidence wenn HRM 0% war
            if validation.original_confidence < 0.1:
                combined_confidence = validation.llm_confidence * 0.8  # Etwas konservativ
            
            response = requests.post(
                f"{BACKEND_URL}/api/facts",
                json={
                    'statement': validation.fact,
                    'source': 'llm_validated',
                    'confidence': combined_confidence,
                    'metadata': {
                        'hrm_confidence': validation.original_confidence,
                        'llm_confidence': validation.llm_confidence,
                        'reasoning': validation.reasoning
                    }
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.ok and response.json().get('success'):
                self.stats['added_to_kb'] += 1
                print(f"    💾 Added to KB with {combined_confidence:.1%} confidence")
                return True
                
        except Exception as e:
            print(f"    ❌ Failed to add to KB: {e}")
        
        return False
    
    def _print_boost_summary(self):
        """Druckt Zusammenfassung der Boost-Operation"""
        print("\n" + "="*60)
        print("📊 BOOST SUMMARY")
        print("="*60)
        
        if self.stats['total_validated'] > 0:
            boost_rate = (self.stats['boosted'] / self.stats['total_validated']) * 100
            
            print(f"\n✅ RESULTS:")
            print(f"  Total Validated: {self.stats['total_validated']}")
            print(f"  Successfully Boosted: {self.stats['boosted']} ({boost_rate:.1f}%)")
            print(f"  Rejected by LLM: {self.stats['rejected']}")
            print(f"  Added to KB: {self.stats['added_to_kb']}")
            
            # Durchschnittlicher Boost
            if self.validated_facts:
                avg_original = sum(v.original_confidence for v in self.validated_facts) / len(self.validated_facts)
                avg_llm = sum(v.llm_confidence for v in self.validated_facts) / len(self.validated_facts)
                avg_boost = avg_llm - avg_original
                
                print(f"\n📈 CONFIDENCE BOOST:")
                print(f"  Average Original: {avg_original:.1%}")
                print(f"  Average LLM: {avg_llm:.1%}")
                print(f"  Average Boost: +{avg_boost:.1%}")
            
            # Top Boosts
            top_boosts = sorted(self.validated_facts, 
                              key=lambda x: x.llm_confidence - x.original_confidence, 
                              reverse=True)[:3]
            
            if top_boosts:
                print(f"\n🏆 TOP BOOSTS:")
                for v in top_boosts:
                    boost = v.llm_confidence - v.original_confidence
                    print(f"  • {v.fact[:50]}...")
                    print(f"    {v.original_confidence:.1%} → {v.llm_confidence:.1%} (+{boost:.1%})")
    
    def create_feedback_loop(self):
        """
        Erstellt Feedback für HRM basierend auf LLM-Validierungen
        """
        print("\n" + "="*60)
        print("🔄 CREATING HRM FEEDBACK LOOP")
        print("="*60)
        
        feedback_data = []
        
        for validation in self.validated_facts:
            if validation.llm_confidence > 0.6:
                # Positive Feedback für HRM
                feedback_data.append({
                    'fact': validation.fact,
                    'expected_confidence': validation.llm_confidence,
                    'feedback_type': 'positive'
                })
        
        if feedback_data:
            try:
                # Sende Feedback an HRM
                response = requests.post(
                    f"{BACKEND_URL}/api/hrm/feedback",
                    json={'feedback_batch': feedback_data},
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                if response.ok:
                    print(f"✅ Sent {len(feedback_data)} feedback items to HRM")
                    print("   HRM will learn from LLM-validated facts!")
                else:
                    print(f"⚠️ Feedback submission failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Feedback error: {e}")

class IntegratedExplorationWithBoost:
    """
    Integriert V4 Exploration mit LLM Boosting
    """
    
    def __init__(self):
        self.booster = LLMConfidenceBooster()
        self.all_test_results = []
    
    def run_boosted_exploration(self):
        """
        Führt kompletten Zyklus durch:
        1. V4 Exploration
        2. Sammle 0% Facts
        3. LLM Validation
        4. KB Update
        5. HRM Feedback
        """
        print("\n" + "="*60)
        print("🚀 INTEGRATED EXPLORATION WITH LLM BOOST")
        print("="*60)
        
        # Simuliere Exploration-Ergebnisse
        # In Produktion würde dies von V4 kommen
        sample_failed_facts = [
            ("Requires(Computer, CPU).", 0.0),
            ("Creates(Artist, Art).", 0.0),
            ("Influences(Temperature, Ice).", 0.0),
            ("DependsOn(Software, Hardware).", 0.0),
            ("Produces(Factory, Product).", 0.0),
            ("ConnectsTo(France, Germany).", 0.0),
            ("Affects(Weather, Mood).", 0.0),
            ("Prevents(Vaccine, Disease).", 0.0),
            ("GeneratedBy(Electricity, Generator).", 0.0),
            ("LocatedAt(Heart, Body).", 0.0)
        ]
        
        # Phase 1: Sammle Failed Facts
        print("\n📊 PHASE 1: Collecting failed facts...")
        self.booster.collect_failed_facts(sample_failed_facts)
        
        # Phase 2: LLM Validation & Boost
        print("\n🤖 PHASE 2: LLM Validation & Boosting...")
        self.booster.boost_confidence_batch(limit=5)
        
        # Phase 3: Feedback Loop
        print("\n🔄 PHASE 3: Creating feedback loop...")
        self.booster.create_feedback_loop()
        
        # Final Summary
        self._print_final_summary()
    
    def _print_final_summary(self):
        """Finale Zusammenfassung"""
        print("\n" + "="*60)
        print("🏁 INTEGRATED EXPLORATION COMPLETE")
        print("="*60)
        
        print("\n💡 KEY INSIGHTS:")
        print("• HRM finds patterns but misses some valid facts")
        print("• LLM can validate semantic correctness")
        print("• Combined approach achieves better coverage")
        print("• Feedback loop enables continuous improvement")
        
        print("\n🎯 NEXT STEPS:")
        print("1. Run V4 MEGA TURBO exploration")
        print("2. Collect all 0% confidence facts")
        print("3. Validate with LLM booster")
        print("4. Update KB with boosted facts")
        print("5. Let HRM learn from validated facts")

def main():
    """Main execution"""
    print("\n🤖 LLM CONFIDENCE BOOSTER")
    print("="*60)
    print("Validates and boosts low-confidence facts")
    print("="*60)
    
    print("\nOptions:")
    print("1. Test with sample facts")
    print("2. Integrated exploration with boost")
    print("3. Manual fact validation")
    
    choice = input("\nChoice (1-3): ")
    
    if choice == '1':
        booster = LLMConfidenceBooster()
        
        # Test Facts
        test_facts = [
            ("Requires(Computer, CPU).", 0.0),
            ("BornIn(Renaissance, Technology).", 0.0),
            ("Creates(Sun, Light).", 0.0),
            ("HasPurpose(Knife, Cutting).", 0.0),
            ("Influenced(Socrates, Plato).", 0.0)
        ]
        
        booster.collect_failed_facts(test_facts)
        booster.boost_confidence_batch(limit=5)
        booster.create_feedback_loop()
        
    elif choice == '2':
        integrated = IntegratedExplorationWithBoost()
        integrated.run_boosted_exploration()
        
    elif choice == '3':
        booster = LLMConfidenceBooster()
        
        fact = input("Enter fact to validate: ")
        validation = booster.validate_with_llm(fact, 0.0)
        
        print(f"\nValidation Result:")
        print(f"  LLM Confidence: {validation.llm_confidence:.1%}")
        print(f"  Reasoning: {validation.reasoning}")
        print(f"  Should Add: {validation.should_add}")
    
    print("\n✅ LLM Confidence Booster complete!")

if __name__ == "__main__":
    main()
