"""
HAK/GAL Nischen Flask API
Read-only REST Endpoints für Nischen-System
GPT5-konform: GET /niches, /niches/{name}/stats, /niches/{name}/search
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
import json
import sqlite3
from typing import Dict, Any
import os

# Import der MCP-Tools für Code-Reuse
from niche_mcp_tools import NicheMCPTools

app = Flask(__name__)
CORS(app)  # Enable CORS für Frontend-Integration

# Konfiguration
NICHES_DIR = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/niches")
niche_tools = NicheMCPTools(str(NICHES_DIR))

# === API Endpoints ===

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "niche-api",
        "version": "1.0.0"
    })

@app.route('/niches', methods=['GET'])
def list_niches():
    """
    GET /niches
    Liste aller Nischen mit Basis-Statistiken
    """
    try:
        result = niche_tools.niche_list()
        
        # Response formatting
        return jsonify({
            "success": True,
            "data": {
                "niches": result.get("niches", []),
                "summary": {
                    "total_niches": result.get("total_niches", 0),
                    "total_facts": result.get("total_facts", 0)
                }
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/niches/<string:niche_name>/stats', methods=['GET'])
def get_niche_stats(niche_name: str):
    """
    GET /niches/{name}/stats
    Detaillierte Statistiken einer spezifischen Nische
    """
    try:
        result = niche_tools.niche_stats(niche_name)
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 404
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/niches/<string:niche_name>/search', methods=['GET'])
def search_niche(niche_name: str):
    """
    GET /niches/{name}/search?q=...&limit=...
    Suche in einer spezifischen Nische
    
    Query Parameters:
    - q: Suchbegriff (required)
    - limit: Max. Anzahl Ergebnisse (optional, default: 10, max: 100)
    """
    try:
        # Query-Parameter extrahieren
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', '10')
        
        # Validierung
        if not query:
            return jsonify({
                "success": False,
                "error": "Query parameter 'q' is required"
            }), 400
        
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
            elif limit > 100:
                limit = 100
        except ValueError:
            limit = 10
        
        # Suche durchführen
        result = niche_tools.niche_query(niche_name, query, limit)
        
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 404
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# === Zusätzliche Utility Endpoints ===

@app.route('/niches/<string:niche_name>/keywords', methods=['GET'])
def get_niche_keywords(niche_name: str):
    """
    GET /niches/{name}/keywords
    Gibt nur die Keywords einer Nische zurück
    """
    try:
        config_path = NICHES_DIR / "niches_config.json"
        
        if not config_path.exists():
            return jsonify({
                "success": False,
                "error": "No niches configured"
            }), 404
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if niche_name not in config:
            return jsonify({
                "success": False,
                "error": f"Niche '{niche_name}' not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": {
                "niche": niche_name,
                "keywords": config[niche_name].get("keywords", []),
                "threshold": config[niche_name].get("threshold", 0.5)
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/niches/summary', methods=['GET'])
def get_system_summary():
    """
    GET /niches/summary
    Übersicht über das gesamte Nischen-System
    """
    try:
        result = niche_tools.niche_list()
        
        # Kategorisierung der Nischen
        categories = {
            "large": [],     # >100 Fakten
            "medium": [],    # 10-100 Fakten
            "small": [],     # 1-10 Fakten
            "empty": []      # 0 Fakten
        }
        
        for niche in result.get("niches", []):
            count = niche["fact_count"]
            if count == 0:
                categories["empty"].append(niche["name"])
            elif count <= 10:
                categories["small"].append(niche["name"])
            elif count <= 100:
                categories["medium"].append(niche["name"])
            else:
                categories["large"].append(niche["name"])
        
        return jsonify({
            "success": True,
            "data": {
                "total_niches": result.get("total_niches", 0),
                "total_facts": result.get("total_facts", 0),
                "categories": categories,
                "avg_facts_per_niche": round(
                    result.get("total_facts", 0) / max(result.get("total_niches", 1), 1),
                    1
                )
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# === Error Handler ===

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# === Standalone Server ===

if __name__ == '__main__':
    print("=== NISCHEN FLASK API ===")
    print("Endpoints:")
    print("  GET http://localhost:5003/niches")
    print("  GET http://localhost:5003/niches/{name}/stats")
    print("  GET http://localhost:5003/niches/{name}/search?q=...&limit=...")
    print("  GET http://localhost:5003/niches/{name}/keywords")
    print("  GET http://localhost:5003/niches/summary")
    print("\nStarting server on port 5003...")
    
    # Port 5003 um Konflikt mit HAK/GAL API (5002) zu vermeiden
    app.run(
        host='127.0.0.1',
        port=5003,
        debug=True
    )
