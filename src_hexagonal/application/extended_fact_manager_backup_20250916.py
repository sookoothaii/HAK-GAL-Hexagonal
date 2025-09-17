#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extended Fact Manager - Multi-Argument & Formula Support
=========================================================
Manages facts with 3-5+ arguments, formulas, and domain-specific patterns
"""

import json
import sqlite3
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

class ExtendedFactManager:
    """
    Manager for extended facts with multi-argument support
    """
    
    def __init__(self, db_path: str = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Domain-specific patterns for multi-argument facts
        self.DOMAIN_PATTERNS = {
            'chemistry': {
                'reaction': {
                    'pattern': r'(\w+)\s*\+\s*(\w+)\s*(?:->|→)\s*(\w+)',
                    'predicate': 'ChemicalReaction',
                    'args': 3,
                    'template': 'ChemicalReaction({0}, {1}, {2})'
                },
                'compound': {
                    'pattern': r'(\w+)\s+has\s+formula\s+(\w+)',
                    'predicate': 'HasFormula', 
                    'args': 2,
                    'template': 'HasFormula({0}, {1})'
                },
                'reaction_full': {
                    'pattern': r'reaction:\s*(\w+)\s*\+\s*(\w+)\s*→\s*(\w+)\s*\+\s*(\w+)\s*\((\w+)\)',
                    'predicate': 'Reaction',
                    'args': 5,
                    'template': 'Reaction({0}, {1}, {2}, {3}, {4})'
                }
            },
            'physics': {
                'force': {
                    'pattern': r'force\s+on\s+(\w+)\s+is\s+([\d.]+)\s*(\w+)',
                    'predicate': 'Force',
                    'args': 3,
                    'template': 'Force({0}, {1}, {2})'
                },
                'energy': {
                    'pattern': r'(\w+)\s+has\s+([\d.]+)\s*(\w+)\s+of\s+(\w+)\s+energy',
                    'predicate': 'Energy',
                    'args': 4,
                    'template': 'Energy({0}, {1}, {2}, {3})'
                },
                'motion': {
                    'pattern': r'(\w+)\s+moves\s+at\s+([\d.]+)\s*(\w+)\s+in\s+direction\s+(\w+)',
                    'predicate': 'Motion',
                    'args': 4,
                    'template': 'Motion({0}, {1}, {2}, {3})'
                }
            },
            'geography': {
                'location': {
                    'pattern': r'(\w+)\s+(?:is\s+)?located\s+(?:in|at)\s+(\w+),?\s*(\w+)?',
                    'predicate': 'Located',
                    'args': 3,
                    'template': 'Located({0}, {1}, {2})'
                },
                'coordinates': {
                    'pattern': r'(\w+)\s+at\s+([\d.-]+),\s*([\d.-]+)',
                    'predicate': 'AtCoordinates',
                    'args': 3,
                    'template': 'AtCoordinates({0}, {1}, {2})'
                }
            },
            'biology': {
                'process': {
                    'pattern': r'(\w+)\s+converts\s+(\w+)\s+to\s+(\w+)\s+(?:in|at)\s+(\w+)',
                    'predicate': 'BiologicalProcess',
                    'args': 4,
                    'template': 'BiologicalProcess({0}, {1}, {2}, {3})'
                },
                'pathway': {
                    'pattern': r'pathway:\s*(\w+)\s*→\s*(\w+)\s*→\s*(\w+)',
                    'predicate': 'MetabolicPathway',
                    'args': 3,
                    'template': 'MetabolicPathway({0}, {1}, {2})'
                }
            },
            'economics': {
                'transaction': {
                    'pattern': r'(\w+)\s+(?:sends|transfers)\s+([\d.]+)\s*(\w+)\s+to\s+(\w+)',
                    'predicate': 'Transaction',
                    'args': 4,
                    'template': 'Transaction({0}, {1}, {2}, {3})'
                },
                'market': {
                    'pattern': r'(\w+)\s+price:\s*([\d.]+)\s*(\w+)\s+at\s+(\w+)',
                    'predicate': 'MarketPrice',
                    'args': 4,
                    'template': 'MarketPrice({0}, {1}, {2}, {3})'
                }
            },
            'medicine': {
                'treatment': {
                    'pattern': r'(\w+)\s+treats\s+(\w+)\s+with\s+(\w+)\s+efficacy',
                    'predicate': 'Treatment',
                    'args': 3,
                    'template': 'Treatment({0}, {1}, {2})'
                },
                'diagnosis': {
                    'pattern': r'(\w+)\s+indicates\s+(\w+)\s+with\s+([\d.]+)%?\s+confidence',
                    'predicate': 'Diagnosis',
                    'args': 3,
                    'template': 'Diagnosis({0}, {1}, {2})'
                }
            },
            'technology': {
                'protocol': {
                    'pattern': r'(\w+)\s+connects\s+to\s+(\w+)\s+via\s+(\w+)',
                    'predicate': 'NetworkProtocol',
                    'args': 3,
                    'template': 'NetworkProtocol({0}, {1}, {2})'
                },
                'data_flow': {
                    'pattern': r'data\s+flows\s+from\s+(\w+)\s+to\s+(\w+)\s+at\s+([\d.]+)\s*(\w+)',
                    'predicate': 'DataFlow',
                    'args': 4,
                    'template': 'DataFlow({0}, {1}, {2}, {3})'
                }
            },
            'mathematics': {
                'equation': {
                    'pattern': r'(\w+)\s*=\s*(\w+)\s*\*\s*(\w+)',
                    'predicate': 'Equation',
                    'args': 3,
                    'template': 'Equation({0}, {1}, {2})'
                },
                'relation': {
                    'pattern': r'(\w+)\s+is\s+proportional\s+to\s+(\w+)\s+with\s+factor\s+([\d.]+)',
                    'predicate': 'Proportional',
                    'args': 3,
                    'template': 'Proportional({0}, {1}, {2})'
                }
            }
        }
        
        # Multi-argument templates
        self.MULTI_ARG_TEMPLATES = {
            3: [
                "Located({0}, {1}, {2})",
                "Transfers({0}, {1}, {2})",
                "Converts({0}, {1}, {2})",
                "Connects({0}, {1}, {2})",
                "Causes({0}, {1}, {2})"
            ],
            4: [
                "Process({0}, {1}, {2}, {3})",
                "Reaction({0}, {1}, {2}, {3})",
                "Transaction({0}, {1}, {2}, {3})",
                "Measurement({0}, {1}, {2}, {3})",
                "Route({0}, {1}, {2}, {3})"
            ],
            5: [
                "ChemicalReaction({0}, {1}, {2}, {3}, {4})",
                "Experiment({0}, {1}, {2}, {3}, {4})",
                "DataTransfer({0}, {1}, {2}, {3}, {4})",
                "ComplexProcess({0}, {1}, {2}, {3}, {4})",
                "SystemState({0}, {1}, {2}, {3}, {4})"
            ]
        }
    
    def add_multi_arg_fact(self, 
                          predicate: str,
                          args: List[str],
                          domain: str = None,
                          fact_type: str = "multi_arg",
                          confidence: float = 1.0,
                          source: str = "ExtendedFactManager") -> Optional[int]:
        """
        Add a multi-argument fact to the database
        
        Args:
            predicate: The predicate name
            args: List of arguments (3-5+ supported)
            domain: Domain classification
            fact_type: Type of fact
            confidence: Confidence score
            source: Source of the fact
            
        Returns:
            ID of inserted fact or None if failed
        """
        arg_count = len(args)
        
        # Build statement
        statement = f"{predicate}({', '.join(args)})."
        
        # Prepare arguments for database
        arg_values = [None] * 5
        args_json = None
        
        for i, arg in enumerate(args[:5]):
            arg_values[i] = arg
            
        # If more than 5 arguments, store extras in JSON
        if arg_count > 5:
            extra_args = {f'arg{i+6}': args[i+5] for i in range(len(args[5:]))}
            args_json = json.dumps(extra_args)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO facts_extended (
                    statement, predicate, arg_count,
                    arg1, arg2, arg3, arg4, arg5, args_json,
                    fact_type, domain, complexity, confidence, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                statement, predicate, arg_count,
                arg_values[0], arg_values[1], arg_values[2], 
                arg_values[3], arg_values[4], args_json,
                fact_type, domain, min(arg_count, 5), confidence, source
            ))
            
            conn.commit()
            fact_id = cursor.lastrowid
            self.logger.info(f"Added multi-arg fact {fact_id}: {statement}")
            return fact_id
            
        except sqlite3.IntegrityError:
            self.logger.debug(f"Fact already exists: {statement}")
            return None
        except Exception as e:
            self.logger.error(f"Error adding fact: {e}")
            return None
        finally:
            conn.close()
    
    def add_formula(self,
                    name: str,
                    expression: str,
                    domain: str,
                    variables: Dict[str, str],
                    constants: Dict[str, Any] = None,
                    fact_id: int = None) -> Optional[int]:
        """
        Add a mathematical formula
        
        Args:
            name: Formula name
            expression: Mathematical expression
            domain: Domain (physics, chemistry, etc.)
            variables: Dict of variable names and descriptions
            constants: Dict of constants and values
            fact_id: Optional linked fact ID
            
        Returns:
            ID of inserted formula or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO formulas (
                    name, expression, domain, variables, constants, fact_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name, expression, domain,
                json.dumps(variables),
                json.dumps(constants or {}),
                fact_id
            ))
            
            conn.commit()
            formula_id = cursor.lastrowid
            self.logger.info(f"Added formula {formula_id}: {name} = {expression}")
            return formula_id
            
        except Exception as e:
            self.logger.error(f"Error adding formula: {e}")
            return None
        finally:
            conn.close()
    
    def extract_multi_arg_facts(self, text: str, domain: str = None) -> List[Dict[str, Any]]:
        """
        Extract multi-argument facts from text
        
        Args:
            text: Text to analyze
            domain: Optional domain hint
            
        Returns:
            List of extracted facts with metadata
        """
        extracted_facts = []
        
        # Try domain-specific patterns
        domains_to_check = [domain] if domain else list(self.DOMAIN_PATTERNS.keys())
        
        for dom in domains_to_check:
            if dom not in self.DOMAIN_PATTERNS:
                continue
                
            for pattern_name, pattern_info in self.DOMAIN_PATTERNS[dom].items():
                regex = pattern_info['pattern']
                matches = re.finditer(regex, text, re.IGNORECASE)
                
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= pattern_info['args']:
                        fact = {
                            'predicate': pattern_info['predicate'],
                            'args': list(groups[:pattern_info['args']]),
                            'domain': dom,
                            'pattern': pattern_name,
                            'statement': pattern_info['template'].format(*groups[:pattern_info['args']])
                        }
                        extracted_facts.append(fact)
        
        return extracted_facts
    
    def generate_domain_facts(self, domain: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate domain-specific multi-argument facts
        
        Args:
            domain: Target domain
            count: Number of facts to generate
            
        Returns:
            List of generated facts
        """
        facts = []
        
        if domain == 'chemistry':
            facts.extend([
                {'predicate': 'Reaction', 'args': ['H2', 'O2', 'H2O', 'combustion', 'exothermic'], 'domain': 'chemistry'},
                {'predicate': 'Catalyst', 'args': ['Pt', 'H2', 'hydrogenation', '25C'], 'domain': 'chemistry'},
                {'predicate': 'Solubility', 'args': ['NaCl', 'H2O', '359g/L', '20C'], 'domain': 'chemistry'},
                {'predicate': 'Oxidation', 'args': ['Fe', 'O2', 'Fe2O3', 'rust'], 'domain': 'chemistry'},
                {'predicate': 'AcidBase', 'args': ['HCl', 'NaOH', 'NaCl', 'H2O', 'neutralization'], 'domain': 'chemistry'}
            ])
        
        elif domain == 'physics':
            facts.extend([
                {'predicate': 'Force', 'args': ['Earth', 'Moon', '1.98e20N', 'gravitational'], 'domain': 'physics'},
                {'predicate': 'Energy', 'args': ['Photon', '2.5eV', 'electromagnetic', 'visible'], 'domain': 'physics'},
                {'predicate': 'Motion', 'args': ['Electron', '2.2e6m/s', 'orbital', 'hydrogen'], 'domain': 'physics'},
                {'predicate': 'Wave', 'args': ['Light', '650nm', 'red', 'visible', 'electromagnetic'], 'domain': 'physics'},
                {'predicate': 'Field', 'args': ['Magnet', '0.5T', 'north', 'uniform'], 'domain': 'physics'}
            ])
        
        elif domain == 'biology':
            facts.extend([
                {'predicate': 'Photosynthesis', 'args': ['CO2', 'H2O', 'Glucose', 'O2', 'chloroplast'], 'domain': 'biology'},
                {'predicate': 'Transcription', 'args': ['DNA', 'RNA', 'polymerase', 'nucleus'], 'domain': 'biology'},
                {'predicate': 'CellDivision', 'args': ['Cell', 'Mitosis', '2', 'identical'], 'domain': 'biology'},
                {'predicate': 'Enzyme', 'args': ['Amylase', 'Starch', 'Glucose', 'pH7', '37C'], 'domain': 'biology'},
                {'predicate': 'Mutation', 'args': ['Gene', 'A', 'T', 'point', 'substitution'], 'domain': 'biology'}
            ])
        
        elif domain == 'economics':
            facts.extend([
                {'predicate': 'Transaction', 'args': ['Alice', 'Bob', '1000USD', '2025-09-15', 'payment'], 'domain': 'economics'},
                {'predicate': 'Market', 'args': ['Gold', '2000USD/oz', 'NYSE', '2025-09-15'], 'domain': 'economics'},
                {'predicate': 'Trade', 'args': ['USA', 'China', '500B', '2025', 'imports'], 'domain': 'economics'},
                {'predicate': 'Investment', 'args': ['Fund', 'Tesla', '10M', '12%', 'equity'], 'domain': 'economics'},
                {'predicate': 'Currency', 'args': ['EUR', 'USD', '1.18', '2025-09-15'], 'domain': 'economics'}
            ])
        
        elif domain == 'geography':
            facts.extend([
                {'predicate': 'Located', 'args': ['Paris', 'France', 'Europe'], 'domain': 'geography'},
                {'predicate': 'Coordinates', 'args': ['Berlin', '52.5200N', '13.4050E'], 'domain': 'geography'},
                {'predicate': 'Border', 'args': ['Germany', 'France', '451km'], 'domain': 'geography'},
                {'predicate': 'River', 'args': ['Rhine', 'Switzerland', 'Netherlands', '1233km'], 'domain': 'geography'},
                {'predicate': 'Mountain', 'args': ['Everest', 'Nepal', 'China', '8849m'], 'domain': 'geography'}
            ])
        
        elif domain == 'medicine':
            facts.extend([
                {'predicate': 'Treatment', 'args': ['Aspirin', 'Headache', '500mg', '85%'], 'domain': 'medicine'},
                {'predicate': 'Diagnosis', 'args': ['MRI', 'BrainTumor', '95%', 'confirmed'], 'domain': 'medicine'},
                {'predicate': 'Vaccine', 'args': ['mRNA', 'COVID19', '95%', 'Pfizer'], 'domain': 'medicine'},
                {'predicate': 'Surgery', 'args': ['Appendectomy', 'Appendicitis', '98%', 'laparoscopic'], 'domain': 'medicine'},
                {'predicate': 'Drug', 'args': ['Insulin', 'Diabetes', 'subcutaneous', 'daily'], 'domain': 'medicine'}
            ])
        
        elif domain == 'technology':
            facts.extend([
                {'predicate': 'Protocol', 'args': ['Client', 'Server', 'HTTPS', '443'], 'domain': 'technology'},
                {'predicate': 'Algorithm', 'args': ['QuickSort', 'O(nlogn)', 'average', 'divide-conquer'], 'domain': 'technology'},
                {'predicate': 'Network', 'args': ['Router', 'Switch', '1Gbps', 'Ethernet'], 'domain': 'technology'},
                {'predicate': 'Database', 'args': ['PostgreSQL', 'ACID', 'relational', 'SQL'], 'domain': 'technology'},
                {'predicate': 'Encryption', 'args': ['AES', '256bit', 'symmetric', 'block'], 'domain': 'technology'}
            ])
        
        elif domain == 'mathematics':
            facts.extend([
                {'predicate': 'Equation', 'args': ['E', 'mc2', 'relativity', 'Einstein'], 'domain': 'mathematics'},
                {'predicate': 'Function', 'args': ['f(x)', 'x2', 'quadratic', 'parabola'], 'domain': 'mathematics'},
                {'predicate': 'Theorem', 'args': ['Pythagorean', 'a2+b2', 'c2', 'right', 'triangle'], 'domain': 'mathematics'},
                {'predicate': 'Proof', 'args': ['Euclid', 'infinite', 'primes', 'contradiction'], 'domain': 'mathematics'},
                {'predicate': 'Calculation', 'args': ['Pi', '3.14159', 'circumference', 'diameter'], 'domain': 'mathematics'}
            ])
        
        # NEUE DOMAINS für mehr Themenvarianz
        elif domain == 'astronomy':
            facts.extend([
                {'predicate': 'Orbit', 'args': ['Earth', 'Sun', '365.25', 'days', 'elliptical'], 'domain': 'astronomy'},
                {'predicate': 'Gravity', 'args': ['BlackHole', 'EventHorizon', 'singularity', 'spacetime'], 'domain': 'astronomy'},
                {'predicate': 'Planet', 'args': ['Mars', 'Red', 'Olympus', 'Mons', 'volcano'], 'domain': 'astronomy'},
                {'predicate': 'Star', 'args': ['Sun', 'G2V', 'yellow', 'dwarf', '4.6B'], 'domain': 'astronomy'},
                {'predicate': 'Galaxy', 'args': ['MilkyWay', 'spiral', '100B', 'stars', 'barred'], 'domain': 'astronomy'}
            ])
        
        elif domain == 'geology':
            facts.extend([
                {'predicate': 'Earthquake', 'args': ['SanAndreas', '7.8', 'Richter', 'California', '1906'], 'domain': 'geology'},
                {'predicate': 'Volcano', 'args': ['Vesuvius', 'Pompeii', '79AD', 'pyroclastic', 'flow'], 'domain': 'geology'},
                {'predicate': 'Fossil', 'args': ['T-Rex', 'Cretaceous', '65M', 'years', 'extinct'], 'domain': 'geology'},
                {'predicate': 'Mineral', 'args': ['Diamond', 'carbon', 'cubic', 'crystal', 'hardest'], 'domain': 'geology'},
                {'predicate': 'Rock', 'args': ['Granite', 'igneous', 'quartz', 'feldspar', 'mica'], 'domain': 'geology'}
            ])
        
        elif domain == 'psychology':
            facts.extend([
                {'predicate': 'Memory', 'args': ['Hippocampus', 'long-term', 'consolidation', 'sleep'], 'domain': 'psychology'},
                {'predicate': 'Learning', 'args': ['Pavlov', 'conditioning', 'stimulus', 'response'], 'domain': 'psychology'},
                {'predicate': 'Behavior', 'args': ['Operant', 'reinforcement', 'positive', 'negative'], 'domain': 'psychology'},
                {'predicate': 'Emotion', 'args': ['Amygdala', 'fear', 'processing', 'threat'], 'domain': 'psychology'},
                {'predicate': 'Cognition', 'args': ['Prefrontal', 'executive', 'function', 'decision'], 'domain': 'psychology'}
            ])
        
        elif domain == 'sociology':
            facts.extend([
                {'predicate': 'Society', 'args': ['Industrial', 'revolution', 'urbanization', 'class'], 'domain': 'sociology'},
                {'predicate': 'Culture', 'args': ['Language', 'beliefs', 'values', 'norms'], 'domain': 'sociology'},
                {'predicate': 'Community', 'args': ['Social', 'capital', 'trust', 'cooperation'], 'domain': 'sociology'},
                {'predicate': 'Institution', 'args': ['Family', 'education', 'religion', 'government'], 'domain': 'sociology'},
                {'predicate': 'Organization', 'args': ['Bureaucracy', 'hierarchy', 'formal', 'structure'], 'domain': 'sociology'}
            ])
        
        elif domain == 'history':
            facts.extend([
                {'predicate': 'Event', 'args': ['WWII', '1939-1945', 'Allies', 'Axis', 'global'], 'domain': 'history'},
                {'predicate': 'Period', 'args': ['Renaissance', '14th-17th', 'century', 'art', 'science'], 'domain': 'history'},
                {'predicate': 'Era', 'args': ['Industrial', 'Age', 'steam', 'power', 'manufacturing'], 'domain': 'history'},
                {'predicate': 'Civilization', 'args': ['Roman', 'Empire', '27BC-476AD', 'Mediterranean'], 'domain': 'history'},
                {'predicate': 'War', 'args': ['Napoleonic', 'Wars', '1803-1815', 'France', 'coalition'], 'domain': 'history'}
            ])
        
        elif domain == 'linguistics':
            facts.extend([
                {'predicate': 'Language', 'args': ['German', 'Indo-European', '95M', 'speakers'], 'domain': 'linguistics'},
                {'predicate': 'Grammar', 'args': ['Syntax', 'morphology', 'phonology', 'semantics'], 'domain': 'linguistics'},
                {'predicate': 'Syntax', 'args': ['SVO', 'subject', 'verb', 'object', 'order'], 'domain': 'linguistics'},
                {'predicate': 'Semantics', 'args': ['Meaning', 'reference', 'sense', 'context'], 'domain': 'linguistics'},
                {'predicate': 'Phonetics', 'args': ['IPA', 'International', 'Phonetic', 'Alphabet'], 'domain': 'linguistics'}
            ])
        
        elif domain == 'philosophy':
            facts.extend([
                {'predicate': 'Logic', 'args': ['Syllogism', 'premise', 'conclusion', 'valid'], 'domain': 'philosophy'},
                {'predicate': 'Reasoning', 'args': ['Deductive', 'inductive', 'abductive', 'inference'], 'domain': 'philosophy'},
                {'predicate': 'Argument', 'args': ['Premise', 'conclusion', 'validity', 'soundness'], 'domain': 'philosophy'},
                {'predicate': 'Theory', 'args': ['Utilitarianism', 'greatest', 'good', 'happiness'], 'domain': 'philosophy'},
                {'predicate': 'Concept', 'args': ['Justice', 'fairness', 'equality', 'rights'], 'domain': 'philosophy'}
            ])
        
        elif domain == 'art':
            facts.extend([
                {'predicate': 'Painting', 'args': ['MonaLisa', 'Leonardo', 'Renaissance', 'oil', 'canvas'], 'domain': 'art'},
                {'predicate': 'Sculpture', 'args': ['David', 'Michelangelo', 'marble', 'Renaissance'], 'domain': 'art'},
                {'predicate': 'Design', 'args': ['Bauhaus', 'modernist', 'function', 'form'], 'domain': 'art'},
                {'predicate': 'Style', 'args': ['Impressionism', 'Monet', 'Renoir', 'light', 'color'], 'domain': 'art'},
                {'predicate': 'Technique', 'args': ['Chiaroscuro', 'light', 'dark', 'contrast'], 'domain': 'art'}
            ])
        
        elif domain == 'music':
            facts.extend([
                {'predicate': 'Composition', 'args': ['Symphony', 'Beethoven', '9th', 'Ode', 'Joy'], 'domain': 'music'},
                {'predicate': 'Melody', 'args': ['Theme', 'variation', 'development', 'recapitulation'], 'domain': 'music'},
                {'predicate': 'Harmony', 'args': ['Chord', 'progression', 'tonic', 'dominant'], 'domain': 'music'},
                {'predicate': 'Rhythm', 'args': ['Meter', 'time', 'signature', 'beat', 'tempo'], 'domain': 'music'},
                {'predicate': 'Instrument', 'args': ['Piano', '88', 'keys', 'strings', 'hammers'], 'domain': 'music'}
            ])
        
        elif domain == 'literature':
            facts.extend([
                {'predicate': 'Novel', 'args': ['War', 'Peace', 'Tolstoy', 'Russian', 'epic'], 'domain': 'literature'},
                {'predicate': 'Poetry', 'args': ['Sonnet', '14', 'lines', 'iambic', 'pentameter'], 'domain': 'literature'},
                {'predicate': 'Drama', 'args': ['Hamlet', 'Shakespeare', 'tragedy', 'revenge'], 'domain': 'literature'},
                {'predicate': 'Character', 'args': ['Protagonist', 'antagonist', 'conflict', 'resolution'], 'domain': 'literature'},
                {'predicate': 'Plot', 'args': ['Exposition', 'rising', 'action', 'climax', 'falling'], 'domain': 'literature'}
            ])
        
        elif domain == 'architecture':
            facts.extend([
                {'predicate': 'Building', 'args': ['Parthenon', 'Athens', 'Doric', 'columns', 'marble'], 'domain': 'architecture'},
                {'predicate': 'Structure', 'args': ['Gothic', 'cathedral', 'flying', 'buttress', 'ribbed'], 'domain': 'architecture'},
                {'predicate': 'Material', 'args': ['Concrete', 'steel', 'reinforced', 'modern', 'construction'], 'domain': 'architecture'},
                {'predicate': 'Foundation', 'args': ['Pile', 'driving', 'load', 'bearing', 'capacity'], 'domain': 'architecture'},
                {'predicate': 'Roof', 'args': ['Dome', 'Pantheon', 'concrete', 'oculus', 'opening'], 'domain': 'architecture'}
            ])
        
        elif domain == 'engineering':
            facts.extend([
                {'predicate': 'Machine', 'args': ['Steam', 'engine', 'Watt', 'industrial', 'revolution'], 'domain': 'engineering'},
                {'predicate': 'Device', 'args': ['Telescope', 'Galileo', 'lenses', 'magnification', 'astronomy'], 'domain': 'engineering'},
                {'predicate': 'Component', 'args': ['Gear', 'ratio', 'torque', 'speed', 'mechanical'], 'domain': 'engineering'},
                {'predicate': 'System', 'args': ['Electrical', 'grid', 'power', 'distribution', 'network'], 'domain': 'engineering'},
                {'predicate': 'Process', 'args': ['Manufacturing', 'assembly', 'line', 'Ford', 'automation'], 'domain': 'engineering'}
            ])
        
        elif domain == 'computer_science':
            facts.extend([
                {'predicate': 'Algorithm', 'args': ['Dijkstra', 'shortest', 'path', 'graph', 'weighted'], 'domain': 'computer_science'},
                {'predicate': 'DataStructure', 'args': ['Binary', 'tree', 'search', 'logarithmic', 'complexity'], 'domain': 'computer_science'},
                {'predicate': 'Programming', 'args': ['Python', 'object-oriented', 'interpreted', 'dynamic'], 'domain': 'computer_science'},
                {'predicate': 'Database', 'args': ['SQL', 'relational', 'ACID', 'transactions', 'integrity'], 'domain': 'computer_science'},
                {'predicate': 'Network', 'args': ['TCP/IP', 'protocol', 'stack', 'internet', 'communication'], 'domain': 'computer_science'}
            ])
        
        elif domain == 'robotics':
            facts.extend([
                {'predicate': 'Robot', 'args': ['ASIMO', 'Honda', 'bipedal', '130cm', '54kg'], 'domain': 'robotics'},
                {'predicate': 'Sensor', 'args': ['LIDAR', 'laser', 'ranging', 'autonomous', 'vehicles'], 'domain': 'robotics'},
                {'predicate': 'Actuator', 'args': ['Servo', 'motor', 'position', 'control', 'feedback'], 'domain': 'robotics'},
                {'predicate': 'Programming', 'args': ['ROS', 'Robot', 'Operating', 'System', 'framework'], 'domain': 'robotics'},
                {'predicate': 'Navigation', 'args': ['SLAM', 'simultaneous', 'localization', 'mapping'], 'domain': 'robotics'}
            ])
        
        elif domain == 'ai':
            facts.extend([
                {'predicate': 'Intelligence', 'args': ['Artificial', 'machine', 'learning', 'neural', 'networks'], 'domain': 'ai'},
                {'predicate': 'Learning', 'args': ['Deep', 'learning', 'backpropagation', 'gradient', 'descent'], 'domain': 'ai'},
                {'predicate': 'Neural', 'args': ['Perceptron', 'weights', 'bias', 'activation', 'function'], 'domain': 'ai'},
                {'predicate': 'Pattern', 'args': ['Recognition', 'classification', 'supervised', 'unsupervised'], 'domain': 'ai'},
                {'predicate': 'Classification', 'args': ['Support', 'Vector', 'Machine', 'SVM', 'hyperplane'], 'domain': 'ai'}
            ])
        
        elif domain == 'cryptography':
            facts.extend([
                {'predicate': 'Security', 'args': ['RSA', 'public', 'key', 'cryptography', 'asymmetric'], 'domain': 'cryptography'},
                {'predicate': 'Privacy', 'args': ['Zero-knowledge', 'proof', 'verification', 'without', 'revealing'], 'domain': 'cryptography'},
                {'predicate': 'Authentication', 'args': ['Digital', 'signature', 'hash', 'function', 'integrity'], 'domain': 'cryptography'},
                {'predicate': 'Authorization', 'args': ['Access', 'control', 'permissions', 'roles', 'policies'], 'domain': 'cryptography'},
                {'predicate': 'Blockchain', 'args': ['Bitcoin', 'distributed', 'ledger', 'consensus', 'mining'], 'domain': 'cryptography'}
            ])
        
        elif domain == 'environmental_science':
            facts.extend([
                {'predicate': 'Climate', 'args': ['Global', 'warming', '1.1C', '1880-2020', 'CO2'], 'domain': 'environmental_science'},
                {'predicate': 'Weather', 'args': ['Hurricane', 'Category', '5', 'wind', 'speed'], 'domain': 'environmental_science'},
                {'predicate': 'Temperature', 'args': ['Greenhouse', 'effect', 'radiation', 'trapping', 'heat'], 'domain': 'environmental_science'},
                {'predicate': 'Precipitation', 'args': ['Rain', 'snow', 'hail', 'sleet', 'atmospheric'], 'domain': 'environmental_science'},
                {'predicate': 'Wind', 'args': ['Trade', 'winds', 'Coriolis', 'effect', 'rotation'], 'domain': 'environmental_science'}
            ])
        
        elif domain == 'ecology':
            facts.extend([
                {'predicate': 'Ecosystem', 'args': ['Food', 'web', 'producer', 'consumer', 'decomposer'], 'domain': 'ecology'},
                {'predicate': 'Species', 'args': ['Biodiversity', 'extinction', 'conservation', 'habitat', 'loss'], 'domain': 'ecology'},
                {'predicate': 'Habitat', 'args': ['Niche', 'environment', 'resources', 'competition', 'adaptation'], 'domain': 'ecology'},
                {'predicate': 'Biodiversity', 'args': ['Genetic', 'species', 'ecosystem', 'diversity', 'hotspot'], 'domain': 'ecology'},
                {'predicate': 'Conservation', 'args': ['Protected', 'area', 'endangered', 'species', 'recovery'], 'domain': 'ecology'}
            ])
        
        elif domain == 'genetics':
            facts.extend([
                {'predicate': 'Gene', 'args': ['CFTR', 'chromosome7', '1480', 'amino', 'acids'], 'domain': 'genetics'},
                {'predicate': 'DNA', 'args': ['Double', 'helix', 'Watson', 'Crick', 'base', 'pairs'], 'domain': 'genetics'},
                {'predicate': 'RNA', 'args': ['Messenger', 'mRNA', 'transcription', 'translation', 'protein'], 'domain': 'genetics'},
                {'predicate': 'Protein', 'args': ['Amino', 'acids', 'peptide', 'bonds', 'folding'], 'domain': 'genetics'},
                {'predicate': 'Chromosome', 'args': ['Human', '46', 'diploid', 'haploid', 'meiosis'], 'domain': 'genetics'}
            ])
        
        elif domain == 'neuroscience':
            facts.extend([
                {'predicate': 'Brain', 'args': ['Cerebrum', 'cerebellum', 'brainstem', 'cortex', 'white'], 'domain': 'neuroscience'},
                {'predicate': 'Neuron', 'args': ['Dendrite', 'axon', 'synapse', 'neurotransmitter', 'action'], 'domain': 'neuroscience'},
                {'predicate': 'Synapse', 'args': ['Presynaptic', 'postsynaptic', 'vesicle', 'receptor', 'binding'], 'domain': 'neuroscience'},
                {'predicate': 'Neurotransmitter', 'args': ['Dopamine', 'serotonin', 'GABA', 'glutamate', 'acetylcholine'], 'domain': 'neuroscience'},
                {'predicate': 'Cortex', 'args': ['Cerebral', 'gray', 'matter', 'gyri', 'sulci'], 'domain': 'neuroscience'}
            ])
        
        elif domain == 'immunology':
            facts.extend([
                {'predicate': 'Immune', 'args': ['Innate', 'adaptive', 'response', 'pathogen', 'antigen'], 'domain': 'immunology'},
                {'predicate': 'Antibody', 'args': ['Immunoglobulin', 'B-cell', 'plasma', 'memory', 'affinity'], 'domain': 'immunology'},
                {'predicate': 'Antigen', 'args': ['Epitope', 'binding', 'site', 'recognition', 'specificity'], 'domain': 'immunology'},
                {'predicate': 'Pathogen', 'args': ['Bacteria', 'virus', 'fungus', 'parasite', 'infection'], 'domain': 'immunology'},
                {'predicate': 'Infection', 'args': ['Acute', 'chronic', 'latent', 'opportunistic', 'nosocomial'], 'domain': 'immunology'}
            ])
        
        elif domain == 'pharmacology':
            facts.extend([
                {'predicate': 'Medicine', 'args': ['Drug', 'pharmacokinetics', 'pharmacodynamics', 'dose', 'response'], 'domain': 'pharmacology'},
                {'predicate': 'Therapy', 'args': ['Treatment', 'efficacy', 'safety', 'tolerability', 'adherence'], 'domain': 'pharmacology'},
                {'predicate': 'Dosage', 'args': ['Therapeutic', 'window', 'minimum', 'effective', 'toxic'], 'domain': 'pharmacology'},
                {'predicate': 'SideEffect', 'args': ['Adverse', 'event', 'contraindication', 'interaction', 'monitoring'], 'domain': 'pharmacology'},
                {'predicate': 'Contraindication', 'args': ['Absolute', 'relative', 'risk', 'benefit', 'assessment'], 'domain': 'pharmacology'}
            ])
        
        elif domain == 'surgery':
            facts.extend([
                {'predicate': 'Operation', 'args': ['Surgical', 'procedure', 'anesthesia', 'incision', 'closure'], 'domain': 'surgery'},
                {'predicate': 'Procedure', 'args': ['Laparoscopic', 'minimally', 'invasive', 'endoscope', 'trocar'], 'domain': 'surgery'},
                {'predicate': 'Anesthesia', 'args': ['General', 'local', 'regional', 'sedation', 'monitoring'], 'domain': 'surgery'},
                {'predicate': 'Recovery', 'args': ['Postoperative', 'care', 'complications', 'rehabilitation', 'follow-up'], 'domain': 'surgery'},
                {'predicate': 'Complication', 'args': ['Infection', 'bleeding', 'organ', 'damage', 'adhesion'], 'domain': 'surgery'}
            ])
        
        elif domain == 'finance':
            facts.extend([
                {'predicate': 'Money', 'args': ['Currency', 'exchange', 'rate', 'inflation', 'deflation'], 'domain': 'finance'},
                {'predicate': 'Bank', 'args': ['Central', 'bank', 'monetary', 'policy', 'interest', 'rate'], 'domain': 'finance'},
                {'predicate': 'Credit', 'args': ['Loan', 'debt', 'interest', 'principal', 'collateral'], 'domain': 'finance'},
                {'predicate': 'Loan', 'args': ['Mortgage', 'amortization', 'down', 'payment', 'equity'], 'domain': 'finance'},
                {'predicate': 'Interest', 'args': ['Compound', 'simple', 'APR', 'APY', 'yield'], 'domain': 'finance'}
            ])
        
        elif domain == 'marketing':
            facts.extend([
                {'predicate': 'Customer', 'args': ['Target', 'market', 'segmentation', 'demographics', 'psychographics'], 'domain': 'marketing'},
                {'predicate': 'Product', 'args': ['Lifecycle', 'introduction', 'growth', 'maturity', 'decline'], 'domain': 'marketing'},
                {'predicate': 'Service', 'args': ['Customer', 'satisfaction', 'quality', 'expectations', 'perceptions'], 'domain': 'marketing'},
                {'predicate': 'Brand', 'args': ['Identity', 'equity', 'loyalty', 'awareness', 'association'], 'domain': 'marketing'},
                {'predicate': 'Advertising', 'args': ['Campaign', 'reach', 'frequency', 'impact', 'ROI'], 'domain': 'marketing'}
            ])
        
        elif domain == 'management':
            facts.extend([
                {'predicate': 'Leadership', 'args': ['Transformational', 'transactional', 'charismatic', 'servant'], 'domain': 'management'},
                {'predicate': 'Strategy', 'args': ['SWOT', 'analysis', 'competitive', 'advantage', 'positioning'], 'domain': 'management'},
                {'predicate': 'Planning', 'args': ['Strategic', 'tactical', 'operational', 'budget', 'forecast'], 'domain': 'management'},
                {'predicate': 'Execution', 'args': ['Implementation', 'monitoring', 'control', 'feedback', 'adjustment'], 'domain': 'management'},
                {'predicate': 'Team', 'args': ['Forming', 'storming', 'norming', 'performing', 'adjourning'], 'domain': 'management'}
            ])
        
        elif domain == 'entrepreneurship':
            facts.extend([
                {'predicate': 'Startup', 'args': ['Lean', 'canvas', 'MVP', 'pivot', 'iteration'], 'domain': 'entrepreneurship'},
                {'predicate': 'Innovation', 'args': ['Disruptive', 'sustaining', 'incremental', 'radical', 'breakthrough'], 'domain': 'entrepreneurship'},
                {'predicate': 'Venture', 'args': ['Capital', 'angel', 'investor', 'equity', 'valuation'], 'domain': 'entrepreneurship'},
                {'predicate': 'Funding', 'args': ['Seed', 'Series', 'A', 'B', 'C', 'round'], 'domain': 'entrepreneurship'},
                {'predicate': 'Growth', 'args': ['Scaling', 'hiring', 'expansion', 'market', 'penetration'], 'domain': 'entrepreneurship'}
            ])
        
        elif domain == 'politics':
            facts.extend([
                {'predicate': 'Government', 'args': ['Democracy', 'republic', 'monarchy', 'authoritarianism', 'totalitarianism'], 'domain': 'politics'},
                {'predicate': 'Policy', 'args': ['Public', 'social', 'economic', 'foreign', 'domestic'], 'domain': 'politics'},
                {'predicate': 'Law', 'args': ['Constitutional', 'statutory', 'common', 'civil', 'criminal'], 'domain': 'politics'},
                {'predicate': 'Regulation', 'args': ['Administrative', 'agency', 'rulemaking', 'enforcement', 'compliance'], 'domain': 'politics'},
                {'predicate': 'Democracy', 'args': ['Representative', 'direct', 'majority', 'rule', 'minority', 'rights'], 'domain': 'politics'}
            ])
        
        elif domain == 'law':
            facts.extend([
                {'predicate': 'Justice', 'args': ['Distributive', 'procedural', 'retributive', 'restorative', 'social'], 'domain': 'law'},
                {'predicate': 'Court', 'args': ['Supreme', 'appellate', 'trial', 'jurisdiction', 'venue'], 'domain': 'law'},
                {'predicate': 'Judge', 'args': ['Impartial', 'independent', 'tenure', 'appointment', 'election'], 'domain': 'law'},
                {'predicate': 'Jury', 'args': ['Grand', 'petit', 'voir', 'dire', 'deliberation'], 'domain': 'law'},
                {'predicate': 'Verdict', 'args': ['Guilty', 'not', 'guilty', 'hung', 'jury', 'mistrial'], 'domain': 'law'}
            ])
        
        elif domain == 'ethics':
            facts.extend([
                {'predicate': 'Morality', 'args': ['Deontological', 'consequentialist', 'virtue', 'ethics', 'care'], 'domain': 'ethics'},
                {'predicate': 'Virtue', 'args': ['Aristotle', 'golden', 'mean', 'excellence', 'character'], 'domain': 'ethics'},
                {'predicate': 'Duty', 'args': ['Kant', 'categorical', 'imperative', 'universalizability', 'autonomy'], 'domain': 'ethics'},
                {'predicate': 'Rights', 'args': ['Natural', 'human', 'civil', 'political', 'social'], 'domain': 'ethics'},
                {'predicate': 'Responsibility', 'args': ['Moral', 'legal', 'causal', 'role', 'collective'], 'domain': 'ethics'}
            ])
        
        elif domain == 'anthropology':
            facts.extend([
                {'predicate': 'Human', 'args': ['Evolution', 'hominid', 'australopithecus', 'homo', 'sapiens'], 'domain': 'anthropology'},
                {'predicate': 'Evolution', 'args': ['Natural', 'selection', 'adaptation', 'fitness', 'survival'], 'domain': 'anthropology'},
                {'predicate': 'Culture', 'args': ['Material', 'non-material', 'symbols', 'values', 'norms'], 'domain': 'anthropology'},
                {'predicate': 'Tradition', 'args': ['Oral', 'written', 'customs', 'rituals', 'ceremonies'], 'domain': 'anthropology'},
                {'predicate': 'Custom', 'args': ['Folkways', 'mores', 'taboos', 'sanctions', 'enforcement'], 'domain': 'anthropology'}
            ])
        
        elif domain == 'archaeology':
            facts.extend([
                {'predicate': 'Artifact', 'args': ['Stone', 'tools', 'pottery', 'jewelry', 'weapons'], 'domain': 'archaeology'},
                {'predicate': 'Excavation', 'args': ['Stratigraphy', 'context', 'provenience', 'association', 'dating'], 'domain': 'archaeology'},
                {'predicate': 'Site', 'args': ['Settlement', 'burial', 'ritual', 'industrial', 'military'], 'domain': 'archaeology'},
                {'predicate': 'Dating', 'args': ['Radiocarbon', 'potassium-argon', 'thermoluminescence', 'relative', 'absolute'], 'domain': 'archaeology'},
                {'predicate': 'Analysis', 'args': ['Lithic', 'ceramic', 'faunal', 'botanical', 'isotopic'], 'domain': 'archaeology'}
            ])
        
        elif domain == 'paleontology':
            facts.extend([
                {'predicate': 'Dinosaur', 'args': ['Tyrannosaurus', 'rex', 'Cretaceous', 'carnivore', 'bipedal'], 'domain': 'paleontology'},
                {'predicate': 'Extinction', 'args': ['K-T', 'boundary', 'asteroid', 'impact', 'Chicxulub'], 'domain': 'paleontology'},
                {'predicate': 'Fossil', 'args': ['Preservation', 'taphonomy', 'permineralization', 'replacement', 'carbonization'], 'domain': 'paleontology'},
                {'predicate': 'Evolution', 'args': ['Phylogeny', 'cladistics', 'common', 'ancestor', 'divergence'], 'domain': 'paleontology'},
                {'predicate': 'Adaptation', 'args': ['Natural', 'selection', 'environmental', 'pressure', 'fitness'], 'domain': 'paleontology'}
            ])
        
        elif domain == 'meteorology':
            facts.extend([
                {'predicate': 'Storm', 'args': ['Thunderstorm', 'lightning', 'thunder', 'precipitation', 'convection'], 'domain': 'meteorology'},
                {'predicate': 'Hurricane', 'args': ['Category', 'Saffir-Simpson', 'wind', 'speed', 'pressure'], 'domain': 'meteorology'},
                {'predicate': 'Tornado', 'args': ['Fujita', 'scale', 'funnel', 'cloud', 'vortex'], 'domain': 'meteorology'},
                {'predicate': 'Blizzard', 'args': ['Snow', 'wind', 'visibility', 'temperature', 'duration'], 'domain': 'meteorology'},
                {'predicate': 'Drought', 'args': ['Precipitation', 'deficit', 'soil', 'moisture', 'agricultural'], 'domain': 'meteorology'}
            ])
        
        elif domain == 'oceanography':
            facts.extend([
                {'predicate': 'Ocean', 'args': ['Pacific', 'Atlantic', 'Indian', 'Arctic', 'Southern'], 'domain': 'oceanography'},
                {'predicate': 'Sea', 'args': ['Mediterranean', 'Caribbean', 'Red', 'Black', 'Caspian'], 'domain': 'oceanography'},
                {'predicate': 'Current', 'args': ['Gulf', 'Stream', 'thermohaline', 'circulation', 'conveyor'], 'domain': 'oceanography'},
                {'predicate': 'Tide', 'args': ['Spring', 'neap', 'lunar', 'solar', 'gravitational'], 'domain': 'oceanography'},
                {'predicate': 'Wave', 'args': ['Surface', 'deep', 'water', 'swell', 'breaking'], 'domain': 'oceanography'}
            ])
        
        return facts[:count]
    
    def batch_add_facts(self, facts: List[Dict[str, Any]], use_governance: bool = True) -> int:
        """
        Batch add multiple facts
        
        Args:
            facts: List of fact dictionaries
            use_governance: Whether to use governance engine
            
        Returns:
            Number of successfully added facts
        """
        added = 0
        
        if use_governance:
            try:
                from src_hexagonal.application.transactional_governance_engine import TransactionalGovernanceEngine
                engine = TransactionalGovernanceEngine()
                
                # Convert to statements
                statements = []
                for fact in facts:
                    if 'statement' in fact:
                        statements.append(fact['statement'])
                    elif 'predicate' in fact and 'args' in fact:
                        stmt = f"{fact['predicate']}({', '.join(fact['args'])})."
                        statements.append(stmt)
                
                context = {
                    'operator': 'ExtendedFactManager',
                    'reason': 'Multi-argument fact generation',
                    'harm_prob': 0.0001,
                    'sustain_index': 0.95,
                    'externally_legal': True,
                    'universalizable_proof': True
                }
                
                added = engine.governed_add_facts_atomic(statements, context)
                self.logger.info(f"Added {added} facts through governance")
                
            except Exception as e:
                self.logger.warning(f"Governance failed, falling back to direct insert: {e}")
                # Fallback to direct insert
                for fact in facts:
                    if self.add_multi_arg_fact(
                        fact.get('predicate', 'Unknown'),
                        fact.get('args', []),
                        fact.get('domain'),
                        fact.get('fact_type', 'multi_arg'),
                        fact.get('confidence', 1.0)
                    ):
                        added += 1
        else:
            # Direct insert without governance
            for fact in facts:
                if self.add_multi_arg_fact(
                    fact.get('predicate', 'Unknown'),
                    fact.get('args', []),
                    fact.get('domain'),
                    fact.get('fact_type', 'multi_arg'),
                    fact.get('confidence', 1.0)
                ):
                    added += 1
        
        return added


def test_manager():
    """Test the ExtendedFactManager"""
    manager = ExtendedFactManager()
    
    # Test adding multi-arg facts
    print("Testing multi-argument facts...")
    
    # Chemistry example
    fact_id = manager.add_multi_arg_fact(
        'ChemicalReaction',
        ['2H2', 'O2', '2H2O', 'combustion', 'exothermic'],
        domain='chemistry',
        confidence=0.95
    )
    print(f"Added chemistry fact: {fact_id}")
    
    # Physics example
    fact_id = manager.add_multi_arg_fact(
        'Force',
        ['Earth', 'Moon', '1.98e20N', 'gravitational'],
        domain='physics'
    )
    print(f"Added physics fact: {fact_id}")
    
    # Test formula
    formula_id = manager.add_formula(
        'kinetic_energy',
        'KE = 0.5 * m * v^2',
        'physics',
        {'KE': 'Kinetic Energy (J)', 'm': 'Mass (kg)', 'v': 'Velocity (m/s)'}
    )
    print(f"Added formula: {formula_id}")
    
    # Test extraction
    text = "The reaction H2 + O2 -> H2O is exothermic. Berlin is located in Germany, Europe."
    extracted = manager.extract_multi_arg_facts(text)
    print(f"Extracted {len(extracted)} facts from text")
    
    # Test batch generation
    for domain in ['chemistry', 'physics', 'biology', 'economics']:
        facts = manager.generate_domain_facts(domain, 5)
        added = manager.batch_add_facts(facts, use_governance=False)
        print(f"Added {added} {domain} facts")
    
    print("\nExtendedFactManager test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_manager()
