#!/usr/bin/env python3
"""
Prometheus Metrics Server
"""

import http.server
import socketserver
import threading
import time
import json
import requests
from datetime import datetime

class PrometheusHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            try:
                # Get metrics from Flask API
                response = requests.get('http://127.0.0.1:5000/api/metrics', timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Convert to Prometheus format
                    metrics = self.format_prometheus_metrics(data)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain; version=0.0.4; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(metrics.encode('utf-8'))
                else:
                    self.send_response(503)
                    self.end_headers()
                    self.wfile.write(b'# Service unavailable\n')
            except Exception as e:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(f'# Error: {str(e)}\n'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'# Not found\n')
    
    def format_prometheus_metrics(self, data):
        """Format Flask metrics to Prometheus format"""
        timestamp = int(datetime.now().timestamp() * 1000)
        
        metrics = []
        metrics.append('# HELP hakgal_facts_total Total number of facts in database')
        metrics.append('# TYPE hakgal_facts_total gauge')
        metrics.append(f'hakgal_facts_total {data["facts_count"]} {timestamp}')
        
        metrics.append('# HELP hakgal_query_time_seconds Average query time in seconds')
        metrics.append('# TYPE hakgal_query_time_seconds gauge')
        metrics.append(f'hakgal_query_time_seconds {data["avg_query_time"]} {timestamp}')
        
        metrics.append('# HELP hakgal_cache_hits_total Total cache hits')
        metrics.append('# TYPE hakgal_cache_hits_total counter')
        metrics.append(f'hakgal_cache_hits_total {data["cache_hits"]} {timestamp}')
        
        metrics.append('# HELP hakgal_cache_misses_total Total cache misses')
        metrics.append('# TYPE hakgal_cache_misses_total counter')
        metrics.append(f'hakgal_cache_misses_total {data["cache_misses"]} {timestamp}')
        
        metrics.append('# HELP hakgal_system_cpu_percent CPU usage percentage')
        metrics.append('# TYPE hakgal_system_cpu_percent gauge')
        metrics.append(f'hakgal_system_cpu_percent {data["system_cpu_percent"]} {timestamp}')
        
        metrics.append('# HELP hakgal_system_memory_percent Memory usage percentage')
        metrics.append('# TYPE hakgal_system_memory_percent gauge')
        metrics.append(f'hakgal_system_memory_percent {data["system_memory_percent"]} {timestamp}')
        
        metrics.append('# HELP hakgal_database_connections Database connections')
        metrics.append('# TYPE hakgal_database_connections gauge')
        metrics.append(f'hakgal_database_connections {data["database_connections"]} {timestamp}')
        
        metrics.append('# HELP hakgal_wal_size_bytes WAL size in bytes')
        metrics.append('# TYPE hakgal_wal_size_bytes gauge')
        metrics.append(f'hakgal_wal_size_bytes {data["wal_size_bytes"]} {timestamp}')
        
        return '\n'.join(metrics) + '\n'
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def main():
    """Start Prometheus metrics server"""
    print("🚀 Starting Prometheus Metrics Server")
    print("=" * 50)
    
    PORT = 8000
    
    try:
        with socketserver.TCPServer(("", PORT), PrometheusHandler) as httpd:
            print(f"📊 Prometheus Server running on port {PORT}")
            print(f"📈 Metrics endpoint: http://localhost:{PORT}/metrics")
            print("⏹️  Press Ctrl+C to stop")
            print("=" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Prometheus server...")
        print("✅ Prometheus server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
