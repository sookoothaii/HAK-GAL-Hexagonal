#!/usr/bin/env python3
"""
HAK-GAL Hexagonal Architecture - Safe Parallel Setup
=====================================================
Nach HAK/GAL Verfassung Artikel 3: Externe Verifikation

Dieses Script erstellt eine sichere Parallel-Umgebung für die 
Hexagonal-Migration ohne das Original-System zu gefährden.
"""

import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime

class HexagonalSetup:
    def __init__(self):
        self.original_path = Path(r"D:\MCP Mods\HAK_GAL_SUITE")
        self.hexagonal_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def verify_original(self):
        """Verifiziere dass Original-System existiert und läuft"""
        print("🔍 Verifiziere Original HAK-GAL System...")
        
        checks = {
            "Main API": self.original_path / "src" / "hak_gal" / "api.py",
            "K-Assistant": self.original_path / "src" / "hak_gal" / "services" / "k_assistant_thread_safe_v2.py",
            "Database": self.original_path / "k_assistant.db",
            "HRM Model": self.original_path / "hrm_unified" / "clean_model.pth",
            "Virtual Env": self.original_path / ".venv"
        }
        
        all_good = True
        for name, path in checks.items():
            if path.exists():
                print(f"  ✅ {name}: {path.name}")
            else:
                print(f"  ❌ {name}: FEHLT!")
                all_good = False
                
        return all_good
    
    def create_directory_structure(self):
        """Erstelle Hexagonal-Verzeichnisstruktur"""
        print("\n📁 Erstelle Hexagonal-Verzeichnisstruktur...")
        
        directories = [
            "src_hexagonal",
            "src_hexagonal/core",
            "src_hexagonal/core/domain",
            "src_hexagonal/core/ports",
            "src_hexagonal/adapters",
            "src_hexagonal/adapters/inbound",
            "src_hexagonal/adapters/outbound",
            "src_hexagonal/application",
            "tests",
            "tests/unit",
            "tests/integration",
            "config",
            "docs",
            "migration_tools"
        ]
        
        for dir_name in directories:
            dir_path = self.hexagonal_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {dir_name}/")
            
    def copy_critical_files(self):
        """Kopiere nur kritische Dateien (nicht alles!)"""
        print("\n📋 Kopiere kritische Dateien...")
        
        # Nur Config und kleine Dateien kopieren
        files_to_copy = [
            (".env", ".env"),
            ("requirements.txt", "requirements_original.txt"),
            ("pyproject.toml", "pyproject_original.toml")
        ]
        
        for src, dst in files_to_copy:
            src_path = self.original_path / src
            dst_path = self.hexagonal_path / dst
            
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                print(f"  ✅ Kopiert: {src} → {dst}")
            else:
                print(f"  ⚠️ Nicht gefunden: {src}")
                
        # Kopiere die Datenbank für Development
        db_src = self.original_path / "k_assistant.db"
        db_dst = self.hexagonal_path / "k_assistant_dev.db"
        
        if db_src.exists():
            shutil.copy2(db_src, db_dst)
            print(f"  ✅ Development DB kopiert: {db_dst.name}")
            
    def create_virtual_environment(self):
        """Erstelle separate virtuelle Umgebung"""
        print("\n🐍 Erstelle separate Virtual Environment...")
        
        venv_path = self.hexagonal_path / ".venv_hexa"
        
        # Erstelle venv
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"  ✅ Virtual Environment erstellt: .venv_hexa")
        
        # Erstelle Aktivierungsskript
        activate_script = self.hexagonal_path / "activate_hexa.bat"
        activate_script.write_text(
            f"@echo off\n"
            f"echo Aktiviere Hexagonal Environment...\n"
            f"call .venv_hexa\\Scripts\\activate.bat\n"
            f"echo ✅ Hexagonal Environment aktiv!\n"
        )
        print(f"  ✅ Aktivierungsskript erstellt: activate_hexa.bat")
        
    def create_wrapper_modules(self):
        """Erstelle Wrapper für Original-Code"""
        print("\n🔗 Erstelle Wrapper-Module...")
        
        # Legacy Wrapper
        legacy_wrapper = self.hexagonal_path / "src_hexagonal" / "legacy_wrapper.py"
        legacy_wrapper.write_text('''"""
Legacy System Wrapper
=====================
Ermöglicht Zugriff auf Original HAK-GAL ohne Modifikation
"""

import sys
from pathlib import Path

# Add original HAK-GAL to path (READ-ONLY!)
ORIGINAL_PATH = Path(r"D:\\MCP Mods\\HAK_GAL_SUITE")
sys.path.insert(0, str(ORIGINAL_PATH / "src"))

def get_legacy_k_assistant():
    """Get original K-Assistant instance"""
    try:
        from hak_gal.services.k_assistant_thread_safe_v2 import k_assistant_singleton
        return k_assistant_singleton
    except ImportError as e:
        print(f"❌ Cannot import legacy K-Assistant: {e}")
        return None

def get_legacy_hrm():
    """Get original HRM system"""
    try:
        sys.path.insert(0, str(ORIGINAL_PATH / "hrm_unified"))
        from unified_hrm_api import get_hrm_instance
        return get_hrm_instance()
    except ImportError as e:
        print(f"❌ Cannot import legacy HRM: {e}")
        return None
''')
        print(f"  ✅ Legacy Wrapper erstellt")
        
        # Hexagonal Repository Interface
        repo_interface = self.hexagonal_path / "src_hexagonal" / "core" / "ports" / "__init__.py"
        repo_interface.parent.mkdir(parents=True, exist_ok=True)
        repo_interface.write_text('''"""
Hexagonal Ports (Interfaces)
============================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class FactRepository(ABC):
    """Port for Fact Storage"""
    
    @abstractmethod
    def add_fact(self, fact: Dict[str, Any]) -> bool:
        """Add a new fact"""
        pass
    
    @abstractmethod
    def get_facts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve facts"""
        pass
    
    @abstractmethod
    def query_facts(self, query: str) -> List[Dict[str, Any]]:
        """Query facts"""
        pass

class ReasoningEngine(ABC):
    """Port for Reasoning Services"""
    
    @abstractmethod
    def reason(self, query: str) -> Dict[str, Any]:
        """Perform reasoning on query"""
        pass
    
    @abstractmethod
    def get_confidence(self, statement: str) -> float:
        """Get confidence score for statement"""
        pass
''')
        print(f"  ✅ Port Interfaces erstellt")
        
    def create_test_script(self):
        """Erstelle Test-Script für Parallel-Betrieb"""
        print("\n🧪 Erstelle Test-Script...")
        
        test_script = self.hexagonal_path / "test_parallel.py"
        test_script.write_text('''#!/usr/bin/env python3
"""
Test Parallel Operation
========================
Testet ob beide Systeme parallel laufen können
"""

import sys
import requests
from pathlib import Path

def test_original_system():
    """Test Original HAK-GAL on port 5000"""
    print("\\n🔍 Teste Original HAK-GAL (Port 5000)...")
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("  ✅ Original System läuft!")
            return True
    except:
        print("  ⚠️ Original System nicht erreichbar")
    return False

def test_hexagonal_system():
    """Test Hexagonal System on port 5001"""
    print("\\n🔍 Teste Hexagonal System (Port 5001)...")
    try:
        response = requests.get("http://localhost:5001/health")
        if response.status_code == 200:
            print("  ✅ Hexagonal System läuft!")
            return True
    except:
        print("  ⚠️ Hexagonal System noch nicht gestartet")
    return False

def test_legacy_wrapper():
    """Test Legacy Wrapper Import"""
    print("\\n🔍 Teste Legacy Wrapper...")
    
    # Add hexagonal to path
    sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))
    
    try:
        from legacy_wrapper import get_legacy_k_assistant, get_legacy_hrm
        
        k_assistant = get_legacy_k_assistant()
        if k_assistant:
            print("  ✅ Legacy K-Assistant importiert")
        
        hrm = get_legacy_hrm()
        if hrm:
            print("  ✅ Legacy HRM importiert")
            
        return True
    except Exception as e:
        print(f"  ❌ Wrapper Fehler: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("HAK-GAL PARALLEL SYSTEM TEST")
    print("=" * 60)
    
    original_ok = test_original_system()
    hexagonal_ok = test_hexagonal_system()
    wrapper_ok = test_legacy_wrapper()
    
    print("\\n" + "=" * 60)
    print("ERGEBNIS:")
    print(f"  Original System:  {'✅' if original_ok else '❌'}")
    print(f"  Hexagonal System: {'✅' if hexagonal_ok else '⚠️ Noch nicht implementiert'}")
    print(f"  Legacy Wrapper:   {'✅' if wrapper_ok else '❌'}")
    print("=" * 60)
''')
        print(f"  ✅ Test-Script erstellt: test_parallel.py")
        
    def create_readme(self):
        """Erstelle README mit Instruktionen"""
        print("\n📝 Erstelle README...")
        
        readme = self.hexagonal_path / "README.md"
        readme.write_text(f'''# HAK-GAL Hexagonal Architecture Migration

**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Status:** Parallel Development Environment  
**Original:** D:\\MCP Mods\\HAK_GAL_SUITE (NICHT MODIFIZIEREN!)  

## 🎯 Ziel

Sichere Migration zu Hexagonal Architecture OHNE das Original zu gefährden.

## 📁 Struktur

```
HAK_GAL_HEXAGONAL/
├── .venv_hexa/           # Separate Python Environment  
├── k_assistant_dev.db    # Development Database (Kopie)
├── src_hexagonal/        # Neue Hexagonal Implementation
│   ├── core/            # Domain Logic (Port & Adapter frei)
│   ├── adapters/        # Input/Output Adapters
│   └── legacy_wrapper.py # Zugriff auf Original (Read-Only)
└── test_parallel.py      # Test für Parallel-Betrieb
```

## 🚀 Quick Start

### 1. Aktiviere Hexagonal Environment
```bash
cd "D:\\MCP Mods\\HAK_GAL_HEXAGONAL"
activate_hexa.bat
```

### 2. Installiere Dependencies
```bash
pip install -r requirements_hexa.txt
```

### 3. Teste Parallel-Betrieb
```bash
# Terminal 1: Original System (Port 5000)
cd "D:\\MCP Mods\\HAK_GAL_SUITE"
.venv\\Scripts\\activate
python src/hak_gal/api.py

# Terminal 2: Hexagonal System (Port 5001)
cd "D:\\MCP Mods\\HAK_GAL_HEXAGONAL"
activate_hexa.bat
python test_parallel.py
```

## ⚠️ WICHTIGE REGELN

1. **NIEMALS** Original HAK_GAL_SUITE direkt modifizieren!
2. **IMMER** über legacy_wrapper.py auf Original zugreifen
3. **PORT 5000** = Original, **PORT 5001** = Hexagonal
4. **BACKUP** vor kritischen Änderungen!

## 🔄 Migration Strategy

### Phase 1: Wrapper (Woche 1)
- [ ] Legacy Wrapper funktioniert
- [ ] Ports definiert
- [ ] Erste Adapter implementiert

### Phase 2: Core Migration (Woche 2-3)
- [ ] Domain Logic extrahiert
- [ ] Unit Tests geschrieben
- [ ] Integration Tests laufen

### Phase 3: Full Hexagonal (Woche 4+)
- [ ] Alle Adapter implementiert
- [ ] Performance optimiert
- [ ] Production ready

## 📊 Status

- Original System: ✅ Läuft weiter auf Port 5000
- Hexagonal System: 🚧 In Entwicklung auf Port 5001
- Database: 📋 Development-Kopie verwendet
- Risk Level: 🟢 Niedrig (vollständig isoliert)
''')
        print(f"  ✅ README.md erstellt")
        
    def run(self):
        """Führe komplettes Setup aus"""
        print("=" * 60)
        print("HAK-GAL HEXAGONAL - PARALLEL SETUP")
        print("=" * 60)
        
        # 1. Verifiziere Original
        if not self.verify_original():
            print("\n❌ Original-System nicht vollständig! Abbruch.")
            return False
            
        # 2. Erstelle Struktur
        self.create_directory_structure()
        
        # 3. Kopiere kritische Dateien
        self.copy_critical_files()
        
        # 4. Erstelle venv
        self.create_virtual_environment()
        
        # 5. Erstelle Wrapper
        self.create_wrapper_modules()
        
        # 6. Erstelle Test-Script
        self.create_test_script()
        
        # 7. Erstelle README
        self.create_readme()
        
        print("\n" + "=" * 60)
        print("✅ HEXAGONAL PARALLEL SETUP KOMPLETT!")
        print("=" * 60)
        print("\nNächste Schritte:")
        print("1. cd D:\\MCP Mods\\HAK_GAL_HEXAGONAL")
        print("2. activate_hexa.bat")
        print("3. pip install flask torch numpy")
        print("4. python test_parallel.py")
        print("\nOriginal System bleibt UNVERÄNDERT auf Port 5000!")
        print("Hexagonal Development auf Port 5001!")
        
        return True

if __name__ == "__main__":
    setup = HexagonalSetup()
    setup.run()
