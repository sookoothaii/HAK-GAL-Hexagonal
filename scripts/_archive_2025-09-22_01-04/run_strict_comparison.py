#!/usr/bin/env python3
"""
ERWEITERTER LLM-VERGLEICHSTEST
Mit striktem wissenschaftlichem Validator und 3-5 Fakten/Domain
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from strict_scientific_validator import ScientificFactValidator, create_strict_validation_prompt

# Konfiguration
FACTS_PER_DOMAIN = 3  # Erhöht von 1 auf 3
OUTPUT_DIR = Path("validation_results/llm_runs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Test-Domains mit präzisen Anforderungen
TEST_DOMAINS = {
    "CHEMISTRY": {
        "predicates": ["ChemicalReaction", "MolecularStructure", "ElectronConfiguration"],
        "min_args": 6,
        "max_args": 7
    },
    "PHYSICS": {
        "predicates": ["ElectromagneticWave", "ParticleInteraction", "Motion"],
        "min_args": 6,
        "max_args": 7
    },
    "BIOLOGY": {
        "predicates": ["ProteinSynthesis", "CellularRespiration", "DNAReplication"],
        "min_args": 6,
        "max_args": 7
    },
    "COMPUTER_SCIENCE": {
        "predicates": ["AlgorithmAnalysis", "TCPConnection", "DataStructure"],
        "min_args": 6,
        "max_args": 7
    },
    "MATHEMATICS": {
        "predicates": ["FunctionAnalysis", "MatrixOperation", "NumberProperty"],
        "min_args": 6,
        "max_args": 7
    }
}

def generate_precise_prompt(domain: str, predicate: str) -> str:
    """
    Generiert präzisen Prompt für wissenschaftliche Fakten
    """
    examples = {
        "ChemicalReaction": "ChemicalReaction(N2, 3H2, 2NH3, null, Fe_catalyst, 450C, 200atm)",
        "MolecularStructure": "MolecularStructure(CH4, carbon, 4hydrogen, tetrahedral, sp3, nonpolar, 109.5deg)",
        "ElectromagneticWave": "ElectromagneticWave(visible_light, 500nm, 600THz, 2.48eV, linear, vacuum, 299792458m/s)",
        "ParticleInteraction": "ParticleInteraction(electron, proton, electromagnetic, -13.6eV, conserved, opposite, hydrogen)",
        "ProteinSynthesis": "ProteinSynthesis(insulin_gene, pre_mRNA, mRNA, ribosome, amino_acids, proinsulin, ER)",
        "CellularRespiration": "CellularRespiration(glucose, 6O2, 6CO2, 6H2O, 38ATP, mitochondria, aerobic)",
        "AlgorithmAnalysis": "AlgorithmAnalysis(quicksort, O(nlogn), O(nlogn), O(n2), O(logn), divide_conquer, unstable)",
        "TCPConnection": "TCPConnection(192.168.1.1, 8080, 10.0.0.1, 443, SYN_ACK, 0x1234, established)",
        "FunctionAnalysis": "FunctionAnalysis(sin_x, periodic, continuous, cos_x, -sin_x, bounded, wave)",
        "MatrixOperation": "MatrixOperation(A_3x3, B_3x3, multiply, C_3x3, 27_ops, non_commutative, O_n3)",
        "DNAReplication": "DNAReplication(template, DNA_polymerase, primer, nucleotides, 3to5_direction, lagging, semiconservative)",
        "DataStructure": "DataStructure(B_tree, balanced, O_logn, O_logn, O_logn, disk_optimized, database)",
        "NumberProperty": "NumberProperty(6, composite, perfect, 1_2_3_6, sum_12, abundant_false, first_perfect)"
    }
    
    example = examples.get(predicate, examples.get(list(examples.keys())[0]))
    
    return f"""Generate a scientifically accurate {domain} fact using the {predicate} predicate.

REQUIREMENTS:
1. Use EXACTLY 6 or 7 arguments
2. Must be 100% scientifically correct
3. Include proper units (C, K, atm, m/s, eV, etc.)
4. Use 'null' for absent values, never skip positions
5. Follow conservation laws (mass, energy, momentum)

Example format:
{example}

