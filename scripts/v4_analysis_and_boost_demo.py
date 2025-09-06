#!/usr/bin/env python3
"""
HAK-GAL V4 Results Analyzer & LLM Booster
==========================================
Analysiert V4 Ergebnisse und boosted Failed Facts mit LLM
"""

import json

# Die Failed Facts aus V4 (0% Confidence)
FAILED_FACTS_FROM_V4 = [
    # Prevents (alle 0%)
    ("Prevents(HealthProperNutrition, ChronicDiseasese).", 0.0),
    ("Prevents(ProperNutrition, Deficienciese).", 0.0),
    ("Prevents(Stigma, Seekinghelp).", 0.0),
    
    # Influences (alle 0%)
    ("Influences(AdvancementsAndEnvironmental, OnHumanSo).", 0.0),
    ("Influences(OfOneInstantly, AnotherEvenAt).", 0.0),
    ("Influences(OfHowContext, LanguageUse).", 0.0),
    
    # Supports (alle 0%)
    ("Supports(HeartDiseaseDiabetes, ImmuneFunctionAnd).", 0.0),
    ("Supports(highCapacity, UpTo1).", 0.0),
    ("Supports(capacity, UpTo1).", 0.0),
    
    # SubfieldOf (alle 0%)
    ("SubfieldOf(Biotechnology, LifeSciences).", 0.0),
    ("SubfieldOf(Epistemology, Philosophy).", 0.0),
    ("SubfieldOf(Syntax, Linguistics).", 0.0),
    
    # Studies (alle 0%)
    ("Studies(Philosopher, Wisdom).", 0.0),
    ("Studies(Epistemology, Knowledge).", 0.0),
    ("Studies(Linguistics, LanguageStructure).", 0.0),
    
    # Controls (alle 0%)
    ("Controls(access, RestrictData).", 0.0),
    ("Controls(NoSingleEntity, NetworkAll).", 0.0),
    
    # Enables (alle 0%)
    ("Enables(quantumCryptographyEntanglement, SecureComm).", 0.0),
    ("Enables(Personalized_Medicine, Targeted_Therapies).", 0.0),
]

# Erfolgreiche Facts (100%) zum Vergleich
SUCCESSFUL_FACTS_FROM_V4 = [
    ("MayCause(FoodShortages, SpreadOfRevolutionaryIdeal).", 1.0),
    ("DependsOn(NeuralReasoning, AttentionMechanisms).", 1.0),
    ("IsIn(FrenchRevolution, France).", 1.0),
    ("Reduces(ArcticIceMelt, EarthsReflectivityalbedo).", 1.0),
    ("PotentiallyRelatedTo(PointedArches, FlyingButtress).", 1.0),
]

def analyze_v4_results():
    """Analysiert was schief gelaufen ist"""
    print("📊 V4 RESULT ANALYSIS")
    print("="*60)
    
    # Problem 1: Entity-Qualität
    print("\n🔍 PROBLEM 1: Entity Extraction Issues")
    print("-"*40)
    
    bad_entities = [
        "HealthProperNutrition",
        "ChronicDiseasese",
        "AdvancementsAndEnvironmental",
        "OnHumanSo",
        "OfOneInstantly",
        "AnotherEvenAt"
    ]
    
    for entity in bad_entities:
        issues = []
        if len(entity) > 20:
            issues.append("zu lang/zusammengeklebt")
        if entity.endswith("se"):
            issues.append("Tippfehler")
        if entity.startswith("Of") or entity.startswith("On"):
            issues.append("Fragment")
        
        print(f"  ❌ {entity}: {', '.join(issues)}")
    
    print("\n🔍 PROBLEM 2: Success Pattern")
    print("-"*40)
    print("  ✅ Erfolgreiche Prädikate nutzen BEKANNTE Entitäten:")
    print("     • FrenchRevolution, France (historisch)")
    print("     • NeuralReasoning, AttentionMechanisms (AI)")
    print("     • ArcticIceMelt (Klimawandel)")
    print("\n  ❌ Gescheiterte nutzen UNBEKANNTE/KAPUTTE Entitäten")

