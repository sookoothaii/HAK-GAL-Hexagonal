import os
import glob

def fix_imports():
    count = 0
    for filepath in glob.glob("src/**/*.tsx", recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'from " @/' in content:
                new_content = content.replace('from " @/', 'from "@/')
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Korrigiert: {filepath}")
                count += 1
        except Exception as e:
            print(f"Fehler bei {filepath}: {e}")
    print(f"\nKorrektur abgeschlossen. {count} Dateien wurden geändert.")

if __name__ == "__main__":
    fix_imports()
