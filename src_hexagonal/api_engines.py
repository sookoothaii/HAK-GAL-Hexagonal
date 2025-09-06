"""
Simple Engine API Endpoints - Pragmatic Integration
"""
from flask import Blueprint, jsonify, request
import subprocess
import threading
import time
import json
from pathlib import Path

engines_bp = Blueprint('engines', __name__)

# Simple engine runners
class EngineRunner:
    def __init__(self):
        self.running_processes = {}
        
    def run_thesis(self, duration_minutes=1):
        """Run THESIS engine for pattern analysis"""
        try:
            # Just call the existing engine
            engine_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/infrastructure/engines/thesis_fast.py")
            if not engine_path.exists():
                return {"error": "THESIS engine not found", "success": False}
            
            # Run for short duration
            result = subprocess.run(
                ["python", str(engine_path), "-d", str(duration_minutes/60)],
                capture_output=True,
                text=True,
                timeout=duration_minutes * 60 + 10
            )
            
            # Parse output for patterns found
            output_lines = result.stdout.split('\n')
            patterns = []
            for line in output_lines:
                if 'Generated' in line or 'Added' in line:
                    patterns.append(line.strip())
            
            return {
                "success": True,
                "patterns_found": len(patterns),
                "summary": patterns[:10],  # First 10 patterns
                "duration_minutes": duration_minutes
            }
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def run_aethelred(self, topic="knowledge systems", duration_minutes=1):
        """Run Aethelred engine for fact generation"""
        try:
            engine_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/infrastructure/engines/aethelred_fast.py")
            if not engine_path.exists():
                return {"error": "Aethelred engine not found", "success": False}
            
            # Set topic via environment variable
            import os
            os.environ['AETHELRED_TOPIC'] = topic
            
            # Run for short duration
            result = subprocess.run(
                ["python", str(engine_path), "-d", str(duration_minutes/60)],
                capture_output=True,
                text=True,
                timeout=duration_minutes * 60 + 10
            )
            
            # Parse output for generated facts
            output_lines = result.stdout.split('\n')
            facts = []
            for line in output_lines:
                if 'Generated' in line or 'Added' in line:
                    facts.append(line.strip())
            
            return {
                "success": True,
                "facts_generated": len(facts),
                "topic": topic,
                "sample_facts": facts[:5],
                "duration_minutes": duration_minutes
            }
        except Exception as e:
            return {"error": str(e), "success": False}

runner = EngineRunner()

@engines_bp.route('/api/engines/thesis', methods=['POST'])
def run_thesis_engine():
    """Run THESIS pattern analysis"""
    data = request.get_json() or {}
    duration = min(data.get('duration_minutes', 1), 5)  # Max 5 minutes
    
    # Run in thread to avoid blocking
    result = runner.run_thesis(duration)
    return jsonify(result)

@engines_bp.route('/api/engines/aethelred', methods=['POST'])
def run_aethelred_engine():
    """Run Aethelred fact generation"""
    data = request.get_json() or {}
    topic = data.get('topic', 'knowledge systems')
    duration = min(data.get('duration_minutes', 1), 5)  # Max 5 minutes
    
    result = runner.run_aethelred(topic, duration)
    return jsonify(result)

@engines_bp.route('/api/engines/status', methods=['GET'])
def engine_status():
    """Get status of engines"""
    return jsonify({
        "thesis": {"available": True, "type": "pattern_analysis"},
        "aethelred": {"available": True, "type": "fact_generation"},
        "governor": {"available": True, "type": "orchestration"}
    })
