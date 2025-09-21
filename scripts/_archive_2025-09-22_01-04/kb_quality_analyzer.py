"""
HAK-GAL Knowledge Base Quality Analyzer
========================================
Analysiert die Qualität der generierten Fakten in der Datenbank
und identifiziert Probleme wie Duplikate, falsche Fakten, etc.
"""

import sqlite3
import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Any
import json
from datetime import datetime
import difflib

class FactQualityAnalyzer:
    """Umfassende Qualitätsanalyse für HAK-GAL Fakten"""
    
    def __init__(self, db_path: str = "hexagonal_kb.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Bekannte korrekte Fakten für Validierung
        self.known_facts = {
            'chemistry': {
                'H2O': ['hydrogen', 'oxygen'],
                'NH3': ['nitrogen', 'hydrogen'],  # NICHT oxygen!
                'CO2': ['carbon', 'oxygen'],
                'CH4': ['carbon', 'hydrogen']
            },
            'biology': {
                'cell': ['nucleus', 'membrane', 'cytoplasm'],
                'DNA': ['nucleotides', 'genes'],
                'virus': ['protein', 'RNA', 'DNA'],  # NICHT organs!
            },
            'physics': {
                'atom': ['proton', 'neutron', 'electron'],
                'gravity': 'force',  # nicht particle
                'momentum': 'property',  # nicht part
            }
        }
        
    def analyze_all(self) -> Dict[str, Any]:
        """Führt eine vollständige Qualitätsanalyse durch"""
        print("🔍 Starte umfassende Qualitätsanalyse...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_facts': self.get_total_count(),
            'predicate_analysis': self.analyze_predicates(),
            'duplicate_analysis': self.find_duplicates(),
            'semantic_issues': self.find_semantic_issues(),
            'pattern_analysis': self.analyze_patterns(),
            'quality_score': 0.0,
            'recommendations': []
        }
        
        # Berechne Qualitätsscore
        results['quality_score'] = self.calculate_quality_score(results)
        
        # Generiere Empfehlungen
        results['recommendations'] = self.generate_recommendations(results)
        
        return results
    
    def get_total_count(self) -> int:
        """Holt die Gesamtanzahl der Fakten"""
        self.cursor.execute("SELECT COUNT(*) FROM facts")
        return self.cursor.fetchone()[0]
    
    def analyze_predicates(self) -> Dict[str, Any]:
        """Analysiert die Verteilung der Prädikate"""
        self.cursor.execute("""
            SELECT 
                SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                COUNT(*) as count
            FROM facts
            GROUP BY predicate
            ORDER BY count DESC
        """)
        
        predicates = {}
        total = 0
        for row in self.cursor.fetchall():
            if row[0]:  # Ignoriere NULL
                predicates[row[0]] = row[1]
                total += row[1]
        
        # Berechne Probleme
        issues = []
        
        # Problem 1: DirectTest Dominanz
        if 'DirectTest' in predicates:
            dt_percentage = (predicates['DirectTest'] / total) * 100
            if dt_percentage > 50:
                issues.append({
                    'type': 'CRITICAL',
                    'issue': f'DirectTest macht {dt_percentage:.1f}% aller Fakten aus',
                    'impact': 'Sehr geringe Diversität'
                })
        
        # Problem 2: Unbalancierte Verteilung
        top_3_count = sum(list(predicates.values())[:3])
        top_3_percentage = (top_3_count / total) * 100
        if top_3_percentage > 80:
            issues.append({
                'type': 'WARNING',
                'issue': f'Top 3 Prädikate machen {top_3_percentage:.1f}% aus',
                'impact': 'Unbalancierte Wissensverteilung'
            })
        
        return {
            'distribution': predicates,
            'total_unique': len(predicates),
            'issues': issues,
            'diversity_score': 1.0 - (top_3_percentage / 100)
        }
    
    def find_duplicates(self) -> Dict[str, Any]:
        """Findet exakte und ähnliche Duplikate"""
        self.cursor.execute("""
            SELECT statement, COUNT(*) as count
            FROM facts
            GROUP BY statement
            HAVING count > 1
            ORDER BY count DESC
            LIMIT 100
        """)
        
        exact_duplicates = []
        for row in self.cursor.fetchall():
            exact_duplicates.append({
                'statement': row[0],
                'count': row[1]
            })
        
        # Finde ähnliche Fakten (Levenshtein-Distanz)
        self.cursor.execute("SELECT statement FROM facts ORDER BY RANDOM() LIMIT 1000")
        sample_facts = [row[0] for row in self.cursor.fetchall()]
        
        similar_pairs = []
        for i, fact1 in enumerate(sample_facts):
            for fact2 in sample_facts[i+1:]:
                similarity = difflib.SequenceMatcher(None, fact1, fact2).ratio()
                if 0.8 < similarity < 1.0:  # Ähnlich aber nicht identisch
                    similar_pairs.append({
                        'fact1': fact1,
                        'fact2': fact2,
                        'similarity': similarity
                    })
        
        return {
            'exact_duplicates': exact_duplicates,
            'exact_count': len(exact_duplicates),
            'similar_pairs': similar_pairs[:20],  # Top 20
            'similar_count': len(similar_pairs),
            'duplication_rate': len(exact_duplicates) / self.get_total_count()
        }
    
    def find_semantic_issues(self) -> Dict[str, Any]:
        """Findet semantische Probleme und falsche Fakten"""
        issues = []
        
        # Prüfe chemische Fakten
        self.cursor.execute("""
            SELECT statement FROM facts
            WHERE statement LIKE '%NH3%' OR statement LIKE '%H2O%' 
               OR statement LIKE '%CO2%' OR statement LIKE '%CH4%'
            LIMIT 100
        """)
        
        for row in self.cursor.fetchall():
            statement = row[0]
            
            # NH3 sollte kein Oxygen enthalten
            if 'NH3' in statement and 'oxygen' in statement.lower():
                issues.append({
                    'type': 'FACTUAL_ERROR',
                    'statement': statement,
                    'problem': 'NH3 (Ammoniak) enthält kein Oxygen, nur Nitrogen und Hydrogen'
                })
            
            # H2O sollte Hydrogen und Oxygen enthalten
            if 'H2O' in statement and 'carbon' in statement.lower():
                issues.append({
                    'type': 'FACTUAL_ERROR',
                    'statement': statement,
                    'problem': 'H2O enthält kein Carbon'
                })
        
        # Prüfe biologische Fakten
        self.cursor.execute("""
            SELECT statement FROM facts
            WHERE statement LIKE '%virus%' OR statement LIKE '%cell%'
               OR statement LIKE '%DNA%'
            LIMIT 100
        """)
        
        for row in self.cursor.fetchall():
            statement = row[0]
            
            # Viren haben keine Organe
            if 'virus' in statement.lower() and 'organ' in statement.lower():
                issues.append({
                    'type': 'CONCEPTUAL_ERROR',
                    'statement': statement,
                    'problem': 'Viren haben keine Organe, sie sind viel einfacher strukturiert'
                })
            
            # Gravity ist keine Particle oder Part
            if 'gravity' in statement.lower() and ('particle' in statement or 'HasPart' in statement):
                issues.append({
                    'type': 'CONCEPTUAL_ERROR',
                    'statement': statement,
                    'problem': 'Gravity ist eine Kraft, kein Teilchen oder Teil'
                })
        
        return {
            'issues': issues[:50],  # Top 50 Probleme
            'total_issues': len(issues),
            'error_types': Counter([i['type'] for i in issues])
        }
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analysiert Muster in den generierten Fakten"""
        
        # Hole die letzten 500 Fakten
        self.cursor.execute("""
            SELECT statement, created_at FROM facts
            ORDER BY id DESC
            LIMIT 500
        """)
        
        recent_facts = self.cursor.fetchall()
        
        # Analysiere Entitäten-Frequenz
        entities = []
        predicates = []
        
        for fact in recent_facts:
            statement = fact[0]
            # Extrahiere Prädikat
            if '(' in statement:
                pred = statement.split('(')[0]
                predicates.append(pred)
                
                # Extrahiere Entitäten
                match = re.match(r'.*\((.*?)\)', statement)
                if match:
                    parts = match.group(1).split(',')
                    entities.extend([p.strip() for p in parts])
        
        entity_freq = Counter(entities)
        predicate_freq = Counter(predicates)
        
        # Finde übermäßig wiederholte Muster
        repetitive_patterns = []
        
        # Prüfe auf sich wiederholende Entitäten
        for entity, count in entity_freq.most_common(10):
            if count > 20:  # Mehr als 20 mal in 500 Fakten
                repetitive_patterns.append({
                    'type': 'REPETITIVE_ENTITY',
                    'entity': entity,
                    'frequency': count,
                    'percentage': (count / 500) * 100
                })
        
        return {
            'top_entities': dict(entity_freq.most_common(20)),
            'top_predicates': dict(predicate_freq.most_common(10)),
            'repetitive_patterns': repetitive_patterns,
            'diversity_metrics': {
                'unique_entities': len(set(entities)),
                'unique_predicates': len(set(predicates)),
                'entity_diversity': len(set(entities)) / len(entities) if entities else 0,
                'predicate_diversity': len(set(predicates)) / len(predicates) if predicates else 0
            }
        }
    
    def calculate_quality_score(self, results: Dict) -> float:
        """Berechnet einen Gesamtqualitätsscore (0-100)"""
        score = 100.0
        
        # Abzüge für Probleme
        
        # DirectTest Dominanz
        pred_analysis = results['predicate_analysis']
        if pred_analysis['distribution'].get('DirectTest', 0) > 10000:
            dt_percentage = pred_analysis['distribution']['DirectTest'] / results['total_facts']
            score -= min(40, dt_percentage * 50)  # Max 40 Punkte Abzug
        
        # Duplikate
        dup_rate = results['duplicate_analysis']['duplication_rate']
        score -= min(20, dup_rate * 100)  # Max 20 Punkte Abzug
        
        # Semantische Fehler
        semantic_issues = results['semantic_issues']['total_issues']
        score -= min(20, semantic_issues * 0.5)  # Max 20 Punkte Abzug
        
        # Diversität
        diversity = results['pattern_analysis']['diversity_metrics']['entity_diversity']
        if diversity < 0.5:
            score -= (0.5 - diversity) * 20  # Max 10 Punkte Abzug
        
        return max(0, min(100, score))
    
    def generate_recommendations(self, results: Dict) -> List[str]:
        """Generiert konkrete Handlungsempfehlungen"""
        recommendations = []
        
        # DirectTest Problem
        if 'DirectTest' in results['predicate_analysis']['distribution']:
            dt_count = results['predicate_analysis']['distribution']['DirectTest']
            if dt_count > 10000:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'action': 'DirectTest-Generator stoppen oder stark reduzieren',
                    'reason': f'{dt_count} DirectTest-Fakten dominieren die Datenbank',
                    'command': 'python src_hexagonal/stop_direct_test_generator.py'
                })
        
        # Duplikate
        if results['duplicate_analysis']['exact_count'] > 100:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Duplikat-Bereinigung durchführen',
                'reason': f"{results['duplicate_analysis']['exact_count']} exakte Duplikate gefunden",
                'command': 'python scripts/remove_duplicate_facts.py'
            })
        
        # Semantische Fehler
        if results['semantic_issues']['total_issues'] > 10:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Fact-Validator implementieren',
                'reason': f"{results['semantic_issues']['total_issues']} fehlerhafte Fakten gefunden",
                'command': 'python scripts/implement_fact_validator.py'
            })
        
        # Diversität
        if results['pattern_analysis']['diversity_metrics']['entity_diversity'] < 0.5:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Diversität der Entitäten erhöhen',
                'reason': 'Zu viele wiederholte Entitäten',
                'command': 'python scripts/enhance_entity_diversity.py'
            })
        
        # Generator-Geschwindigkeit
        recommendations.append({
            'priority': 'INFO',
            'action': 'Generator-Geschwindigkeit prüfen',
            'reason': '800-1000 Fakten/Minute ist sehr schnell - Qualität vor Quantität!',
            'command': 'python scripts/adjust_generation_rate.py --target-rate=100'
        })
        
        return recommendations
    
    def generate_report(self, results: Dict) -> str:
        """Generiert einen formattierten Report"""
        report = []
        report.append("=" * 60)
        report.append("   HAK-GAL KNOWLEDGE BASE QUALITÄTSANALYSE")
        report.append("=" * 60)
        report.append(f"\nZeitpunkt: {results['timestamp']}")
        report.append(f"Gesamtanzahl Fakten: {results['total_facts']:,}")
        report.append(f"\n{'='*60}")
        
        # Qualitätsscore
        score = results['quality_score']
        score_emoji = "🟢" if score > 70 else "🟡" if score > 40 else "🔴"
        report.append(f"\n{score_emoji} QUALITÄTSSCORE: {score:.1f}/100")
        
        # Hauptprobleme
        report.append(f"\n{'='*60}")
        report.append("\n🚨 HAUPTPROBLEME:")
        report.append("-" * 40)
        
        # DirectTest Dominanz
        if 'DirectTest' in results['predicate_analysis']['distribution']:
            dt_count = results['predicate_analysis']['distribution']['DirectTest']
            dt_percentage = (dt_count / results['total_facts']) * 100
            report.append(f"• DirectTest-Dominanz: {dt_count:,} Fakten ({dt_percentage:.1f}%)")
        
        # Duplikate
        report.append(f"• Exakte Duplikate: {results['duplicate_analysis']['exact_count']}")
        report.append(f"• Ähnliche Paare: {results['duplicate_analysis']['similar_count']}")
        
        # Semantische Fehler
        report.append(f"• Semantische Fehler: {results['semantic_issues']['total_issues']}")
        
        # Diversität
        diversity = results['pattern_analysis']['diversity_metrics']
        report.append(f"• Entitäten-Diversität: {diversity['entity_diversity']:.2%}")
        
        # Top Empfehlungen
        report.append(f"\n{'='*60}")
        report.append("\n💡 EMPFEHLUNGEN:")
        report.append("-" * 40)
        
        for rec in results['recommendations'][:5]:
            report.append(f"\n[{rec['priority']}] {rec['action']}")
            report.append(f"  Grund: {rec['reason']}")
            if 'command' in rec:
                report.append(f"  Befehl: {rec['command']}")
        
        # Beispiele fehlerhafter Fakten
        if results['semantic_issues']['issues']:
            report.append(f"\n{'='*60}")
            report.append("\n❌ BEISPIELE FEHLERHAFTER FAKTEN:")
            report.append("-" * 40)
            
            for issue in results['semantic_issues']['issues'][:5]:
                report.append(f"\n• {issue['statement']}")
                report.append(f"  Problem: {issue['problem']}")
        
        report.append(f"\n{'='*60}")
        
        return "\n".join(report)

def main():
    """Hauptfunktion"""
    print("Initialisiere Qualitätsanalyse...")
    
    analyzer = FactQualityAnalyzer()
    results = analyzer.analyze_all()
    
    # Generiere Report
    report = analyzer.generate_report(results)
    print(report)
    
    # Speichere detaillierte Ergebnisse
    with open("kb_quality_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Detaillierte Ergebnisse gespeichert in: kb_quality_analysis.json")
    
    # Speichere Report
    with open("kb_quality_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Report gespeichert in: kb_quality_report.md")
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Zeige kritische Aktionen
    if results['quality_score'] < 50:
        print("\n🚨 KRITISCH: Qualitätsscore unter 50!")
        print("Sofortige Maßnahmen erforderlich:")
        for rec in results['recommendations']:
            if rec['priority'] == 'CRITICAL':
                print(f"  → {rec['action']}")
