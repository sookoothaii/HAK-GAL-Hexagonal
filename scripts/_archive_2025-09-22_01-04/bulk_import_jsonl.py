#!/usr/bin/env python3
"""
HAK-GAL Bulk Import JSONL to SQLite
====================================
Importiert JSONL-Dateien in die HAK-GAL Knowledge Base
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class BulkImporter:
    """Import JSONL files into HAK-GAL SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = "D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db"
        
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.stats = {
            'processed': 0,
            'imported': 0,
            'duplicates': 0,
            'errors': 0
        }
    
    def import_jsonl(self, jsonl_path: str) -> Dict:
        """Import a JSONL file into the database"""
        
        if not Path(jsonl_path).exists():
            raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")
        
        print(f"[IMPORT] Starting import from: {jsonl_path}")
        self.stats = {'processed': 0, 'imported': 0, 'duplicates': 0, 'errors': 0}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                self.stats['processed'] += 1
                
                try:
                    # Parse JSONL line
                    data = json.loads(line.strip())
                    
                    # Handle different JSONL formats
                    statement = None
                    
                    # Format 1: {"statement": "Fact(...)"}
                    if 'statement' in data:
                        statement = data['statement']
                    
                    # Format 2: {"fact": "Fact(...)"}
                    elif 'fact' in data:
                        statement = data['fact']
                    
                    # Format 3: {"text": "Fact(...)"}
                    elif 'text' in data:
                        statement = data['text']
                    
                    # Format 4: Direct string
                    elif isinstance(data, str):
                        statement = data
                    
                    if not statement:
                        print(f"Line {line_num}: No statement found in: {data}")
                        self.stats['errors'] += 1
                        continue
                    
                    # Ensure statement ends with period
                    if not statement.endswith('.'):
                        statement += '.'
                    
                    # Extract metadata
                    context = data.get('context', {}) if isinstance(data, dict) else {}
                    metadata = data.get('metadata', {}) if isinstance(data, dict) else {}
                    source = data.get('source', jsonl_path) if isinstance(data, dict) else jsonl_path
                    confidence = data.get('confidence', 1.0) if isinstance(data, dict) else 1.0
                    
                    # Convert to JSON strings
                    context_json = json.dumps(context) if context else '{}'
                    metadata_json = json.dumps(metadata) if metadata else '{}'
                    
                    # Try to insert
                    try:
                        cursor.execute("""
                            INSERT INTO facts (statement, context, fact_metadata, source, confidence)
                            VALUES (?, ?, ?, ?, ?)
                        """, (statement, context_json, metadata_json, source, confidence))
                        self.stats['imported'] += 1
                        
                        if self.stats['imported'] % 100 == 0:
                            print(f"[PROGRESS] Imported {self.stats['imported']} facts...")
                            
                    except sqlite3.IntegrityError:
                        # Duplicate
                        self.stats['duplicates'] += 1
                        
                except json.JSONDecodeError as e:
                    print(f"Line {line_num}: Invalid JSON - {e}")
                    self.stats['errors'] += 1
                    
                except Exception as e:
                    print(f"Line {line_num}: Error - {e}")
                    self.stats['errors'] += 1
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("IMPORT COMPLETE")
        print("=" * 60)
        print(f"✅ Imported: {self.stats['imported']}")
        print(f"⚠️  Duplicates: {self.stats['duplicates']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"📊 Total processed: {self.stats['processed']}")
        print("=" * 60)
        
        return self.stats
    
    def export_to_jsonl(self, output_path: str = None, limit: int = None) -> str:
        """Export database to JSONL format"""
        
        if not output_path:
            output_path = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT statement, context, fact_metadata, source, confidence FROM facts"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        
        count = 0
        with open(output_path, 'w', encoding='utf-8') as f:
            for row in cursor:
                statement, context, metadata, source, confidence = row
                
                # Parse JSON strings
                try:
                    context_dict = json.loads(context) if context else {}
                except:
                    context_dict = {}
                
                try:
                    metadata_dict = json.loads(metadata) if metadata else {}
                except:
                    metadata_dict = {}
                
                # Create JSONL entry
                entry = {
                    'statement': statement,
                    'context': context_dict,
                    'metadata': metadata_dict,
                    'source': source,
                    'confidence': confidence
                }
                
                f.write(json.dumps(entry) + '\n')
                count += 1
        
        conn.close()
        
        print(f"[EXPORT] Exported {count} facts to: {output_path}")
        return output_path

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HAK-GAL Bulk Import/Export Tool')
    parser.add_argument('action', choices=['import', 'export'], help='Action to perform')
    parser.add_argument('file', nargs='?', help='File to import from or export to')
    parser.add_argument('--db', help='Database path', default=None)
    parser.add_argument('--limit', type=int, help='Limit number of facts (export only)')
    
    args = parser.parse_args()
    
    importer = BulkImporter(args.db)
    
    if args.action == 'import':
        if not args.file:
            print("Error: Please specify a JSONL file to import")
            sys.exit(1)
        importer.import_jsonl(args.file)
        
    elif args.action == 'export':
        output = args.file or None
        importer.export_to_jsonl(output, args.limit)

if __name__ == "__main__":
    main()