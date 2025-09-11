import os

file_path = "test-mcp-claude.py"
full_file_path = os.path.join(os.path.dirname(__file__), file_path)

try:
    with open(full_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace all occurrences of \" with "
    corrected_content = content.replace('\\"', '"') # Corrected line

    with open(full_file_path, 'w', encoding='utf-8') as f:
        f.write(corrected_content)

    print(f"Successfully fixed escaped quotes in {file_path}")
except FileNotFoundError:
    print(f"Error: File not found at {full_file_path}")
except Exception as e:
    print(f"An error occurred: {e}")