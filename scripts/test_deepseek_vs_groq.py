#!/usr/bin/env python3
"""
DEEPSEEK vs GROQ - Faktengenerierung Vergleichstest
Testet welches LLM bessere wissenschaftliche Fakten mit 6-7 Argumenten generiert
"""

import json
import os
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Provider einbinden
from src_hexagonal.adapters.llm_providers import GroqProvider, DeepSeekProvider, MultiLLMProvider

TEST_DOMAINS = [
    "CHEMISTRY",
    "PHYSICS", 
    "BIOLOGY",
    "COMPUTER_SCIENCE",
    "MATHEMATICS"
]

# Beispiel-Prompts für komplexe Fakten (6-7 Argumente)
FACT_GENERATION_PROMPTS = {
    "CHEMISTRY": """
    Generate a scientifically accurate fact about chemical reactions with 6-7 arguments.
    Format: Predicate(arg1, arg2, arg3, arg4, arg5, arg6, [arg7])
    
    Example patterns:
    - ChemicalReaction(reactant1, reactant2, product1, product2, catalyst, temperature, pressure)
    - MolecularStructure(compound, centralAtom, ligand1, ligand2, ligand3, geometry, hybridization)
    
    The fact must be scientifically correct and verifiable.
    Return ONLY the fact, no explanation.
    """,
    
    "PHYSICS": """
    Generate a scientifically accurate physics fact with 6-7 arguments.
    Format: Predicate(arg1, arg2, arg3, arg4, arg5, arg6, [arg7])
    
    Example patterns:
    - ElectromagneticWave(wavelength, frequency, energy, amplitude, polarization, medium, speed)
    - ParticleInteraction(particle1, particle2, force, energy, momentum, spin, charge)
    
    The fact must follow known physics laws.
    Return ONLY the fact, no explanation.
    """,
    
    "BIOLOGY": """
    Generate a scientifically accurate biology fact with 6-7 arguments.
    Format: Predicate(arg1, arg2, arg3, arg4, arg5, arg6, [arg7])
    
    Example patterns:
    - ProteinSynthesis(gene, mRNA, ribosome, tRNA, aminoAcid, protein, location)
    - EcosystemInteraction(producer, primaryConsumer, secondaryConsumer, decomposer, energy, nutrients, habitat)
    
    The fact must be biologically accurate.
    Return ONLY the fact, no explanation.
    """,
    
    "COMPUTER_SCIENCE": """
    Generate a technically accurate computer science fact with 6-7 arguments.
    Format: Predicate(arg1, arg2, arg3, arg4, arg5, arg6, [arg7])
    
    Example patterns:
    - NetworkProtocol(layer, protocol, sourcePort, destPort, payload, checksum, flags)
    - AlgorithmComplexity(algorithm, bestCase, averageCase, worstCase, spaceComplexity, dataStructure, operation)
    
    The fact must be technically correct.
    Return ONLY the fact, no explanation.
    """
}

# Validierungsprompt für generierte Fakten
VALIDATION_PROMPT = """
Evaluate this fact for scientific/technical accuracy:
{fact}

Respond with JSON:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["list of problems if any"],
    "corrected_fact": "corrected version if needed"
}}
"""

def extract_fact(text: str) -> str:
    """Extrahiert die erste Zeile im Format Predicate(...). Entfernt Codefences/Erklärungen."""
    if not text:
        return ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # Entferne Codefences, Markdown
    lines = [ln for ln in lines if not (ln.startswith("```") or ln.endswith("```"))]
    for ln in lines:
        if "(" in ln and ")" in ln:
            return ln.rstrip(";.") + "."
    # Fallback auf erste Zeile
    return lines[0] if lines else ""

# Lokale Validierungs-Hilfen
PREDICATE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def parse_statement(fact: str) -> tuple[str, list[str]]:
    """Parst Predicate(args...) zu (predicate, [args]) oder ("", [])."""
    if not fact or "(" not in fact or not fact.endswith(")"):
        return "", []
    i = fact.find("(")
    predicate = fact[:i].strip()
    inner = fact[i+1:-1]
    args = [a.strip() for a in inner.split(",") if a.strip()]
    return predicate, args

