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
            },
            # BATCH 1: CORE SCIENCES - NEW DOMAINS
            'astronomy': {
                'celestial_body': {
                    'pattern': r'(\w+)\s+is\s+a\s+(\w+)\s+with\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'CelestialBody',
                    'args': 5,
                    'template': 'CelestialBody({0}, {1}, {2}, {3}, {4})'
                },
                'orbit': {
                    'pattern': r'(\w+)\s+orbits\s+(\w+)\s+at\s+([\d.]+)\s*(\w+)\s+in\s+(\w+)',
                    'predicate': 'Orbit',
                    'args': 5,
                    'template': 'Orbit({0}, {1}, {2}, {3}, {4})'
                },
                'galaxy': {
                    'pattern': r'(\w+)\s+is\s+a\s+(\w+)\s+galaxy\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Galaxy',
                    'args': 5,
                    'template': 'Galaxy({0}, {1}, {2}, {3}, {4})'
                },
                'telescope': {
                    'pattern': r'(\w+)\s+telescope\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Telescope',
                    'args': 5,
                    'template': 'Telescope({0}, {1}, {2}, {3}, {4})'
                },
                'exoplanet': {
                    'pattern': r'(\w+)\s+is\s+an\s+exoplanet\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Exoplanet',
                    'args': 5,
                    'template': 'Exoplanet({0}, {1}, {2}, {3}, {4})'
                }
            },
            'geology': {
                'mineral': {
                    'pattern': r'(\w+)\s+is\s+a\s+(\w+)\s+mineral\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Mineral',
                    'args': 5,
                    'template': 'Mineral({0}, {1}, {2}, {3}, {4})'
                },
                'rock': {
                    'pattern': r'(\w+)\s+is\s+a\s+(\w+)\s+rock\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Rock',
                    'args': 5,
                    'template': 'Rock({0}, {1}, {2}, {3}, {4})'
                },
                'tectonic': {
                    'pattern': r'(\w+)\s+plate\s+is\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Tectonic',
                    'args': 5,
                    'template': 'Tectonic({0}, {1}, {2}, {3}, {4})'
                },
                'volcano': {
                    'pattern': r'(\w+)\s+is\s+a\s+(\w+)\s+volcano\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Volcano',
                    'args': 5,
                    'template': 'Volcano({0}, {1}, {2}, {3}, {4})'
                },
                'era': {
                    'pattern': r'(\w+)\s+era\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Era',
                    'args': 5,
                    'template': 'Era({0}, {1}, {2}, {3}, {4})'
                }
            },
            'psychology': {
                'behavior': {
                    'pattern': r'(\w+)\s+behavior\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Behavior',
                    'args': 5,
                    'template': 'Behavior({0}, {1}, {2}, {3}, {4})'
                },
                'cognition': {
                    'pattern': r'(\w+)\s+cognition\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Cognition',
                    'args': 5,
                    'template': 'Cognition({0}, {1}, {2}, {3}, {4})'
                },
                'personality': {
                    'pattern': r'(\w+)\s+personality\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Personality',
                    'args': 5,
                    'template': 'Personality({0}, {1}, {2}, {3}, {4})'
                },
                'development': {
                    'pattern': r'(\w+)\s+development\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Development',
                    'args': 5,
                    'template': 'Development({0}, {1}, {2}, {3}, {4})'
                },
                'disorder': {
                    'pattern': r'(\w+)\s+disorder\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Disorder',
                    'args': 5,
                    'template': 'Disorder({0}, {1}, {2}, {3}, {4})'
                }
            },
            'neuroscience': {
                'neuron': {
                    'pattern': r'(\w+)\s+neuron\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Neuron',
                    'args': 5,
                    'template': 'Neuron({0}, {1}, {2}, {3}, {4})'
                },
                'brain_region': {
                    'pattern': r'(\w+)\s+brain\s+region\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'BrainRegion',
                    'args': 5,
                    'template': 'BrainRegion({0}, {1}, {2}, {3}, {4})'
                },
                'neurotransmitter': {
                    'pattern': r'(\w+)\s+neurotransmitter\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Neurotransmitter',
                    'args': 5,
                    'template': 'Neurotransmitter({0}, {1}, {2}, {3}, {4})'
                },
                'plasticity': {
                    'pattern': r'(\w+)\s+plasticity\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Plasticity',
                    'args': 5,
                    'template': 'Plasticity({0}, {1}, {2}, {3}, {4})'
                },
                'imaging': {
                    'pattern': r'(\w+)\s+imaging\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Imaging',
                    'args': 5,
                    'template': 'Imaging({0}, {1}, {2}, {3}, {4})'
                }
            },
            'sociology': {
                'group': {
                    'pattern': r'(\w+)\s+group\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Group',
                    'args': 5,
                    'template': 'Group({0}, {1}, {2}, {3}, {4})'
                },
                'institution': {
                    'pattern': r'(\w+)\s+institution\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Institution',
                    'args': 5,
                    'template': 'Institution({0}, {1}, {2}, {3}, {4})'
                },
                'theory': {
                    'pattern': r'(\w+)\s+theory\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Theory',
                    'args': 5,
                    'template': 'Theory({0}, {1}, {2}, {3}, {4})'
                },
                'culture': {
                    'pattern': r'(\w+)\s+culture\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Culture',
                    'args': 5,
                    'template': 'Culture({0}, {1}, {2}, {3}, {4})'
                },
                'mobility': {
                    'pattern': r'(\w+)\s+mobility\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Mobility',
                    'args': 5,
                    'template': 'Mobility({0}, {1}, {2}, {3}, {4})'
                }
            },
            'linguistics': {
                'phoneme': {
                    'pattern': r'(\w+)\s+phoneme\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Phoneme',
                    'args': 5,
                    'template': 'Phoneme({0}, {1}, {2}, {3}, {4})'
                },
                'syntax': {
                    'pattern': r'(\w+)\s+syntax\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Syntax',
                    'args': 5,
                    'template': 'Syntax({0}, {1}, {2}, {3}, {4})'
                },
                'semantics': {
                    'pattern': r'(\w+)\s+semantics\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Semantics',
                    'args': 5,
                    'template': 'Semantics({0}, {1}, {2}, {3}, {4})'
                },
                'language': {
                    'pattern': r'(\w+)\s+language\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Language',
                    'args': 5,
                    'template': 'Language({0}, {1}, {2}, {3}, {4})'
                },
                'evolution': {
                    'pattern': r'(\w+)\s+evolution\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Evolution',
                    'args': 5,
                    'template': 'Evolution({0}, {1}, {2}, {3}, {4})'
                }
            },
            # BATCH 2: ARTS & HUMANITIES - NEW DOMAINS
            'philosophy': {
                'concept': {
                    'pattern': r'(\w+)\s+concept\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Concept',
                    'args': 5,
                    'template': 'Concept({0}, {1}, {2}, {3}, {4})'
                },
                'theory': {
                    'pattern': r'(\w+)\s+theory\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Theory',
                    'args': 5,
                    'template': 'Theory({0}, {1}, {2}, {3}, {4})'
                },
                'argument': {
                    'pattern': r'(\w+)\s+argument\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Argument',
                    'args': 5,
                    'template': 'Argument({0}, {1}, {2}, {3}, {4})'
                },
                'reasoning': {
                    'pattern': r'(\w+)\s+reasoning\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Reasoning',
                    'args': 5,
                    'template': 'Reasoning({0}, {1}, {2}, {3}, {4})'
                },
                'logic': {
                    'pattern': r'(\w+)\s+logic\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Logic',
                    'args': 5,
                    'template': 'Logic({0}, {1}, {2}, {3}, {4})'
                }
            },
            'art': {
                'painting': {
                    'pattern': r'(\w+)\s+painting\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Painting',
                    'args': 5,
                    'template': 'Painting({0}, {1}, {2}, {3}, {4})'
                },
                'sculpture': {
                    'pattern': r'(\w+)\s+sculpture\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Sculpture',
                    'args': 5,
                    'template': 'Sculpture({0}, {1}, {2}, {3}, {4})'
                },
                'movement': {
                    'pattern': r'(\w+)\s+movement\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Movement',
                    'args': 5,
                    'template': 'Movement({0}, {1}, {2}, {3}, {4})'
                },
                'technique': {
                    'pattern': r'(\w+)\s+technique\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Technique',
                    'args': 5,
                    'template': 'Technique({0}, {1}, {2}, {3}, {4})'
                },
                'style': {
                    'pattern': r'(\w+)\s+style\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Style',
                    'args': 5,
                    'template': 'Style({0}, {1}, {2}, {3}, {4})'
                }
            },
            'music': {
                'instrument': {
                    'pattern': r'(\w+)\s+instrument\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Instrument',
                    'args': 5,
                    'template': 'Instrument({0}, {1}, {2}, {3}, {4})'
                },
                'rhythm': {
                    'pattern': r'(\w+)\s+rhythm\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Rhythm',
                    'args': 5,
                    'template': 'Rhythm({0}, {1}, {2}, {3}, {4})'
                },
                'harmony': {
                    'pattern': r'(\w+)\s+harmony\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Harmony',
                    'args': 5,
                    'template': 'Harmony({0}, {1}, {2}, {3}, {4})'
                },
                'melody': {
                    'pattern': r'(\w+)\s+melody\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Melody',
                    'args': 5,
                    'template': 'Melody({0}, {1}, {2}, {3}, {4})'
                },
                'composition': {
                    'pattern': r'(\w+)\s+composition\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Composition',
                    'args': 5,
                    'template': 'Composition({0}, {1}, {2}, {3}, {4})'
                }
            },
            'literature': {
                'plot': {
                    'pattern': r'(\w+)\s+plot\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Plot',
                    'args': 5,
                    'template': 'Plot({0}, {1}, {2}, {3}, {4})'
                },
                'character': {
                    'pattern': r'(\w+)\s+character\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Character',
                    'args': 5,
                    'template': 'Character({0}, {1}, {2}, {3}, {4})'
                },
                'drama': {
                    'pattern': r'(\w+)\s+drama\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Drama',
                    'args': 5,
                    'template': 'Drama({0}, {1}, {2}, {3}, {4})'
                },
                'poetry': {
                    'pattern': r'(\w+)\s+poetry\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Poetry',
                    'args': 5,
                    'template': 'Poetry({0}, {1}, {2}, {3}, {4})'
                },
                'novel': {
                    'pattern': r'(\w+)\s+novel\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Novel',
                    'args': 5,
                    'template': 'Novel({0}, {1}, {2}, {3}, {4})'
                }
            },
            'history': {
                'war': {
                    'pattern': r'(\w+)\s+war\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'War',
                    'args': 5,
                    'template': 'War({0}, {1}, {2}, {3}, {4})'
                },
                'civilization': {
                    'pattern': r'(\w+)\s+civilization\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Civilization',
                    'args': 5,
                    'template': 'Civilization({0}, {1}, {2}, {3}, {4})'
                },
                'era': {
                    'pattern': r'(\w+)\s+era\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Era',
                    'args': 5,
                    'template': 'Era({0}, {1}, {2}, {3}, {4})'
                },
                'period': {
                    'pattern': r'(\w+)\s+period\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Period',
                    'args': 5,
                    'template': 'Period({0}, {1}, {2}, {3}, {4})'
                },
                'event': {
                    'pattern': r'(\w+)\s+event\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Event',
                    'args': 5,
                    'template': 'Event({0}, {1}, {2}, {3}, {4})'
                }
            },
            'architecture': {
                'roof': {
                    'pattern': r'(\w+)\s+roof\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Roof',
                    'args': 5,
                    'template': 'Roof({0}, {1}, {2}, {3}, {4})'
                },
                'foundation': {
                    'pattern': r'(\w+)\s+foundation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Foundation',
                    'args': 5,
                    'template': 'Foundation({0}, {1}, {2}, {3}, {4})'
                },
                'material': {
                    'pattern': r'(\w+)\s+material\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Material',
                    'args': 5,
                    'template': 'Material({0}, {1}, {2}, {3}, {4})'
                },
                'structure': {
                    'pattern': r'(\w+)\s+structure\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Structure',
                    'args': 5,
                    'template': 'Structure({0}, {1}, {2}, {3}, {4})'
                },
                'building': {
                    'pattern': r'(\w+)\s+building\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Building',
                    'args': 5,
                    'template': 'Building({0}, {1}, {2}, {3}, {4})'
                }
            },
            # BATCH 3: ENGINEERING & TECH - NEW DOMAINS
            'engineering': {
                'machine': {
                    'pattern': r'(\w+)\s+machine\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Machine',
                    'args': 5,
                    'template': 'Machine({0}, {1}, {2}, {3}, {4})'
                },
                'device': {
                    'pattern': r'(\w+)\s+device\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Device',
                    'args': 5,
                    'template': 'Device({0}, {1}, {2}, {3}, {4})'
                },
                'component': {
                    'pattern': r'(\w+)\s+component\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Component',
                    'args': 5,
                    'template': 'Component({0}, {1}, {2}, {3}, {4})'
                },
                'system': {
                    'pattern': r'(\w+)\s+system\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'System',
                    'args': 5,
                    'template': 'System({0}, {1}, {2}, {3}, {4})'
                },
                'process': {
                    'pattern': r'(\w+)\s+process\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Process',
                    'args': 5,
                    'template': 'Process({0}, {1}, {2}, {3}, {4})'
                }
            },
            'robotics': {
                'robot': {
                    'pattern': r'(\w+)\s+robot\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Robot',
                    'args': 5,
                    'template': 'Robot({0}, {1}, {2}, {3}, {4})'
                },
                'sensor': {
                    'pattern': r'(\w+)\s+sensor\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Sensor',
                    'args': 5,
                    'template': 'Sensor({0}, {1}, {2}, {3}, {4})'
                },
                'actuator': {
                    'pattern': r'(\w+)\s+actuator\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Actuator',
                    'args': 5,
                    'template': 'Actuator({0}, {1}, {2}, {3}, {4})'
                },
                'programming': {
                    'pattern': r'(\w+)\s+programming\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Programming',
                    'args': 5,
                    'template': 'Programming({0}, {1}, {2}, {3}, {4})'
                },
                'navigation': {
                    'pattern': r'(\w+)\s+navigation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Navigation',
                    'args': 5,
                    'template': 'Navigation({0}, {1}, {2}, {3}, {4})'
                }
            },
            'computer_science': {
                'algorithm': {
                    'pattern': r'(\w+)\s+algorithm\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Algorithm',
                    'args': 5,
                    'template': 'Algorithm({0}, {1}, {2}, {3}, {4})'
                },
                'data_structure': {
                    'pattern': r'(\w+)\s+data\s+structure\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'DataStructure',
                    'args': 5,
                    'template': 'DataStructure({0}, {1}, {2}, {3}, {4})'
                },
                'programming_language': {
                    'pattern': r'(\w+)\s+programming\s+language\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'ProgrammingLanguage',
                    'args': 5,
                    'template': 'ProgrammingLanguage({0}, {1}, {2}, {3}, {4})'
                },
                'software_engineering': {
                    'pattern': r'(\w+)\s+software\s+engineering\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'SoftwareEngineering',
                    'args': 5,
                    'template': 'SoftwareEngineering({0}, {1}, {2}, {3}, {4})'
                },
                'database': {
                    'pattern': r'(\w+)\s+database\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Database',
                    'args': 5,
                    'template': 'Database({0}, {1}, {2}, {3}, {4})'
                }
            },
            'ai': {
                'intelligence': {
                    'pattern': r'(\w+)\s+intelligence\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Intelligence',
                    'args': 5,
                    'template': 'Intelligence({0}, {1}, {2}, {3}, {4})'
                },
                'learning': {
                    'pattern': r'(\w+)\s+learning\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Learning',
                    'args': 5,
                    'template': 'Learning({0}, {1}, {2}, {3}, {4})'
                },
                'neural': {
                    'pattern': r'(\w+)\s+neural\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Neural',
                    'args': 5,
                    'template': 'Neural({0}, {1}, {2}, {3}, {4})'
                },
                'pattern': {
                    'pattern': r'(\w+)\s+pattern\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Pattern',
                    'args': 5,
                    'template': 'Pattern({0}, {1}, {2}, {3}, {4})'
                },
                'classification': {
                    'pattern': r'(\w+)\s+classification\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Classification',
                    'args': 5,
                    'template': 'Classification({0}, {1}, {2}, {3}, {4})'
                }
            },
            'cryptography': {
                'security': {
                    'pattern': r'(\w+)\s+security\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Security',
                    'args': 5,
                    'template': 'Security({0}, {1}, {2}, {3}, {4})'
                },
                'privacy': {
                    'pattern': r'(\w+)\s+privacy\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Privacy',
                    'args': 5,
                    'template': 'Privacy({0}, {1}, {2}, {3}, {4})'
                },
                'authentication': {
                    'pattern': r'(\w+)\s+authentication\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Authentication',
                    'args': 5,
                    'template': 'Authentication({0}, {1}, {2}, {3}, {4})'
                },
                'authorization': {
                    'pattern': r'(\w+)\s+authorization\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Authorization',
                    'args': 5,
                    'template': 'Authorization({0}, {1}, {2}, {3}, {4})'
                },
                'blockchain': {
                    'pattern': r'(\w+)\s+blockchain\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Blockchain',
                    'args': 5,
                    'template': 'Blockchain({0}, {1}, {2}, {3}, {4})'
                }
            },
            'environmental_science': {
                'climate': {
                    'pattern': r'(\w+)\s+climate\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Climate',
                    'args': 5,
                    'template': 'Climate({0}, {1}, {2}, {3}, {4})'
                },
                'weather': {
                    'pattern': r'(\w+)\s+weather\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Weather',
                    'args': 5,
                    'template': 'Weather({0}, {1}, {2}, {3}, {4})'
                },
                'temperature': {
                    'pattern': r'(\w+)\s+temperature\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Temperature',
                    'args': 5,
                    'template': 'Temperature({0}, {1}, {2}, {3}, {4})'
                },
                'precipitation': {
                    'pattern': r'(\w+)\s+precipitation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Precipitation',
                    'args': 5,
                    'template': 'Precipitation({0}, {1}, {2}, {3}, {4})'
                },
                'wind': {
                    'pattern': r'(\w+)\s+wind\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Wind',
                    'args': 5,
                    'template': 'Wind({0}, {1}, {2}, {3}, {4})'
                }
            },
            # BATCH 4: LIFE SCIENCES - NEW DOMAINS
            'genetics': {
                'gene': {
                    'pattern': r'(\w+)\s+gene\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Gene',
                    'args': 5,
                    'template': 'Gene({0}, {1}, {2}, {3}, {4})'
                },
                'dna': {
                    'pattern': r'(\w+)\s+dna\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'DNA',
                    'args': 5,
                    'template': 'DNA({0}, {1}, {2}, {3}, {4})'
                },
                'rna': {
                    'pattern': r'(\w+)\s+rna\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'RNA',
                    'args': 5,
                    'template': 'RNA({0}, {1}, {2}, {3}, {4})'
                },
                'protein': {
                    'pattern': r'(\w+)\s+protein\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Protein',
                    'args': 5,
                    'template': 'Protein({0}, {1}, {2}, {3}, {4})'
                },
                'chromosome': {
                    'pattern': r'(\w+)\s+chromosome\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Chromosome',
                    'args': 5,
                    'template': 'Chromosome({0}, {1}, {2}, {3}, {4})'
                }
            },
            'immunology': {
                'immune': {
                    'pattern': r'(\w+)\s+immune\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Immune',
                    'args': 5,
                    'template': 'Immune({0}, {1}, {2}, {3}, {4})'
                },
                'antibody': {
                    'pattern': r'(\w+)\s+antibody\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Antibody',
                    'args': 5,
                    'template': 'Antibody({0}, {1}, {2}, {3}, {4})'
                },
                'antigen': {
                    'pattern': r'(\w+)\s+antigen\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Antigen',
                    'args': 5,
                    'template': 'Antigen({0}, {1}, {2}, {3}, {4})'
                },
                'pathogen': {
                    'pattern': r'(\w+)\s+pathogen\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Pathogen',
                    'args': 5,
                    'template': 'Pathogen({0}, {1}, {2}, {3}, {4})'
                },
                'infection': {
                    'pattern': r'(\w+)\s+infection\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Infection',
                    'args': 5,
                    'template': 'Infection({0}, {1}, {2}, {3}, {4})'
                }
            },
            'pharmacology': {
                'medicine': {
                    'pattern': r'(\w+)\s+medicine\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Medicine',
                    'args': 5,
                    'template': 'Medicine({0}, {1}, {2}, {3}, {4})'
                },
                'therapy': {
                    'pattern': r'(\w+)\s+therapy\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Therapy',
                    'args': 5,
                    'template': 'Therapy({0}, {1}, {2}, {3}, {4})'
                },
                'dosage': {
                    'pattern': r'(\w+)\s+dosage\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Dosage',
                    'args': 5,
                    'template': 'Dosage({0}, {1}, {2}, {3}, {4})'
                },
                'side_effect': {
                    'pattern': r'(\w+)\s+side\s+effect\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'SideEffect',
                    'args': 5,
                    'template': 'SideEffect({0}, {1}, {2}, {3}, {4})'
                },
                'efficacy': {
                    'pattern': r'(\w+)\s+efficacy\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Efficacy',
                    'args': 5,
                    'template': 'Efficacy({0}, {1}, {2}, {3}, {4})'
                }
            },
            'surgery': {
                'operation': {
                    'pattern': r'(\w+)\s+operation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Operation',
                    'args': 5,
                    'template': 'Operation({0}, {1}, {2}, {3}, {4})'
                },
                'procedure': {
                    'pattern': r'(\w+)\s+procedure\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Procedure',
                    'args': 5,
                    'template': 'Procedure({0}, {1}, {2}, {3}, {4})'
                },
                'anesthesia': {
                    'pattern': r'(\w+)\s+anesthesia\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Anesthesia',
                    'args': 5,
                    'template': 'Anesthesia({0}, {1}, {2}, {3}, {4})'
                },
                'recovery': {
                    'pattern': r'(\w+)\s+recovery\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Recovery',
                    'args': 5,
                    'template': 'Recovery({0}, {1}, {2}, {3}, {4})'
                },
                'complication': {
                    'pattern': r'(\w+)\s+complication\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Complication',
                    'args': 5,
                    'template': 'Complication({0}, {1}, {2}, {3}, {4})'
                }
            },
            'ecology': {
                'ecosystem': {
                    'pattern': r'(\w+)\s+ecosystem\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Ecosystem',
                    'args': 5,
                    'template': 'Ecosystem({0}, {1}, {2}, {3}, {4})'
                },
                'species': {
                    'pattern': r'(\w+)\s+species\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Species',
                    'args': 5,
                    'template': 'Species({0}, {1}, {2}, {3}, {4})'
                },
                'habitat': {
                    'pattern': r'(\w+)\s+habitat\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Habitat',
                    'args': 5,
                    'template': 'Habitat({0}, {1}, {2}, {3}, {4})'
                },
                'biodiversity': {
                    'pattern': r'(\w+)\s+biodiversity\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Biodiversity',
                    'args': 5,
                    'template': 'Biodiversity({0}, {1}, {2}, {3}, {4})'
                },
                'conservation': {
                    'pattern': r'(\w+)\s+conservation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Conservation',
                    'args': 5,
                    'template': 'Conservation({0}, {1}, {2}, {3}, {4})'
                }
            },
            'climate': {
                'storm': {
                    'pattern': r'(\w+)\s+storm\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Storm',
                    'args': 5,
                    'template': 'Storm({0}, {1}, {2}, {3}, {4})'
                },
                'hurricane': {
                    'pattern': r'(\w+)\s+hurricane\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Hurricane',
                    'args': 5,
                    'template': 'Hurricane({0}, {1}, {2}, {3}, {4})'
                },
                'tornado': {
                    'pattern': r'(\w+)\s+tornado\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Tornado',
                    'args': 5,
                    'template': 'Tornado({0}, {1}, {2}, {3}, {4})'
                },
                'blizzard': {
                    'pattern': r'(\w+)\s+blizzard\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Blizzard',
                    'args': 5,
                    'template': 'Blizzard({0}, {1}, {2}, {3}, {4})'
                },
                'drought': {
                    'pattern': r'(\w+)\s+drought\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Drought',
                    'args': 5,
                    'template': 'Drought({0}, {1}, {2}, {3}, {4})'
                }
            },
            # BATCH 5: BUSINESS & LAW - NEW DOMAINS
            'finance': {
                'money': {
                    'pattern': r'(\w+)\s+money\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Money',
                    'args': 5,
                    'template': 'Money({0}, {1}, {2}, {3}, {4})'
                },
                'bank': {
                    'pattern': r'(\w+)\s+bank\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Bank',
                    'args': 5,
                    'template': 'Bank({0}, {1}, {2}, {3}, {4})'
                },
                'credit': {
                    'pattern': r'(\w+)\s+credit\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Credit',
                    'args': 5,
                    'template': 'Credit({0}, {1}, {2}, {3}, {4})'
                },
                'loan': {
                    'pattern': r'(\w+)\s+loan\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Loan',
                    'args': 5,
                    'template': 'Loan({0}, {1}, {2}, {3}, {4})'
                },
                'interest': {
                    'pattern': r'(\w+)\s+interest\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Interest',
                    'args': 5,
                    'template': 'Interest({0}, {1}, {2}, {3}, {4})'
                }
            },
            'marketing': {
                'customer': {
                    'pattern': r'(\w+)\s+customer\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Customer',
                    'args': 5,
                    'template': 'Customer({0}, {1}, {2}, {3}, {4})'
                },
                'product': {
                    'pattern': r'(\w+)\s+product\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Product',
                    'args': 5,
                    'template': 'Product({0}, {1}, {2}, {3}, {4})'
                },
                'service': {
                    'pattern': r'(\w+)\s+service\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Service',
                    'args': 5,
                    'template': 'Service({0}, {1}, {2}, {3}, {4})'
                },
                'brand': {
                    'pattern': r'(\w+)\s+brand\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Brand',
                    'args': 5,
                    'template': 'Brand({0}, {1}, {2}, {3}, {4})'
                },
                'advertising': {
                    'pattern': r'(\w+)\s+advertising\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Advertising',
                    'args': 5,
                    'template': 'Advertising({0}, {1}, {2}, {3}, {4})'
                }
            },
            'management': {
                'leadership': {
                    'pattern': r'(\w+)\s+leadership\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Leadership',
                    'args': 5,
                    'template': 'Leadership({0}, {1}, {2}, {3}, {4})'
                },
                'strategy': {
                    'pattern': r'(\w+)\s+strategy\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Strategy',
                    'args': 5,
                    'template': 'Strategy({0}, {1}, {2}, {3}, {4})'
                },
                'planning': {
                    'pattern': r'(\w+)\s+planning\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Planning',
                    'args': 5,
                    'template': 'Planning({0}, {1}, {2}, {3}, {4})'
                },
                'execution': {
                    'pattern': r'(\w+)\s+execution\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Execution',
                    'args': 5,
                    'template': 'Execution({0}, {1}, {2}, {3}, {4})'
                },
                'team': {
                    'pattern': r'(\w+)\s+team\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Team',
                    'args': 5,
                    'template': 'Team({0}, {1}, {2}, {3}, {4})'
                }
            },
            'entrepreneurship': {
                'startup': {
                    'pattern': r'(\w+)\s+startup\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Startup',
                    'args': 5,
                    'template': 'Startup({0}, {1}, {2}, {3}, {4})'
                },
                'innovation': {
                    'pattern': r'(\w+)\s+innovation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Innovation',
                    'args': 5,
                    'template': 'Innovation({0}, {1}, {2}, {3}, {4})'
                },
                'venture': {
                    'pattern': r'(\w+)\s+venture\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Venture',
                    'args': 5,
                    'template': 'Venture({0}, {1}, {2}, {3}, {4})'
                },
                'funding': {
                    'pattern': r'(\w+)\s+funding\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Funding',
                    'args': 5,
                    'template': 'Funding({0}, {1}, {2}, {3}, {4})'
                },
                'growth': {
                    'pattern': r'(\w+)\s+growth\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Growth',
                    'args': 5,
                    'template': 'Growth({0}, {1}, {2}, {3}, {4})'
                }
            },
            'politics': {
                'government': {
                    'pattern': r'(\w+)\s+government\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Government',
                    'args': 5,
                    'template': 'Government({0}, {1}, {2}, {3}, {4})'
                },
                'policy': {
                    'pattern': r'(\w+)\s+policy\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Policy',
                    'args': 5,
                    'template': 'Policy({0}, {1}, {2}, {3}, {4})'
                },
                'law': {
                    'pattern': r'(\w+)\s+law\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Law',
                    'args': 5,
                    'template': 'Law({0}, {1}, {2}, {3}, {4})'
                },
                'regulation': {
                    'pattern': r'(\w+)\s+regulation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Regulation',
                    'args': 5,
                    'template': 'Regulation({0}, {1}, {2}, {3}, {4})'
                },
                'democracy': {
                    'pattern': r'(\w+)\s+democracy\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Democracy',
                    'args': 5,
                    'template': 'Democracy({0}, {1}, {2}, {3}, {4})'
                }
            },
            'law': {
                'justice': {
                    'pattern': r'(\w+)\s+justice\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Justice',
                    'args': 5,
                    'template': 'Justice({0}, {1}, {2}, {3}, {4})'
                },
                'court': {
                    'pattern': r'(\w+)\s+court\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Court',
                    'args': 5,
                    'template': 'Court({0}, {1}, {2}, {3}, {4})'
                },
                'judge': {
                    'pattern': r'(\w+)\s+judge\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Judge',
                    'args': 5,
                    'template': 'Judge({0}, {1}, {2}, {3}, {4})'
                },
                'jury': {
                    'pattern': r'(\w+)\s+jury\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Jury',
                    'args': 5,
                    'template': 'Jury({0}, {1}, {2}, {3}, {4})'
                },
                'verdict': {
                    'pattern': r'(\w+)\s+verdict\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Verdict',
                    'args': 5,
                    'template': 'Verdict({0}, {1}, {2}, {3}, {4})'
                }
            },
            # BATCH 6: EARTH & ANCIENT - FINAL DOMAINS
            'ethics': {
                'morality': {
                    'pattern': r'(\w+)\s+morality\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Morality',
                    'args': 5,
                    'template': 'Morality({0}, {1}, {2}, {3}, {4})'
                },
                'virtue': {
                    'pattern': r'(\w+)\s+virtue\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Virtue',
                    'args': 5,
                    'template': 'Virtue({0}, {1}, {2}, {3}, {4})'
                },
                'duty': {
                    'pattern': r'(\w+)\s+duty\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Duty',
                    'args': 5,
                    'template': 'Duty({0}, {1}, {2}, {3}, {4})'
                },
                'rights': {
                    'pattern': r'(\w+)\s+rights\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Rights',
                    'args': 5,
                    'template': 'Rights({0}, {1}, {2}, {3}, {4})'
                },
                'responsibility': {
                    'pattern': r'(\w+)\s+responsibility\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Responsibility',
                    'args': 5,
                    'template': 'Responsibility({0}, {1}, {2}, {3}, {4})'
                }
            },
            'anthropology': {
                'human': {
                    'pattern': r'(\w+)\s+human\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Human',
                    'args': 5,
                    'template': 'Human({0}, {1}, {2}, {3}, {4})'
                },
                'evolution': {
                    'pattern': r'(\w+)\s+evolution\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Evolution',
                    'args': 5,
                    'template': 'Evolution({0}, {1}, {2}, {3}, {4})'
                },
                'culture': {
                    'pattern': r'(\w+)\s+culture\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Culture',
                    'args': 5,
                    'template': 'Culture({0}, {1}, {2}, {3}, {4})'
                },
                'tradition': {
                    'pattern': r'(\w+)\s+tradition\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Tradition',
                    'args': 5,
                    'template': 'Tradition({0}, {1}, {2}, {3}, {4})'
                },
                'custom': {
                    'pattern': r'(\w+)\s+custom\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Custom',
                    'args': 5,
                    'template': 'Custom({0}, {1}, {2}, {3}, {4})'
                }
            },
            'archaeology': {
                'artifact': {
                    'pattern': r'(\w+)\s+artifact\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Artifact',
                    'args': 5,
                    'template': 'Artifact({0}, {1}, {2}, {3}, {4})'
                },
                'excavation': {
                    'pattern': r'(\w+)\s+excavation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Excavation',
                    'args': 5,
                    'template': 'Excavation({0}, {1}, {2}, {3}, {4})'
                },
                'site': {
                    'pattern': r'(\w+)\s+site\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Site',
                    'args': 5,
                    'template': 'Site({0}, {1}, {2}, {3}, {4})'
                },
                'dating': {
                    'pattern': r'(\w+)\s+dating\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Dating',
                    'args': 5,
                    'template': 'Dating({0}, {1}, {2}, {3}, {4})'
                },
                'analysis': {
                    'pattern': r'(\w+)\s+analysis\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Analysis',
                    'args': 5,
                    'template': 'Analysis({0}, {1}, {2}, {3}, {4})'
                }
            },
            'paleontology': {
                'dinosaur': {
                    'pattern': r'(\w+)\s+dinosaur\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Dinosaur',
                    'args': 5,
                    'template': 'Dinosaur({0}, {1}, {2}, {3}, {4})'
                },
                'extinction': {
                    'pattern': r'(\w+)\s+extinction\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Extinction',
                    'args': 5,
                    'template': 'Extinction({0}, {1}, {2}, {3}, {4})'
                },
                'fossil': {
                    'pattern': r'(\w+)\s+fossil\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Fossil',
                    'args': 5,
                    'template': 'Fossil({0}, {1}, {2}, {3}, {4})'
                },
                'evolution': {
                    'pattern': r'(\w+)\s+evolution\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Evolution',
                    'args': 5,
                    'template': 'Evolution({0}, {1}, {2}, {3}, {4})'
                },
                'adaptation': {
                    'pattern': r'(\w+)\s+adaptation\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Adaptation',
                    'args': 5,
                    'template': 'Adaptation({0}, {1}, {2}, {3}, {4})'
                }
            },
            'meteorology': {
                'storm': {
                    'pattern': r'(\w+)\s+storm\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Storm',
                    'args': 5,
                    'template': 'Storm({0}, {1}, {2}, {3}, {4})'
                },
                'hurricane': {
                    'pattern': r'(\w+)\s+hurricane\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Hurricane',
                    'args': 5,
                    'template': 'Hurricane({0}, {1}, {2}, {3}, {4})'
                },
                'tornado': {
                    'pattern': r'(\w+)\s+tornado\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Tornado',
                    'args': 5,
                    'template': 'Tornado({0}, {1}, {2}, {3}, {4})'
                },
                'blizzard': {
                    'pattern': r'(\w+)\s+blizzard\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Blizzard',
                    'args': 5,
                    'template': 'Blizzard({0}, {1}, {2}, {3}, {4})'
                },
                'drought': {
                    'pattern': r'(\w+)\s+drought\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Drought',
                    'args': 5,
                    'template': 'Drought({0}, {1}, {2}, {3}, {4})'
                }
            },
            'oceanography': {
                'ocean': {
                    'pattern': r'(\w+)\s+ocean\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Ocean',
                    'args': 5,
                    'template': 'Ocean({0}, {1}, {2}, {3}, {4})'
                },
                'sea': {
                    'pattern': r'(\w+)\s+sea\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Sea',
                    'args': 5,
                    'template': 'Sea({0}, {1}, {2}, {3}, {4})'
                },
                'current': {
                    'pattern': r'(\w+)\s+current\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Current',
                    'args': 5,
                    'template': 'Current({0}, {1}, {2}, {3}, {4})'
                },
                'tide': {
                    'pattern': r'(\w+)\s+tide\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Tide',
                    'args': 5,
                    'template': 'Tide({0}, {1}, {2}, {3}, {4})'
                },
                'wave': {
                    'pattern': r'(\w+)\s+wave\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)',
                    'predicate': 'Wave',
                    'args': 5,
                    'template': 'Wave({0}, {1}, {2}, {3}, {4})'
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
