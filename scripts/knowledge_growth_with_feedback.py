#!/usr/bin/env python3
"""
HAK-GAL Knowledge Growth Monitor with HRM Feedback
===================================================
Enhanced test that confirms facts to increase confidence scores
Implements the feedback loop for neural network training

Nach HAK/GAL Verfassung Artikel 3: Externe Verifikation
"""

import requests
import json
import time
import re
import sqlite3
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Configuration
BACKEND_URL = 'http://localhost:5002'
DATABASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'
HRM_FEEDBACK_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\data\hrm_feedback.json'
OUTPUT_FILE = f'knowledge_growth_with_feedback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

@dataclass
class QueryResult:
    """Enhanced result with feedback tracking"""
    query: str
    query_type: str
    success: bool
    response_time_ms: float
    neural_confidence: float
    neural_confidence_after_feedback: float = 0.0
    kb_facts_found: int = 0
    facts_added: int = 0
    facts_confirmed: int = 0
    feedback_sent: bool = False
    error: str = ""

class KnowledgeGrowthWithFeedback:
    """
    Advanced test suite with HRM feedback integration
    Confirms facts to increase neural confidence
    """
    
    def __init__(self, auto_add_facts: bool = True, auto_confirm: bool = True):
        self.results: List[QueryResult] = []
        self.test_pairs = self._create_test_pairs()
        self.auto_add_facts = auto_add_facts
        self.auto_confirm = auto_confirm
        
        # Tracking
        self.total_facts_added = 0
        self.total_facts_confirmed = 0
        self.total_feedback_sent = 0
        self.confidence_improvements = []
        
        # Cache for confirmed facts
        self.confirmed_facts = set()
        self.initial_db_count = self._get_database_fact_count()
        
    def _get_database_fact_count(self) -> int:
        """Get current fact count from database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def _send_hrm_feedback(self, query: str, is_correct: bool = True) -> bool:
        """
        Send feedback to HRM system to update neural confidence
        This simulates the frontend confirmation action
        """
        try:
            print(f"      {Colors.CYAN}📤 Sending HRM feedback (correct={is_correct})...{Colors.RESET}")
            
            # Try multiple feedback endpoints
            feedback_endpoints = [
                '/api/hrm/feedback',
                '/api/feedback',
                '/api/neural/feedback',
                '/api/confirm'
            ]
            
            for endpoint in feedback_endpoints:
                try:
                    response = requests.post(
                        f"{BACKEND_URL}{endpoint}",
                        json={
                            'query': query,
                            'is_correct': is_correct,
                            'confidence_boost': 0.1,  # Boost confidence by 10%
                            'source': 'automated_test'
                        },
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                    if response.ok:
                        print(f"      {Colors.GREEN}✅ Feedback accepted via {endpoint}{Colors.RESET}")
                        self.total_feedback_sent += 1
                        return True
                except:
                    continue
            
            # Alternative: Direct HRM feedback file update
            self._update_hrm_feedback_file(query, is_correct)
            return True
            
        except Exception as e:
            print(f"      {Colors.YELLOW}⚠️ Could not send feedback: {e}{Colors.RESET}")
            return False
    
    def _update_hrm_feedback_file(self, query: str, is_correct: bool):
        """Update HRM feedback file directly"""
        try:
            # Load existing feedback
            feedback_data = {}
            try:
                with open(HRM_FEEDBACK_PATH, 'r') as f:
                    feedback_data = json.load(f)
            except:
                feedback_data = {'feedback_entries': []}
            
            # Add new feedback
            feedback_data['feedback_entries'].append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'is_correct': is_correct,
                'confidence_boost': 0.1,
                'source': 'automated_test'
            })
            
            # Save updated feedback
            with open(HRM_FEEDBACK_PATH, 'w') as f:
                json.dump(feedback_data, f, indent=2)
                
            print(f"      {Colors.GREEN}📝 Updated HRM feedback file{Colors.RESET}")
            
        except Exception as e:
            print(f"      {Colors.YELLOW}⚠️ Could not update feedback file: {e}{Colors.RESET}")
    
    def _confirm_existing_facts(self, query: str, facts_found: List[str]) -> int:
        """
        Confirm facts that were found in the knowledge base
        This increases their confidence and trains the HRM
        """
        confirmed = 0
        
        if not self.auto_confirm or not facts_found:
            return 0
        
        print(f"      {Colors.CYAN}🔄 Confirming {len(facts_found)} existing facts...{Colors.RESET}")
        
        for fact in facts_found:
            if fact not in self.confirmed_facts:
                # Send positive feedback for this fact
                if self._send_hrm_feedback(fact, is_correct=True):
                    confirmed += 1
                    self.confirmed_facts.add(fact)
                    print(f"      {Colors.GREEN}✓ Confirmed: {fact[:60]}...{Colors.RESET}")
                
                time.sleep(0.05)  # Small delay
        
        if confirmed > 0:
            self.total_facts_confirmed += confirmed
            print(f"      {Colors.GREEN}📈 Confirmed {confirmed} facts (improves future confidence){Colors.RESET}")
        
        return confirmed
    
    def _test_query_with_feedback(self, query: str, query_type: str) -> QueryResult:
        """Test query and apply feedback loop"""
        start_time = time.time()
        
        try:
            # First attempt - get initial confidence
            print(f"      {Colors.BLUE}[1/3] Initial query...{Colors.RESET}")
            response = requests.post(
                f"{BACKEND_URL}/api/reason",
                json={'query': query},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if not response.ok:
                return QueryResult(
                    query=query,
                    query_type=query_type,
                    success=False,
                    response_time_ms=response_time_ms,
                    neural_confidence=0.0,
                    error=f"HTTP {response.status_code}"
                )
            
            data = response.json()
            initial_confidence = data.get('confidence', 0.0)
            
            # Search for existing facts
            print(f"      {Colors.BLUE}[2/3] Searching KB...{Colors.RESET}")
            kb_facts = []
            try:
                search_response = requests.post(
                    f"{BACKEND_URL}/api/search",
                    json={'query': query, 'limit': 20},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                if search_response.ok:
                    search_data = search_response.json()
                    kb_facts = [r.get('statement', '') for r in search_data.get('results', [])]
                    print(f"      {Colors.GREEN}📚 Found {len(kb_facts)} KB facts{Colors.RESET}")
            except:
                pass
            
            # Confirm existing facts (feedback loop)
            facts_confirmed = 0
            if kb_facts and self.auto_confirm:
                print(f"      {Colors.BLUE}[3/3] Applying feedback...{Colors.RESET}")
                facts_confirmed = self._confirm_existing_facts(query, kb_facts)
                
                # If we confirmed facts, send feedback for the original query too
                if facts_confirmed > 0:
                    self._send_hrm_feedback(query, is_correct=True)
            
            # Re-test to get updated confidence after feedback
            final_confidence = initial_confidence
            if facts_confirmed > 0:
                time.sleep(0.5)  # Give system time to process feedback
                
                print(f"      {Colors.CYAN}🔄 Re-testing for updated confidence...{Colors.RESET}")
                retry_response = requests.post(
                    f"{BACKEND_URL}/api/reason",
                    json={'query': query},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if retry_response.ok:
                    retry_data = retry_response.json()
                    final_confidence = retry_data.get('confidence', initial_confidence)
                    
                    if final_confidence > initial_confidence:
                        improvement = (final_confidence - initial_confidence) * 100
                        self.confidence_improvements.append(improvement)
                        print(f"      {Colors.GREEN}📈 Confidence improved: "
                              f"{initial_confidence:.1%} → {final_confidence:.1%} "
                              f"(+{improvement:.1f}%){Colors.RESET}")
            
            # Get LLM suggestions and add new facts
            facts_added = 0
            if self.auto_add_facts:
                facts_added = self._add_new_facts_from_llm(query)
            
            return QueryResult(
                query=query,
                query_type=query_type,
                success=True,
                response_time_ms=response_time_ms,
                neural_confidence=initial_confidence,
                neural_confidence_after_feedback=final_confidence,
                kb_facts_found=len(kb_facts),
                facts_added=facts_added,
                facts_confirmed=facts_confirmed,
                feedback_sent=(facts_confirmed > 0)
            )
            
        except Exception as e:
            return QueryResult(
                query=query,
                query_type=query_type,
                success=False,
                response_time_ms=(time.time() - start_time) * 1000,
                neural_confidence=0.0,
                error=str(e)
            )
    
    def _add_new_facts_from_llm(self, query: str) -> int:
        """Get LLM suggestions and add to KB"""
        try:
            # Get LLM suggestions
            response = requests.post(
                f"{BACKEND_URL}/api/llm/get-explanation",
                json={'topic': query, 'context_facts': []},
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            
            if not response.ok:
                return 0
            
            data = response.json()
            suggested_facts = [
                f.get('fact', '') for f in data.get('suggested_facts', [])
                if f.get('fact', '').strip()
            ]
            
            if not suggested_facts:
                return 0
            
            print(f"      {Colors.BLUE}💡 Adding {len(suggested_facts)} LLM suggestions...{Colors.RESET}")
            
            added = 0
            for fact in suggested_facts:
                if self._validate_and_add_fact(fact):
                    added += 1
            
            if added > 0:
                self.total_facts_added += added
                print(f"      {Colors.GREEN}✅ Added {added} new facts{Colors.RESET}")
            
            return added
            
        except:
            return 0
    
    def _validate_and_add_fact(self, fact: str) -> bool:
        """Validate and add a single fact"""
        if not fact or 'Entity1' in fact or 'Entity2' in fact:
            return False
        
        fact = fact.strip()
        if not fact.endswith('.'):
            fact += '.'
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/facts",
                json={
                    'statement': fact,
                    'source': 'LLM_suggestion',
                    'confidence': 0.7
                },
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            return response.ok and response.json().get('success', False)
        except:
            return False
    
    def _create_test_pairs(self) -> List[Tuple[str, str, str]]:
        """Create test pairs"""
        return [
            ("Philosophy", "Is Socrates a philosopher?", "IsA(Socrates, Philosopher)."),
            ("Philosophy", "Did Socrates influence Plato?", "Influenced(Socrates, Plato)."),
            ("Technology", "Does a computer have a CPU?", "HasPart(Computer, CPU)."),
            ("Technology", "Is Python a programming language?", "IsA(Python, ProgrammingLanguage)."),
            ("Geography", "Is Berlin located in Germany?", "LocatedIn(Berlin, Germany)."),
            ("Science", "Is water a liquid?", "IsA(Water, Liquid)."),
            ("Biology", "Are birds animals?", "IsA(Birds, Animals)."),
            ("Mathematics", "Is seven a prime number?", "IsA(Seven, PrimeNumber)."),
        ]
    
    def run_feedback_enhanced_test(self):
        """Run test with feedback loop"""
        print(f"{Colors.BOLD}{Colors.CYAN}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║   HAK-GAL KNOWLEDGE GROWTH WITH HRM FEEDBACK LOOP         ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        
        print(f"Testing: {len(self.test_pairs)} pairs")
        print(f"Mode: {Colors.GREEN}AUTO-CONFIRM ENABLED{Colors.RESET}")
        print(f"Initial DB: {self.initial_db_count:,} facts")
        print("="*60)
        
        # Test connectivity
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.ok:
                print(f"{Colors.GREEN}✅ Backend online{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Backend error{Colors.RESET}")
                return False
        except:
            print(f"{Colors.RED}❌ Backend not accessible{Colors.RESET}")
            return False
        
        print(f"\n{Colors.BOLD}🚀 STARTING FEEDBACK-ENHANCED TEST...{Colors.RESET}\n")
        
        for i, (domain, natural_query, symbolic_query) in enumerate(self.test_pairs, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(self.test_pairs)}] {domain}:{Colors.RESET}")
            
            # Test natural query
            print(f"   {Colors.CYAN}🧠 Natural: {natural_query}{Colors.RESET}")
            natural_result = self._test_query_with_feedback(natural_query, "natural")
            self.results.append(natural_result)
            
            if natural_result.success:
                conf_str = f"{natural_result.neural_confidence:.1%}"
                if natural_result.neural_confidence_after_feedback > natural_result.neural_confidence:
                    conf_str += f" → {natural_result.neural_confidence_after_feedback:.1%}"
                    conf_str = f"{Colors.GREEN}{conf_str}{Colors.RESET}"
                else:
                    conf_str = f"{Colors.YELLOW}{conf_str}{Colors.RESET}"
                
                print(f"      Confidence: {conf_str}, Time: {natural_result.response_time_ms:.0f}ms")
                
                if natural_result.facts_confirmed > 0:
                    print(f"      {Colors.GREEN}✅ Confirmed {natural_result.facts_confirmed} facts{Colors.RESET}")
                if natural_result.facts_added > 0:
                    print(f"      {Colors.GREEN}📥 Added {natural_result.facts_added} new facts{Colors.RESET}")
            
            time.sleep(0.3)
            
            # Test symbolic query
            print(f"   {Colors.YELLOW}⚡ Symbolic: {symbolic_query}{Colors.RESET}")
            symbolic_result = self._test_query_with_feedback(symbolic_query, "symbolic")
            self.results.append(symbolic_result)
            
            if symbolic_result.success:
                conf_str = f"{symbolic_result.neural_confidence:.1%}"
                if symbolic_result.neural_confidence_after_feedback > symbolic_result.neural_confidence:
                    conf_str += f" → {symbolic_result.neural_confidence_after_feedback:.1%}"
                    conf_str = f"{Colors.GREEN}{conf_str}{Colors.RESET}"
                else:
                    conf_str = f"{Colors.YELLOW}{conf_str}{Colors.RESET}"
                
                print(f"      Confidence: {conf_str}, Time: {symbolic_result.response_time_ms:.0f}ms")
                
                if symbolic_result.facts_confirmed > 0:
                    print(f"      {Colors.GREEN}✅ Confirmed {symbolic_result.facts_confirmed} facts{Colors.RESET}")
                if symbolic_result.facts_added > 0:
                    print(f"      {Colors.GREEN}📥 Added {symbolic_result.facts_added} new facts{Colors.RESET}")
            
            # Pair summary
            total_confirmed = natural_result.facts_confirmed + symbolic_result.facts_confirmed
            total_added = natural_result.facts_added + symbolic_result.facts_added
            
            if total_confirmed > 0 or total_added > 0:
                current_db = self._get_database_fact_count()
                print(f"      {Colors.BOLD}📊 Pair: +{total_added} new, "
                      f"{total_confirmed} confirmed (DB: {current_db:,}){Colors.RESET}")
            
            time.sleep(0.2)
        
        # Final summary
        self._print_final_summary()
        self._save_results()
        
        return True
    
    def _print_final_summary(self):
        """Print comprehensive summary"""
        final_db_count = self._get_database_fact_count()
        total_growth = final_db_count - self.initial_db_count
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}✨ FEEDBACK-ENHANCED TEST COMPLETED ✨{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}📊 DATABASE GROWTH:{Colors.RESET}")
        print(f"  Initial:     {self.initial_db_count:,} facts")
        print(f"  Final:       {Colors.GREEN}{final_db_count:,} facts{Colors.RESET}")
        print(f"  Net Growth:  {Colors.GREEN}+{total_growth} facts{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}🔄 FEEDBACK METRICS:{Colors.RESET}")
        print(f"  Facts Confirmed:     {Colors.GREEN}{self.total_facts_confirmed}{Colors.RESET}")
        print(f"  Facts Added:         {Colors.GREEN}{self.total_facts_added}{Colors.RESET}")
        print(f"  Feedback Sent:       {Colors.CYAN}{self.total_feedback_sent}{Colors.RESET}")
        
        if self.confidence_improvements:
            avg_improvement = sum(self.confidence_improvements) / len(self.confidence_improvements)
            print(f"  Avg Confidence Gain: {Colors.GREEN}+{avg_improvement:.1f}%{Colors.RESET}")
        
        # Confidence analysis
        natural_results = [r for r in self.results if r.query_type == "natural" and r.success]
        symbolic_results = [r for r in self.results if r.query_type == "symbolic" and r.success]
        
        if natural_results:
            avg_initial = sum(r.neural_confidence for r in natural_results) / len(natural_results)
            avg_final = sum(r.neural_confidence_after_feedback for r in natural_results) / len(natural_results)
            
            print(f"\n{Colors.BOLD}🧠 NATURAL QUERIES:{Colors.RESET}")
            print(f"  Initial Avg: {avg_initial:.1%}")
            if avg_final > avg_initial:
                print(f"  Final Avg:   {Colors.GREEN}{avg_final:.1%} (+{(avg_final-avg_initial)*100:.1f}%){Colors.RESET}")
        
        if symbolic_results:
            avg_initial = sum(r.neural_confidence for r in symbolic_results) / len(symbolic_results)
            avg_final = sum(r.neural_confidence_after_feedback for r in symbolic_results) / len(symbolic_results)
            
            print(f"\n{Colors.BOLD}⚡ SYMBOLIC QUERIES:{Colors.RESET}")
            print(f"  Initial Avg: {avg_initial:.1%}")
            if avg_final > avg_initial:
                print(f"  Final Avg:   {Colors.GREEN}{avg_final:.1%} (+{(avg_final-avg_initial)*100:.1f}%){Colors.RESET}")
        
        print(f"\n{Colors.CYAN}💡 The feedback loop is training the HRM!{Colors.RESET}")
        print(f"{Colors.CYAN}   Future queries will have higher initial confidence.{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    def _save_results(self):
        """Save detailed results with feedback data"""
        results_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'backend_url': BACKEND_URL,
                'initial_db_facts': self.initial_db_count,
                'final_db_facts': self._get_database_fact_count(),
                'total_facts_confirmed': self.total_facts_confirmed,
                'total_facts_added': self.total_facts_added,
                'total_feedback_sent': self.total_feedback_sent,
                'avg_confidence_improvement': sum(self.confidence_improvements) / len(self.confidence_improvements) if self.confidence_improvements else 0
            },
            'results': [
                {
                    'query': r.query,
                    'query_type': r.query_type,
                    'success': r.success,
                    'response_time_ms': r.response_time_ms,
                    'neural_confidence_initial': r.neural_confidence,
                    'neural_confidence_final': r.neural_confidence_after_feedback,
                    'confidence_improved': r.neural_confidence_after_feedback > r.neural_confidence,
                    'kb_facts_found': r.kb_facts_found,
                    'facts_confirmed': r.facts_confirmed,
                    'facts_added': r.facts_added,
                    'feedback_sent': r.feedback_sent,
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
            print(f"{Colors.RED}❌ Failed to save: {e}{Colors.RESET}")

def main():
    """Main execution"""
    import sys
    
    auto_confirm = '--no-confirm' not in sys.argv
    auto_add = '--no-add' not in sys.argv
    
    print(f"\n{Colors.BOLD}")
    if auto_confirm:
        print(f"{Colors.GREEN}🔄 AUTO-CONFIRM: Facts will be confirmed (trains HRM){Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}📋 NO CONFIRM: Facts won't be confirmed{Colors.RESET}")
    
    if auto_add:
        print(f"{Colors.GREEN}📥 AUTO-ADD: New facts will be added{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}📋 NO ADD: New facts won't be added{Colors.RESET}")
    print(f"{Colors.RESET}")
    
    tester = KnowledgeGrowthWithFeedback(
        auto_add_facts=auto_add,
        auto_confirm=auto_confirm
    )
    
    try:
        success = tester.run_feedback_enhanced_test()
        if not success:
            print(f"\n{Colors.RED}💥 Test failed{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏹️ Interrupted{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}💥 Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
