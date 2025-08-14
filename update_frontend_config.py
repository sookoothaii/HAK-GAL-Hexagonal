#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update Frontend Configuration for HEXAGONAL
============================================
Adjusts frontend to use HEXAGONAL backend by default
"""

import os
import json
from pathlib import Path

def update_frontend_config():
    """Update frontend configuration to use HEXAGONAL backend"""
    
    frontend_path = Path("frontend")
    
    if not frontend_path.exists():
        print("❌ Frontend directory not found. Run migrate_complete_system.bat first!")
        return False
    
    # 1. Update package.json name
    package_json_path = frontend_path / "package.json"
    if package_json_path.exists():
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package = json.load(f)
        
        package['name'] = 'hak-gal-hexagonal-frontend'
        
        with open(package_json_path, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2)
        print("✅ Updated package.json")
    
    # 2. Update backends.ts to default to hexagonal
    backends_path = frontend_path / "src" / "config" / "backends.ts"
    if backends_path.exists():
        with open(backends_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Change default backend
        content = content.replace(
            "localStorage.getItem('activeBackend') || 'hexagonal'",
            "localStorage.getItem('activeBackend') || 'hexagonal'"
        )
        
        # Update hexagonal features to reflect current state
        content = content.replace(
            "autoLearning: false,  // Needs engine integration",
            "autoLearning: true,  // Engines integrated"
        )
        
        content = content.replace(
            "llmIntegration: false,  // Limited",
            "llmIntegration: true,  // DeepSeek/Gemini/Mistral"
        )
        
        with open(backends_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Updated backends.ts configuration")
    
    # 3. Create vite.config.ts if not exists
    vite_config_path = frontend_path / "vite.config.ts"
    if not vite_config_path.exists():
        vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:5001',
        ws: true,
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
'''
        with open(vite_config_path, 'w', encoding='utf-8') as f:
            f.write(vite_config)
        print("✅ Created vite.config.ts with HEXAGONAL proxy")
    
    # 4. Create or update .env.local
    env_local_path = frontend_path / ".env.local"
    env_content = """# HEXAGONAL Frontend Configuration
VITE_API_URL=http://localhost:5001
VITE_WS_URL=http://localhost:5001
VITE_DEFAULT_BACKEND=hexagonal
"""
    with open(env_local_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✅ Created .env.local")
    
    # 5. Create start script
    start_script_path = Path("start_hexagonal_complete.bat")
    start_script = """@echo off
echo ============================================================
echo STARTING HEXAGONAL COMPLETE SYSTEM
echo ============================================================
echo.

echo [1/3] Starting HEXAGONAL Backend (Port 5001)...
start "HEXAGONAL Backend" cmd /k "python src_hexagonal\\hexagonal_api_enhanced_clean.py"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [2/3] Starting Frontend (Port 5173)...
cd frontend
start "HEXAGONAL Frontend" cmd /k "npm run dev"

echo.
echo [3/3] Starting Governor (if needed)...
echo Governor can be controlled from frontend

echo.
echo ============================================================
echo HEXAGONAL SYSTEM RUNNING
echo ============================================================
echo.
echo Backend:  http://localhost:5001
echo Frontend: http://localhost:5173
echo.
echo To stop: Close all command windows
echo.
pause
"""
    with open(start_script_path, 'w') as f:
        f.write(start_script)
    print("✅ Created start_hexagonal_complete.bat")
    
    print("\n" + "="*60)
    print("FRONTEND CONFIGURATION UPDATED")
    print("="*60)
    print("\nNext steps:")
    print("1. cd frontend && npm install")
    print("2. Run start_hexagonal_complete.bat")
    print("\nFrontend will now use HEXAGONAL backend by default!")
    
    return True

if __name__ == "__main__":
    update_frontend_config()
