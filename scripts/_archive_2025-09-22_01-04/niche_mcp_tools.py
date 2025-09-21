"""
HAK/GAL Nischen MCP-Tools
Read-only Tools für Integration in MCP-Server
Basierend auf GPT5-Empfehlung
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any

class NicheMCPTools:
    """Read-only MCP-Tools für Nischen-System"""
    
    def __init__(self, niches_dir: str = "niches"):
        self.niches_dir = Path(niches_dir)
        self.config_path = self.niches_dir / "niches_config.json"
    
    def niche_list(self) -> Dict[str, Any]:
        """
        MCP Tool: Liste aller Nischen mit Basis-Stats
        Returns: {"niches": [...], "total_facts": N, "total_niches": N}
        """
        try:
            if not self.config_path.exists():
                return {
                    "error": "No niches configured",
                    "niches": [],
                    "total_facts": 0,
                    "total_niches": 0
                }
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            niches = []
            total_facts = 0
            
            for name, data in config.items():
                niche_db = self.niches_dir / f"{name}.db"
                fact_count = 0
                
                if niche_db.exists():
                    conn = sqlite3.connect(niche_db, timeout=5.0)
                    conn.execute('PRAGMA query_only = ON')  # Read-only mode
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM facts')
                    fact_count = cursor.fetchone()[0]
                    conn.close()
                
                niches.append({
                    "name": name,
                    "fact_count": fact_count,
                    "keywords": data.get("keywords", []),
                    "threshold": data.get("threshold", 0.5),
                    "last_updated": data.get("last_updated", "unknown")
                })
                total_facts += fact_count
            
            return {
                "niches": niches,
                "total_facts": total_facts,
                "total_niches": len(niches)
            }
            
        except Exception as e:
            return {"error": str(e), "niches": []}
    
    def niche_stats(self, niche_name: str) -> Dict[str, Any]:
        """
        MCP Tool: Detaillierte Statistiken einer Nische
        Args: niche_name - Name der Nische
        Returns: Erweiterte Stats inkl. Telemetrie
        """
        try:
            # Config laden
            if not self.config_path.exists():
                return {"error": "No niches configured"}
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            if niche_name not in config:
                return {"error": f"Niche '{niche_name}' not found"}
            
            niche_data = config[niche_name]
            niche_db = self.niches_dir / f"{niche_name}.db"
            
            if not niche_db.exists():
                return {"error": f"Niche database not found"}
            
            # Statistiken sammeln
            conn = sqlite3.connect(niche_db, timeout=5.0)
            conn.execute('PRAGMA query_only = ON')
            cursor = conn.cursor()
            
            # Basis-Stats
            cursor.execute('SELECT COUNT(*) FROM facts')
            fact_count = cursor.fetchone()[0]
            
            # Relevanz-Verteilung
            cursor.execute('''
                SELECT 
                    MIN(relevance_score) as min_score,
                    MAX(relevance_score) as max_score,
                    AVG(relevance_score) as avg_score
                FROM facts
            ''')
            relevance_stats = cursor.fetchone()
            
            # Top-Keywords nach Häufigkeit
            cursor.execute('''
                SELECT fact_text, relevance_score 
                FROM facts 
                ORDER BY relevance_score DESC 
                LIMIT 5
            ''')
            top_facts = [
                {"fact": row[0][:100], "score": row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Import-Telemetrie (falls vorhanden)
            telemetry = {}
            try:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as import_runs,
                        SUM(facts_imported) as total_imported,
                        AVG(duration_seconds) as avg_duration,
                        MAX(timestamp) as last_import
                    FROM import_stats
                ''')
                tel_data = cursor.fetchone()
                if tel_data[0] > 0:  # Wenn Import-Stats existieren
                    telemetry = {
                        "import_runs": tel_data[0],
                        "total_imported": tel_data[1],
                        "avg_import_duration": round(tel_data[2], 3) if tel_data[2] else 0,
                        "last_import": tel_data[3]
                    }
            except sqlite3.OperationalError:
                # import_stats Tabelle existiert nicht
                pass
            
            conn.close()
            
            return {
                "niche": niche_name,
                "fact_count": fact_count,
                "keywords": niche_data.get("keywords", []),
                "threshold": niche_data.get("threshold", 0.5),
                "created_at": niche_data.get("created_at"),
                "last_updated": niche_data.get("last_updated"),
                "relevance_stats": {
                    "min": round(relevance_stats[0] or 0, 3),
                    "max": round(relevance_stats[1] or 0, 3),
                    "avg": round(relevance_stats[2] or 0, 3)
                },
                "top_facts": top_facts,
                "telemetry": telemetry
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def niche_query(self, niche_name: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        MCP Tool: Suche in einer Nische
        Args:
            niche_name - Name der Nische
            query - Suchbegriff
            limit - Max. Anzahl Ergebnisse (default: 10)
        Returns: Suchergebnisse sortiert nach Relevanz
        """
        try:
            # Validierung
            if not niche_name:
                return {"error": "niche_name required"}
            if not query:
                return {"error": "query required"}
            if limit < 1 or limit > 100:
                limit = 10
            
            niche_db = self.niches_dir / f"{niche_name}.db"
            if not niche_db.exists():
                return {"error": f"Niche '{niche_name}' not found"}
            
            # Suche durchführen
            conn = sqlite3.connect(niche_db, timeout=5.0)
            conn.execute('PRAGMA query_only = ON')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT fact_text, relevance_score
                FROM facts
                WHERE LOWER(fact_text) LIKE LOWER(?)
                ORDER BY relevance_score DESC, fact_text
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "fact": row[0],
                    "relevance": round(row[1], 3),
                    "preview": row[0][:150] + "..." if len(row[0]) > 150 else row[0]
                })
            
            # Gesamt-Treffer zählen
            cursor.execute('''
                SELECT COUNT(*)
                FROM facts
                WHERE LOWER(fact_text) LIKE LOWER(?)
            ''', (f'%{query}%',))
            total_matches = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "niche": niche_name,
                "query": query,
                "total_matches": total_matches,
                "returned": len(results),
                "limit": limit,
                "results": results
            }
            
        except Exception as e:
            return {"error": str(e)}

