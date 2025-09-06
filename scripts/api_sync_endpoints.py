"""
API Enhancement for Synchronous Agent Communication
Füge diese Endpoints zu hexagonal_api_enhanced_clean.py hinzu
"""

import threading
import time
from queue import Queue, Empty

# Global response storage for synchronous communication
agent_response_queues = {}
agent_response_lock = threading.Lock()

@app.route('/api/agent-bus/delegate-sync', methods=['POST'])
@require_api_key
def delegate_task_synchronous():
    """
    Synchronous task delegation - wartet auf Antwort
    
    Request body:
    {
        "target_agent": "gemini|cursor|claude_cli|claude_desktop",
        "task_description": "Task to complete",
        "context": {},
        "timeout": 30  # optional, default 30 seconds
    }
    
    Returns: Die tatsächliche Agent-Antwort
    """
    try:
        data = request.json
        target_agent = data.get('target_agent')
        task_description = data.get('task_description')
        context = data.get('context', {})
        timeout = data.get('timeout', 30)
        
        if not target_agent or not task_description:
            return jsonify({"error": "Missing target_agent or task_description"}), 400
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Create response queue for this task
        response_queue = Queue()
        with agent_response_lock:
            agent_response_queues[task_id] = response_queue
        
        # Delegate task
        adapter = get_agent_adapter(target_agent, socketio)
        if not adapter:
            return jsonify({"error": f"Unknown agent: {target_agent}"}), 400
        
        # Start delegation in thread
        def delegate_and_monitor():
            result = adapter.dispatch(task_description, context)
            # Monitor for response
            response = monitor_for_response(target_agent, task_id, timeout)
            response_queue.put(response)
        
        thread = threading.Thread(target=delegate_and_monitor)
        thread.start()
        
        # Wait for response
        try:
            response = response_queue.get(timeout=timeout)
            
            # Clean up
            with agent_response_lock:
                del agent_response_queues[task_id]
            
            return jsonify({
                "task_id": task_id,
                "agent": target_agent,
                "status": "completed",
                "response": response
            })
            
        except Empty:
            # Timeout
            with agent_response_lock:
                del agent_response_queues[task_id]
            
            return jsonify({
                "task_id": task_id,
                "agent": target_agent,
                "status": "timeout",
                "error": f"No response after {timeout} seconds"
            }), 408
            
    except Exception as e:
        logger.error(f"Error in synchronous delegation: {e}")
        return jsonify({"error": str(e)}), 500


def monitor_for_response(agent, task_id, timeout):
    """Monitor all possible locations for agent response"""
    
    start_time = time.time()
    response_dir = Path("agent_responses")
    
    while time.time() - start_time < timeout:
        # Check agent_responses directory
        for file in response_dir.rglob(f"*{task_id}*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('task_id') == task_id:
                    response = data.get('response', {})
                    if response.get('status') == 'completed':
                        return response.get('result', 'Task completed')
            except:
                pass
        
        # Check latest response for agent
        latest_file = response_dir / "by_agent" / agent / "latest.json"
        if latest_file.exists():
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if this is newer than our request
                if data.get('timestamp', '') > datetime.now().isoformat()[:19]:
                    response = data.get('response', {})
                    if response.get('status') == 'completed':
                        return response.get('result', 'Task completed')
            except:
                pass
        
        # Special check for Gemini
        if agent == "gemini":
            gemini_file = response_dir / "gemini_latest_full_response.txt"
            if gemini_file.exists():
                mod_time = gemini_file.stat().st_mtime
                if time.time() - mod_time < 60:
                    with open(gemini_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if task_id in content:
                        # Extract the actual response
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'Full Response:' in line and i + 1 < len(lines):
                                return '\n'.join(lines[i+1:])
        
        time.sleep(1)
    
    return None


@app.route('/api/agent-bus/chat', methods=['POST'])
@require_api_key
def chat_with_agent():
    """
    Simplified chat interface for agent communication
    
    Request body:
    {
        "agent": "gemini|cursor|claude_cli|claude_desktop",
        "message": "Your message"
    }
    
    Returns: The agent's response as plain text
    """
    try:
        data = request.json
        agent = data.get('agent')
        message = data.get('message')
        
        if not agent or not message:
            return jsonify({"error": "Missing agent or message"}), 400
        
        # Use synchronous delegation
        response = requests.post(
            "http://127.0.0.1:5002/api/agent-bus/delegate-sync",
            headers={"X-API-Key": request.headers.get('X-API-Key')},
            json={
                "target_agent": agent,
                "task_description": message,
                "timeout": 30
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "agent": agent,
                "message": message,
                "response": data.get('response', 'No response')
            })
        else:
            return jsonify({
                "agent": agent,
                "message": message,
                "response": "Error: No response from agent"
            }), response.status_code
            
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({"error": str(e)}), 500


# WebSocket support for real-time communication
@socketio.on('agent_request')
def handle_agent_request(data):
    """Handle real-time agent requests via WebSocket"""
    
    agent = data.get('agent')
    message = data.get('message')
    client_id = request.sid
    
    if not agent or not message:
        emit('error', {'message': 'Missing agent or message'})
        return
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Send acknowledgment
    emit('request_acknowledged', {
        'task_id': task_id,
        'agent': agent
    })
    
    # Delegate in background
    def delegate_and_respond():
        adapter = get_agent_adapter(agent, socketio)
        if adapter:
            # Dispatch task
            result = adapter.dispatch(message, {'websocket': True})
            
            # Monitor for response
            response = monitor_for_response(agent, task_id, 30)
            
            # Send response back via WebSocket
            socketio.emit('agent_response', {
                'task_id': task_id,
                'agent': agent,
                'response': response or 'No response received'
            }, room=client_id)
    
    thread = threading.Thread(target=delegate_and_respond)
    thread.daemon = True
    thread.start()
