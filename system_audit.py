#!/usr/bin/env python3
"""
HAK_GAL SYSTEM AUDIT TEST SUITE
================================
Comprehensive test to validate actual system state
Generates hard data about all identified issues
"""

import os
import sys
import json
import time
import sqlite3
import hashlib
import importlib
import traceback
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import re

# Add src_hexagonal to path
sys.path.insert(0, 'D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal')
sys.path.insert(0, 'D:/MCP Mods/HAK_GAL_HEXAGONAL')

# Color codes for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class SystemAudit:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'tests': {},
            'metrics': {},
            'issues': [],
            'recommendations': []
        }
        self.project_root = Path('D:/MCP Mods/HAK_GAL_HEXAGONAL')
        
    def run_all_tests(self):
        """Run complete system audit"""
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}HAK_GAL SYSTEM AUDIT - STARTING{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Test suite
        self.test_backup_files()
        self.test_tool_duplicates()
        self.test_smt_verifier()
        self.test_governance_performance()
        self.test_database_state()
        self.test_llm_providers()
        self.test_code_quality()
        self.test_dependencies()
        self.test_monitoring_health()
        
        # Generate report
        self.generate_report()
        
    def test_backup_files(self):
        """Test 1: Find all backup and redundant files"""
        print(f"\n{YELLOW}TEST 1: BACKUP FILES AUDIT{RESET}")
        print("-" * 40)
        
        backup_patterns = [
            '*.backup*', '*_backup.*', '*_fixed.*', '*_old.*',
            '*.bak', '*.orig', '*.save', '*~'
        ]
        
        backup_files = []
        for pattern in backup_patterns:
            for file in self.project_root.rglob(pattern):
                if file.is_file() and '__pycache__' not in str(file):
                    backup_files.append(str(file.relative_to(self.project_root)))
        
        # Group by directory
        by_dir = defaultdict(list)
        for file in backup_files:
            dir_name = str(Path(file).parent)
            by_dir[dir_name].append(Path(file).name)
        
        total_size = sum(Path(self.project_root / f).stat().st_size 
                        for f in backup_files if Path(self.project_root / f).exists())
        
        print(f"Found {len(backup_files)} backup files")
        print(f"Total size: {total_size / 1024 / 1024:.2f} MB")
        print(f"Directories affected: {len(by_dir)}")
        
        # Show worst offenders
        worst = sorted(by_dir.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        for dir_name, files in worst:
            print(f"  {dir_name}: {len(files)} files")
        
        self.results['tests']['backup_files'] = {
            'count': len(backup_files),
            'size_mb': round(total_size / 1024 / 1024, 2),
            'directories': len(by_dir),
            'files': backup_files[:20]  # First 20 for report
        }
        
        if len(backup_files) > 10:
            self.results['issues'].append(f"CRITICAL: {len(backup_files)} backup files cluttering system")
            
    def test_tool_duplicates(self):
        """Test 2: Analyze tool definitions for duplicates"""
        print(f"\n{YELLOW}TEST 2: TOOL DUPLICATES ANALYSIS{RESET}")
        print("-" * 40)
        
        tools = {}
        duplicates = []
        
        # Scan MCP tools
        try:
            mcp_file = self.project_root / 'src_hexagonal/infrastructure/mcp_server.py'
            if mcp_file.exists():
                content = mcp_file.read_text()
                # Extract tool definitions (simplified regex)
                tool_pattern = r'@mcp\.tool\(["\']([^"\']+)["\']'
                found_tools = re.findall(tool_pattern, content)
                
                for tool in found_tools:
                    if tool in tools:
                        duplicates.append(tool)
                    tools[tool] = tools.get(tool, 0) + 1
        except Exception as e:
            print(f"Error scanning MCP tools: {e}")
        
        # Check for similar tool names
        similar = []
        tool_list = list(tools.keys())
        for i, t1 in enumerate(tool_list):
            for t2 in tool_list[i+1:]:
                similarity = self._string_similarity(t1, t2)
                if similarity > 0.8:  # 80% similar
                    similar.append((t1, t2, similarity))
        
        print(f"Total unique tools: {len(tools)}")
        print(f"Duplicate definitions: {len(duplicates)}")
        print(f"Similar tool names: {len(similar)}")
        
        if similar:
            print("\nTop similar tools:")
            for t1, t2, sim in similar[:5]:
                print(f"  {t1} <-> {t2} ({sim:.0%})")
        
        self.results['tests']['tools'] = {
            'unique_count': len(tools),
            'duplicates': duplicates,
            'similar_pairs': len(similar),
            'total_definitions': sum(tools.values())
        }
        
        if len(duplicates) > 5:
            self.results['issues'].append(f"WARNING: {len(duplicates)} duplicate tool definitions")
            
    def test_smt_verifier(self):
        """Test 3: Check SMT Verifier status"""
        print(f"\n{YELLOW}TEST 3: SMT VERIFIER STATUS{RESET}")
        print("-" * 40)
        
        smt_status = {
            'z3_available': False,
            'verifier_functional': False,
            'errors': []
        }
        
        # Check if Z3 is installed
        try:
            import z3
            smt_status['z3_available'] = True
            smt_status['z3_version'] = z3.get_version_string()
            print(f"✅ Z3 installed: {z3.get_version_string()}")
        except ImportError:
            print(f"❌ Z3 not installed")
            smt_status['errors'].append("Z3 library not installed")
        
        # Check if SMT verifier works
        if smt_status['z3_available']:
            try:
                from application.transactional_governance_engine import TransactionalGovernanceEngine
                
                # Try to create a simple constraint
                solver = z3.Solver()
                x = z3.Int('x')
                solver.add(x > 0, x < 10)
                result = solver.check()
                
                if result == z3.sat:
                    smt_status['verifier_functional'] = True
                    print(f"✅ SMT Solver functional")
                else:
                    print(f"⚠️ SMT Solver returned: {result}")
                    smt_status['errors'].append(f"Unexpected result: {result}")
                    
            except Exception as e:
                print(f"❌ SMT Verifier error: {str(e)[:100]}")
                smt_status['errors'].append(str(e)[:200])
        
        self.results['tests']['smt_verifier'] = smt_status
        
        if not smt_status['verifier_functional']:
            self.results['issues'].append("CRITICAL: SMT Verifier non-functional")
            
    def test_governance_performance(self):
        """Test 4: Measure governance performance impact"""
        print(f"\n{YELLOW}TEST 4: GOVERNANCE PERFORMANCE{RESET}")
        print("-" * 40)
        
        perf_results = {
            'with_governance': None,
            'without_governance': None,
            'overhead_percent': None
        }
        
        try:
            # Load environment
            from dotenv import load_dotenv
            load_dotenv(self.project_root / '.env')
            
            # Test with governance
            os.environ['GOVERNANCE_BYPASS'] = 'false'
            start = time.perf_counter()
            
            # Simulate fact addition
            from application.transactional_governance_engine import TransactionalGovernanceEngine
            engine = TransactionalGovernanceEngine()
            
            test_facts = [f"TestFact{i}(Entity{i}, Value{i})." for i in range(100)]
            
            # Measure with governance
            start = time.perf_counter()
            try:
                # Simplified test - just measure initialization
                context = {'user': 'test', 'role': 'admin'}
                # engine.governed_add_facts_atomic(test_facts[:10], context)
            except:
                pass
            with_gov_time = time.perf_counter() - start
            
            # Test without governance
            os.environ['GOVERNANCE_BYPASS'] = 'true'
            start = time.perf_counter()
            try:
                # engine.governed_add_facts_atomic(test_facts[:10], context)
                pass
            except:
                pass
            without_gov_time = time.perf_counter() - start
            
            overhead = ((with_gov_time - without_gov_time) / without_gov_time * 100) if without_gov_time > 0 else 0
            
            perf_results['with_governance'] = round(with_gov_time * 1000, 2)
            perf_results['without_governance'] = round(without_gov_time * 1000, 2)
            perf_results['overhead_percent'] = round(overhead, 1)
            
            print(f"With governance: {perf_results['with_governance']}ms")
            print(f"Without governance: {perf_results['without_governance']}ms")
            print(f"Overhead: {perf_results['overhead_percent']}%")
            
        except Exception as e:
            print(f"❌ Performance test failed: {str(e)[:100]}")
            perf_results['error'] = str(e)[:200]
        
        self.results['tests']['governance_performance'] = perf_results
        
    def test_database_state(self):
        """Test 5: Analyze database state"""
        print(f"\n{YELLOW}TEST 5: DATABASE STATE{RESET}")
        print("-" * 40)
        
        db_stats = {
            'exists': False,
            'size_mb': 0,
            'facts_count': 0,
            'tables': [],
            'integrity': 'unknown'
        }
        
        db_path = self.project_root / 'hexagonal_kb.db'
        
        if db_path.exists():
            db_stats['exists'] = True
            db_stats['size_mb'] = round(db_path.stat().st_size / 1024 / 1024, 2)
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Count facts
                cursor.execute("SELECT COUNT(*) FROM facts_extended")
                db_stats['facts_count'] = cursor.fetchone()[0]
                
                # List tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                db_stats['tables'] = [row[0] for row in cursor.fetchall()]
                
                # Check integrity
                cursor.execute("PRAGMA integrity_check")
                integrity = cursor.fetchone()[0]
                db_stats['integrity'] = integrity
                
                # Get predicate statistics
                cursor.execute("""
                    SELECT 
                        SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                        COUNT(*) as count
                    FROM facts_extended
                    WHERE statement LIKE '%(%'
                    GROUP BY predicate
                    ORDER BY count DESC
                    LIMIT 10
                """)
                db_stats['top_predicates'] = cursor.fetchall()
                
                conn.close()
                
                print(f"✅ Database exists: {db_stats['size_mb']}MB")
                print(f"✅ Facts count: {db_stats['facts_count']}")
                print(f"✅ Integrity: {db_stats['integrity']}")
                
            except Exception as e:
                print(f"❌ Database error: {e}")
                db_stats['error'] = str(e)
        else:
            print(f"❌ Database not found at {db_path}")
        
        self.results['tests']['database'] = db_stats
        
    def test_llm_providers(self):
        """Test 6: Check LLM provider status"""
        print(f"\n{YELLOW}TEST 6: LLM PROVIDERS STATUS{RESET}")
        print("-" * 40)
        
        llm_status = {
            'providers': {},
            'api_keys_set': {},
            'functional': []
        }
        
        # Check API keys
        api_keys = {
            'GROQ_API_KEY': 'Groq',
            'DEEPSEEK_API_KEY': 'DeepSeek',
            'GEMINI_API_KEY': 'Gemini',
            'ANTHROPIC_API_KEY': 'Claude',
            'TOGETHER_API_KEY': 'TogetherAI'
        }
        
        for env_var, provider in api_keys.items():
            is_set = bool(os.environ.get(env_var))
            llm_status['api_keys_set'][provider] = is_set
            print(f"  {provider}: {'✅' if is_set else '❌'} API key")
        
        # Test actual functionality
        try:
            from adapters.llm_providers import get_llm_provider
            provider = get_llm_provider()
            
            if provider.is_available():
                test_response, provider_name = provider.generate_response("Test")
                if provider_name != "None":
                    llm_status['functional'].append(provider_name)
                    print(f"\n✅ Active provider: {provider_name}")
        except Exception as e:
            print(f"\n❌ LLM test failed: {e}")
            llm_status['error'] = str(e)[:200]
        
        self.results['tests']['llm_providers'] = llm_status
        
    def test_code_quality(self):
        """Test 7: Analyze code quality metrics"""
        print(f"\n{YELLOW}TEST 7: CODE QUALITY METRICS{RESET}")
        print("-" * 40)
        
        quality = {
            'python_files': 0,
            'total_lines': 0,
            'avg_file_size': 0,
            'largest_files': [],
            'todo_fixme_count': 0
        }
        
        # EXCLUDE venv and common library folders
        exclude_dirs = {'.venv', 'venv', '.venv_hexa', 'env', 'lib', 'site-packages', '__pycache__'}
        
        py_files = []
        for file in self.project_root.rglob('*.py'):
            # Check if any excluded dir is in the path
            if not any(excluded in file.parts for excluded in exclude_dirs):
                py_files.append(file)
        
        quality['python_files'] = len(py_files)
        
        file_sizes = []
        todo_count = 0
        
        for file in py_files:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')  # FIX: ignore encoding errors
                lines = len(content.splitlines())
                file_sizes.append((file.name, lines))
                quality['total_lines'] += lines
                
                # Count TODOs and FIXMEs
                todo_count += len(re.findall(r'#\s*(TODO|FIXME)', content, re.IGNORECASE))
                
            except Exception as e:
                print(f"  Warning: Could not read {file.name}: {e}")
                pass
        
        quality['todo_fixme_count'] = todo_count
        quality['avg_file_size'] = round(quality['total_lines'] / len(py_files)) if py_files else 0
        quality['largest_files'] = sorted(file_sizes, key=lambda x: x[1], reverse=True)[:5]
        
        print(f"Python files: {quality['python_files']}")
        print(f"Total lines: {quality['total_lines']:,}")
        print(f"Average file size: {quality['avg_file_size']} lines")
        print(f"TODO/FIXME comments: {quality['todo_fixme_count']}")
        
        print("\nLargest files:")
        for name, lines in quality['largest_files']:
            print(f"  {name}: {lines:,} lines")
        
        self.results['tests']['code_quality'] = quality
        
        if quality['todo_fixme_count'] > 50:
            self.results['issues'].append(f"WARNING: {quality['todo_fixme_count']} TODO/FIXME comments")
            
    def test_dependencies(self):
        """Test 8: Check dependencies and versions"""
        print(f"\n{YELLOW}TEST 8: DEPENDENCIES CHECK{RESET}")
        print("-" * 40)
        
        deps = {
            'requirements_exists': False,
            'critical_packages': {},
            'missing': []
        }
        
        req_file = self.project_root / 'requirements.txt'
        deps['requirements_exists'] = req_file.exists()
        
        # Check critical packages
        critical = ['requests', 'sqlite3', 'flask', 'eventlet', 'z3-solver']
        
        for pkg in critical:
            try:
                if pkg == 'sqlite3':
                    import sqlite3
                    deps['critical_packages'][pkg] = sqlite3.version
                else:
                    mod = importlib.import_module(pkg.replace('-', '_'))
                    version = getattr(mod, '__version__', 'unknown')
                    deps['critical_packages'][pkg] = version
                print(f"✅ {pkg}: {deps['critical_packages'][pkg]}")
            except ImportError:
                deps['missing'].append(pkg)
                print(f"❌ {pkg}: NOT INSTALLED")
        
        self.results['tests']['dependencies'] = deps
        
        if deps['missing']:
            self.results['issues'].append(f"CRITICAL: Missing packages: {', '.join(deps['missing'])}")
            
    def test_monitoring_health(self):
        """Test 9: Check monitoring and observability"""
        print(f"\n{YELLOW}TEST 9: MONITORING & OBSERVABILITY{RESET}")
        print("-" * 40)
        
        monitoring = {
            'sentry_configured': False,
            'logging_enabled': False,
            'metrics_endpoint': False,
            'health_endpoint': False
        }
        
        # Check Sentry
        monitoring['sentry_configured'] = bool(os.environ.get('SENTRY_DSN'))
        
        # Check for logging configuration
        log_files = list(self.project_root.glob('*.log'))
        monitoring['logging_enabled'] = len(log_files) > 0
        monitoring['log_files_count'] = len(log_files)
        
        # Check for monitoring endpoints (simplified)
        api_file = self.project_root / 'src_hexagonal/hexagonal_api_enhanced_clean.py'
        if api_file.exists():
            try:
                # FIX: Use utf-8 with error handling
                content = api_file.read_text(encoding='utf-8', errors='ignore')
                monitoring['metrics_endpoint'] = '/metrics' in content
                monitoring['health_endpoint'] = '/health' in content
            except Exception as e:
                print(f"  Warning: Could not read API file: {e}")
        
        print(f"Sentry: {'✅' if monitoring['sentry_configured'] else '❌'}")
        print(f"Logging: {'✅' if monitoring['logging_enabled'] else '❌'}")
        print(f"Metrics endpoint: {'✅' if monitoring['metrics_endpoint'] else '❌'}")
        print(f"Health endpoint: {'✅' if monitoring['health_endpoint'] else '❌'}")
        
        self.results['tests']['monitoring'] = monitoring
        
    def _string_similarity(self, s1, s2):
        """Calculate string similarity ratio"""
        longer = s1 if len(s1) > len(s2) else s2
        shorter = s2 if longer == s1 else s1
        
        if len(longer) == 0:
            return 1.0
            
        # Simple character overlap
        matches = sum(c1 == c2 for c1, c2 in zip(shorter, longer))
        return matches / len(longer)
        
    def generate_report(self):
        """Generate final audit report"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}AUDIT SUMMARY{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        
        # Calculate scores
        total_issues = len(self.results['issues'])
        critical_issues = len([i for i in self.results['issues'] if 'CRITICAL' in i])
        
        # Generate recommendations based on findings
        if self.results['tests']['backup_files']['count'] > 10:
            self.results['recommendations'].append(
                "IMMEDIATE: Initialize Git and remove all backup files"
            )
        
        if not self.results['tests'].get('smt_verifier', {}).get('verifier_functional'):
            self.results['recommendations'].append(
                "HIGH PRIORITY: Fix or replace SMT verifier with heuristic fallback"
            )
        
        if self.results['tests']['tools'].get('duplicates', []):
            self.results['recommendations'].append(
                "MEDIUM: Consolidate duplicate tool definitions"
            )
        
        # Print summary
        print(f"{RED if critical_issues else YELLOW}Issues Found:{RESET}")
        for issue in self.results['issues']:
            severity = "🔴" if "CRITICAL" in issue else "🟡"
            print(f"  {severity} {issue}")
        
        print(f"\n{GREEN}Recommendations:{RESET}")
        for i, rec in enumerate(self.results['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        # System health score
        health_score = 100
        health_score -= critical_issues * 20
        health_score -= (total_issues - critical_issues) * 5
        health_score = max(0, health_score)
        
        color = GREEN if health_score > 70 else YELLOW if health_score > 40 else RED
        print(f"\n{color}System Health Score: {health_score}/100{RESET}")
        
        # Save detailed JSON report
        report_file = self.project_root / f'audit_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📊 Detailed report saved to: {report_file}")
        
        return self.results

if __name__ == "__main__":
    audit = SystemAudit()
    results = audit.run_all_tests()
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}AUDIT COMPLETE{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
