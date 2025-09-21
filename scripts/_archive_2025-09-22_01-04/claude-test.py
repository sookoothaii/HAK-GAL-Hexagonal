# test_claude.py
"""
Minimal Claude API reachability & response test.
- No third-party deps (uses urllib).
- Reads API key from --key, environment (ANTHROPIC_API_KEY), or a local .env file.
- Sends a single Messages API request and prints the first text segment.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"  # official version header

# A safe default; change if you have access to a newer model.
DEFAULT_MODEL = "claude-3-5-sonnet-20240620"


def load_key_from_env_file(filename: str = ".env") -> str | None:
    """
    Very small .env reader: looks for a line like ANTHROPIC_API_KEY=sk-ant-...
    (Ignores quotes and whitespace. Does not export to os.environ.)
    """
    if not os.path.isfile(filename):
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("ANTHROPIC_API_KEY"):
                    # Accept formats: KEY=value or KEY="value"
                    _, _, raw = line.partition("=")
                    raw = raw.strip().strip("'").strip('"')
                    return raw or None
    except Exception:
        return None
    return None


def resolve_api_key(cli_key: str | None) -> str | None:
    if cli_key:
        return cli_key.strip()
    env_key = os.getenv("ANTHROPIC_API_KEY")
    if env_key:
        return env_key.strip()
    file_key = load_key_from_env_file(".env")
    if file_key:
        return file_key.strip()
    return None


def call_claude(api_key: str, prompt: str, model: str, max_tokens: int = 256, timeout: int = 30) -> dict:
    """
    Sends a non-streaming Messages API request.
    Returns the parsed JSON response (dict). Raises urllib.error.HTTPError on HTTP errors.
    """
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=data,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
            # Optional: you may set "anthropic-beta": "...", or "anthropic-dangerous-direct-browser-access": "true" if needed.
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return json.loads(body.decode("utf-8"))


def extract_text(resp: dict) -> str:
    """
    Extracts the first text segment from the Messages API response.
    """
    try:
        content = resp.get("content") or []
        for block in content:
            if block.get("type") == "text" and "text" in block:
                return block["text"]
        return ""
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Test a single Claude API call.")
    parser.add_argument("--key", type=str, default=None, help="Anthropic API key (overrides env/.env).")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Claude model (default: {DEFAULT_MODEL})")
    parser.add_argument("--prompt", type=str, default="Say hello in one concise sentence.",
                        help="User prompt to send.")
    parser.add_argument("--max-tokens", type=int, default=256, help="max_tokens for the reply.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    args = parser.parse_args()

    api_key = resolve_api_key(args.key)
    if not api_key:
        print(
            "ERROR: No API key found. Provide --key, or set ANTHROPIC_API_KEY, or put it in .env\n"
            "Example (.env):\nANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx\n",
            file=sys.stderr,
        )
        return 2

    print(f"-> Using model: {args.model}")
    print("-> Sending request to Claude ...")
    t0 = time.time()
    try:
        resp = call_claude(api_key, args.prompt, args.model, args.max_tokens, args.timeout)
        dt = time.time() - t0
        text = extract_text(resp)
        print("\n=== RESPONSE (first text block) ===")
        print(text or "[No text content in response]")
        print("\n=== METADATA ===")
        print(f"Latency: {dt:.2f}s")
        if "id" in resp:
            print(f"Response ID: {resp['id']}")
        if "model" in resp:
            print(f"Resolved Model: {resp['model']}")
        return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print("\nHTTP ERROR:")
        print(f"Status: {e.code}")
        print(body)
        # Common diagnostics:
        if e.code == 401:
            print("\nHint: 401 usually means an invalid or missing API key.")
        elif e.code == 403:
            print("\nHint: 403 may indicate permission issues for the chosen model.")
        elif e.code == 429:
            print("\nHint: 429 means rate limit or quota exceeded.")
        return 1
    except urllib.error.URLError as e:
        print("\nNETWORK ERROR:")
        print(repr(e))
        print("Hint: Check DNS/SSL/Proxy and local firewall.")
        return 1
    except Exception as e:
        print("\nUNEXPECTED ERROR:")
        print(repr(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
