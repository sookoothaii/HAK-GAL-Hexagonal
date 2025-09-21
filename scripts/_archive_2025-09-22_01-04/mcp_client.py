#!/usr/bin/env python3
"""
HAK_GAL MCP Client - One-Shot Command Executor

This script acts as a command-line client to the hak_gal_mcp_fixed.py server.
It starts the server as a subprocess, sends a single JSON-RPC request to its stdin,
reads a single JSON-RPC response from its stdout, prints the result, and terminates.

This allows stateless tools like `run_shell_command` to interact with the stateful MCP server.
"""

import sys
import os
import json
import subprocess
import argparse
import threading

# --- Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser(description="HAK_GAL MCP One-Shot Client")
    parser.add_argument(
        "--tool",
        required=True,
        help="The name of the tool to call (e.g., 'list_tools', 'kb_stats')."
    )
    parser.add_argument(
        "--params",
        default="{}",
        help="A JSON string representing the tool parameters (e.g., '{\"limit\': 10}')."
    )
    # Add specific arguments for complex tools to avoid quoting issues
    parser.add_argument(
        "--title",
        help="Title for project_snapshot tool."
    )
    parser.add_argument(
        "--description",
        help="Description for project_snapshot tool."
    )
    parser.add_argument(
        "--hub-path",
        help="Hub path for project_snapshot tool."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for the command."
    )
    return parser.parse_args()

# --- Main Execution Logic ---
def main():
    args = parse_args()
    
    # --- Construct Parameters ---
    # If special args are provided, use them. Otherwise, use the generic --params.
    if args.tool == 'project_snapshot' and args.title:
        params_obj = {
            "title": args.title,
            "description": args.description or "",
            "hub_path": args.hub_path or ""
        }
    else:
        try:
            params_obj = json.loads(args.params)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON in --params argument"}), file=sys.stderr)
            sys.exit(1)

    # --- Construct the JSON-RPC Request ---
    # The server expects the tool name in the format "tools/call"
    # with the actual tool name inside the params.
    if args.tool == 'list_tools':
        # Special case for tool listing
        method = 'tools/list'
        rpc_params = {}
    else:
        method = 'tools/call'
        rpc_params = {
            "name": args.tool,
            "arguments": params_obj
        }

    request_obj = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": rpc_params
    }
    request_str = json.dumps(request_obj) + '\n'

    # --- Prepare and Launch the Server Subprocess ---
    script_path = os.path.join(os.path.dirname(__file__), 'hak_gal_mcp_fixed.py')
    python_exe = sys.executable # Use the same python that runs this client
    
    # Environment setup to match MCP_START_FULL.bat
    project_root = os.path.dirname(os.path.dirname(__file__))
    site_packages = os.path.join(project_root, ".venv_hexa", "Lib", "site-packages")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONUTF8"] = "1"
    # Prepend our venv's site-packages to PYTHONPATH to ensure it's found first.
    existing_python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{site_packages}{os.pathsep}{existing_python_path}"
    env["HAKGAL_WRITE_ENABLED"] = "true" # Enable writes for tools that need it
    env["HAKGAL_API_BASE_URL"] = "http://127.0.0.1:5002" # Explicitly target the main backend

    proc = subprocess.Popen(
        [python_exe, "-u", script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        env=env
    )

    # --- Communication with the Subprocess ---
    response_json = None
    error_output = ""

    def read_stderr():
        nonlocal error_output
        for line in iter(proc.stderr.readline, ''):
            error_output += line

    stderr_thread = threading.Thread(target=read_stderr)
    stderr_thread.daemon = True
    stderr_thread.start()

    try:
        # The server sends a `server/ready` message first. We read and discard it.
        # Then we read the actual response to our request.
        
        # Write our request to the server's stdin
        proc.stdin.write(request_str)
        proc.stdin.flush()
        proc.stdin.close() # Signal that we are done writing

        # Read until we get our response
        for line in iter(proc.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue
            try:
                response = json.loads(line)
                if response.get("method") == "server/ready":
                    continue # Ignore the ready signal
                if response.get("id") == 1:
                    response_json = response
                    break # We got our response
            except json.JSONDecodeError:
                # Ignore lines that are not valid JSON
                continue

    finally:
        # --- Cleanup ---
        proc.terminate() # Terminate the server process
        proc.wait(timeout=5)
        if proc.poll() is None:
            proc.kill()
        stderr_thread.join(timeout=1)

    # --- Output the Result ---
    if response_json:
        print(json.dumps(response_json, indent=2))
    else:
        print(json.dumps({
            "error": "Did not receive a valid JSON-RPC response from the server.",
            "stderr": error_output
        }), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
