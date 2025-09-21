"""
Advanced Temperature Profiles for Different Tasks
"""
from pathlib import Path
import json
import sys

PROFILES = {
    "factual": {
        "name": "Factual/Scientific (Recommended for HAK-GAL)",
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 40,
        "repeat_penalty": 1.1,
        "seed": 42,
        "description": "Minimizes hallucinations, best for facts"
    },
    "deterministic": {
        "name": "Fully Deterministic",
        "temperature": 0.0,
        "top_p": 1.0,
        "top_k": 1,
        "repeat_penalty": 1.0,
        "seed": 42,
        "description": "Always same output (may be repetitive)"
    },
    "balanced": {
        "name": "Balanced",
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 50,
        "repeat_penalty": 1.05,
        "seed": None,
        "description": "Balance between creativity and accuracy"
    },
    "creative": {
        "name": "Creative (NOT for facts!)",
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 100,
        "repeat_penalty": 1.0,
        "seed": None,
        "description": "For stories, brainstorming (will hallucinate!)"
    },
    "focused": {
        "name": "Ultra-Focused",
        "temperature": 0.05,
        "top_p": 0.8,
        "top_k": 20,
        "repeat_penalty": 1.2,
        "seed": 42,
        "description": "Extremely conservative, minimal variation"
    }
}

def apply_profile(profile_name):
    """Apply a temperature profile to ollama_adapter.py"""
    
    if profile_name not in PROFILES:
        print(f"❌ Unknown profile: {profile_name}")
        print(f"Available: {', '.join(PROFILES.keys())}")
        return False
    
    profile = PROFILES[profile_name]
    adapter_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/adapters/ollama_adapter.py")
    
    if not adapter_file.exists():
        print(f"❌ File not found: {adapter_file}")
        return False
    
    content = adapter_file.read_text(encoding='utf-8')
    
    # Build new options string
    options_str = '"options": {\n'
    options_str += f'                    "temperature": {profile["temperature"]},\n'
    options_str += f'                    "top_p": {profile["top_p"]},\n'
    options_str += f'                    "top_k": {profile["top_k"]},\n'
    options_str += f'                    "repeat_penalty": {profile["repeat_penalty"]},\n'
    if profile["seed"] is not None:
        options_str += f'                    "seed": {profile["seed"]},\n'
    options_str += '                    "num_predict": 1500\n'
    options_str += '                }'
    
    # Replace options block
    import re
    pattern = r'"options":\s*\{[^}]+\}'
    content = re.sub(pattern, options_str, content)
    
    adapter_file.write_text(content, encoding='utf-8')
    
    print(f"✅ Applied profile: {profile['name']}")
    print(f"   {profile['description']}")
    print(f"\nSettings:")
    print(f"  Temperature: {profile['temperature']}")
    print(f"  Top-P: {profile['top_p']}")
    print(f"  Top-K: {profile['top_k']}")
    print(f"  Repeat Penalty: {profile['repeat_penalty']}")
    if profile['seed']:
        print(f"  Seed: {profile['seed']} (deterministic)")
    
    return True

def main():
    print("=" * 60)
    print("OLLAMA TEMPERATURE PROFILE MANAGER")
    print("=" * 60)
    print("\nAvailable Profiles:\n")
    
    for key, profile in PROFILES.items():
        print(f"{key:15} - {profile['name']}")
        print(f"{'':15}   Temperature: {profile['temperature']}, Top-P: {profile['top_p']}")
        print(f"{'':15}   {profile['description']}")
        print()
    
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Command line argument
        profile = sys.argv[1]
    else:
        # Interactive
        print("\nRecommended for HAK-GAL: 'factual' or 'focused'")
        profile = input("\nSelect profile [factual/deterministic/balanced/creative/focused]: ").strip()
        
        if not profile:
            profile = "factual"
            print(f"Using default: {profile}")
    
    if apply_profile(profile):
        print("\n" + "=" * 60)
        print("SUCCESS! Restart API for changes to take effect.")
        print("=" * 60)
    else:
        print("\n❌ Failed to apply profile")

if __name__ == "__main__":
    main()
