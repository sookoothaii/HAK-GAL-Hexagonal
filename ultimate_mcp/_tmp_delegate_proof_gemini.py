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
        "target_agent": "Gemini",
        "task_description": "Schreibe genau: PROOF_GEMINI_OK_67890",
        "context": {"kb": "hexagonal_kb.db"}
    }
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})

    # Extract text
    proof = None
    for resp in captured:
        if resp.get("id") == 2:
            items = resp.get("result", {}).get("content", [])
            for it in items:
                if it.get("type") == "text":
                    proof = it.get("text")
                    break
    print("Gemini Antwort:")
    print(proof or "<keine>")

asyncio.run(main())
