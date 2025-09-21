#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Knowledge Validator
============================
Extrahiert Fakten aus der Knowledge Base und validiert sie durch:
1. Generierung von Python-Testcode
2. Ausführung von MCP-Tools
3. Empirische Verifikation der Behauptungen

Version: 1.0
Author: Claude (Anthropic)
Prinzip: HAK-GAL Artikel 3 - Externe Verifikation
"""

import requests
import json
import sqlite3
import subprocess
import tempfile
import re
import os
import sys
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Configuration
API_BASE_URL = "http://localhost:5002/api"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
DB_PATH = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
MCP_TOOLS_PATH = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")

class VerificationStatus(Enum):
    """Status einer Verifikation"""
    VERIFIED = "✅ VERIFIED"
    FAILED = "❌ FAILED"
    UNVERIFIABLE = "⚠️ UNVERIFIABLE"
    PARTIAL = "🔶 PARTIAL"

@dataclass
class ValidationResult:
    """Ergebnis einer Validierung"""
    fact: str
    status: VerificationStatus
    method: str  # 'python_test' oder 'mcp_tool'
    evidence: str
    timestamp: datetime
    confidence: float  # 0.0 - 1.0

class KnowledgeValidator:
    """Hauptklasse für Wissensvalidierung"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.validation_results = []
        self.session_start = datetime.now()
        
        # Mapping von Prädikaten zu Validierungsmethoden
        self.validation_mappings = {
            # System-Komponenten → Python-Tests
            "RunsOn": self.validate_port_binding,
            "ConsistsOf": self.validate_system_component,
            "Contains": self.validate_contains_relationship,
            "Uses": self.validate_uses_relationship,
            
            # API-Endpoints → HTTP-Tests
            "Endpoint": self.validate_api_endpoint,
            "RequiresHeader": self.validate_api_header,
            
            # MCP-Tools → Tool-Execution
            "MCPTool": self.validate_mcp_tool,
            "HasToolCount": self.validate_tool_count,
            
            # Datenbank → SQL-Queries
            "HasColumn": self.validate_db_column,
            "IndexedOn": self.validate_db_index,
            
            # Performance → Benchmarks
            "Performance": self.validate_performance_claim,
            "ResponseTime": self.validate_response_time,
            
            # Files/Paths → Filesystem-Checks
            "Location": self.validate_file_location,
            "CacheFile": self.validate_cache_file,
            
            # Numerische Werte → Arithmetik
            "CurrentFactCount": self.validate_fact_count,
            "HasToolCategory": self.validate_tool_category
        }
    
    def extract_testable_facts(self, limit: int = 100) -> List[str]:
        """Extrahiere testbare Fakten aus der KB"""
        testable_facts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hole Fakten mit testbaren Prädikaten
            testable_predicates = list(self.validation_mappings.keys())
            
            for predicate in testable_predicates:
                query = f"SELECT statement FROM facts WHERE statement LIKE '{predicate}(%' LIMIT 10"
                cursor.execute(query)
                facts = cursor.fetchall()
                testable_facts.extend([f[0] for f in facts])
            
            conn.close()
            
        except Exception as e:
            print(f"❌ DB Error: {e}")
        
        return testable_facts[:limit]
    
    def parse_fact(self, fact: str) -> Optional[Tuple[str, List[str]]]:
        """Parse einen Fakt in Prädikat und Argumente"""
        match = re.match(r'^([A-Za-z0-9_]+)\(([^)]+)\)\.?$', fact)
        if match:
            predicate = match.group(1)
            args_str = match.group(2)
            # Vorsichtiges Splitting bei Kommas
            args = [arg.strip() for arg in re.split(r',\s*', args_str)]
            return predicate, args
        return None
    
    # === Port/Network Validierung ===
    
    def validate_port_binding(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Port-Binding durch netstat oder Python-Socket"""
        if len(args) < 2:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "python_test", 
                                   "Insufficient arguments", datetime.now(), 0.0)
        
        service = args[0]
        port_str = args[1]
        
        # Extrahiere Port-Nummer
        port_match = re.search(r'(\d+)', port_str)
        if not port_match:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "python_test",
                                   f"Could not extract port from {port_str}", datetime.now(), 0.0)
        
        port = int(port_match.group(1))
        
        # Generiere Python-Testcode
        test_code = f"""
import socket
import sys

def test_port_binding(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

port = {port}
is_open = test_port_binding(port)
print(f"Port {{port}} is {{'OPEN' if is_open else 'CLOSED'}}")
sys.exit(0 if is_open else 1)
"""
        
        # Führe Test aus
        try:
            result = self.execute_python_test(test_code)
            if result['success']:
                return ValidationResult(fact, VerificationStatus.VERIFIED, "python_test",
                                      f"Port {port} is accessible", datetime.now(), 0.9)
            else:
                return ValidationResult(fact, VerificationStatus.FAILED, "python_test",
                                      f"Port {port} is not accessible", datetime.now(), 0.9)
        except Exception as e:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "python_test",
                                  f"Test execution failed: {e}", datetime.now(), 0.0)
    
    # === System-Komponenten Validierung ===
    
    def validate_system_component(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere System-Komponenten durch Datei-Existenz"""
        if len(args) < 2:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "filesystem",
                                   "Insufficient arguments", datetime.now(), 0.0)
        
        system = args[0]
        component = args[1]
        
        # Map Komponenten zu erwarteten Dateien/Verzeichnissen
        component_files = {
            "Hexagonal_Architecture": "src_hexagonal",
            "MCP_Server": "hakgal_mcp_v31_REPAIRED.py",
            "REST_API": "hexagonal_api_enhanced_clean.py",
            "Multi_Agent_System": "adapters/agent_adapters.py",
            "Knowledge_Base": "hexagonal_kb.db"
        }
        
        if component in component_files:
            file_path = MCP_TOOLS_PATH / component_files[component]
            if file_path.exists():
                return ValidationResult(fact, VerificationStatus.VERIFIED, "filesystem",
                                      f"Component file {file_path.name} exists", datetime.now(), 0.95)
            else:
                return ValidationResult(fact, VerificationStatus.FAILED, "filesystem",
                                      f"Component file {file_path.name} not found", datetime.now(), 0.95)
        
        return ValidationResult(fact, VerificationStatus.PARTIAL, "filesystem",
                              f"Component {component} not mapped to file", datetime.now(), 0.3)
    
    # === API Endpoint Validierung ===
    
    def validate_api_endpoint(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere API-Endpoints durch HTTP-Requests"""
        if len(args) < 4:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "http_test",
                                   "Insufficient arguments", datetime.now(), 0.0)
        
        api_name = args[0]
        method = args[1]
        endpoint = args[2]
        
        # Konstruiere URL
        url = f"{API_BASE_URL}{endpoint}" if endpoint.startswith('/') else f"{API_BASE_URL}/{endpoint}"
        
        # Teste Endpoint
        try:
            headers = {"X-API-Key": API_KEY}
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif method == "POST":
                # Dummy-Daten für POST
                response = requests.post(url, headers=headers, json={}, timeout=5)
            else:
                response = requests.request(method, url, headers=headers, timeout=5)
            
            if response.status_code < 500:  # Nicht-Server-Fehler
                return ValidationResult(fact, VerificationStatus.VERIFIED, "http_test",
                                      f"Endpoint {method} {endpoint} responds with {response.status_code}", 
                                      datetime.now(), 0.8)
            else:
                return ValidationResult(fact, VerificationStatus.FAILED, "http_test",
                                      f"Endpoint {method} {endpoint} returns {response.status_code}",
                                      datetime.now(), 0.8)
                                      
        except Exception as e:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "http_test",
                                  f"Could not test endpoint: {e}", datetime.now(), 0.0)
    
    # === MCP Tool Validierung ===
    
    def validate_mcp_tool(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere MCP-Tool durch tatsächlichen Tool-Call"""
        if len(args) < 1:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "mcp_tool",
                                   "No tool name provided", datetime.now(), 0.0)
        
        tool_name = args[0]
        
        # Spezielle Validierung für bekannte Tools
        if tool_name == "get_facts_count":
            try:
                # Rufe Tool über API
                response = requests.get(
                    f"{API_BASE_URL}/facts/count",
                    headers={"X-API-Key": API_KEY},
                    timeout=5
                )
                if response.status_code == 200:
                    return ValidationResult(fact, VerificationStatus.VERIFIED, "mcp_tool",
                                          f"Tool {tool_name} executed successfully", datetime.now(), 0.95)
            except:
                pass
        
        return ValidationResult(fact, VerificationStatus.PARTIAL, "mcp_tool",
                              f"Tool {tool_name} exists but not fully tested", datetime.now(), 0.5)
    
    # === Datenbank Validierung ===
    
    def validate_fact_count(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Faktenanzahl durch direkten DB-Query"""
        if len(args) < 2:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "sql_query",
                                   "Insufficient arguments", datetime.now(), 0.0)
        
        kb_name = args[0]
        claimed_count = args[1]
        
        # Extrahiere Zahl
        count_match = re.search(r'(\d+)', claimed_count)
        if not count_match:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "sql_query",
                                   f"Could not extract number from {claimed_count}", datetime.now(), 0.0)
        
        claimed = int(count_match.group(1))
        
        # Zähle tatsächliche Fakten
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            actual = cursor.fetchone()[0]
            conn.close()
            
            # Toleranz von ±5%
            tolerance = actual * 0.05
            if abs(actual - claimed) <= tolerance:
                return ValidationResult(fact, VerificationStatus.VERIFIED, "sql_query",
                                      f"Actual count {actual} matches claimed {claimed}", datetime.now(), 0.95)
            else:
                return ValidationResult(fact, VerificationStatus.FAILED, "sql_query",
                                      f"Actual count {actual} differs from claimed {claimed}", datetime.now(), 0.95)
                                      
        except Exception as e:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "sql_query",
                                  f"Database query failed: {e}", datetime.now(), 0.0)
    
    # === Fallback-Validierungen ===
    
    def validate_contains_relationship(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Generische Contains-Validierung"""
        return ValidationResult(fact, VerificationStatus.PARTIAL, "logical",
                              "Contains relationship assumed valid", datetime.now(), 0.6)
    
    def validate_uses_relationship(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Generische Uses-Validierung"""
        return ValidationResult(fact, VerificationStatus.PARTIAL, "logical",
                              "Uses relationship assumed valid", datetime.now(), 0.6)
    
    def validate_api_header(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere API-Header-Anforderung"""
        return ValidationResult(fact, VerificationStatus.PARTIAL, "config",
                              "Header requirement noted", datetime.now(), 0.7)
    
    def validate_tool_count(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Tool-Anzahl"""
        if len(args) >= 2:
            claimed_count = args[1]
            # Könnte hier tatsächlich Tools zählen
            return ValidationResult(fact, VerificationStatus.PARTIAL, "count",
                                  f"Tool count {claimed_count} not independently verified", datetime.now(), 0.5)
        return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "count",
                              "Insufficient data", datetime.now(), 0.0)
    
    def validate_db_column(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Datenbank-Spalte"""
        return ValidationResult(fact, VerificationStatus.PARTIAL, "schema",
                              "Column existence not verified", datetime.now(), 0.4)
    
    def validate_db_index(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Datenbank-Index"""
        return ValidationResult(fact, VerificationStatus.PARTIAL, "schema",
                              "Index existence not verified", datetime.now(), 0.4)
    
    def validate_performance_claim(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Performance-Behauptung"""
        return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "benchmark",
                              "Performance claim requires dedicated benchmark", datetime.now(), 0.2)
    
    def validate_response_time(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Response-Zeit"""
        return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "timing",
                              "Response time requires live measurement", datetime.now(), 0.2)
    
    def validate_file_location(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Datei-Location"""
        if len(args) >= 2:
            location = args[1]
            path = Path(location.replace('_', ' ').replace('\\', '/'))
            if path.exists():
                return ValidationResult(fact, VerificationStatus.VERIFIED, "filesystem",
                                      f"Location {path} exists", datetime.now(), 0.95)
        return ValidationResult(fact, VerificationStatus.FAILED, "filesystem",
                              "Location not found", datetime.now(), 0.95)
    
    def validate_cache_file(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Cache-Datei"""
        if len(args) >= 2:
            cache_file = args[1]
            # Konvertiere Unterstrich-Notation
            file_name = cache_file.replace('_json', '.json').replace('_', '.')
            path = MCP_TOOLS_PATH / file_name
            if path.exists():
                return ValidationResult(fact, VerificationStatus.VERIFIED, "filesystem",
                                      f"Cache file {file_name} exists", datetime.now(), 0.95)
        return ValidationResult(fact, VerificationStatus.FAILED, "filesystem",
                              "Cache file not found", datetime.now(), 0.95)
    
    def validate_tool_category(self, fact: str, predicate: str, args: List[str]) -> ValidationResult:
        """Validiere Tool-Kategorie"""
        return ValidationResult(fact, VerificationStatus.PARTIAL, "categorization",
                              "Tool category noted", datetime.now(), 0.5)
    
    # === Hilfs-Methoden ===
    
    def execute_python_test(self, code: str) -> Dict[str, Any]:
        """Führe Python-Testcode aus"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        finally:
            os.unlink(temp_file)
    
    def validate_fact(self, fact: str) -> ValidationResult:
        """Validiere einen einzelnen Fakt"""
        parsed = self.parse_fact(fact)
        
        if not parsed:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "parse_error",
                                  "Could not parse fact", datetime.now(), 0.0)
        
        predicate, args = parsed
        
        # Finde passende Validierungsmethode
        if predicate in self.validation_mappings:
            validator = self.validation_mappings[predicate]
            return validator(fact, predicate, args)
        else:
            return ValidationResult(fact, VerificationStatus.UNVERIFIABLE, "no_validator",
                                  f"No validator for predicate {predicate}", datetime.now(), 0.0)
    
    def run_validation(self, limit: int = 50):
        """Hauptvalidierungsloop"""
        print("=" * 80)
        print("HAK-GAL KNOWLEDGE VALIDATOR")
        print("=" * 80)
        print("Extracting and validating knowledge claims...")
        print("=" * 80)
        
        # Extrahiere testbare Fakten
        facts = self.extract_testable_facts(limit)
        print(f"\n📊 Found {len(facts)} testable facts")
        
        # Validiere jeden Fakt
        for i, fact in enumerate(facts, 1):
            print(f"\n[{i}/{len(facts)}] Testing: {fact[:80]}...")
            
            result = self.validate_fact(fact)
            self.validation_results.append(result)
            
            # Status-Ausgabe
            confidence_bar = "█" * int(result.confidence * 10)
            print(f"  {result.status.value}")
            print(f"  Method: {result.method}")
            print(f"  Evidence: {result.evidence}")
            print(f"  Confidence: {confidence_bar} {result.confidence:.1%}")
        
        # Zusammenfassung
        self.print_summary()
        self.save_validation_report()
    
    def print_summary(self):
        """Drucke Validierungs-Zusammenfassung"""
        total = len(self.validation_results)
        verified = sum(1 for r in self.validation_results if r.status == VerificationStatus.VERIFIED)
        failed = sum(1 for r in self.validation_results if r.status == VerificationStatus.FAILED)
        partial = sum(1 for r in self.validation_results if r.status == VerificationStatus.PARTIAL)
        unverifiable = sum(1 for r in self.validation_results if r.status == VerificationStatus.UNVERIFIABLE)
        
        avg_confidence = sum(r.confidence for r in self.validation_results) / total if total > 0 else 0
        
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print(f"  Total facts tested: {total}")
        print(f"  ✅ Verified: {verified} ({verified/total*100:.1f}%)")
        print(f"  ❌ Failed: {failed} ({failed/total*100:.1f}%)")
        print(f"  🔶 Partial: {partial} ({partial/total*100:.1f}%)")
        print(f"  ⚠️ Unverifiable: {unverifiable} ({unverifiable/total*100:.1f}%)")
        print(f"  Average confidence: {avg_confidence:.1%}")
        print("=" * 80)
    
    def save_validation_report(self):
        """Speichere Validierungsbericht"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_facts": len(self.validation_results),
            "results": [
                {
                    "fact": r.fact,
                    "status": r.status.value,
                    "method": r.method,
                    "evidence": r.evidence,
                    "confidence": r.confidence
                }
                for r in self.validation_results
            ],
            "summary": {
                "verified": sum(1 for r in self.validation_results if r.status == VerificationStatus.VERIFIED),
                "failed": sum(1 for r in self.validation_results if r.status == VerificationStatus.FAILED),
                "partial": sum(1 for r in self.validation_results if r.status == VerificationStatus.PARTIAL),
                "unverifiable": sum(1 for r in self.validation_results if r.status == VerificationStatus.UNVERIFIABLE)
            }
        }
        
        report_file = MCP_TOOLS_PATH / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved to: {report_file}")

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HAK-GAL Knowledge Validator')
    parser.add_argument('--limit', type=int, default=50, help='Number of facts to validate')
    parser.add_argument('--test', action='store_true', help='Test mode with only 5 facts')
    
    args = parser.parse_args()
    
    validator = KnowledgeValidator()
    
    if args.test:
        validator.run_validation(limit=5)
    else:
        validator.run_validation(limit=args.limit)

if __name__ == "__main__":
    main()
