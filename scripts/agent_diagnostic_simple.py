import requests
import json
import subprocess
import sys
import os
from datetime import datetime

print('=== CLAUDE CLI DIAGNOSTIC & ALTERNATIVE AGENT TESTS ===')
print('Start Time:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print()

BASE_URL = 'http://127.0.0.1:5002'
API_KEY = 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d'
HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def test_claude_cli_detailed():
    '''Detailed Claude CLI diagnostic'''
    print('[DIAGNOSING] CLAUDE CLI ERROR CODE 1')
    print('-' * 40)

    # Test 1: Check if claude command exists
    print('1. Checking Claude CLI installation...')
    try:
        result = subprocess.run(['where', 'claude'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print('   SUCCESS: Claude CLI found at:', result.stdout.strip())
        else:
            print('   ERROR: Claude CLI not found in PATH')
            print('   Details:', result.stderr)
    except Exception as e:
        print('   ERROR checking Claude CLI:', str(e))

    # Test 2: Try direct Claude CLI call
    print()
    print('2. Testing direct Claude CLI call...')
    try:
        test_prompt = 'Say hello in one word'
        result = subprocess.run(
            ['claude', test_prompt],
            capture_output=True, text=True, timeout=30
        )
        print('   Return Code:', result.returncode)
        if result.returncode == 0:
            print('   SUCCESS: Direct call worked')
            print('   Output:', result.stdout[:100] + '...' if len(result.stdout) > 100 else result.stdout)
        else:
            print('   ERROR: Direct call failed')
            print('   Stdout:', result.stdout)
            print('   Stderr:', result.stderr)
    except subprocess.TimeoutExpired:
        print('   TIMEOUT: Direct call took too long')
    except Exception as e:
        print('   ERROR in direct call:', str(e))

    # Test 3: Check environment variables
    print()
    print('3. Checking environment variables...')
    env_vars = ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY']
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        if value != 'NOT SET':
            print(f'   {var}: SET (length: {len(value)})')
        else:
            print(f'   {var}: NOT SET')

    # Test 4: HAK-GAL Claude CLI delegation
    print()
    print('4. Testing HAK-GAL Claude CLI delegation...')
    payload = {
        'target_agent': 'claude_cli',
        'task_description': 'Say hello',
        'context': {'test': 'diagnostic'}
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/agent-bus/delegate',
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        print('   HTTP Status:', response.status_code)
        if response.status_code == 200:
            result = response.json()
            print('   SUCCESS: Delegation worked')
            print('   Response keys:', list(result.keys()))
            if 'response' in result:
                print('   Response preview:', result['response'][:100] + '...')
        else:
            print('   ERROR: Delegation failed')
            print('   Response:', response.text)
    except Exception as e:
        print('   ERROR in delegation:', str(e))

def test_gemini_reliability():
    '''Test Gemini reliability with multiple calls'''
    print()
    print('[TESTING] GEMINI RELIABILITY')
    print('-' * 40)

    test_tasks = [
        'Count to 5',
        'What is 2+2?',
        'Say hello in German'
    ]

    print('Running 3 quick Gemini tests...')
    for i, task in enumerate(test_tasks, 1):
        print(f'{i}. Testing: "{task}"')
        payload = {
            'target_agent': 'gemini',
            'task_description': task,
            'context': {'test_id': i}
        }

        try:
            import time
            start = time.time()
            response = requests.post(
                f'{BASE_URL}/api/agent-bus/delegate',
                headers=HEADERS,
                json=payload,
                timeout=15
            )
            end = time.time()

            if response.status_code == 200:
                result = response.json()
                print(f'   SUCCESS: {end-start:.1f}s')
                if 'response' in result:
                    preview = result['response'][:50].replace('\n', ' ')
                    print(f'   Response: "{preview}..."')
            else:
                print(f'   FAILED: HTTP {response.status_code}')

        except Exception as e:
            print(f'   ERROR: {str(e)}')

        import time
        time.sleep(1)  # Brief pause

def test_cursor_file_system():
    '''Test Cursor via file system'''
    print()
    print('[TESTING] CURSOR FILE SYSTEM')
    print('-' * 40)

    exchange_dir = 'cursor_exchange'

    print('1. Checking cursor_exchange directory...')
    if os.path.exists(exchange_dir):
        files = os.listdir(exchange_dir)
        print(f'   SUCCESS: Directory exists with {len(files)} files')
        if files:
            print('   Recent files:')
            for file in sorted(files, key=lambda x: os.path.getmtime(os.path.join(exchange_dir, x)), reverse=True)[:3]:
                mtime = datetime.fromtimestamp(os.path.getmtime(os.path.join(exchange_dir, file)))
                print(f'   - {file} ({mtime.strftime("%H:%M:%S")})')
    else:
        print('   INFO: cursor_exchange directory not found')
        try:
            os.makedirs(exchange_dir)
            print('   SUCCESS: Created cursor_exchange directory')
        except Exception as e:
            print('   ERROR creating directory:', str(e))

# Run diagnostic tests
test_claude_cli_detailed()
test_cursor_file_system()
test_gemini_reliability()

print()
print('=' * 50)
print('DIAGNOSTIC SUMMARY')
print('=' * 50)
print('- Claude CLI: Likely missing API key or installation issue')
print('- Claude Desktop: May work but no direct API response')
print('- Cursor: File-based communication system')
print('- Gemini: Reliable and fast AI agent')
print()
print('RECOMMENDATION: Use Gemini for reliable AI tasks')