def test_llm_fact_generation(llm_name: str, api_function, prompts: Dict) -> Dict:
    """
    Testet ein LLM auf Faktengenerierung
    """
    results = {
        "llm": llm_name,
        "timestamp": time.time(),
        "domains": {},
        "metrics": {
            "total_generated": 0,
            "valid_facts": 0,
            "invalid_facts": 0,
            "avg_confidence": 0.0,
            "avg_arguments": 0.0,
            "generation_time": 0.0
        }
    }
    
    for domain, prompt in prompts.items():
        print(f"\nTesting {llm_name} on {domain}...")
        domain_results = {
            "facts": [],
            "validation": []
        }
        
        # Anzahl pro Domain via ENV konfigurierbar (Default: 2)
        facts_per_domain = int(os.environ.get("FACTS_PER_DOMAIN", "2"))
        for i in range(facts_per_domain):
            start = time.time()
            
            try:
                # Generiere Fakt
                fact_text = api_function(prompt)
                fact = extract_fact(fact_text)
                generation_time = time.time() - start
                
                # Zähle Argumente
                arg_count = fact.count(',') + 1
                
                # Validiere Fakt (mit anderem LLM für Objektivität)
                validation = validate_fact(fact)
                
                domain_results["facts"].append({
                    "fact": fact,
                    "arg_count": arg_count,
                    "generation_time": generation_time,
                    "valid": validation["is_valid"],
                    "confidence": validation["confidence"],
                    "issues": validation.get("issues", [])
                })
                
                # Update Metriken
                results["metrics"]["total_generated"] += 1
                if validation["is_valid"]:
                    results["metrics"]["valid_facts"] += 1
                else:
                    results["metrics"]["invalid_facts"] += 1
                    
                results["metrics"]["avg_arguments"] += arg_count
                results["metrics"]["avg_confidence"] += validation["confidence"]
                results["metrics"]["generation_time"] += generation_time
                
            except Exception as e:
                print(f"  Error: {e}")
                domain_results["facts"].append({
                    "error": str(e)
                })
        
        results["domains"][domain] = domain_results
    
    # Berechne Durchschnitte
    if results["metrics"]["total_generated"] > 0:
        results["metrics"]["avg_arguments"] /= results["metrics"]["total_generated"]
        results["metrics"]["avg_confidence"] /= results["metrics"]["total_generated"]
        results["metrics"]["accuracy_rate"] = results["metrics"]["valid_facts"] / results["metrics"]["total_generated"]
    
    return results

def validate_fact(fact: str) -> Dict:
    """Validiert einen Fakt via Multi-LLM (Groq→DeepSeek→Gemini→Claude→Ollama) und lokalen Regeln."""
    try:
        validator = MultiLLMProvider()
        schema_str = '{"is_valid": true|false, "confidence": number, "issues": [], "corrected_fact": string|null}'
        payload = (
            "Respond ONLY with JSON (no code fences, no prose). Schema: "
            + schema_str + "\n" + VALIDATION_PROMPT.format(fact=fact)
        )
        resp_text, _ = validator.generate_response(payload)
        data = json.loads(resp_text)
        is_valid = bool(data.get("is_valid", False))
        conf = float(data.get("confidence", 0.0))
        issues = data.get("issues", []) or []

        # Lokale Plausibilitätsprüfung: 6–7 Argumente und gültiges Prädikat-Token
        pred, args = parse_statement(fact)
        local_ok = bool(PREDICATE_RE.match(pred)) and (6 <= len(args) <= 7)
        if not local_ok:
            issues.append("local_rule_violation: predicate_or_argcount")
            is_valid = False
            conf = min(conf, 0.5)
        return {"is_valid": is_valid, "confidence": conf, "issues": issues}
    except Exception:
        return {"is_valid": False, "confidence": 0.0, "issues": ["validator_error_or_non_json"]}

