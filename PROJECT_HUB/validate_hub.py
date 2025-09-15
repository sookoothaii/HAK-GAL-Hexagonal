#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJECT_HUB Document Validator/Linter v2.0
Enforces routing and frontmatter rules based on routing_table.json
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class HubValidator:
    def __init__(self, hub_path: str = "."):
        self.hub_path = Path(hub_path)
        self.routing_table_path = self.hub_path / "docs" / "meta" / "routing_table.json"
        self.routing = None
        self.errors = []
        self.warnings = []
        self.stats = {
            "files_checked": 0,
            "valid_files": 0,
            "files_with_errors": 0,
            "files_with_warnings": 0,
            "total_errors": 0,
            "total_warnings": 0
        }
        
    def load_routing_table(self) -> bool:
        """Load the routing table from meta/"""
        if not self.routing_table_path.exists():
            self.errors.append("❌ CRITICAL: routing_table.json not found!")
            return False
        
        try:
            with open(self.routing_table_path, 'r') as f:
                self.routing = json.load(f)
                return True
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ CRITICAL: Invalid JSON in routing_table.json: {e}")
            return False
    
    def extract_frontmatter(self, file_path: Path) -> Optional[Dict]:
        """Extract YAML frontmatter from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return None
        
        if not content.startswith('---'):
            return None
        
        try:
            end_idx = content.index('---', 3)
            fm_text = content[3:end_idx].strip()
            return yaml.safe_load(fm_text)
        except:
            return None
    
    def validate_document(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """Validate a single document"""
        errors = []
        warnings = []
        rel_path = file_path.relative_to(self.hub_path)
        
        # Determine if file is legacy (before cutoff date)
        cutoff_date = datetime(2025, 9, 15, 0, 0, 0)  # System runs in September 2025
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        is_legacy = file_mtime < cutoff_date
        
        # Extract frontmatter
        fm = self.extract_frontmatter(file_path)
        if not fm:
            if is_legacy:
                # Legacy files don't need frontmatter - skip validation
                return errors, warnings
            else:
                # New files MUST have frontmatter
                errors.append("❌ New file (created after 2025-01-28) MUST have frontmatter")
                return errors, warnings
        
        # Check required fields
        required_fields = ['title', 'created', 'author', 'topics', 'tags', 'privacy', 'summary_200']
        for field in required_fields:
            if field not in fm:
                if field in ['title', 'topics', 'summary_200']:
                    errors.append(f"❌ Missing required field '{field}'")
                else:
                    warnings.append(f"⚠️ Missing recommended field '{field}'")
        
        # Validate topics field
        if 'topics' in fm:
            if not isinstance(fm['topics'], list):
                errors.append("❌ 'topics' must be an array, not string")
            elif len(fm['topics']) == 0:
                errors.append("❌ 'topics' array is empty")
            else:
                primary_topic = fm['topics'][0]
                
                # Check if topic is deprecated
                if 'deprecated_topics' in self.routing and primary_topic in self.routing['deprecated_topics']:
                    errors.append(f"❌ Topic '{primary_topic}' is deprecated! {self.routing['deprecated_topics'][primary_topic]['note']}")
                
                # Check if topic is in routing table
                if primary_topic in self.routing['routing_table']:
                    expected_path = self.routing['routing_table'][primary_topic]
                    actual_path = str(rel_path.parent).replace('\\', '/') + '/'
                    
                    # Normalize paths
                    if actual_path == './':
                        actual_path = ''
                    if actual_path.startswith('./'):
                        actual_path = actual_path[2:]
                    
                    if actual_path != expected_path and actual_path != expected_path.rstrip('/'):
                        errors.append(f"📁 Wrong folder! Topic '{primary_topic}' → should be in {expected_path}, but is in {actual_path}")
                
                # Check for forbidden new topics
                if 'lint' in self.routing and 'forbid_new_topic' in self.routing['lint']:
                    if primary_topic in self.routing['lint']['forbid_new_topic']:
                        # Check if file is new (simple heuristic: check created date if available)
                        if 'created' in fm:
                            try:
                                created_date = datetime.fromisoformat(fm['created'].replace('Z', '+00:00'))
                                cutoff_date = datetime.fromisoformat('2025-01-27T00:00:00+00:00')
                                if created_date > cutoff_date:
                                    errors.append(f"❌ Cannot use topic '{primary_topic}' for new documents (created after 2025-01-27)")
                            except:
                                pass
        
        # Check for deprecated 'topic' (singular)
        if 'topic' in fm:
            errors.append("❌ Deprecated 'topic' (singular) field - use 'topics' array instead")
        
        # Validate summary_200
        if 'summary_200' in fm:
            word_count = len(str(fm['summary_200']).split())
            if word_count > 200:
                warnings.append(f"📝 summary_200 too long: {word_count} words (max 200)")
        
        # Check tags for cpp usage
        if 'tags' in fm and isinstance(fm['tags'], list):
            # This is correct - cpp should be a tag, not a topic
            pass
        
        # Check if rationale is provided for analysis folder
        if 'analysis/' in str(rel_path):
            if 'rationale' not in fm:
                warnings.append("⚠️ Files in analysis/ should include 'rationale' field explaining placement")
        
        return errors, warnings
    
    def validate_all(self):
        """Validate all markdown files in PROJECT_HUB"""
        # Find all .md files
        md_files = list(self.hub_path.rglob("*.md"))
        
        for file_path in md_files:
            # Skip certain paths
            skip_patterns = ['node_modules', '.git', '__pycache__', 'venv', '.venv']
            if any(pattern in str(file_path) for pattern in skip_patterns):
                continue
            
            self.stats["files_checked"] += 1
            file_errors, file_warnings = self.validate_document(file_path)
            
            if file_errors or file_warnings:
                rel_path = file_path.relative_to(self.hub_path)
                
                if file_errors:
                    self.stats["files_with_errors"] += 1
                    self.stats["total_errors"] += len(file_errors)
                    print(f"\n📄 {rel_path}")
                    for error in file_errors:
                        print(f"   {error}")
                
                if file_warnings:
                    self.stats["files_with_warnings"] += 1
                    self.stats["total_warnings"] += len(file_warnings)
                    if not file_errors:  # Only print path if not already printed
                        print(f"\n📄 {rel_path}")
                    for warning in file_warnings:
                        print(f"   {warning}")
            else:
                self.stats["valid_files"] += 1
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print("\n🚨 CRITICAL ERRORS:")
            for error in self.errors:
                print(f"   {error}")
        
        print(f"\n📈 Statistics:")
        print(f"   Files checked:      {self.stats['files_checked']}")
        print(f"   Valid files:        {self.stats['valid_files']}")
        print(f"   Files with errors:  {self.stats['files_with_errors']}")
        print(f"   Files with warnings:{self.stats['files_with_warnings']}")
        print(f"   Total errors:       {self.stats['total_errors']}")
        print(f"   Total warnings:     {self.stats['total_warnings']}")
        
        if self.stats["total_errors"] == 0:
            print("\n✅ No errors found! All documents follow routing rules.")
        else:
            print(f"\n❌ Found {self.stats['total_errors']} errors that need fixing.")
        
        if self.stats["total_warnings"] > 0:
            print(f"⚠️  Found {self.stats['total_warnings']} warnings to review.")

def main():
    """Main entry point"""
    print("🔍 PROJECT_HUB Document Validator v2.0")
    print("=" * 60)
    
    validator = HubValidator()
    
    if not validator.load_routing_table():
        print("Cannot proceed without routing_table.json")
        return 1
    
    print(f"✅ Loaded routing table v{validator.routing.get('schemaVersion', '?')}")
    print(f"   Last updated: {validator.routing.get('updated', 'unknown')}")
    
    validator.validate_all()
    validator.print_summary()
    
    # Return exit code based on errors
    return 1 if validator.stats["total_errors"] > 0 else 0

if __name__ == "__main__":
    exit(main())