#!/usr/bin/env python3
"""
Clipboard Manager für OpenCode Integration
Hilft beim Transfer von Clipboard-Inhalten
"""

import sys
import os

def get_clipboard_windows():
    """Windows Clipboard auslesen"""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except ImportError:
        # Fallback zu PowerShell
        import subprocess
        result = subprocess.run(['powershell', '-Command', 'Get-Clipboard'], 
                              capture_output=True, text=True)
        return result.stdout

def get_clipboard_tkinter():
    """Plattformübergreifend mit tkinter"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Fenster verstecken
        clipboard_content = root.clipboard_get()
        root.destroy()
        return clipboard_content
    except Exception as e:
        return f"Error: {e}"

def save_to_file(content, filename="clipboard_content.txt"):
    """Speichert Clipboard in Datei"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

def main():
    print("=== Clipboard Manager für OpenCode ===\n")
    
    # Versuche Clipboard zu lesen
    content = None
    
    # Methode 1: tkinter (meist verfügbar)
    try:
        content = get_clipboard_tkinter()
        print("✓ Clipboard via tkinter gelesen")
    except:
        pass
    
    # Methode 2: Windows-spezifisch
    if not content and sys.platform == "win32":
        try:
            content = get_clipboard_windows()
            print("✓ Clipboard via Windows API gelesen")
        except:
            pass
    
    if content:
        # In Datei speichern
        filename = save_to_file(content)
        print(f"\n📄 Gespeichert in: {filename}")
        print(f"📏 Länge: {len(content)} Zeichen")
        print("\n--- INHALT PREVIEW (erste 200 Zeichen) ---")
        print(content[:200])
        if len(content) > 200:
            print("...")
        print("\n✅ Sie können die Datei jetzt in OpenCode öffnen!")
        
        # Optional: Direkt in OpenCode öffnen
        if input("\nSoll die Datei in OpenCode geöffnet werden? (j/n): ").lower() == 'j':
            os.system(f'opencode "{filename}"')
    else:
        print("❌ Konnte Clipboard nicht lesen.")
        print("\nAlternative: Nutzen Sie Strg+V direkt in OpenCode")

if __name__ == "__main__":
    main()
