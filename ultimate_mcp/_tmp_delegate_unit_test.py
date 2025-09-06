import asyncio, json, sys
from pathlib import Path
# Projektwurzel in sys.path aufnehmen, damit "ultimate_mcp" als Paket gefunden wird
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def main():
    server = HAKGALMCPServer()
    responses = []
    async def capture(resp):
        responses.append(resp)
    server.send_response = capture

    await server.handle_initialize({"id": 1})
    args = {
        "target_agent": "DeepSeek",
        "task_description": "Schreibe genau das Wort READY.",
        "context": {"kb": "hexagonal_kb.db", "note": "kurzer Test"}
    }
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})

    for r in responses:
        print(json.dumps(r, ensure_ascii=False))

asyncio.run(main())
