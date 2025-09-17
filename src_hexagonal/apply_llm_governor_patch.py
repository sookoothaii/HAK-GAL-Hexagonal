#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTOMATIC LLM GOVERNOR INTEGRATION SCRIPT
==========================================
Applies the LLM Governor integration to hexagonal_api_enhanced_clean.py
"""

import os
import sys
import shutil
from pathlib import Path

def apply_llm_governor_patch():
    """
    Automatically integrate LLM Governor into the backend
    """
    
    print("=" * 60)
    print("LLM GOVERNOR AUTOMATIC INTEGRATION")
    print("=" * 60)
    
    # Path to the main API file
    api_file = Path("hexagonal_api_enhanced_clean.py")
    
    if not api_file.exists():
        print(f"[ERROR] {api_file} not found!")
        print("Please run this script from src_hexagonal directory")
        return False
    
    # Backup original file
    backup_file = api_file.with_suffix('.py.backup')
    print(f"[1/5] Creating backup: {backup_file}")
    shutil.copy2(api_file, backup_file)
    
    # Read the file
    print(f"[2/5] Reading {api_file}")
    with open(api_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find insertion points
    import_line = None
    init_line = None
    governor_start_line = None
    
    for i, line in enumerate(lines):
        # Find where to add import (after other adapter imports)
        if 'from src_hexagonal.llm_config_routes import' in line:
            import_line = i + 1
        
        # Find where to add initialization (after self.governor init)
        if 'print("[OK] Governor initialized' in line:
            init_line = i + 1
        
        # Find governor_start method
        if 'def governor_start():' in line:
            governor_start_line = i - 1  # Include decorator
    
    if not all([import_line, init_line, governor_start_line]):
        print("[ERROR] Could not find all insertion points!")
        print(f"  Import line: {import_line}")
        print(f"  Init line: {init_line}")
        print(f"  Governor start line: {governor_start_line}")
        return False
    
    print(f"[3/5] Found insertion points:")
    print(f"  Import at line: {import_line}")
    print(f"  Init at line: {init_line}")
    print(f"  Governor start at line: {governor_start_line}")
    
    # Check if already integrated
    content = ''.join(lines)
    if 'llm_governor_integration' in content:
        print("[INFO] LLM Governor already integrated!")
        return True
    
    # Apply patches
    print("[4/5] Applying patches...")
    
    # 1. Add import
    import_code = "from src_hexagonal.llm_governor_integration import integrate_llm_governor\n"
    lines.insert(import_line, import_code)
    print("  ✓ Import added")
    
    # Adjust line numbers after insertion
    init_line += 1
    governor_start_line += 1
    
    # 2. Add initialization
    init_code = """
        # Initialize LLM Governor
        self.llm_governor_integration = None
        if enable_governor:
            try:
                self.llm_governor_integration = integrate_llm_governor(self.app)
                print("[OK] LLM Governor Integration enabled")
            except Exception as e:
                print(f"[WARNING] LLM Governor Integration failed: {e}")
        
"""
    lines.insert(init_line, init_code)
    print("  ✓ Initialization added")
    
    # Adjust line numbers
    governor_start_line += init_code.count('\n')
    
    # 3. Replace governor_start method
    # Find the end of the method
    governor_end_line = governor_start_line
    indent_count = 0
    for i in range(governor_start_line, len(lines)):
        if 'def ' in lines[i] and i > governor_start_line + 2:
            governor_end_line = i
            break
    
    # New governor_start method
    new_governor_start = """        @self.app.route('/api/governor/start', methods=['POST'])
        # # # # # @require_api_key
        def governor_start():
            data = request.get_json(silent=True) or {}
            use_llm = data.get('use_llm', False)
            
            # Check if LLM Governor requested
            if use_llm and self.llm_governor_integration:
                self.llm_governor_integration.enabled = True
                # Also start the standard governor for engines
                if self.governor:
                    self.governor.start()
                return jsonify({
                    'success': True, 
                    'mode': 'llm_governor',
                    'provider': self.llm_governor_integration.config['provider']
                })
            else:
                # Use standard Thompson governor
                success = self.governor.start() if self.governor else False
                return jsonify({'success': success, 'mode': 'thompson'})
        
"""
    
    # Replace the method
    del lines[governor_start_line:governor_end_line]
    lines.insert(governor_start_line, new_governor_start)
    print("  ✓ Governor start method updated")
    
    # 4. Add LLM Governor status to status() method
    for i, line in enumerate(lines):
        if "if self.governor:" in line and "'governor'] =" in lines[i+1]:
            # Found the governor status section
            insert_line = i + 2
            while insert_line < len(lines) and lines[insert_line].strip():
                insert_line += 1
            
            status_code = """            
            if self.llm_governor_integration:
                base_status['llm_governor'] = {
                    'available': True,
                    'enabled': self.llm_governor_integration.enabled,
                    'provider': self.llm_governor_integration.config['provider'],
                    'epsilon': self.llm_governor_integration.config['epsilon'],
                    'metrics': self.llm_governor_integration.get_metrics()
                }
"""
            lines.insert(insert_line, status_code)
            print("  ✓ Status endpoint updated")
            break
    
    # 5. Write the modified file
    print(f"[5/5] Writing modified {api_file}")
    with open(api_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n" + "=" * 60)
    print("✅ LLM GOVERNOR INTEGRATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart the backend:")
    print("   Ctrl+C")
    print("   python hexagonal_api_enhanced_clean.py")
    print("\n2. Test the integration:")
    print("   curl http://localhost:5002/api/llm-governor/status")
    print("\n3. Enable LLM Governor:")
    print('   curl -X POST http://localhost:5002/api/llm-governor/enable')
    print("\nBackup saved as:", backup_file)
    
    return True

if __name__ == "__main__":
    # Change to src_hexagonal directory if needed
    current_dir = Path.cwd()
    if current_dir.name != 'src_hexagonal':
        src_hex_dir = current_dir / 'src_hexagonal'
        if src_hex_dir.exists():
            os.chdir(src_hex_dir)
            print(f"Changed directory to: {src_hex_dir}")
    
    success = apply_llm_governor_patch()
    
    if not success:
        print("\n[ERROR] Integration failed!")
        print("Please apply the patch manually using LLM_GOVERNOR_INTEGRATION_PATCH.py")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Integration complete!")
        sys.exit(0)