def compare_llms(results_groq: Dict, results_deepseek: Dict) -> Dict:
    """
    Vergleicht die Ergebnisse beider LLMs
    """
    comparison = {
        "winner": None,
        "summary": {},
        "recommendations": []
    }
    
    # Vergleiche Metriken
    metrics_comparison = {
        "accuracy": {
            "groq": results_groq["metrics"].get("accuracy_rate", 0),
            "deepseek": results_deepseek["metrics"].get("accuracy_rate", 0)
        },
        "avg_confidence": {
            "groq": results_groq["metrics"]["avg_confidence"],
            "deepseek": results_deepseek["metrics"]["avg_confidence"]
        },
        "avg_arguments": {
            "groq": results_groq["metrics"]["avg_arguments"],
            "deepseek": results_deepseek["metrics"]["avg_arguments"]
        },
        "speed": {
            "groq": results_groq["metrics"]["generation_time"],
            "deepseek": results_deepseek["metrics"]["generation_time"]
        }
    }
    
    # Bestimme Gewinner
    groq_score = 0
    deepseek_score = 0
    
    # Accuracy ist am wichtigsten (Gewicht 3)
    if metrics_comparison["accuracy"]["groq"] > metrics_comparison["accuracy"]["deepseek"]:
        groq_score += 3
    else:
        deepseek_score += 3
    
    # Confidence (Gewicht 2)
    if metrics_comparison["avg_confidence"]["groq"] > metrics_comparison["avg_confidence"]["deepseek"]:
        groq_score += 2
    else:
        deepseek_score += 2
    
    # Argument Count - näher an 6-7 ist besser (Gewicht 1)
    groq_distance = abs(metrics_comparison["avg_arguments"]["groq"] - 6.5)
    deepseek_distance = abs(metrics_comparison["avg_arguments"]["deepseek"] - 6.5)
    if groq_distance < deepseek_distance:
        groq_score += 1
    else:
        deepseek_score += 1
    
    comparison["winner"] = "DeepSeek" if deepseek_score > groq_score else "Groq"
    comparison["scores"] = {"groq": groq_score, "deepseek": deepseek_score}
    comparison["metrics"] = metrics_comparison
    
    # Empfehlungen
    if metrics_comparison["accuracy"]["deepseek"] > metrics_comparison["accuracy"]["groq"]:
        comparison["recommendations"].append(
            "DeepSeek zeigt höhere Genauigkeit - für wissenschaftliche Fakten empfohlen"
        )
    
    if metrics_comparison["avg_arguments"]["deepseek"] > 5.5:
        comparison["recommendations"].append(
            "DeepSeek generiert erfolgreich komplexe Fakten mit 6+ Argumenten"
        )
    
    return comparison

