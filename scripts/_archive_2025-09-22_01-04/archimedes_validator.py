#!/usr/bin/env python3
"""
Archimedes Engine JSON Schema Validator
========================================
Validiert die generierten Artefakte gegen ihre JSON Schemas.
Erstellt von Claude basierend auf GPT5's Schema-Definitionen.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema nicht installiert!")
    print("Installiere mit: pip install jsonschema")
    sys.exit(1)

class ArchimedesValidator:
    """Validiert Archimedes Engine Outputs gegen JSON Schemas"""
    
    def __init__(self, project_root: Path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL")):
        self.project_root = project_root
        self.schemas_dir = project_root / "docs" / "schemas"
        self.artefacts_dir = project_root
        
        # Schema-Dateien
        self.hypotheses_schema_path = self.schemas_dir / "archimedes_hypotheses.schema.json"
        self.designs_schema_path = self.schemas_dir / "archimedes_experimental_designs.schema.json"
        
        # Artefakt-Dateien
        self.hypotheses_file = self.artefacts_dir / "hypotheses.json"
        self.designs_file = self.artefacts_dir / "experimental_designs.json"
        
    def load_schema(self, schema_path: Path) -> Dict[str, Any]:
        """Lade JSON Schema von Datei"""
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema nicht gefunden: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_data(self, data_path: Path) -> Any:
        """Lade JSON-Daten von Datei"""
        if not data_path.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {data_path}")
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_file(self, data_path: Path, schema_path: Path) -> Tuple[bool, str]:
        """Validiere eine JSON-Datei gegen ein Schema"""
        try:
            schema = self.load_schema(schema_path)
            data = self.load_data(data_path)
            
            # Validierung
            validate(instance=data, schema=schema)
            
            return True, f"✅ Validierung erfolgreich fuer {data_path.name}"
            
        except FileNotFoundError as e:
            return False, f"❌ Datei-Fehler: {e}"
        except ValidationError as e:
            return False, f"❌ Validierungs-Fehler in {data_path.name}:\n   {e.message}"
        except json.JSONDecodeError as e:
            return False, f"❌ JSON-Parse-Fehler in {data_path.name}:\n   {e}"
        except Exception as e:
            return False, f"❌ Unerwarteter Fehler: {e}"
    
    def validate_all(self) -> bool:
        """Validiere alle Archimedes Artefakte"""
        print("=" * 60)
        print("ARCHIMEDES ENGINE JSON SCHEMA VALIDATION")
        print("=" * 60)
        
        all_valid = True
        
        # Validiere Hypothesen
        print("\n1. Validiere hypotheses.json...")
        valid, message = self.validate_file(self.hypotheses_file, self.hypotheses_schema_path)
        print(message)
        all_valid = all_valid and valid
        
        if valid:
            # Zusaetzliche Statistiken
            data = self.load_data(self.hypotheses_file)
            print(f"   - Anzahl Hypothesen: {len(data)}")
            llm_origins = set(h.get('llm_origin', 'Unknown') for h in data)
            print(f"   - LLM Sources: {', '.join(llm_origins)}")
        
        # Validiere Experimental Designs
        print("\n2. Validiere experimental_designs.json...")
        valid, message = self.validate_file(self.designs_file, self.designs_schema_path)
        print(message)
        all_valid = all_valid and valid
        
        if valid:
            # Zusaetzliche Statistiken
            data = self.load_data(self.designs_file)
            print(f"   - Anzahl Designs: {len(data)}")
            llm_origins = set(d.get('llm_origin', 'Unknown') for d in data)
            print(f"   - LLM Sources: {', '.join(llm_origins)}")
            
            # Pruefe ob alle hypothesis_ids referenziert sind
            hypo_ids = set(d.get('hypothesis_id', '') for d in data)
            print(f"   - Referenzierte Hypothesen: {', '.join(sorted(hypo_ids))}")
        
        # Zusammenfassung
        print("\n" + "=" * 60)
        if all_valid:
            print("✅ ALLE VALIDIERUNGEN ERFOLGREICH!")
            print("Die Archimedes Engine Outputs entsprechen den Schemas.")
        else:
            print("❌ VALIDIERUNG FEHLGESCHLAGEN!")
            print("Bitte korrigiere die Fehler und versuche es erneut.")
        print("=" * 60)
        
        return all_valid
    
    def add_to_self_check(self):
        """Fuege Validierung zu self_check.py hinzu"""
        self_check_path = self.project_root / "self_check.py"
        
        if not self_check_path.exists():
            print(f"⚠️  self_check.py nicht gefunden: {self_check_path}")
            return
        
        # TODO: Integration in self_check.py
        print("\n📝 Integration in self_check.py:")
        print("   Fuege folgende Zeile zu self_check.py hinzu:")
        print("   from archimedes_validator import ArchimedesValidator")
        print("   validator = ArchimedesValidator()")
        print("   validator.validate_all()")

def main():
    """Hauptfunktion"""
    validator = ArchimedesValidator()
    success = validator.validate_all()
    
    # Optional: Integration-Hinweis
    if success:
        validator.add_to_self_check()
    
    # Exit-Code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
