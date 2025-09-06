import sys
import os
import json

# Test-Code für execute_code
print("=== TEST EXECUTE_CODE ===")
print(f"Python Version: {sys.version}")
print(f"Working Directory: {os.getcwd()}")

# Test verschiedene Ausgaben
print("Line 1: Simple text")
print("Line 2: Numbers:", 42, 3.14)

# Test JSON output
data = {"status": "success", "value": 123}
print(f"JSON Data: {json.dumps(data)}")

# Test mehrere Zeilen
for i in range(3):
    print(f"Loop iteration {i}")

# Test stderr
import sys
sys.stderr.write("This is an error message\n")

print("\n=== TEST COMPLETE ===")
