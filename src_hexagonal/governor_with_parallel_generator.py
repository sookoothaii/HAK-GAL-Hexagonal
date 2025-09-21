#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GOVERNOR WITH PARALLEL GENERATOR
===============================
Dieses Script startet den Governor UND den Generator parallel
"""

import subprocess
import threading
import time
import sys
import os
from pathlib import Path

def start_generator():
    """Starte den Simple Fact Generator"""
    print("🚀 Starting Simple Fact Generator...")
    
    hex_root = Path(__file__).parent.parent
    generator_path = hex_root / "src_hexagonal" / "infrastructure" / "engines" / "simple_fact_generator.py"
    
    if not generator_path.exists():
        print(f"❌ Generator not found: {generator_path}")
        return
    
    try:
        # Starte Generator als subprocess
        process = subprocess.Popen([
            sys.executable, str(generator_path)
        ], cwd=str(hex_root))
        
        print(f"✅ Generator started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start generator: {e}")
        return None

def start_governor():
    """Starte den Governor"""
    print("🎯 Starting Governor...")
    
    hex_root = Path(__file__).parent.parent
    api_path = hex_root / "src_hexagonal" / "hexagonal_api_enhanced_clean.py"
    
    if not api_path.exists():
        print(f"❌ API not found: {api_path}")
        return
    
    try:
        # Starte API als subprocess
        process = subprocess.Popen([
            sys.executable, str(api_path)
        ], cwd=str(hex_root))
        
        print(f"✅ Governor started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start governor: {e}")
        return None

def main():
    print("=" * 60)
    print("🚀 STARTING GOVERNOR WITH PARALLEL GENERATOR")
    print("=" * 60)
    
    # Starte Generator
    generator_process = start_generator()
    if not generator_process:
        print("❌ Failed to start generator, exiting...")
        return
    
    # Warte kurz
    time.sleep(2)
    
    # Starte Governor
    governor_process = start_governor()
    if not governor_process:
        print("❌ Failed to start governor, exiting...")
        generator_process.terminate()
        return
    
    print("\n✅ BOTH SYSTEMS STARTED!")
    print("📊 Generator: High-speed fact generation")
    print("🎯 Governor: Engine management")
    print("\n🌐 Frontend: http://localhost:8088/governor")
    print("📈 Dashboard: http://localhost:8088/dashboard")
    
    try:
        # Warte auf beide Prozesse
        while True:
            # Prüfe Generator
            if generator_process.poll() is not None:
                print("❌ Generator stopped unexpectedly")
                break
            
            # Prüfe Governor
            if governor_process.poll() is not None:
                print("❌ Governor stopped unexpectedly")
                break
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        
        # Stoppe beide Prozesse
        if generator_process and generator_process.poll() is None:
            generator_process.terminate()
            print("✅ Generator stopped")
        
        if governor_process and governor_process.poll() is None:
            governor_process.terminate()
            print("✅ Governor stopped")

if __name__ == "__main__":
    main()






