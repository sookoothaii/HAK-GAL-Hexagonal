import subprocess
import json
import os
import logging
import sys
import time
from typing import Dict, Any, Optional

class MCPBridge:
    def __init__(self, mcp_path: str = "ultimate_mcp/hakgal_mcp_ultimate.py"):
        self.mcp_path = mcp_path
        self.process = None
        self.logger = logging.getLogger('MCPBridge')
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def _start_process(self):
        if self.process and self.process.poll() is None: # Process is still running
            return
        
        # Ensure we are in the correct directory to launch MCP
        mcp_dir = os.path.dirname(self.mcp_path)
        if not mcp_dir: # If mcp_path is just a filename, assume current dir
            mcp_dir = "."
        
        # Use the venv's python executable
        python_executable = os.path.join(os.path.dirname(sys.executable), "python.exe")
        
        self.logger.info(f"Starting MCP process: {python_executable} {self.mcp_path} from {mcp_dir}")
        
        self.process = subprocess.Popen(
            [python_executable, self.mcp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, # Use text mode for stdin/stdout
            bufsize=1, # Line-buffered
            cwd=mcp_dir # Run from MCP's directory
        )
        self.logger.info("MCP process started.")

    def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._start_process() # Ensure process is running
        
        request_id = int(time.time() * 1000) # Simple unique ID
        json_rpc_request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id
        }
        
        request_str = json.dumps(json_rpc_request) + "\n"
        self.logger.debug(f"Sending request: {request_str.strip()}")
        
        try:
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
            
            # Read response - MCP server should send one line per response
            response_str = self.process.stdout.readline()
            self.logger.debug(f"Received response: {response_str.strip()}")
            
            response_json = json.loads(response_str)
            return response_json
        except Exception as e:
            self.logger.error(f"Error sending/receiving from MCP: {e}")
            return {"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}, "id": request_id}

    def close(self):
        if self.process:
            self.process.stdin.close()
            self.process.stdout.close()
            self.process.stderr.close()
            self.process.terminate()
            self.process.wait(timeout=5)
            self.logger.info("MCP process closed.")

# Example usage (for testing this bridge)
if __name__ == "__main__":
    # Adjust path if running from different directory
    mcp_server_path = "ultimate_mcp/hakgal_mcp_ultimate.py" 
    
    # Ensure the venv's python is used for the subprocess
    import sys
    python_executable = os.path.join(os.path.dirname(sys.executable), "python.exe")
    
    # Test if the MCP server path is correct
    if not os.path.exists(mcp_server_path):
        print(f"Error: MCP server script not found at {mcp_server_path}")
        sys.exit(1)

    bridge = MCPBridge(mcp_path=mcp_server_path)
    
    try:
        print("Testing MCP Bridge: Calling 'tools/list'...")
        response = bridge.send_request(method="tools/list", params={})
        print(f"Response: {json.dumps(response, indent=2)}")
        
        print("\nTesting MCP Bridge: Calling 'llm/chat' with a message...")
        response = bridge.send_request(
            method="llm/chat",
            params={
                "model": "mistral", # Assuming Mistral is configured in MCP
                "messages": [{"role": "user", "content": "Say hello"}]
            }
        )
        print(f"Response: {json.dumps(response, indent=2)}")

    finally:
        bridge.close()
