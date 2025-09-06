#!/usr/bin/env python3
"""
Deploy HRM Learning System - Robust Version
============================================
Safely deploy the HRM feedback learning system
"""

import sys
import os
import subprocess
import time
from pathlib import Path
import json

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_status():
    """Check if backend and frontend are running"""
    import requests
    
    backend_running = False
    frontend_running = False
    
    try:
        r = requests.get('http://localhost:5001/health', timeout=1)
        backend_running = r.status_code == 200
    except:
        pass
    
    try:
        r = requests.get('http://localhost:5173', timeout=1)
        frontend_running = True  # If it responds at all
    except:
        pass
    
    return backend_running, frontend_running

def deploy_backend():
    """Deploy backend changes"""
    print("\n[DEPLOY] Deploying Backend HRM Feedback System...")
    
    # Check if files exist
    feedback_adapter = Path("src_hexagonal/adapters/hrm_feedback_adapter.py")
    feedback_endpoints = Path("src_hexagonal/adapters/hrm_feedback_endpoints.py")
    
    # Use robust patch script if available, otherwise fallback
    patch_scripts = [
        Path("patch_hrm_feedback_robust.py"),
        Path("patch_hrm_feedback.py")
    ]
    
    patch_script = None
    for script in patch_scripts:
        if script.exists():
            patch_script = script
            break
    
    if not patch_script:
        print("[ERROR] No patch script found")
        return False
    
    if not all([feedback_adapter.exists(), feedback_endpoints.exists()]):
        print("[ERROR] Missing required files:")
        if not feedback_adapter.exists():
            print(f"        - {feedback_adapter}")
        if not feedback_endpoints.exists():
            print(f"        - {feedback_endpoints}")
        return False
    
    print("[OK] All backend files present")
    print(f"[INFO] Using patch script: {patch_script}")
    
    # Apply patch with UTF-8 environment
    print("[PATCH] Patching API with feedback endpoints...")
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    result = subprocess.run(
        [sys.executable, str(patch_script)], 
        capture_output=True, 
        text=True,
        encoding='utf-8',
        env=env
    )
    
    if result.returncode != 0:
        print(f"[ERROR] Patch failed with return code {result.returncode}")
        if result.stdout:
            print("[STDOUT]:", result.stdout)
        if result.stderr:
            print("[STDERR]:", result.stderr)
        return False
    
    print("[OK] Backend patched successfully")
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            print(f"       {line}")
    
    return True

def deploy_frontend():
    """Deploy frontend changes"""
    print("\n[DEPLOY] Deploying Frontend Confidence Cache...")
    
    # Check if files exist
    cache_hook = Path("frontend/src/hooks/useConfidenceCache.ts")
    enhanced_query = Path("frontend/src/pages/ProUnifiedQueryEnhanced.tsx")
    
    if not all([cache_hook.exists(), enhanced_query.exists()]):
        print("[ERROR] Missing required files:")
        if not cache_hook.exists():
            print(f"        - {cache_hook}")
        if not enhanced_query.exists():
            print(f"        - {enhanced_query}")
        return False
    
    print("[OK] All frontend files present")
    
    # Update ProApp.tsx to use enhanced version (optional)
    app_file = Path("frontend/src/ProApp.tsx")
    if app_file.exists():
        content = app_file.read_text(encoding='utf-8')
        if "ProUnifiedQueryEnhanced" not in content:
            print("[NOTE] ProApp.tsx not updated - using patch mode instead")
            print("      The enhanced version patches the original at runtime")
    
    return True

def test_deployment():
    """Test the deployed system"""
    print("\n[TEST] Testing Deployment...")
    
    try:
        import requests
        
        # Test feedback endpoint
        try:
            r = requests.post('http://localhost:5001/api/hrm/feedback', 
                             json={
                                 'query': 'TestQuery(Test, Deployment)',
                                 'type': 'positive',
                                 'confidence': 0.5
                             },
                             timeout=2)
            
            if r.status_code in [200, 201]:
                print("[OK] Backend feedback endpoint working")
                data = r.json()
                print(f"     New confidence: {data.get('new_confidence', 'N/A')}")
                print(f"     Adjustment: {data.get('adjustment', 'N/A')}")
            else:
                print(f"[WARN] Backend endpoint returned {r.status_code}")
                if r.status_code == 404:
                    print("       Endpoint not found - backend needs restart")
        except Exception as e:
            print(f"[INFO] Backend test failed: {e}")
            print("       This is expected - backend needs restart to load new endpoints")
    except ImportError:
        print("[WARN] requests library not available for testing")
    
    # Check frontend files
    if Path("frontend/src/hooks/useConfidenceCache.ts").exists():
        print("[OK] Frontend cache hook deployed")
    
    if Path("frontend/src/pages/ProUnifiedQueryEnhanced.tsx").exists():
        print("[OK] Frontend enhanced query deployed")
    
    return True

def main():
    """Main deployment process"""
    print("=" * 60)
    print("HRM LEARNING SYSTEM DEPLOYMENT (ROBUST)")
    print("=" * 60)
    
    # Check current status
    backend_running, frontend_running = check_status()
    
    print(f"\n[STATUS] Current Status:")
    print(f"         Backend (5001): {'Running' if backend_running else 'Stopped'}")
    print(f"         Frontend (5173): {'Running' if frontend_running else 'Stopped'}")
    
    # Deploy components
    backend_ok = deploy_backend()
    frontend_ok = deploy_frontend()
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)
    
    if backend_ok and frontend_ok:
        print("[SUCCESS] All components deployed successfully!")
        
        print("\n[NEXT] Next Steps:")
        
        if backend_running:
            print("\n1. [ACTION REQUIRED] RESTART BACKEND to load new endpoints:")
            print("   -------------------------------------------------------")
            print("   a) Stop backend: Press Ctrl+C in backend terminal")
            print("   b) Start again: python src_hexagonal/hexagonal_api_enhanced.py")
            print("   -------------------------------------------------------")
        else:
            print("\n1. [OK] Start backend with new endpoints:")
            print("        python src_hexagonal/hexagonal_api_enhanced.py")
        
        if frontend_running:
            print("\n2. [OK] Frontend will auto-reload (Vite HMR)")
            print("        - Changes take effect immediately")
            print("        - Check browser console for 'HRM Learning patch applied'")
        else:
            print("\n2. Start frontend:")
            print("   cd frontend && npm run dev")
        
        print("\n3. [TEST] Test the system:")
        print("          - Open http://localhost:5173")
        print("          - Run a query like 'IsA(Socrates, Philosopher)'")
        print("          - Click 'Verify Response'")
        print("          - Run the same query again")
        print("          - Confidence should increase!")
        
        print("\n4. [VERIFY] Run test script after backend restart:")
        print("          python test_hrm_learning.py")
        
        # Test if possible
        test_deployment()
        
    else:
        print("[ERROR] Deployment incomplete")
        if not backend_ok:
            print("        - Backend deployment failed")
            print("        - Check error messages above")
        if not frontend_ok:
            print("        - Frontend deployment failed")
    
    print("\n" + "=" * 60)
    print("END OF DEPLOYMENT")
    print("=" * 60)

if __name__ == "__main__":
    main()
