#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CHECK EXTENDED ENGINE STATUS
=============================
Verifies that the system is using the Extended Engine
"""

import sys
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_configuration():
    """Check if configuration files point to extended engine"""
    print(f"\n{BLUE}=== CONFIGURATION CHECK ==={RESET}")
    
    files_to_check = [
        ('governor_adapter.py', 'src_hexagonal/adapters/governor_adapter.py'),
        ('api_engines.py', 'src_hexagonal/api_engines.py'),
        ('api_engines_async.py', 'src_hexagonal/api_engines_async.py')
    ]
    
    all_extended = True
    
    for name, path in files_to_check:
        full_path = Path(f"D:/MCP Mods/HAK_GAL_HEXAGONAL/{path}")
        if full_path.exists():
            content = full_path.read_text()
            if 'aethelred_extended.py' in content:
                print(f"  ✅ {name}: {GREEN}Using Extended Engine{RESET}")
            elif 'aethelred_fast.py' in content:
                print(f"  ❌ {name}: {RED}Still using Fast Engine{RESET}")
                all_extended = False
            else:
                print(f"  ⚠️  {name}: {YELLOW}Unknown configuration{RESET}")
        else:
            print(f"  ❌ {name}: {RED}File not found{RESET}")
            all_extended = False
    
    return all_extended

def check_database_growth():
    """Check if multi-argument facts are being generated"""
    print(f"\n{BLUE}=== DATABASE STATUS ==={RESET}")
    
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Count facts by argument count
    cursor.execute("""
        SELECT arg_count, COUNT(*) as count 
        FROM facts_extended 
        GROUP BY arg_count 
        ORDER BY arg_count
    """)
    
    results = cursor.fetchall()
    total_facts = sum(r[1] for r in results)
    multi_arg_facts = sum(r[1] for r in results if r[0] > 2)
    
    print(f"  Total facts: {total_facts:,}")
    print(f"  Distribution:")
    for arg_count, count in results:
        percentage = (count / total_facts * 100) if total_facts > 0 else 0
        bar = '█' * int(percentage / 2)
        print(f"    {arg_count} args: {count:6,} ({percentage:5.1f}%) {bar}")
    
    multi_ratio = (multi_arg_facts / total_facts * 100) if total_facts > 0 else 0
    
    if multi_ratio > 10:
        print(f"\n  {GREEN}✅ Multi-arg ratio: {multi_ratio:.1f}% - EXCELLENT!{RESET}")
    elif multi_ratio > 5:
        print(f"\n  {YELLOW}⚠️  Multi-arg ratio: {multi_ratio:.1f}% - Growing...{RESET}")
    else:
        print(f"\n  {RED}❌ Multi-arg ratio: {multi_ratio:.1f}% - Need Extended Engine!{RESET}")
    
    # Check recent facts
    cursor.execute("""
        SELECT statement, created_at 
        FROM facts_extended 
        WHERE arg_count >= 3 
        ORDER BY id DESC 
        LIMIT 3
    """)
    
    recent = cursor.fetchall()
    if recent:
        print(f"\n  {BLUE}Recent multi-arg facts:{RESET}")
        for stmt, created in recent:
            if len(stmt) > 70:
                stmt = stmt[:67] + "..."
            print(f"    - {stmt}")
    
    conn.close()
    return multi_ratio > 5

def check_running_processes():
    """Check if extended engine is currently running"""
    print(f"\n{BLUE}=== PROCESS CHECK ==={RESET}")
    
    import subprocess
    
    try:
        # Check for Python processes
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True,
            text=True
        )
        
        if 'aethelred_extended' in result.stdout:
            print(f"  {GREEN}✅ Extended Engine is RUNNING!{RESET}")
            return True
        elif 'aethelred_fast' in result.stdout:
            print(f"  {YELLOW}⚠️  Fast Engine is running (old version){RESET}")
            return False
        else:
            print(f"  {YELLOW}ℹ️  No Aethelred engine currently running{RESET}")
            return None
            
    except Exception as e:
        print(f"  {YELLOW}Could not check processes: {e}{RESET}")
        return None

def main():
    """Main check routine"""
    print("="*60)
    print(f"{BLUE}EXTENDED ENGINE STATUS CHECK{RESET}")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run checks
    config_ok = check_configuration()
    db_ok = check_database_growth()
    process_status = check_running_processes()
    
    # Summary
    print(f"\n{BLUE}=== SUMMARY ==={RESET}")
    
    if config_ok and db_ok:
        print(f"\n{GREEN}🎉 SYSTEM FULLY UPGRADED!{RESET}")
        print("The Extended Engine is configured and working.")
        print("All new facts will be multi-argument with high quality!")
    elif config_ok:
        print(f"\n{YELLOW}⚠️  CONFIGURATION UPDATED{RESET}")
        print("Extended Engine is configured but needs to run longer.")
        print("Restart the Governor to use the new configuration.")
    else:
        print(f"\n{RED}❌ UPDATE NEEDED{RESET}")
        print("System still using old Fast Engine.")
        print("Configuration files need to be updated.")
    
    # Recommendations
    print(f"\n{BLUE}=== RECOMMENDATIONS ==={RESET}")
    
    if not config_ok:
        print("1. Update configuration files to use aethelred_extended.py")
        print("2. Restart the backend and Governor")
    elif not db_ok:
        print("1. Let the Extended Engine run for 30+ minutes")
        print("2. Monitor with: python start_multi_arg.py --stats")
    else:
        print("✅ System optimal - continue running!")
    
    return config_ok and db_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
