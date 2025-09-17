#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Domain Coverage Test Framework
===============================
Wissenschaftlicher Test-Framework für die Validierung der 36 neuen Domains
Erstellt von Claude Opus 4.1 als Lead Architect
"""

import sys
import os
sys.path.append(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")

from src_hexagonal.application.extended_fact_manager import ExtendedFactManager
import json
from datetime import datetime
from typing import Dict, List, Tuple

class DomainCoverageValidator:
    """
    Wissenschaftliche Validierung der Domain-Implementation
    """
    
    def __init__(self):
        self.manager = ExtendedFactManager()
        self.results = {}
        
        # Alle 44 Domains die getestet werden müssen
        self.all_domains = [
            # Original 8
            'chemistry', 'physics', 'biology', 'economics', 
            'geography', 'medicine', 'technology', 'mathematics',
            
            # Neue 36 Domains
            'astronomy', 'geology', 'psychology', 'sociology',
            'history', 'linguistics', 'philosophy', 'art',
            'music', 'literature', 'architecture', 'engineering',
            'computer_science', 'robotics', 'ai', 'cryptography',
            'environmental_science', 'climate', 'ecology', 'genetics',
            'neuroscience', 'immunology', 'pharmacology', 'surgery',
            'finance', 'marketing', 'management', 'entrepreneurship',
            'politics', 'law', 'ethics', 'anthropology',
            'archaeology', 'paleontology', 'meteorology', 'oceanography'
        ]
        
        # Batches für strukturierte Implementation
        self.batches = {
            1: ['astronomy', 'geology', 'psychology', 'neuroscience', 'sociology', 'linguistics'],
            2: ['philosophy', 'art', 'music', 'literature', 'history', 'architecture'],
            3: ['engineering', 'robotics', 'computer_science', 'ai', 'cryptography', 'environmental_science'],
            4: ['genetics', 'immunology', 'pharmacology', 'surgery', 'ecology', 'climate'],
            5: ['finance', 'marketing', 'management', 'entrepreneurship', 'politics', 'law'],
            6: ['ethics', 'anthropology', 'archaeology', 'paleontology', 'meteorology', 'oceanography']
        }
    
    def test_domain(self, domain: str) -> Dict:
        """
        Teste einzelne Domain
        """
        result = {
            'domain': domain,
            'status': 'FAIL',
            'facts_generated': 0,
            'unique_predicates': [],
            'multi_arg_ratio': 0.0,
            'errors': []
        }
        
        try:
            # Generiere Facts für Domain
            facts = self.manager.generate_domain_facts(domain, 10)
            
            if not facts:
                result['errors'].append('No facts generated')
                return result
            
            result['facts_generated'] = len(facts)
            
            # Analysiere Predicates
            predicates = set()
            multi_arg_count = 0
            
            for fact in facts:
                predicates.add(fact.get('predicate', 'Unknown'))
                if 'args' in fact and len(fact['args']) > 2:
                    multi_arg_count += 1
            
            result['unique_predicates'] = list(predicates)
            result['multi_arg_ratio'] = (multi_arg_count / len(facts)) * 100 if facts else 0
            
            # Validierung
            if result['facts_generated'] >= 5:
                if result['multi_arg_ratio'] >= 80:
                    result['status'] = 'PASS'
                else:
                    result['status'] = 'PARTIAL'
                    result['errors'].append(f'Low multi-arg ratio: {result["multi_arg_ratio"]:.1f}%')
            else:
                result['errors'].append(f'Only {result["facts_generated"]} facts generated (min: 5)')
        
        except Exception as e:
            result['errors'].append(f'Exception: {str(e)}')
        
        return result
    
    def test_batch(self, batch_num: int) -> Dict:
        """
        Teste einen kompletten Batch
        """
        if batch_num not in self.batches:
            return {'error': f'Invalid batch number: {batch_num}'}
        
        batch_domains = self.batches[batch_num]
        batch_results = {
            'batch': batch_num,
            'domains': batch_domains,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(batch_domains),
                'passed': 0,
                'partial': 0,
                'failed': 0
            },
            'details': {}
        }
        
        print(f"\n{'='*60}")
        print(f"TESTING BATCH {batch_num}: {', '.join(batch_domains)}")
        print(f"{'='*60}")
        
        for domain in batch_domains:
            print(f"\nTesting {domain}...", end=' ')
            result = self.test_domain(domain)
            batch_results['details'][domain] = result
            
            if result['status'] == 'PASS':
                batch_results['summary']['passed'] += 1
                print("✅ PASS")
            elif result['status'] == 'PARTIAL':
                batch_results['summary']['partial'] += 1
                print("⚠️ PARTIAL")
            else:
                batch_results['summary']['failed'] += 1
                print("❌ FAIL")
                if result['errors']:
                    for error in result['errors']:
                        print(f"  - {error}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"BATCH {batch_num} SUMMARY:")
        print(f"  Passed:  {batch_results['summary']['passed']}/{batch_results['summary']['total']}")
        print(f"  Partial: {batch_results['summary']['partial']}/{batch_results['summary']['total']}")
        print(f"  Failed:  {batch_results['summary']['failed']}/{batch_results['summary']['total']}")
        print(f"{'='*60}\n")
        
        self.results[f'batch_{batch_num}'] = batch_results
        return batch_results
    
    def test_all_domains(self) -> Dict:
        """
        Teste ALLE Domains
        """
        all_results = {
            'timestamp': datetime.now().isoformat(),
            'total_domains': len(self.all_domains),
            'summary': {
                'passed': 0,
                'partial': 0,
                'failed': 0
            },
            'by_domain': {}
        }
        
        print(f"\n{'='*60}")
        print(f"TESTING ALL {len(self.all_domains)} DOMAINS")
        print(f"{'='*60}")
        
        for domain in self.all_domains:
            result = self.test_domain(domain)
            all_results['by_domain'][domain] = result
            
            if result['status'] == 'PASS':
                all_results['summary']['passed'] += 1
            elif result['status'] == 'PARTIAL':
                all_results['summary']['partial'] += 1
            else:
                all_results['summary']['failed'] += 1
        
        # Generate report
        self.generate_report(all_results)
        return all_results
    
    def generate_report(self, results: Dict):
        """
        Generiere wissenschaftlichen Report
        """
        report_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\agent_hub\claude-opus\validation\domain_coverage_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nReport saved to: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("FINAL VALIDATION REPORT")
        print("="*60)
        print(f"Total Domains: {results['total_domains']}")
        print(f"✅ Passed:  {results['summary']['passed']}")
        print(f"⚠️ Partial: {results['summary']['partial']}")
        print(f"❌ Failed:  {results['summary']['failed']}")
        
        # List failed domains
        failed = [d for d, r in results['by_domain'].items() if r['status'] == 'FAIL']
        if failed:
            print(f"\nFailed Domains: {', '.join(failed)}")
        
        print("="*60)


def main():
    """Main entry point"""
    validator = DomainCoverageValidator()
    
    # Test first batch (before implementation)
    print("\n🔬 BASELINE TEST - Batch 1 (Before Implementation)")
    baseline = validator.test_batch(1)
    
    # Save baseline
    with open(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\agent_hub\claude-opus\validation\baseline_batch1.json", 'w') as f:
        json.dump(baseline, f, indent=2)
    
    print("\nBaseline established. Ready for Sonnet implementation.")
    print("After implementation, run: python domain_test_framework.py --batch 1")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Domain Coverage Test Framework")
    parser.add_argument("--batch", type=int, help="Test specific batch (1-6)")
    parser.add_argument("--all", action="store_true", help="Test all domains")
    args = parser.parse_args()
    
    validator = DomainCoverageValidator()
    
    if args.all:
        validator.test_all_domains()
    elif args.batch:
        validator.test_batch(args.batch)
    else:
        main()
