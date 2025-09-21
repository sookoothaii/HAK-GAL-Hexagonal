#!/usr/bin/env python3
"""
HAK-GAL Knowledge Growth Monitor & Test Suite
==============================================
Enhanced test with real-time metrics and database monitoring
Shows facts/minute, total facts, and system activity

Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import requests
import json
import time
import re
import sqlite3
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = 'http://localhost:5002'
DATABASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'
OUTPUT_FILE = f'knowledge_growth_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

# ANSI Color codes for better visualization
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

@dataclass
class SystemMetrics:
    """Real-time system metrics"""
    start_time: datetime
    initial_facts: int
    current_facts: int
    facts_added_session: int
    facts_per_minute: float
    queries_processed: int
    success_rate: float
    avg_response_time: float
    
    def update(self, db_facts: int):
        """Update metrics with current database count"""
        self.current_facts = db_facts
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        if elapsed > 0:
            self.facts_per_minute = self.facts_added_session / elapsed

@dataclass
class QueryResult:
    """Results from a single query"""
    query: str
    query_type: str
    success: bool
    response_time_ms: float
    neural_confidence: float
    kb_facts_found: int
    response_text: str
    suggested_facts: List[str]
    facts_added: int = 0
    facts_duplicates: int = 0
    facts_errors: int = 0
    facts_invalid: int = 0
    error: str = ""

class KnowledgeGrowthMonitor:
    """
    Advanced test suite with real-time metrics and monitoring
    """
    
    def __init__(self, auto_add_facts: bool = True):
        self.results: List[QueryResult] = []
        self.test_pairs = self._create_test_pairs()
        self.auto_add_facts = auto_add_facts
        
        # Session counters
        self.total_facts_added = 0
        self.total_duplicates = 0
        self.total_errors = 0
        self.total_invalid = 0
        
        # Initialize metrics
        self.metrics = self._initialize_metrics()
        self.test_start_time = None
        
    def _get_database_fact_count(self) -> int:
        """Get current fact count directly from database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Could not read database directly: {e}{Colors.RESET}")
            return 0
    
    def _get_facts_by_source(self) -> Dict[str, int]:
        """Get fact count by source"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM facts 
                GROUP BY source
            """)
            results = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
            return results
        except:
            return {}
    
    def _initialize_metrics(self) -> SystemMetrics:
        """Initialize system metrics"""
        initial_facts = self._get_database_fact_count()
        return SystemMetrics(
            start_time=datetime.now(),
            initial_facts=initial_facts,
            current_facts=initial_facts,
            facts_added_session=0,
            facts_per_minute=0.0,
            queries_processed=0,
            success_rate=0.0,
            avg_response_time=0.0
        )
    
    def _print_dashboard(self):
        """Print real-time dashboard with metrics"""
        # Clear previous lines (simple approach)
        print("\n" + "="*80)
        print(f"{Colors.BOLD}{Colors.CYAN}📊 KNOWLEDGE GROWTH MONITOR - LIVE METRICS{Colors.RESET}")
        print("="*80)
        
        # Get current database stats
        current_facts = self._get_database_fact_count()
        facts_by_source = self._get_facts_by_source()
        
        # Calculate metrics
        elapsed_time = (datetime.now() - self.metrics.start_time).total_seconds()
        elapsed_minutes = elapsed_time / 60
        facts_added = current_facts - self.metrics.initial_facts
        facts_per_minute = facts_added / elapsed_minutes if elapsed_minutes > 0 else 0
        
        # Database Stats
        print(f"\n{Colors.BOLD}📦 DATABASE STATUS:{Colors.RESET}")
        print(f"  Total Facts:        {Colors.GREEN}{current_facts:,}{Colors.RESET}")
        print(f"  Initial Facts:      {self.metrics.initial_facts:,}")
        print(f"  Growth This Session: {Colors.GREEN}+{facts_added}{Colors.RESET}")
        
        # Source breakdown
        if facts_by_source:
            print(f"\n{Colors.BOLD}📝 FACTS BY SOURCE:{Colors.RESET}")
            for source, count in sorted(facts_by_source.items(), key=lambda x: x[1], reverse=True)[:3]:
                if source == 'LLM_suggestion':
                    print(f"  {source}: {Colors.CYAN}{count:,}{Colors.RESET} ← Our additions!")
                else:
                    print(f"  {source}: {count:,}")
        
        # Performance Metrics
        print(f"\n{Colors.BOLD}⚡ PERFORMANCE METRICS:{Colors.RESET}")
        print(f"  Facts/Minute:       {Colors.YELLOW}{facts_per_minute:.1f}{Colors.RESET}")
        print(f"  Elapsed Time:       {elapsed_minutes:.1f} minutes")
        print(f"  Queries Processed:  {self.metrics.queries_processed}")
        
        if self.metrics.avg_response_time > 0:
            print(f"  Avg Response Time:  {self.metrics.avg_response_time:.0f}ms")
        
        # Session Stats
        print(f"\n{Colors.BOLD}📈 SESSION STATISTICS:{Colors.RESET}")
        print(f"  Facts Added:     {Colors.GREEN}{self.total_facts_added}{Colors.RESET}")
        print(f"  Duplicates:      {Colors.YELLOW}{self.total_duplicates}{Colors.RESET}")
        print(f"  Errors:          {Colors.RED}{self.total_errors}{Colors.RESET}")
        print(f"  Invalid Filtered: {self.total_invalid}")
        
        # Success Rate
        total_attempts = self.total_facts_added + self.total_duplicates + self.total_errors
        if total_attempts > 0:
            success_rate = (self.total_facts_added / total_attempts) * 100
            print(f"  Success Rate:    {Colors.GREEN if success_rate > 50 else Colors.YELLOW}{success_rate:.1f}%{Colors.RESET}")
        
        # Projection
        if facts_per_minute > 0:
            facts_to_10k = max(0, 10000 - current_facts)
            minutes_to_10k = facts_to_10k / facts_per_minute
            hours_to_10k = minutes_to_10k / 60
            print(f"\n{Colors.BOLD}🎯 PROJECTION TO 10,000 FACTS:{Colors.RESET}")
            print(f"  Facts Needed: {facts_to_10k:,}")
            print(f"  ETA at current rate: {hours_to_10k:.1f} hours")
        
        print("="*80)
    
    def _create_test_pairs(self) -> List[Tuple[str, str, str]]:
        """Create 20 test pairs: (domain, natural_query, symbolic_query)"""
        return [
            # Philosophy & History
            ("Philosophy", "Is Socrates a philosopher?", "IsA(Socrates, Philosopher)."),
            ("Philosophy", "Did Socrates influence Plato?", "Influenced(Socrates, Plato)."),
            ("History", "Was Napoleon from France?", "BornIn(Napoleon, France)."),
            ("History", "Did Rome conquer Gaul?", "Conquered(Rome, Gaul)."),
            
            # Technology & Computing
            ("Technology", "Does a computer have a CPU?", "HasPart(Computer, CPU)."),
            ("Technology", "Is Python a programming language?", "IsA(Python, ProgrammingLanguage)."),
            ("Computing", "Does software run on hardware?", "RunsOn(Software, Hardware)."),
            ("Computing", "Is an algorithm a procedure?", "IsA(Algorithm, Procedure)."),
            
            # Geography & Places
            ("Geography", "Is Berlin located in Germany?", "LocatedIn(Berlin, Germany)."),
            ("Geography", "Is the Pacific an ocean?", "IsA(Pacific, Ocean)."),
            ("Geography", "Does France border Spain?", "Borders(France, Spain)."),
            ("Geography", "Is Tokyo the capital of Japan?", "CapitalOf(Tokyo, Japan)."),
            
            # Science & Nature
            ("Science", "Is water a liquid?", "IsA(Water, Liquid)."),
            ("Biology", "Are birds animals?", "IsA(Birds, Animals)."),
            ("Physics", "Does gravity cause falling?", "Causes(Gravity, Falling)."),
            ("Chemistry", "Does hydrogen have one proton?", "HasProperty(Hydrogen, OneProton)."),
            
            # Mathematics & Logic
            ("Mathematics", "Is seven a prime number?", "IsA(Seven, PrimeNumber)."),
            ("Logic", "Does reasoning require thinking?", "Requires(Reasoning, Thinking)."),
            
            # Arts & Culture
            ("Literature", "Was Shakespeare a writer?", "IsA(Shakespeare, Writer)."),
            ("Music", "Is a piano an instrument?", "IsA(Piano, Instrument).")
        ]
    
    def _validate_and_fix_fact(self, fact: str) -> Optional[str]:
        """Validate and fix fact format"""
        if not fact or not fact.strip():
            return None
        
        fact = fact.strip()
        
        # Remove trailing period if exists
        if fact.endswith('.'):
            fact = fact[:-1]
        
        # Valid format check
        valid_pattern = r'^[A-Z][a-zA-Z0-9_]*\([A-Z][a-zA-Z0-9_]*(?:,\s*[A-Z][a-zA-Z0-9_]*)+\)$'
        if re.match(valid_pattern, fact):
            return fact + '.'
        
        # Single argument pattern
        single_arg_pattern = r'^([A-Z][a-zA-Z0-9_]*)\(([A-Z][a-zA-Z0-9_]*)\)$'
        match = re.match(single_arg_pattern, fact)
        if match:
            predicate, entity = match.groups()
            
            # Convert to proper format
            if predicate in ['Human', 'Person', 'Philosopher', 'Teacher', 'Greek', 'Roman']:
                return f"IsA({entity}, {predicate})."
            elif predicate in ['Mortal', 'Wise', 'Famous', 'Ancient']:
                return f"HasProperty({entity}, {predicate})."
            elif predicate.startswith('Studied'):
                subject = predicate[7:]
                if subject:
                    return f"Studied({entity}, {subject})."
            elif predicate.startswith('Taught'):
                subject = predicate[6:]
                if subject:
                    return f"Taught({entity}, {subject})."
            else:
                return f"{predicate}({entity}, True)."
        
        # Skip templates and complex logic
        if 'Entity1' in fact or 'Entity2' in fact or 'Predicate' in fact:
            return None
        if fact.startswith('ForAll') or fact.startswith('Exists') or '→' in fact:
            return None
        
        return None
    
    def _add_suggested_facts(self, suggested_facts: List[str], query_context: str) -> Tuple[int, int, int, int]:
        """Add suggested facts with monitoring"""
        if not self.auto_add_facts or not suggested_facts:
            return 0, 0, 0, 0
        
        added = 0
        duplicates = 0
        errors = 0
        invalid = 0
        
        print(f"      {Colors.CYAN}📥 Processing {len(suggested_facts)} facts...{Colors.RESET}")
        
        for i, fact in enumerate(suggested_facts, 1):
            # Validate and fix
            fixed_fact = self._validate_and_fix_fact(fact)
            
            if not fixed_fact:
                invalid += 1
                continue
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/facts",
                    json={
                        'statement': fixed_fact, 
                        'source': 'LLM_suggestion',
                        'confidence': 0.7
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.ok:
                    data = response.json()
                    if data.get('success'):
                        added += 1
                        print(f"      {Colors.GREEN}✅ [{i}/{len(suggested_facts)}] Added: {fixed_fact}{Colors.RESET}")
                    else:
                        message = data.get('message', '')
                        if 'exists' in message.lower() or 'duplicate' in message.lower():
                            duplicates += 1
                        else:
                            errors += 1
                elif response.status_code == 409:
                    duplicates += 1
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
            
            time.sleep(0.03)  # Small delay
        
        # Update session counters
        self.total_facts_added += added
        self.total_duplicates += duplicates
        self.total_errors += errors
        self.total_invalid += invalid
        
        return added, duplicates, errors, invalid
    
    def _test_query(self, query: str, query_type: str) -> QueryResult:
        """Test a single query"""
        start_time = time.time()
        
        try:
            # Reason endpoint
            response = requests.post(
                f"{BACKEND_URL}/api/reason",
                json={'query': query},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if response.ok:
                data = response.json()
                
                # Get LLM suggestions
                print(f"      {Colors.BLUE}🔍 Getting LLM suggestions...{Colors.RESET}")
                suggested_facts = []
                
                try:
                    explanation_response = requests.post(
                        f"{BACKEND_URL}/api/llm/get-explanation",
                        json={'topic': query, 'context_facts': []},
                        headers={'Content-Type': 'application/json'},
                        timeout=20
                    )
                    
                    if explanation_response.ok:
                        exp_data = explanation_response.json()
                        raw_facts = [
                            fact.get('fact', '') for fact in exp_data.get('suggested_facts', [])
                            if fact.get('fact', '').strip()
                        ]
                        suggested_facts = [
                            f for f in raw_facts 
                            if not ('Entity1' in f and 'Entity2' in f and 'Predicate' in f)
                        ]
                        print(f"      {Colors.GREEN}📝 Got {len(suggested_facts)} suggestions{Colors.RESET}")
                except:
                    pass
                
                # KB search
                kb_facts_found = 0
                try:
                    search_response = requests.post(
                        f"{BACKEND_URL}/api/search",
                        json={'query': query, 'limit': 10},
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    if search_response.ok:
                        search_data = search_response.json()
                        kb_facts_found = len(search_data.get('results', []))
                except:
                    pass
                
                # Add facts
                facts_added = 0
                facts_duplicates = 0
                facts_errors = 0
                facts_invalid = 0
                
                if self.auto_add_facts and suggested_facts:
                    facts_added, facts_duplicates, facts_errors, facts_invalid = self._add_suggested_facts(
                        suggested_facts, query
                    )
                
                # Update metrics
                self.metrics.queries_processed += 1
                
                return QueryResult(
                    query=query,
                    query_type=query_type,
                    success=True,
                    response_time_ms=response_time_ms,
                    neural_confidence=data.get('confidence', 0.0),
                    kb_facts_found=kb_facts_found,
                    response_text="",
                    suggested_facts=suggested_facts,
                    facts_added=facts_added,
                    facts_duplicates=facts_duplicates,
                    facts_errors=facts_errors,
                    facts_invalid=facts_invalid
                )
            else:
                return QueryResult(
                    query=query,
                    query_type=query_type,
                    success=False,
                    response_time_ms=response_time_ms,
                    neural_confidence=0.0,
                    kb_facts_found=0,
                    response_text="",
                    suggested_facts=[],
                    error=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            return QueryResult(
                query=query,
                query_type=query_type,
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                neural_confidence=0.0,
                kb_facts_found=0,
                response_text="",
                suggested_facts=[],
                error=str(e)
            )
    
    def _test_backend_connectivity(self) -> bool:
        """Test backend connectivity"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.ok:
                data = response.json()
                print(f"{Colors.GREEN}✅ Backend online: {data.get('status', 'unknown')}{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}❌ Backend health check failed{Colors.RESET}")
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Backend not accessible: {e}{Colors.RESET}")
            return False
    
    def run_monitored_test_suite(self):
        """Run test suite with monitoring"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║     HAK-GAL KNOWLEDGE GROWTH MONITOR & TEST SUITE         ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        
        print(f"Testing {len(self.test_pairs)} question pairs")
        print(f"Backend: {BACKEND_URL}")
        print(f"Database: {DATABASE_PATH}")
        print(f"Mode: {Colors.GREEN if self.auto_add_facts else Colors.YELLOW}{'AUTO-ADD ENABLED' if self.auto_add_facts else 'READ-ONLY'}{Colors.RESET}")
        print("="*60)
        
        # Test connectivity
        if not self._test_backend_connectivity():
            return False
        
        # Show initial dashboard
        self._print_dashboard()
        
        print(f"\n{Colors.BOLD}🚀 STARTING TEST SUITE...{Colors.RESET}\n")
        self.test_start_time = datetime.now()
        
        total_tests = len(self.test_pairs) * 2
        current_test = 0
        
        # Progress tracking
        for domain, natural_query, symbolic_query in self.test_pairs:
            current_test += 1
            
            # Print dashboard every 5 tests
            if current_test % 5 == 0:
                self._print_dashboard()
            
            print(f"\n{Colors.BOLD}[{current_test:2d}/{total_tests}] {domain}:{Colors.RESET}")
            
            # Natural query
            print(f"   {Colors.CYAN}🧠 Natural: {natural_query}{Colors.RESET}")
            natural_result = self._test_query(natural_query, "natural")
            self.results.append(natural_result)
            
            if natural_result.success:
                conf_color = Colors.GREEN if natural_result.neural_confidence > 0.5 else Colors.YELLOW
                print(f"      {conf_color}Confidence: {natural_result.neural_confidence:.1%}{Colors.RESET}, "
                      f"Time: {natural_result.response_time_ms:.0f}ms")
                if natural_result.facts_added > 0:
                    print(f"      {Colors.GREEN}💾 Added {natural_result.facts_added} facts!{Colors.RESET}")
            
            time.sleep(0.2)
            
            current_test += 1
            
            # Symbolic query
            print(f"   {Colors.YELLOW}⚡ Symbolic: {symbolic_query}{Colors.RESET}")
            symbolic_result = self._test_query(symbolic_query, "symbolic")
            self.results.append(symbolic_result)
            
            if symbolic_result.success:
                conf_color = Colors.GREEN if symbolic_result.neural_confidence > 0.5 else Colors.YELLOW
                print(f"      {conf_color}Confidence: {symbolic_result.neural_confidence:.1%}{Colors.RESET}, "
                      f"Time: {symbolic_result.response_time_ms:.0f}ms")
                if symbolic_result.facts_added > 0:
                    print(f"      {Colors.GREEN}💾 Added {symbolic_result.facts_added} facts!{Colors.RESET}")
            
            # Show pair summary
            if natural_result.success and symbolic_result.success:
                total_added = natural_result.facts_added + symbolic_result.facts_added
                if total_added > 0:
                    current_db_facts = self._get_database_fact_count()
                    print(f"      {Colors.BOLD}📊 Pair Total: +{total_added} facts "
                          f"(DB now: {current_db_facts:,}){Colors.RESET}")
            
            time.sleep(0.1)
        
        # Final dashboard
        print(f"\n{Colors.BOLD}{Colors.CYAN}FINAL RESULTS:{Colors.RESET}")
        self._print_dashboard()
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_final_summary()
        
        return True
    
    def _save_results(self):
        """Save detailed results"""
        final_facts = self._get_database_fact_count()
        elapsed_time = (datetime.now() - self.test_start_time).total_seconds()
        
        results_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'backend_url': BACKEND_URL,
                'database_path': DATABASE_PATH,
                'test_duration_seconds': elapsed_time,
                'initial_facts': self.metrics.initial_facts,
                'final_facts': final_facts,
                'facts_added': final_facts - self.metrics.initial_facts,
                'facts_per_minute': (final_facts - self.metrics.initial_facts) / (elapsed_time / 60),
                'total_queries': len(self.results),
                'successful_queries': len([r for r in self.results if r.success]),
                'total_facts_added': self.total_facts_added,
                'total_duplicates': self.total_duplicates,
                'total_errors': self.total_errors,
                'total_invalid': self.total_invalid
            },
            'results': [
                {
                    'query': r.query,
                    'query_type': r.query_type,
                    'success': r.success,
                    'response_time_ms': r.response_time_ms,
                    'neural_confidence': r.neural_confidence,
                    'kb_facts_found': r.kb_facts_found,
                    'facts_added': r.facts_added,
                    'facts_duplicates': r.facts_duplicates,
                    'facts_errors': r.facts_errors,
                    'facts_invalid': r.facts_invalid,
                    'error': r.error
                }
                for r in self.results
            ]
        }
        
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print(f"\n{Colors.GREEN}💾 Results saved to: {OUTPUT_FILE}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to save results: {e}{Colors.RESET}")
    
    def _print_final_summary(self):
        """Print final summary with key metrics"""
        final_facts = self._get_database_fact_count()
        growth = final_facts - self.metrics.initial_facts
        elapsed = (datetime.now() - self.test_start_time).total_seconds() / 60
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}✨ TEST COMPLETED SUCCESSFULLY ✨{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}📊 FINAL METRICS:{Colors.RESET}")
        print(f"  Database Growth:    {Colors.GREEN}+{growth} facts{Colors.RESET}")
        print(f"  Final Total:        {Colors.GREEN}{final_facts:,} facts{Colors.RESET}")
        print(f"  Facts/Minute:       {Colors.YELLOW}{growth/elapsed:.1f}{Colors.RESET}")
        print(f"  Test Duration:      {elapsed:.1f} minutes")
        print(f"  Success Rate:       {(self.total_facts_added/(self.total_facts_added+self.total_errors+self.total_duplicates)*100 if (self.total_facts_added+self.total_errors+self.total_duplicates) > 0 else 0):.1f}%")
        
        if growth > 0:
            print(f"\n{Colors.BOLD}🎯 ACHIEVEMENT UNLOCKED:{Colors.RESET}")
            if growth > 200:
                print(f"  {Colors.GREEN}🏆 MEGA GROWTH: Added {growth} facts in one session!{Colors.RESET}")
            elif growth > 100:
                print(f"  {Colors.GREEN}🥇 SUPER GROWTH: Added {growth} facts!{Colors.RESET}")
            elif growth > 50:
                print(f"  {Colors.GREEN}🥈 GREAT GROWTH: Added {growth} facts!{Colors.RESET}")
            else:
                print(f"  {Colors.GREEN}🥉 GOOD START: Added {growth} facts!{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}Next: Run 'python analyze_database.py' for detailed analysis{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")

def main():
    """Main execution"""
    import sys
    
    # Parse arguments
    auto_add = '--no-add' not in sys.argv
    
    print(f"\n{Colors.BOLD}")
    if auto_add:
        print(f"{Colors.GREEN}🔥 AUTO-ADD MODE: Facts will be added to database{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}📋 READ-ONLY MODE: No facts will be added{Colors.RESET}")
    print(f"{Colors.RESET}")
    
    monitor = KnowledgeGrowthMonitor(auto_add_facts=auto_add)
    
    try:
        success = monitor.run_monitored_test_suite()
        if not success:
            print(f"\n{Colors.RED}💥 Test failed - check backend{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏹️ Test interrupted by user{Colors.RESET}")
        monitor._print_dashboard()
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
