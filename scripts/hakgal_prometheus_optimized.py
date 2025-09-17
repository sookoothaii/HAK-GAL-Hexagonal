#!/usr/bin/env python3
"""
HAK/GAL Prometheus Exporter - OPTIMIZED STANDALONE SERVICE
"""
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import psutil
import time
import threading
import random

# Metriken definieren
cpu_usage = Gauge('system_cpu_percent', 'System CPU usage')
memory_usage = Gauge('system_memory_percent', 'System memory usage')
disk_usage = Gauge('system_disk_percent', 'System disk usage')
query_execution = Histogram('query_execution_time_seconds', 'Query execution time')
cache_hit_rate = Gauge('cache_hit_rate', 'Cache hit rate percentage')
active_threads = Gauge('active_threads', 'Number of active threads')
db_connections = Gauge('database_connections', 'Active database connections')

def collect_system_metrics():
    """Sammle System-Metriken kontinuierlich"""
    while True:
        try:
            # CPU und Memory
            cpu_usage.set(psutil.cpu_percent(interval=1))
            memory_usage.set(psutil.virtual_memory().percent)
            disk_usage.set(psutil.disk_usage('/').percent)
            
            # Threads und Connections
            active_threads.set(threading.active_count())
            db_connections.set(len([c for c in psutil.net_connections() if c.laddr.port == 5432]))
            
            # Simuliere Cache-Hit-Rate (in Production aus Redis/Cache)
            cache_hit_rate.set(75 + random.randint(0, 20))
            
            # Simuliere Query-Zeit
            query_execution.observe(random.uniform(0.001, 0.05))
            
        except Exception as e:
            print(f"Error collecting metrics: {e}")
        
        time.sleep(5)

if __name__ == '__main__':
    print("HAK/GAL Prometheus Exporter - OPTIMIZED")
    print("Starting metrics collection...")
    
    # Starte Metrics Collector Thread
    collector = threading.Thread(target=collect_system_metrics, daemon=True)
    collector.start()
    
    # Starte Prometheus HTTP Server
    start_http_server(8000)
    print("Prometheus metrics available at http://localhost:8000")
    print("Optimized for high-performance collection")
    
    # Keep running
    while True:
        time.sleep(60)