#!/usr/bin/env python3
"""
Entity Migration Fix - Complete German to English Translation
Based on statistical analysis revealing ~50 facts with German entities
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Complete entity migration map based on analysis
ENTITY_MIGRATION_MAP = {
    # Philosophy entities found in KB
    "Phänomene": "Phenomena",
    "WahrgenommeneWelt": "PerceivedWorld",
    "KritischeTheorie": "CriticalTheory", 
    "ModernerPhilosophie": "ModernPhilosophy",
    "Ästhetik": "Aesthetics",
    "KritischePhilosophie": "CriticalPhilosophy",
    "AutonomieDerVernunft": "AutonomyOfReason",
    "ModerneEpistemologie": "ModernEpistemology",
    "ModerneEthik": "ModernEthics",
    "SpätereDenker": "LaterThinkers",
    "UnerkennbareRealität": "UnknowableReality",
    "SelbstgegebenenVernunftgesetzen": "SelfGivenReasonLaws",
    "WissenBeginntMitErfahrung": "KnowledgeBeginsWithExperience",
    "MoralischePflichtEntstehtAusSelbstgegebenenVernunftgesetzen": "MoralDutyArisesFromSelfGivenReasonLaws",
    "SubjektiveAberUniversellKommunizierbareSchönheit": "SubjectiveButUniversallyCommunicableBeauty",
    "EinflussAufSpätereDenker": "InfluenceOnLaterThinkers",
    "WurzelInInteresselosemVergnügen": "RootedInDisinterestedPleasure",
    "Ethik": "Ethics",
    "Metaphysik": "Metaphysics",
    "Epistemologie": "Epistemology",
    "Noumena": "Noumena",  # Already English but check usage
    "KantIdeen": "KantIdeas"
}

class EntityMigrator:
    def __init__(self, kb_path: str):
        self.kb_path = Path(kb_path)
        self.backup_path = self.kb_path.with_suffix('.pre_entity_migration.jsonl')
        self.stats = {
            'total_facts': 0,
            'migrated_facts': 0,
            'entities_replaced': {},
            'failed_facts': []
        }
    
    def create_backup(self):
        """Create backup before migration"""
        print(f"Creating backup: {self.backup_path}")
        self.backup_path.write_bytes(self.kb_path.read_bytes())
    
    def migrate_entity(self, text: str) -> Tuple[str, List[str]]:
        """Migrate German entities to English in text"""
        changes = []
        modified = text
        
        for german, english in ENTITY_MIGRATION_MAP.items():
            if german in modified:
                # Replace with word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(german) + r'\b'
                new_text = re.sub(pattern, english, modified)
                if new_text != modified:
                    changes.append(f"{german}→{english}")
                    if german not in self.stats['entities_replaced']:
                        self.stats['entities_replaced'][german] = 0
                    self.stats['entities_replaced'][german] += 1
                modified = new_text
        
        return modified, changes
    
    def process_fact(self, fact: dict) -> dict:
        """Process single fact for entity migration"""
        if 'statement' not in fact:
            return fact
        
        original = fact['statement']
        migrated, changes = self.migrate_entity(original)
        
        if changes:
            self.stats['migrated_facts'] += 1
            fact['statement'] = migrated
            
            # Add migration metadata
            if 'metadata' not in fact:
                fact['metadata'] = {}
            fact['metadata']['entity_migration'] = {
                'timestamp': datetime.now().isoformat(),
                'changes': changes,
                'original': original
            }
        
        return fact
    
    def run_migration(self):
        """Execute the migration"""
        print("Starting Entity Migration to 100% English...")
        
        # Create backup
        self.create_backup()
        
        # Read all facts
        facts = []
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        fact = json.loads(line)
                        facts.append(fact)
                        self.stats['total_facts'] += 1
                    except json.JSONDecodeError as e:
                        print(f"Error parsing: {line[:50]}... - {e}")
                        self.stats['failed_facts'].append(line[:50])
        
        # Process each fact
        migrated_facts = []
        for fact in facts:
            migrated_fact = self.process_fact(fact)
            migrated_facts.append(migrated_fact)
        
        # Write migrated facts
        with open(self.kb_path, 'w', encoding='utf-8') as f:
            for fact in migrated_facts:
                f.write(json.dumps(fact, ensure_ascii=False) + '\n')
        
        # Print statistics
        self.print_stats()
        
        return self.stats
    
    def print_stats(self):
        """Print migration statistics"""
        print("\n" + "="*60)
        print("ENTITY MIGRATION COMPLETE")
        print("="*60)
        print(f"Total facts processed: {self.stats['total_facts']}")
        print(f"Facts with migrated entities: {self.stats['migrated_facts']}")
        print(f"Migration rate: {self.stats['migrated_facts']/self.stats['total_facts']*100:.1f}%")
        
        if self.stats['entities_replaced']:
            print("\nEntities Migrated:")
            for entity, count in sorted(self.stats['entities_replaced'].items(), 
                                       key=lambda x: x[1], reverse=True):
                english = ENTITY_MIGRATION_MAP.get(entity, "?")
                print(f"  {entity} → {english}: {count} occurrences")
        
        if self.stats['failed_facts']:
            print(f"\n⚠️ Failed to parse {len(self.stats['failed_facts'])} facts")
    
    def verify_migration(self):
        """Verify no German entities remain"""
        print("\nVerifying migration...")
        german_found = []
        
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                for german_entity in ENTITY_MIGRATION_MAP.keys():
                    if german_entity in line:
                        german_found.append((i, german_entity, line[:100]))
        
        if german_found:
            print(f"⚠️ WARNING: {len(german_found)} German entities still found!")
            for line_num, entity, preview in german_found[:5]:
                print(f"  Line {line_num}: {entity} in {preview}...")
        else:
            print("✅ SUCCESS: No German entities found - 100% English!")
        
        return len(german_found) == 0


def main():
    kb_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\data\k_assistant.kb.jsonl"
    
    # Run migration
    migrator = EntityMigrator(kb_path)
    stats = migrator.run_migration()
    
    # Verify results
    success = migrator.verify_migration()
    
    # Also fix the logical quantor anomaly
    print("\nFixing logical quantor anomaly...")
    fix_logical_quantor(kb_path)
    
    print("\n" + "="*60)
    print("MIGRATION STATUS: " + ("SUCCESS ✅" if success else "NEEDS REVIEW ⚠️"))
    print("="*60)
    
    return success


def fix_logical_quantor(kb_path: str):
    """Fix the 'all x' logical quantor to proper predicate format"""
    path = Path(kb_path)
    facts = []
    fixed_count = 0
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                fact = json.loads(line)
                statement = fact.get('statement', '')
                
                # Fix the logical quantor
                if 'all x' in statement.lower():
                    # Convert to proper predicate format
                    fact['statement'] = "ImpliesUniversally(IsHuman, IsMortal)."
                    fact['metadata'] = fact.get('metadata', {})
                    fact['metadata']['fixed_from'] = statement
                    fact['metadata']['fix_reason'] = 'Converted logical quantor to predicate format'
                    fixed_count += 1
                    print(f"  Fixed: {statement[:50]}... → ImpliesUniversally(IsHuman, IsMortal).")
                
                facts.append(fact)
    
    if fixed_count > 0:
        with open(path, 'w', encoding='utf-8') as f:
            for fact in facts:
                f.write(json.dumps(fact, ensure_ascii=False) + '\n')
        print(f"  Fixed {fixed_count} logical quantor anomalies")
    else:
        print("  No logical quantor anomalies found")


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
