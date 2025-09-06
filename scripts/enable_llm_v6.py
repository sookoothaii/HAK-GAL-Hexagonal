#!/usr/bin/env python3
"""
Enable LLM in v6_safe_boost
"""

import os
from pathlib import Path

# Set environment to enable LLM
os.environ['V6_USE_LLM'] = 'true'

# Load API keys from HAK_GAL_SUITE
suite_env = Path("D:/MCP Mods/HAK_GAL_SUITE/.env")
if suite_env.exists():
    print("Loading LLM API keys...")
    for line in suite_env.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if 'API_KEY' in key:
                os.environ[key] = val
                print(f"  ✅ {key}")

# Check if v6_safe_boost exists and patch it
v6_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/v6_safe_boost.py")
if v6_file.exists():
    content = v6_file.read_text(encoding='utf-8')
    
    # Add LLM activation at the top if not present
    if 'USE_LLM = ' not in content:
        # Find imports section
        import_section_end = content.find('\n\n', content.find('import '))
        if import_section_end > 0:
            # Add USE_LLM flag
            addition = "\n# LLM Activation\nUSE_LLM = os.environ.get('V6_USE_LLM', 'false').lower() == 'true'\n"
            content = content[:import_section_end] + addition + content[import_section_end:]
            
            # Also ensure LLM is called in score_statement
            if 'llm_score = 0.0' in content:
                content = content.replace(
                    'llm_score = 0.0',
                    'llm_score = get_llm_score(stmt) if USE_LLM else 0.0'
                )
            
            # Save with backup
            v6_file.rename(v6_file.with_suffix('.py.backup_llm'))
            v6_file.write_text(content, encoding='utf-8')
            print("\n✅ v6_safe_boost patched for LLM support")
    else:
        print("\n✅ v6_safe_boost already has LLM support")
else:
    print("⚠️ v6_safe_boost.py not found")

print("\n📝 Instructions:")
print("1. Run: python enable_llm_v6.py")
print("2. Then run: python v6_autopilot_enhanced.py")
print("3. Select option 1 for a quick test")
