#!/usr/bin/env python3
"""
Initialize and check HAK_GAL Knowledge Base
Diagnose why facts aren't loading
"""

import sqlite3
import json
from pathlib import Path

def check_database():
    """Check SQLite database content"""
    
    print("=" * 60)
    print("Checking HAK_GAL Database")
    print("=" * 60)
    
    db_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.db")
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    print(f"✅ Database found: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for facts table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTables in database: {[t[0] for t in tables]}")
        
        # Try to count facts
        try:
            cursor.execute("SELECT COUNT(*) FROM facts;")
            count = cursor.fetchone()[0]
            print(f"✅ Facts in database: {count}")
            
            # Show sample facts
            if count > 0:
                cursor.execute("SELECT statement FROM facts LIMIT 5;")
                sample_facts = cursor.fetchall()
                print("\nSample facts:")
                for i, fact in enumerate(sample_facts, 1):
                    print(f"  {i}. {fact[0]}")
        except sqlite3.OperationalError as e:
            print(f"❌ No 'facts' table found: {e}")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")


def check_jsonl_file():
    """Check JSONL knowledge base file"""
    
    print("\n" + "=" * 60)
    print("Checking JSONL Knowledge Base")
    print("=" * 60)
    
    jsonl_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
    
    if not jsonl_path.exists():
        print(f"❌ JSONL file not found: {jsonl_path}")
        return
    
    print(f"✅ JSONL file found: {jsonl_path}")
    
    try:
        facts = []
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    facts.append(json.loads(line))
        
        print(f"✅ Facts in JSONL: {len(facts)}")
        
        if facts:
            print("\nSample facts from JSONL:")
            for i, fact in enumerate(facts[:5], 1):
                if isinstance(fact, dict):
                    statement = fact.get('statement', fact.get('fact', str(fact)))
                else:
                    statement = str(fact)
                print(f"  {i}. {statement[:80]}...")
                
    except Exception as e:
        print(f"❌ JSONL error: {e}")


def create_test_facts():
    """Create test facts if database is empty"""
    
    print("\n" + "=" * 60)
    print("Creating Test Facts (if needed)")
    print("=" * 60)
    
    db_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create facts table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement TEXT NOT NULL UNIQUE,
                confidence REAL DEFAULT 1.0,
                source TEXT DEFAULT 'test',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Check if we have facts
        cursor.execute("SELECT COUNT(*) FROM facts;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("No facts found. Creating test facts...")
            
            test_facts = [
                "HexagonalArchitecture(Promotes, CleanSeparation).",
                "CleanArchitecture(Uses, PortsAndAdapters).",
                "MCP(Enables, ModelContextProtocol).",
                "HAK_GAL(Implements, NeurosymbolicAI).",
                "KnowledgeBase(Stores, Facts).",
                "HRM(Performs, NeuralReasoning).",
                "LLMEnsemble(Includes, DeepSeek).",
                "LLMEnsemble(Includes, Gemini).",
                "Python(Powers, HAK_GAL).",
                "Flask(Provides, APIFramework)."
            ]
            
            for fact in test_facts:
                try:
                    cursor.execute("INSERT INTO facts (statement) VALUES (?);", (fact,))
                except sqlite3.IntegrityError:
                    pass  # Fact already exists
            
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM facts;")
            new_count = cursor.fetchone()[0]
            print(f"✅ Created {new_count} test facts")
        else:
            print(f"✅ Database already has {count} facts")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating test facts: {e}")


if __name__ == "__main__":
    print("HAK_GAL Knowledge Base Diagnostic Tool\n")
    
    # Check database
    check_database()
    
    # Check JSONL file
    check_jsonl_file()
    
    # Create test facts if needed
    create_test_facts()
    
    print("\n" + "=" * 60)
    print("Diagnostic complete!")
    print("\nNext steps:")
    print("1. If database was empty, restart HAK_GAL API")
    print("2. Run test_mcp_integration.py again")
    print("3. Facts should now be available")
    print("=" * 60)
