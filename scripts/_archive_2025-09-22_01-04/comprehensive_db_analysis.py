#!/usr/bin/env python3
"""
HAK-GAL Comprehensive Database Analysis & Cleanup
==================================================
Wissenschaftliche Analyse und Bereinigung der Knowledge Base
"""

import sqlite3
import re
from collections import defaultdict
from datetime import datetime
import json

class ComprehensiveAnalyzer:
    def __init__(self, db_path="hexagonal_kb.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.report = []
        
    def analyze_all(self):
        """Führt komplette Analyse durch"""
        print("="*70)
        print("HAK-GAL COMPREHENSIVE DATABASE ANALYSIS")
        print("="*70)
        
        # 1. Basis-Statistik
        self.basic_stats()
        
        # 2. Prädikat-Analyse
        self.predicate_analysis()
        
        # 3. Chemische Fehler
        self.chemical_errors()
        
        # 4. Duplikate
        self.duplicate_analysis()
        
        # 5. Qualitäts-Score
        self.quality_assessment()
        
        return self.report
    
    def basic_stats(self):
        """Grundlegende Statistiken"""
        self.cursor.execute("SELECT COUNT(*) FROM facts")
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(DISTINCT statement) FROM facts")
        unique = self.cursor.fetchone()[0]
        
        self.cursor.execute("""
            SELECT AVG(LENGTH(statement)) as avg_len,
                   MIN(LENGTH(statement)) as min_len,
                   MAX(LENGTH(statement)) as max_len
            FROM facts
        """)
        lengths = self.cursor.fetchone()
        
        stats = {
            'total_facts': total,
            'unique_facts': unique,
            'duplicates': total - unique,
            'avg_length': round(lengths[0], 2),
            'min_length': lengths[1],
            'max_length': lengths[2]
        }
        
        print("\n1. GRUNDSTATISTIK:")
        print("-"*40)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        self.report.append(('basic_stats', stats))
        return stats
    
    def predicate_analysis(self):
        """Analysiert alle Prädikate"""
        self.cursor.execute("""
            SELECT 
                CASE 
                    WHEN instr(statement, '(') > 0 
                    THEN substr(statement, 1, instr(statement, '(') - 1)
                    ELSE 'NO_PREDICATE'
                END as predicate,
                COUNT(*) as count
            FROM facts
            GROUP BY predicate
            ORDER BY count DESC
        """)
        
        predicates = self.cursor.fetchall()
        
        print("\n2. PRÄDIKAT-VERTEILUNG:")
        print("-"*40)
        
        total = sum(count for _, count in predicates)
        
        # Top 10 anzeigen
        for pred, count in predicates[:10]:
            percentage = (count/total)*100
            print(f"  {pred}: {count} ({percentage:.1f}%)")
        
        # Kategorisierung
        categories = {
            'structural': ['HasPart', 'ConsistsOf', 'Contains'],
            'relational': ['IsTypeOf', 'IsA', 'IsSimilarTo', 'DependsOn'],
            'functional': ['HasPurpose', 'Causes', 'Uses', 'Requires'],
            'properties': ['HasProperty', 'IsDefinedAs'],
            'chemical': ['Bond', 'Element', 'Molecule'],
            'biological': ['Gene', 'Protein', 'Cell', 'DNA'],
            'technical': ['API', 'Algorithm', 'Network', 'Matrix']
        }
        
        category_counts = defaultdict(int)
        for pred, count in predicates:
            found = False
            for cat, keywords in categories.items():
                if pred in keywords:
                    category_counts[cat] += count
                    found = True
                    break
            if not found:
                category_counts['other'] += count
        
        print("\nKategorien:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count/total)*100
            print(f"  {cat}: {count} ({percentage:.1f}%)")
        
        self.report.append(('predicates', dict(predicates[:20])))
        return predicates
    
    def chemical_errors(self):
        """Detaillierte chemische Fehleranalyse"""
        
        chemicals = {
            'H2O': {'elements': ['hydrogen', 'oxygen'], 'formula': 'H₂O'},
            'NH3': {'elements': ['nitrogen', 'hydrogen'], 'formula': 'NH₃'},
            'CH4': {'elements': ['carbon', 'hydrogen'], 'formula': 'CH₄'},
            'CO2': {'elements': ['carbon', 'oxygen'], 'formula': 'CO₂'},
            'NaCl': {'elements': ['sodium', 'chlorine'], 'formula': 'NaCl'},
            'O2': {'elements': ['oxygen'], 'formula': 'O₂'},
            'N2': {'elements': ['nitrogen'], 'formula': 'N₂'},
            'H2': {'elements': ['hydrogen'], 'formula': 'H₂'}
        }
        
        print("\n3. CHEMISCHE FEHLERANALYSE:")
        print("-"*40)
        
        errors_found = []
        
        for compound, data in chemicals.items():
            valid_elements = data['elements']
            
            # Finde alle Statements mit diesem Compound
            self.cursor.execute(f"SELECT statement FROM facts WHERE statement LIKE '%{compound}%'")
            statements = self.cursor.fetchall()
            
            for stmt in statements:
                statement = stmt[0].lower()
                
                # Prüfe auf falsche Elemente
                wrong_elements = []
                if compound == 'H2O' and 'carbon' in statement:
                    wrong_elements.append('carbon')
                if compound == 'NH3' and 'oxygen' in statement:
                    wrong_elements.append('oxygen')
                if compound == 'CH4' and 'oxygen' in statement:
                    wrong_elements.append('oxygen')
                if compound == 'CO2' and 'hydrogen' in statement and 'ConsistsOf' in stmt[0]:
                    wrong_elements.append('hydrogen')
                if compound == 'NaCl' and 'carbon' in statement:
                    wrong_elements.append('carbon')
                
                if wrong_elements:
                    errors_found.append({
                        'statement': stmt[0],
                        'compound': compound,
                        'wrong_elements': wrong_elements,
                        'correct_formula': data['formula']
                    })
        
        print(f"Gefundene chemische Fehler: {len(errors_found)}")
        
        # Gruppiere nach Fehlertyp
        error_types = defaultdict(int)
        for error in errors_found:
            key = f"{error['compound']} enthält nicht: {', '.join(error['wrong_elements'])}"
            error_types[key] += 1
        
        print("\nFehlertypen:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {error_type}: {count} Mal")
        
        self.report.append(('chemical_errors', {
            'total': len(errors_found),
            'types': dict(error_types)
        }))
        
        return errors_found
    
    def duplicate_analysis(self):
        """Findet Duplikate und ähnliche Statements"""
        
        print("\n4. DUPLIKAT-ANALYSE:")
        print("-"*40)
        
        # Exakte Duplikate
        self.cursor.execute("""
            SELECT statement, COUNT(*) as cnt
            FROM facts
            GROUP BY statement
            HAVING cnt > 1
            ORDER BY cnt DESC
            LIMIT 10
        """)
        
        exact_duplicates = self.cursor.fetchall()
        
        if exact_duplicates:
            print("Exakte Duplikate:")
            for stmt, count in exact_duplicates:
                print(f"  {count}x: {stmt[:60]}...")
        else:
            print("Keine exakten Duplikate gefunden")
        
        # Ähnliche Statements (gleiche Entitäten, andere Reihenfolge)
        self.cursor.execute("SELECT statement FROM facts WHERE statement LIKE 'ConsistsOf%' LIMIT 1000")
        consists_statements = self.cursor.fetchall()
        
        similar_groups = defaultdict(list)
        for stmt in consists_statements:
            statement = stmt[0]
            # Extrahiere Entitäten
            match = re.match(r'ConsistsOf\((.*?)\)\.', statement)
            if match:
                entities = sorted([e.strip() for e in match.group(1).split(',')])
                key = tuple(entities)
                similar_groups[key].append(statement)
        
        print(f"\nÄhnliche ConsistsOf-Gruppen: {len(similar_groups)}")
        
        # Zeige Gruppen mit mehreren Varianten
        multi_variants = [g for g in similar_groups.values() if len(g) > 1]
        if multi_variants:
            print(f"Gruppen mit mehreren Varianten: {len(multi_variants)}")
            for group in multi_variants[:3]:
                print(f"  Gruppe mit {len(group)} Varianten:")
                for stmt in group[:2]:
                    print(f"    - {stmt}")
        
        self.report.append(('duplicates', {
            'exact': len(exact_duplicates),
            'similar_groups': len(similar_groups)
        }))
        
    def quality_assessment(self):
        """Berechnet Qualitäts-Score"""
        
        print("\n5. QUALITÄTSBEWERTUNG:")
        print("-"*40)
        
        self.cursor.execute("SELECT COUNT(*) FROM facts")
        total = self.cursor.fetchone()[0]
        
        # Faktoren für Qualität
        factors = {}
        
        # 1. Chemische Korrektheit
        self.cursor.execute("""
            SELECT COUNT(*) FROM facts 
            WHERE (statement LIKE '%NH3%oxygen%')
               OR (statement LIKE '%H2O%carbon%')
               OR (statement LIKE '%CH4%oxygen%')
        """)
        chem_errors = self.cursor.fetchone()[0]
        factors['chemical_accuracy'] = max(0, 100 - (chem_errors/total)*200)
        
        # 2. Prädikat-Diversität (Shannon-Entropie)
        self.cursor.execute("""
            SELECT COUNT(*) as cnt
            FROM facts
            GROUP BY substr(statement, 1, instr(statement, '(') - 1)
        """)
        unique_predicates = len(self.cursor.fetchall())
        factors['predicate_diversity'] = min(100, unique_predicates * 2)
        
        # 3. Statement-Länge (optimal: 20-60 Zeichen)
        self.cursor.execute("""
            SELECT COUNT(*) FROM facts
            WHERE LENGTH(statement) BETWEEN 20 AND 60
        """)
        optimal_length = self.cursor.fetchone()[0]
        factors['optimal_length'] = (optimal_length/total) * 100
        
        # 4. Keine Duplikate
        self.cursor.execute("""
            SELECT COUNT(DISTINCT statement) FROM facts
        """)
        unique = self.cursor.fetchone()[0]
        factors['uniqueness'] = (unique/total) * 100
        
        # 5. Semantische Struktur (hat Prädikat mit Klammern)
        self.cursor.execute("""
            SELECT COUNT(*) FROM facts
            WHERE statement LIKE '%(%)'
        """)
        well_formed = self.cursor.fetchone()[0]
        factors['well_formed'] = (well_formed/total) * 100
        
        # Gewichteter Durchschnitt
        weights = {
            'chemical_accuracy': 0.3,
            'predicate_diversity': 0.2,
            'optimal_length': 0.1,
            'uniqueness': 0.2,
            'well_formed': 0.2
        }
        
        overall_score = sum(factors[k] * weights[k] for k in factors)
        
        print("Qualitätsfaktoren:")
        for factor, score in factors.items():
            print(f"  {factor}: {score:.1f}/100")
        
        print(f"\n📊 GESAMT-QUALITÄTSSCORE: {overall_score:.1f}/100")
        
        # Bewertung
        if overall_score >= 80:
            rating = "EXZELLENT"
        elif overall_score >= 60:
            rating = "GUT"
        elif overall_score >= 40:
            rating = "MITTELMÄSSIG"
        else:
            rating = "SCHLECHT"
        
        print(f"Bewertung: {rating}")
        
        self.report.append(('quality_score', {
            'factors': factors,
            'overall': overall_score,
            'rating': rating
        }))
        
        return overall_score

def main():
    analyzer = ComprehensiveAnalyzer()
    report = analyzer.analyze_all()
    
    # Speichere Report als JSON
    with open("comprehensive_analysis.json", "w") as f:
        json.dump(dict(report), f, indent=2)
    
    print("\n" + "="*70)
    print("Analyse abgeschlossen!")
    print("Report gespeichert in: comprehensive_analysis.json")
    
if __name__ == "__main__":
    main()
