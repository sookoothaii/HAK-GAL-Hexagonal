#!/usr/bin/env python3
"""
DIRECT FIX - Force DeepSeek only by modifying the exact line
"""

from pathlib import Path
import shutil

def apply_deepseek_only_fix():
    """Directly modify the provider initialization"""
    
    print("🔧 APPLYING DIRECT FIX FOR DEEPSEEK-ONLY")
    print("="*60)
    
    api_file = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py")
    
    # Create backup
    backup = api_file.with_suffix('.py.backup_gemini')
    shutil.copy2(api_file, backup)
    print(f"✅ Backup created: {backup.name}")
    
    # Read file
    content = api_file.read_text(encoding='utf-8')
    
    # Find the exact section (around line 380)
    old_section = """                providers = [
                    GeminiProvider(),     # Gemini FIRST - verified working
                    DeepSeekProvider(),   # DeepSeek as fallback
                    # MistralProvider() removed - 401 Unauthorized
                ]"""
    
    new_section = """                # TEMPORARY FIX: Only use DeepSeek (no Gemini)
                providers = [
                    DeepSeekProvider(),   # ONLY DeepSeek - no Gemini
                    # GeminiProvider(),   # DISABLED - no API key
                    # MistralProvider()   # DISABLED - 401 error
                ]"""
    
    if old_section in content:
        content = content.replace(old_section, new_section)
        api_file.write_text(content, encoding='utf-8')
        print("✅ Successfully modified provider initialization!")
        print("\n📝 Changes:")
        print("  • GeminiProvider() is now COMMENTED OUT")
        print("  • DeepSeekProvider() is the ONLY active provider")
        return True
    else:
        print("❌ Could not find exact provider section")
        print("\n🔍 Trying alternative approach...")
        
        # Alternative: Add check before provider initialization
        check_code = """
                # DEEPSEEK-ONLY MODE: Skip Gemini if no API key
                if not os.environ.get('GEMINI_API_KEY'):
                    print("[LLM] No Gemini API key - using DeepSeek only")
                    providers = [DeepSeekProvider()]
                else:"""
        
        if "providers = [" in content and "GeminiProvider()" in content:
            # Find the line and add check before it
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                if "providers = [" in line and i > 0:
                    # Add check before this line
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + "# DEEPSEEK-ONLY MODE CHECK")
                    new_lines.append(' ' * indent + "if not os.environ.get('GEMINI_API_KEY'):")
                    new_lines.append(' ' * (indent + 4) + "print('[LLM] No Gemini key - using DeepSeek only')")
                    new_lines.append(' ' * (indent + 4) + "providers = [DeepSeekProvider()]")
                    new_lines.append(' ' * indent + "else:")
                    new_lines.append(' ' * (indent + 4) + line.strip())
                    
                    # Continue with the rest of the provider list
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip().startswith(']'):
                            new_lines.append(' ' * (indent + 4) + lines[j].strip())
                            break
                        else:
                            new_lines.append(' ' * (indent + 4) + lines[j].strip())
                elif i > 0 and "GeminiProvider()" in lines[i-1]:
                    # Skip lines that are part of the provider list we just handled
                    if ']' not in line:
                        continue
                else:
                    new_lines.append(line)
            
            api_file.write_text('\n'.join(new_lines), encoding='utf-8')
            print("✅ Applied alternative fix!")
            return True
    
    return False

def verify_fix():
    """Verify the fix was applied"""
    api_file = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py")
    content = api_file.read_text(encoding='utf-8')
    
    if "# GeminiProvider()" in content or "providers = [DeepSeekProvider()]" in content:
        print("\n✅ Fix verified - DeepSeek-only mode active")
        return True
    else:
        print("\n❌ Fix not applied correctly")
        return False

def main():
    print("🚀 DIRECT DEEPSEEK-ONLY FIX")
    print("="*60)
    
    success = apply_deepseek_only_fix()
    
    if success:
        verify_fix()
        print("\n⚠️ BACKEND MUST BE RESTARTED!")
        print("\n1. Stop backend (Ctrl+C)")
        print("2. Start again:")
        print('   cd "D:\\MCP Mods\\HAK_GAL_HEXAGONAL"')
        print("   .\\.venv_hexa\\Scripts\\activate")
        print("   python src_hexagonal/hexagonal_api_enhanced_clean.py")
        print("\n3. Check backend log - should NOT show Gemini errors anymore")
    else:
        print("\n❌ Fix failed - manual edit required")

if __name__ == "__main__":
    main()
