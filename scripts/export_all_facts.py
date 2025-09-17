#!/usr/bin/env python
"""
Export All Facts to Project Hub
================================
Exports the complete knowledge base according to project_hub rules
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import hashlib

print("="*60)
print("KNOWLEDGE BASE EXPORT TO PROJECT HUB")
print("="*60)

# Configuration
db_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
hub_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\project_hub")
export_dir = hub_path / "knowledge_base_exports"

# Create export directory
export_dir.mkdir(parents=True, exist_ok=True)

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get total count
cursor.execute("SELECT COUNT(*) FROM facts")
total_count = cursor.fetchone()[0]
print(f"\n📊 Database Statistics:")
print(f"   Total Facts: {total_count:,}")

# Create timestamp for this export
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Export formats
exports = {}

# 1. Export as structured JSON
print(f"\n📝 Exporting to JSON format...")
cursor.execute("SELECT id, statement, metadata FROM facts ORDER BY id")
facts_json = []
for row in cursor.fetchall():
    fact_id, statement, metadata = row
    facts_json.append({
        'id': fact_id,
        'statement': statement,
        'metadata': json.loads(metadata) if metadata else {}
    })

json_file = export_dir / f"kb_export_{timestamp}.json"
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump({
        'export_date': datetime.now().isoformat(),
        'total_facts': total_count,
        'facts': facts_json
    }, f, indent=2, ensure_ascii=False)
print(f"   ✅ Saved: {json_file.name}")

# 2. Export as plain text (statements only)
print(f"\n📄 Exporting to plain text...")
cursor.execute("SELECT statement FROM facts ORDER BY id")
text_file = export_dir / f"kb_statements_{timestamp}.txt"
with open(text_file, 'w', encoding='utf-8') as f:
    for (statement,) in cursor.fetchall():
        f.write(statement + '\n')
print(f"   ✅ Saved: {text_file.name}")

# 3. Export by domain/predicate
print(f"\n📂 Exporting by domain...")
cursor.execute("""
    SELECT 
        SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
        COUNT(*) as count
    FROM facts
    WHERE statement LIKE '%(%'
    GROUP BY predicate
    ORDER BY count DESC
""")

predicates = cursor.fetchall()
domain_dir = export_dir / f"by_domain_{timestamp}"
domain_dir.mkdir(exist_ok=True)

for predicate, count in predicates[:20]:  # Top 20 predicates
    if predicate:
        cursor.execute(
            "SELECT statement FROM facts WHERE statement LIKE ? ORDER BY id",
            (f"{predicate}(%",)
        )
        
        pred_file = domain_dir / f"{predicate}_{count}_facts.txt"
        with open(pred_file, 'w', encoding='utf-8') as f:
            for (statement,) in cursor.fetchall():
                f.write(statement + '\n')
        
        print(f"   ✅ {predicate}: {count} facts")

# 4. Create a summary/manifest
print(f"\n📋 Creating manifest...")
manifest = {
    'export_date': datetime.now().isoformat(),
    'total_facts': total_count,
    'files': {
        'json': json_file.name,
        'text': text_file.name,
        'domain_directory': domain_dir.name
    },
    'statistics': {
        'predicates': len(predicates),
        'top_predicates': [
            {'name': p, 'count': c} 
            for p, c in predicates[:10] if p
        ]
    },
    'checksums': {
        'json': hashlib.md5(open(json_file, 'rb').read()).hexdigest(),
        'text': hashlib.md5(open(text_file, 'rb').read()).hexdigest()
    }
}

manifest_file = export_dir / f"manifest_{timestamp}.json"
with open(manifest_file, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)
print(f"   ✅ Saved: {manifest_file.name}")

# 5. Create latest symlink/copy
latest_json = export_dir / "kb_latest.json"
latest_text = export_dir / "kb_latest.txt"
latest_manifest = export_dir / "manifest_latest.json"

# Copy to latest files
import shutil
shutil.copy2(json_file, latest_json)
shutil.copy2(text_file, latest_text)
shutil.copy2(manifest_file, latest_manifest)

print(f"\n✅ Created 'latest' links for easy access")

# Close database
conn.close()

print("\n" + "="*60)
print("EXPORT COMPLETE")
print("="*60)
print(f"\n📁 Export Location: {export_dir}")
print(f"\nFiles created:")
print(f"  • kb_export_{timestamp}.json - Complete JSON export")
print(f"  • kb_statements_{timestamp}.txt - Plain text statements")
print(f"  • by_domain_{timestamp}/ - Organized by predicate")
print(f"  • manifest_{timestamp}.json - Export metadata")
print(f"\nLatest versions:")
print(f"  • kb_latest.json")
print(f"  • kb_latest.txt")
print(f"  • manifest_latest.json")
print("\n" + "="*60)

# Project Hub Integration
print("\n🔗 PROJECT HUB INTEGRATION")
print("="*60)

# Create project hub snapshot
snapshot_data = {
    'timestamp': datetime.now().isoformat(),
    'title': f'Knowledge Base Snapshot - {total_count} Facts',
    'description': f'Complete export of HAK-GAL knowledge base with {total_count} facts',
    'files': {
        'json': str(json_file),
        'text': str(text_file),
        'manifest': str(manifest_file)
    },
    'metrics': {
        'total_facts': total_count,
        'predicates': len(predicates),
        'export_size_mb': {
            'json': json_file.stat().st_size / (1024*1024),
            'text': text_file.stat().st_size / (1024*1024)
        }
    }
}

hub_snapshot = hub_path / f"kb_snapshot_{timestamp}.json"
with open(hub_snapshot, 'w', encoding='utf-8') as f:
    json.dump(snapshot_data, f, indent=2)

print(f"✅ Project Hub Snapshot created: {hub_snapshot.name}")
print(f"\nAll {total_count:,} facts exported successfully!")
print("="*60)
