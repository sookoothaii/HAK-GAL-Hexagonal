#!/usr/bin/env python3
"""
Minimal MCP STDIO Server for Cursor
Safe, dependency-free, Windows-friendly. Provides a small toolset to verify connectivity.
"""

import sys
import json
import os


def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg, separators=(",", ":")) + "\n")
    sys.stdout.flush()


TOOLS = [
    {
        "name": "echo",
        "description": "Echo arguments back",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "ping",
        "description": "Health ping",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "env_info",
        "description": "Show selected environment variables",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "time_now",
        "description": "Return current time (ISO)",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def handle_initialize(req_id):
    send(
        {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {},
                    "prompts": {},
                },
                "serverInfo": {"name": "HAK_GAL Minimal MCP", "version": "0.1"},
            },
        }
    )


def handle_tools_list(req_id):
    send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})


def handle_tools_call(req_id, name, arguments):
    if name == "echo":
        text = str(arguments.get("text", ""))
        send({"jsonrpc": "2.0", "id": req_id, "result": {"text": text}})
        return
    if name == "ping":
        send({"jsonrpc": "2.0", "id": req_id, "result": {"status": "ok"}})
        return
    if name == "env_info":
        keys = [
            "PYTHONIOENCODING",
            "PYTHONUTF8",
            "PYTHONUNBUFFERED",
            "PYTHONPATH",
            "HAKGAL_API_BASE_URL",
            "HAKGAL_WRITE_ENABLED",
            "HAKGAL_HUB_PATH",
        ]
        info = {k: os.environ.get(k) for k in keys}
        send({"jsonrpc": "2.0", "id": req_id, "result": info})
        return
    if name == "time_now":
        import datetime as _dt

        send({"jsonrpc": "2.0", "id": req_id, "result": {"now": _dt.datetime.utcnow().isoformat() + "Z"}})
        return

    send(
        {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Tool not found: {name}"},
        }
    )


def main():
    # Line-based JSON-RPC over stdio
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            req_id = req.get("id")
            if method == "initialize":
                handle_initialize(req_id)
            elif method == "tools/list":
                handle_tools_list(req_id)
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                handle_tools_call(req_id, name, args)
            elif method == "shutdown":
                send({"jsonrpc": "2.0", "id": req_id, "result": {}})
                break
            else:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"},
                    }
                )
        except Exception as e:
            send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}})


if __name__ == "__main__":
    main()



