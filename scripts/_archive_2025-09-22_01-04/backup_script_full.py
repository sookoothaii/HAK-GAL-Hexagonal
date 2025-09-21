#!/usr/bin/env python3
"""
HAK_GAL HEXAGONAL - Complete Backup Script (Python Version)
Equivalent to BACKUP_SUITE.ps1 - Full system backup with all components
Version: 1.0
"""

import os
import shutil
import datetime
import json
import hashlib
import zipfile
from pathlib import Path
from typing import List, Dict, Set

# Konfiguration
PROJECT_ROOT = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = Path(f"D:\\MCP Mods\\HAK_GAL_BACKUP_{TIMESTAMP}")

class HexagonalCompleteBackup:
    """Complete Backup Manager - Python equivalent to BACKUP_SUITE.ps1"""
    
    def __init__(self):
        self.timestamp = TIMESTAMP
        self.backup_path = BACKUP_DIR
        self.log_file = self.backup_path / "backup.log"
        self.manifest = []
        
    def write_log(self, message: str):
        """Log message to console and file"""
        log_entry = f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}: {message}"
        print(f"[CYAN] {log_entry}")
        if self.log_file.exists():
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
    
    def backup_database(self):
        """1. CRITICAL - Database & Backups"""
        self.write_log("Backing up Database...")
        db_dir = self.backup_path / "database"
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all database files
        for db_file in PROJECT_ROOT.glob("hexagonal_kb.db*"):
            shutil.copy2(db_file, db_dir)
        
        # Copy existing backups
        if (PROJECT_ROOT / "backups").exists():
            shutil.copytree(PROJECT_ROOT / "backups", db_dir / "backups", dirs_exist_ok=True)
    
    def backup_models(self):
        """2. CRITICAL - Trained Models"""
        self.write_log("Backing up Models...")
        models_dir = self.backup_path / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        
        if (PROJECT_ROOT / "models").exists():
            for model_file in (PROJECT_ROOT / "models").glob("*"):
                if model_file.is_file():
                    shutil.copy2(model_file, models_dir)
    
    def backup_project_hub(self):
        """3. CRITICAL - Project Hub & Documentation"""
        self.write_log("Backing up Project Hub...")
        if (PROJECT_ROOT / "project_hub").exists():
            shutil.copytree(PROJECT_ROOT / "project_hub", 
                          self.backup_path / "project_hub", dirs_exist_ok=True)
    
    def backup_source_code(self):
        """4. SOURCE CODE"""
        self.write_log("Backing up Source Code...")
        if (PROJECT_ROOT / "src_hexagonal").exists():
            shutil.copytree(PROJECT_ROOT / "src_hexagonal", 
                          self.backup_path / "src_hexagonal", dirs_exist_ok=True)
    
    def backup_frontend(self):
        """5. FRONTEND (NEW!)"""
        self.write_log("Backing up Frontend...")
        frontend_dir = self.backup_path / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        
        if (PROJECT_ROOT / "frontend").exists():
            # Exclude large directories
            exclude = {'node_modules', 'dist', '.vite', 'coverage', '.turbo'}
            
            for item in (PROJECT_ROOT / "frontend").iterdir():
                if item.name not in exclude:
                    if item.is_file():
                        shutil.copy2(item, frontend_dir)
                    else:
                        shutil.copytree(item, frontend_dir / item.name, dirs_exist_ok=True)
            
            # Ensure package files are copied
            for pkg_file in ['package.json', 'package-lock.json']:
                src = PROJECT_ROOT / "frontend" / pkg_file
                if src.exists():
                    shutil.copy2(src, frontend_dir)
    
    def backup_mcp_tools(self):
        """6. MCP TOOLS"""
        self.write_log("Backing up MCP Tools...")
        mcp_dir = self.backup_path / "mcp_tools"
        mcp_dir.mkdir(parents=True, exist_ok=True)
        
        for mcp_file in PROJECT_ROOT.glob("*mcp*.py"):
            shutil.copy2(mcp_file, mcp_dir)
    
    def backup_configuration(self):
        """7. CONFIGURATION"""
        self.write_log("Backing up Configuration...")
        config_dir = self.backup_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Environment files
        for env_file in PROJECT_ROOT.glob(".env*"):
            shutil.copy2(env_file, config_dir)
        
        # Claude configs
        for claude_file in PROJECT_ROOT.glob("claude*.json"):
            shutil.copy2(claude_file, config_dir)
        
        # Other configs
        for config_file in PROJECT_ROOT.glob("*config*.json"):
            shutil.copy2(config_file, config_dir)
            
        # HAK GAL constitution
        for const_file in PROJECT_ROOT.glob("hak_gal_constitution*"):
            shutil.copy2(const_file, config_dir)
    
    def backup_test_results(self):
        """8. TEST RESULTS"""
        self.write_log("Backing up Test Results...")
        tests_dir = self.backup_path / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        
        patterns = ["*test*.json", "*test*.py", "benchmark*.json", "llm_test*.json"]
        for pattern in patterns:
            for test_file in PROJECT_ROOT.glob(pattern):
                if test_file.is_file():
                    shutil.copy2(test_file, tests_dir)
    
    def backup_logs(self):
        """9. LOGS & AUDIT"""
        self.write_log("Backing up Logs...")
        logs_dir = self.backup_path / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        for log_file in PROJECT_ROOT.glob("*.log"):
            shutil.copy2(log_file, logs_dir)
        
        # Special audit log
        audit_log = PROJECT_ROOT / "mcp_write_audit.log"
        if audit_log.exists():
            shutil.copy2(audit_log, logs_dir)
    
    def create_manifest(self):
        """10. Get System Info"""
        self.write_log("Documenting System State...")
        
        manifest_content = f"""HAK_GAL SUITE BACKUP MANIFEST
=============================
Timestamp: {self.timestamp}
System: HAK_GAL MCP SQLite Full FIXED v3.1
Database: hexagonal_kb.db
Facts Count: 5,927
Models: HRM v2 (3.5M params)
Ollama Models: qwen2.5:32b-instruct-q3_K_M (15GB), qwen2.5:7b (4.7GB)
Frontend: React + Vite + TypeScript + Tailwind CSS

BACKUP CONTENTS:
- SQLite Database + WAL/SHM files
- Trained Models (hrm_model_v2.pth)
- Project Hub (all reports & snapshots)
- Source Code (src_hexagonal)
- Frontend Code (React/Vite app)
- MCP Tools (45 tools)
- Configuration Files
- Test Results & Benchmarks
- Audit Logs

RESTORE INSTRUCTIONS:
1. Extract backup to D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\
2. Verify database integrity
3. Check model files
4. Install backend dependencies: pip install -r requirements.txt
5. Install frontend dependencies: cd frontend && npm install
6. Start backend: python src_hexagonal/hexagonal_api_enhanced_clean.py
7. Start frontend: cd frontend && npm run dev

PYTHON DEPENDENCIES (install if needed):
pip install flask flask-cors flask-socketio eventlet
pip install numpy torch scikit-learn
pip install httpx sqlite3 pathlib
pip install python-dotenv

FRONTEND DEPENDENCIES (install if needed):
cd frontend
npm install

OLLAMA MODELS (pull if needed):
ollama pull qwen2.5:32b-instruct-q3_K_M
ollama pull qwen2.5:7b
"""
        
        manifest_path = self.backup_path / "MANIFEST.txt"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
    
    def calculate_size(self):
        """11. Calculate sizes"""
        self.write_log("Calculating backup size...")
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.backup_path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                total_size += filepath.stat().st_size
        
        size_mb = total_size / (1024 * 1024)
        self.write_log(f"Total backup size: {size_mb:.2f} MB")
        return size_mb
    
    def create_zip(self):
        """12. Create ZIP Archive"""
        zip_path = Path(f"D:\\MCP Mods\\HAK_GAL_SUITE_BACKUP_{self.timestamp}.zip")
        self.write_log("Creating ZIP archive...")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.backup_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.backup_path.parent)
                    zipf.write(file_path, arcname)
        
        self.write_log(f"ZIP created: {zip_path}")
        return zip_path
    
    def run(self):
        """Execute complete backup"""
        print("\n" + "="*40)
        print("HAK_GAL SUITE COMPLETE BACKUP")
        print(f"Timestamp: {self.timestamp}")
        print("="*40 + "\n")
        
        # Create backup directory
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create log file
        self.log_file.touch()
        self.write_log("Starting HAK_GAL Suite Backup...")
        
        # Run all backup steps
        try:
            self.backup_database()
            self.backup_models()
            self.backup_project_hub()
            self.backup_source_code()
            self.backup_frontend()
            self.backup_mcp_tools()
            self.backup_configuration()
            self.backup_test_results()
            self.backup_logs()
            self.create_manifest()
            
            size_mb = self.calculate_size()
            
            # Ask for ZIP creation
            create_zip = input("\nCreate ZIP archive? (y/n): ")
            if create_zip.lower() == 'y':
                self.create_zip()
            
            print("\n" + "="*40)
            print("BACKUP COMPLETE!")
            print(f"Location: {self.backup_path}")
            print(f"Size: {size_mb:.2f} MB")
            print("="*40 + "\n")
            
            self.write_log("Backup completed successfully")
            
        except Exception as e:
            self.write_log(f"ERROR: {str(e)}")
            print(f"\n❌ BACKUP FAILED: {str(e)}")
            raise

def main():
    """Main function"""
    backup = HexagonalCompleteBackup()
    backup.run()

if __name__ == "__main__":
    main()
