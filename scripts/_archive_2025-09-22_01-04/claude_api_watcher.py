import time
import json
import os
from pathlib import Path
import requests
from typing import Optional, Dict, Any

# --- Configuration ---
EXCHANGE_DIR = Path(__file__).parent.parent / "claude_cli_exchange"
POLL_INTERVAL = 5
PROCESS_TIMEOUT = 120

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # Latest model

def call_claude_api(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call Claude via Anthropic API directly."""
    if not ANTHROPIC_API_KEY:
        return {
            "status": "error",
            "result": "ANTHROPIC_API_KEY environment variable not set"
        }

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    # Build the message
    system_prompt = "You are Claude, an AI assistant integrated into the HAK/GAL multi-agent system. Provide helpful, accurate responses."

    if context:
        user_prompt = f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)}"
    else:
        user_prompt = prompt

    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    try:
        response = requests.post(
            CLAUDE_API_URL,
            headers=headers,
            json=data,
            timeout=PROCESS_TIMEOUT
        )

        if response.status_code == 200:
            result = response.json()
            content = result["content"][0]["text"] if result["content"] else ""
            return {
                "status": "completed",
                "result": content,
                "model": CLAUDE_MODEL,
                "usage": result.get("usage", {})
            }
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            return {
                "status": "error",
                "result": error_msg
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "result": f"Request timed out after {PROCESS_TIMEOUT} seconds"
        }
    except Exception as e:
        return {
            "status": "error",
            "result": f"API call failed: {str(e)}"
        }

def process_task(task_file: Path):
    """Reads a task, executes it with Claude API, and writes the response."""
    print(f"--- Found task: {task_file.name} ---")

    task_id = None
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)

        task_id = task_data.get("id")
        prompt = task_data.get("task", "")
        context = task_data.get("context", {})

        print(f"Processing task {task_id} with Claude API...")
        result_data = call_claude_api(prompt, context)

        # Write the response file if a task_id was successfully read
        if task_id:
            response_file = EXCHANGE_DIR / f"response_{task_id}.json"
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2)
            print(f"Wrote response to {response_file.name}")

    except Exception as e:
        print(f"Error processing task file {task_file.name}: {e}")
        # If we have a task_id, we can still write an error response
        if task_id:
            response_file = EXCHANGE_DIR / f"response_{task_id}.json"
            error_data = {"status": "error", "result": f"Failed to process task file: {e}"}
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2)
    finally:
        # Clean up the original task file
        task_file.unlink(missing_ok=True)
        print(f"Cleaned up task file: {task_file.name}")

def watch_directory():
    """Monitors the exchange directory for new tasks."""
    print("--- Claude API Watchdog Started ---")
    print(f"Watching directory: {EXCHANGE_DIR.resolve()}")
    print(f"Claude API Key: {'SET' if ANTHROPIC_API_KEY else 'NOT SET'}")
    print(f"Model: {CLAUDE_MODEL}")
    EXCHANGE_DIR.mkdir(exist_ok=True)

    while True:
        try:
            # Find the oldest task file to process first
            task_files = sorted(EXCHANGE_DIR.glob("task_*.json"), key=os.path.getmtime)
            if task_files:
                process_task(task_files[0])
            else:
                # No tasks, wait for the poll interval
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\n--- Watchdog stopped by user. ---")
            break
        except Exception as e:
            print(f"An error occurred in the watch loop: {e}")
            time.sleep(POLL_INTERVAL * 2) # Wait a bit longer after an error

if __name__ == "__main__":
    watch_directory()