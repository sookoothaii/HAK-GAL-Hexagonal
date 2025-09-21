#!/usr/bin/env python3
"""
Deploy HRM Learning System
===========================
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
    patch_script = Path("patch_hrm_feedback.py")
    
    if not all([feedback_adapter.exists(), feedback_endpoints.exists(), patch_script.exists()]):
        print("[ERROR] Missing required files")
        return False
    
    print("[OK] All backend files present")
    
    # Apply patch with UTF-8 environment
    print("[PATCH] Patching API with feedback endpoints...")
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    result = subprocess.run(
        [sys.executable, "patch_hrm_feedback.py"], 
        capture_output=True, 
        text=True,
        encoding='utf-8',
        env=env
    )
    
    if result.returncode != 0:
        print(f"[ERROR] Patch failed: {result.stderr}")
        return False
    
    print("[OK] Backend patched successfully")
    return True

def deploy_frontend():
    """Deploy frontend changes"""
    print("\n[DEPLOY] Deploying Frontend Confidence Cache...")
    
    # Check if files exist
    cache_hook = Path("frontend/src/hooks/useConfidenceCache.ts")
    enhanced_query = Path("frontend/src/pages/ProUnifiedQueryEnhanced.tsx")
    
    if not all([cache_hook.exists(), enhanced_query.exists()]):
        print("[ERROR] Missing required files")
        return False
    
    print("[OK] All frontend files present")
    
    # Update ProApp.tsx to use enhanced version (optional)
    app_file = Path("frontend/src/ProApp.tsx")
    if app_file.exists():
        content = app_file.read_text()
        if "ProUnifiedQueryEnhanced" not in content:
            print("[NOTE] ProApp.tsx not updated - using patch mode instead")
            print("      The enhanced version patches the original at runtime")
    
    return True

def test_deployment():
    """Test the deployed system"""
    print("\n[TEST] Testing Deployment...")
    
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
    except Exception as e:
        print(f"[ERROR] Backend test failed: {e}")
        print("        This is normal if backend needs restart")
    
    # Check frontend files
    if Path("frontend/src/hooks/useConfidenceCache.ts").exists():
        print("[OK] Frontend cache hook deployed")
    
    if Path("frontend/src/pages/ProUnifiedQueryEnhanced.tsx").exists():
        print("[OK] Frontend enhanced query deployed")
    
    return True

def main():
    """Main deployment process"""
    print("=" * 60)
    print("HRM LEARNING SYSTEM DEPLOYMENT")
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
            print("1. [ACTION] RESTART BACKEND to load new endpoints:")
            print("            - Stop: Ctrl+C in backend terminal")
            print("            - Start: python src_hexagonal/hexagonal_api_enhanced.py")
        else:
            print("1. [OK] Start backend with new endpoints:")
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
        
        # Test if possible
        test_deployment()
        
    else:
        print("[ERROR] Deployment incomplete")
        if not backend_ok:
            print("        - Backend deployment failed")
        if not frontend_ok:
            print("        - Frontend deployment failed")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
