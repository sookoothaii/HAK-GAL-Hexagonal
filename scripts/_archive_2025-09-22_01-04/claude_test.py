# claude_test.py
"""
Claude API test with model aliases and model listing.
- No third-party deps (urllib only).
- Key from --key | $ANTHROPIC_API_KEY | .env
- Aliases: sonnet-3.7 (s37), sonnet-4 (s4)
- --list-models shows what your key can access.
"""

from __future__ import annotations
import argparse, json, os, sys, time
import urllib.request, urllib.error

API_URL_MESSAGES = "https://api.anthropic.com/v1/messages"
API_URL_MODELS = "https://api.anthropic.com/v1/models"
API_VERSION = "2023-06-01"

# Update these IDs to whatever your org wirklich freigeschaltet hat.
MODEL_ALIASES = {
    "sonnet-3.7": "claude-3-7-sonnet-20250219",
    "sonnet-4": "claude-sonnet-4-20250514",
    "s37": "claude-3-7-sonnet-20250219",
    "s4": "claude-sonnet-4-20250514",
    "claude-3-7-sonnet-20250219": "claude-3-7-sonnet-20250219",
    "claude-sonnet-4-20250514": "claude-sonnet-4-20250514",
}

DEFAULT_MODEL = MODEL_ALIASES["sonnet-3.7"]

def load_key_from_env_file(filename: str = ".env") -> str | None:
    if not os.path.isfile(filename):
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("ANTHROPIC_API_KEY"):
                    _, _, raw = line.partition("=")
                    return raw.strip().strip('"').strip("'") or None
    except Exception:
        return None
    return None

def resolve_api_key(cli_key: str | None) -> str | None:
    return (cli_key or os.getenv("ANTHROPIC_API_KEY") or load_key_from_env_file(".env"))

def resolve_model(name: str) -> str:
    return MODEL_ALIASES.get(name, name)

def list_models(api_key: str) -> list[dict]:
    req = urllib.request.Request(
        API_URL_MODELS,
        method="GET",
        headers={"x-api-key": api_key, "anthropic-version": API_VERSION},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8")).get("data", [])

def call_claude(api_key: str, prompt: str, model: str, max_tokens: int = 256, timeout: int = 30) -> dict:
    payload = {"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        API_URL_MESSAGES,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def extract_text(resp: dict) -> str:
    for block in resp.get("content", []) or []:
        if block.get("type") == "text":
            return block.get("text", "")
    return ""

def main() -> int:
    ap = argparse.ArgumentParser(description="Test a Claude API call (with model aliases and listing).")
    ap.add_argument("--key", type=str, help="Anthropic API key (overrides env/.env).")
    ap.add_argument("--model", type=str, default=DEFAULT_MODEL,
                    help="Model name or alias (e.g., sonnet-3.7, sonnet-4, s37, s4, or full ID).")
    ap.add_argument("--prompt", type=str, default="Return OK if alive.")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--list-models", action="store_true", help="List models visible to your key and exit.")
    args = ap.parse_args()

    api_key = resolve_api_key(args.key)
    if not api_key:
        print("ERROR: Provide --key, set ANTHROPIC_API_KEY, or put it in .env", file=sys.stderr)
        return 2

    if args.list_models:
        try:
            models = list_models(api_key)
            print("=== MODELS VISIBLE TO THIS KEY ===")
            for m in models:
                mid = m.get("id", "?")
                ver = m.get("display_version") or ""
                print(f"- {mid} {ver}")
            return 0
        except urllib.error.HTTPError as e:
            print("HTTP ERROR while listing models:", e.code)
            print(e.read().decode("utf-8", errors="replace"))
            return 1

    model_id = resolve_model(args.model)
    # einfache Validierung + Hilfetext
    if model_id not in MODEL_ALIASES.values() and not model_id.startswith("claude"):
        print(f"WARNING: Unknown alias/model '{args.model}'. Using as-is: '{model_id}'", file=sys.stderr)

    print(f"-> Using model: {model_id}")
    try:
        t0 = time.time()
        resp = call_claude(api_key, args.prompt, model_id, args.max_tokens, args.timeout)
        dt = time.time() - t0
        print("\n=== RESPONSE ===")
        print(extract_text(resp) or "[No text block]")
        print("\n=== META ===")
        print(f"Latency: {dt:.2f}s")
        if "id" in resp:
            print(f"Response ID: {resp['id']}")
        if "model" in resp:
            print(f"Resolved Model: {resp['model']}")
        return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print("\nHTTP ERROR:", e.code)
        print(body)
        if e.code == 403:
            print("\nHint: 403 ⇒ Key/Org hat keinen Zugriff auf dieses Modell (oder Region/Quota).")
        elif e.code == 401:
            print("\nHint: 401 ⇒ Key fehlt/ist ungültig.")
        elif e.code == 429:
            print("\nHint: 429 ⇒ Rate Limit/Quota erschöpft.")
        return 1
    except Exception as e:
        print("\nUNEXPECTED ERROR:", repr(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
