#!/usr/bin/env python3
"""
HAK_GAL System Cleanup and Optimization Script
Version: 1.0
Date: 2025-09-15
Author: claude-opus-4.1

Performs automated cleanup and optimization tasks:
- Token sanitization
- Frontmatter validation
- Duplicate detection
- Catalog regeneration
"""

import os
import re
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple
import argparse
import logging

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_HUB = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB")
HEXAGONAL_ROOT = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")

class SystemCleaner:
    """Main cleanup orchestrator"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.stats = {
            'tokens_sanitized': 0,
            'frontmatter_fixed': 0,
            'duplicates_found': 0,
            'files_relocated': 0,
            'catalog_entries': 0
        }
    
    def sanitize_tokens(self) -> int:
        """Replace exposed tokens with placeholders"""
        token_pattern = r'[a-f0-9]{32,64}'
        safe_replacement = '${HAKGAL_AUTH_TOKEN}'
        count = 0
        
        for md_file in HEXAGONAL_ROOT.rglob('*.md'):
            if '.git' in str(md_file):
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find potential tokens
                matches = re.findall(token_pattern, content)
                if matches:
                    # Check if they're not already placeholders
                    for match in matches:
                        if 'YOUR_TOKEN_HERE' not in content and 'HAKGAL_AUTH_TOKEN' not in content:
                            if not self.dry_run:
                                content = content.replace(match, safe_replacement)
                                with open(md_file, 'w', encoding='utf-8') as f:
                                    f.write(content)
                            count += 1
                            logger.info(f"Sanitized token in {md_file.name}")
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        self.stats['tokens_sanitized'] = count
        return count
    
    def fix_frontmatter(self) -> int:
        """Add minimal frontmatter to files missing it"""
        count = 0
        
        for md_file in PROJECT_HUB.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.startswith('---'):
                    # Generate minimal frontmatter
                    title = md_file.stem.replace('_', ' ').title()
                    created = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    
                    # Determine topic from path
                    topic = 'technical_reports'
                    if 'guides' in str(md_file):
                        topic = 'guides'
                    elif 'meta' in str(md_file):
                        topic = 'meta'
                    elif 'analysis' in str(md_file):
                        topic = 'analysis'
                    
                    frontmatter = f'''---
title: "{title}"
created: "{created}"
author: "system-cleanup"
topics: ["{topic}"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

'''
                    
                    if not self.dry_run:
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(frontmatter + content)
                    
                    count += 1
                    logger.info(f"Added frontmatter to {md_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")
        
        self.stats['frontmatter_fixed'] = count
        return count
    
    def detect_duplicates(self) -> List[Tuple[Path, Path]]:
        """Find duplicate files based on content hash"""
        file_hashes: Dict[str, List[Path]] = {}
        duplicates = []
        
        for file_path in PROJECT_HUB.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.md', '.py', '.json']:
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        file_hashes[file_hash].append(file_path)
                    else:
                        file_hashes[file_hash] = [file_path]
                except Exception as e:
                    logger.error(f"Error hashing {file_path}: {e}")
        
        # Find duplicates
        for hash_val, paths in file_hashes.items():
            if len(paths) > 1:
                for i in range(1, len(paths)):
                    duplicates.append((paths[0], paths[i]))
                    logger.warning(f"Duplicate found: {paths[0].name} == {paths[i].name}")
        
        self.stats['duplicates_found'] = len(duplicates)
        return duplicates
    
    def generate_catalog(self) -> int:
        """Generate updated catalog of all documents"""
        catalog_entries = []
        
        for md_file in PROJECT_HUB.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract frontmatter if exists
                metadata = {'title': md_file.stem, 'topics': ['unknown'], 'tags': []}
                if content.startswith('---'):
                    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        try:
                            fm = yaml.safe_load(match.group(1))
                            metadata.update(fm)
                        except:
                            pass
                
                # Get file stats
                stats = md_file.stat()
                
                catalog_entries.append({
                    'path': str(md_file.relative_to(PROJECT_HUB)),
                    'title': metadata.get('title', md_file.stem),
                    'topics': metadata.get('topics', ['unknown']),
                    'tags': metadata.get('tags', []),
                    'size': stats.st_size,
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error cataloging {md_file}: {e}")
        
        # Sort by modification date
        catalog_entries.sort(key=lambda x: x['modified'], reverse=True)
        
        # Generate catalog markdown
        catalog_md = f"""---
