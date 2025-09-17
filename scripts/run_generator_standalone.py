#!/usr/bin/env python3
"""
Run the optimized generator standalone for continuous fact generation
"""
import os
import sys
import time
from pathlib import Path

# Setup paths
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal")
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\infrastructure\engines")

# Set auth token
os.environ['HAKGAL_AUTH_TOKEN'] = '515f57956e7bd15ddc3817573598f190'

print("="*60)
print("STANDALONE OPTIMIZED FACT GENERATOR")
print("="*60)

# Import the optimized generator
from simple_fact_generator import SimpleFactGenerator

# Create generator instance
generator = SimpleFactGenerator()

print("\nGenerator Configuration:")
print(f"  Predicates: {len(generator.predicates)} types")
print(f"  HasProperty weight: {generator.predicates['HasProperty']*100:.0f}%")
print(f"  Duplicate prevention: Active")
print(f"  API endpoint: http://127.0.0.1:5002")

print("\nStarting continuous generation...")
print("Press Ctrl+C to stop")
print("-"*60)

# Run continuously
try:
    generator.run(duration_minutes=60)  # Run for 60 minutes
except KeyboardInterrupt:
    print("\n\nStopped by user")
    generator.print_stats()
