#!/usr/bin/env python3
"""
Force reload the optimized generator and clear Python cache
"""
import sys
import os
import importlib
from pathlib import Path

print("="*60)
print("FORCE RELOAD OPTIMIZED GENERATOR")
print("="*60)

# 1. Clear Python cache for the module
module_names = [
    'llm_governor_generator',
    'infrastructure.engines.simple_fact_generator',
    'simple_fact_generator'
]

for mod_name in module_names:
    if mod_name in sys.modules:
        del sys.modules[mod_name]
        print(f"✅ Cleared cache for: {mod_name}")

# 2. Force Python to reload from disk
import importlib
importlib.invalidate_caches()
print("✅ Invalidated Python import caches")

# 3. Test import of the optimized generator
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal")
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\infrastructure\engines")

try:
    from llm_governor_generator import LLMGovernorWithGenerator
    
    # Test that it's the optimized version
    gov = LLMGovernorWithGenerator()
    
    # Check if it uses the optimized SimpleFactGenerator
    if hasattr(gov, 'generator'):
        print("✅ Using optimized SimpleFactGenerator")
        
        # Check for balanced predicates
        if hasattr(gov.generator, 'predicates'):
            has_prop_weight = gov.generator.predicates.get('HasProperty', 1.0)
            print(f"✅ HasProperty weight: {has_prop_weight*100:.0f}% (should be 20%)")
            
            if has_prop_weight <= 0.25:
                print("✅ OPTIMIZED GENERATOR CONFIRMED!")
            else:
                print("⚠️ Still using old generator weights")
    else:
        print("⚠️ Not using SimpleFactGenerator")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("1. Restart the backend server")
print("2. You should see: '[LLM Governor] Started with OPTIMIZED fact generation'")
print("3. Monitor with: python scripts\\monitor_generation.py")
print("="*60)