Generate ONE fact only. Output ONLY the fact, no explanation.
Format: {predicate}(arg1, arg2, arg3, arg4, arg5, arg6[, arg7])"""


def run_comprehensive_test(llm_provider: str, api_function) -> Dict:
    """
    Führt umfassenden Test mit strikter Validierung durch
    """
    validator = ScientificFactValidator()
    
    results = {
        "provider": llm_provider,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "facts_per_domain": FACTS_PER_DOMAIN,
            "domains": list(TEST_DOMAINS.keys()),
            "validator": "strict_scientific"
        },
        "domains": {},
        "metrics": {
            "total_generated": 0,
            "valid_facts": 0,
            "invalid_facts": 0,
            "avg_confidence": 0.0,
            "avg_arguments": 0.0,
            "avg_generation_time": 0.0,
            "domain_accuracy": {}
        }
    }
    
    all_confidences = []
    all_arg_counts = []
    all_gen_times = []
    
    for domain, config in TEST_DOMAINS.items():
        print(f"\n{llm_provider} - Testing {domain}...")
        
        domain_results = {
            "predicates": config["predicates"],
            "facts": [],
            "valid_count": 0,
            "invalid_count": 0
        }
        
        for predicate in config["predicates"][:1]:  # Test nur ersten Prädikat pro Domain
            for i in range(FACTS_PER_DOMAIN):
                prompt = generate_precise_prompt(domain, predicate)
                
                try:
                    # Generiere Fakt
                    start = time.time()
                    generated_fact = api_function(prompt)
                    gen_time = time.time() - start
                    
                    # Validiere mit striktem Validator
                    validation = validator.validate_fact(generated_fact, domain)
                    
                    # Zähle Argumente
                    arg_count = generated_fact.count(',') + 1
                    
                    # Speichere Ergebnis
                    fact_result = {
                        "fact": generated_fact,
                        "predicate": predicate,
                        "arg_count": arg_count,
                        "generation_time": gen_time,
                        "valid": validation["is_valid"],
                        "confidence": validation["confidence"],
                        "issues": validation["issues"],
                        "domain_check": validation["domain_check"],
                        "scientific_accuracy": validation["scientific_accuracy"]
                    }
                    
                    domain_results["facts"].append(fact_result)
                    
                    # Update Metriken
                    results["metrics"]["total_generated"] += 1
                    if validation["is_valid"]:
                        results["metrics"]["valid_facts"] += 1
                        domain_results["valid_count"] += 1
                        print(f"  ✓ Valid: {generated_fact[:60]}...")
                    else:
                        results["metrics"]["invalid_facts"] += 1
                        domain_results["invalid_count"] += 1
                        print(f"  ✗ Invalid: {validation['issues'][0] if validation['issues'] else 'Unknown'}")
                    
                    all_confidences.append(validation["confidence"])
                    all_arg_counts.append(arg_count)
                    all_gen_times.append(gen_time)
                    
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
                    domain_results["facts"].append({
                        "error": str(e),
                        "predicate": predicate
                    })
                    results["metrics"]["invalid_facts"] += 1
                
                time.sleep(0.5)  # Rate limiting
        
        # Domain-Genauigkeit
        total = domain_results["valid_count"] + domain_results["invalid_count"]
        if total > 0:
            domain_accuracy = domain_results["valid_count"] / total
        else:
            domain_accuracy = 0.0
        
        results["metrics"]["domain_accuracy"][domain] = domain_accuracy
        results["domains"][domain] = domain_results
    
    # Berechne Durchschnitte
    if results["metrics"]["total_generated"] > 0:
        results["metrics"]["avg_confidence"] = sum(all_confidences) / len(all_confidences)
        results["metrics"]["avg_arguments"] = sum(all_arg_counts) / len(all_arg_counts)
        results["metrics"]["avg_generation_time"] = sum(all_gen_times) / len(all_gen_times)
        results["metrics"]["overall_accuracy"] = results["metrics"]["valid_facts"] / results["metrics"]["total_generated"]
    
    return results


def compare_providers(groq_results: Dict, deepseek_results: Dict) -> Dict:
    """
    Vergleicht Groq und DeepSeek mit wissenschaftlichen Kriterien
    """
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "winner": None,
        "scores": {"groq": 0, "deepseek": 0},
        "detailed_comparison": {},
        "recommendations": []
    }
    
    # Gewichtete Bewertung
    criteria = {
        "overall_accuracy": {"weight": 5, "higher_better": True},  # Wichtigster Faktor!
        "avg_confidence": {"weight": 3, "higher_better": True},
        "avg_arguments": {"weight": 2, "target": 6.5},  # Nähe zu 6-7 Argumenten
        "avg_generation_time": {"weight": 1, "higher_better": False}  # Geschwindigkeit weniger wichtig
    }
    
    for criterion, config in criteria.items():
        groq_val = groq_results["metrics"].get(criterion, 0)
        deepseek_val = deepseek_results["metrics"].get(criterion, 0)
        
        comparison["detailed_comparison"][criterion] = {
            "groq": groq_val,
            "deepseek": deepseek_val
        }
        
        # Bewertung
        if "target" in config:
            # Nähe zum Zielwert
            groq_distance = abs(groq_val - config["target"])
            deepseek_distance = abs(deepseek_val - config["target"])
            if groq_distance < deepseek_distance:
                comparison["scores"]["groq"] += config["weight"]
            else:
                comparison["scores"]["deepseek"] += config["weight"]
        else:
            # Höher/niedriger ist besser
            if config["higher_better"]:
                if groq_val > deepseek_val:
                    comparison["scores"]["groq"] += config["weight"]
                else:
                    comparison["scores"]["deepseek"] += config["weight"]
            else:
                if groq_val < deepseek_val:
                    comparison["scores"]["groq"] += config["weight"]
                else:
                    comparison["scores"]["deepseek"] += config["weight"]
    
    # Bestimme Gewinner
    if comparison["scores"]["deepseek"] > comparison["scores"]["groq"]:
        comparison["winner"] = "DeepSeek"
    else:
        comparison["winner"] = "Groq"
    
    # Domain-spezifische Analyse
    comparison["domain_performance"] = {}
    for domain in TEST_DOMAINS.keys():
        groq_acc = groq_results["metrics"]["domain_accuracy"].get(domain, 0)
        deepseek_acc = deepseek_results["metrics"]["domain_accuracy"].get(domain, 0)
        
        comparison["domain_performance"][domain] = {
            "groq": f"{groq_acc:.1%}",
            "deepseek": f"{deepseek_acc:.1%}",
            "winner": "DeepSeek" if deepseek_acc > groq_acc else "Groq"
        }
    
    # Empfehlungen
    overall_winner = comparison["winner"]
    overall_acc = comparison["detailed_comparison"]["overall_accuracy"]
    
    if overall_acc[overall_winner.lower()] > 0.8:
        comparison["recommendations"].append(
            f"✅ {overall_winner} empfohlen - {overall_acc[overall_winner.lower()]:.1%} wissenschaftliche Genauigkeit"
        )
    elif overall_acc[overall_winner.lower()] > 0.6:
        comparison["recommendations"].append(
            f"⚠️ {overall_winner} bedingt geeignet - weitere Optimierung nötig"
        )
    else:
        comparison["recommendations"].append(
            f"❌ Beide LLMs unzureichend - striktere Prompts oder andere Modelle testen"
        )
    
    # Domain-spezifische Empfehlungen
    for domain, perf in comparison["domain_performance"].items():
        if float(perf["deepseek"].rstrip('%')) / 100 > 0.9:
            comparison["recommendations"].append(
                f"DeepSeek exzellent für {domain}"
            )
        elif float(perf["groq"].rstrip('%')) / 100 > 0.9:
            comparison["recommendations"].append(
                f"Groq exzellent für {domain}"
            )
    
    return comparison


def generate_report(groq_results: Dict, deepseek_results: Dict, comparison: Dict) -> str:
    """
    Generiert detaillierten Vergleichsbericht
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report = f"""
WISSENSCHAFTLICHER LLM-FAKTENGENERIERUNG VERGLEICHSTEST
{'='*60}
Zeitstempel: {timestamp}
Konfiguration: {FACTS_PER_DOMAIN} Fakten/Domain, Strikter Validator

ZUSAMMENFASSUNG
{'-'*40}
🏆 GEWINNER: {comparison['winner']}
Punkte: Groq {comparison['scores']['groq']} - DeepSeek {comparison['scores']['deepseek']}

WISSENSCHAFTLICHE GENAUIGKEIT
{'-'*40}
                    Groq        DeepSeek    Besser
Gesamt-Genauigkeit: {comparison['detailed_comparison']['overall_accuracy']['groq']:.1%}      {comparison['detailed_comparison']['overall_accuracy']['deepseek']:.1%}       {comparison['winner']}
Ø Konfidenz:        {comparison['detailed_comparison']['avg_confidence']['groq']:.2f}        {comparison['detailed_comparison']['avg_confidence']['deepseek']:.2f}         {'DeepSeek' if comparison['detailed_comparison']['avg_confidence']['deepseek'] > comparison['detailed_comparison']['avg_confidence']['groq'] else 'Groq'}
Ø Argumente:        {comparison['detailed_comparison']['avg_arguments']['groq']:.1f}        {comparison['detailed_comparison']['avg_arguments']['deepseek']:.1f}         {'DeepSeek' if abs(comparison['detailed_comparison']['avg_arguments']['deepseek']-6.5) < abs(comparison['detailed_comparison']['avg_arguments']['groq']-6.5) else 'Groq'}
Ø Zeit/Fakt:        {comparison['detailed_comparison']['avg_generation_time']['groq']:.2f}s      {comparison['detailed_comparison']['avg_generation_time']['deepseek']:.2f}s       {'DeepSeek' if comparison['detailed_comparison']['avg_generation_time']['deepseek'] < comparison['detailed_comparison']['avg_generation_time']['groq'] else 'Groq'}

DOMAIN-SPEZIFISCHE LEISTUNG
{'-'*40}
"""
    
    for domain, perf in comparison["domain_performance"].items():
        report += f"{domain:20} Groq: {perf['groq']}   DeepSeek: {perf['deepseek']}   → {perf['winner']}\n"
    
    report += f"""
BEISPIELE GENERIERTER FAKTEN
{'-'*40}

GROQ - Beste validierte Fakten:
"""
    
    # Sammle beste Groq-Fakten
    groq_valid = []
    for domain_data in groq_results["domains"].values():
        for fact in domain_data["facts"]:
            if fact.get("valid", False):
                groq_valid.append(fact)
    
    groq_valid_sorted = sorted(groq_valid, key=lambda x: x["confidence"], reverse=True)[:3]
    
    for i, fact_data in enumerate(groq_valid_sorted, 1):
        report += f"{i}. {fact_data['fact'][:80]}...\n"
        report += f"   Konfidenz: {fact_data['confidence']:.2f}, Args: {fact_data['arg_count']}\n"
    
    report += f"""
DEEPSEEK - Beste validierte Fakten:
"""
    
    # Sammle beste DeepSeek-Fakten
    deepseek_valid = []
    for domain_data in deepseek_results["domains"].values():
        for fact in domain_data["facts"]:
            if fact.get("valid", False):
                deepseek_valid.append(fact)
    
    deepseek_valid_sorted = sorted(deepseek_valid, key=lambda x: x["confidence"], reverse=True)[:3]
    
    for i, fact_data in enumerate(deepseek_valid_sorted, 1):
        report += f"{i}. {fact_data['fact'][:80]}...\n"
        report += f"   Konfidenz: {fact_data['confidence']:.2f}, Args: {fact_data['arg_count']}\n"
    
    report += f"""
EMPFEHLUNGEN
{'-'*40}
"""
    
    for rec in comparison["recommendations"]:
        report += f"{rec}\n"
    
    report += f"""
{'='*60}
Detaillierte Ergebnisse gespeichert in:
- {OUTPUT_DIR}/groq_{timestamp}.json
- {OUTPUT_DIR}/deepseek_{timestamp}.json
- {OUTPUT_DIR}/comparison_{timestamp}.json
"""
    
    return report


