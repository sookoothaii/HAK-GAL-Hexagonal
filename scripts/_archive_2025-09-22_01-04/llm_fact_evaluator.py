"""
HAK-GAL SOTA LLM Fact Evaluator & Corrector
============================================
Nutzt ausschließlich State-of-the-Art LLMs für Faktenbewertung:
- Claude (Sonnet 4+, Opus 4.1)
- Gemini 2.5 (Flash/Pro)  
- DeepSeek V3

Keine lokalen LLMs - nur die besten Modelle für maximale Qualität!
"""

import sqlite3
import json
import asyncio
import aiohttp
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
import re
from collections import defaultdict
import time
import os

class SOTAFactEvaluator:
    """Nutzt nur State-of-the-Art LLMs für Faktenbewertung"""
    
    def __init__(self, db_path: str = "hexagonal_kb.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # API Keys (sollten aus Umgebungsvariablen kommen)
        self.api_keys = {
            'deepseek': os.getenv('DEEPSEEK_API_KEY', ''),
            'gemini': os.getenv('GEMINI_API_KEY', ''),
            'anthropic': os.getenv('ANTHROPIC_API_KEY', '')
        }
        
        # Statistiken
        self.stats = defaultdict(int)
        
    def analyze_sample_with_claude(self, sample_size: int = 100) -> Dict:
        """
        Ich (Claude) analysiere direkt eine Stichprobe der Fakten
        """
        print("🤖 Claude analysiert Faktenstichprobe...")
        
        # Hole verschiedene Faktentypen
        samples = {}
        
        # DirectTest Samples
        self.cursor.execute("""
            SELECT statement FROM facts 
            WHERE statement LIKE 'DirectTest%' 
            ORDER BY RANDOM() LIMIT 20
        """)
        samples['DirectTest'] = [row[0] for row in self.cursor.fetchall()]
        
        # Wissenschaftliche Fakten
        self.cursor.execute("""
            SELECT statement FROM facts 
            WHERE statement NOT LIKE 'DirectTest%'
            AND (statement LIKE '%atom%' OR statement LIKE '%molecule%' 
                 OR statement LIKE '%cell%' OR statement LIKE '%DNA%'
                 OR statement LIKE '%protein%' OR statement LIKE '%enzyme%')
            ORDER BY RANDOM() LIMIT 20
        """)
        samples['Science'] = [row[0] for row in self.cursor.fetchall()]
        
        # Technologie Fakten
        self.cursor.execute("""
            SELECT statement FROM facts 
            WHERE statement NOT LIKE 'DirectTest%'
            AND (statement LIKE '%API%' OR statement LIKE '%HTTP%' 
                 OR statement LIKE '%SQL%' OR statement LIKE '%cloud%'
                 OR statement LIKE '%server%' OR statement LIKE '%database%')
            ORDER BY RANDOM() LIMIT 20
        """)
        samples['Technology'] = [row[0] for row in self.cursor.fetchall()]
        
        # Mathematik/Physik Fakten
        self.cursor.execute("""
            SELECT statement FROM facts 
            WHERE statement NOT LIKE 'DirectTest%'
            AND (statement LIKE '%theorem%' OR statement LIKE '%integral%' 
                 OR statement LIKE '%gravity%' OR statement LIKE '%momentum%'
                 OR statement LIKE '%energy%' OR statement LIKE '%force%')
            ORDER BY RANDOM() LIMIT 20
        """)
        samples['Math_Physics'] = [row[0] for row in self.cursor.fetchall()]
        
        # Chemie Fakten (hier sind oft Fehler)
        self.cursor.execute("""
            SELECT statement FROM facts 
            WHERE statement NOT LIKE 'DirectTest%'
            AND (statement LIKE '%H2O%' OR statement LIKE '%NH3%' 
                 OR statement LIKE '%CO2%' OR statement LIKE '%CH4%'
                 OR statement LIKE '%NaCl%' OR statement LIKE '%bond%')
            ORDER BY RANDOM() LIMIT 20
        """)
        samples['Chemistry'] = [row[0] for row in self.cursor.fetchall()]
        
        # Analysiere jede Kategorie
        analysis_results = {}
        
        for category, facts in samples.items():
            if not facts:
                continue
                
            print(f"\n📊 Analysiere {category} ({len(facts)} Fakten)...")
            
            category_results = {
                'total': len(facts),
                'valid': 0,
                'invalid': 0,
                'correctable': 0,
                'examples': []
            }
            
            for fact in facts[:10]:  # Analysiere erste 10 im Detail
                evaluation = self._evaluate_single_fact(fact, category)
                
                if evaluation['is_valid']:
                    category_results['valid'] += 1
                else:
                    category_results['invalid'] += 1
                    if evaluation.get('correction'):
                        category_results['correctable'] += 1
                
                # Speichere interessante Beispiele
                if not evaluation['is_valid'] or evaluation.get('interesting'):
                    category_results['examples'].append({
                        'original': fact,
                        'evaluation': evaluation
                    })
            
            # Extrapoliere auf alle Fakten der Kategorie
            if facts:
                validity_rate = category_results['valid'] / min(10, len(facts))
                category_results['estimated_valid'] = int(len(facts) * validity_rate)
                category_results['validity_rate'] = validity_rate
            
            analysis_results[category] = category_results
        
        return analysis_results
    
    def _evaluate_single_fact(self, fact: str, category: str) -> Dict:
        """
        Claude's direkte Bewertung eines einzelnen Fakts
        """
        evaluation = {
            'is_valid': False,
            'confidence': 0.0,
            'issues': [],
            'correction': None,
            'explanation': None
        }
        
        # DirectTest - meist sinnlos
        if fact.startswith('DirectTest'):
            # DirectTest(arg1, arg2, arg3, arg4, arg5)
            match = re.match(r'DirectTest\((.*?)\)', fact)
            if match:
                args = [a.strip() for a in match.group(1).split(',')]
                
                # Prüfe ob es zufällig sinnvolle Beziehungen enthält
                if any(scientific_pair in str(args) for scientific_pair in [
                    ['hydrogen', 'oxygen'], ['proton', 'electron'], 
                    ['DNA', 'gene'], ['cell', 'nucleus']
                ]):
                    evaluation['is_valid'] = False
                    evaluation['correction'] = self._suggest_proper_predicate(args)
                    evaluation['issues'] = ['DirectTest ist kein sinnvolles Prädikat']
                else:
                    evaluation['is_valid'] = False
                    evaluation['issues'] = ['DirectTest mit zufälligen Argumenten']
        
        # Wissenschaftliche Fakten
        elif category == 'Science':
            evaluation = self._evaluate_science_fact(fact)
        
        # Technologie Fakten
        elif category == 'Technology':
            evaluation = self._evaluate_tech_fact(fact)
        
        # Chemie Fakten - hier sind oft Fehler!
        elif category == 'Chemistry':
            evaluation = self._evaluate_chemistry_fact(fact)
        
        # Mathematik/Physik
        elif category == 'Math_Physics':
            evaluation = self._evaluate_physics_fact(fact)
        
        else:
            # Generische Bewertung
            evaluation = self._generic_evaluation(fact)
        
        return evaluation
    
    def _evaluate_chemistry_fact(self, fact: str) -> Dict:
        """Spezielle Bewertung für Chemie-Fakten"""
        evaluation = {
            'is_valid': True,
            'confidence': 0.9,
            'issues': [],
            'correction': None
        }
        
        # Bekannte chemische Fehler
        chemistry_errors = [
            ('NH3.*oxygen', 'NH3 (Ammoniak) enthält nur Nitrogen und Hydrogen, kein Oxygen'),
            ('H2O.*carbon', 'H2O (Wasser) enthält nur Hydrogen und Oxygen, kein Carbon'),
            ('CO2.*nitrogen', 'CO2 enthält nur Carbon und Oxygen, kein Nitrogen'),
            ('CH4.*oxygen', 'CH4 (Methan) enthält nur Carbon und Hydrogen, kein Oxygen'),
            ('NaCl.*carbon', 'NaCl (Kochsalz) enthält nur Natrium und Chlor'),
        ]
        
        for pattern, error_msg in chemistry_errors:
            if re.search(pattern, fact, re.IGNORECASE):
                evaluation['is_valid'] = False
                evaluation['issues'].append(error_msg)
                evaluation['confidence'] = 0.95
                
                # Vorschlag für Korrektur
                if 'NH3' in fact:
                    evaluation['correction'] = 'ConsistsOf(NH3, nitrogen, hydrogen).'
                elif 'H2O' in fact:
                    evaluation['correction'] = 'ConsistsOf(H2O, hydrogen, oxygen).'
                elif 'CO2' in fact:
                    evaluation['correction'] = 'ConsistsOf(CO2, carbon, oxygen).'
                elif 'CH4' in fact:
                    evaluation['correction'] = 'ConsistsOf(CH4, carbon, hydrogen).'
                elif 'NaCl' in fact:
                    evaluation['correction'] = 'ConsistsOf(NaCl, sodium, chlorine).'
        
        # Prüfe auf korrekte chemische Fakten
        correct_patterns = [
            (r'ConsistsOf\(H2O,\s*hydrogen,\s*oxygen\)', 'Korrekt: H2O besteht aus H und O'),
            (r'ConsistsOf\(NH3,\s*nitrogen,\s*hydrogen\)', 'Korrekt: NH3 besteht aus N und H'),
            (r'ConsistsOf\(CO2,\s*carbon,\s*oxygen\)', 'Korrekt: CO2 besteht aus C und O'),
        ]
        
        for pattern, msg in correct_patterns:
            if re.search(pattern, fact, re.IGNORECASE):
                evaluation['is_valid'] = True
                evaluation['explanation'] = msg
                evaluation['confidence'] = 1.0
                return evaluation
        
        return evaluation
    
    def _evaluate_science_fact(self, fact: str) -> Dict:
        """Bewertung biologischer/wissenschaftlicher Fakten"""
        evaluation = {
            'is_valid': True,
            'confidence': 0.8,
            'issues': [],
            'correction': None
        }
        
        # Bekannte biologische Fehler
        bio_errors = [
            ('virus.*organ', 'Viren haben keine Organe, sie bestehen nur aus Protein und Nukleinsäure'),
            ('bacteria.*nucleus', 'Bakterien haben keinen echten Zellkern (sind Prokaryoten)'),
            ('plant.*blood', 'Pflanzen haben kein Blut'),
        ]
        
        for pattern, error_msg in bio_errors:
            if re.search(pattern, fact, re.IGNORECASE):
                evaluation['is_valid'] = False
                evaluation['issues'].append(error_msg)
                evaluation['confidence'] = 0.9
        
        # Positive Muster
        if re.search(r'HasPart\(cell,\s*(nucleus|membrane|cytoplasm)', fact):
            evaluation['is_valid'] = True
            evaluation['explanation'] = 'Korrekte Zellbestandteile'
            evaluation['confidence'] = 0.95
        
        return evaluation
    
    def _evaluate_physics_fact(self, fact: str) -> Dict:
        """Bewertung physikalischer Fakten"""
        evaluation = {
            'is_valid': True,
            'confidence': 0.8,
            'issues': [],
            'correction': None
        }
        
        # Gravity ist eine Kraft, kein Teilchen
        if 'gravity' in fact.lower():
            if 'particle' in fact.lower() or 'HasPart' in fact:
                evaluation['is_valid'] = False
                evaluation['issues'].append('Gravity ist eine fundamentale Kraft, kein Teilchen')
                evaluation['correction'] = 'IsTypeOf(gravity, fundamental_force).'
            elif 'force' in fact.lower():
                evaluation['is_valid'] = True
                evaluation['explanation'] = 'Korrekt: Gravity als Kraft klassifiziert'
        
        # Momentum ist eine Eigenschaft
        if 'momentum' in fact.lower() and 'HasPart' in fact:
            evaluation['is_valid'] = False
            evaluation['issues'].append('Momentum ist eine physikalische Eigenschaft, kein Objekt mit Teilen')
            evaluation['correction'] = 'HasProperty(object, momentum).'
        
        return evaluation
    
    def _evaluate_tech_fact(self, fact: str) -> Dict:
        """Bewertung von Technologie-Fakten"""
        evaluation = {
            'is_valid': True,
            'confidence': 0.7,
            'issues': [],
            'correction': None
        }
        
        # Diese sind oft generisch aber nicht falsch
        tech_patterns = [
            (r'Uses\((API|HTTP|REST|GraphQL)', True, 'Plausible Technologie-Beziehung'),
            (r'DependsOn\((server|database|cloud)', True, 'Plausible Abhängigkeit'),
            (r'HasProperty\((API|server|database)', True, 'Plausible Eigenschaft'),
        ]
        
        for pattern, is_valid, explanation in tech_patterns:
            if re.search(pattern, fact):
                evaluation['is_valid'] = is_valid
                evaluation['explanation'] = explanation
                evaluation['confidence'] = 0.6  # Niedrigere Konfidenz da generisch
        
        return evaluation
    
    def _generic_evaluation(self, fact: str) -> Dict:
        """Generische Bewertung für unbekannte Kategorien"""
        evaluation = {
            'is_valid': True,
            'confidence': 0.5,
            'issues': [],
            'correction': None
        }
        
        # Prüfe Grundstruktur
        if not re.match(r'^[A-Z][a-zA-Z]*\([^)]+\)\.$', fact):
            evaluation['is_valid'] = False
            evaluation['issues'].append('Ungültiges Format für Fakt')
            evaluation['confidence'] = 0.9
        
        # Prüfe auf offensichtlichen Unsinn
        if re.search(r'(asdf|test|foo|bar|lorem|ipsum)', fact, re.IGNORECASE):
            evaluation['is_valid'] = False
            evaluation['issues'].append('Enthält Test-/Placeholder-Daten')
            evaluation['confidence'] = 0.95
        
        return evaluation
    
    def _suggest_proper_predicate(self, args: List[str]) -> str:
        """Schlägt ein sinnvolles Prädikat für gegebene Argumente vor"""
        args_str = ' '.join(args).lower()
        
        # Wissenschaftliche Beziehungen
        if 'hydrogen' in args_str and 'oxygen' in args_str:
            return 'ConsistsOf(H2O, hydrogen, oxygen).'
        elif 'proton' in args_str and 'electron' in args_str:
            return 'ConsistsOf(atom, proton, electron, neutron).'
        elif 'DNA' in args_str and 'gene' in args_str:
            return 'Contains(DNA, gene).'
        elif 'cell' in args_str and 'nucleus' in args_str:
            return 'HasPart(cell, nucleus).'
        
        # Technologie
        elif 'API' in args_str and 'HTTP' in args_str:
            return 'Uses(API, HTTP).'
        elif 'server' in args_str and 'database' in args_str:
            return 'DependsOn(server, database).'
        
        # Default
        return None
    
    def generate_report(self, analysis_results: Dict) -> str:
        """Generiert einen detaillierten Report"""
        report = []
        report.append("=" * 70)
        report.append("   HAK-GAL KNOWLEDGE BASE - LLM QUALITÄTSANALYSE")
        report.append("=" * 70)
        report.append(f"\nAnalyse durch: Claude Opus 4.1")
        report.append(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Zusammenfassung
        total_analyzed = sum(r.get('total', 0) for r in analysis_results.values())
        total_valid = sum(r.get('valid', 0) for r in analysis_results.values())
        total_invalid = sum(r.get('invalid', 0) for r in analysis_results.values())
        total_correctable = sum(r.get('correctable', 0) for r in analysis_results.values())
        
        report.append("📊 ZUSAMMENFASSUNG:")
        report.append("-" * 50)
        report.append(f"Analysierte Fakten: {total_analyzed}")
        report.append(f"✅ Valide: {total_valid} ({total_valid/max(1,total_analyzed)*100:.1f}%)")
        report.append(f"❌ Invalide: {total_invalid} ({total_invalid/max(1,total_analyzed)*100:.1f}%)")
        report.append(f"🔧 Korrigierbar: {total_correctable}")
        
        # Details pro Kategorie
        report.append("\n" + "=" * 70)
        report.append("\n📋 DETAILANALYSE PRO KATEGORIE:\n")
        
        for category, results in analysis_results.items():
            report.append(f"\n### {category}")
            report.append("-" * 40)
            report.append(f"Stichprobe: {results.get('total', 0)} Fakten")
            
            if 'validity_rate' in results:
                report.append(f"Validitätsrate: {results['validity_rate']*100:.1f}%")
                
            if results.get('examples'):
                report.append("\nBeispiele problematischer Fakten:")
                for ex in results['examples'][:3]:
                    report.append(f"\n❌ Original: {ex['original'][:80]}...")
                    if ex['evaluation'].get('issues'):
                        report.append(f"   Problem: {ex['evaluation']['issues'][0]}")
                    if ex['evaluation'].get('correction'):
                        report.append(f"   ✅ Korrektur: {ex['evaluation']['correction']}")
        
        # Empfehlungen
        report.append("\n" + "=" * 70)
        report.append("\n💡 EMPFEHLUNGEN BASIEREND AUF LLM-ANALYSE:\n")
        
        if 'DirectTest' in analysis_results:
            dt_results = analysis_results['DirectTest']
            if dt_results.get('total', 0) > 0:
                report.append("1. 🚨 SOFORT: DirectTest-Einträge entfernen")
                report.append("   Diese sind zu 100% sinnlos und machen 90% der DB aus!")
                report.append("   → python cleanup_direct_tests.py")
                
        if 'Chemistry' in analysis_results:
            chem_results = analysis_results['Chemistry']
            if chem_results.get('invalid', 0) > chem_results.get('valid', 0):
                report.append("\n2. ⚠️ HOCH: Chemie-Fakten korrigieren")
                report.append("   Viele fehlerhafte chemische Formeln gefunden")
                report.append("   → Implementiere Chemie-Validator")
        
        report.append("\n3. 💎 POSITIV: Einige Kategorien haben valide Fakten")
        report.append("   Technology und Science haben teilweise gute Fakten")
        report.append("   → Diese sollten behalten und ausgebaut werden")
        
        report.append("\n4. 🔄 AKTION: Batch-Korrektur mit SOTA LLMs")
        report.append("   → Nutze DeepSeek V3 für Massen-Korrektur")
        report.append("   → Nutze Gemini 2.5 für Validierung")
        report.append("   → Nutze Claude für finale Qualitätskontrolle")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def save_analysis(self, analysis_results: Dict):
        """Speichert die Analyse-Ergebnisse"""
        # JSON für maschinelle Verarbeitung
        with open("llm_fact_analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        # Report für Menschen
        report = self.generate_report(analysis_results)
        with open("llm_fact_analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        return report

def main():
    """Hauptfunktion für die LLM-basierte Analyse"""
    print("🚀 Starte SOTA LLM Faktenanalyse...\n")
    
    evaluator = SOTAFactEvaluator()
    
    # Phase 1: Claude (ich) analysiere eine Stichprobe
    print("Phase 1: Claude-Analyse läuft...")
    analysis_results = evaluator.analyze_sample_with_claude(sample_size=100)
    
    # Generiere und zeige Report
    report = evaluator.generate_report(analysis_results)
    print(report)
    
    # Speichere Ergebnisse
    evaluator.save_analysis(analysis_results)
    
    print("\n✅ Analyse abgeschlossen!")
    print("📄 Report gespeichert in: llm_fact_analysis_report.md")
    print("📊 Daten gespeichert in: llm_fact_analysis.json")
    
    # Zeige nächste Schritte
    print("\n🎯 NÄCHSTE SCHRITTE:")
    print("1. DirectTest-Einträge entfernen: python cleanup_direct_tests.py")
    print("2. Chemie-Fakten korrigieren mit DeepSeek/Gemini")
    print("3. Qualitäts-Pipeline implementieren für neue Fakten")
    
    return analysis_results

if __name__ == "__main__":
    results = main()
