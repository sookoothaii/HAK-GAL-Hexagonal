"""
TIMEOUT FIX für HAK-GAL Backend
Erhöht die Timeouts für alle LLM Provider
"""

import os

# Setze längere Timeouts als Umgebungsvariablen
os.environ["CLAUDE_TIMEOUT"] = "60"      # 60 Sekunden statt 30
os.environ["DEEPSEEK_TIMEOUT"] = "60"    # 60 Sekunden statt 15
os.environ["GEMINI_TIMEOUT"] = "45"      # 45 Sekunden statt 20
os.environ["GROQ_TIMEOUT"] = "45"        # 45 Sekunden statt 25
os.environ["ANTHROPIC_TIMEOUT"] = "60"   # Alternative für Claude

# SSL Einstellungen
os.environ["REQUESTS_CA_BUNDLE"] = ""    # Deaktiviert SSL-Verifikation temporär
os.environ["SSL_VERIFY"] = "false"       # Für Debugging

print("Timeout-Einstellungen gesetzt:")
print(f"  Claude:   {os.environ['CLAUDE_TIMEOUT']}s")
print(f"  DeepSeek: {os.environ['DEEPSEEK_TIMEOUT']}s")
print(f"  Gemini:   {os.environ['GEMINI_TIMEOUT']}s")
print(f"  Groq:     {os.environ['GROQ_TIMEOUT']}s")
