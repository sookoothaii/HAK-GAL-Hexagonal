#!/usr/bin/env python3
"""
v6_autopilot with EKR Integration - MAIN DATABASE VERSION
Generates contextually relevant facts based on existing knowledge base entities
"""

import json
import random
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import the EKR components
from ekr_implementation import EKRParser, EKRDatabase, FactType
from ekr_fact_generator import EKRFactGenerator

class EKREnhancedAutopilot:
    """Enhanced autopilot storing contextually relevant facts in main hexagonal database"""
    
    def __init__(self, db_path: str = None):
        # DEFAULT TO MAIN DATABASE
        if db_path is None:
            db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        
        print(f"📁 Using database: {db_path}")
        
        # Initialize database with main path
        self.db = EKRDatabase(db_path)
        self.parser = EKRParser()
        self.generator = EKRFactGenerator()
        
        # Knowledge Base Context - Major entities and themes from existing data
        self.knowledge_domains = {
            'hak_gal_system': [
                'HAK_GAL', 'HAK_GAL_Backend', 'HAK_GAL_Frontend', 'HAK_GAL_API', 
                'AethelredEngine', 'Hexagonal', 'KnowledgeBase'
            ],
            'machine_learning': [
                'MachineLearning', 'NeuralNetworks', 'ArtificialIntelligence', 
                'Algorithm', 'CPU', 'Networks'
            ],
            'philosophy': [
                'ImmanuelKant', 'Socrates', 'Plato', 'CategoricalImperative', 
                'Ethics', 'Philosopher', 'Epistemology', 'KantPhilosophy'
            ],
            'history': [
                'FrenchRevolution', 'ByzantineEmpire', 'AncientEgypt', 'SilkRoad',
                'NationalAssembly', 'ReignOfTerror', 'JustinianI', 'Pharaohs'
            ],
            'science': [
                'CRISPR', 'DNA', 'QuantumEntanglement', 'StellarNucleosynthesis',
                'PlateTectonics', 'KrebsCycle', 'HumanBrain', 'Neurotransmitters'
            ],
            'architecture': [
                'GothicCathedrals', 'StainedGlass', 'PointedArches', 
                'FlyingButtresses', 'RibbedVaults'
            ],
            'economics': [
                'KeynesianEconomics', 'CounterCyclicalPolicies', 'MultiplierEffect',
                'FinancialCrisis', 'Socialism'
            ],
            'biology': [
                'Synapses', 'Plasticity', 'Pruning', 'Nucleotides', 
                'SyntheticBiology', 'Biotechnology'
            ]
        }
        
        # Common predicates from existing data
        self.common_predicates = [
            'HasProperty', 'HasPart', 'HasPurpose', 'Causes', 'IsDefinedAs',
            'IsSimilarTo', 'IsTypeOf', 'HasLocation', 'ConsistsOf', 'IsA',
            'WasDevelopedBy', 'Uses', 'StudiedBy', 'Requires', 'Enables',
            'Creates', 'DependsOn', 'IsPartOf', 'HasExample'
        ]
        
        # Statistics tracking
        self.stats = {
            'total_facts': 0,
            'binary_facts': 0,
            'nary_facts': 0,
            'typed_facts': 0,
            'formula_facts': 0,
            'temporal_facts': 0,
            'graph_facts': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        # Verify database is working
        self._check_database()
    
    def _check_database(self):
        """Verify database is properly initialized"""
        try:
            # Check both old and new tables
            count_old = 0
            count_new = 0
            
            # Check original facts table if exists
            try:
                count_old = self.db.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
                print(f"📊 Original facts table: {count_old} facts")
            except:
                pass
            
            # Check new facts_v2 table
            try:
                count_new = self.db.conn.execute("SELECT COUNT(*) FROM facts_v2").fetchone()[0]
                print(f"📊 Extended facts table: {count_new} facts")
            except sqlite3.OperationalError:
                print("🔧 Creating extended tables in main database...")
                self.db._init_schema()
                count_new = 0
                print("✅ Extended tables created")
            
            print(f"📊 Total facts in database: {count_old + count_new}")
            
        except Exception as e:
            print(f"⚠️ Database check error: {e}")
    
    def generate_contextual_binary_facts(self, count: int) -> List[str]:
        """Generate binary facts using real entities from the knowledge base"""
        facts = []
        
        for _ in range(count):
            # Choose a domain
            domain = random.choice(list(self.knowledge_domains.keys()))
            entities = self.knowledge_domains[domain]
            predicate = random.choice(self.common_predicates)
            
            if domain == 'hak_gal_system':
                templates = [
                    f"HasProperty(HAK_GAL, {random.choice(['Scalable', 'Modular', 'Extensible', 'Robust', 'Efficient'])})",
                    f"HasPart(HAK_GAL_Backend, {random.choice(['APILayer', 'DatabaseConnector', 'LLMAdapter', 'WebSocketHandler'])})",
                    f"Uses(AethelredEngine, {random.choice(['MachineLearning', 'NeuralNetworks', 'Algorithm'])})",
                    f"Enables(Hexagonal, {random.choice(['Modularity', 'Testability', 'Maintainability'])})",
                    f"HasPurpose(KnowledgeBase, {random.choice(['FactStorage', 'KnowledgeRetrieval', 'SemanticSearch'])})"
                ]
                
            elif domain == 'philosophy':
                templates = [
                    f"WasDevelopedBy(CategoricalImperative, ImmanuelKant)",
                    f"StudiedBy({random.choice(['Ethics', 'Epistemology', 'Metaphysics'])}, {random.choice(['ImmanuelKant', 'Socrates', 'Plato'])})",
                    f"HasProperty(Socrates, {random.choice(['Wise', 'Questioning', 'Rational', 'Ethical'])})",
                    f"IsDefinedAs(CategoricalImperative, {random.choice(['MoralLaw', 'UniversalPrinciple', 'EthicalMaxim'])})",
                    f"Causes(SocraticMethod, {random.choice(['CriticalThinking', 'SelfExamination', 'WisdomSeeking'])})"
                ]
                
            elif domain == 'science':
                templates = [
                    f"HasProperty(CRISPR, {random.choice(['Precise', 'Programmable', 'Efficient', 'Versatile'])})",
                    f"HasPart(DNA, {random.choice(['Nucleotides', 'BasePairs', 'DoubleHelix', 'GeneticCode'])})",
                    f"Causes(QuantumEntanglement, {random.choice(['NonLocality', 'Correlation', 'Superposition'])})",
                    f"IsPartOf(KrebsCycle, {random.choice(['CellularRespiration', 'Metabolism', 'EnergyProduction'])})",
                    f"HasPurpose(Neurotransmitters, {random.choice(['SignalTransmission', 'SynapticCommunication', 'NeuralFunction'])})"
                ]
                
            elif domain == 'history':
                templates = [
                    f"HasPart(FrenchRevolution, {random.choice(['ReignOfTerror', 'StormingOfTheBastille', 'EstatesGeneral'])})",
                    f"HasLocation(ByzantineEmpire, {random.choice(['Constantinople', 'Anatolia', 'Balkans'])})",
                    f"WasDevelopedBy(SilkRoad, {random.choice(['ChineseDynasties', 'PersianEmpire', 'RomanEmpire'])})",
                    f"HasProperty(AncientEgypt, {random.choice(['Monumental', 'Hierarchical', 'Agricultural', 'Religious'])})",
                    f"Causes(NationalAssembly, {random.choice(['PoliticalReform', 'SocialChange', 'ConstitutionalMonarchy'])})"
                ]
                
            elif domain == 'architecture':
                templates = [
                    f"HasProperty(GothicCathedrals, {random.choice(['Vertical', 'Luminous', 'Ornate', 'Spiritual'])})",
                    f"HasPart(GothicCathedrals, {random.choice(['PointedArches', 'FlyingButtresses', 'RibbedVaults', 'StainedGlass'])})",
                    f"Enables(FlyingButtresses, {random.choice(['StructuralSupport', 'HeightIncrease', 'WallThinning'])})",
                    f"HasPurpose(StainedGlass, {random.choice(['LightFiltering', 'ReligiousInstruction', 'ArtisticExpression'])})"
                ]
                
            elif domain == 'machine_learning':
                templates = [
                    f"HasProperty(NeuralNetworks, {random.choice(['Adaptive', 'Parallel', 'Distributed', 'Learning'])})",
                    f"Uses(MachineLearning, {random.choice(['Algorithm', 'Statistics', 'DataAnalysis'])})",
                    f"Requires(ArtificialIntelligence, {random.choice(['ComputationalPower', 'DataSets', 'Algorithm'])})",
                    f"Enables(Algorithm, {random.choice(['ProblemSolving', 'Optimization', 'PatternRecognition'])})"
                ]
                
            elif domain == 'economics':
                templates = [
                    f"HasProperty(KeynesianEconomics, {random.choice(['Interventionist', 'DemandFocused', 'CounterCyclical'])})",
                    f"Causes(FinancialCrisis, {random.choice(['EconomicRecession', 'UnemploymentRise', 'MarketVolatility'])})",
                    f"IsDefinedAs(MultiplierEffect, {random.choice(['EconomicAmplification', 'SpendingImpact', 'FiscalMultiplier'])})",
                    f"Uses(CounterCyclicalPolicies, {random.choice(['GovernmentSpending', 'MonetaryPolicy', 'FiscalStimulus'])})"
                ]
                
            else:  # biology
                templates = [
                    f"HasProperty(Synapses, {random.choice(['Plastic', 'Adaptive', 'ElectrochemicallyActive'])})",
                    f"Causes(Plasticity, {random.choice(['LearningAdaptation', 'MemoryFormation', 'NeuralReorganization'])})",
                    f"HasPart(SyntheticBiology, {random.choice(['BiologicalEngineering', 'GeneticModification', 'ProteinDesign'])})",
                    f"Uses(Biotechnology, {random.choice(['GeneticEngineering', 'Fermentation', 'CellCulture'])})"
                ]
            
            fact = random.choice(templates) + "."
            facts.append(fact)
        
        return facts
    
    def generate_contextual_complex_facts(self, count: int) -> List[str]:
        """Generate complex n-ary and temporal facts"""
        facts = []
        
        for _ in range(count):
            fact_type = random.choice(['nary', 'temporal', 'typed'])
            
            if fact_type == 'nary':
                # N-ary relationships with real entities
                templates = [
                    f"TransformedBy(FrenchRevolution, NationalAssembly, EstatesGeneral, PoliticalReform).",
                    f"ConsistsOf(HAK_GAL_Backend, LLMAdapter, DatabaseConnector, APILayer).",
                    f"ProcessedBy(DNA, CRISPR, GeneticModification, PreciseEditing).",
                    f"InfluencedBy(GothicCathedrals, RomanArchitecture, ByzantineArt, IslamicPatterns).",
                    f"ConnectsRegions(SilkRoad, China, Persia, Europe, CentralAsia).",
                    f"ComposedOf(NeuralNetworks, InputLayer, HiddenLayer, OutputLayer, ActivationFunction)."
                ]
                
            elif fact_type == 'temporal':
                # Temporal facts with real historical/process data
                templates = [
                    f"OccurredDuring(FrenchRevolution, Period(1789, 1799)).",
                    f"DevelopedIn(CRISPR, Period(2012, 2020)).",
                    f"FlourishedDuring(ByzantineEmpire, Period(330, 1453)).",
                    f"EvolveDuring(HumanBrain, Period(ChildhoodYears, AdultYears)).",
                    f"ActiveDuring(SilkRoad, Period(130BCE, 1453CE)).",
                    f"ImplementedIn(HAK_GAL, Period(2024, 2025))."
                ]
                
            else:  # typed facts
                # Typed arguments with proper types
                templates = [
                    f"HasMeasurement(GothicCathedrals:Architecture, Height:Meters, 100).",
                    f"ProcessesData(HAK_GAL_Backend:System, Facts:DataType, 6300).",
                    f"ContainsElements(DNA:Molecule, Nucleotides:Count, 4).",
                    f"SpansRegion(SilkRoad:TradeRoute, Distance:Kilometers, 6400).",
                    f"RequiresMemory(NeuralNetworks:Model, VRAM:Gigabytes, 16).",
                    f"HasParameters(AethelredEngine:AIModel, Count:Number, 600000)."
                ]
            
            fact = random.choice(templates)
            facts.append(fact)
        
        return facts
    
    def generate_batch(self, complexity_distribution: Dict[str, float] = None) -> List[str]:
        """Generate a batch of contextually relevant facts"""
        if complexity_distribution is None:
            # Distribution focusing on quality contextual facts
            complexity_distribution = {
                'binary': 0.6,      # 60% contextual binary facts
                'complex': 0.4      # 40% complex n-ary/temporal facts
            }
        
        batch_size = 15  # Increased batch size for better variety
        facts = []
        
        # Generate contextual binary facts
        binary_count = int(batch_size * complexity_distribution.get('binary', 0.6))
        facts.extend(self.generate_contextual_binary_facts(binary_count))
        
        # Generate complex facts
        complex_count = int(batch_size * complexity_distribution.get('complex', 0.4))
        facts.extend(self.generate_contextual_complex_facts(complex_count))
        
        # Shuffle for variety
        random.shuffle(facts)
        
        return facts[:batch_size]  # Ensure exact batch size
    
    def store_facts(self, facts: List[str]) -> Dict[str, int]:
        """Store facts in main database"""
        results = {
            'stored': 0,
            'stored_simple': 0,
            'stored_complex': 0,
            'duplicates': 0,
            'errors': 0
        }
        
        for fact in facts:
            try:
                # Parse to determine type
                parsed = self.parser.parse(fact)
                
                # Check if already exists in facts_v2
                existing = self.db.conn.execute(
                    "SELECT id FROM facts_v2 WHERE statement = ?", 
                    (fact,)
                ).fetchone()
                
                if existing:
                    results['duplicates'] += 1
                else:
                    # Store in extended table
                    fact_id = self.db.add_fact(statement=fact, source="v6_autopilot_contextual")
                    
                    if fact_id:
                        results['stored'] += 1
                        
                        # Track simple vs complex
                        if parsed.fact_type == FactType.BINARY:
                            results['stored_simple'] += 1
                            
                            # ALSO store simple facts in original table for compatibility
                            try:
                                self.db.conn.execute("""
                                    INSERT OR IGNORE INTO facts (statement, confidence, source)
                                    VALUES (?, 1.0, 'v6_autopilot_contextual')
                                """, (fact,))
                                self.db.conn.commit()
                            except:
                                pass  # Original table might not exist
                        else:
                            results['stored_complex'] += 1
                        
                        self.update_stats(parsed.fact_type.value)
                        
            except Exception as e:
                results['errors'] += 1
                self.stats['errors'] += 1
                # Only show first 60 chars of error
                error_msg = str(e)[:60]
                if 'no such table' not in error_msg:  # Don't spam table errors
                    print(f"  ⚠️ Error: {error_msg}")
        
        return results
    
    def update_stats(self, fact_type: str):
        """Update statistics for fact type"""
        self.stats['total_facts'] += 1
        
        stats_map = {
            'binary': 'binary_facts',
            'nary': 'nary_facts',
            'typed': 'typed_facts',
            'formula': 'formula_facts',
            'temporal': 'temporal_facts',
            'graph': 'graph_facts'
        }
        
        if fact_type in stats_map:
            self.stats[stats_map[fact_type]] += 1
    
    def run_cycle(self):
        """Run one generation cycle"""
        print(f"\n🔄 Generation Cycle at {datetime.now().strftime('%H:%M:%S')}")
        
        # Generate contextual facts
        facts = self.generate_batch()
        print(f"  📝 Generated {len(facts)} contextual facts")
        
        # Store facts
        results = self.store_facts(facts)
        print(f"  ✅ Stored: {results['stored']} (Simple: {results['stored_simple']}, Complex: {results['stored_complex']})")
        
        if results['duplicates'] > 0:
            print(f"  ⚠️  Duplicates: {results['duplicates']}")
        
        if results['errors'] > 0:
            print(f"  ❌ Errors: {results['errors']}")
        
        # Show sample of successfully stored facts
        if results['stored'] > 0:
            print("  📋 Sample contextual facts generated:")
            shown = 0
            for fact in facts:
                if shown >= 3:
                    break
                # Verify it was stored
                exists = self.db.conn.execute(
                    "SELECT id FROM facts_v2 WHERE statement = ?", 
                    (fact,)
                ).fetchone()
                if exists:
                    if len(fact) > 70:
                        print(f"     • {fact[:70]}...")
                    else:
                        print(f"     • {fact}")
                    shown += 1
        
        return results
    
    def show_statistics(self):
        """Display current statistics"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print("\n" + "="*70)
        print("📊 EKR Contextual Autopilot Final Statistics")
        print("="*70)
        print(f"Runtime: {runtime:.0f} seconds")
        print(f"Total Contextual Facts Generated: {self.stats['total_facts']}")
        
        if self.stats['total_facts'] > 0:
            print("\n📈 Complexity Distribution (Generated):")
            for fact_type in ['binary', 'nary', 'typed', 'formula', 'temporal', 'graph']:
                key = f"{fact_type}_facts"
                count = self.stats.get(key, 0)
                if count > 0:
                    percentage = (count / self.stats['total_facts'] * 100)
                    print(f"  • {fact_type.title():10s}: {count:3d} ({percentage:.1f}%)")
        
        if self.stats['errors'] > 0:
            print(f"\n⚠️  Total Errors: {self.stats['errors']}")
        
        # Database statistics
        try:
            print("\n💾 Main Database Statistics:")
            
            # Count in original facts table
            try:
                count_old = self.db.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
                print(f"  Original facts table: {count_old} facts")
            except:
                count_old = 0
            
            # Count in extended facts_v2 table
            count_new = self.db.conn.execute("SELECT COUNT(*) FROM facts_v2").fetchone()[0]
            print(f"  Extended facts table: {count_new} facts")
            print(f"  📊 Total: {count_old + count_new} facts")
            
            # Show breakdown by type in facts_v2
            if count_new > 0:
                print("\n📈 Database Breakdown by Type (facts_v2):")
                for fact_type in ['binary', 'nary', 'typed', 'formula', 'temporal', 'graph']:
                    count = self.db.conn.execute(
                        "SELECT COUNT(*) FROM facts_v2 WHERE fact_type = ?", 
                        (fact_type,)
                    ).fetchone()[0]
                    if count > 0:
                        percentage = (count / count_new * 100)
                        print(f"   - {fact_type:10s}: {count:4d} ({percentage:.1f}%)")
            
        except Exception as e:
            print(f"⚠️  Could not retrieve database statistics: {e}")
        
        # Performance metrics
        if runtime > 0 and self.stats['total_facts'] > 0:
            print(f"\n⚡ Performance:")
            print(f"   Facts/second: {self.stats['total_facts']/runtime:.2f}")
            total_attempted = self.stats['total_facts'] + self.stats['errors']
            if total_attempted > 0:
                print(f"   Success rate: {(self.stats['total_facts']/total_attempted)*100:.1f}%")
    
    def show_sample_facts(self, count: int = 3):
        """Show sample facts from database"""
        print(f"\n📚 Sample Contextual Facts from Main Database:")
        
        # Show recent contextual facts
        try:
            recent_facts = self.db.conn.execute("""
                SELECT statement FROM facts_v2 
                WHERE source = 'v6_autopilot_contextual' 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (count * 2,)).fetchall()
            
            if recent_facts:
                print("\n🆕 Recently Generated Contextual Facts:")
                for i, (statement,) in enumerate(recent_facts[:count]):
                    if len(statement) > 80:
                        print(f"  • {statement[:80]}...")
                    else:
                        print(f"  • {statement}")
            
        except Exception as e:
            print(f"  Could not retrieve sample facts: {e}")
        
        # Show complex facts by type
        for fact_type in [FactType.NARY, FactType.TEMPORAL, FactType.TYPED]:
            facts = self.db.query_by_type(fact_type)
            if facts:
                print(f"\n{fact_type.value.title()} Facts:")
                for fact in facts[:2]:  # Show 2 per type
                    statement = fact['statement']
                    if len(statement) > 80:
                        print(f"  • {statement[:80]}...")
                    else:
                        print(f"  • {statement}")
    
    def run(self, cycles: int = 10, delay: float = 5.0):
        """Run the contextual autopilot for specified cycles"""
        print("🚀 Starting EKR Contextual Enhanced Autopilot")
        print("🎯 Contextual Knowledge Integration Mode")
        print(f"   Database: hexagonal_kb.db")
        print(f"   Knowledge Domains: {len(self.knowledge_domains)} domains")
        print(f"   Common Predicates: {len(self.common_predicates)} types")
        print(f"   Cycles: {cycles}")
        print(f"   Delay: {delay}s between cycles")
        print("="*70)
        
        try:
            for i in range(cycles):
                print(f"\n[Cycle {i+1}/{cycles}]")
                self.run_cycle()
                
                if i < cycles - 1:
                    time.sleep(delay)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Autopilot stopped by user")
        
        finally:
            self.show_statistics()
            
            # Show some sample contextual facts
            if self.stats['total_facts'] > 0:
                self.show_sample_facts(3)
            
            # Close database connection
            self.db.conn.close()
            print("\n✅ EKR Contextual Autopilot session complete!")
            print("💾 All contextual facts stored in: hexagonal_kb.db")
            print("🎯 Facts are now contextually integrated with existing knowledge!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EKR Contextual Enhanced Autopilot - Main DB')
    parser.add_argument('--cycles', type=int, default=10, help='Number of cycles')
    parser.add_argument('--delay', type=float, default=5.0, help='Delay between cycles')
    parser.add_argument('--db', type=str, default=None, 
                       help='Database path (default: hexagonal_kb.db)')
    
    args = parser.parse_args()
    
    # Use main database by default
    db_path = args.db or r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    
    # Initialize and run
    autopilot = EKREnhancedAutopilot(db_path)
    autopilot.run(cycles=args.cycles, delay=args.delay)


if __name__ == "__main__":
    main()
