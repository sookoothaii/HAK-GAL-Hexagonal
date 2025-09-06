import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

TOOLS = [
  ("sentry_test_connection", {}, 70),
  ("sentry_whoami", {}, 71),
  ("sentry_find_organizations", {}, 72),
  ("sentry_find_projects", {"organization_slug": "samui-science-lab"}, 73),
  ("sentry_search_issues", {"query": "is:unresolved", "limit": 5}, 74),
]

async def call(name, args, req_id):
    s=HAKGALMCPServer(); out=[]
    async def cap(r): out.append(r)
    s.send_response=cap
    await s.handle_initialize({"id":1})
    await s.handle_tool_call({"id":req_id, "params":{"name":name, "arguments":args}})
    for r in out:
        if r.get("id")==req_id:
            items=(r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type")=="text":
                    return it.get("text")
    return ""

async def main():
    for name, args, rid in TOOLS:
        out = await call(name, args, rid)
        print(f"[{name}]\n" + (out or "<no output>") + "\n")

asyncio.run(main())
