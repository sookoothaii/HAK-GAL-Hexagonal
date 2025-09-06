import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def main():
    server = HAKGALMCPServer()
    captured = []
    async def capture(resp):
        captured.append(resp)
    server.send_response = capture

    await server.handle_initialize({"id": 1})
    args = {
        "target_agent": "Claude:sonnet",
        "task_description": "Schreibe genau: PROOF_CLAUDE_OK_99999",
        "context": {"kb": "hexagonal_kb.db"}
    }
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})

    text = None
    for resp in captured:
        if resp.get("id") == 2:
            items = resp.get("result", {}).get("content", [])
            for it in items:
                if it.get("type") == "text":
                    text = it.get("text")
                    break
    print("Claude Antwort:")
    print(text or "<keine>")

asyncio.run(main())
