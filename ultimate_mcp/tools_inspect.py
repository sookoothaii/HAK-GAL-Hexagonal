import asyncio
import json
import sys
from pathlib import Path

# Ermöglicht Import des Servers
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer


async def main():
    server = HAKGALMCPServer()
    tools = []

    async def capture(resp):
        res = resp.get("result") or {}
        if "tools" in res:
            tools.extend(res["tools"])

    server.send_response = capture

    await server.handle_initialize({"id": 1})
    await server.handle_list_tools({"id": 2})

    names = [t.get("name") for t in tools]
    print(json.dumps({"count": len(tools), "names": names}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())