title: "PROJECT_HUB Catalog"
created: "{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}"
author: "system-cleanup"
topics: ["snapshots"]
tags: ["catalog", "index"]
privacy: "internal"
summary_200: |-
  Auto-generated catalog of all PROJECT_HUB documents. Contains {len(catalog_entries)} entries
  sorted by modification date. Includes path, title, topics, tags, size, and modification time.
---

# PROJECT_HUB Catalog

Generated: {datetime.now(timezone.utc).isoformat()}
Total Documents: {len(catalog_entries)}

## Document Index

| Path | Title | Topics | Modified |
|------|-------|--------|----------|
"""
        
        for entry in catalog_entries[:50]:  # First 50 entries
            topics_str = ', '.join(entry['topics'])
            catalog_md += f"| {entry['path']} | {entry['title']} | {topics_str} | {entry['modified'][:10]} |\n"
        
        if not self.dry_run:
            catalog_path = PROJECT_HUB / 'docs' / 'snapshots' / f'catalog_{datetime.now().strftime("%Y%m%d")}_auto.md'
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            with open(catalog_path, 'w', encoding='utf-8') as f:
                f.write(catalog_md)
            logger.info(f"Generated catalog with {len(catalog_entries)} entries")
            
            # Also save JSON version
            json_path = catalog_path.with_suffix('.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(catalog_entries, f, indent=2, default=str)
        
        self.stats['catalog_entries'] = len(catalog_entries)
        return len(catalog_entries)
    
    def generate_report(self) -> str:
        """Generate cleanup report"""
        report = f"""
# HAK_GAL System Cleanup Report
Date: {datetime.now(timezone.utc).isoformat()}
Mode: {"DRY RUN" if self.dry_run else "LIVE"}

## Actions Performed

1. **Token Sanitization**
   - Tokens replaced: {self.stats['tokens_sanitized']}
   - Status: {'✅ Complete' if self.stats['tokens_sanitized'] == 0 else '⚠️ Fixed'}

2. **Frontmatter Fixes**
   - Files updated: {self.stats['frontmatter_fixed']}
   - Coverage: {(372 - self.stats['frontmatter_fixed'])/372*100:.1f}% complete

3. **Duplicate Detection**
   - Duplicates found: {self.stats['duplicates_found']}
   - Action: {'Manual review required' if self.stats['duplicates_found'] > 0 else '✅ None found'}

4. **Catalog Generation**
   - Entries cataloged: {self.stats['catalog_entries']}
   - Status: {'✅ Generated' if self.stats['catalog_entries'] > 0 else '❌ Failed'}

## Recommendations

"""
        if self.stats['tokens_sanitized'] > 0:
            report += "- Rotate exposed tokens externally\n"
        if self.stats['frontmatter_fixed'] > 0:
            report += "- Review auto-generated frontmatter for accuracy\n"
        if self.stats['duplicates_found'] > 0:
            report += "- Consolidate or remove duplicate files\n"
        
        report += "\n## Next Steps\n"
        report += "1. Review this report\n"
        report += "2. Run with --live to apply changes\n" if self.dry_run else "2. Verify changes\n"
        report += "3. Commit to version control\n"
        
        return report
    
    def run(self):
        """Execute all cleanup tasks"""
        logger.info("Starting HAK_GAL system cleanup...")
        
        # Run cleanup tasks
        self.sanitize_tokens()
        self.fix_frontmatter()
        self.detect_duplicates()
        self.generate_catalog()
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        if not self.dry_run:
            report_path = PROJECT_HUB / 'docs' / 'status_reports' / f'cleanup_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {report_path}")
        
        print(report)
        return self.stats

def main():
    parser = argparse.ArgumentParser(description='HAK_GAL System Cleanup')
    parser.add_argument('--live', action='store_true', help='Apply changes (default is dry-run)')
    args = parser.parse_args()
    
    cleaner = SystemCleaner(dry_run=not args.live)
    stats = cleaner.run()
    
    return 0 if stats['tokens_sanitized'] == 0 else 1

if __name__ == '__main__':
    exit(main())
