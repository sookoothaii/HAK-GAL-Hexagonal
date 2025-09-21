#!/usr/bin/env python3
"""
MAKE BACKEND EXTREMELY LOUD - SEE EVERYTHING!
==============================================
"""

from pathlib import Path

print("🔥" * 40)
print("MAKING BACKEND SUPER VERBOSE - YOU WILL SEE EVERYTHING!")
print("🔥" * 40)

# 1. Fix Governor Adapter - Make it SCREAM
governor_file = Path("src_hexagonal/adapters/governor_adapter.py")
if governor_file.exists():
    with open(governor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(governor_file.with_suffix('.py.bak'), 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Add massive logging to start_engine
    content = content.replace(
        'def start_engine(self, engine_name: str, duration_minutes: float = 5) -> bool:',
        '''def start_engine(self, engine_name: str, duration_minutes: float = 5) -> bool:
        print("\\n" + "🚀"*40)
        print(f"START_ENGINE CALLED: {engine_name}")
        print(f"Duration: {duration_minutes} minutes")
        print("🚀"*40)'''
    )
    
    # Log the command being executed
    content = content.replace(
        'logger.info(f"Starting {engine_name} engine for {duration_minutes} minutes")',
        '''print(f"\\n🔥 EXECUTING COMMAND:")
        print(f"  {' '.join(cmd)}")
        print(f"  CWD: {Path.cwd()}")
        print(f"  Engine script exists: {engine_path.exists()}")
        logger.info(f"Starting {engine_name} engine for {duration_minutes} minutes")'''
    )
    
    # Log subprocess creation
    content = content.replace(
        'process = subprocess.Popen(',
        '''print("📡 Creating subprocess...")
        process = subprocess.Popen('''
    )
    
    # Add output capture
    if 'stdout=subprocess.PIPE,' in content and '# Capture output immediately' not in content:
        content = content.replace(
            'text=True\n            )',
            '''text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Capture output immediately
            import threading
            def read_output(proc, name):
                while True:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    print(f"[{name} OUTPUT] {line.strip()}")
            
            output_thread = threading.Thread(target=read_output, args=(process, engine_name))
            output_thread.daemon = True
            output_thread.start()'''
        )
    
    with open(governor_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Governor Adapter - Now SUPER verbose")

# 2. Fix Main API - Show everything
api_file = Path("src_hexagonal/api/main.py")
if api_file.exists():
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(api_file.with_suffix('.py.bak'), 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Add startup banner
    if '__name__ == "__main__"' in content and 'SUPER VERBOSE MODE' not in content:
        content = content.replace(
            'if __name__ == "__main__":',
            '''if __name__ == "__main__":
    print("\\n" + "🔥"*40)
    print("HAK-GAL HEXAGONAL - SUPER VERBOSE MODE ACTIVATED!")
    print("You will see EVERYTHING that happens!")
    print("🔥"*40 + "\\n")'''
        )
    
    # Log governor control
    if '@socketio.on("governor_control")' in content and 'GOVERNOR CONTROL RECEIVED' not in content:
        content = content.replace(
            'def handle_governor_control(data):',
            '''def handle_governor_control(data):
    print(f"\\n{'='*60}")
    print(f"🎮 GOVERNOR CONTROL RECEIVED: {data}")
    print(f"{'='*60}")'''
        )
    
    # Log governor start
    if 'governor.start()' in content and 'CALLING GOVERNOR.START' not in content:
        content = content.replace(
            'success = governor.start()',
            '''print("\\n🚀 CALLING GOVERNOR.START()...")
            success = governor.start()
            print(f"Governor start result: {success}")'''
        )
    
    with open(api_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Main API - Now shows all events")

# 3. Fix Engine Manager
engine_mgr = Path("src_hexagonal/adapters/engine_manager.py")
if engine_mgr.exists():
    with open(engine_mgr, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(engine_mgr.with_suffix('.py.bak'), 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Log engine starts
    content = content.replace(
        'def start_engine(self, engine_id: str) -> bool:',
        '''def start_engine(self, engine_id: str) -> bool:
        print(f"\\n🚀 ENGINE_MANAGER.START_ENGINE: {engine_id}")'''
    )
    
    with open(engine_mgr, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Engine Manager - Verbose logging added")

# 4. Fix base engine to show API calls
base_engine = Path("src_hexagonal/infrastructure/engines/base_engine.py")
if base_engine.exists():
    with open(base_engine, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Log LLM calls
    if 'def get_llm_explanation' in content and 'CALLING LLM FOR TOPIC' not in content:
        content = content.replace(
            'self.logger.info(f"Getting LLM explanation for: {topic}")',
            '''print(f"\\n📡 CALLING LLM FOR TOPIC: {topic}")
        self.logger.info(f"Getting LLM explanation for: {topic}")'''
        )
    
    # Log fact additions
    if 'def add_facts_batch' in content and 'ADDING FACTS TO KB' not in content:
        content = content.replace(
            'self.logger.info(f"Adding {len(facts)} facts to KB")',
            '''print(f"\\n💾 ADDING {len(facts)} FACTS TO KB")
        print(f"First 3: {facts[:3] if facts else 'none'}")
        self.logger.info(f"Adding {len(facts)} facts to KB")'''
        )
    
    with open(base_engine, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Base Engine - Shows all API calls")

print("\n" + "="*60)
print("BACKEND IS NOW SUPER VERBOSE!")
print("="*60)
print("\nRestart the backend now:")
print("  python src_hexagonal/api/main.py")
print("\nYou will see:")
print("  - Every button click")
print("  - Every engine start attempt")
print("  - Every subprocess command")
print("  - Every LLM call")
print("  - Every fact addition")
print("  - All errors with full details")
