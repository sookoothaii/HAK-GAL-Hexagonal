#!/usr/bin/env python3
"""
HAK-GAL Complete SQLite3 Migration Plan
========================================
Vollständige Umstellung auf SQLite3-basierte Architektur
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class HAKGALSQLiteMigration:
    """Complete SQLite3 migration for HAK-GAL Suite"""
    
    def __init__(self):
        self.db_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
        self.legacy_paths = {
            'jsonl': Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl"),
            'audit': Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log"),
            'responses': Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/agent_responses/"),
        }
    
    def create_complete_schema(self):
        """Create complete SQLite3 schema for HAK-GAL"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        schema = """
        -- =====================================================
        -- HAK-GAL COMPLETE SQLITE3 SCHEMA
        -- =====================================================
        
        -- 1. FACTS TABLE (Core Knowledge Base)
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT NOT NULL UNIQUE,
            predicate TEXT,
            subject TEXT,
            object TEXT,
            confidence REAL DEFAULT 1.0,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSON,
            embedding BLOB,  -- For future vector search
            INDEX idx_predicate (predicate),
            INDEX idx_subject (subject),
            INDEX idx_object (object),
            INDEX idx_created (created_at)
        );
        
        -- 2. FACT GROUPS (Compressed Storage)
        CREATE TABLE IF NOT EXISTS fact_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_key TEXT NOT NULL UNIQUE,
            predicate TEXT NOT NULL,
            arguments JSON NOT NULL,
            fact_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_group_predicate (predicate)
        );
        
        -- 3. AGENTS TABLE (Multi-Agent System)
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,  -- gemini, claude_cli, cursor, ollama
            config JSON,
            status TEXT DEFAULT 'active',
            last_used TIMESTAMP,
            total_requests INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            avg_response_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 4. AGENT TASKS (Task Delegation)
        CREATE TABLE IF NOT EXISTS agent_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL UNIQUE,
            agent_id INTEGER,
            task_description TEXT,
            context JSON,
            status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
            request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            response_time TIMESTAMP,
            response_text TEXT,
            response_metadata JSON,
            error_message TEXT,
            duration_ms INTEGER,
            tokens_used INTEGER,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        );
        
        -- 5. AUDIT LOG (All System Operations)
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,
            entity_type TEXT,  -- fact, agent, task, etc.
            entity_id INTEGER,
            user TEXT,
            auth_token TEXT,
            payload JSON,
            result TEXT,
            error TEXT,
            ip_address TEXT,
            session_id TEXT,
            INDEX idx_audit_timestamp (timestamp),
            INDEX idx_audit_action (action)
        );
        
        -- 6. SESSIONS (User Sessions)
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL UNIQUE,
            user_id TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            metadata JSON
        );
        
        -- 7. QUERIES (Search History)
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            query_text TEXT NOT NULL,
            query_type TEXT,  -- search, reason, llm, etc.
            results_count INTEGER,
            response_time_ms INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSON,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );
        
        -- 8. SYSTEM METRICS (Performance Monitoring)
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metric_type TEXT NOT NULL,  -- cpu, memory, disk, api_call, etc.
            metric_name TEXT NOT NULL,
            metric_value REAL,
            unit TEXT,
            metadata JSON,
            INDEX idx_metrics_timestamp (timestamp),
            INDEX idx_metrics_type (metric_type)
        );
        
        -- 9. BACKUPS (Backup Management)
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_id TEXT NOT NULL UNIQUE,
            backup_path TEXT NOT NULL,
            description TEXT,
            facts_count INTEGER,
            db_size_bytes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            metadata JSON
        );
        
        -- 10. PROJECT SNAPSHOTS
        CREATE TABLE IF NOT EXISTS project_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            description TEXT,
            hub_path TEXT,
            files JSON,
            facts_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            metadata JSON
        );
        
        -- 11. WEBSOCKET EVENTS (Real-time Communication)
        CREATE TABLE IF NOT EXISTS websocket_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data JSON,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_ws_client (client_id),
            INDEX idx_ws_timestamp (timestamp)
        );
        
        -- 12. API KEYS (Authentication)
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_hash TEXT NOT NULL UNIQUE,
            name TEXT,
            permissions JSON,
            rate_limit INTEGER DEFAULT 1000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            total_requests INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        );
        
        -- 13. RATE LIMITING
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL,  -- IP or API key
            endpoint TEXT NOT NULL,
            requests_count INTEGER DEFAULT 1,
            window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_rate_identifier (identifier),
            INDEX idx_rate_window (window_start)
        );
        
        -- 14. CACHE (Response Cache)
        CREATE TABLE IF NOT EXISTS cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_key TEXT NOT NULL UNIQUE,
            cache_value TEXT,
            ttl_seconds INTEGER DEFAULT 3600,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hit_count INTEGER DEFAULT 0,
            INDEX idx_cache_key (cache_key),
            INDEX idx_cache_created (created_at)
        );
        
        -- 15. ERROR LOG
        CREATE TABLE IF NOT EXISTS error_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_type TEXT NOT NULL,
            error_message TEXT,
            stack_trace TEXT,
            context JSON,
            severity TEXT DEFAULT 'ERROR',  -- DEBUG, INFO, WARNING, ERROR, CRITICAL
            resolved BOOLEAN DEFAULT 0,
            INDEX idx_error_timestamp (timestamp),
            INDEX idx_error_type (error_type)
        );
        
        -- =====================================================
        -- VIEWS FOR COMMON QUERIES
        -- =====================================================
        
        -- Recent Facts View
        CREATE VIEW IF NOT EXISTS v_recent_facts AS
        SELECT 
            id, 
            statement, 
            predicate, 
            created_at,
            source
        FROM facts 
        ORDER BY created_at DESC 
        LIMIT 100;
        
        -- Agent Performance View
        CREATE VIEW IF NOT EXISTS v_agent_performance AS
        SELECT 
            a.name,
            a.type,
            COUNT(t.id) as total_tasks,
            AVG(t.duration_ms) as avg_duration_ms,
            SUM(t.tokens_used) as total_tokens,
            MAX(t.request_time) as last_used
        FROM agents a
        LEFT JOIN agent_tasks t ON a.id = t.agent_id
        GROUP BY a.id;
        
        -- System Health View
        CREATE VIEW IF NOT EXISTS v_system_health AS
        SELECT 
            (SELECT COUNT(*) FROM facts) as total_facts,
            (SELECT COUNT(*) FROM agent_tasks WHERE status = 'completed') as completed_tasks,
            (SELECT COUNT(*) FROM agent_tasks WHERE status = 'failed') as failed_tasks,
            (SELECT AVG(response_time_ms) FROM queries WHERE timestamp > datetime('now', '-1 hour')) as avg_response_time_1h,
            (SELECT COUNT(*) FROM error_log WHERE resolved = 0) as unresolved_errors;
        
        -- =====================================================
        -- TRIGGERS FOR AUTOMATIC UPDATES
        -- =====================================================
        
        -- Auto-update timestamp
        CREATE TRIGGER IF NOT EXISTS update_facts_timestamp 
        AFTER UPDATE ON facts
        BEGIN
            UPDATE facts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        
        -- Auto-update session activity
        CREATE TRIGGER IF NOT EXISTS update_session_activity
        AFTER INSERT ON queries
        BEGIN
            UPDATE sessions SET last_activity = CURRENT_TIMESTAMP 
            WHERE session_id = NEW.session_id;
        END;
        
        -- Auto-clean old cache entries
        CREATE TRIGGER IF NOT EXISTS clean_expired_cache
        AFTER INSERT ON cache
        WHEN (SELECT COUNT(*) FROM cache) > 10000
        BEGIN
            DELETE FROM cache 
            WHERE datetime(created_at, '+' || ttl_seconds || ' seconds') < datetime('now');
        END;
        """
        
        # Execute schema creation
        cursor.executescript(schema)
        conn.commit()
        
        print("✅ Complete SQLite3 schema created successfully!")
        return True
    
    def migrate_jsonl_to_sqlite(self):
        """Migrate JSONL data to SQLite"""
        
        if not self.legacy_paths['jsonl'].exists():
            print("No JSONL file to migrate")
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        migrated = 0
        with open(self.legacy_paths['jsonl'], 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    statement = data.get('statement', data.get('text', ''))
                    
                    if statement:
                        cursor.execute("""
                            INSERT OR IGNORE INTO facts (statement, source, metadata)
                            VALUES (?, ?, ?)
                        """, (statement, 'jsonl_migration', json.dumps(data)))
                        migrated += 1
                except:
                    continue
        
        conn.commit()
        print(f"✅ Migrated {migrated} facts from JSONL")
    
    def create_indexes(self):
        """Create performance indexes"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_facts_predicate ON facts(predicate)",
            "CREATE INDEX IF NOT EXISTS idx_facts_created ON facts(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON agent_tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp DESC)",
        ]
        
        for idx in indexes:
            cursor.execute(idx)
        
        conn.commit()
        print("✅ Performance indexes created")
    
    def optimize_database(self):
        """Optimize SQLite database"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # SQLite optimizations
        optimizations = [
            "PRAGMA journal_mode = WAL",  # Write-Ahead Logging
            "PRAGMA synchronous = NORMAL",  # Faster writes
            "PRAGMA cache_size = -64000",  # 64MB cache
            "PRAGMA temp_store = MEMORY",  # Use memory for temp tables
            "PRAGMA mmap_size = 268435456",  # 256MB memory-mapped I/O
            "VACUUM",  # Rebuild database file
            "ANALYZE",  # Update statistics
        ]
        
        for opt in optimizations:
            cursor.execute(opt)
            print(f"  ✅ {opt}")
        
        conn.commit()
        print("✅ Database optimized")
    
    def generate_migration_report(self):
        """Generate migration report"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'tables': {},
            'total_size': 0
        }
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            report['tables'][table_name] = count
        
        # Get database size
        report['total_size'] = self.db_path.stat().st_size
        
        # Save report
        report_path = Path("sqlite_migration_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Migration report saved to {report_path}")
        return report

if __name__ == "__main__":
    print("=" * 60)
    print("HAK-GAL COMPLETE SQLITE3 MIGRATION")
    print("=" * 60)
    
    migrator = HAKGALSQLiteMigration()
    
    # Run migration
    print("\n1. Creating complete schema...")
    migrator.create_complete_schema()
    
    print("\n2. Migrating JSONL data...")
    migrator.migrate_jsonl_to_sqlite()
    
    print("\n3. Creating indexes...")
    migrator.create_indexes()
    
    print("\n4. Optimizing database...")
    migrator.optimize_database()
    
    print("\n5. Generating report...")
    report = migrator.generate_migration_report()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)
    
    for table, count in report['tables'].items():
        print(f"  {table}: {count} records")
    
    print(f"\nTotal database size: {report['total_size'] / 1024 / 1024:.2f} MB")