def generate_report(results_groq: Dict, results_deepseek: Dict, comparison: Dict):
    """
    Generiert einen detaillierten Vergleichsbericht
    """
    report = f"""
DEEPSEEK vs GROQ - FAKTENGENERIERUNG VERGLEICHSTEST
{'='*60}

ZUSAMMENFASSUNG
{'-'*40}
Gewinner: {comparison['winner']}
Punkte: Groq {comparison['scores']['groq']} - DeepSeek {comparison['scores']['deepseek']}

METRIKEN VERGLEICH
{'-'*40}
                    Groq        DeepSeek    Besser
Genauigkeit:        {comparison['metrics']['accuracy']['groq']:.1%}      {comparison['metrics']['accuracy']['deepseek']:.1%}       {'DeepSeek' if comparison['metrics']['accuracy']['deepseek'] > comparison['metrics']['accuracy']['groq'] else 'Groq'}
Konfidenz:          {comparison['metrics']['avg_confidence']['groq']:.2f}        {comparison['metrics']['avg_confidence']['deepseek']:.2f}         {'DeepSeek' if comparison['metrics']['avg_confidence']['deepseek'] > comparison['metrics']['avg_confidence']['groq'] else 'Groq'}
Ø Argumente:        {comparison['metrics']['avg_arguments']['groq']:.1f}        {comparison['metrics']['avg_arguments']['deepseek']:.1f}         {'DeepSeek' if abs(comparison['metrics']['avg_arguments']['deepseek']-6.5) < abs(comparison['metrics']['avg_arguments']['groq']-6.5) else 'Groq'}
Geschwindigkeit:    {comparison['metrics']['speed']['groq']:.2f}s      {comparison['metrics']['speed']['deepseek']:.2f}s       {'DeepSeek' if comparison['metrics']['speed']['deepseek'] < comparison['metrics']['speed']['groq'] else 'Groq'}

EMPFEHLUNGEN
{'-'*40}
"""
    
    for rec in comparison['recommendations']:
        report += f"• {rec}\n"
    
    # Beispiele guter Fakten
    report += f"""
BEISPIELE GENERIERTER FAKTEN
{'-'*40}

GROQ - Beste Fakten:
"""
    # Zeige die besten 3 Fakten von Groq
    groq_facts = []
    for domain_data in results_groq["domains"].values():
        groq_facts.extend(domain_data["facts"])
    
    groq_facts_sorted = sorted(
        [f for f in groq_facts if "fact" in f and f.get("valid", False)],
        key=lambda x: x["confidence"],
        reverse=True
    )[:3]
    
    for i, fact_data in enumerate(groq_facts_sorted, 1):
        report += f"{i}. {fact_data['fact']}\n   (Konfidenz: {fact_data['confidence']:.2f}, Args: {fact_data['arg_count']})\n"
    
    report += f"""
DEEPSEEK - Beste Fakten:
"""
    # Zeige die besten 3 Fakten von DeepSeek
    deepseek_facts = []
    for domain_data in results_deepseek["domains"].values():
        deepseek_facts.extend(domain_data["facts"])
    
    deepseek_facts_sorted = sorted(
        [f for f in deepseek_facts if "fact" in f and f.get("valid", False)],
        key=lambda x: x["confidence"],
        reverse=True
    )[:3]
    
    for i, fact_data in enumerate(deepseek_facts_sorted, 1):
        report += f"{i}. {fact_data['fact']}\n   (Konfidenz: {fact_data['confidence']:.2f}, Args: {fact_data['arg_count']})\n"
    
    return report

if __name__ == "__main__":
    print("STARTE DEEPSEEK vs GROQ VERGLEICHSTEST")
    print("="*60)
    
    # Provider-Initialisierung
    groq_provider = GroqProvider()
    deepseek_provider = DeepSeekProvider()

    def groq_generate(prompt: str) -> str:
        text, _ = groq_provider.generate_response(prompt)
        return text

    def deepseek_generate(prompt: str) -> str:
        text, _ = deepseek_provider.generate_response(prompt)
        return text
    
    # Führe Tests durch
    print("\n1. Teste Groq...")
    results_groq = test_llm_fact_generation("Groq", groq_generate, FACT_GENERATION_PROMPTS)
    
    print("\n2. Teste DeepSeek...")
    results_deepseek = test_llm_fact_generation("DeepSeek", deepseek_generate, FACT_GENERATION_PROMPTS)
    
    print("\n3. Vergleiche Ergebnisse...")
    comparison = compare_llms(results_groq, results_deepseek)
    
    # Generiere Bericht
    report = generate_report(results_groq, results_deepseek, comparison)
    print(report)
    
    # Speichere Ergebnisse versioniert
    out_dir = Path("validation_results/llm_runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"llm_comparison_results_{ts}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "groq": results_groq,
            "deepseek": results_deepseek,
            "comparison": comparison
        }, f, indent=2, ensure_ascii=False)

    print(f"\nErgebnisse gespeichert in {out_file}")
