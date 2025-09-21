"""
Claude Desktop Integration Helper
=================================

This script helps you work with the file-based exchange method
when Claude Desktop doesn't support MCP or URL schemes.
"""

import json
import os
from pathlib import Path
import time

def create_response_for_request(request_file):
    """Create a response file for a given request"""
    
    # Read the request
    with open(request_file, 'r') as f:
        request_data = json.load(f)
    
    print(f"\nRequest ID: {request_data['id']}")
    print(f"Task: {request_data['task']}")
    print(f"Context: {json.dumps(request_data['context'], indent=2)}")
    
    # Get user response
    print("\n" + "="*60)
    print("MANUAL RESPONSE NEEDED")
    print("="*60)
    print("\nPlease copy this task to Claude Desktop manually and paste the response below.")
    print("(Type 'END' on a new line when done)\n")
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    response_text = '\n'.join(lines)
    
    # Create response file
    response_file = request_file.replace('.json', '_response.json')
    response_data = {
        "request_id": request_data['id'],
        "response": response_text,
        "timestamp": time.time(),
        "processed_by": "manual_helper"
    }
    
    with open(response_file, 'w') as f:
        json.dump(response_data, f, indent=2)
    
    print(f"\n✅ Response saved to: {response_file}")
    return response_file

def watch_for_requests():
    """Watch the exchange directory for new requests"""
    
    exchange_dir = Path("claude_desktop_exchange")
    exchange_dir.mkdir(exist_ok=True)
    
    print("Watching for Claude Desktop requests...")
    print(f"Directory: {exchange_dir.absolute()}")
    print("\nPress Ctrl+C to stop\n")
    
    processed = set()
    
    try:
        while True:
            # Check for request files
            for file in exchange_dir.glob("request_*.json"):
                if file.name not in processed and not file.name.endswith("_response.json"):
                    print(f"\n🆕 New request found: {file.name}")
                    processed.add(file.name)
                    
                    # Check if response already exists
                    response_file = file.parent / file.name.replace('.json', '_response.json')
                    if response_file.exists():
                        print(f"   Response already exists: {response_file.name}")
                    else:
                        print(f"   No response yet. Creating manual response...")
                        create_response_for_request(str(file))
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nStopped watching for requests.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        watch_for_requests()
    else:
        # Check for existing request files
        exchange_dir = Path("claude_desktop_exchange")
        if exchange_dir.exists():
            requests = list(exchange_dir.glob("request_*.json"))
            # Filter out response files
            requests = [r for r in requests if not r.name.endswith('_response.json')]
            pending = [r for r in requests if not (r.parent / r.name.replace('.json', '_response.json')).exists()]
            
            if pending:
                print(f"Found {len(pending)} pending request(s):")
                for i, req in enumerate(pending):
                    print(f"{i+1}. {req.name}")
                
                choice = input("\nWhich request to process? (number or 'all'): ")
                
                if choice.lower() == 'all':
                    for req in pending:
                        create_response_for_request(str(req))
                else:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(pending):
                            create_response_for_request(str(pending[idx]))
                    except:
                        print("Invalid choice")
            else:
                print("No pending requests found.")
                print("\nUsage:")
                print("  python claude_desktop_helper.py        # Process pending requests")
                print("  python claude_desktop_helper.py watch  # Watch for new requests")
