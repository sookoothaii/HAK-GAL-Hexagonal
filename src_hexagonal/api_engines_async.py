"""
Async Engine API - Non-blocking engine execution
"""
from flask import Blueprint, jsonify, request
import subprocess
import threading
import time
import uuid
from pathlib import Path

engines_async_bp = Blueprint('engines_async', __name__)

# Store running tasks
running_tasks = {}

def run_engine_async(task_id, engine_type, params):
    """Run engine in background thread"""
    try:
        running_tasks[task_id]['status'] = 'running'
        running_tasks[task_id]['start_time'] = time.time()
        
        if engine_type == 'thesis':
            engine_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/infrastructure/engines/thesis_fast.py")
        elif engine_type == 'aethelred':
            engine_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/infrastructure/engines/aethelred_fast.py")
        else:
            raise ValueError(f"Unknown engine: {engine_type}")
        
        duration = params.get('duration_minutes', 1)
        
        # Run the engine
        result = subprocess.run(
            ["python", str(engine_path), "-d", str(duration/60)],
            capture_output=True,
            text=True,
            timeout=duration * 60 + 30  # Extra 30 sec buffer
        )
        
        # Parse output
        output_lines = result.stdout.split('\n')
        patterns = []
        for line in output_lines:
            if 'Generated' in line or 'Added' in line:
                patterns.append(line.strip())
        
        # Update task result
        running_tasks[task_id].update({
            'status': 'completed',
            'result': {
                'success': True,
                'patterns_found': len(patterns),
                'summary': patterns[:10],
                'duration_minutes': duration
            },
            'end_time': time.time()
        })
        
    except Exception as e:
        running_tasks[task_id].update({
            'status': 'failed',
            'error': str(e),
            'end_time': time.time()
        })

@engines_async_bp.route('/api/engines/async/start', methods=['POST'])
def start_engine_async():
    """Start engine asynchronously - returns immediately"""
    data = request.get_json() or {}
    engine_type = data.get('engine', 'thesis')
    duration = data.get('duration_minutes', 1)
    
    # Create task ID
    task_id = str(uuid.uuid4())
    
    # Store task info
    running_tasks[task_id] = {
        'id': task_id,
        'engine': engine_type,
        'status': 'pending',
        'params': data
    }
    
    # Start in background thread
    thread = threading.Thread(
        target=run_engine_async,
        args=(task_id, engine_type, data)
    )
    thread.daemon = True
    thread.start()
    
    # Return immediately
    return jsonify({
        'task_id': task_id,
        'status': 'started',
        'message': f'{engine_type} engine started for {duration} minutes'
    })

@engines_async_bp.route('/api/engines/async/status/<task_id>', methods=['GET'])
def get_engine_status(task_id):
    """Check status of async engine task"""
    if task_id not in running_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = running_tasks[task_id]
    
    # Calculate runtime if still running
    if task['status'] == 'running' and 'start_time' in task:
        task['runtime_seconds'] = time.time() - task['start_time']
    
    return jsonify(task)

@engines_async_bp.route('/api/engines/async/list', methods=['GET'])
def list_running_engines():
    """List all engine tasks"""
    return jsonify({
        'tasks': list(running_tasks.values()),
        'running': len([t for t in running_tasks.values() if t['status'] == 'running']),
        'completed': len([t for t in running_tasks.values() if t['status'] == 'completed']),
        'failed': len([t for t in running_tasks.values() if t['status'] == 'failed'])
    })

@engines_async_bp.route('/api/engines/async/stop/<task_id>', methods=['POST'])
def stop_engine(task_id):
    """Stop a running engine task"""
    if task_id not in running_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    # TODO: Implement actual process killing
    running_tasks[task_id]['status'] = 'stopped'
    
    return jsonify({'message': 'Stop signal sent', 'task_id': task_id})
