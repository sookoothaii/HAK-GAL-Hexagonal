#!/usr/bin/env python3
"""
Fix the provider initialization to use ONLY DeepSeek
This modifies hexagonal_api_enhanced_clean.py
"""

from pathlib import Path
import shutil

def fix_providers_deepseek_only():
    """Modify the API file to use only DeepSeek"""
    
    print("🔧 FIXING PROVIDER INITIALIZATION FOR DEEPSEEK-ONLY")
    print("="*60)
    
    api_file = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py")
    
    # Backup
    backup = api_file.with_suffix('.py.backup_original')
    if not backup.exists():
        shutil.copy2(api_file, backup)
        print(f"✅ Backup created: {backup.name}")
    
    # Read content
    content = api_file.read_text(encoding='utf-8')
    
    # Replace the provider initialization section
    old_block = """                providers = [
                    GeminiProvider(),     # Gemini FIRST - verified working
                    DeepSeekProvider(),   # DeepSeek as fallback
                    # MistralProvider() removed - 401 Unauthorized
                ]"""
    
    new_block = """                # DEEPSEEK-ONLY MODE (no Gemini)
                # Check for DeepSeek API key
                if os.environ.get('DEEPSEEK_API_KEY'):
                    providers = [
                        DeepSeekProvider(),   # DeepSeek ONLY
                        # GeminiProvider() - DISABLED (no API key)
                    ]
                    print("[LLM] Using DeepSeek provider only")
                else:
                    providers = []
                    print("[LLM] WARNING: No DeepSeek API key found!")"""
    
    if old_block in content:
        content = content.replace(old_block, new_block)
        api_file.write_text(content, encoding='utf-8')
        print("✅ Provider initialization fixed!")
        print("\n📝 Changes made:")
        print("  • GeminiProvider removed")
        print("  • DeepSeekProvider is the ONLY provider")
        print("  • Added check for DEEPSEEK_API_KEY")
        return True
    else:
        print("⚠️ Provider block not found in expected format")
        print("Trying alternative fix...")
        
        # Alternative: Find and replace line by line
        if "GeminiProvider()" in content:
            lines = content.split('\n')
            new_lines = []
            in_provider_block = False
            
            for i, line in enumerate(lines):
                # Look for the providers initialization
                if "providers = [" in line:
                    in_provider_block = True
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(line)
                    new_lines.append(' ' * (indent + 4) + "# DEEPSEEK-ONLY MODE")
                elif in_provider_block:
                    if "GeminiProvider()" in line:
                        # Comment out Gemini
                        new_lines.append(' ' * (indent + 4) + "# " + line.strip() + " - DISABLED")
                    elif "DeepSeekProvider()" in line:
                        new_lines.append(' ' * (indent + 4) + "DeepSeekProvider(),  # ONLY ACTIVE PROVIDER")
                    elif "]" in line:
                        new_lines.append(line)
                        in_provider_block = False
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            api_file.write_text('\n'.join(new_lines), encoding='utf-8')
            print("✅ Applied alternative fix!")
            return True
    
    return False

def verify_changes():
    """Verify the changes were applied"""
    api_file = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py")
    content = api_file.read_text(encoding='utf-8')
    
    has_deepseek = "DeepSeekProvider()" in content
    gemini_disabled = "# GeminiProvider()" in content or "GeminiProvider() - DISABLED" in content
    
    print("\n🔍 Verification:")
    print(f"  • DeepSeek active: {has_deepseek}")
    print(f"  • Gemini disabled: {gemini_disabled}")
    
    if has_deepseek and (gemini_disabled or "DeepSeekProvider(),  # ONLY ACTIVE PROVIDER" in content):
        print("\n✅ SUCCESS: DeepSeek-only mode configured!")
        return True
    else:
        print("\n⚠️ WARNING: Manual verification needed")
        return False

def main():
    print("🚀 DEEPSEEK-ONLY CONFIGURATION")
    print("="*60)
    
    if fix_providers_deepseek_only():
        if verify_changes():
            print("\n📋 NEXT STEPS:")
            print("="*60)
            print("\n1. Stop all running processes (Ctrl+C)")
            print("\n2. Use the new startup script:")
            print("   .\\START_COMPLETE_SYSTEM_DEEPSEEK.bat")
            print("\n3. The system will now use ONLY DeepSeek!")
            print("\n✅ Configuration complete!")
        else:
            print("\n⚠️ Please check the file manually")
    else:
        print("\n❌ Automatic fix failed")
        print("Please edit src_hexagonal/hexagonal_api_enhanced_clean.py manually")
        print("Change:")
        print("  GeminiProvider(),")
        print("To:")
        print("  # GeminiProvider(),  # DISABLED")

if __name__ == "__main__":
    main()