# === Integration in MCP-Server ===
def register_niche_tools(mcp_server):
    """
    Registriert die Nischen-Tools im MCP-Server
    Füge dies in hakgal_mcp_ultimate.py ein
    """
    tools = NicheMCPTools()
    
    mcp_server.register_tool(
        name="niche_list",
        description="Liste aller Nischen mit Basis-Statistiken",
        parameters={},
        handler=lambda: tools.niche_list()
    )
    
    mcp_server.register_tool(
        name="niche_stats",
        description="Detaillierte Statistiken einer Nische",
        parameters={
            "niche_name": {"type": "string", "description": "Name der Nische"}
        },
        handler=lambda params: tools.niche_stats(params["niche_name"])
    )
    
    mcp_server.register_tool(
        name="niche_query",
        description="Suche in einer spezifischen Nische",
        parameters={
            "niche_name": {"type": "string", "description": "Name der Nische"},
            "query": {"type": "string", "description": "Suchbegriff"},
            "limit": {"type": "integer", "description": "Max. Ergebnisse", "default": 10}
        },
        handler=lambda params: tools.niche_query(
            params["niche_name"],
            params["query"],
            params.get("limit", 10)
        )
    )

# === Standalone Test ===
if __name__ == "__main__":
    import os
    os.chdir("D:\\MCP Mods\\HAK_GAL_HEXAGONAL")
    
    tools = NicheMCPTools()
    
    print("=== NISCHEN MCP-TOOLS TEST ===\n")
    
    # Test 1: Liste
    print("1. niche_list():")
    result = tools.niche_list()
    print(f"   {result['total_niches']} Nischen, {result['total_facts']} Fakten gesamt")
    
    # Test 2: Stats
    if result['niches']:
        test_niche = result['niches'][0]['name']
        print(f"\n2. niche_stats('{test_niche}'):")
        stats = tools.niche_stats(test_niche)
        print(f"   {stats.get('fact_count', 0)} Fakten")
        print(f"   Relevanz: {stats.get('relevance_stats', {}).get('avg', 0):.3f} (avg)")
        
        # Test 3: Query
        print(f"\n3. niche_query('{test_niche}', 'HAK_GAL'):")
        query_result = tools.niche_query(test_niche, 'HAK_GAL', 2)
        print(f"   {query_result.get('total_matches', 0)} Treffer")
        for r in query_result.get('results', [])[:2]:
            print(f"   [{r['relevance']}] {r['preview'][:60]}...")
    
    print("\n✅ MCP-Tools bereit für Integration!")
