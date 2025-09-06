#!/usr/bin/env python
"""
Fixed generate_bridge_facts with complex patterns support
"""

def generate_bridge_facts_fixed(self, source: str, target: str, count: int = 8) -> List[str]:
    """
    Generiere Bridge-Fakten MIT komplexen Patterns (2-6 Argumente)
    Kombiniert KB-gestützte 2-stellige UND sinnvolle komplexe Patterns
    """
    facts = []
    
    # TEIL 1: KB-gestützte 2-stellige Fakten (wie bisher)
    # ... existing KB/LLM logic for 2-arg facts ...
    
    # TEIL 2: Sinnvolle komplexe Patterns OHNE Platzhalter
    complex_patterns = []
    
    # Nur für sinnvolle Kombinationen
    if "HAK_GAL" in source or "HAK_GAL" in target:
        # HAK-GAL spezifische komplexe Fakten
        other = target if "HAK_GAL" in source else source
        complex_patterns.extend([
            f"Architecture(HAK_GAL, Hexagonal, REST_API, MCP_Server, {other}).",
            f"System(HAK_GAL, Knowledge_Base, Multi_Agent, API, {other}).",
            f"Process(HAK_GAL, Input, Analysis, Storage, {other})."
        ])
    
    elif "MachineLearning" in source or "MachineLearning" in target:
        # ML-spezifische komplexe Fakten
        other = target if "MachineLearning" in source else source
        complex_patterns.extend([
            f"Algorithm(MachineLearning, Training, Validation, Testing, {other}).",
            f"Process(MachineLearning, Data, Model, Prediction, {other}).",
            f"System(MachineLearning, Input, Processing, Output, {other})."
        ])
    
    else:
        # Generische ABER sinnvolle komplexe Patterns
        # Mit echten Konzepten statt Platzhaldern
        complex_patterns.extend([
            f"Process({source}, Analysis, Synthesis, {target}).",
            f"Mechanism({source}, Interaction, Effect, {target}).",
            f"System({source}, Input, Transformation, {target})."
        ])
    
    # Kombiniere beide Ansätze
    all_candidates = facts + complex_patterns
    
    # Filter durch Cache und QualityGate
    final_facts = []
    for fact in all_candidates[:count]:
        if not self.cache.is_duplicate(fact):
            if self.qgate.passes(fact):
                final_facts.append(fact)
    
    return final_facts
