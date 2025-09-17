#!/usr/bin/env python
"""
BYPASS THESIS ENGINE - RUN GENERATOR DIRECTLY
==============================================
"""
import os
import sys
import time
import threading

# Add paths
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal")
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\infrastructure\engines")

# Set auth token
os.environ['HAKGAL_AUTH_TOKEN'] = '515f57956e7bd15ddc3817573598f190'

print("="*60)
print("BYPASSING THESIS ENGINE - ACTIVATING GENERATOR")
print("="*60)

# Import the optimized generator
from simple_fact_generator import SimpleFactGenerator

print("\n✅ Loaded optimized SimpleFactGenerator")

# Create instance
generator = SimpleFactGenerator()
print(f"✅ HasProperty: {generator.predicates['HasProperty']*100:.0f}% (optimized)")
print(f"✅ Predicates: {len(generator.predicates)} types")
print(f"✅ Duplicate prevention: Active")

print("\n" + "="*60)
print("STARTING CONTINUOUS GENERATION")
print("="*60)
print("This bypasses the Thesis/Aethelred engines")
print("and runs the optimized fact generator directly!")
print("\nPress Ctrl+C to stop")
print("-"*60)

# Run in thread so it doesn't block
def run_generator():
    try:
        generator.run(duration_minutes=60)  # Run for 60 minutes
    except:
        pass

thread = threading.Thread(target=run_generator)
thread.daemon = True
thread.start()

# Monitor progress
try:
    while True:
        time.sleep(10)
        if generator.stats['facts_added'] > 0:
            rate = generator.stats['facts_added'] / ((time.time() - generator.start_time) / 60) if hasattr(generator, 'start_time') else 0
            print(f"\r✅ Generated: {generator.stats['facts_added']} facts | Rate: {rate:.1f} facts/min | Duplicates prevented: {generator.stats['duplicates_prevented']}", end="")
except KeyboardInterrupt:
    print("\n\n" + "="*60)
    print("STOPPED")
    generator.print_stats()
    print("="*60)