def simulate_llm_boost():
    """Simuliert wie LLM die Failed Facts retten würde"""
    print("\n" + "="*60)
    print("🤖 LLM BOOST SIMULATION")
    print("="*60)
    
    boosted_facts = []
    
    for fact, hrm_conf in FAILED_FACTS_FROM_V4[:10]:
        print(f"\n📝 Original: {fact}")
        print(f"   HRM: {hrm_conf:.1%}")
        
        # LLM würde erkennen und korrigieren
        if "HealthProperNutrition" in fact:
            corrected = "Prevents(ProperNutrition, ChronicDiseases)."
            llm_conf = 0.85
            reasoning = "Korrigiert: Entities getrennt, Tippfehler behoben"
            
        elif "Biotechnology" in fact and "LifeSciences" in fact:
            corrected = fact  # Ist eigentlich korrekt!
            llm_conf = 0.90
            reasoning = "Semantisch korrekt - Biotechnologie IST Teilgebiet"
            
        elif "Epistemology" in fact and "Philosophy" in fact:
            corrected = fact
            llm_conf = 0.95
            reasoning = "Absolut korrekt - Erkenntnistheorie ist Teil der Philosophie"
            
        elif "Philosopher" in fact and "Wisdom" in fact:
            corrected = "Studies(Philosopher, Wisdom)."
            llm_conf = 0.80
            reasoning = "Klassische philosophische Beziehung"
            
        elif "AdvancementsAndEnvironmental" in fact:
            corrected = "Influences(TechnologicalAdvances, Environment)."
            llm_conf = 0.75
            reasoning = "Entities korrigiert und getrennt"
            
        elif "quantumCryptographyEntanglement" in fact:
            corrected = "Enables(QuantumEntanglement, SecureCommunication)."
            llm_conf = 0.85
            reasoning = "Quantenverschränkung ermöglicht sichere Kommunikation"
            
        else:
            corrected = fact
            llm_conf = 0.50
            reasoning = "Unsicher aber möglicherweise valide"
        
        # Combined Confidence
        combined = (hrm_conf + llm_conf * 2) / 3
        
        print(f"   🤖 LLM: {llm_conf:.1%}")
        print(f"   💡 {reasoning}")
        
        if corrected != fact:
            print(f"   ✏️ Korrigiert: {corrected}")
        
        print(f"   ➡️ COMBINED: {combined:.1%}")
        
        if combined > 0.5:
            print(f"   ✅ WÜRDE ZUR KB HINZUGEFÜGT!")
            boosted_facts.append((corrected, combined))
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("📊 LLM BOOST RESULTS")
    print("="*60)
    
    print(f"\n✅ Gerettete Facts: {len(boosted_facts)}/10")
    print(f"📈 Durchschnittlicher Boost: +{sum(f[1] for f in boosted_facts)/len(boosted_facts)*100:.1f}%")
    
    print("\n🏆 TOP GERETTETE FACTS:")
    for fact, conf in sorted(boosted_facts, key=lambda x: x[1], reverse=True)[:3]:
        print(f"  • {fact[:50]}... ({conf:.1%})")

def recommend_fixes():
    """Empfehlungen für V5"""
    print("\n" + "="*60)
    print("🔧 EMPFEHLUNGEN FÜR V5")
    print("="*60)
    
    print("\n1. ENTITY EXTRACTION FIXEN:")
    print("   • Regex verbessern für saubere Entity-Trennung")
    print("   • CamelCase splitten: 'HealthProperNutrition' → 'Health', 'Proper Nutrition'")
    print("   • Längenlimit für Entities (max 30 chars)")
    
    print("\n2. LLM PRE-VALIDATION:")
    print("   • Facts VOR HRM-Test durch LLM validieren")
    print("   • Kaputte Entities korrigieren")
    print("   • Nur saubere Facts an HRM senden")
    
    print("\n3. ZWEI-WEGE-STRATEGIE:")
    print("   • Weg 1: HRM → Bei Erfolg direkt in KB")
    print("   • Weg 2: HRM versagt → LLM Boost → Combined Score → KB")
    
    print("\n4. PATTERN LEARNING:")
    print("   • Erfolgreiche Patterns speichern")
    print("   • 'MayCause', 'DependsOn', 'IsIn' priorisieren")
    print("   • Von gescheiterten Patterns lernen")

def main():
    print("\n🔬 V4 RESULTS ANALYSIS & LLM BOOST DEMO")
    print("="*60)
    
    # Analyse
    analyze_v4_results()
    
    # LLM Boost Simulation
    simulate_llm_boost()
    
    # Empfehlungen
    recommend_fixes()
    
    print("\n" + "="*60)
    print("💡 FAZIT:")
    print("="*60)
    print("\nV4 hat 55% erreicht - gut aber nicht genug!")
    print("Mit LLM Boost könnten wir auf 75-80% kommen!")
    print("\nDie Hauptprobleme:")
    print("1. Entity-Extraktion produziert Müll")
    print("2. HRM erkennt korrupte Entities nicht")
    print("3. Semantisch korrekte Facts werden verworfen")
    print("\nDie Lösung:")
    print("→ LLM als Validator UND Korrektor!")
    print("→ V4.5 oder V5 mit integriertem LLM Boost!")

if __name__ == "__main__":
    main()
