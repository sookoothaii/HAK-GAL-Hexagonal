#!/usr/bin/env python3
"""
Safe Memory Cache für HAK_GAL_HEXAGONAL
Implementiert eine sichere In-Memory-Caching-Schicht nur für Read-Operations
Stört das bestehende System nicht, bringt aber messbare Performance-Vorteile
"""

import sqlite3
import time
import json
import hashlib
from typing import Dict, List, Any, Optional
from functools import wraps
import threading

class SafeMemoryCache:
    """
    Sichere In-Memory-Caching-Schicht
    - Nur Read-Cache (keine Write-Operationen)
    - LRU-Eviction bei Speicherlimit
    - Thread-safe
    - Messbare Performance-Verbesserungen
    """
    
    def __init__(self, max_size_mb: int = 50, ttl_seconds: int = 300):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict] = {}
        self.access_times: Dict[str, float] = {}
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
    
    def _get_cache_key(self, query: str, params: tuple = ()) -> str:
        """Generiert einen eindeutigen Cache-Key für eine Abfrage"""
        key_data = f"{query}:{params}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, timestamp: float) -> bool:
        """Prüft ob ein Cache-Eintrag abgelaufen ist"""
        return time.time() - timestamp > self.ttl_seconds
    
    def _get_cache_size(self) -> int:
        """Berechnet die aktuelle Cache-Größe in Bytes"""
        total_size = 0
        for key, data in self.cache.items():
            # Grobe Schätzung der Größe
            total_size += len(key) + len(str(data))
        return total_size
    
    def _evict_lru(self):
        """Entfernt die am wenigsten kürzlich verwendeten Einträge"""
        if not self.cache:
            return
        
        # Sortiere nach Zugriffszeit
        sorted_items = sorted(self.access_times.items(), key=lambda x: x[1])
        
        # Entferne 25% der ältesten Einträge
        evict_count = max(1, len(sorted_items) // 4)
        for key, _ in sorted_items[:evict_count]:
            if key in self.cache:
                del self.cache[key]
                del self.access_times[key]
                self.stats['evictions'] += 1
    
    def get(self, query: str, params: tuple = ()) -> Optional[List[Dict]]:
        """Holt Daten aus dem Cache"""
        with self.lock:
            self.stats['total_requests'] += 1
            cache_key = self._get_cache_key(query, params)
            
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                # Prüfe TTL
                if self._is_expired(entry['timestamp']):
                    del self.cache[cache_key]
                    del self.access_times[cache_key]
                    self.stats['misses'] += 1
                    return None
                
                # Update Zugriffszeit
                self.access_times[cache_key] = time.time()
                self.stats['hits'] += 1
                return entry['data']
            
            self.stats['misses'] += 1
            return None
    
    def put(self, query: str, params: tuple, data: List[Dict]):
        """Speichert Daten im Cache"""
        with self.lock:
            cache_key = self._get_cache_key(query, params)
            
            # Prüfe Speicherlimit
            if self._get_cache_size() > self.max_size_bytes:
                self._evict_lru()
            
            # Speichere Daten
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            self.access_times[cache_key] = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Cache-Statistiken zurück"""
        with self.lock:
            hit_rate = (self.stats['hits'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0
            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'total_requests': self.stats['total_requests'],
                'hit_rate_percent': round(hit_rate, 2),
                'cache_size_bytes': self._get_cache_size(),
                'cache_entries': len(self.cache),
                'evictions': self.stats['evictions']
            }
    
    def clear(self):
        """Leert den Cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.stats = {'hits': 0, 'misses': 0, 'evictions': 0, 'total_requests': 0}

# Globaler Cache-Instance
_cache_instance = SafeMemoryCache(max_size_mb=50, ttl_seconds=300)

def cached_query(func):
    """Decorator für gecachte Datenbankabfragen"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Generiere Cache-Key aus Funktionsname und Argumenten
        cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
        
        # Versuche Cache-Hit
        cached_result = _cache_instance.get(cache_key, ())
        if cached_result is not None:
            return cached_result
        
        # Cache-Miss: Führe Abfrage aus
        result = func(*args, **kwargs)
        
        # Speichere im Cache
        if result:
            _cache_instance.put(cache_key, (), result)
        
        return result
    return wrapper

class CachedDatabase:
    """Wrapper für SQLite mit integriertem Cache"""
    
    def __init__(self, db_path: str = 'hexagonal_kb.db'):
        self.db_path = db_path
        self.cache = _cache_instance
    
    def get_connection(self):
        """Gibt eine SQLite-Verbindung zurück"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    @cached_query
    def get_facts_by_predicate(self, predicate: str, limit: int = 100) -> List[Dict]:
        """Holt Fakten nach Prädikat (gecacht)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM facts WHERE predicate = ? LIMIT ?', (predicate, limit))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    @cached_query
    def get_facts_by_source(self, source: str, limit: int = 100) -> List[Dict]:
        """Holt Fakten nach Quelle (gecacht)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM facts WHERE source = ? LIMIT ?', (source, limit))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    @cached_query
    def get_facts_extended_by_type(self, fact_type: str, limit: int = 100) -> List[Dict]:
        """Holt erweiterte Fakten nach Typ (gecacht)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM facts_extended WHERE fact_type = ? LIMIT ?', (fact_type, limit))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    @cached_query
    def get_most_common_predicates(self, limit: int = 10) -> List[Dict]:
        """Holt häufigste Prädikate (gecacht)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT predicate, COUNT(*) as count 
            FROM facts 
            WHERE predicate IS NOT NULL 
            GROUP BY predicate 
            ORDER BY count DESC 
            LIMIT ?
        ''', (limit,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Gibt Cache-Statistiken zurück"""
        return self.cache.get_stats()

def performance_test_cached_vs_uncached():
    """Testet Performance-Unterschied zwischen gecachten und ungecachten Abfragen"""
    
    print('=== Cache Performance Test ===')
    print()
    
    # Teste mit und ohne Cache
    cached_db = CachedDatabase()
    
    # Test-Abfragen
    test_queries = [
        ("get_facts_by_predicate", "is_a", 100),
        ("get_facts_by_source", "system", 100),
        ("get_most_common_predicates", 10),
    ]
    
    print('1. Erste Ausführung (Cache-Miss):')
    for func_name, *args in test_queries:
        start_time = time.time()
        func = getattr(cached_db, func_name)
        result = func(*args)
        end_time = time.time()
        print(f'   {func_name}: {len(result)} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    print()
    print('2. Zweite Ausführung (Cache-Hit):')
    for func_name, *args in test_queries:
        start_time = time.time()
        func = getattr(cached_db, func_name)
        result = func(*args)
        end_time = time.time()
        print(f'   {func_name}: {len(result)} Ergebnisse in {(end_time - start_time)*1000:.2f}ms')
    
    print()
    print('3. Cache-Statistiken:')
    stats = cached_db.get_cache_stats()
    for key, value in stats.items():
        print(f'   {key}: {value}')
    
    print()
    print('4. Performance-Vergleich:')
    
    # Teste ohne Cache
    conn = sqlite3.connect('hexagonal_kb.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Gleiche Abfragen ohne Cache
    start_time = time.time()
    cursor.execute('SELECT * FROM facts WHERE predicate = ? LIMIT ?', ('is_a', 100))
    results = cursor.fetchall()
    end_time = time.time()
    uncached_time = (end_time - start_time) * 1000
    
    # Mit Cache (zweite Ausführung)
    start_time = time.time()
    cached_results = cached_db.get_facts_by_predicate('is_a', 100)
    end_time = time.time()
    cached_time = (end_time - start_time) * 1000
    
    speedup = uncached_time / cached_time if cached_time > 0 else float('inf')
    print(f'   Ungecacht: {uncached_time:.2f}ms')
    print(f'   Gecacht: {cached_time:.2f}ms')
    print(f'   Speedup: {speedup:.1f}x')
    
    conn.close()

if __name__ == '__main__':
    performance_test_cached_vs_uncached()




