#!/usr/bin/env python3
"""
Creative Fact Generator for V6 Autopilot
Generates diverse, interesting facts for knowledge base expansion
"""

import random
import json
from pathlib import Path
from typing import List

class CreativeFactGenerator:
    """Generates diverse facts across multiple domains"""
    
    def __init__(self):
        # Diverse predicates
        self.predicates = [
            "IsA", "HasPart", "Causes", "Prevents", "Enables",
            "RequiresFor", "ProducedBy", "UsedIn", "FoundIn", "RelatedTo",
            "DependsOn", "Influences", "Transforms", "Connects", "Supports",
            "SubfieldOf", "ComponentOf", "CharacteristicOf", "PropertyOf", "MemberOf"
        ]
        
        # Rich entity sets across domains
        self.entities = {
            'technology': [
                'QuantumComputer', 'NeuralNetwork', 'Blockchain', 'CloudComputing',
                'MachineLearning', 'DeepLearning', 'Cryptocurrency', 'IoT',
                'VirtualReality', 'AugmentedReality', 'BigData', 'CyberSecurity',
                'ArtificialIntelligence', 'RoboticProcess', 'EdgeComputing'
            ],
            'science': [
                'DNA', 'RNA', 'Protein', 'Cell', 'Atom', 'Molecule', 'Electron',
                'Photon', 'Quantum', 'Entropy', 'Energy', 'Matter', 'Gravity',
                'Evolution', 'Ecosystem', 'Biodiversity', 'Climate', 'Genome'
            ],
            'philosophy': [
                'Consciousness', 'Ethics', 'Logic', 'Metaphysics', 'Epistemology',
                'Aesthetics', 'Morality', 'Reality', 'Truth', 'Knowledge',
                'Wisdom', 'Justice', 'Freedom', 'Virtue', 'Reason'
            ],
            'medicine': [
                'Antibody', 'Vaccine', 'Immunity', 'Metabolism', 'Hormone',
                'Neurotransmitter', 'Enzyme', 'Receptor', 'Pathogen', 'Diagnosis',
                'Treatment', 'Prevention', 'Therapy', 'Surgery', 'Medicine'
            ],
            'business': [
                'Strategy', 'Innovation', 'Marketing', 'Finance', 'Operations',
                'Supply Chain', 'Customer', 'Product', 'Service', 'Revenue',
                'Profit', 'Investment', 'Risk', 'Growth', 'Competition'
            ],
            'nature': [
                'Ocean', 'Forest', 'Mountain', 'River', 'Desert', 'Atmosphere',
                'Biosphere', 'Ecosystem', 'Species', 'Habitat', 'Climate',
                'Weather', 'Season', 'Cycle', 'Resource'
            ]
        }
        
        # Relationships between domains
        self.cross_domain_rules = [
            ('technology', 'science', ['DependsOn', 'UsedIn', 'Enables']),
            ('medicine', 'science', ['RequiresFor', 'BasedOn', 'Utilizes']),
            ('business', 'technology', ['Adopts', 'Leverages', 'InvestsIn']),
            ('philosophy', 'science', ['Questions', 'Analyzes', 'Interprets']),
            ('nature', 'science', ['StudiedBy', 'Influences', 'Provides'])
        ]
    
    def generate_intra_domain_fact(self, domain: str) -> str:
        """Generate fact within a single domain"""
        entities = self.entities[domain]
        predicate = random.choice(self.predicates)
        entity1 = random.choice(entities)
        entity2 = random.choice([e for e in entities if e != entity1])
        return f"{predicate}({entity1}, {entity2})."
    
    def generate_cross_domain_fact(self) -> str:
        """Generate fact across domains"""
        rule = random.choice(self.cross_domain_rules)
        domain1, domain2, predicates = rule
        entity1 = random.choice(self.entities[domain1])
        entity2 = random.choice(self.entities[domain2])
        predicate = random.choice(predicates + self.predicates[:5])
        return f"{predicate}({entity1}, {entity2})."
    
    def generate_complex_fact(self) -> str:
        """Generate more complex relationships"""
        templates = [
            "EnablesThrough({e1}, {e2}, {e3})",
            "TransformsInto({e1}, {e2})",
            "CombinesWith({e1}, {e2}, {e3})",
            "PrerequisiteFor({e1}, {e2})",
            "CompetesWIth({e1}, {e2})",
        ]
        
        template = random.choice(templates)
        all_entities = []
        for entities in self.entities.values():
            all_entities.extend(entities)
        
        selected = random.sample(all_entities, 3)
        fact = template.format(e1=selected[0], e2=selected[1], e3=selected[2])
        return fact + "."
    
    def generate_batch(self, count: int, diversity: float = 0.7) -> List[str]:
        """Generate batch of diverse facts
        
        Args:
            count: Number of facts to generate
            diversity: 0.0-1.0, higher = more cross-domain
        """
        facts = []
        seen = set()
        
        for _ in range(count * 2):  # Generate extra to filter duplicates
            rand = random.random()
            
            if rand < (1 - diversity):
                # Intra-domain fact
                domain = random.choice(list(self.entities.keys()))
                fact = self.generate_intra_domain_fact(domain)
            elif rand < 0.9:
                # Cross-domain fact
                fact = self.generate_cross_domain_fact()
            else:
                # Complex fact
                fact = self.generate_complex_fact()
            
            if fact not in seen:
                seen.add(fact)
                facts.append(fact)
                
            if len(facts) >= count:
                break
        
        return facts[:count]
    
    def generate_themed_batch(self, theme: str, count: int) -> List[str]:
        """Generate facts around a specific theme"""
        themes = {
            'ai_revolution': [
                'Enables(MachineLearning, Automation).',
                'Transforms(DeepLearning, Industry).',
                'RequiresFor(BigData, AI_Training).',
                'ProducedBy(NeuralNetwork, Research).',
                'Influences(AI, Society).',
            ],
            'biological_systems': [
                'HasPart(Cell, Mitochondria).',
                'Produces(DNA, Protein).',
                'Regulates(Enzyme, Metabolism).',
                'Protects(Antibody, Organism).',
                'Enables(Evolution, Adaptation).',
            ],
            'digital_transformation': [
                'Enables(CloudComputing, Scalability).',
                'RequiresFor(Blockchain, Cryptocurrency).',
                'Transforms(IoT, Manufacturing).',
                'Supports(5G, EdgeComputing).',
                'Accelerates(Automation, Productivity).',
            ]
        }
        
        if theme in themes:
            base = themes[theme]
            # Extend with variations
            extended = []
            for fact in base:
                extended.append(fact)
                # Create variations
                parts = fact.replace('.', '').replace('(', ' ').replace(')', '').split()
                if len(parts) >= 3:
                    # Swap entities sometimes
                    if random.random() > 0.5:
                        new_fact = f"{parts[0]}({parts[2]}, {parts[1]})."
                        extended.append(new_fact)
            
            return random.sample(extended * (count // len(extended) + 1), count)
        else:
            return self.generate_batch(count)


def main():
    """Generate facts and save them for v6_autopilot"""
    generator = CreativeFactGenerator()
    
    # Generate diverse batches
    batches = {
        'general_diverse': generator.generate_batch(100, diversity=0.8),
        'technology_focused': generator.generate_batch(50, diversity=0.3),
        'ai_themed': generator.generate_themed_batch('ai_revolution', 30),
        'bio_themed': generator.generate_themed_batch('biological_systems', 30),
        'digital_themed': generator.generate_themed_batch('digital_transformation', 30)
    }
    
    # Save all facts
    output_dir = Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/creative_facts')
    output_dir.mkdir(exist_ok=True)
    
    all_facts = []
    for name, facts in batches.items():
        # Save individual batch
        batch_file = output_dir / f'{name}.txt'
        batch_file.write_text('\n'.join(facts), encoding='utf-8')
        print(f"✅ Saved {len(facts)} facts to {batch_file.name}")
        all_facts.extend(facts)
    
    # Save combined file for easy import
    combined_file = output_dir / 'all_creative_facts.jsonl'
    with combined_file.open('w', encoding='utf-8') as f:
        for fact in all_facts:
            f.write(json.dumps({'statement': fact}) + '\n')
    
    print(f"\n✅ Total: {len(all_facts)} creative facts generated")
    print(f"📁 Location: {output_dir}")
    
    # Sample output
    print("\n📝 Sample facts generated:")
    for fact in random.sample(all_facts, min(10, len(all_facts))):
        print(f"  • {fact}")
    
    print("\n💡 To use with v6_autopilot:")
    print("1. Copy facts to logs/ directory as v6_boost_log_creative.jsonl")
    print("2. Select 'logs' as source when running v6_autopilot")
    print("3. Or modify v6_autopilot to read from creative_facts/")


if __name__ == '__main__':
    main()
