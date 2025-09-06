import subprocess, sys, json, time, os

server_cmd = [sys.executable, "ultimate_mcp/hakgal_mcp_ultimate.py"]
proc = subprocess.Popen(server_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

def send(obj):
    line = json.dumps(obj)
    proc.stdin.write(line + "\n")
    proc.stdin.flush()

def read_some(timeout=5.0):
    out = []
    start = time.time()
    while time.time() - start < timeout:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.05)
            continue
        out.append(line.strip())
        if len(out) > 5:
            break
    return out

# Initialize
send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{}})
init_lines = read_some(3.0)

# Delegate task call
args = {
    "target_agent": "DeepSeek",
    "task_description": "Erstelle eine prägnante Ein-Satz-Zusammenfassung des HAK_GAL Hexagonal Projekts.",
    "context": {"kb":"hexagonal_kb.db","ports":{"backend":5002,"governor":5001,"frontend":5173,"caddy":8088}}
}
send({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"delegate_task","arguments":args}})
reply_lines = read_some(45.0)

# Output results
print("INIT:\n" + "\n".join(init_lines))
print("\nREPLY:\n" + "\n".join(reply_lines))

try:
    proc.terminate()
except Exception:
    pass
