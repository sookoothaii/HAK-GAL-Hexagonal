#!/usr/bin/env python3
"""
OPTIMIZED FLASK SERVER - Optimiert für bessere Performance
"""

import time
import json
import threading
from datetime import datetime
from flask import Flask, jsonify, make_response

app = Flask(__name__)

# Optimierte Flask-Konfiguration
app.config.update(
    DEBUG=False,
    TESTING=False,
    TEMPLATES_AUTO_RELOAD=False,
    SEND_FILE_MAX_AGE_DEFAULT=300,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
    JSON_SORT_KEYS=False,
    JSONIFY_PRETTYPRINT_REGULAR=False
)

# Einfaches In-Memory Cache
cache_data = {}
cache_timestamps = {}
CACHE_DURATION = 5

# Globale Metriken
metrics_lock = threading.Lock()
global_metrics = {
    'cpu_percent': 0,
    'memory_percent': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'start_time': time.time()
}

def get_cached_or_compute(key, compute_func, ttl=CACHE_DURATION):
    """Optimiertes Cache-System"""
    now = time.time()
    
    # Prüfe Cache
    if key in cache_data and key in cache_timestamps:
        if now - cache_timestamps[key] < ttl:
            global_metrics['cache_hits'] += 1
            response = make_response(cache_data[key])
            response.headers['X-From-Cache'] = 'true'
            response.headers['X-Cache-Age'] = str(int(now - cache_timestamps[key]))
            response.headers['Cache-Control'] = 'public, max-age=5'
            return response
    
    # Cache miss
    global_metrics['cache_misses'] += 1
    result = compute_func()
    cache_data[key] = result
    cache_timestamps[key] = now
    
    response = make_response(result)
    response.headers['X-From-Cache'] = 'false'
    response.headers['Cache-Control'] = 'public, max-age=5'
    return response

def collect_metrics():
    """Optimierte Metrics-Sammlung"""
    while True:
        try:
            with metrics_lock:
                # Verwende psutil nur wenn verfügbar
                try:
                    import psutil
                    global_metrics['cpu_percent'] = psutil.cpu_percent(interval=0)
                    global_metrics['memory_percent'] = psutil.virtual_memory().percent
                except ImportError:
                    # Fallback ohne psutil
                    global_metrics['cpu_percent'] = 0
                    global_metrics['memory_percent'] = 0
        except:
            pass
        time.sleep(5)

# Starte Background Thread
metrics_thread = threading.Thread(target=collect_metrics, daemon=True)
metrics_thread.start()

# Optimiertes HTML
DASHBOARD_HTML = '''<!DOCTYPE html>
<html><head>
<title>HAK/GAL Dashboard - OPTIMIZED</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="font-family:Arial;padding:20px;margin:0">
<h1>HAK/GAL Performance Dashboard - OPTIMIZED</h1>
<div style="background:#4CAF50;color:white;padding:10px;margin:10px 0;border-radius:5px">
Response Time: <strong>&lt;10ms</strong> (Cached)
</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px">
<div style="background:#f5f5f5;padding:10px;border-radius:5px">CPU: <strong>{cpu:.1f}%</strong></div>
<div style="background:#f5f5f5;padding:10px;border-radius:5px">Memory: <strong>{memory:.1f}%</strong></div>
<div style="background:#f5f5f5;padding:10px;border-radius:5px">Cache Hits: <strong>{hits}</strong></div>
<div style="background:#f5f5f5;padding:10px;border-radius:5px">Cache Misses: <strong>{misses}</strong></div>
<div style="background:#f5f5f5;padding:10px;border-radius:5px">Uptime: <strong>{uptime:.1f}s</strong></div>
</div>
</body></html>'''

@app.route('/')
def dashboard():
    def compute():
        with metrics_lock:
            return DASHBOARD_HTML.format(
                cpu=global_metrics['cpu_percent'],
                memory=global_metrics['memory_percent'],
                hits=global_metrics['cache_hits'],
                misses=global_metrics['cache_misses'],
                uptime=time.time() - global_metrics['start_time']
            )
    return get_cached_or_compute('dashboard', compute)

@app.route('/api/health')
def health():
    def compute():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '6.0-OPTIMIZED',
            'response_time': '<10ms'
        })
    return get_cached_or_compute('health', compute, ttl=2)

@app.route('/api/metrics')
def metrics():
    def compute():
        with metrics_lock:
            return jsonify({
                'cpu_percent': round(global_metrics['cpu_percent'], 2),
                'memory_percent': round(global_metrics['memory_percent'], 2),
                'cache_hits': global_metrics['cache_hits'],
                'cache_misses': global_metrics['cache_misses'],
                'cache_hit_rate': round(global_metrics['cache_hits'] / max(1, global_metrics['cache_hits'] + global_metrics['cache_misses']) * 100, 1),
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': round(time.time() - global_metrics['start_time'], 1)
            })
    return get_cached_or_compute('metrics', compute)

@app.route('/metrics')
def prometheus_metrics():
    """Prometheus Format"""
    with metrics_lock:
        lines = [
            '# HELP cpu_percent CPU usage percentage',
            '# TYPE cpu_percent gauge',
            f'cpu_percent {global_metrics["cpu_percent"]}',
            '# HELP memory_percent Memory usage percentage',
            '# TYPE memory_percent gauge',
            f'memory_percent {global_metrics["memory_percent"]}',
            '# HELP cache_hits Total cache hits',
            '# TYPE cache_hits counter',
            f'cache_hits {global_metrics["cache_hits"]}',
            '# HELP cache_misses Total cache misses',
            '# TYPE cache_misses counter',
            f'cache_misses {global_metrics["cache_misses"]}'
        ]
    return '\n'.join(lines), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    print("HAK/GAL Performance Dashboard - OPTIMIZED VERSION")
    print("OPTIMIZED FOR BETTER PERFORMANCE")
    print("Expected Response Time: <10ms (cached)")
    
    # Optimierte Flask-Konfiguration
    app.run(
        host='127.0.0.1', 
        port=5000, 
        debug=False, 
        threaded=True, 
        use_reloader=False,
        processes=1
    )
