#!/usr/bin/env python3
"""
Direct Fix for Aethelred Engine Syntax Error
============================================
Directly fixes the indentation and missing except block
"""

from pathlib import Path
from datetime import datetime

def direct_fix():
    """Apply direct fix to the syntax error"""
    
    engine_path = Path("src_hexagonal/infrastructure/engines/aethelred_engine.py")
    
    if not engine_path.exists():
        print(f"❌ Engine file not found: {engine_path}")
        return False
    
    # Read the file
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    backup_path = engine_path.parent / f"aethelred_engine_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup created: {backup_path.name}")
    
    # The problematic section (with wrong indentation)
    problematic = """            # Collect results
            for topic, future in futures:
                try:
                    facts = future.result(timeout=80)
                    # Filter out existing facts
            new_facts = [f for f in facts if f not in existing]

            # Optional confidence gate (strict mode): keep only high-confidence facts
            strict_val = os.environ.get('AETHELRED_STRICT_CONFIDENCE', '')
            if strict_val:
                try:
                    threshold = float(strict_val)
                    gated = []
                    for st in new_facts:
                        c = self.get_confidence(st, timeout=8)
                        if c >= threshold:
                            gated.append(st)
                    new_facts = gated
                    self.logger.info(f"Confidence gate {threshold}: {len(new_facts)} passed")
                except Exception as e:
                    self.logger.warning(f"Strict confidence parse/apply error: {e}")
                    all_new_facts.extend(new_facts)
                except Exception as e:
                    self.logger.error(f"Error processing {topic}: {e}")"""
    
    # The fixed version (with correct indentation and structure)
    fixed = """            # Collect results
            for topic, future in futures:
                try:
                    facts = future.result(timeout=80)
                    # Filter out existing facts
                    new_facts = [f for f in facts if f not in existing]
                    
                    # Optional confidence gate (strict mode): keep only high-confidence facts
                    strict_val = os.environ.get('AETHELRED_STRICT_CONFIDENCE', '')
                    if strict_val:
                        try:
                            threshold = float(strict_val)
                            gated = []
                            for st in new_facts:
                                c = self.get_confidence(st, timeout=8)
                                if c >= threshold:
                                    gated.append(st)
                            new_facts = gated
                            self.logger.info(f"Confidence gate {threshold}: {len(new_facts)} passed")
                        except Exception as e:
                            self.logger.warning(f"Strict confidence parse/apply error: {e}")
                    
                    all_new_facts.extend(new_facts)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {topic}: {e}")"""
    
    # Replace the problematic section
    if problematic in content:
        content = content.replace(problematic, fixed)
        print("✅ Found and fixed the exact problematic section!")
        
        # Write the fixed content
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("\n" + "="*60)
        print("✅ SYNTAX ERROR FIXED SUCCESSFULLY!")
        print("="*60)
        print("\nThe following changes were made:")
        print("1. Fixed indentation of 'new_facts = [f for f in facts...]' line")
        print("2. Moved confidence gate logic inside try block")
        print("3. Fixed except block placement")
        print("4. Removed duplicate except block")
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Test the engine:")
        print("   python test_engine_debug.py")
        print("\n2. If test passes, apply the LLM fix:")
        print("   python FINAL_LLM_FIX.py")
        print("\n3. Restart the backend:")
        print("   python src_hexagonal/hexagonal_api_enhanced.py")
        
        return True
    else:
        print("⚠️ Could not find exact pattern, trying alternative approach...")
        
        # Alternative: replace line by line
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Find the problematic section
            if "facts = future.result(timeout=80)" in line:
                fixed_lines.append(line)  # Add the facts = line
                i += 1
                
                if i < len(lines) and "# Filter out existing facts" in lines[i]:
                    fixed_lines.append(lines[i])  # Add comment
                    i += 1
                    
                    if i < len(lines) and "new_facts = [f for f in facts if f not in existing]" in lines[i]:
                        # Fix the indentation - should have 20 spaces (5 indents * 4)
                        fixed_lines.append("                    new_facts = [f for f in facts if f not in existing]")
                        i += 1
                        
                        # Skip empty line if present
                        if i < len(lines) and lines[i].strip() == "":
                            fixed_lines.append("")
                            i += 1
                        
                        # Now handle the confidence gate section
                        while i < len(lines):
                            if "except Exception as e:" in lines[i] and "self.logger.error(f\"Error processing {topic}" in lines[i+1] if i+1 < len(lines) else False:
                                # Found the except block - make sure it's properly placed
                                fixed_lines.append("                except Exception as e:")
                                fixed_lines.append("                    self.logger.error(f\"Error processing {topic}: {e}\")")
                                i += 2
                                break
                            elif "all_new_facts.extend(new_facts)" in lines[i]:
                                # This should be inside try block
                                fixed_lines.append("                    all_new_facts.extend(new_facts)")
                                fixed_lines.append("                    ")
                                i += 1
                            else:
                                # Keep the line with proper indentation if it's part of try block
                                if lines[i].strip() and not lines[i].strip().startswith("#"):
                                    # Ensure proper indentation (20 spaces for try block content)
                                    stripped = lines[i].lstrip()
                                    if "strict_val" in stripped or "threshold" in stripped or "gated" in stripped:
                                        fixed_lines.append("                    " + stripped)
                                    else:
                                        fixed_lines.append(lines[i])
                                else:
                                    fixed_lines.append(lines[i])
                                i += 1
                    else:
                        fixed_lines.append(lines[i])
                        i += 1
                else:
                    fixed_lines.append(lines[i])
                    i += 1
            else:
                fixed_lines.append(line)
                i += 1
        
        # Write the fixed content
        fixed_content = '\n'.join(fixed_lines)
        with open(engine_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Applied alternative fix")
        return True

if __name__ == "__main__":
    print("="*60)
    print("DIRECT FIX FOR AETHELRED ENGINE SYNTAX ERROR")
    print("="*60)
    
    success = direct_fix()
    
    if success:
        print("\n✅ Fix completed! Test with: python test_engine_debug.py")
    else:
        print("\n❌ Automatic fix failed")
        print("\nYou can manually restore from backup or use clean version:")
        print("  cp src_hexagonal/infrastructure/engines/aethelred_engine_clean.py src_hexagonal/infrastructure/engines/aethelred_engine.py")
