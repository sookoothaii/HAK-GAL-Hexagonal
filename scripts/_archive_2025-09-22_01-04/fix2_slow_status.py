#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAK/GAL FIX 2: Optimize slow /api/status endpoint
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def main():
    print("FIX 2: Optimizing slow /api/status endpoint...")
    
    api_file = Path(__file__).parent / 'src_hexagonal' / 'hexagonal_api_enhanced_clean.py'
    
    if not api_file.exists():
        print("ERROR: API file not found!")
        print(f"  Looking for: {api_file}")
        return False
    
    # Read file
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the code to replace
    old_code = '''            if self.system_monitor:
                base_status['monitoring'] = self.system_monitor.get_status()
                base_status['system_metrics'] = self.system_monitor.get_system_metrics()'''
    
    # New optimized code
    new_code = '''            if self.system_monitor:
                base_status['monitoring'] = self.system_monitor.get_status()
                # Only include expensive system metrics if explicitly requested
                if request.args.get('include_metrics', '').lower() == 'true':
                    base_status['system_metrics'] = self.system_monitor.get_system_metrics()'''
    
    if old_code not in content:
        print("WARNING: Could not find the exact code to replace.")
        print("  The endpoint might already be optimized.")
        return False
    
    # Create backup
    backup_name = f'hexagonal_api_enhanced_clean.py.bak_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    backup_file = api_file.parent / backup_name
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"BACKUP: Created {backup_name}")
    
    # Replace code
    new_content = content.replace(old_code, new_code)
    
    # Write updated file
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("SUCCESS: Status endpoint optimized!")
    print("")
    print("USAGE:")
    print("  Fast: /api/status")
    print("  Full: /api/status?include_metrics=true")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
