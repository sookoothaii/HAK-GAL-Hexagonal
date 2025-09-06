import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer
import asyncio

async def call(tool, args=None):
    server = HAKGALMCPServer()
    out = []
    async def cap(resp): out.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})
    await server.handle_tool_call({"id": 2, "params": {"name": tool, "arguments": (args or {})}})
    for r in out:
        if r.get("id") == 2:
            items = (r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type") == "text":
                    return it.get("text")
    return ""

async def main():
    p = argparse.ArgumentParser(description='DB Maintenance CLI')
    sp = p.add_subparsers(dest='cmd', required=True)
    sp.add_parser('backup_now')
    pr = sp.add_parser('rotate'); pr.add_argument('--keep-last', type=int, default=10)
    pc = sp.add_parser('checkpoint'); pc.add_argument('--mode', default='TRUNCATE')
    sp.add_parser('vacuum')
    args = p.parse_args()
    if args.cmd == 'backup_now':
        print(await call('db_backup_now'))
    elif args.cmd == 'rotate':
        print(await call('db_backup_rotate', {"keep_last": args.keep_last}))
    elif args.cmd == 'checkpoint':
        print(await call('db_checkpoint', {"mode": args.mode}))
    elif args.cmd == 'vacuum':
        print(await call('db_vacuum'))

if __name__ == '__main__':
    asyncio.run(main())
