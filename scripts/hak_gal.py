#!/usr/bin/env python
"""
HAK/GAL System Launcher - Haupteinstiegspunkt
"""

import sys
import argparse
import subprocess
import os
from pathlib import Path

# Setze Pfade
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src_hexagonal"))

def run_load_test(facts=1000, workers=10, mode='direct'):
    """Führe Load Test aus"""
    print(f"🚀 Starting Load Test: {facts} facts, {workers} workers, mode={mode}")
    subprocess.run([
        sys.executable, 
        "load_test_governance.py",
        "--facts", str(facts),
        "--workers", str(workers),
        "--mode", mode
    ])

def run_comprehensive_test():
    """Führe umfassende Tests aus"""
    print("🧪 Running Comprehensive Tests...")
    subprocess.run([sys.executable, "test_governance_comprehensive.py"])

def run_repair():
    """Führe Reparatur aus"""
    print("🔧 Running System Repair...")
    subprocess.run([sys.executable, "fix_governance_issues.py"])

def run_monitor(port=8080):
    """Starte Monitoring Dashboard"""
    print(f"📊 Starting Monitoring Dashboard on port {port}...")
    
    # Erstelle einfaches Monitoring-Skript wenn nicht vorhanden
    monitor_file = BASE_DIR / "governance_monitor.py"
    if not monitor_file.exists():
        create_monitor_script(monitor_file)
    
    subprocess.run([sys.executable, str(monitor_file), "--port", str(port)])

def create_monitor_script(path):
    """Erstelle einfaches Monitoring-Skript"""
    monitor_code = '''#!/usr/bin/env python
"""Simple Monitoring Dashboard for HAK/GAL System"""

import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
import argparse

def get_stats():
    """Get current system statistics"""
    db_path = "hexagonal_kb.db"
    
    if not Path(db_path).exists():
        return {"error": "Database not found"}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Get basic counts
    stats['total_facts'] = cursor.execute("SELECT COUNT(*) FROM facts_extended").fetchone()[0]
    stats['unique_predicates'] = cursor.execute("SELECT COUNT(DISTINCT predicate) FROM facts_extended").fetchone()[0]
    
    # Get recent facts
    cursor.execute("SELECT * FROM facts_extended ORDER BY created_at DESC LIMIT 5")
    stats['recent_facts'] = cursor.fetchall()
    
    # Get WAL mode
    stats['wal_mode'] = cursor.execute("PRAGMA journal_mode").fetchone()[0]
    
    # Get database size
    cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
    stats['db_size_bytes'] = cursor.fetchone()[0]
    
    conn.close()
    
    return stats

def print_dashboard():
    """Print dashboard to console"""
    stats = get_stats()
    
    print("\\n" + "="*60)
    print("📊 HAK/GAL GOVERNANCE SYSTEM MONITOR")
    print("="*60)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Database: hexagonal_kb.db (WAL: {stats.get('wal_mode', 'unknown')})")
    print(f"📈 Total Facts: {stats.get('total_facts', 0)}")
    print(f"🏷️ Unique Predicates: {stats.get('unique_predicates', 0)}")
    print(f"💾 Database Size: {stats.get('db_size_bytes', 0) / 1024 / 1024:.2f} MB")
    print("="*60)
    
    return stats

def main():
    parser = argparse.ArgumentParser(description='HAK/GAL System Monitor')
    parser.add_argument('--port', type=int, default=8080, help='Port for web dashboard')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    parser.add_argument('--web', action='store_true', help='Start web dashboard')
    
    args = parser.parse_args()
    
    if args.web:
        print(f"Web dashboard would start on port {args.port}")
        print("(Web interface not yet implemented - using console mode)")
    
    print(f"Starting console monitor (updates every {args.interval}s)...")
    print("Press Ctrl+C to stop\\n")
    
    try:
        while True:
            print_dashboard()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\\nMonitor stopped.")

if __name__ == "__main__":
    main()
'''
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(monitor_code)
    print(f"✅ Created monitoring script: {path}")

def show_status():
    """Zeige System-Status"""
    print("\n" + "="*60)
    print("🏛️ HAK/GAL GOVERNANCE SYSTEM STATUS")
    print("="*60)
    
    # Check database
    db_path = BASE_DIR / "hexagonal_kb.db"
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get stats
        facts_count = cursor.execute("SELECT COUNT(*) FROM facts_extended").fetchone()[0]
        wal_mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
        
        print(f"✅ Database: {db_path.name}")
        print(f"   - Facts: {facts_count}")
        print(f"   - WAL Mode: {wal_mode}")
        
        conn.close()
    else:
        print("❌ Database not found")
    
    # Check key files
    key_files = [
        "load_test_governance.py",
        "test_governance_comprehensive.py", 
        "fix_governance_issues.py",
        "src_hexagonal/application/transactional_governance_engine.py"
    ]
    
    print("\n📁 Key Files:")
    for file in key_files:
        path = BASE_DIR / file
        if path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
    
    print("="*60)
    print("\nAvailable commands:")
    print("  python hak_gal.py test        - Run comprehensive tests")
    print("  python hak_gal.py load        - Run load test (1000 facts)")
    print("  python hak_gal.py repair      - Repair system issues")
    print("  python hak_gal.py monitor     - Start monitoring dashboard")
    print("  python hak_gal.py status      - Show this status")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description='HAK/GAL Governance System')
    parser.add_argument('command', nargs='?', default='status',
                       choices=['test', 'load', 'repair', 'monitor', 'status'],
                       help='Command to run')
    parser.add_argument('--facts', type=int, default=1000, help='Number of facts for load test')
    parser.add_argument('--workers', type=int, default=10, help='Number of workers for load test')
    parser.add_argument('--mode', default='direct', choices=['direct', 'governance', 'both'],
                       help='Test mode')
    parser.add_argument('--port', type=int, default=8080, help='Port for monitoring dashboard')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        run_comprehensive_test()
    elif args.command == 'load':
        run_load_test(args.facts, args.workers, args.mode)
    elif args.command == 'repair':
        run_repair()
    elif args.command == 'monitor':
        run_monitor(args.port)
    else:  # status
        show_status()

if __name__ == "__main__":
    # Imports for status check
    import sqlite3
    
    main()
