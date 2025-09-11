#!/usr/bin/env python
"""
HAK/GAL Governance System Monitor
Real-time monitoring dashboard for system health and performance
"""

import sqlite3
import json
import time
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import threading

# Try to import optional dependencies
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

class GovernanceMonitor:
    """Monitor for HAK/GAL Governance System"""
    
    def __init__(self, db_path: str = "hexagonal_kb.db"):
        self.db_path = db_path
        self.metrics_history = []
        self.max_history = 100
        
    def get_database_stats(self) -> Dict:
        """Get current database statistics"""
        if not Path(self.db_path).exists():
            return {"error": "Database not found"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        try:
            # Basic counts
            stats['total_facts'] = cursor.execute("SELECT COUNT(*) FROM facts_extended").fetchone()[0]
            stats['unique_predicates'] = cursor.execute("SELECT COUNT(DISTINCT predicate) FROM facts_extended").fetchone()[0]
            stats['unique_sources'] = cursor.execute("SELECT COUNT(DISTINCT source) FROM facts_extended").fetchone()[0]
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM facts_extended 
                WHERE created_at > datetime('now', '-1 hour')
            """)
            stats['facts_last_hour'] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM facts_extended 
                WHERE created_at > datetime('now', '-24 hours')
            """)
            stats['facts_last_24h'] = cursor.fetchone()[0]
            
            # Top predicates
            cursor.execute("""
                SELECT predicate, COUNT(*) as count 
                FROM facts_extended 
                GROUP BY predicate 
                ORDER BY count DESC 
                LIMIT 5
            """)
            stats['top_predicates'] = cursor.fetchall()
            
            # Database configuration
            stats['wal_mode'] = cursor.execute("PRAGMA journal_mode").fetchone()[0]
            stats['page_size'] = cursor.execute("PRAGMA page_size").fetchone()[0]
            stats['cache_size'] = cursor.execute("PRAGMA cache_size").fetchone()[0]
            
            # Database size
            cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
            stats['db_size_bytes'] = cursor.fetchone()[0]
            
            # Integrity check
            cursor.execute("PRAGMA quick_check")
            stats['integrity'] = cursor.fetchone()[0]
            
        except Exception as e:
            stats['error'] = str(e)
        finally:
            conn.close()
        
        stats['timestamp'] = datetime.now().isoformat()
        return stats
    
    def get_audit_stats(self) -> Dict:
        """Get audit log statistics"""
        audit_file = Path("audit_log.jsonl")
        stats = {}
        
        if not audit_file.exists():
            stats['status'] = 'No audit log found'
            return stats
        
        try:
            entries = []
            with open(audit_file, 'r') as f:
                for line in f:
                    try:
                        entries.append(json.loads(line))
                    except:
                        continue
            
            stats['total_entries'] = len(entries)
            stats['status'] = 'Active'
            
            if entries:
                # Check chain integrity
                valid_chain = True
                for i in range(1, len(entries)):
                    if entries[i].get('prev_hash') != entries[i-1].get('entry_hash'):
                        valid_chain = False
                        break
                
                stats['chain_integrity'] = 'Valid' if valid_chain else 'Broken'
                stats['latest_entry'] = entries[-1].get('ts', 'Unknown')
                
                # Event types
                event_types = {}
                for entry in entries:
                    event = entry.get('event', 'unknown')
                    event_types[event] = event_types.get(event, 0) + 1
                stats['event_types'] = event_types
                
        except Exception as e:
            stats['error'] = str(e)
        
        return stats
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        metrics = {}
        
        # Get database stats
        db_stats = self.get_database_stats()
        
        if 'error' not in db_stats:
            metrics['facts_per_minute'] = db_stats.get('facts_last_hour', 0) / 60
            metrics['facts_per_hour'] = db_stats.get('facts_last_hour', 0)
            metrics['facts_per_day'] = db_stats.get('facts_last_24h', 0)
            
            # Database health
            metrics['db_size_mb'] = db_stats.get('db_size_bytes', 0) / 1024 / 1024
            metrics['wal_enabled'] = db_stats.get('wal_mode') == 'wal'
            metrics['integrity_ok'] = db_stats.get('integrity') == 'ok'
        
        # Store in history
        self.metrics_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
        
        # Keep only recent history
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
        
        return metrics
    
    def print_console_dashboard(self):
        """Print dashboard to console"""
        # Clear screen (works on Windows and Unix)
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
        db_stats = self.get_database_stats()
        audit_stats = self.get_audit_stats()
        perf_metrics = self.get_performance_metrics()
        
        print("="*70)
        print("📊 HAK/GAL GOVERNANCE SYSTEM MONITOR".center(70))
        print("="*70)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(70))
        print("="*70)
        
        # Database Section
        print("\n📁 DATABASE STATUS")
        print("-"*35)
        if 'error' not in db_stats:
            print(f"Total Facts:        {db_stats.get('total_facts', 0):,}")
            print(f"Unique Predicates:  {db_stats.get('unique_predicates', 0)}")
            print(f"Database Size:      {perf_metrics.get('db_size_mb', 0):.2f} MB")
            print(f"WAL Mode:           {'✅ Enabled' if perf_metrics.get('wal_enabled') else '❌ Disabled'}")
            print(f"Integrity:          {'✅ OK' if perf_metrics.get('integrity_ok') else '❌ Failed'}")
        else:
            print(f"❌ Error: {db_stats.get('error')}")
        
        # Performance Section
        print("\n📈 PERFORMANCE METRICS")
        print("-"*35)
        print(f"Facts/Hour:         {perf_metrics.get('facts_per_hour', 0):.1f}")
        print(f"Facts/Day:          {perf_metrics.get('facts_per_day', 0):.1f}")
        
        # Top Predicates
        if db_stats.get('top_predicates'):
            print("\n🏷️ TOP PREDICATES")
            print("-"*35)
            for pred, count in db_stats['top_predicates']:
                bar = '█' * min(20, int(count / max(1, db_stats['total_facts']) * 100))
                print(f"{pred:20} {bar} {count}")
        
        # Audit Section
        print("\n📝 AUDIT LOG")
        print("-"*35)
        print(f"Total Entries:      {audit_stats.get('total_entries', 0)}")
        print(f"Chain Integrity:    {audit_stats.get('chain_integrity', 'Unknown')}")
        if audit_stats.get('latest_entry'):
            print(f"Latest Entry:       {audit_stats['latest_entry'][:19]}")
        
        # Event Types
        if audit_stats.get('event_types'):
            print("\nEvent Types:")
            for event, count in sorted(audit_stats['event_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {event:30} {count:5}")
        
        print("\n" + "="*70)
        print("Press Ctrl+C to exit | Updates every 5 seconds")
    
    def run_web_dashboard(self, port: int = 8080):
        """Run Streamlit web dashboard"""
        if not HAS_STREAMLIT:
            print("❌ Streamlit not installed. Install with: pip install streamlit")
            print("Falling back to console mode...")
            self.run_console_monitor()
            return
        
        # Create streamlit app
        st.set_page_config(
            page_title="HAK/GAL Monitor",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 HAK/GAL Governance System Monitor")
        
        # Auto-refresh
        st.button("🔄 Refresh")
        
        # Get current stats
        db_stats = self.get_database_stats()
        audit_stats = self.get_audit_stats()
        perf_metrics = self.get_performance_metrics()
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Facts", f"{db_stats.get('total_facts', 0):,}")
        with col2:
            st.metric("Database Size", f"{perf_metrics.get('db_size_mb', 0):.2f} MB")
        with col3:
            st.metric("Facts/Hour", f"{perf_metrics.get('facts_per_hour', 0):.1f}")
        with col4:
            st.metric("WAL Mode", "✅" if perf_metrics.get('wal_enabled') else "❌")
        
        # More details in tabs
        tab1, tab2, tab3 = st.tabs(["Database", "Audit Log", "Performance"])
        
        with tab1:
            st.json(db_stats)
        
        with tab2:
            st.json(audit_stats)
        
        with tab3:
            st.json(perf_metrics)
    
    def run_console_monitor(self, interval: int = 5):
        """Run console monitoring loop"""
        print("Starting console monitor...")
        print(f"Updates every {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.print_console_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nMonitor stopped.")
            sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description='HAK/GAL Governance System Monitor')
    parser.add_argument('--port', type=int, default=8080, help='Port for web dashboard')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    parser.add_argument('--web', action='store_true', help='Start web dashboard (requires streamlit)')
    parser.add_argument('--db', default='hexagonal_kb.db', help='Database path')
    
    args = parser.parse_args()
    
    monitor = GovernanceMonitor(db_path=args.db)
    
    if args.web:
        monitor.run_web_dashboard(port=args.port)
    else:
        monitor.run_console_monitor(interval=args.interval)

if __name__ == "__main__":
    main()
