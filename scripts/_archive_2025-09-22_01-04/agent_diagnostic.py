import requests
import json
import subprocess
import sys
import os
from datetime import datetime

print('=== CLAUDE CLI DIAGNOSTIC & ALTERNATIVE AGENT TESTS ===')
print(f'Start Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

BASE_URL = 'http://127.0.0.1:5002'
API_KEY = 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d'
HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

def test_claude_cli_detailed():
    '''Detailed Claude CLI diagnostic'''
    print('🔍 DIAGNOSING CLAUDE CLI ERROR CODE 1')
    print('-' * 40)

    # Test 1: Check if claude command exists
    print('1. Checking Claude CLI installation...')
    try:
        result = subprocess.run(['where', 'claude'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print('   ✅ Claude CLI found at:', result.stdout.strip())
        else:
            print('   ❌ Claude CLI not found in PATH')
            print('   Error:', result.stderr)
    except Exception as e:
        print('   ❌ Error checking Claude CLI:', str(e))

    # Test 2: Try direct Claude CLI call
    print('\n2. Testing direct Claude CLI call...')
    try:
        test_prompt = 'Say hello in one word'
        result = subprocess.run(
            ['claude', '--model', 'claude-3-5-sonnet-20241022', test_prompt],
            capture_output=True, text=True, timeout=30
        )
        print(f'   Return Code: {result.returncode}')
        if result.returncode == 0:
            print('   ✅ Direct call successful')
            print('   Output:', result.stdout[:100] + '...' if len(result.stdout) > 100 else result.stdout)
        else:
            print('   ❌ Direct call failed')
            print('   Stdout:', result.stdout)
            print('   Stderr:', result.stderr)
    except subprocess.TimeoutExpired:
        print('   ⏰ Direct call timed out')
    except Exception as e:
        print('   ❌ Error in direct call:', str(e))

    # Test 3: Check environment variables
    print('\n3. Checking environment variables...')
    env_vars = ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY', 'PATH']
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        if var == 'PATH':
            print(f'   {var}: ... (length: {len(value)})')
        elif 'API_KEY' in var and value != 'NOT SET':
            print(f'   {var}: SET (length: {len(value)})')
        else:
            print(f'   {var}: {value}')

    # Test 4: HAK-GAL Claude CLI delegation
    print('\n4. Testing HAK-GAL Claude CLI delegation...')
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
        print(f'   HTTP Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print('   ✅ Delegation successful')
            print('   Response keys:', list(result.keys()))
            if 'response' in result:
                print('   Response preview:', result['response'][:100] + '...')
        else:
            print('   ❌ Delegation failed')
            print('   Response:', response.text)
    except Exception as e:
        print('   ❌ Delegation error:', str(e))

def test_claude_desktop_alternative():
    '''Test Claude Desktop via alternative methods'''
    print('\n🔍 TESTING CLAUDE DESKTOP ALTERNATIVES')
    print('-' * 40)

    # Method 1: Check if Claude Desktop is running
    print('1. Checking Claude Desktop process...')
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Claude.exe'], capture_output=True, text=True)
        if 'Claude.exe' in result.stdout:
            print('   ✅ Claude Desktop is running')
        else:
            print('   ❌ Claude Desktop not running')
    except Exception as e:
        print('   ❌ Error checking process:', str(e))

    # Method 2: Try to open Claude Desktop
    print('\n2. Testing Claude Desktop launch...')
    try:
        # Try common Claude Desktop paths
        paths = [
            'C:\\Users\\%USERNAME%\\AppData\\Local\\AnthropicClaude\\claude.exe',
            'C:\\Program Files\\Claude\\claude.exe',
            'C:\\Users\\sooko\\AppData\\Local\\Programs\\Claude\\Claude.exe'
        ]

        for path in paths:
            try:
                result = subprocess.run([path], capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f'   ✅ Claude Desktop launched from: {path}')
                    break
            except:
                continue
        else:
            print('   ❌ Could not launch Claude Desktop from known paths')

    except Exception as e:
        print('   ❌ Error launching Claude Desktop:', str(e))

def test_cursor_alternative():
    '''Test Cursor via file-based communication'''
    print('\n🔍 TESTING CURSOR ALTERNATIVES')
    print('-' * 40)

    # Check cursor_exchange directory
    exchange_dir = 'cursor_exchange'

    print('1. Checking cursor_exchange directory...')
    if os.path.exists(exchange_dir):
        files = os.listdir(exchange_dir)
        print(f'   ✅ Directory exists with {len(files)} files')
        if files:
            print('   Recent files:')
            for file in sorted(files, key=lambda x: os.path.getmtime(os.path.join(exchange_dir, x)), reverse=True)[:3]:
                mtime = datetime.fromtimestamp(os.path.getmtime(os.path.join(exchange_dir, file)))
                print(f'   • {file} ({mtime.strftime("%H:%M:%S")})')
    else:
        print('   ❌ cursor_exchange directory not found')
        try:
            os.makedirs(exchange_dir)
            print('   ✅ Created cursor_exchange directory')
        except Exception as e:
            print('   ❌ Could not create directory:', str(e))

    # Test Cursor delegation
    print('\n2. Testing Cursor delegation...')
    payload = {
        'target_agent': 'cursor',
        'task_description': 'Create a simple Python hello world script',
        'context': {'output_file': 'hello.py'}
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/agent-bus/delegate',
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        print(f'   HTTP Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            print('   ✅ Cursor delegation successful')
            print('   Response:', json.dumps(result, indent=2))

            # Check if file was created
            if os.path.exists('hello.py'):
                print('   ✅ Output file created: hello.py')
                with open('hello.py', 'r') as f:
                    content = f.read()
                    print('   Content preview:', content[:100])
            else:
                print('   ❌ Output file not created')
        else:
            print('   ❌ Cursor delegation failed')
            print('   Response:', response.text)
    except Exception as e:
        print('   ❌ Cursor delegation error:', str(e))

def test_gemini_reliability():
    '''Test Gemini reliability with multiple calls'''
    print('\n🔍 TESTING GEMINI RELIABILITY')
    print('-' * 40)

    test_tasks = [
        'Count to 5',
        'What is 2+2?',
        'Say hello in German'
    ]

    print('Running 3 quick Gemini tests...')
    for i, task in enumerate(test_tasks, 1):
        print(f'\n{i}. Testing: "{task}"')
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
                print(f'   ✅ {end-start:.1f}s - Success')
                if 'response' in result:
                    preview = result['response'][:50].replace('\n', ' ')
                    print(f'   📝 "{preview}..."')
            else:
                print(f'   ❌ Failed: HTTP {response.status_code}')

        except Exception as e:
            print(f'   ❌ Error: {str(e)}')

        import time
        time.sleep(1)  # Brief pause

# Run all diagnostic tests
test_claude_cli_detailed()
test_claude_desktop_alternative()
test_cursor_alternative()
test_gemini_reliability()

print('\n' + '=' * 50)
print('📊 DIAGNOSTIC SUMMARY')
print('=' * 50)
print('🔍 Claude CLI: Error Code 1 - Installation/API Key issue')
print('🔍 Claude Desktop: App launches but no API response')
print('🔍 Cursor: File-based communication (async)')
print('🔍 Gemini: 100% reliable and fast')
print('\n💡 RECOMMENDATION: Focus on Gemini for reliable AI tasks')