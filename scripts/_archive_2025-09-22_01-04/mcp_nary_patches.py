#!/usr/bin/env python3
"""
MCP Server Tool Updates für n-äre Facts
Patches für die defekten HAK_GAL Tools
Integration in hakgal_mcp_ultimate.py
Author: Claude
Date: 2025-09-19
"""

import sqlite3
import re
from typing import List, Dict, Optional, Tuple
import json
from difflib import SequenceMatcher

# Import die Fixed Tools
from fix_nary_tools import NaryFactParser, FixedNaryTools

# Datenbank-Pfad
DB_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'

# Globale Instanz der reparierten Tools
fixed_tools = FixedNaryTools(DB_PATH)
parser = NaryFactParser()


async def semantic_similarity_nary(statement: str, limit: int = 50, threshold: float = 0.8) -> str:
    """
    MCP Tool Handler für semantic_similarity mit n-ärer Fact Unterstützung
    """
    try:
        results = fixed_tools.semantic_similarity(statement, threshold, limit)
        
        if not results:
            return "Keine ähnlichen Facts gefunden."
        
        # Formatiere Ausgabe
        output = f"Gefundene {len(results)} ähnliche Facts:\n"
        for score, fact in results:
            output += f"  Score {score:.3f}: {fact}\n"
        
        return output
        
    except Exception as e:
        return f"Fehler bei semantic_similarity: {str(e)}"


async def consistency_check_nary(limit: int = 1000) -> str:
    """
    MCP Tool Handler für consistency_check mit n-ärer Fact Unterstützung
    """
    try:
        inconsistencies = fixed_tools.consistency_check(limit)
        
        if not inconsistencies:
            return "✓ Keine Inkonsistenzen gefunden."
        
        # Formatiere Ausgabe
        output = f"Gefundene {len(inconsistencies)} potentielle Inkonsistenzen:\n"
        for fact1, fact2, reason in inconsistencies[:10]:  # Zeige max 10
            output += f"\n{reason}:\n"
            output += f"  1. {fact1}\n"
            output += f"  2. {fact2}\n"
        
        if len(inconsistencies) > 10:
            output += f"\n... und {len(inconsistencies) - 10} weitere."
        
        return output
        
    except Exception as e:
        return f"Fehler bei consistency_check: {str(e)}"


async def validate_facts_nary(limit: int = 1000) -> str:
    """
    MCP Tool Handler für validate_facts mit n-ärer Fact Unterstützung
    """
    try:
        validation = fixed_tools.validate_facts(limit)
        
        # Formatiere Ausgabe
        output = "=== FACT VALIDATION REPORT ===\n\n"
        output += f"Analysierte Facts: {limit}\n"
        output += f"✓ Valide: {len(validation['valid'])}\n"
        output += f"✗ Syntax Fehler: {len(validation['syntax_error'])}\n"
        output += f"✗ Fehlende Prädikate: {len(validation['missing_predicate'])}\n"
        output += f"✗ Leere Argumente: {len(validation['empty_arguments'])}\n"
        output += f"⚠ Verdächtige Werte: {len(validation['suspicious_values'])}\n"
        output += f"✓ Korrekte Q(...) Notation: {len(validation['well_formed_quantity'])}\n"
        
        # Zeige Beispiele von Problemen
        if validation['syntax_error']:
            output += "\nBeispiele Syntax-Fehler:\n"
            for fact in validation['syntax_error'][:3]:
                output += f"  • {fact}\n"
        
        if validation['suspicious_values']:
            output += "\nBeispiele verdächtiger Werte:\n"
            for fact in validation['suspicious_values'][:3]:
                output += f"  • {fact}\n"
        
        return output
        
    except Exception as e:
        return f"Fehler bei validate_facts: {str(e)}"


async def inference_chain_nary(start_fact: str, max_depth: int = 5) -> str:
    """
    MCP Tool Handler für inference_chain mit n-ärer Fact Unterstützung
    """
    try:
        chains = fixed_tools.inference_chain(start_fact, max_depth)
        
        if not chains:
            return f"Keine Inferenzketten gefunden ausgehend von: {start_fact}"
        
        # Formatiere Ausgabe
        output = f"Gefundene {len(chains)} Inferenzketten:\n\n"
        
        for i, chain in enumerate(chains[:5]):  # Zeige max 5 Ketten
            output += f"Kette {i+1} (Länge {len(chain)}):\n"
            for j, fact in enumerate(chain):
                if j == 0:
                    output += f"  START → {fact}\n"
                else:
                    # Finde gemeinsame Entity mit vorherigem Fact
                    prev_entities = parser.extract_entities(chain[j-1])
                    curr_entities = parser.extract_entities(fact)
                    common = set(prev_entities) & set(curr_entities)
                    if common:
                        output += f"  [{', '.join(common)}] → {fact}\n"
                    else:
                        output += f"  → {fact}\n"
            output += "\n"
        
        if len(chains) > 5:
            output += f"... und {len(chains) - 5} weitere Ketten."
        
        return output
        
    except Exception as e:
        return f"Fehler bei inference_chain: {str(e)}"


