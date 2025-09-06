import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional


class MCPClient:
    """
    Minimaler JSON-RPC-Client für den HAK-GAL MCP-Server über STDIO.
    Startet den Server-Prozess (python -m hak_gal_mcp) im Subprozess und
    sendet/empfängt JSON-RPC-Zeilen.

    Nutzung (Read-Only):
      client = MCPClient(python_path=r".\\.venv_hexa\\Scripts\\python.exe")
      client.start()
      health = client.call_tool("health_check", {})
      client.stop()
    """

    def __init__(self, python_path: str = sys.executable, extra_env: Optional[Dict[str, str]] = None, cwd: Optional[str] = None):
        self.python_path = python_path
        self.extra_env = extra_env or {}
        self.cwd = cwd or os.getcwd()
        self.proc: Optional[subprocess.Popen] = None
        self._next_id = 1

    def start(self) -> None:
        if self.proc is not None:
            return
        env = os.environ.copy()
        env.update(self.extra_env)
        # Erzwinge UTF-8 für stabile STDIO
        env.setdefault("PYTHONIOENCODING", "utf-8")
        cmd = [self.python_path, "-m", "hak_gal_mcp"]
        self.proc = subprocess.Popen(
            cmd,
            cwd=self.cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        # Initialisiere Protokoll
        self._send({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {}
        })
        # Kleines Zeitfenster für server/ready und init-Antwort
        time.sleep(0.2)
        # Tools auflisten (nicht zwingend, aber sanity check)
        self._send({
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list",
            "params": {}
        })
        time.sleep(0.2)

    def stop(self) -> None:
        if self.proc is None:
            return
        try:
            # Shutdown senden (best effort)
            self._send({
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "shutdown",
                "params": {}
            })
            time.sleep(0.1)
        except Exception:
            pass
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass
        self.proc = None

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        Führt ein MCP-Tool aus und gibt den Textinhalt der Antwort zurück.
        """
        if self.proc is None:
            raise RuntimeError("MCPClient not started")
        req_id = self._next_request_id()
        self._send({
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}}
        })
        # Warte auf Antwortzeilen; einfache Timeout-Logik
        deadline = time.time() + 5.0
        while time.time() < deadline:
            line = self._readline(timeout=0.1)
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("id") == req_id and "result" in obj:
                result = obj["result"]
                # Server liefert {"content":[{"type":"text","text":"..."}]}
                content = result.get("content") if isinstance(result, dict) else None
                if isinstance(content, list) and content:
                    text = content[0].get("text", "")
                    return str(text)
                # Fallback: gesamte JSON-Antwort als Text
                return json.dumps(result)
        raise TimeoutError(f"No response for tool '{name}' within timeout")

    def _next_request_id(self) -> int:
        i = self._next_id
        self._next_id += 1
        return i

    def _send(self, obj: Dict[str, Any]) -> None:
        if self.proc is None or self.proc.stdin is None:
            raise RuntimeError("MCPClient process/stdin not available")
        line = json.dumps(obj)
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def _readline(self, timeout: float = 0.1) -> Optional[str]:
        if self.proc is None or self.proc.stdout is None:
            return None
        # Nicht-blockierendes Lesen durch kurzes Sleep + readline
        time.sleep(timeout)
        try:
            return self.proc.stdout.readline().strip() or None
        except Exception:
            return None


def default_client() -> MCPClient:
    """Konstruktor mit sinnvollen Defaults für dieses Projekt."""
    python_path = os.environ.get("MCP_PYTHON", os.path.join(".\\.venv_hexa\\Scripts\\python.exe"))
    extra_env = {
        # Cursor-Konfiguration spiegelt diese ENV ebenfalls wider
        "HAKGAL_API_BASE_URL": os.environ.get("HAKGAL_API_BASE_URL", "http://127.0.0.1:5001"),
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        # Lesen genügt für Status-Posts
        "HAKGAL_WRITE_ENABLED": os.environ.get("HAKGAL_WRITE_ENABLED", "false"),
        "HAKGAL_HUB_PATH": os.environ.get("HAKGAL_HUB_PATH", os.path.join(os.getcwd(), "PROJECT_HUB")),
    }
    return MCPClient(python_path=python_path, extra_env=extra_env, cwd=os.getcwd())


