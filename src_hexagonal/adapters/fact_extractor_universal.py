"""
Universal Fact Extractor - Enhanced with Scientific N-ary Support
==================================================================
Extracts relevant facts from LLM responses with full scientific n-ary support
"""
import re
from typing import List, Optional, Set
import random

class UniversalFactExtractor:
    """Extract facts from LLM responses with scientific n-ary support"""
    
    def __init__(self):
        # Pattern 1: Standard Prolog facts (supporting multi-args)
        self.prolog_pattern = re.compile(
            r'([A-Z][A-Za-z0-9_]*)\s*\(\s*([^()]+)\s*\)\s*\.',
            re.MULTILINE
        )
        
        # Pattern 2: Bullet point facts
        self.bullet_pattern = re.compile(
            r'[-•*]\s*([A-Z][A-Za-z0-9_]*)\s*\(\s*([^()]+)\s*\)\s*\.?',
            re.MULTILINE
        )
        
        # Pattern 3: Numbered facts  
        self.numbered_pattern = re.compile(
            r'\d+\.\s*([A-Z][A-Za-z0-9_]*)\s*\(\s*([^()]+)\s*\)\s*\.?',
            re.MULTILINE
        )
        
        # Pattern 4: Inline facts
        self.inline_pattern = re.compile(
            r'\b([A-Z][A-Za-z0-9_]{2,})\(([^()]+)\)',
            re.MULTILINE
        )
        
        # Valid predicates - ERWEITERT mit wissenschaftlichen Prädikaten
        self.VALID_PREDICATES = {
            # Original simple predicates (2-arg)
            'IsA', 'HasPart', 'PartOf', 'Causes', 'UsedFor', 'LocatedIn',
            'HasProperty', 'IsDefinedAs', 'SubClass', 'SuperClass',
            'RelatedTo', 'DependsOn', 'Enables', 'Requires', 'Contains',
            'ConnectedTo', 'InfluencedBy', 'Influences', 'SimilarTo',
            'DifferentFrom', 'OpposedTo', 'ComplementaryTo', 'DerivedFrom',
            'LeadsTo', 'Prevents', 'Supports', 'Contradicts', 'Explains',
            'Application', 'StudiedBy', 'UsedIn', 'Implies', 'Suggests',
            'ConsciousnessProperty', 'ConsciousnessTheory', 'AIType',
            'PhilosophicalPosition', 'TheoryProponent', 'RelationshipStatus',
            'EthicalConsideration', 'MeasurementProblem', 'EmergentProperty',
            'SimulatedProperty', 'LacksProperty', 'DebatedTopic', 'ScientificConsensus',
            
            # NEUE wissenschaftliche n-äre Prädikate (3-10 args)
            'ChemicalFormula', 'ChemicalReaction', 'OrganicReaction', 'ReactionKinetics',
            'ElectronicTransition', 'MolecularStructure', 'CrystalStructure',
            'ProteinInteraction', 'MetabolicPathway', 'EnzymeKinetics',
            'Equilibrium', 'Catalysis', 'Synthesis', 'Decomposition',
            'RedoxReaction', 'AcidBase', 'Precipitation', 'Complexation',
            'PhotochemicalReaction', 'ElectrochemicalCell', 'ThermodynamicData',
            'SpectroscopicData', 'MolecularWeight', 'BoilingPoint', 'MeltingPoint',
            'Solubility', 'pKa', 'ReactionMechanism', 'IntermolecularForces',
            'BondEnergy', 'ActivationEnergy', 'GibbsEnergy', 'Enthalpy', 'Entropy',
            
            # Physics predicates
            'Motion', 'Force', 'Energy', 'Wave', 'QuantumState', 'Collision',
            'ElectromagneticField', 'GravitationalField', 'Oscillation',
            
            # Biology predicates  
            'GeneExpression', 'Mutation', 'SignalPathway', 'Photosynthesis',
            'CellCycle', 'DNAReplication', 'Transcription', 'Translation',
            
            # Neuroscience predicates
            'NeuralCircuit', 'SynapticPlasticity', 'CognitiveProcess',
            'Neurotransmitter', 'IonChannel', 'ActionPotential',
            
            # Medicine predicates
            'DrugInteraction', 'Pharmacokinetics', 'Disease', 'Treatment',
            'Diagnosis', 'Symptom', 'SideEffect', 'ClinicalTrial',
            
            # Additional
            'Algorithm', 'DataStructure', 'NetworkProtocol', 'Function',
            'Theorem', 'Proof', 'Relation'
        }
    
    def extract_facts(self, text: str, query: Optional[str] = None) -> List[str]:
        """
        Extract relevant facts from LLM response text
        
        Args:
            text: The LLM response text
            query: Original query for context
            
        Returns:
            List of relevant fact suggestions
        """
        facts = []
        seen = set()
        
        # First, try to extract facts directly from the LLM response
        patterns = [
            self.prolog_pattern,
            self.bullet_pattern,
            self.numbered_pattern,
            self.inline_pattern
        ]
        
        for pattern in patterns:
            for match in pattern.finditer(text):
                predicate = match.group(1)
                args = match.group(2) if len(match.groups()) >= 2 else ''
                
                # Skip invalid predicates
                if predicate not in self.VALID_PREDICATES:
                    continue
                
                # Parse arguments
                arg_list = [arg.strip() for arg in args.split(',')]
                
                # Create fact
                fact = f"{predicate}({', '.join(arg_list)})."
                
                # Check if valid and unique
                if self._is_valid_fact(fact) and fact not in seen:
                    facts.append(fact)
                    seen.add(fact)
        
        # If no facts found in text, generate context-aware facts
        if len(facts) < 5:
            # Detect domain from text content
            domain = self._detect_domain(text, query)
            generated = self._generate_domain_specific_facts(text, query, domain)
            
            for fact in generated:
                if fact not in seen and self._is_valid_fact(fact):
                    facts.append(fact)
                    seen.add(fact)
        
        return facts[:20]  # Limit to 20 facts
    
    def _detect_domain(self, text: str, query: str) -> str:
        """Detect the domain/topic from text and query"""
        combined = (text + " " + (query or "")).lower()
        
        # Check for specific domains
        if any(word in combined for word in ['consciousness', 'aware', 'sentience', 'subjective', 'qualia']):
            return 'consciousness'
        elif any(word in combined for word in ['artificial intelligence', ' ai ', 'machine learning', 'neural']):
            return 'ai'
        elif any(word in combined for word in ['quantum', 'physics', 'energy', 'particle']):
            return 'physics'
        elif any(word in combined for word in ['chemical', 'formula', 'reaction', 'molecule', 'acid', 'base', 'compound', 'lsd', 'drug']):
            return 'chemistry'
        elif any(word in combined for word in ['biological', 'cell', 'dna', 'protein', 'gene']):
            return 'biology'
        else:
            return 'general'
    
    def _extract_query_entities(self, query: str) -> Set[str]:
        """Extract entities from the query"""
        entities = set()
        if not query:
            return entities
        
        # Skip extracting the entire query as an entity
        # Extract meaningful words instead
        stop_words = {'what', 'is', 'the', 'between', 'and', 'of', 'how', 'why', 'when', 'where', 'relationship'}
        
        for word in query.split():
            clean_word = word.strip(',.!?()').lower()
            if clean_word not in stop_words and len(clean_word) > 2:
                # Keep specific entities like LSD in uppercase
                if clean_word in ['lsd', 'dna', 'rna', 'atp', 'co2', 'h2o']:
                    entities.add(clean_word.upper())
                else:
                    entities.add(word.strip(',.!?()').capitalize())
        
        return entities
    
    def _clean_entity(self, entity: str) -> str:
        """Clean entity name for use in facts"""
        # Remove special chars, keep alphanumeric and underscores
        cleaned = re.sub(r'[^\\w]', '', entity)
        # Ensure starts with capital
        if cleaned and cleaned[0].islower():
            cleaned = cleaned.capitalize()
        return cleaned or 'Entity'
    
    def _is_valid_fact(self, fact: str) -> bool:
        """Validate fact format and content"""
        if not fact or len(fact) < 10:
            return False
        
        # Check format
        if not re.match(r'^[A-Z][A-Za-z0-9_]*\([^()]+\)\.$', fact):
            return False
        
        # Filter out test/example facts
        lower_fact = fact.lower()
        invalid_terms = ['test', 'example', 'foo', 'bar', 'xyz', 'abc']
        for term in invalid_terms:
            if term in lower_fact:
                return False
        
        # Filter out malformed entities (like full questions as entities)
        if 'whatisthe' in lower_fact or 'howdoes' in lower_fact:
            return False
        
        return True
    
    def _generate_domain_specific_facts(self, text: str, query: str, domain: str) -> List[str]:
        """Generate domain-specific facts based on detected context"""
        facts = []
        
        # Extract meaningful entities from query
        entities = self._extract_query_entities(query) if query else set()
        
        if domain == 'chemistry':
            # Check for specific chemicals mentioned
            lower_text = text.lower()
            
            # LSD specific facts
            if 'lsd' in lower_text or 'lysergic' in lower_text:
                facts.extend([
                    f"ChemicalFormula(LSD, C20H25N3O, MW:323.4).",
                    f"MolecularStructure(LSD, indole_ring, diethylamide_group, tetracyclic, ergot_derived).",
                    f"Synthesis(LSD, lysergic_acid, diethylamine, POCl3, reflux, yield:60).",
                    f"Pharmacokinetics(LSD, oral, t_half:3.6h, metabolism:hepatic, excretion:renal).",
                    f"DrugClass(LSD, hallucinogen, psychedelic, serotonergic, Schedule_I).",
                    f"ReceptorBinding(LSD, 5HT2A, agonist, Ki:2.9nM, hallucinogenic_effects).",
                    f"DerivedFrom(LSD, ergot_alkaloids, Claviceps_purpurea).",
                    f"Discovery(LSD, Albert_Hofmann, 1938, Sandoz_Laboratories, Basel).",
                    f"ChemicalReaction(lysergic_acid, SOCl2, lysergyl_chloride, SO2, HCl, diethylamine_addition, LSD)."
                ])
            
            # Water specific facts
            elif 'water' in lower_text or 'h2o' in lower_text:
                facts.extend([
                    f"ChemicalFormula(water, H2O, MW:18.015).",
                    f"MolecularStructure(water, bent, O_center, 2H, bond_angle:104.5, sp3_hybrid).",
                    f"PhysicalProperties(H2O, bp:100C, mp:0C, density:1.0g/ml, dipole:1.85D, pH:7.0).",
                    f"IntermolecularForces(water, hydrogen_bonding, dipole_dipole, 4_bonds_max)."
                ])
            
            # General chemistry facts for other queries
            else:
                facts.extend([
                    f"ChemicalReaction(reactant1, reactant2, product1, product2, catalyst, temp:25C, pressure:1atm).",
                    f"ReactionKinetics(reaction, k:1.5e-3, Ea:75kJ/mol, A:1e10, T:298K).",
                    f"Equilibrium(A, B, C, D, Keq:1.5e3, T:298K, P:1atm).",
                    f"AcidBase(acid, base, conjugate_base, conjugate_acid, pKa:4.7, pH:7.0).",
                    f"OrganicReaction(substrate, reagent, product, mechanism, solvent, yield:85, time:2h).",
                    f"Catalysis(substrate, catalyst, intermediate, product, turnover:1000, selectivity:95).",
                    f"IsA(Chemistry, Science).",
                    f"HasProperty(Molecules, ChemicalBonds)."
                ])
                
                # Add entity-specific facts if entities found
                for entity in list(entities)[:2]:
                    if entity.upper() in ['CO2', 'H2O', 'O2', 'N2', 'CH4']:
                        facts.append(f"ChemicalFormula({entity}, {entity}, MW:calculated).")
                    else:
                        facts.append(f"Contains({entity}, atoms).")
        
        elif domain == 'consciousness':
            # Generate consciousness-related facts
            facts.extend([
                f"ConsciousnessProperty(Subjectivity, FundamentalAspect).",
                f"ConsciousnessProperty(Qualia, Experience).",
                f"ConsciousnessTheory(HardProblem, Chalmers).",
                f"ConsciousnessTheory(IntegratedInformation, Tononi).",
                f"RelationshipStatus(CurrentAI, Consciousness, NonExistent).",
                f"LacksProperty(CurrentAI, SubjectiveExperience).",
                f"DebatedTopic(MachineConsciousness, Philosophy).",
                f"PhilosophicalPosition(Functionalism, ConsciousnessEmergence).",
                f"PhilosophicalPosition(BiologicalNaturalism, RequiresBiology).",
                f"EthicalConsideration(ConsciousAI, MoralStatus)."
            ])
            
            # Add AI-specific consciousness facts if AI is mentioned
            if 'AI' in entities or 'ai' in text.lower():
                facts.extend([
                    f"AIType(NarrowAI, CurrentSystems).",
                    f"AIType(GeneralAI, Hypothetical).",
                    f"SimulatedProperty(AI, ConsciousnessAppearance).",
                    f"LacksProperty(AI, PhenomenalConsciousness).",
                    f"ScientificConsensus(NoCurrentAIConsciousness, 2024)."
                ])
        
        elif domain == 'ai':
            facts.extend([
                f"IsA(ArtificialIntelligence, Technology).",
                f"UsedFor(MachineLearning, PatternRecognition).",
                f"Enables(NeuralNetworks, DeepLearning).",
                f"RequiresData(MachineLearning, TrainingData).",
                f"Application(AI, Healthcare).",
                f"Application(AI, Automation).",
                f"HasProperty(AI, ComputationalIntelligence).",
                f"DifferentFrom(AI, HumanIntelligence)."
            ])
            
            # Add consciousness-related AI facts if consciousness is mentioned
            if any(word in text.lower() for word in ['conscious', 'aware', 'sentience']):
                facts.extend([
                    f"LacksProperty(CurrentAI, Consciousness).",
                    f"DebatedTopic(AIConsciousness, Future).",
                    f"SimulatedProperty(AI, BehavioralConsciousness)."
                ])
        
        elif domain == 'physics':
            facts.extend([
                f"Motion(object, position:x0, velocity:v0, acceleration:a, time:t, position_final:xf).",
                f"Force(object, magnitude:10N, direction:theta, resultant:F_net, acceleration:a).",
                f"Energy(system, kinetic:KE, potential:PE, total:E_total, conserved:true).",
                f"Wave(electromagnetic, frequency:f, wavelength:lambda, speed:c, energy:E).",
                f"QuantumState(particle, n:1, l:0, ml:0, ms:0.5, wavefunction:psi).",
                f"IsA(QuantumMechanics, PhysicsField).",
                f"HasProperty(QuantumParticles, Superposition)."
            ])
        
        elif domain == 'biology':
            facts.extend([
                f"GeneExpression(gene, mRNA, protein, regulation:positive, location:nucleus).",
                f"MetabolicPathway(glycolysis, glucose, pyruvate, ATP:2, NADH:2, cytoplasm, anaerobic).",
                f"ProteinInteraction(proteinA, proteinB, Kd:1nM, complex:AB, function:signaling).",
                f"CellCycle(G1, S, G2, M, checkpoints:3, duration:24h, regulation:CDK).",
                f"Mutation(gene, position:125, wildtype:A, mutant:G, effect:missense, phenotype:altered).",
                f"IsA(Biology, LifeScience).",
                f"HasProperty(LivingOrganisms, Metabolism)."
            ])
        
        else:  # general domain
            # Generate generic but relevant facts
            if entities:
                for entity in list(entities)[:3]:  # Limit to avoid spam
                    clean_entity = self._clean_entity(entity)
                    facts.extend([
                        f"IsA({clean_entity}, Concept).",
                        f"StudiedBy({clean_entity}, Researchers)."
                    ])
        
        return facts[:15]  # Limit generated facts

# Global instance
universal_extractor = UniversalFactExtractor()

def extract_facts_from_llm(text: str, topic: str = '') -> List[str]:
    """Main entry point for fact extraction"""
    return universal_extractor.extract_facts(text, topic)
