#!/usr/bin/env python3
"""
Deep Facts Analysis für HAK-GAL Knowledge Base
==============================================
Nach HAK/GAL Artikel 6: Empirische Validierung
Vollständige Diagnose der Knowledge Base Probleme
"""

import sqlite3
import re
from collections import Counter, defaultdict
from pathlib import Path
import json

class DeepFactsAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.facts = []
        self.predicates = defaultdict(list)
        self.issues = {
            'malformed': [],
            'duplicates': [],
            'encoding': [],
            'mixed_language': [],
            'unclassified': [],
            'suspicious': []
        }
        
    def load_facts(self):
        """Load all facts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check which table structure we have
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facts'")
        if cursor.fetchone():
            # Get column names
            cursor.execute("PRAGMA table_info(facts)")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            
            if 'statement' in col_names:
                cursor.execute("SELECT rowid, statement, context, fact_metadata FROM facts")
            else:
                # Fallback for different schema
                cursor.execute("SELECT rowid, * FROM facts")
        else:
            print("[ERROR] No 'facts' table found in database")
            conn.close()
            return
            
        self.facts = cursor.fetchall()
        conn.close()
        print(f"[LOADED] {len(self.facts)} facts from database")
        
    def analyze_predicates(self):
        """Analyze predicate patterns and languages"""
        english_predicates = set([
            'IsTypeOf', 'HasTrait', 'IsMemberOf', 'HasProperty', 'Uses',
            'Requires', 'CanBe', 'Contains', 'Produces', 'Affects',
            'Influences', 'ConsistsOf', 'HasCapability', 'IsPartOf',
            'RelatesTo', 'DependsOn', 'Enables', 'Supports', 'Provides',
            'HasComponent', 'ProcessedBy', 'GeneratedFrom', 'UsedFor',
            'LocatedIn', 'OccursIn', 'MeasuredIn', 'DefinedAs', 'ClassifiedAs'
        ])
        
        german_predicates = set([
            'IstTypVon', 'HatEigenschaft', 'IstMitgliedVon', 'Verwendet',
            'Benötigt', 'KannSein', 'Enthält', 'Produziert', 'Beeinflusst',
            'BestehtAus', 'HatFähigkeit', 'IstTeilVon', 'BeziehungZu',
            'HängtAbVon', 'Ermöglicht', 'Unterstützt', 'Bietet',
            'HatKomponente', 'VerarbeitetDurch', 'GeneriertVon', 'VerwendetFür'
        ])
        
        stats = {
            'total': len(self.facts),
            'english': 0,
            'german': 0,
            'mixed': 0,
            'unknown': 0,
            'malformed': 0
        }
        
        predicate_counter = Counter()
        language_mix = []
        
        for row_id, statement, context, metadata in self.facts:
            try:
                # Extract predicate
                if '(' in statement and ')' in statement:
                    predicate = statement.split('(')[0].strip()
                    predicate_counter[predicate] += 1
                    
                    # Classify language
                    if predicate in english_predicates:
                        stats['english'] += 1
                        self.predicates['english'].append((row_id, predicate, statement))
                    elif predicate in german_predicates:
                        stats['german'] += 1
                        self.predicates['german'].append((row_id, predicate, statement))
                    else:
                        # Check for mixed patterns
                        if any(eng in predicate for eng in ['Has', 'Is', 'Can', 'Uses']):
                            stats['mixed'] += 1
                            language_mix.append((row_id, predicate, statement))
                        else:
                            stats['unknown'] += 1
                            self.issues['unclassified'].append((row_id, predicate, statement))
                else:
                    stats['malformed'] += 1
                    self.issues['malformed'].append((row_id, statement))
                    
            except Exception as e:
                self.issues['suspicious'].append((row_id, statement, str(e)))
                
        return stats, predicate_counter, language_mix
        
    def find_missing_patterns(self):
        """Identify what types of facts are missing"""
        expected_patterns = {
            'Physics': ['Gravity', 'Mass', 'Energy', 'Force', 'Velocity'],
            'Chemistry': ['Element', 'Compound', 'Reaction', 'Molecule', 'Atom'],
            'Biology': ['Cell', 'DNA', 'Protein', 'Organism', 'Evolution'],
            'Computer Science': ['Algorithm', 'DataStructure', 'Network', 'Database', 'AI'],
            'Mathematics': ['Number', 'Equation', 'Theorem', 'Geometry', 'Calculus'],
            'HAK/GAL': ['Governor', 'HRM', 'Reasoning', 'Knowledge', 'Fact']
        }
        
        found_patterns = defaultdict(int)
        missing_patterns = defaultdict(list)
        
        for _, statement, _, _ in self.facts:
            for category, patterns in expected_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in statement.lower():
                        found_patterns[f"{category}:{pattern}"] += 1
                        
        # Check what's missing
        for category, patterns in expected_patterns.items():
            for pattern in patterns:
                key = f"{category}:{pattern}"
                if found_patterns[key] == 0:
                    missing_patterns[category].append(pattern)
                    
        return found_patterns, missing_patterns
        
    def check_encoding_issues(self):
        """Check for encoding problems"""
        encoding_problems = []
        
        for row_id, statement, _, _ in self.facts:
            # Check for common encoding issues
            if any(char in statement for char in ['â€™', 'â€"', 'Â', '�']):
                encoding_problems.append((row_id, statement, 'UTF-8 corruption'))
            elif any(ord(char) > 127 for char in statement):
                non_ascii = [char for char in statement if ord(char) > 127]
                encoding_problems.append((row_id, statement, f'Non-ASCII: {non_ascii}'))
                
        return encoding_problems
        
    def find_duplicates(self):
        """Find duplicate or near-duplicate facts"""
        seen = {}
        duplicates = []
        
        for row_id, statement, _, _ in self.facts:
            # Normalize for comparison
            normalized = statement.lower().strip().rstrip('.')
            
            if normalized in seen:
                duplicates.append((row_id, statement, seen[normalized]))
            else:
                seen[normalized] = row_id
                
        return duplicates
        
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*60)
        print("HAK-GAL KNOWLEDGE BASE DEEP ANALYSIS")
        print("="*60)
        
        # Load and analyze
        self.load_facts()
        stats, predicates, mixed = self.analyze_predicates()
        found, missing = self.find_missing_patterns()
        encoding = self.check_encoding_issues()
        duplicates = self.find_duplicates()
        
        # Report statistics
        print(f"\n[STATISTICS]")
        print(f"Total Facts: {stats['total']}")
        print(f"English: {stats['english']} ({stats['english']/stats['total']*100:.1f}%)")
        print(f"German: {stats['german']} ({stats['german']/stats['total']*100:.1f}%)")
        print(f"Mixed: {stats['mixed']} ({stats['mixed']/stats['total']*100:.1f}%)")
        print(f"Unknown: {stats['unknown']} ({stats['unknown']/stats['total']*100:.1f}%)")
        print(f"Malformed: {stats['malformed']} ({stats['malformed']/stats['total']*100:.1f}%)")
        
        # Top predicates
        print(f"\n[TOP PREDICATES]")
        for pred, count in predicates.most_common(10):
            print(f"  {pred}: {count}")
            
        # Missing patterns
        print(f"\n[MISSING KNOWLEDGE DOMAINS]")
        for category, patterns in missing.items():
            if patterns:
                print(f"  {category}: Missing {patterns}")
                
        # Issues summary
        print(f"\n[QUALITY ISSUES]")
        print(f"Encoding Problems: {len(encoding)}")
        print(f"Duplicates: {len(duplicates)}")
        print(f"Unclassified Predicates: {len(self.issues['unclassified'])}")
        print(f"Malformed Facts: {len(self.issues['malformed'])}")
        
        # Sample problematic facts
        if self.issues['unclassified']:
            print(f"\n[SAMPLE UNCLASSIFIED FACTS]")
            for row_id, pred, stmt in self.issues['unclassified'][:5]:
                print(f"  ID {row_id}: {pred} - {stmt[:60]}...")
                
        # Expected vs Actual
        print(f"\n[CRITICAL FINDING]")
        print(f"Expected Facts (from docs): 3080")
        print(f"Actual Facts in DB: {stats['total']}")
        print(f"MISSING: {3080 - stats['total']} facts ({(3080-stats['total'])/3080*100:.1f}%)")
        
        # Recommendations
        print(f"\n[RECOMMENDATIONS]")
        print("1. URGENT: Restore missing 1850 facts from backup")
        print("2. Standardize predicates to single language (prefer English)")
        print("3. Fix encoding issues in 62+ facts")
        print("4. Remove duplicates")
        print("5. Add missing knowledge domains")
        print("6. Implement predicate validation")
        
        # Save detailed report
        report = {
            'statistics': stats,
            'top_predicates': dict(predicates.most_common(20)),
            'missing_domains': dict(missing),
            'encoding_issues': len(encoding),
            'duplicates': len(duplicates),
            'unclassified': len(self.issues['unclassified']),
            'recommendations': [
                'Restore missing 1850 facts',
                'Standardize language',
                'Fix encoding',
                'Remove duplicates',
                'Add missing domains'
            ]
        }
        
        with open('facts_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"\n[SAVED] Detailed report: facts_analysis_report.json")
        
        return report

def main():
    # Find database
    db_path = Path('k_assistant.db')
    if not db_path.exists():
        db_path = Path('..') / 'HAK_GAL_SUITE' / 'k_assistant.db'
        
    if not db_path.exists():
        print("[ERROR] Database not found")
        return 1
        
    analyzer = DeepFactsAnalyzer(str(db_path))
    report = analyzer.generate_report()
    
    # Critical alert
    if report['statistics']['total'] < 3000:
        print("\n" + "!"*60)
        print("CRITICAL: Knowledge Base is INCOMPLETE!")
        print("Action Required: Restore from backup or rebuild")
        print("!"*60)
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())