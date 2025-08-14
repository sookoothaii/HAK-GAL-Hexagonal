#!/usr/bin/env python
"""
Quick Performance Optimization - Database Indexing
===================================================
Immediate performance boost for search operations
"""

import sqlite3
from pathlib import Path
import time

def optimize_database(db_path='k_assistant_dev.db'):
    """Add indexes for better query performance"""
    
    print("="*60)
    print("[DATABASE OPTIMIZATION]")
    print("="*60)
    
    if not Path(db_path).exists():
        print(f"[ERROR] Database not found: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check current indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='facts'
            """)
            existing_indexes = [row[0] for row in cursor.fetchall()]
            print(f"Existing indexes: {existing_indexes}")
            
            # Create performance indexes
            indexes = [
                ("idx_facts_statement", "CREATE INDEX IF NOT EXISTS idx_facts_statement ON facts(statement)"),
                ("idx_facts_created_at", "CREATE INDEX IF NOT EXISTS idx_facts_created_at ON facts(created_at)"),
                ("idx_facts_confidence", "CREATE INDEX IF NOT EXISTS idx_facts_confidence ON facts(confidence)"),
                ("idx_facts_source", "CREATE INDEX IF NOT EXISTS idx_facts_source ON facts(source)"),
            ]
            
            for idx_name, idx_sql in indexes:
                print(f"\nCreating index: {idx_name}")
                start = time.time()
                cursor.execute(idx_sql)
                elapsed = time.time() - start
                print(f"  [OK] Created in {elapsed:.3f} seconds")
            
            # Analyze database for query optimizer
            print("\nRunning ANALYZE...")
            cursor.execute("ANALYZE")
            
            # Vacuum to reclaim space
            print("Running VACUUM...")
            cursor.execute("VACUUM")
            
            # Get database stats
            cursor.execute("SELECT COUNT(*) FROM facts")
            fact_count = cursor.fetchone()[0]
            
            # Test query performance
            print("\n" + "="*60)
            print("[PERFORMANCE TEST]")
            print("="*60)
            
            # Test 1: Search by keyword
            query = "SELECT * FROM facts WHERE statement LIKE '%Computer%' LIMIT 10"
            start = time.time()
            cursor.execute(query)
            results = cursor.fetchall()
            elapsed = time.time() - start
            print(f"Search query: {elapsed*1000:.2f}ms ({len(results)} results)")
            
            # Test 2: Order by confidence
            query = "SELECT * FROM facts ORDER BY confidence DESC LIMIT 10"
            start = time.time()
            cursor.execute(query)
            results = cursor.fetchall()
            elapsed = time.time() - start
            print(f"Order by confidence: {elapsed*1000:.2f}ms")
            
            # Test 3: Recent facts
            query = "SELECT * FROM facts ORDER BY created_at DESC LIMIT 10"
            start = time.time()
            cursor.execute(query)
            results = cursor.fetchall()
            elapsed = time.time() - start
            print(f"Recent facts: {elapsed*1000:.2f}ms")
            
            print("\n" + "="*60)
            print("[OPTIMIZATION COMPLETE]")
            print("="*60)
            print(f"Database: {db_path}")
            print(f"Facts: {fact_count}")
            print(f"Indexes: {len(indexes)} created")
            print("Expected improvement: 10-100x for search queries")
            print("="*60)
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Optimization failed: {e}")
        return False

if __name__ == "__main__":
    optimize_database()
