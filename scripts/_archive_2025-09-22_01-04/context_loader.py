import os

def get_combined_context(target_llm: str, base_path: str = ".") -> str:
    """
    Loads and combines context from the SSoT and a target-specific markdown file.
    """
    ssot_path = os.path.join(base_path, "ssot.md")
    specific_path = os.path.join(base_path, f"{target_llm}.md")

    context_parts = []

    # Always load the Single Source of Truth
    if os.path.exists(ssot_path):
        try:
            with open(ssot_path, 'r', encoding='utf-8') as f:
                context_parts.append(f"--- START GLOBAL CONTEXT ---\n{f.read()}\n--- END GLOBAL CONTEXT ---")
        except Exception:
            pass # Ignore if file is not readable

    # Load the specific context if it exists
    if os.path.exists(specific_path):
        try:
            with open(specific_path, 'r', encoding='utf-8') as f:
                context_parts.append(f"--- START SPECIFIC CONTEXT ({target_llm}) ---\n{f.read()}\n--- END SPECIFIC CONTEXT ---")
        except Exception:
            pass # Ignore if file is not readable

    if not context_parts:
        return ""

    return "\n\n".join(context_parts) + "\n\n---\n\n"

if __name__ == '__main__':
    # Example usage
    print("--- Testing for 'gemini' ---")
    gemini_context = get_combined_context('gemini', base_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL')
    print(gemini_context)

    print("\n--- Testing for 'claude' (specific file doesn't exist) ---")
    claude_context = get_combined_context('claude', base_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL')
    print(claude_context)
