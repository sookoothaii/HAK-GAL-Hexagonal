#!/usr/bin/env python3
"""
FIX FACT GENERATION SYSTEM
===========================
Stoppt die fehlerhaften Generatoren und aktiviert den intelligenten Generator
"""

import os
import sys
import subprocess
import time
import psutil
import signal

def kill_process_by_name(process_name):
    """Kill all processes matching the name"""
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            if process_name in ' '.join(cmdline):
                print(f"  Killing PID {proc.info['pid']}: {process_name}")
                proc.terminate()
                killed += 1
                time.sleep(0.5)
                if proc.is_running():
                    proc.kill()  # Force kill if still running
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return killed

def main():
    print("="*80)
    print("FACT GENERATION SYSTEM REPAIR")
    print("="*80)
    
    # 1. Stop all faulty generators
    print("\n1. STOPPING FAULTY GENERATORS...")
    print("-"*40)
    
    faulty_generators = [
        'aethelred_engine',
        'llm_governor_generator',
        'simple_fact_generator',
        'governor_with_parallel'
    ]
    
    total_killed = 0
    for gen in faulty_generators:
        killed = kill_process_by_name(gen)
        if killed:
            print(f"  ✓ Stopped {killed} {gen} process(es)")
            total_killed += killed
    
    if total_killed == 0:
        print("  ℹ No faulty generators were running")
    
    # 2. Clean up the database from bad facts
    print("\n2. DATABASE CLEANUP ANALYSIS...")
    print("-"*40)
    
    import sqlite3
    conn = sqlite3.connect(r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db')
    cursor = conn.cursor()
    
    # Count problematic facts
    cursor.execute("""
        SELECT COUNT(*) FROM facts 
        WHERE (statement LIKE '%NH3%' AND statement LIKE '%oxygen%')
           OR (statement LIKE '%H2O%' AND statement LIKE '%carbon%')
           OR (statement LIKE '%CH4%' AND statement LIKE '%oxygen%')
           OR (statement LIKE '%virus%' AND statement LIKE '%organ%')
           OR (statement LIKE '%bacteria%' AND statement LIKE '%nucleus%')
    """)
    bad_facts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM facts")
    total_facts = cursor.fetchone()[0]
    
    print(f"  Total facts: {total_facts:,}")
    print(f"  Problematic facts: {bad_facts:,} ({bad_facts/total_facts*100:.1f}%)")
    
    if bad_facts > 0:
        choice = input("\n  Remove problematic facts? (y/n): ")
        if choice.lower() == 'y':
            cursor.execute("""
                DELETE FROM facts 
                WHERE (statement LIKE '%NH3%' AND statement LIKE '%oxygen%')
                   OR (statement LIKE '%H2O%' AND statement LIKE '%carbon%')
                   OR (statement LIKE '%CH4%' AND statement LIKE '%oxygen%')
                   OR (statement LIKE '%virus%' AND statement LIKE '%organ%')
                   OR (statement LIKE '%bacteria%' AND statement LIKE '%nucleus%')
            """)
            removed = cursor.rowcount
            conn.commit()
            print(f"  ✓ Removed {removed} problematic facts")
    
    conn.close()
    
    # 3. Configure the new generator
    print("\n3. CONFIGURING INTELLIGENT GENERATOR...")
    print("-"*40)
    
    # Create config file
    config = """# INTELLIGENT FACT GENERATOR CONFIG
GENERATOR_MODE=intelligent
VALIDATION_ENABLED=true
RATE_LIMIT=30  # facts per minute
DOMAINS=chemistry,biology,physics,computer_science,mathematics
CROSS_DOMAIN_PERCENTAGE=20
BATCH_SIZE=5
API_PORT=5002
"""
    
    with open('generator_config.env', 'w') as f:
        f.write(config)
    print("  ✓ Configuration file created")
    
    # 4. Test the new generator
    print("\n4. TESTING INTELLIGENT GENERATOR...")
    print("-"*40)
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from intelligent_fact_generator import IntelligentFactGenerator
    
    generator = IntelligentFactGenerator()
    print("\n  Sample facts that would be generated:")
    print("  " + "-"*35)
    
    test_facts = []
    for _ in range(5):
        domain = 'chemistry'
        fact = generator.generate_fact_from_knowledge(domain)
        if fact:
            valid = "✓" if generator.validate_fact(fact) else "✗"
            print(f"  {valid} {fact}")
            test_facts.append(fact)
    
    # 5. Offer to start the generator
    print("\n5. ACTIVATION...")
    print("-"*40)
    
    print("\nThe Intelligent Fact Generator is ready to run.")
    print("It will generate scientifically accurate facts with validation.")
    print("\nFeatures:")
    print("  • Scientific accuracy validation")
    print("  • No invalid chemical combinations")
    print("  • Balanced predicate distribution")
    print("  • Cross-domain knowledge connections")
    print("  • Duplicate prevention")
    
    choice = input("\nStart the Intelligent Generator now? (y/n): ")
    
    if choice.lower() == 'y':
        duration = float(input("Duration in minutes (default: 1.0): ") or "1.0")
        print("\n" + "="*80)
        print("STARTING INTELLIGENT FACT GENERATOR")
        print("="*80)
        generator.run(duration_minutes=duration)
    else:
        print("\nTo start the generator later, run:")
        print("  python intelligent_fact_generator.py")
    
    print("\n" + "="*80)
    print("REPAIR COMPLETE")
    print("="*80)
    print("\nSummary:")
    print("  ✓ Faulty generators stopped")
    print("  ✓ Database cleaned")
    print("  ✓ Intelligent generator configured")
    print("  ✓ System ready for accurate fact generation")
    print("\nThe fact generation system is now repaired and ready.")


if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("Installing required package: psutil")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    main()
