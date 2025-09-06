import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def call(agent: str):
    server = HAKGALMCPServer()
    captured = []
    async def cap(resp): captured.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})
    args = {"target_agent": agent, "task_description": "Antworte genau: OK_"+agent.replace(":","_"), "context": {}}
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})
    text = None
    for r in captured:
        if r.get("id") == 2:
            items = r.get("result", {}).get("content", [])
            for it in items:
                if it.get("type") == "text":
                    text = it.get("text")
                    break
    print(f"[{agent}] -> {text}")

async def main():
    for agent in ("DeepSeek:chat", "Gemini:2.5-flash", "Claude:sonnet"):
        try:
            await call(agent)
        except Exception as e:
            print(f"[{agent}] ERROR: {e}")

asyncio.run(main())
