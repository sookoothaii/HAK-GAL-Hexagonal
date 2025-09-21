#!/usr/bin/env python3
"""
HAK_GAL MCP Server mit n-ären Fact Patches
Dies ist ein Wrapper der die gepatchten Tools lädt
"""

import sys
import os

# Füge scripts zum Path hinzu BEVOR wir den Server laden
sys.path.insert(0, r'D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts')
sys.path.insert(0, r'D:\MCP Mods\HAK_GAL_HEXAGONAL')

print("Loading n-ary fact patches...")

# Importiere und aktiviere Patches
try:
    from fix_nary_tools import FixedNaryTools
    from mcp_nary_patches import (
        semantic_similarity_nary, 
        consistency_check_nary,
        validate_facts_nary,
        inference_chain_nary
    )
    
    print("✓ N-ary fact patches loaded successfully")
    
    # Monkey-patch die Funktionen direkt ins globale Namespace
    import builtins
    builtins.semantic_similarity_fixed = semantic_similarity_nary
    builtins.consistency_check_fixed = consistency_check_nary
    builtins.validate_facts_fixed = validate_facts_nary
    builtins.inference_chain_fixed = inference_chain_nary
    builtins.NARY_PATCHES_AVAILABLE = True
    
    print("✓ Patches registered globally")
    
except ImportError as e:
    print(f"Warning: Could not load n-ary patches: {e}")
    import builtins
    builtins.NARY_PATCHES_AVAILABLE = False

# Lade und modifiziere den Server Code BEVOR Ausführung
print("Loading HAK_GAL MCP Server...")

with open(r'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\hakgal_mcp_ultimate.py', 'r', encoding='utf-8') as f:
    server_code = f.read()

# Injiziere Patch-Handler in den Server Code
patch_injection = '''
# === INJECTED N-ARY PATCHES ===
if 'NARY_PATCHES_AVAILABLE' in dir(__builtins__) and __builtins__.NARY_PATCHES_AVAILABLE:
    print("Activating n-ary patches in server...")
    _original_semantic_similarity = globals().get('semantic_similarity', None)
    _original_consistency_check = globals().get('consistency_check', None)
    _original_validate_facts = globals().get('validate_facts', None)
    _original_inference_chain = globals().get('inference_chain', None)
    
    # Override mit gepatchten Versionen
    async def semantic_similarity_override(*args, **kwargs):
        if hasattr(__builtins__, 'semantic_similarity_fixed'):
            return await __builtins__.semantic_similarity_fixed(*args, **kwargs)
        elif _original_semantic_similarity:
            return await _original_semantic_similarity(*args, **kwargs)
        return "Tool not available"
    
    async def consistency_check_override(*args, **kwargs):
        if hasattr(__builtins__, 'consistency_check_fixed'):
            return await __builtins__.consistency_check_fixed(*args, **kwargs)
        elif _original_consistency_check:
            return await _original_consistency_check(*args, **kwargs)
        return "Tool not available"
    
    # Registriere Overrides
    globals()['semantic_similarity'] = semantic_similarity_override
    globals()['consistency_check'] = consistency_check_override
    print("✓ N-ary patches activated in server")
# === END INJECTED PATCHES ===

'''

# Füge Injection nach den Imports aber vor main() ein
import_end = server_code.rfind('async def main()')
if import_end > 0:
    server_code = server_code[:import_end] + patch_injection + server_code[import_end:]

# Führe modifizierten Code aus
exec(server_code)
