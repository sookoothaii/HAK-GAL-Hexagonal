#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HAK-GAL Advanced Growth Engine with Dynamic Topic Discovery
===========================================================
- Automatische Entdeckung neuer Themenfelder
- Support für komplexe Fakten mit variabler Argumentanzahl
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

# --- ADVANCED FACT PATTERNS ---
COMPLEX_FACT_PATTERNS = {
    # Variable Argumente (2-5)
    "Formula": r"Formula\(([^,]+),\s*([^,]+)(?:,\s*([^,]+))?(?:,\s*([^,]+))?(?:,\s*([^,]+))?\)\.",
    "Equation": r"Equation\(([^,]+),\s*([^,]+)(?:,\s*([^,]+))?\)\.",
    "Function": r"Function\(([^,]+),\s*([^,]+)(?:,\s*([^,]+))?(?:,\s*([^,]+))?\)\.",
    "Relation": r"Relation\(([^,]+)(?:,\s*[^,]+)*\)\.",
    "Process": r"Process\(([^,]+)(?:,\s*[^,]+)*\)\.",
    "System": r"System\(([^,]+)(?:,\s*[^,]+)*\)\.",
    
    # Standard 2-Argumente
    "Standard": r"[A-Z][A-Za-z0-9_]*\([^,]+,\s*[^,]+\)\."
}

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
            cursor.execute("SELECT statement FROM facts")
            all_facts = [row[0] for row in cursor.fetchall()]
            
            # Analysiere Entities und Predicates
            entities = set()
            predicates = Counter()
            connections = defaultdict(set)
            
            for fact in all_facts:
                # Parse fact
                match = re.match(r'^([A-Za-z0-9_]+)\(([^,)]+)(?:,\s*([^)]+))?\)\.$', fact)
                if match:
                    pred = match.group(1)
                    entity1 = match.group(2).strip()
                    entity2 = match.group(3).strip() if match.group(3) else None
                    
                    predicates[pred] += 1
                    entities.add(entity1)
                    if entity2:
                        entities.add(entity2)
                        connections[entity1].add(entity2)
                        connections[entity2].add(entity1)
            
            # Finde Cluster (stark vernetzte Entities)
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
            return {}
    
    def _find_clusters(self, connections: Dict, entities: Set) -> List[Dict]:
        """Finde Themenclusters basierend auf Vernetzung"""
        clusters = []
        visited = set()
        
        for entity in entities:
            if entity in visited:
                continue
                
            # BFS für zusammenhängende Komponenten
            cluster = set()
            queue = [entity]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                    
                visited.add(current)
                cluster.add(current)
                
                # Füge verbundene Entities hinzu
                for connected in connections.get(current, []):
                    if connected not in visited:
                        queue.append(connected)
            
            if len(cluster) > 3:  # Nur signifikante Cluster
                clusters.append({
                    'entities': list(cluster),
                    'size': len(cluster),
                    'core': entity
                })
        
        return sorted(clusters, key=lambda x: x['size'], reverse=True)[:10]
    
    def _identify_knowledge_gaps(self, predicates: Counter, entities: Set) -> List[str]:
        """Identifiziere Bereiche mit wenig Wissen"""
        gaps = []
        
        # Prädikate mit wenig Verwendung
        rare_predicates = [p for p, count in predicates.items() if count < 5]
        
        # Entities mit wenig Verbindungen
        # (Hier vereinfacht - in Produktion würde man die Verbindungen zählen)
        
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
        
        # 3. Cross-Domain Topics (Verbinde verschiedene Cluster)
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
        self.formula_templates = [
            "Formula({subject}, {equation}, {variables})",
            "Formula({subject}, {equation}, {variables}, {conditions})",
            "Formula({subject}, {equation}, {variables}, {conditions}, {domain})",
            
            "Equation({name}, {left_side}, {right_side})",
            "Equation({name}, {expression}, {solution})",
            
            "Function({name}, {input}, {output})",
            "Function({name}, {input}, {output}, {domain})",
            "Function({name}, {input}, {output}, {domain}, {properties})",
            
            "Process({name}, {input}, {transformation}, {output})",
            "Process({name}, {stage1}, {stage2}, {stage3}, {result})",
            
            "System({name}, {components})",
            "System({name}, {input}, {processing}, {output}, {feedback})",
            
            "Relation({entity1}, {entity2}, {type})",
            "Relation({entity1}, {entity2}, {type}, {strength})",
            "Relation({entity1}, {entity2}, {entity3}, {type}, {context})"
        ]
        
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
            # Verschiedene Darstellungsformen
            facts.append(f"Formula({name}, {equation}, {variables}).")
            facts.append(f"Formula({name}, {equation}, {variables}, {domain}).")
            facts.append(f"UsedIn({name}, {domain}).")
            facts.append(f"HasVariables({name}, {variables}).")
            facts.append(f"Equation({name}, {equation}).")
            
        return facts
    
    def generate_complex_relations(self, entities: List[str]) -> List[str]:
        """Generiere komplexe Relationen zwischen Entities"""
        facts = []
        
        if len(entities) < 3:
            return facts
        
        # 3-stellige Relationen
        for i in range(min(10, len(entities)-2)):
            e1, e2, e3 = random.sample(entities, 3)
            facts.append(f"Mediates({e1}, {e2}, {e3}).")
            facts.append(f"Connects({e1}, {e2}, Through_{e3}).")
        
        # 4-stellige Relationen
        if len(entities) >= 4:
            for i in range(min(5, len(entities)-3)):
                e1, e2, e3, e4 = random.sample(entities, 4)
                facts.append(f"Process({e1}, {e2}, {e3}, {e4}).")
                facts.append(f"Transform({e1}, {e2}, {e3}, ResultsIn_{e4}).")
        
        # 5-stellige Relationen (System-Beschreibungen)
        if len(entities) >= 5:
            for i in range(min(3, len(entities)-4)):
                es = random.sample(entities, 5)
                facts.append(f"System({es[0]}, {es[1]}, {es[2]}, {es[3]}, {es[4]}).")
        
        return facts
    
    def generate_domain_formulas(self, domain: str) -> List[str]:
        """Generiere domänenspezifische Formeln"""
        facts = []
        
        domain_formulas = {
            "Chemistry": [
                "Formula(WaterFormation, 2H2+O2→2H2O, H2_O2_H2O)",
                "Reaction(Combustion, Fuel, Oxygen, CO2_H2O_Energy)",
                "Process(Photosynthesis, CO2, H2O, Light, Glucose_O2)",
                "Equation(IdealGas, PV=nRT, P_V_n_R_T)"
            ],
            "Biology": [
                "Process(ProteinSynthesis, DNA, Transcription, RNA, Translation, Protein)",
                "Pathway(Glycolysis, Glucose, ATP, Pyruvate, 10_Steps)",
                "System(Circulatory, Heart, Arteries, Veins, Capillaries, Blood)",
                "Function(Enzyme, Substrate, Product, Catalysis)"
            ],
            "Economics": [
                "Formula(GDP, C+I+G+(X-M), Consumption_Investment_Government_NetExports)",
                "Equation(Supply_Demand, Qs=Qd, Equilibrium)",
                "Function(Utility, Consumption, Satisfaction, Diminishing_Returns)",
                "Model(IS_LM, Interest_Rate, Output, Equilibrium)"
            ],
            "Computer_Science": [
                "Algorithm(QuickSort, Array, Pivot, Partition, O(nlogn))",
                "Complexity(BubbleSort, O(n^2), Time, Worst_Case)",
                "DataStructure(BinaryTree, Node, Left_Child, Right_Child, Traversal)",
                "Protocol(TCP_IP, Network, Transport, Packets, Reliability)"
            ],
            "Physics": [
                "Formula(KineticEnergy, ½mv², m_v, Classical)",
                "Law(Conservation, Energy, Closed_System, Constant)",
                "Principle(Uncertainty, Δx·Δp≥ℏ/2, Position_Momentum, Quantum)",
                "Field(Electromagnetic, E, B, Maxwell, Waves)"
            ]
        }
        
        if domain in domain_formulas:
            facts.extend(domain_formulas[domain])
        
        # Generiere zusätzliche Variationen
        for fact in facts[:]:
            # Extrahiere Komponenten für Querverbindungen
            match = re.match(r'^(\w+)\(([^)]+)\)\.$', fact[:-1] + '.')
            if match:
                pred = match.group(1)
                args = match.group(2).split(', ')
                if len(args) >= 2:
                    facts.append(f"RelatedTo({args[0]}, {args[-1]}).")
                    facts.append(f"PartOf({args[0]}, {domain}).")
        
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
            'new_domains': set()
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
    
    def add_fact(self, fact: str, validate: bool = True) -> bool:
        """Füge Fakt zur KB hinzu (unterstützt komplexe Formate)"""
        if validate:
            # Validiere gegen alle Patterns
            valid = False
            for pattern_name, pattern in COMPLEX_FACT_PATTERNS.items():
                if re.match(pattern, fact):
                    valid = True
                    if pattern_name != "Standard":
                        self.session_stats['complex_facts'] += 1
                    if "Formula" in fact or "Equation" in fact:
                        self.session_stats['formulas_added'] += 1
                    break
            
            if not valid:
                print(f"[AddFact] Invalid format: {fact}")
                return False
        
        # Add via API
        result = self.call_api("/facts", data={"statement": fact})
        
        if result.get('success') or 'exists' in str(result.get('message', '')).lower():
            if result.get('success'):
                self.session_stats['facts_added'] += 1
                print(f"  ✅ Added: {fact[:80]}...")
            return True
        return False
    
    def explore_dynamic_topic(self, topic_info: Dict) -> int:
        """Exploriere ein dynamisch entdecktes Topic"""
        print(f"\n🔍 Exploring Dynamic Topic: {topic_info['name']}")
        print(f"   Type: {topic_info['type']}")
        print(f"   Focus: {topic_info['focus']}")
        
        facts_added = 0
        
        # Generiere Prompt basierend auf Topic-Typ
        if topic_info['type'] == 'cluster_expansion':
            prompt = f"""
            Expand knowledge about {topic_info['focus']} and its relationships.
            Related entities: {', '.join(topic_info['related'][:5])}
            
            Generate facts about:
            1. Deep properties and characteristics
            2. Complex relationships (use 3-4 arguments)
            3. Mathematical formulas if applicable
            4. Processes and systems involving this topic
            """
        
        elif topic_info['type'] == 'gap_filling':
            prompt = f"""
            Fill knowledge gap about {topic_info['focus']}.
            This is an underrepresented area in our knowledge base.
            
            Generate comprehensive facts including:
            1. Basic definitions and properties
            2. Key formulas and equations (use Formula() predicate)
            3. Important relationships and processes
            4. System descriptions (use System() with multiple arguments)
            """
        
        elif topic_info['type'] == 'cross_domain':
            prompt = f"""
            Explore connections: {topic_info['focus']}
            Bridge entities: {', '.join(topic_info['related'])}
            
            Generate facts that:
            1. Connect different domains
            2. Show interdependencies (use Mediates(), Connects() with 3+ arguments)
            3. Describe transformation processes
            4. Create system-level understanding
            """
        
        else:
            prompt = f"Explore topic: {topic_info['focus']}"
        
        # Call LLM
        response = self.call_api("/llm/get-explanation", data={
            "topic": topic_info['focus'],
            "context_facts": topic_info.get('related', [])
        })
        
        if response.get('suggested_facts'):
            for fact in response['suggested_facts']:
                if self.add_fact(fact):
                    facts_added += 1
        
        # Zusätzlich: Generiere komplexe Fakten
        if topic_info['type'] == 'gap_filling' and 'Mathematical' in topic_info['name']:
            print("   📐 Adding mathematical formulas...")
            for formula in self.fact_generator.generate_mathematical_facts()[:10]:
                if self.add_fact(formula):
                    facts_added += 1
        
        # Generiere Cross-Domain Relations
        if topic_info.get('related'):
            print("   🔗 Creating complex relations...")
            for relation in self.fact_generator.generate_complex_relations(topic_info['related'])[:5]:
                if self.add_fact(relation):
                    facts_added += 1
        
        self.session_stats['topics_explored'].add(topic_info['name'])
        if topic_info['type'] == 'gap_filling':
            self.session_stats['new_domains'].add(topic_info['name'])
        
        return facts_added
    
    def run_adaptive_growth(self, cycles: int = 10):
        """Hauptloop mit adaptivem Lernen"""
        print("=" * 80)
        print("HAK-GAL ADVANCED ADAPTIVE GROWTH ENGINE")
        print("=" * 80)
        print(f"Features:")
        print(f"  • Dynamic topic discovery")
        print(f"  • Complex facts with variable arguments")
        print(f"  • Mathematical formulas and equations")
        print(f"  • Cross-domain knowledge mining")
        print("=" * 80)
        
        # Initial Knowledge Base Analysis
        print("\n📊 Analyzing Knowledge Base...")
        kb_analysis = self.topic_discovery.analyze_knowledge_base()
        
        print(f"  Total Facts: {kb_analysis.get('total_facts', 0)}")
        print(f"  Unique Entities: {len(kb_analysis.get('entities', []))}")
        print(f"  Predicate Types: {len(kb_analysis.get('predicates', {}))}")
        print(f"  Topic Clusters: {len(kb_analysis.get('clusters', []))}")
        print(f"  Knowledge Gaps: {len(kb_analysis.get('gaps', []))}")
        
        # Generiere initiale Topics
        dynamic_topics = self.topic_discovery.generate_exploration_topics(kb_analysis)
        
        # Füge mathematische Grundlagen hinzu
        print("\n📐 Seeding Mathematical Foundations...")
        math_facts = self.fact_generator.generate_mathematical_facts()
        for fact in math_facts[:20]:
            self.add_fact(fact)
        
        # Hauptloop
        for cycle in range(1, cycles + 1):
            print(f"\n{'='*60}")
            print(f"CYCLE {cycle}/{cycles}")
            print(f"{'='*60}")
            
            # Wähle Topic-Strategie
            if cycle % 3 == 1 and dynamic_topics:
                # Dynamisches Topic
                topic = dynamic_topics.pop(0)
                facts_added = self.explore_dynamic_topic(topic)
                
            elif cycle % 3 == 2:
                # Domänen-spezifische Formeln
                domain = random.choice([
                    "Chemistry", "Biology", "Economics", 
                    "Computer_Science", "Physics"
                ])
                print(f"\n📚 Adding {domain} formulas...")
                facts_added = 0
                for fact in self.fact_generator.generate_domain_formulas(domain):
                    if self.add_fact(fact):
                        facts_added += 1
                
            else:
                # Re-Analyse und neue Topics
                print("\n🔄 Re-analyzing for new patterns...")
                kb_analysis = self.topic_discovery.analyze_knowledge_base()
                new_topics = self.topic_discovery.generate_exploration_topics(kb_analysis)
                if new_topics:
                    dynamic_topics.extend(new_topics[:2])
                    topic = dynamic_topics.pop(0) if dynamic_topics else None
                    if topic:
                        facts_added = self.explore_dynamic_topic(topic)
                    else:
                        facts_added = 0
                else:
                    facts_added = 0
            
            print(f"\n📈 Cycle Summary: +{facts_added} facts")
            
            # Kurze Pause
            time.sleep(2)
        
        # Final Report
        print("\n" + "=" * 80)
        print("ADVANCED GROWTH COMPLETE - FINAL REPORT")
        print("=" * 80)
        print(f"📊 SESSION STATISTICS:")
        print(f"  Total Facts Added: {self.session_stats['facts_added']}")
        print(f"  Complex Facts: {self.session_stats['complex_facts']}")
        print(f"  Formulas Added: {self.session_stats['formulas_added']}")
        print(f"  Topics Explored: {len(self.session_stats['topics_explored'])}")
        print(f"  New Domains: {', '.join(self.session_stats['new_domains'])}")
        
        # Finale Analyse
        final_analysis = self.topic_discovery.analyze_knowledge_base()
        print(f"\n📈 KNOWLEDGE BASE GROWTH:")
        print(f"  Final Total: {final_analysis.get('total_facts', 0)} facts")
        print(f"  Entities: {len(final_analysis.get('entities', []))}")
        print(f"  Clusters: {len(final_analysis.get('clusters', []))}")
        
        print("\n✨ The knowledge base has evolved beyond its initial boundaries!")
        print("=" * 80)

def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='HAK-GAL Advanced Adaptive Growth Engine'
    )
    parser.add_argument(
        '--cycles', 
        type=int, 
        default=10,
        help='Number of growth cycles (default: 10)'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only analyze KB without adding facts'
    )
    
    args = parser.parse_args()
    
    engine = AdvancedGrowthEngine()
    
    if args.analyze_only:
        print("📊 Knowledge Base Analysis Only Mode")
        analysis = engine.topic_discovery.analyze_knowledge_base()
        
        print(f"\n📈 Current State:")
        print(f"  Facts: {analysis.get('total_facts', 0)}")
        print(f"  Entities: {len(analysis.get('entities', []))}")
        
        print(f"\n🏆 Top Predicates:")
        for pred, count in sorted(
            analysis.get('predicates', {}).items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]:
            print(f"  {pred}: {count}")
        
        print(f"\n🌐 Major Clusters:")
        for cluster in analysis.get('clusters', [])[:5]:
            print(f"  {cluster['core']}: {cluster['size']} entities")
        
        print(f"\n🎯 Knowledge Gaps:")
        for gap in analysis.get('gaps', []):
            print(f"  • {gap}")
    else:
        engine.run_adaptive_growth(cycles=args.cycles)

if __name__ == "__main__":
    main()
