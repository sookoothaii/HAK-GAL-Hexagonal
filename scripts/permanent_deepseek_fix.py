#!/usr/bin/env python3
"""
PERMANENT FIX: Force DeepSeek ALWAYS via environment check
This survives reconnects, reloads, and restarts
"""

from pathlib import Path
import shutil

def apply_permanent_deepseek_fix():
    """Apply a permanent fix that ALWAYS uses DeepSeek when no Gemini key"""
    
    print("🔧 APPLYING PERMANENT DEEPSEEK-ONLY FIX")
    print("="*60)
    
    api_file = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py")
    
    # Backup
    backup = api_file.with_suffix('.py.backup_permanent')
    if not backup.exists():
        shutil.copy2(api_file, backup)
        print(f"✅ Backup created: {backup.name}")
    
    # Read content
    content = api_file.read_text(encoding='utf-8')
    
    # Find the LLM provider section
    old_provider_init = """                providers = [
                    GeminiProvider(),     # Gemini FIRST - verified working
                    DeepSeekProvider(),   # DeepSeek as fallback
                    # MistralProvider() removed - 401 Unauthorized
                ]
                llm = MultiLLMProvider(providers)"""
    
    # New robust initialization that checks environment EVERY TIME
    new_provider_init = """                # ROBUST DEEPSEEK-ONLY MODE
                # Check environment variables EVERY TIME providers are initialized
                if not os.environ.get('GEMINI_API_KEY') or os.environ.get('GEMINI_API_KEY') == '':
                    # No Gemini key - use ONLY DeepSeek
                    print("[LLM] No Gemini API key found - using DeepSeek ONLY")
                    providers = [
                        DeepSeekProvider(),   # ONLY DeepSeek
                    ]
                else:
                    # Gemini key exists - use both
                    print("[LLM] Gemini API key found - using Gemini + DeepSeek")
                    providers = [
                        GeminiProvider(),     
                        DeepSeekProvider(),   
                    ]
                llm = MultiLLMProvider(providers)"""
    
    if old_provider_init in content:
        content = content.replace(old_provider_init, new_provider_init)
        api_file.write_text(content, encoding='utf-8')
        print("✅ Applied permanent fix!")
        print("\n📝 Changes:")
        print("  • Environment check EVERY time providers initialize")
        print("  • DeepSeek-only when no Gemini key")
        print("  • Survives reconnects and reloads")
        return True
    else:
        print("⚠️ Trying alternative fix...")
        
        # Alternative: Find the line and modify
        lines = content.split('\n')
        new_lines = []
        found = False
        
        for i, line in enumerate(lines):
            if "providers = [" in line and "GeminiProvider()" in lines[i+1] if i+1 < len(lines) else False:
                # Found the provider initialization
                indent = len(line) - len(line.lstrip())
                
                # Add environment check
                new_lines.append(' ' * indent + "# ROBUST DEEPSEEK-ONLY MODE")
                new_lines.append(' ' * indent + "if not os.environ.get('GEMINI_API_KEY'):")
                new_lines.append(' ' * (indent + 4) + "print('[LLM] No Gemini key - DeepSeek only')")
                new_lines.append(' ' * (indent + 4) + "providers = [DeepSeekProvider()]")
                new_lines.append(' ' * indent + "else:")
                new_lines.append(' ' * (indent + 4) + line.strip())
                found = True
                
                # Skip the original provider lines
                for j in range(i+1, min(i+5, len(lines))):
                    if ']' in lines[j]:
                        new_lines.append(' ' * (indent + 4) + lines[j].strip())
                        break
                    else:
                        new_lines.append(' ' * (indent + 4) + lines[j].strip())
                        
                # Skip processed lines
                for _ in range(j-i):
                    if i+1 < len(lines):
                        lines[i+1] = ''
            else:
                new_lines.append(line)
        
        if found:
            api_file.write_text('\n'.join(new_lines), encoding='utf-8')
            print("✅ Applied alternative fix!")
            return True
    
    return False

def update_startup_script():
    """Update the startup script to ensure no Gemini key"""
    
    print("\n📝 Updating Startup Script")
    print("-"*40)
    
    bat_file = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\START_COMPLETE_SYSTEM_DEEPSEEK.bat")
    
    if bat_file.exists():
        content = bat_file.read_text()
        
        # Make sure we don't set GEMINI_API_KEY
        if "set GEMINI_API_KEY=" not in content:
            print("✅ Startup script already correct")
        else:
            # Remove any GEMINI_API_KEY setting
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if "set GEMINI_API_KEY=" not in line:
                    new_lines.append(line)
            
            bat_file.write_text('\n'.join(new_lines))
            print("✅ Removed GEMINI_API_KEY from startup script")
    else:
        print("⚠️ Startup script not found")

def verify_fix():
    """Verify the fix is in place"""
    api_file = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\hexagonal_api_enhanced_clean.py")
    content = api_file.read_text(encoding='utf-8')
    
    has_env_check = "if not os.environ.get('GEMINI_API_KEY')" in content
    has_deepseek_only = "providers = [DeepSeekProvider()]" in content or "DeepSeekProvider(),   # ONLY" in content
    
    print("\n🔍 Verification:")
    print(f"  • Environment check: {has_env_check}")
    print(f"  • DeepSeek-only code: {has_deepseek_only}")
    
    if has_env_check and has_deepseek_only:
        print("\n✅ PERMANENT FIX VERIFIED!")
        return True
    else:
        print("\n⚠️ Fix may need manual verification")
        return False

def main():
    print("🚀 PERMANENT DEEPSEEK-ONLY FIX")
    print("="*60)
    print("This fix survives WebSocket reconnects and Flask reloads")
    print()
    
    # Apply the permanent fix
    success = apply_permanent_deepseek_fix()
    
    if success:
        update_startup_script()
        verify_fix()
        
        print("\n" + "="*60)
        print("📋 NEXT STEPS:")
        print("\n1. Restart the backend completely:")
        print("   - Close ALL terminal windows")
        print("   - Run: .\\START_COMPLETE_SYSTEM_DEEPSEEK.bat")
        print("\n2. The fix will now:")
        print("   • Check for Gemini key EVERY time")
        print("   • Use DeepSeek when no Gemini key")
        print("   • Survive reconnects and reloads")
        print("\n✅ Fix complete!")
    else:
        print("\n❌ Automatic fix failed")
        print("Manual intervention required")

if __name__ == "__main__":
    main()
