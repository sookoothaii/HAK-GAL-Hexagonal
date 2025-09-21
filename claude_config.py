"""
CLAUDE PROVIDER CONFIGURATION UPDATE
Neueste Claude-Modelle für HAK-GAL
"""

# Verfügbare Claude-Modelle (Stand: Januar 2025)
CLAUDE_MODELS = {
    # Neueste und beste Modelle
    "primary": [
        "claude-3-5-sonnet-20241022",  # Neuestes Sonnet (Oktober 2024)
        "claude-3-5-haiku-20241022",   # Schnellstes Modell
    ],
    
    # Fallback-Modelle
    "fallback": [
        "claude-3-opus-20240229",      # Stärkstes Modell (aber langsamer)
        "claude-3-sonnet-20240229",    # Ausgewogen
        "claude-3-haiku-20240307",     # Schnell und günstig
    ],
    
    # Legacy (nur wenn nichts anderes geht)
    "legacy": [
        "claude-2.1",
        "claude-2.0",
        "claude-instant-1.2"
    ]
}

# Optimale Einstellungen für wissenschaftliche Fakten
CLAUDE_CONFIG = {
    "api_base": "https://api.anthropic.com/v1",
    "headers": {
        "anthropic-version": "2023-06-01",  # Neueste API-Version
        "anthropic-beta": "messages-2023-12-15"  # Beta Features
    },
    "default_model": "claude-3-5-sonnet-20241022",
    "timeout": 45,  # Erhöht von 30
    "max_tokens": 200,  # Für 6-7 Argument Fakten
    "temperature": 0.1,  # Sehr niedrig für Präzision
    "system_prompt": """You are a scientific fact generator creating ONLY scientifically accurate facts.
Each fact MUST have exactly 6-7 arguments.
Include proper units (C, K, atm, m/s, eV).
Follow conservation laws strictly.
Output format: Predicate(arg1, arg2, arg3, arg4, arg5, arg6, arg7)"""
}

# Update für MultiLLM Chain
MULTILLM_CLAUDE_CONFIG = {
    "provider": "claude",
    "models": [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229"
    ],
    "retry_on_error": True,
    "max_retries": 2,
    "timeout_per_try": 45,
    "use_streaming": False,  # Für bessere Stabilität
    "error_handling": "fallback_to_next"
}