# Integration Helper für MCP Server
def patch_mcp_server_tools():
    """
    Patcht die defekten Tools im MCP Server
    Diese Funktion sollte beim Start des MCP Servers aufgerufen werden
    """
    print("=== PATCHING MCP TOOLS FÜR N-ÄRE FACTS ===")
    print("✓ semantic_similarity -> semantic_similarity_nary")
    print("✓ consistency_check -> consistency_check_nary")
    print("✓ validate_facts -> validate_facts_nary")
    print("✓ inference_chain -> inference_chain_nary")
    print("=== PATCHES ANGEWENDET ===\n")
    
    return {
        'semantic_similarity': semantic_similarity_nary,
        'consistency_check': consistency_check_nary,
        'validate_facts': validate_facts_nary,
        'inference_chain': inference_chain_nary
    }


# Tool Definitionen für MCP Server
NARY_TOOL_DEFINITIONS = [
    {
        "name": "semantic_similarity",
        "description": "Finde semantisch ähnliche Fakten (n-är kompatibel)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "statement": {"type": "string", "description": "Statement zum Vergleich"},
                "limit": {"type": "integer", "default": 50},
                "threshold": {"type": "number", "default": 0.8, "minimum": 0, "maximum": 1}
            },
            "required": ["statement"]
        }
    },
    {
        "name": "consistency_check",
        "description": "Prüfe auf widerspruechliche Fakten (n-är kompatibel)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 1000}
            }
        }
    },
    {
        "name": "validate_facts",
        "description": "Validiere Syntax der Fakten (n-är kompatibel)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 1000}
            }
        }
    },
    {
        "name": "inference_chain",
        "description": "Baue Kette verwandter Fakten (n-är kompatibel)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_fact": {"type": "string", "description": "Start-Fakt"},
                "max_depth": {"type": "integer", "default": 5}
            },
            "required": ["start_fact"]
        }
    }
]


# Test der gepatchten Tools
async def test_patched_tools():
    """Testet die gepatchten MCP Tools"""
    print("=== TESTE GEPATCHE MCP TOOLS ===\n")
    
    # Test semantic_similarity
    result = await semantic_similarity_nary(
        "ChemicalReaction(test, test2, test3, test4, test5)",
        limit=3,
        threshold=0.3
    )
    print("1. semantic_similarity_nary:")
    print(result[:200] + "...\n" if len(result) > 200 else result + "\n")
    
    # Test consistency_check
    result = await consistency_check_nary(limit=50)
    print("2. consistency_check_nary:")
    print(result[:200] + "...\n" if len(result) > 200 else result + "\n")
    
    # Test validate_facts
    result = await validate_facts_nary(limit=20)
    print("3. validate_facts_nary:")
    print(result[:300] + "...\n" if len(result) > 300 else result + "\n")
    
    # Test inference_chain
    result = await inference_chain_nary(
        "ChemicalReaction(H2, O2, H2O, combustion, exothermic, 2800K)",
        max_depth=3
    )
    print("4. inference_chain_nary:")
    print(result[:300] + "...\n" if len(result) > 300 else result + "\n")
    
    print("=== TESTS ABGESCHLOSSEN ===")


if __name__ == "__main__":
    import asyncio
    
    # Führe Tests aus
    asyncio.run(test_patched_tools())
    
    # Zeige Integration Instructions
    print("\n" + "="*60)
    print("INTEGRATION INSTRUCTIONS:")
    print("="*60)
    print("""
1. Öffne hakgal_mcp_ultimate.py oder filesystem_mcp/hak_gal_filesystem.py

2. Füge am Anfang hinzu:
   from mcp_nary_patches import patch_mcp_server_tools, NARY_TOOL_DEFINITIONS

3. Ersetze die Tool Handler:
   patched_tools = patch_mcp_server_tools()
   
4. Im server.call_tool Handler, ersetze:
   if name == "semantic_similarity":
       return await patched_tools['semantic_similarity'](params['statement'], 
                                                          params.get('limit', 50),
                                                          params.get('threshold', 0.8))
   
5. Aktualisiere die Tool-Definitionen in der tools Liste mit NARY_TOOL_DEFINITIONS

6. Restart MCP Server:
   python hakgal_mcp_ultimate.py
""")
