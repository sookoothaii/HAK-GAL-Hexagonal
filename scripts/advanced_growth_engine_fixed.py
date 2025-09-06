#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Advanced Growth Engine with FIXED Complex Fact Support
==============================================================
- Korrekte Validierung für variable Argumentanzahl
- Support für alle Prädikat-Typen
- Mathematische Formeln und Gleichungen
- Cross-Domain Knowledge Mining
"""

import requests
import json
import time
import re
import random
import sqlite3
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
from pathlib import Path

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:5002/api"
DB_PATH = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

# --- ERWEITERTE VALIDIERUNG ---
def validate_complex_fact(fact: str) -> bool:
    """
    Validiere Fakten mit variabler Argumentanzahl
    Unterstützt 1-10 Argumente und verschiedene Prädikat-Typen
    """
    if not fact or not fact.endswith('.'):
        return False
    
    # Entferne den Punkt am Ende für Parsing
    fact_no_dot = fact[:-1]
    
    # Pattern für Prädikate mit variabler Argumentanzahl
    # Prädikat(Arg1) oder Prädikat(Arg1, Arg2, ..., ArgN)
    pattern = r'^[A-Z][A-Za-z0-9_]*\([^()]+(?:,\s*[^(),]+)*\)$'
    
    if not re.match(pattern, fact_no_dot):
        return False
    
    # Zusätzliche Validierung: Prüfe ob Klammern balanciert sind
    open_count = fact.count('(')
    close_count = fact.count(')')
    
    if open_count != close_count or open_count == 0:
        return False
    
    # Prüfe ob mindestens 1 Argument vorhanden
    match = re.match(r'^([A-Z][A-Za-z0-9_]*)\(([^)]+)\)$', fact_no_dot)
    if match:
        predicate = match.group(1)
        args_str = match.group(2)
        
        # Split arguments (handle complex args with special chars)
        # Einfache Trennung bei Kommas, die nicht in geschachtelten Strukturen sind
        args = []
        current_arg = ""
        depth = 0
        
        for char in args_str:
            if char == '(' or char == '[' or char == '{':
                depth += 1
            elif char == ')' or char == ']' or char == '}':
                depth -= 1
            elif char == ',' and depth == 0:
                args.append(current_arg.strip())
                current_arg = ""
                continue
            current_arg += char
        
        if current_arg.strip():
            args.append(current_arg.strip())
        
        # Mindestens 1 Argument erforderlich
        if len(args) == 0:
            return False
        
        # Maximal 10 Argumente (kann angepasst werden)
        if len(args) > 10:
            return False
        
        return True
    
    return False

# --- DYNAMIC TOPIC DISCOVERY ---
class DynamicTopicDiscovery:
    """Entdeckt automatisch neue Themenfelder basierend auf KB-Analyse"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.discovered_topics = set()
        self.entity_graph = defaultdict(set)
        self.predicate_stats = Counter()
        
    def analyze_knowledge_base(self) -> Dict[str, Any]:
        """Analysiere KB für neue Themenclusters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Hole alle Fakten
            cursor.execute("SELECT statement FROM facts LIMIT 10000")
            all_facts = [row[0] for row in cursor.fetchall()]
            
            # Analysiere Entities und Predicates
            entities = set()
            predicates = Counter()
            connections = defaultdict(set)
            
            for fact in all_facts:
                # Flexibleres Parsing für verschiedene Argumentanzahlen
                match = re.match(r'^([A-Za-z0-9_]+)\(([^)]+)\)\.$', fact)
                if match:
                    pred = match.group(1)
                    args_str = match.group(2)
                    
                    predicates[pred] += 1
                    
                    # Parse alle Argumente
                    args = [a.strip() for a in args_str.split(',')]
                    for arg in args:
                        # Bereinige Argument
                        clean_arg = re.sub(r'[^A-Za-z0-9_]', '', arg)
                        if clean_arg:
                            entities.add(clean_arg)
                            # Verbinde erste und letzte Entity
                            if len(args) > 1:
                                first = re.sub(r'[^A-Za-z0-9_]', '', args[0])
                                last = re.sub(r'[^A-Za-z0-9_]', '', args[-1])
                                if first and last and first != last:
                                    connections[first].add(last)
                                    connections[last].add(first)
            
            # Finde Cluster
            clusters = self._find_clusters(connections, entities)
            
            # Identifiziere unterrepräsentierte Bereiche
            gaps = self._identify_knowledge_gaps(predicates, entities)
            
            conn.close()
            
            return {
                'entities': entities,
                'predicates': dict(predicates),
                'clusters': clusters,
                'gaps': gaps,
                'total_facts': len(all_facts)
            }
            
        except Exception as e:
            print(f"[TopicDiscovery] Error: {e}")
            return {'entities': set(), 'predicates': {}, 'clusters': [], 'gaps': [], 'total_facts': 0}
    
    def _find_clusters(self, connections: Dict, entities: Set) -> List[Dict]:
        """Finde Themenclusters basierend auf Vernetzung"""
        clusters = []
        visited = set()
        
        for entity in list(entities)[:100]:  # Limit für Performance
            if entity in visited:
                continue
                
            # BFS für zusammenhängende Komponenten
            cluster = set()
            queue = [entity]
            
            while queue and len(cluster) < 50:  # Limit cluster size
                current = queue.pop(0)
                if current in visited:
                    continue
                    
                visited.add(current)
                cluster.add(current)
                
                # Füge verbundene Entities hinzu
                for connected in connections.get(current, []):
                    if connected not in visited and len(cluster) < 50:
                        queue.append(connected)
            
            if len(cluster) > 3:  # Nur signifikante Cluster
                clusters.append({
                    'entities': list(cluster)[:10],  # Limit für Übersichtlichkeit
                    'size': len(cluster),
                    'core': entity
                })
        
        return sorted(clusters, key=lambda x: x['size'], reverse=True)[:10]
    
    def _identify_knowledge_gaps(self, predicates: Counter, entities: Set) -> List[str]:
        """Identifiziere Bereiche mit wenig Wissen"""
        gaps = []
        
        # Vorschläge für neue Topics
        suggestions = [
            "Mathematical_Formulas",
            "Chemical_Reactions", 
            "Historical_Events",
            "Geographic_Relations",
            "Economic_Models",
            "Physical_Laws",
            "Biological_Processes",
            "Computer_Algorithms",
            "Social_Networks",
            "Linguistic_Patterns"
        ]
        
        # Filtere bereits gut abgedeckte Topics
        for topic in suggestions:
            topic_words = topic.lower().split('_')
            coverage = sum(1 for e in entities if any(w in str(e).lower() for w in topic_words))
            if coverage < 10:  # Wenig Abdeckung
                gaps.append(topic)
        
        return gaps[:5]
    
    def generate_exploration_topics(self, analysis: Dict) -> List[Dict]:
        """Generiere neue Topics basierend auf KB-Analyse"""
        topics = []
        
        # 1. Topics aus Clustern
        for cluster in analysis.get('clusters', [])[:3]:
            core_entity = cluster['core']
            topics.append({
                'name': f"Deep_Dive_{core_entity}",
                'focus': core_entity,
                'related': cluster['entities'][:5],
                'type': 'cluster_expansion'
            })
        
        # 2. Topics aus Knowledge Gaps
        for gap in analysis.get('gaps', [])[:3]:
            topics.append({
                'name': gap,
                'focus': gap.replace('_', ' '),
                'related': [],
                'type': 'gap_filling'
            })
        
        # 3. Cross-Domain Topics
        if len(analysis.get('clusters', [])) >= 2:
            cluster1 = analysis['clusters'][0]
            cluster2 = analysis['clusters'][1]
            topics.append({
                'name': f"Bridge_{cluster1['core']}_{cluster2['core']}",
                'focus': f"Connections between {cluster1['core']} and {cluster2['core']}",
                'related': cluster1['entities'][:2] + cluster2['entities'][:2],
                'type': 'cross_domain'
            })
        
        return topics

# --- COMPLEX FACT GENERATOR ---
class ComplexFactGenerator:
    """Generiert komplexe Fakten mit variabler Argumentanzahl"""
    
    def __init__(self):
        self.mathematical_formulas = [
            ("NewtonsSecondLaw", "F=ma", "F,m,a", "Classical_Mechanics"),
            ("EinsteinMassEnergy", "E=mc^2", "E,m,c", "Relativity"),
            ("SchrodingerEquation", "iℏ∂ψ/∂t=Hψ", "ψ,H,t", "Quantum_Mechanics"),
            ("MaxwellEquation", "∇×E=-∂B/∂t", "E,B,t", "Electromagnetism"),
            ("EulerIdentity", "e^(iπ)+1=0", "e,i,π", "Mathematics"),
            ("PythagoreanTheorem", "a^2+b^2=c^2", "a,b,c", "Geometry"),
            ("GaussianDistribution", "f(x)=(1/σ√(2π))e^(-½((x-μ)/σ)²)", "x,μ,σ", "Statistics"),
            ("FourierTransform", "F(ω)=∫f(t)e^(-iωt)dt", "f,t,ω", "Signal_Processing"),
            ("NavierStokes", "ρ(∂v/∂t+v·∇v)=-∇p+μ∇²v+f", "v,p,ρ,μ", "Fluid_Dynamics"),
            ("BlackScholes", "∂V/∂t+½σ²S²∂²V/∂S²+rS∂V/∂S-rV=0", "V,S,t,σ,r", "Finance")
        ]
        
    def generate_mathematical_facts(self) -> List[str]:
        """Generiere mathematische Formeln als Fakten"""
        facts = []
        
        for name, equation, variables, domain in self.mathematical_formulas:
            # Verschiedene gültige Darstellungsformen
            facts.append(f"Formula({name}, {equation}, {variables}).")
            facts.append(f"Formula({name}, {equation}, {variables}, {domain}).")
            facts.append(f"UsedIn({name}, {domain}).")
            facts.append(f"HasVariables({name}, {variables}).")
            facts.append(f"Equation({name}, {equation}).")
            facts.append(f"DescribedBy({name}, {equation}).")
            
        return facts
    
    def generate_complex_relations(self, entities: List[str]) -> List[str]:
        """Generiere komplexe Relationen zwischen Entities"""
        facts = []
        
        if len(entities) < 3:
            return facts
        
        # 3-stellige Relationen
        for i in range(min(5, len(entities)-2)):
            e1, e2, e3 = random.sample(entities, 3)
            facts.append(f"Mediates({e1}, {e2}, {e3}).")
            facts.append(f"Connects({e1}, {e2}, {e3}).")
            facts.append(f"Links({e1}, {e2}, {e3}).")
        
        # 4-stellige Relationen
        if len(entities) >= 4:
            for i in range(min(3, len(entities)-3)):
                e1, e2, e3, e4 = random.sample(entities, 4)
                facts.append(f"Process({e1}, {e2}, {e3}, {e4}).")
                facts.append(f"Transform({e1}, {e2}, {e3}, {e4}).")
        
        # 5-stellige Relationen
        if len(entities) >= 5:
            for i in range(min(2, len(entities)-4)):
                es = random.sample(entities, 5)
                facts.append(f"System({es[0]}, {es[1]}, {es[2]}, {es[3]}, {es[4]}).")
        
        return facts
    
    def generate_domain_formulas(self, domain: str) -> List[str]:
        """Generiere domänenspezifische Formeln"""
        facts = []
        
        domain_formulas = {
            "Chemistry": [
                "Formula(WaterFormation, 2H2+O2=2H2O, H2_O2_H2O).",
                "Reaction(Combustion, Fuel, Oxygen, CO2_H2O_Energy).",
                "Process(Photosynthesis, CO2, H2O, Light, Glucose_O2).",
                "Equation(IdealGas, PV=nRT, P_V_n_R_T).",
                "Catalyzes(Enzyme, Substrate, Product).",
                "Yields(Reaction, Reactants, Products)."
            ],
            "Biology": [
                "Process(ProteinSynthesis, DNA, RNA, Protein).",
                "Pathway(Glycolysis, Glucose, ATP, Pyruvate).",
                "System(Circulatory, Heart, Arteries, Veins, Capillaries).",
                "Function(Enzyme, Substrate, Product).",
                "Regulates(Gene, Expression, Protein).",
                "Transcribes(RNA_Polymerase, DNA, RNA)."
            ],
            "Economics": [
                "Formula(GDP, C+I+G+X-M, Components).",
                "Equation(SupplyDemand, Qs=Qd, Equilibrium).",
                "Function(Utility, Consumption, Satisfaction).",
                "Model(IS_LM, Interest, Output).",
                "Determines(Supply, Demand, Price).",
                "Influences(Policy, Economy, Growth)."
            ],
            "Computer_Science": [
                "Algorithm(QuickSort, Array, Pivot, Sorted).",
                "Complexity(BubbleSort, O_n2, Time).",
                "DataStructure(BinaryTree, Node, Children).",
                "Protocol(TCP_IP, Network, Packets).",
                "Implements(Class, Interface, Methods).",
                "Optimizes(Algorithm, Performance, Resources)."
            ],
            "Physics": [
                "Formula(KineticEnergy, Half_m_v2, Energy).",
                "Law(Conservation, Energy, System).",
                "Principle(Uncertainty, DeltaX_DeltaP, Quantum).",
                "Field(Electromagnetic, E_and_B, Maxwell).",
                "Describes(Equation, Phenomenon, Behavior).",
                "Governs(Law, System, Dynamics)."
            ]
        }
        
        if domain in domain_formulas:
            facts.extend(domain_formulas[domain])
        
        return facts

# --- ADVANCED GROWTH ENGINE ---
class AdvancedGrowthEngine:
    """Hauptengine mit dynamischer Themenentdeckung und komplexen Fakten"""
    
    def __init__(self):
        self.api_base = API_BASE_URL
        self.db_path = DB_PATH
        self.topic_discovery = DynamicTopicDiscovery(DB_PATH)
        self.fact_generator = ComplexFactGenerator()
        self.session_stats = {
            'topics_explored': set(),
            'facts_added': 0,
            'complex_facts': 0,
            'formulas_added': 0,
            'new_domains': set(),
            'failed_validations': 0
        }
        
    def call_api(self, endpoint: str, method: str = 'POST', data: dict = None) -> dict:
        """API Call Helper"""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        try:
            response = requests.request(
                method, 
                f"{self.api_base}{endpoint}",
                headers=headers,
                json=data,
                timeout=60
            )
            return response.json() if response.status_code < 400 else {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def add_fact(self, fact: str) -> bool:
        """Füge Fakt zur KB hinzu mit erweiterter Validierung"""
        # Verwende erweiterte Validierung
        if not validate_complex_fact(fact):
            print(f"  ❌ Invalid format: {fact[:60]}...")
            self.session_stats['failed_validations'] += 1
            return False
        
        # Erkenne Fact-Typ
        if any(p in fact for p in ['Formula', 'Equation', 'System', 'Process']):
            self.session_stats['complex_facts'] += 1
        if 'Formula' in fact or 'Equation' in fact:
            self.session_stats['formulas_added'] += 1
        
        # Add via API
        result = self.call_api("/facts", data={"statement": fact})
        
        if result.get('success') or 'exists' in str(result.get('message', '')).lower():
            if result.get('success'):
                self.session_stats['facts_added'] += 1
                print(f"  ✅ Added: {fact[:60]}...")
            return True
        else:
            print(f"  ⚠️ API rejected: {fact[:40]}... - {result.get('error', 'Unknown')}")
            return False
    
    def explore_dynamic_topic(self, topic_info: Dict) -> int:
        """Exploriere ein dynamisch entdecktes Topic"""
        print(f"\n🔍 Exploring: {topic_info['name']}")
        print(f"   Type: {topic_info['type']}")
        
        facts_added = 0
        
        # Generiere Prompt
        if topic_info['type'] == 'cluster_expansion':
            prompt = f"Expand knowledge about {topic_info['focus']} with related concepts."
        elif topic_info['type'] == 'gap_filling':
            prompt = f"Fill knowledge gap about {topic_info['focus']} with comprehensive facts."
        else:
            prompt = f"Explore connections: {topic_info['focus']}"
        
        # Call LLM
        response = self.call_api("/llm/get-explanation", data={
            "topic": topic_info['focus'],
            "context_facts": topic_info.get('related', [])[:3]
        })
        
        if response.get('suggested_facts'):
            for fact in response['suggested_facts'][:10]:
                if self.add_fact(fact):
                    facts_added += 1
        
        # Zusätzlich: Generiere komplexe Fakten wenn passend
        if 'Mathematical' in topic_info.get('name', '') or 'Formula' in topic_info.get('name', ''):
            for formula in self.fact_generator.generate_mathematical_facts()[:5]:
                if self.add_fact(formula):
                    facts_added += 1
        
        # Generiere Relations wenn Entities vorhanden
        if topic_info.get('related'):
            for relation in self.fact_generator.generate_complex_relations(topic_info['related'])[:3]:
                if self.add_fact(relation):
                    facts_added += 1
        
        self.session_stats['topics_explored'].add(topic_info['name'])
        
        return facts_added
    
    def run_adaptive_growth(self, cycles: int = 10):
        """Hauptloop mit adaptivem Lernen"""
        print("=" * 80)
        print("HAK-GAL ADVANCED ADAPTIVE GROWTH ENGINE - FIXED VERSION")
        print("=" * 80)
        print("Features:")
        print("  • Dynamic topic discovery")
        print("  • Complex facts (1-10 arguments)")
        print("  • Mathematical formulas")
        print("  • Cross-domain mining")
        print("=" * 80)
        
        # Initial Analysis
        print("\n📊 Analyzing Knowledge Base...")
        kb_analysis = self.topic_discovery.analyze_knowledge_base()
        
        print(f"  Facts: {kb_analysis.get('total_facts', 0)}")
        print(f"  Entities: {len(kb_analysis.get('entities', []))}")
        print(f"  Predicates: {len(kb_analysis.get('predicates', {}))}")
        
        # Generiere Topics
        dynamic_topics = self.topic_discovery.generate_exploration_topics(kb_analysis)
        
        # Seed mit Formeln
        print("\n📐 Adding Mathematical Foundations...")
        for fact in self.fact_generator.generate_mathematical_facts()[:10]:
            self.add_fact(fact)
        
        # Hauptloop
        for cycle in range(1, cycles + 1):
            print(f"\n{'='*60}")
            print(f"CYCLE {cycle}/{cycles}")
            print(f"{'='*60}")
            
            if cycle % 3 == 1 and dynamic_topics:
                # Dynamic Topic
                topic = dynamic_topics.pop(0)
                facts_added = self.explore_dynamic_topic(topic)
                
            elif cycle % 3 == 2:
                # Domain Formulas
                domain = random.choice(["Chemistry", "Biology", "Physics", "Computer_Science", "Economics"])
                print(f"\n📚 Adding {domain} formulas...")
                facts_added = 0
                for fact in self.fact_generator.generate_domain_formulas(domain)[:5]:
                    if self.add_fact(fact):
                        facts_added += 1
                
            else:
                # Re-analyze
                print("\n🔄 Re-analyzing...")
                kb_analysis = self.topic_discovery.analyze_knowledge_base()
                new_topics = self.topic_discovery.generate_exploration_topics(kb_analysis)
                if new_topics:
                    dynamic_topics.extend(new_topics[:1])
                facts_added = 0
            
            print(f"\n📈 Cycle Result: +{facts_added} facts")
            time.sleep(1)
        
        # Report
        print("\n" + "=" * 80)
        print("GROWTH COMPLETE - REPORT")
        print("=" * 80)
        print(f"  Added: {self.session_stats['facts_added']} facts")
        print(f"  Complex: {self.session_stats['complex_facts']} facts")
        print(f"  Formulas: {self.session_stats['formulas_added']}")
        print(f"  Topics: {len(self.session_stats['topics_explored'])}")
        print(f"  Failed validations: {self.session_stats['failed_validations']}")
        print("=" * 80)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='HAK-GAL Advanced Growth')
    parser.add_argument('--cycles', type=int, default=10)
    parser.add_argument('--analyze-only', action='store_true')
    
    args = parser.parse_args()
    
    engine = AdvancedGrowthEngine()
    
    if args.analyze_only:
        analysis = engine.topic_discovery.analyze_knowledge_base()
        print(f"\n📊 Analysis:")
        print(f"  Facts: {analysis.get('total_facts', 0)}")
        print(f"  Entities: {len(analysis.get('entities', []))}")
        print(f"  Clusters: {len(analysis.get('clusters', []))}")
    else:
        engine.run_adaptive_growth(cycles=args.cycles)

if __name__ == "__main__":
    main()
