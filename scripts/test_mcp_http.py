import json
import sys
import urllib.request


MCP_BASE = "http://localhost:5050"


def call_streamable_http(url: str, payload: dict, extra_headers: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def main() -> None:
    # tools/list — probiere mehrere Payload-Varianten
    # Varianten: (URL, Body, Extra-Header)
    variants: list[tuple[str, dict, dict | None]] = [
        # 1) /mcp mit {serverId, request}
        (f"{MCP_BASE}/mcp", {
            "serverId": "hak-gal",
            "request": {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        }, None),
        # 2) /mcp?serverId=hak-gal mit purem JSON-RPC
        (f"{MCP_BASE}/mcp?serverId=hak-gal", {
            "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}
        }, None),
        # 3) /mcp/hak-gal mit purem JSON-RPC
        (f"{MCP_BASE}/mcp/hak-gal", {
            "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}
        }, None),
        # 4) /mcp mit x-server-id Header
        (f"{MCP_BASE}/mcp", {
            "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}
        }, {"x-server-id": "hak-gal"}),
    ]

    success_variant = None
    last_err: Exception | None = None
    for idx, (url, body, hdrs) in enumerate(variants, 1):
        try:
            res_list = call_streamable_http(url, body, hdrs)
            tools = res_list.get("result", {}).get("tools", [])
            print(f"variant={idx} url={url} tools_count=", len(tools))
            if tools:
                for t in tools[:10]:
                    print("-", t.get("name"))
                success_variant = (idx, url)
                break
        except Exception as e:
            last_err = e
            print(f"variant={idx} url={url} ERROR: {e}")
    if not success_variant:
        raise SystemExit(f"No variant succeeded. Last error: {last_err}")

    # simple tool call to verify execution
    req_call = {
        "serverId": "hak-gal",
        "request": {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_system_status",
                "arguments": {},
            },
        },
    }
    res_call = call_streamable_http(req_call)
    print("get_system_status=", json.dumps(res_call.get("result", {}), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e)
        sys.exit(1)


