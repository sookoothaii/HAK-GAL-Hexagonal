#!/usr/bin/env python3
"""LIGHTWEIGHT HAK_GAL API - Performance optimized"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path

app = Flask(__name__)
CORS(app)

DB_PATH = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")

# Single optimized connection
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("PRAGMA synchronous = NORMAL")
conn.execute("PRAGMA cache_size = 10000") 
conn.execute("PRAGMA temp_store = MEMORY")
conn.execute("PRAGMA journal_mode = WAL")

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'mode': 'lightweight'})

@app.route('/api/facts/count')
def facts_count():
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM facts")
    count = cursor.fetchone()[0]
    return jsonify({'count': count})

@app.route('/api/facts')
def get_facts():
    limit = request.args.get('limit', 100, type=int)
    cursor = conn.cursor()
    cursor.execute("SELECT statement FROM facts LIMIT ?", (limit,))
    facts = [{'statement': row[0]} for row in cursor.fetchall()]
    return jsonify({'facts': facts, 'count': len(facts)})

if __name__ == '__main__':
    print("LIGHTWEIGHT API on port 5003")
    app.run(host='127.0.0.1', port=5003, debug=False, threaded=True)
