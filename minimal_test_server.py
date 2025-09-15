#!/usr/bin/env python3
"""
MINIMALER TEST-SERVER - OHNE JEGLICHE FEATURES
Nur um die 1-Sekunden-Verzögerung zu identifizieren
"""

import time
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def root():
    """Minimaler Root-Endpoint"""
    return "MINIMAL SERVER - NO DELAYS"

@app.route('/api/health')
def health():
    """Minimaler Health-Check"""
    start_time = time.time()
    
    response = {
        'status': 'healthy',
        'timestamp': time.time(),
        'response_time_ms': 0
    }
    
    end_time = time.time()
    response['response_time_ms'] = round((end_time - start_time) * 1000, 2)
    
    return jsonify(response)

@app.route('/api/metrics')
def metrics():
    """Minimaler Metrics-Endpoint"""
    start_time = time.time()
    
    response = {
        'cpu': 0,
        'memory': 0,
        'timestamp': time.time(),
        'response_time_ms': 0
    }
    
    end_time = time.time()
    response['response_time_ms'] = round((end_time - start_time) * 1000, 2)
    
    return jsonify(response)

@app.route('/test')
def test():
    """Test-Endpoint mit Zeitmessung"""
    start_time = time.time()
    
    # Simuliere eine sehr einfache Operation
    result = {"test": "success", "time": time.time()}
    
    end_time = time.time()
    processing_time = (end_time - start_time) * 1000
    
    return jsonify({
        "result": result,
        "processing_time_ms": round(processing_time, 2),
        "total_time_ms": round(processing_time, 2)
    })

if __name__ == '__main__':
    print("🚀 MINIMAL TEST SERVER - NO FEATURES")
    print("=" * 50)
    print("Testing for 1-second delay...")
    print("Expected: <10ms response time")
    print("=" * 50)
    
    # Minimale Flask-Konfiguration
    app.run(
        host='127.0.0.1', 
        port=5555,  # Anderer Port um Konflikte zu vermeiden
        debug=False, 
        threaded=True, 
        use_reloader=False
    )