import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def call_exec(code: str, language: str, timeout: int):
    server = HAKGALMCPServer()
    out = []
    async def cap(resp): out.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})
    await server.handle_tool_call({"id": 2, "params": {"name": "execute_code", "arguments": {"code": code, "language": language, "timeout": timeout}}})
    for r in out:
        if r.get("id") == 2:
            items = (r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type") == "text":
                    return it.get("text")
    return "<no result>"

async def main():
    print("[CASE 1] Timeout with partial output (python, 2s)")
    code1 = "import time\nfor i in range(5):\n print(i)\n time.sleep(1)\n"
    print(await call_exec(code1, "python", 2))

    print("\n[CASE 2] ASCII sanitization (non-ascii in stdout)")
    code2 = "print('OK ??? ?')\n"
    print(await call_exec(code2, "python", 5))

    print("\n[CASE 3] Normal run")
    code3 = "print(sum(range(5)))\n"
    print(await call_exec(code3, "python", 5))

asyncio.run(main())
