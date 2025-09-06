"""
API Endpoint für Response Viewing
Füge dies zu hexagonal_api_enhanced_clean.py hinzu
"""

@app.route('/api/agent-bus/responses', methods=['GET'])
def get_all_responses():
    """Get all agent responses"""
    try:
        response_dir = Path("agent_responses")
        if not response_dir.exists():
            return jsonify({"error": "No responses found"}), 404
        
        index_file = response_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            return jsonify(index)
        else:
            return jsonify({"error": "No index found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent-bus/responses/<task_id>', methods=['GET'])
def get_response_by_task_id(task_id):
    """Get specific response by task ID"""
    try:
        response_dir = Path("agent_responses")
        
        # Search for the response file
        for root, dirs, files in os.walk(response_dir):
            for file in files:
                if task_id in file and file.endswith('.json'):
                    filepath = Path(root) / file
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    return jsonify(data)
        
        return jsonify({"error": f"No response found for task_id: {task_id}"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent-bus/responses/agent/<agent_name>', methods=['GET'])
def get_agent_responses(agent_name):
    """Get all responses from a specific agent"""
    try:
        agent_dir = Path("agent_responses") / "by_agent" / agent_name
        
        if not agent_dir.exists():
            return jsonify({"error": f"No responses found for agent: {agent_name}"}), 404
        
        responses = []
        for file in agent_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                responses.append(data)
        
        # Sort by timestamp (newest first)
        responses.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            "agent": agent_name,
            "count": len(responses),
            "responses": responses[:10]  # Return only last 10
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agent-bus/responses/latest/<agent_name>', methods=['GET'])
def get_latest_agent_response(agent_name):
    """Get the latest response from a specific agent"""
    try:
        latest_file = Path("agent_responses") / "by_agent" / agent_name / "latest.json"
        
        if not latest_file.exists():
            return jsonify({"error": f"No latest response found for agent: {agent_name}"}), 404
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
