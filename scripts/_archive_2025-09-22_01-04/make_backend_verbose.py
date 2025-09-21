#!/usr/bin/env python3
"""
Make Backend EXTREMELY Verbose
===============================
Shows EVERYTHING that's happening in the backend
"""

import os
from pathlib import Path

def add_verbose_logging():
    """Add extensive logging to all critical backend components"""
    
    fixes = []
    
    # 1. Fix Governor Adapter - Add detailed logging
    governor_path = Path("src_hexagonal/adapters/governor_adapter.py")
    if governor_path.exists():
        with open(governor_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add verbose logging to start method
        if "def start(self)" in content and "VERBOSE GOVERNOR START" not in content:
            content = content.replace(
                "def start(self):",
                """def start(self):
        print("="*60)
        print("🚀 GOVERNOR STARTING - VERBOSE MODE")
        print("="*60)"""
            )
        
        # Add logging to make_decision
        if "def make_decision(self)" in content and "GOVERNOR DECISION CYCLE" not in content:
            content = content.replace(
                "def make_decision(self):",
                """def make_decision(self):
        print("\\n" + "="*60)
        print("🎯 GOVERNOR DECISION CYCLE STARTING")
        print("="*60)"""
            )
        
        # Add logging when starting engines
        if "subprocess.Popen" in content and "STARTING ENGINE PROCESS" not in content:
            content = content.replace(
                "process = subprocess.Popen(",
                """print(f"\\n🚀🚀🚀 STARTING ENGINE PROCESS: {engine_name}")
                print(f"Command: {' '.join(cmd)}")
                print(f"Working dir: {os.getcwd()}")
                process = subprocess.Popen("""
            )
        
        with open(governor_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixes.append("✅ Governor Adapter - Added verbose logging")
    
    # 2. Fix Base Engine - Show all API calls
    base_engine_path = Path("src_hexagonal/infrastructure/engines/base_engine.py")
    if base_engine_path.exists():
        with open(base_engine_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add logging to get_llm_explanation
        if "def get_llm_explanation" in content and "CALLING LLM API" not in content:
            content = content.replace(
                'response = requests.post(url, json=data, timeout=timeout)',
                '''print(f"\\n📡 CALLING LLM API: {url}")
        print(f"Topic: {topic}")
        response = requests.post(url, json=data, timeout=timeout)
        print(f"Response status: {response.status_code}")'''
            )
        
        # Add logging to add_facts_batch
        if "def add_facts_batch" in content and "ADDING FACTS BATCH" not in content:
            content = content.replace(
                'response = requests.post(url, json=data, timeout=30)',
                '''print(f"\\n💾 ADDING FACTS BATCH TO KB")
        print(f"Number of facts: {len(facts)}")
        print(f"First 3 facts: {facts[:3]}")
        response = requests.post(url, json=data, timeout=30)
        print(f"Response: {response.status_code}")'''
            )
        
        with open(base_engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixes.append("✅ Base Engine - Added API call logging")
    
    # 3. Fix Aethelred Engine - Show fact generation
    aethelred_path = Path("src_hexagonal/infrastructure/engines/aethelred_engine.py")
    if aethelred_path.exists():
        with open(aethelred_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add logging to process_topic
        if "def process_topic" in content and "PROCESSING TOPIC" not in content:
            content = content.replace(
                'self.logger.info(f"Processing topic: {topic}")',
                '''print(f"\\n{'='*60}")
        print(f"📚 PROCESSING TOPIC: {topic}")
        print(f"{'='*60}")
        self.logger.info(f"Processing topic: {topic}")'''
            )
        
        # Add logging to run method
        if "def run(self" in content and "AETHELRED ENGINE STARTING" not in content:
            content = content.replace(
                'self.logger.info(f"Starting Aethelred Engine',
                '''print("\\n" + "🔥"*20)
        print("AETHELRED ENGINE STARTING - MAXIMUM VERBOSITY")
        print("🔥"*20)
        self.logger.info(f"Starting Aethelred Engine'''
            )
        
        with open(aethelred_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixes.append("✅ Aethelred Engine - Added verbose fact generation logging")
    
    # 4. Fix main API - Show all WebSocket events
    api_path = Path("src_hexagonal/api/main.py")
    if api_path.exists():
        with open(api_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add logging to governor_control
        if "@socketio.on('governor_control')" in content and "GOVERNOR CONTROL EVENT" not in content:
            content = content.replace(
                "@socketio.on('governor_control')\ndef handle_governor_control(data):",
                """@socketio.on('governor_control')
def handle_governor_control(data):
    print(f"\\n{'='*60}")
    print(f"🎮 GOVERNOR CONTROL EVENT RECEIVED")
    print(f"Data: {data}")
    print(f"{'='*60}")"""
            )
        
        # Add logging to engine start
        if "engine_manager.start_engine" in content and "STARTING ENGINE VIA API" not in content:
            content = content.replace(
                "success = engine_manager.start_engine(engine_id)",
                """print(f"\\n🚀 STARTING ENGINE VIA API: {engine_id}")
            success = engine_manager.start_engine(engine_id)
            print(f"Engine start result: {success}")"""
            )
        
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixes.append("✅ Main API - Added WebSocket event logging")
    
    # 5. Fix LLM Providers - Show ALL responses
    llm_path = Path("src_hexagonal/adapters/llm_providers.py")
    if llm_path.exists():
        with open(llm_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add super verbose logging to DeepSeek
        if "[DeepSeek] Success!" in content and "FULL RESPONSE" not in content:
            content = content.replace(
                'print("[DeepSeek] Success!")',
                '''print("[DeepSeek] Success!")
                response_preview = result['choices'][0]['message']['content'][:500]
                print(f"[DeepSeek] Response preview: {response_preview}")
                print(f"[DeepSeek] Full response length: {len(result['choices'][0]['message']['content'])} chars")'''
            )
        
        with open(llm_path, 'w', encoding='utf-8') as f:
            f.write(content)
        fixes.append("✅ LLM Providers - Added response preview logging")
    
    return fixes

def add_startup_banner():
    """Add a massive startup banner to the API"""
    
    api_path = Path("src_hexagonal/api/main.py")
    if api_path.exists():
        with open(api_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add banner to startup
        if "if __name__ == '__main__':" in content and "VERBOSE MODE ACTIVATED" not in content:
            content = content.replace(
                "if __name__ == '__main__':",
                """if __name__ == '__main__':
    print("\\n" + "="*80)
    print("🔥🔥🔥 HAK-GAL HEXAGONAL BACKEND - VERBOSE MODE ACTIVATED 🔥🔥🔥")
    print("="*80)
    print("EVERYTHING WILL BE LOGGED - PREPARE FOR INFORMATION OVERLOAD!")
    print("="*80 + "\\n")"""
            )
        
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return "✅ Added verbose startup banner"
    return "⚠️ Could not add startup banner"

if __name__ == "__main__":
    print("="*60)
    print("MAKING BACKEND EXTREMELY VERBOSE")
    print("="*60)
    
    # Apply all fixes
    fixes = add_verbose_logging()
    banner = add_startup_banner()
    
    print("\nApplied fixes:")
    for fix in fixes:
        print(f"  {fix}")
    print(f"  {banner}")
    
    print("\n" + "="*60)
    print("BACKEND IS NOW IN MAXIMUM VERBOSE MODE!")
    print("="*60)
    print("\nRestart the backend to see EVERYTHING:")
    print("  python src_hexagonal/api/main.py")
    print("\nYou will now see:")
    print("  - Every governor decision")
    print("  - Every engine start attempt")
    print("  - Every LLM API call")
    print("  - Every fact generation")
    print("  - Every WebSocket event")
    print("  - Full error messages")
    print("\nThe backend will be VERY chatty now!")
