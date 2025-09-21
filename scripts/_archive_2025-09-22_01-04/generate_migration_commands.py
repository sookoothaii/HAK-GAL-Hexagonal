#!/usr/bin/env python3
"""
Complete Entity Migration: German to English
Identifies and fixes all German entities in the knowledge base
"""

import json
import re
from typing import List, Tuple

# Complete list of German entities to migrate
GERMAN_TO_ENGLISH = {
    # Found in KB analysis
    "Phänomene": "Phenomena",
    "WahrgenommeneWelt": "PerceivedWorld",
    "Ästhetik": "Aesthetics",
    "SubjektiveAberUniversellKommunizierbareSchönheit": "SubjectiveButUniversallyCommunicableBeauty",
    "UnerkennbareRealität": "UnknowableReality",
    "KritischeTheorie": "CriticalTheory",
    "ModernerPhilosophie": "ModernPhilosophy",
    "KritischePhilosophie": "CriticalPhilosophy",
    "AutonomieDerVernunft": "AutonomyOfReason",
    "ModerneEpistemologie": "ModernEpistemology",
    "ModerneEthik": "ModernEthics",
    "SpätereDenker": "LaterThinkers",
    "SelbstgegebenenVernunftgesetzen": "SelfGivenReasonLaws",
    "WissenBeginntMitErfahrung": "KnowledgeBeginsWithExperience",
    "MoralischePflichtEntstehtAusSelbstgegebenenVernunftgesetzen": "MoralDutyArisesFromSelfGivenReasonLaws",
    "EinflussAufSpätereDenker": "InfluenceOnLaterThinkers",
    "WurzelInInteresselosemVergnügen": "RootedInDisinterestedPleasure",
    "Ethik": "Ethics",
    "Metaphysik": "Metaphysics",
    "Epistemologie": "Epistemology",
    "KantIdeen": "KantIdeas"
}

# Facts that need to be replaced entirely
FACTS_TO_REPLACE = [
    # Format: (old_statement, new_statement)
    ("IsDefinedAs(Phänomene, WahrgenommeneWelt).", 
     "IsDefinedAs(Phenomena, PerceivedWorld)."),
    
    ("IsDefinedAs(Ästhetik, SubjektiveAberUniversellKommunizierbareSchönheit).", 
     "IsDefinedAs(Aesthetics, SubjectiveButUniversallyCommunicableBeauty)."),
    
    ("IsDefinedAs(Noumena, UnerkennbareRealität).", 
     "IsDefinedAs(Noumena, UnknowableReality)."),
    
    ("IsSimilarTo(KantIdeen, KritischeTheorie).", 
     "IsSimilarTo(KantIdeas, CriticalTheory)."),
    
    ("ConsistsOf(ModernerPhilosophie, Ethik).", 
     "ConsistsOf(ModernPhilosophy, Ethics)."),
    
    ("IsSimilarTo(KantIdeen, ModerneEpistemologie).", 
     "IsSimilarTo(KantIdeas, ModernEpistemology)."),
    
    ("HasProperty(KantIdeen, EinflussAufSpätereDenker).", 
     "HasProperty(KantIdeas, InfluenceOnLaterThinkers)."),
    
    ("ConsistsOf(ModernerPhilosophie, Metaphysik).", 
     "ConsistsOf(ModernPhilosophy, Metaphysics)."),
    
    ("ConsistsOf(ModernerPhilosophie, Epistemologie).", 
     "ConsistsOf(ModernPhilosophy, Epistemology)."),
    
    ("HasProperty(KritischePhilosophie, WissenBeginntMitErfahrung).", 
     "HasProperty(CriticalPhilosophy, KnowledgeBeginsWithExperience)."),
    
    ("HasProperty(AutonomieDerVernunft, MoralischePflichtEntstehtAusSelbstgegebenenVernunftgesetzen).", 
     "HasProperty(AutonomyOfReason, MoralDutyArisesFromSelfGivenReasonLaws)."),
    
    ("IsSimilarTo(KantIdeen, ModerneEthik).", 
     "IsSimilarTo(KantIdeas, ModernEthics)."),
    
    ("HasProperty(Ästhetik, WurzelInInteresselosemVergnügen).", 
     "HasProperty(Aesthetics, RootedInDisinterestedPleasure)."),
    
    # Fix logical quantor
    ("all x (IsHuman(x) -> IsMortal(x)).", 
     "ImpliesUniversally(IsHuman, IsMortal).")
]

def create_migration_script():
    """Generate MCP commands to migrate German entities"""
    
    print("#!/bin/bash")
    print("# Entity Migration Script - German to English")
    print("# Generated from statistical analysis")
    print("")
    print("# Delete German facts and add English replacements")
    
    for old_fact, new_fact in FACTS_TO_REPLACE:
        # Escape quotes for shell
        old_escaped = old_fact.replace('"', '\\"')
        new_escaped = new_fact.replace('"', '\\"')
        
        print(f'echo "Migrating: {old_fact[:50]}..."')
        print(f'# Delete old German fact')
        print(f'curl -X POST http://localhost:5000/api/command \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"command": "delete_fact", "statement": "{old_escaped}", "auth_token": "515f57956e7bd15ddc3817573598f190"}}\'')
        print()
        print(f'# Add new English fact')
        print(f'curl -X POST http://localhost:5000/api/command \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"command": "add_fact", "statement": "{new_escaped}", "source": "entity_migration", "tags": ["migration", "english"]}}\'')
        print()
    
    print("echo 'Migration complete!'")

if __name__ == "__main__":
    create_migration_script()
