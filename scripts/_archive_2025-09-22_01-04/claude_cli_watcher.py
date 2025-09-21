import time
import json
import subprocess
import shutil
import os
from pathlib import Path

# --- Configuration ---
# The directory to watch for tasks, relative to this script's parent directory.
EXCHANGE_DIR = Path(__file__).parent.parent / "claude_cli_exchange"
# Tries to find the 'claude' executable in the system's PATH.
CLAUDE_EXECUTABLE = shutil.which("claude")
# How often to check for new tasks, in seconds.
POLL_INTERVAL = 5
# How long the subprocess is allowed to run, in seconds.
PROCESS_TIMEOUT = 120

def process_task(task_file):
    """Reads a task, executes it with Claude CLI, and writes the response."""
    print(f"--- Found task: {task_file.name} ---")
    
    task_id = None
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
        
        task_id = task_data.get("id")
        prompt = task_data.get("task", "")
        context = task_data.get("context", {})

        if context:
            prompt += f"\n\n--- Context ---\n{json.dumps(context, indent=2)}"

        if not CLAUDE_EXECUTABLE:
            print("Error: 'claude' executable not found in system PATH.")
            result_data = {"status": "error", "result": "Claude executable not found in PATH."}
        else:
            print(f"Running Claude CLI for task {task_id}...")
            try:
                # Execute the claude command with piped input (correct method)
                result = subprocess.run(
                    CLAUDE_EXECUTABLE,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    timeout=PROCESS_TIMEOUT,
                    encoding='utf-8'
                )
                if result.returncode == 0:
                    print("Claude execution successful.")
                    result_data = {"status": "completed", "result": result.stdout.strip()}
                else:
                    print(f"Claude execution failed with code {result.returncode}.")
                    error_output = result.stderr.strip() or result.stdout.strip() or f"No error output. Return code: {result.returncode}"

                    # Check for specific error messages
                    if "Credit balance is too low" in error_output:
                        error_output = "Claude CLI: Insufficient credits or API key not configured properly"
                    elif "not found" in error_output.lower():
                        error_output = "Claude CLI: Authentication or configuration error"

                    result_data = {"status": "error", "result": error_output}
            except subprocess.TimeoutExpired:
                print(f"Error: Claude command timed out after {PROCESS_TIMEOUT} seconds.")
                result_data = {"status": "error", "result": f"Process timed out after {PROCESS_TIMEOUT} seconds."}
            except Exception as e:
                print(f"An unexpected error occurred during subprocess execution: {e}")
                result_data = {"status": "error", "result": f"Python script exception: {e}"}

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
    print("--- Claude CLI Watchdog Started ---")
    print(f"Watching directory: {EXCHANGE_DIR.resolve()}")
    print(f"Claude executable: {CLAUDE_EXECUTABLE or 'NOT FOUND'}")
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