if __name__ == "__main__":
    print("WISSENSCHAFTLICHER LLM-VERGLEICHSTEST")
    print("="*60)
    print(f"Konfiguration: {FACTS_PER_DOMAIN} Fakten/Domain")
    print("Validator: Strikt wissenschaftlich")
    print("Domains:", ", ".join(TEST_DOMAINS.keys()))
    
    # Placeholder API-Funktionen (ersetzen mit echten)
    def groq_api(prompt):
        # TODO: Echter Groq API Call
        return "PlaceholderGroqFact(arg1, arg2, arg3, arg4, arg5, arg6)"
    
    def deepseek_api(prompt):
        # TODO: Echter DeepSeek API Call
        return "PlaceholderDeepSeekFact(arg1, arg2, arg3, arg4, arg5, arg6, arg7)"
    
    print("\n1. Teste Groq...")
    groq_results = run_comprehensive_test("Groq", groq_api)
    
    print("\n2. Teste DeepSeek...")
    deepseek_results = run_comprehensive_test("DeepSeek", deepseek_api)
    
    print("\n3. Vergleiche Ergebnisse...")
    comparison = compare_providers(groq_results, deepseek_results)
    
    # Generiere Bericht
    report = generate_report(groq_results, deepseek_results, comparison)
    print(report)
    
    # Speichere Ergebnisse
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(OUTPUT_DIR / f"groq_{timestamp}.json", "w") as f:
        json.dump(groq_results, f, indent=2)
    
    with open(OUTPUT_DIR / f"deepseek_{timestamp}.json", "w") as f:
        json.dump(deepseek_results, f, indent=2)
    
    with open(OUTPUT_DIR / f"comparison_{timestamp}.json", "w") as f:
        json.dump(comparison, f, indent=2)
    
    with open(OUTPUT_DIR / f"report_{timestamp}.txt", "w") as f:
        f.write(report)
    
    print(f"\n✅ Test abgeschlossen - Ergebnisse in {OUTPUT_DIR}/")
