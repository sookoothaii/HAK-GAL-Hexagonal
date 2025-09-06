# Integration snippet für hakgal_mcp_ultimate.py
# Füge dies am Anfang der Datei hinzu (nach den imports):

try:
    from meta_tools import META_TOOLS
    meta_tools_available = True
except ImportError:
    meta_tools_available = False
    META_TOOLS = None

# In der handle_list_tools Methode, füge diese Tools hinzu:

if meta_tools_available:
    tools.extend([
        {
            "name": "consensus_evaluator",
            "description": "Evaluiert Konsens zwischen mehreren Tool/LLM-Outputs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Eindeutige Task-ID"},
                    "outputs": {
                        "type": "array",
                        "description": "Liste von Tool-Outputs",
                        "items": {
                            "type": "object",
                            "properties": {
                                "tool_name": {"type": "string"},
                                "model": {"type": "string"},
                                "content": {"type": "string"},
                                "confidence": {"type": "number"}
                            }
                        }
                    },
                    "method": {
                        "type": "string",
                        "enum": ["majority_vote", "semantic_similarity", "kappa"],
                        "default": "semantic_similarity"
                    },
                    "threshold": {"type": "number", "default": 0.7}
                },
                "required": ["task_id", "outputs"]
            }
        },
        {
            "name": "reliability_checker",
            "description": "Prüft Konsistenz von Tools über mehrere Ausführungen",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string"},
                    "task": {"type": "string", "description": "Task-Beschreibung zum Testen"},
                    "n_runs": {"type": "integer", "default": 5}
                },
                "required": ["tool_name", "task"]
            }
        },
        {
            "name": "bias_detector",
            "description": "Erkennt systematische Verzerrungen in Tool-Outputs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tool_outputs": {
                        "type": "object",
                        "description": "Dictionary mit tool_name: [outputs]"
                    },
                    "baseline": {"type": "string", "default": "balanced"}
                },
                "required": ["tool_outputs"]
            }
        },
        {
            "name": "delegation_optimizer",
            "description": "Optimiert Task-Delegation basierend auf Performance",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_description": {"type": "string"},
                    "available_tools": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "context": {"type": "object"}
                },
                "required": ["task_description", "available_tools"]
            }
        }
    ])

# In der handle_tool_call Methode, füge diese Cases hinzu:

elif tool_name == "consensus_evaluator" and meta_tools_available:
    task_id = tool_args.get("task_id", "")
    outputs = tool_args.get("outputs", [])
    method = tool_args.get("method", "semantic_similarity")
    threshold = tool_args.get("threshold", 0.7)
    
    try:
        evaluator = META_TOOLS["consensus_evaluator"]
        result_data = evaluator.evaluate_consensus(task_id, outputs, method, threshold)
        
        text = f"""
🔬 **Konsens-Analyse**
Task ID: {result_data['task_id']}
Methode: {result_data['method']}

📊 **Ergebnisse:**
• Konsens-Score: {result_data['consensus_score']:.1%}
• Confidence: {result_data['confidence']}
• Synthese: {result_data['synthesis']}

📈 **Tool-Ranking:**
"""
        for rank in result_data['ranking'][:3]:
            text += f"  {rank['tool_name']}: {rank['alignment_score']:.1%}\n"
        
        if result_data['divergences']:
            text += "\n⚠️ **Divergenzen:**\n"
            for div in result_data['divergences'][:3]:
                text += f"  • {div['tool']}: {', '.join(div.get('unique_focus', []))}\n"
        
        result = {"content": [{"type": "text", "text": text}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}

elif tool_name == "reliability_checker" and meta_tools_available:
    tool_to_check = tool_args.get("tool_name", "")
    task = tool_args.get("task", "")
    n_runs = tool_args.get("n_runs", 5)
    
    try:
        # Simuliere mehrfache Ausführung (in Produktion: echte Delegation)
        def mock_task(**kwargs):
            # Hier würde normalerweise delegate_task aufgerufen
            import random
            responses = [
                "Response A with consistent elements",
                "Response A with consistent elements and variation",
                "Response B different approach",
                "Response A with consistent elements",
                "Response A with minor changes"
            ]
            return random.choice(responses)
        
        checker = META_TOOLS["reliability_checker"]
        result_data = checker.check_reliability(
            tool_to_check,
            mock_task,
            {"task": task},
            n_runs
        )
        
        text = f"""
🔄 **Reliability Check**
Tool: {result_data['tool_name']}
Runs: {result_data['n_runs']}

📊 **Metriken:**
• Konsistenz-Score: {result_data['consistency_score']:.1%}
• Fleiss' Kappa: {result_data['fleiss_kappa']:.2f}
• Durchschn. Laufzeit: {result_data['avg_execution_time']}s
• Stabilität: {result_data['stability']}
• Fehler: {result_data['errors']}/{n_runs}

💡 **Empfehlung:** {"✅ Tool ist zuverlässig" if result_data['stability'] == 'STABLE' else "⚠️ Tool zeigt Inkonsistenzen"}
"""
        result = {"content": [{"type": "text", "text": text}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}

elif tool_name == "bias_detector" and meta_tools_available:
    tool_outputs = tool_args.get("tool_outputs", {})
    baseline = tool_args.get("baseline", "balanced")
    
    try:
        detector = META_TOOLS["bias_detector"]
        result_data = detector.detect_bias(tool_outputs, baseline)
        
        text = f"""
🔍 **Bias-Analyse**
Analysierte Tools: {len(tool_outputs)}
Baseline: {baseline}

📊 **Bias-Scores:**
"""
        for bias in result_data['biases']:
            text += f"\n**{bias['tool_name']}:**\n"
            text += f"  • Gesamt-Bias: {bias['overall_bias_score']:.1%}\n"
            text += f"  • Themen-Bias: {bias['theme_bias']['score']:.1%}\n"
            text += f"  • Längen-Bias: {bias['length_bias']['score']:.1%}\n"
            text += f"  • Sentiment-Bias: {bias['sentiment_bias']['score']:.1%}\n"
        
        if result_data['outliers']:
            text += f"\n⚠️ **Ausreißer:** {', '.join(result_data['outliers'])}\n"
        
        text += f"\n💡 **Empfehlung:** {result_data['recommendation']}"
        
        result = {"content": [{"type": "text", "text": text}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}

elif tool_name == "delegation_optimizer" and meta_tools_available:
    task_description = tool_args.get("task_description", "")
    available_tools = tool_args.get("available_tools", [])
    context = tool_args.get("context", {})
    
    try:
        optimizer = META_TOOLS["delegation_optimizer"]
        result_data = optimizer.optimize_delegation(
            task_description,
            available_tools,
            context
        )
        
        text = f"""
🎯 **Delegation-Optimierung**
Task: {task_description[:100]}...
Task-Hash: {result_data['task_hash']}

📊 **Empfohlene Tools:**
"""
        for tool in result_data['recommended_tools']:
            text += f"  • {tool['tool']}: Score {tool['score']:.1%} (Conf: {tool['confidence']})\n"
        
        text += f"\n🎮 **Strategie:** {result_data['strategy']}\n"
        
        if result_data['fallback_tool']:
            text += f"🔄 **Fallback:** {result_data['fallback_tool']}\n"
        
        features = result_data['task_features']
        text += f"\n📋 **Task-Features:**\n"
        text += f"  • Komplexität: {features['complexity']:.1f}\n"
        text += f"  • Hat Daten: {features['has_data']}\n"
        text += f"  • Hat Analyse: {features['has_analysis']}\n"
        
        result = {"content": [{"type": "text", "text": text}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
