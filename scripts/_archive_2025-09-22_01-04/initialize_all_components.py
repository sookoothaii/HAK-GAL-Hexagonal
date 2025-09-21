#!/usr/bin/env python
"""
Initialize All System Components
=================================
Lädt HRM, Governor und CUDA korrekt
"""

import sys
import os
from pathlib import Path
import time

# Set environment variables FIRST
os.environ['HAKGAL_PORT'] = '5002'
os.environ['HAKGAL_WRITE_ENABLED'] = 'true'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

def initialize_all_components():
    """Initialize HRM, Governor, CUDA and all components"""
    
    print("="*70)
    print("INITIALIZING ALL SYSTEM COMPONENTS")
    print("="*70)
    
    results = {
        'hrm': False,
        'governor': False,
        'cuda': False,
        'database': False
    }
    
    # 1. Check and load PyTorch/CUDA
    print("\n[1] Initializing CUDA...")
    try:
        import torch
        
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            name = torch.cuda.get_device_name(device)
            print(f"✅ CUDA available: {name}")
            print(f"   Device: cuda:{device}")
            print(f"   Memory: {torch.cuda.get_device_properties(device).total_memory / 1e9:.1f} GB")
            
            # Test CUDA with small tensor
            test_tensor = torch.randn(100, 100).cuda()
            print(f"   Test tensor on GPU: Success")
            results['cuda'] = True
        else:
            print("❌ CUDA not available - using CPU")
            print("   This is OK but slower")
    except ImportError:
        print("❌ PyTorch not installed")
        print("   Install with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    except Exception as e:
        print(f"⚠️ CUDA initialization error: {e}")
    
    # 2. Initialize HRM Model
    print("\n[2] Initializing HRM Neural Model...")
    try:
        # Add paths
        sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))
        sys.path.insert(0, str(Path(__file__).parent / "hrm_unified"))
        
        # Try to import HRM
        try:
            from hrm_unified.unified_hrm_api import EnhancedHRMSystem
            
            print("   Loading HRM system...")
            hrm_system = EnhancedHRMSystem()
            
            # Test the model
            test_query = "IsA(Test, Entity)"
            result = hrm_system.reason(test_query)
            
            print(f"✅ HRM Model loaded successfully")
            print(f"   Parameters: {sum(p.numel() for p in hrm_system.model.parameters()):,}")
            print(f"   Test query confidence: {result['confidence']:.3f}")
            results['hrm'] = True
            
        except ImportError as e:
            print(f"⚠️ Could not import HRM: {e}")
            print("   HRM will work in fallback mode")
            
    except Exception as e:
        print(f"❌ HRM initialization failed: {e}")
        print("   System will work without neural confidence")
    
    # 3. Initialize Governor
    print("\n[3] Initializing Governor...")
    try:
        from src_hexagonal.adapters.governor_adapter import GovernorAdapter
        
        governor = GovernorAdapter()
        
        # Check if initialized
        if governor.initialized:
            print("✅ Governor initialized")
            print(f"   Mode: {governor.current_state['mode']}")
            print(f"   Engines available: aethelred, thesis")
            
            # Start governor
            if governor.start():
                print("✅ Governor started successfully")
                results['governor'] = True
            else:
                print("⚠️ Governor initialized but not started")
                print("   Start manually with: python activate_governor_maximum.py")
        else:
            print("❌ Governor initialization failed")
            
    except ImportError as e:
        print(f"❌ Could not import Governor: {e}")
    except Exception as e:
        print(f"❌ Governor error: {e}")
    
    # 4. Check Database
    print("\n[4] Checking Database...")
    try:
        import sqlite3
        db_path = Path("hexagonal_kb.db")
        
        if db_path.exists():
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(DISTINCT predicate) FROM facts WHERE predicate IS NOT NULL")
                predicates = cursor.fetchone()[0]
                
                print(f"✅ Database operational")
                print(f"   Facts: {count:,}")
                print(f"   Predicates: {predicates}")
                print(f"   Mode: WRITE (Port 5002)")
                results['database'] = True
        else:
            print("❌ Database not found")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # 5. Create initialization script
    print("\n[5] Creating startup script with all components...")
    
    startup_script = '''#!/usr/bin/env python
"""
Start HAK-GAL with All Components Loaded
=========================================
Auto-generated startup script
"""

import os
import sys
from pathlib import Path

# Set environment
os.environ['HAKGAL_PORT'] = '5002'
os.environ['HAKGAL_WRITE_ENABLED'] = 'true'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))
sys.path.insert(0, str(Path(__file__).parent / "hrm_unified"))

def start_with_all_components():
    """Start the system with all components"""
    
    print("\\n" + "="*60)
    print("HAK-GAL HEXAGONAL - FULL SYSTEM START")
    print("="*60)
    
    # Import Flask app
    from hexagonal_api_enhanced import create_app
    
    # Create app with all features
    app = create_app(use_legacy=False)
    
    # Initialize HRM if available
    try:
        from hrm_unified.unified_hrm_api import EnhancedHRMSystem
        app.hrm_system = EnhancedHRMSystem()
        print("✅ HRM Neural Model loaded")
    except:
        print("⚠️ HRM in fallback mode")
    
    # Initialize Governor
    try:
        from adapters.governor_adapter import GovernorAdapter
        app.governor = GovernorAdapter()
        app.governor.start()
        print("✅ Governor started")
    except:
        print("⚠️ Governor not available")
    
    # Check CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA enabled: {torch.cuda.get_device_name(0)}")
    except:
        pass
    
    print("="*60)
    print(f"🚀 Starting on http://localhost:5002")
    print(f"📊 Dashboard: http://127.0.0.1:8088/dashboard")
    print("="*60)
    
    # Run the app
    app.run(host='127.0.0.1', port=5002, debug=False)

if __name__ == '__main__':
    start_with_all_components()
'''
    
    startup_file = Path("start_5002_with_all_features.py")
    startup_file.write_text(startup_script)
    print(f"✅ Created: {startup_file}")
    
    # 6. Summary
    print("\n" + "="*70)
    print("INITIALIZATION RESULTS:")
    print("="*70)
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component.upper()}: {'Loaded' if status else 'Not loaded'}")
    
    loaded = sum(results.values())
    total = len(results)
    percentage = (loaded / total) * 100
    
    print(f"\n📊 Components loaded: {loaded}/{total} ({percentage:.0f}%)")
    
    if loaded == total:
        print("\n🎉 ALL COMPONENTS SUCCESSFULLY INITIALIZED!")
    elif loaded >= 2:
        print("\n✅ System operational with partial features")
    else:
        print("\n⚠️ System needs manual intervention")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    
    print("""
1. STOP current backend (Ctrl+C)

2. RUN the fix scripts:
   python fix_405_errors.py
   python fix_dashboard_display.py

3. START with all components:
   python start_5002_with_all_features.py

4. VERIFY in browser:
   http://127.0.0.1:8088/dashboard
   
   Should show:
   - HRM: Loaded (3.5M parameters)
   - Governor: ACTIVE
   - CUDA: Available
   - Port 5002: WRITE mode
""")
    
    return results

if __name__ == "__main__":
    results = initialize_all_components()
    
    if not results['governor']:
        print("\n💡 To start Governor manually:")
        print("   python activate_governor_maximum.py")