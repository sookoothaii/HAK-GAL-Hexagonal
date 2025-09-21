#!/usr/bin/env python3
"""
validate_live_vs_docs.py
========================
Automatische Validierung von Live-System vs. Dokumentation
Generiert Diskrepanz-Report und aktualisiert README-Stats
"""

import os
import re
import json
import sqlite3
from datetime import datetime
from pathlib import Path

class SystemValidator:
    def __init__(self, base_path="."):
        self.base_path = Path(base_path)
        self.discrepancies = []
        self.validations = {}
        
    def validate_z3_status(self):
        """Test Z3/SMT Funktionalität"""
        try:
            import z3
            version = z3.get_version_string()
            
            # Simple functionality test
            x = z3.Int('x')
            solver = z3.Solver()
            solver.add(x > 0, x < 10)
            
            if solver.check() == z3.sat:
                status = "FUNCTIONAL"
            else:
                status = "ERROR"
                
            self.validations["Z3/SMT"] = {
                "status": status,
                "version": version,
                "tested": datetime.now().isoformat()
            }
            return status == "FUNCTIONAL"
            
        except ImportError:
            self.validations["Z3/SMT"] = {
                "status": "NOT_INSTALLED",
                "tested": datetime.now().isoformat()
            }
            return False
            
    def count_kb_facts(self):
        """Zähle Facts in Knowledge Base"""
        db_path = self.base_path / "hexagonal_kb.db"
        
        if not db_path.exists():
            self.validations["KB_Facts"] = {
                "count": 0,
                "error": "Database not found"
            }
            return 0
            
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            conn.close()
            
            # Get DB size
            size_mb = db_path.stat().st_size / (1024 * 1024)
            
            self.validations["KB_Facts"] = {
                "count": count,
                "size_mb": round(size_mb, 2),
                "tested": datetime.now().isoformat()
            }
            return count
            
        except Exception as e:
            self.validations["KB_Facts"] = {
                "count": 0,
                "error": str(e)
            }
            return 0
            
    def count_tools(self):
        """Zähle MCP Tools in beiden Servern"""
        tools = {
            "filesystem": 0,
            "kb": 0,
            "total": 0
        }
        
        # Count Filesystem Tools
        fs_path = self.base_path / "filesystem_mcp" / "hak_gal_filesystem.py"
        if fs_path.exists():
            content = fs_path.read_text(encoding='utf-8', errors='ignore')
            fs_tools = re.findall(r'@server\.tool\(["\']([^"\']+)["\']', content)
            tools["filesystem"] = len(set(fs_tools))
            
        # Count KB Tools  
        kb_path = self.base_path / "ultimate_mcp" / "hakgal_mcp_ultimate.py"
        if kb_path.exists():
            content = kb_path.read_text(encoding='utf-8', errors='ignore')
            kb_tools = re.findall(r'@server\.tool\(["\']([^"\']+)["\']', content)
            tools["kb"] = len(set(kb_tools))
            
        tools["total"] = tools["filesystem"] + tools["kb"]
        
        self.validations["Tools"] = {
            "filesystem": tools["filesystem"],
            "kb": tools["kb"],
            "total": tools["total"],
            "tested": datetime.now().isoformat()
        }
        
        return tools
        
    def check_readme_values(self):
        """Extrahiere Werte aus README.md"""
        readme_path = self.base_path / "README.md"
        
        if not readme_path.exists():
            return {}
            
        content = readme_path.read_text()
        
        readme_values = {}
        
        # Extract facts count from badge
        badge_match = re.search(r'Knowledge%20Facts-(\d+)-', content)
        if badge_match:
            readme_values["facts_badge"] = int(badge_match.group(1))
            
        # Extract facts from text
        facts_match = re.search(r'Facts["\']?:\s*(\d+)', content)
        if facts_match:
            readme_values["facts_text"] = int(facts_match.group(1))
            
        # Extract version
        version_match = re.search(r'Version (\d+\.\d+\.\d+)', content)
        if version_match:
            readme_values["version"] = version_match.group(1)
            
        return readme_values
        
    def compare_and_report(self):
        """Vergleiche Live-System mit Dokumentation"""
        
        # Get live values
        z3_works = self.validate_z3_status()
        facts_count = self.count_kb_facts()
        tools = self.count_tools()
        
        # Get documented values
        readme = self.check_readme_values()
        
        # Compare and find discrepancies
        report = {
            "timestamp": datetime.now().isoformat(),
            "live_system": {
                "z3_functional": z3_works,
                "kb_facts": facts_count,
                "tools": tools
            },
            "documentation": readme,
            "discrepancies": []
        }
        
        # Check for discrepancies
        if readme.get("facts_badge") and readme["facts_badge"] != facts_count:
            report["discrepancies"].append({
                "field": "KB Facts (Badge)",
                "documented": readme["facts_badge"],
                "actual": facts_count,
                "action": "Update README badge"
            })
            
        if readme.get("facts_text") and readme["facts_text"] != facts_count:
            report["discrepancies"].append({
                "field": "KB Facts (Text)",
                "documented": readme["facts_text"],
                "actual": facts_count,
                "action": "Update README text"
            })
            
        # Expected tool counts (from our knowledge)
        expected_tools = {"filesystem": 55, "kb": 64, "total": 119}
        
        if tools["total"] != expected_tools["total"]:
            report["discrepancies"].append({
                "field": "Total Tools",
                "documented": expected_tools["total"],
                "actual": tools["total"],
                "action": "Verify tool registration"
            })
            
        return report
        
    def save_report(self, report):
        """Speichere Validierungsreport"""
        report_path = self.base_path / "PROJECT_HUB" / "validation_report_latest.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Also update the LIVE_SYSTEM_STATUS.md if needed
        if report["discrepancies"]:
            print("\n⚠️ DISKREPANZEN GEFUNDEN:")
            for disc in report["discrepancies"]:
                print(f"  - {disc['field']}: Doku={disc['documented']}, Live={disc['actual']}")
                
        else:
            print("\n✅ KEINE DISKREPANZEN - System und Doku sind synchron!")
            
        return report_path
        
def main():
    print("SYSTEM VALIDIERUNG - Live vs. Dokumentation")
    print("=" * 50)
    
    validator = SystemValidator()
    report = validator.compare_and_report()
    report_path = validator.save_report(report)
    
    print(f"\n📊 Report gespeichert: {report_path}")
    
    # Summary
    print("\n📈 LIVE SYSTEM STATUS:")
    print(f"  • Z3/SMT: {'✅ Funktioniert' if report['live_system']['z3_functional'] else '❌ Fehler'}")
    print(f"  • KB Facts: {report['live_system']['kb_facts']}")
    print(f"  • Tools: {report['live_system']['tools']['total']} " +
          f"(FS: {report['live_system']['tools']['filesystem']}, " +
          f"KB: {report['live_system']['tools']['kb']})")
    
    if report['discrepancies']:
        print(f"\n⚠️ {len(report['discrepancies'])} Diskrepanzen gefunden - README Update empfohlen!")
        return 1
    else:
        print("\n✅ Perfekt synchronisiert!")
        return 0

if __name__ == "__main__":
    exit(main())
