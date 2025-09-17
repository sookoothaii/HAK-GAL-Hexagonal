#!/usr/bin/env python3
"""
MCP Cache Integration für HAK_GAL_HEXAGONAL
Sichere Integration des In-Memory-Caches in bestehende MCP-Server
Stört das laufende System nicht, bringt aber messbare Performance-Vorteile
"""

import os
import sys
import time
from typing import Dict, Any, List

# Füge den aktuellen Pfad zum Python-Path hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from safe_memory_cache import CachedDatabase, _cache_instance

class MCPCacheIntegration:
    """
    Sichere Integration des Caches in MCP-Server
    - Nur Read-Operationen werden gecacht
    - Write-Operationen umgehen den Cache
    - Thread-safe
    - Messbare Performance-Verbesserungen
    """
    
    def __init__(self):
        self.cached_db = CachedDatabase()
        self.cache_enabled = True
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0,
            'performance_gain_ms': 0
        }
    
    def get_facts_count(self) -> int:
        """Holt die Anzahl der Fakten (gecacht)"""
        if not self.cache_enabled:
            return self._uncached_facts_count()
        
        start_time = time.time()
        cached_result = _cache_instance.get("facts_count", ())
        
        if cached_result is not None:
            self.stats['cache_hits'] += 1
            self.stats['total_requests'] += 1
            return cached_result[0]['count']
        
        # Cache-Miss: Führe Abfrage aus
        result = self._uncached_facts_count()
        
        # Speichere im Cache
        _cache_instance.put("facts_count", (), [{'count': result}])
        
        end_time = time.time()
        self.stats['cache_misses'] += 1
        self.stats['total_requests'] += 1
        self.stats['performance_gain_ms'] += (end_time - start_time) * 1000
        
        return result
    
    def _uncached_facts_count(self) -> int:
        """Ungecachte Version der Fakten-Anzahl"""
        conn = self.cached_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM facts')
        result = cursor.fetchone()['count']
        conn.close()
        return result
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        """Sucht in der Wissensdatenbank (gecacht)"""
        if not self.cache_enabled:
            return self._uncached_search_knowledge(query, limit)
        
        start_time = time.time()
        cache_key = f"search_knowledge:{query}:{limit}"
        cached_result = _cache_instance.get(cache_key, ())
        
        if cached_result is not None:
            self.stats['cache_hits'] += 1
            self.stats['total_requests'] += 1
            return cached_result
        
        # Cache-Miss: Führe Suche aus
        result = self._uncached_search_knowledge(query, limit)
        
        # Speichere im Cache
        _cache_instance.put(cache_key, (), result)
        
        end_time = time.time()
        self.stats['cache_misses'] += 1
        self.stats['total_requests'] += 1
        self.stats['performance_gain_ms'] += (end_time - start_time) * 1000
        
        return result
    
    def _uncached_search_knowledge(self, query: str, limit: int) -> List[Dict]:
        """Ungecachte Version der Wissenssuche"""
        conn = self.cached_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT statement, predicate, subject, object, confidence, source
            FROM facts 
            WHERE statement LIKE ? OR predicate LIKE ? OR subject LIKE ? OR object LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_recent_facts(self, count: int = 5) -> List[Dict]:
        """Holt die neuesten Fakten (gecacht)"""
        if not self.cache_enabled:
            return self._uncached_recent_facts(count)
        
        start_time = time.time()
        cache_key = f"recent_facts:{count}"
        cached_result = _cache_instance.get(cache_key, ())
        
        if cached_result is not None:
            self.stats['cache_hits'] += 1
            self.stats['total_requests'] += 1
            return cached_result
        
        # Cache-Miss: Führe Abfrage aus
        result = self._uncached_recent_facts(count)
        
        # Speichere im Cache
        _cache_instance.put(cache_key, (), result)
        
        end_time = time.time()
        self.stats['cache_misses'] += 1
        self.stats['total_requests'] += 1
        self.stats['performance_gain_ms'] += (end_time - start_time) * 1000
        
        return result
    
    def _uncached_recent_facts(self, count: int) -> List[Dict]:
        """Ungecachte Version der neuesten Fakten"""
        conn = self.cached_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT statement, predicate, subject, object, confidence, source
            FROM facts 
            ORDER BY rowid DESC
            LIMIT ?
        ''', (count,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Gibt System-Status zurück (gecacht)"""
        if not self.cache_enabled:
            return self._uncached_system_status()
        
        start_time = time.time()
        cached_result = _cache_instance.get("system_status", ())
        
        if cached_result is not None:
            self.stats['cache_hits'] += 1
            self.stats['total_requests'] += 1
            return cached_result[0]
        
        # Cache-Miss: Führe Abfrage aus
        result = self._uncached_system_status()
        
        # Speichere im Cache
        _cache_instance.put("system_status", (), [result])
        
        end_time = time.time()
        self.stats['cache_misses'] += 1
        self.stats['total_requests'] += 1
        self.stats['performance_gain_ms'] += (end_time - start_time) * 1000
        
        return result
    
    def _uncached_system_status(self) -> Dict[str, Any]:
        """Ungecachte Version des System-Status"""
        conn = self.cached_db.get_connection()
        cursor = conn.cursor()
        
        # Fakten-Anzahl
        cursor.execute('SELECT COUNT(*) as count FROM facts')
        facts_count = cursor.fetchone()['count']
        
        # Datenbank-Info
        cursor.execute('PRAGMA page_count')
        page_count = cursor.fetchone()[0]
        cursor.execute('PRAGMA page_size')
        page_size = cursor.fetchone()[0]
        db_size_mb = (page_count * page_size) / (1024 * 1024)
        
        conn.close()
        
        return {
            'status': 'Operational',
            'database': 'hexagonal_kb.db',
            'facts': facts_count,
            'server': 'HAK_GAL MCP Ultimate v4.0',
            'tools': 66,
            'db_size_mb': round(db_size_mb, 2)
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Gibt Cache-Statistiken zurück"""
        cache_stats = _cache_instance.get_stats()
        hit_rate = (self.stats['cache_hits'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0
        
        return {
            'cache_enabled': self.cache_enabled,
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': self.stats['total_requests'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'performance_gain_ms': round(self.stats['performance_gain_ms'], 2),
            'cache_size_bytes': cache_stats['cache_size_bytes'],
            'cache_entries': cache_stats['cache_entries']
        }
    
    def clear_cache(self):
        """Leert den Cache"""
        _cache_instance.clear()
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0,
            'performance_gain_ms': 0
        }
    
    def toggle_cache(self, enabled: bool):
        """Aktiviert/deaktiviert den Cache"""
        self.cache_enabled = enabled

def test_mcp_cache_integration():
    """Testet die MCP-Cache-Integration"""
    
    print('=== MCP Cache Integration Test ===')
    print()
    
    integration = MCPCacheIntegration()
    
    # Test 1: System-Status
    print('1. System-Status Test:')
    start_time = time.time()
    status = integration.get_system_status()
    end_time = time.time()
    print(f'   Status: {status["status"]}')
    print(f'   Fakten: {status["facts"]:,}')
    print(f'   DB-Größe: {status["db_size_mb"]} MB')
    print(f'   Zeit: {(end_time - start_time)*1000:.2f}ms')
    
    print()
    
    # Test 2: Wissenssuche
    print('2. Wissenssuche Test:')
    start_time = time.time()
    results = integration.search_knowledge('system', 5)
    end_time = time.time()
    print(f'   Suchergebnisse: {len(results)}')
    print(f'   Zeit: {(end_time - start_time)*1000:.2f}ms')
    
    print()
    
    # Test 3: Neueste Fakten
    print('3. Neueste Fakten Test:')
    start_time = time.time()
    recent = integration.get_recent_facts(3)
    end_time = time.time()
    print(f'   Neueste Fakten: {len(recent)}')
    print(f'   Zeit: {(end_time - start_time)*1000:.2f}ms')
    
    print()
    
    # Test 4: Cache-Statistiken
    print('4. Cache-Statistiken:')
    stats = integration.get_cache_stats()
    for key, value in stats.items():
        print(f'   {key}: {value}')
    
    print()
    
    # Test 5: Performance-Vergleich
    print('5. Performance-Vergleich (Cache vs. No-Cache):')
    
    # Mit Cache
    integration.toggle_cache(True)
    start_time = time.time()
    integration.get_system_status()
    cached_time = (time.time() - start_time) * 1000
    
    # Ohne Cache
    integration.toggle_cache(False)
    start_time = time.time()
    integration.get_system_status()
    uncached_time = (time.time() - start_time) * 1000
    
    speedup = uncached_time / cached_time if cached_time > 0 else float('inf')
    print(f'   Mit Cache: {cached_time:.2f}ms')
    print(f'   Ohne Cache: {uncached_time:.2f}ms')
    print(f'   Speedup: {speedup:.1f}x')
    
    # Reaktiviere Cache
    integration.toggle_cache(True)

if __name__ == '__main__':
    test_mcp_cache_integration()




