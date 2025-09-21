#!/usr/bin/env python3
"""
UPDATE: Neueste Claude 4.x Modelle für HAK-GAL
Basierend auf tatsächlich verfügbaren Modellen
"""

import json

# AKTUELLE Claude-Modelle (Januar 2025)
CLAUDE_4_MODELS = {
    "newest": [
        "claude-opus-4-1-20250805",     # Opus 4.1 - Neuestes und stärkstes
        "claude-opus-4-20240729",       # Opus 4
        "claude-sonnet-4-20240620",     # Sonnet 4
        "claude-sonnet-3-7-20240307",   # Sonnet 3.7
    ],
    
    "all_available": [
        # 4.x Serie
        "claude-opus-4-1-20250805",
        "claude-opus-4-20240729", 
        "claude-sonnet-4-20240620",
        
        # 3.7
        "claude-sonnet-3-7-20240307",
        
        # 3.5 Serie (älter aber stabil)
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        
        # 3.0 Serie
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]
}

def update_to_claude_4():
    """
    Aktualisiert die LLM-Config auf Claude 4.x Modelle
    """
    
    config = {
        "version": "4.0",
        "updated": "2025-01-18",
        
        # Claude 4.x als Primär-Provider
        "provider_chain": [
            "claude",      # PRIMÄR - Claude 4.x
            "gemini",      # Sekundär 
            "deepseek",    
            "groq",        
            "ollama"       
        ],
        
        "claude": {
            "enabled": True,
            "models": [
                "claude-opus-4-1-20250805",     # PRIMÄR: Opus 4.1
                "claude-opus-4-20240729",       # Fallback: Opus 4
                "claude-sonnet-4-20240620",     # Fallback: Sonnet 4  
                "claude-sonnet-3-7-20240307",   # Fallback: Sonnet 3.7
                "claude-3-5-sonnet-20241022"    # Letzter Fallback
            ],
            "default_model": "claude-opus-4-1-20250805",
            "api_version": "2023-06-01",
            "timeout": 60,  # Erhöht für Opus 4.1
            "max_retries": 3,
            "temperature": 0.1,  # Präzision für wissenschaftliche Fakten
            "max_tokens": 250,  # Mehr für komplexe 7-Argument-Fakten
            "system_message": """You are Claude Opus 4.1, generating ONLY scientifically accurate facts.
Each fact MUST have exactly 6-7 arguments.
Include proper units (C, K, atm, Pa, m/s, eV, J).
Follow ALL conservation laws (mass, energy, momentum, charge).
Use only validated scientific data.
Output format: Predicate(arg1, arg2, arg3, arg4, arg5, arg6, arg7)
NO explanations, ONLY the fact."""
        },
        
        # Andere Provider als Fallback
        "gemini": {
            "enabled": True,
            "models": ["gemini-2.0-flash-exp"],
            "timeout": 30,
            "temperature": 0.1
        },
        
        "deepseek": {
            "enabled": True,
            "models": ["deepseek-chat"],
            "timeout": 30,
            "temperature": 0.1
        },
        
        "groq": {
            "enabled": True,
            "models": ["mixtral-8x7b-32768"],
            "timeout": 25,
            "temperature": 0.1
        },
        
        # Globale Einstellungen für wissenschaftliche Fakten
        "global": {
            "scientific_mode": True,
            "min_arguments": 6,
            "max_arguments": 7,
            "validation_mode": "strict",
            "require_units": True,
            "require_conservation": True,
            "reject_vague": True,
            "reject_person_names_as_args": True,
            "preferred_domains": [
                "CHEMISTRY",
                "PHYSICS", 
                "BIOLOGY",
                "MATHEMATICS",
                "COMPUTER_SCIENCE"
            ]
        }
    }
    
    # Speichere Config
    paths = [
        "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\llm_config.json",
        "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal\\llm_config.json"
    ]
    
    for path in paths:
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Claude 4.x Config gespeichert: {path}")
    
    print("\n" + "="*60)
    print("✅ UPGRADE AUF CLAUDE 4.x MODELLE KOMPLETT")
    print("-"*40)
    print("Primär-Modell: Claude Opus 4.1")
    print("Fallback-Kette: Opus 4 → Sonnet 4 → Sonnet 3.7")
    print("\nBackend neu starten für Aktivierung:")
    print("  python hexagonal_api_enhanced_clean.py")
    
    return config

if __name__ == "__main__":
    update_to_claude_4()
