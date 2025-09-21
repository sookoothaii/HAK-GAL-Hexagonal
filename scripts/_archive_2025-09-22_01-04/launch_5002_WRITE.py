import os
import sys
from pathlib import Path

def main() -> None:
    root = Path(__file__).resolve().parents[1]

    # UTF-8 I/O
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONUTF8', '1')
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
    except Exception:
        pass

    # Pfade
    sys.path.insert(0, str(root / 'src_hexagonal'))

    # Mojo optional aktiv lassen (für 5002)
    os.environ.setdefault('MOJO_ENABLED', 'true')
    os.environ.setdefault('MOJO_VALIDATE_ENABLED', 'true')
    os.environ.setdefault('MOJO_DUPES_ENABLED', 'false')

    # WRITE-Modus für 5002
    os.environ['HAKGAL_SQLITE_READONLY'] = 'false'
    os.environ['HAKGAL_SQLITE_DB_PATH'] = 'D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db'
    os.environ['HAKGAL_PORT'] = '5002'
    # Trainiertes HRM-Modell für alle Starts explizit setzen
    os.environ.setdefault('HRM_MODEL_PATH', 'D:/MCP Mods/HAK_GAL_HEXAGONAL/models/hrm_model_v2.pth')

    # Write-Guards (HTTP/MCP) – optional aktivieren
    os.environ.setdefault('HAKGAL_WRITE_ENABLED', 'true')
    # Falls ein Write-Token geprüft wird, hier setzen (optional)
    # os.environ.setdefault('HAKGAL_WRITE_TOKEN', 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d')

    print("🎯 PORT 5002 WRITE MODE:")
    print("  - DB Path:", os.environ['HAKGAL_SQLITE_DB_PATH'])
    print("  - Read-only:", os.environ['HAKGAL_SQLITE_READONLY'])
    print("  - Mojo:", os.environ.get('MOJO_ENABLED'))

    # KEEP GEMINI - Fixed to use both providers
    # Gemini will be tried first (7s), DeepSeek as fallback (30s)
    if 'GEMINI_API_KEY' not in os.environ:
        os.environ['GEMINI_API_KEY'] = 'AIzaSyBTLyMNGxQ5TlIvfm2bWYqImrZ1PBVthFk'
        print("  - Added GEMINI_API_KEY for fast responses")
    else:
        print("  - Keeping existing GEMINI_API_KEY")    
    # App starten - use the CLEAN version with fixes
    import hexagonal_api_enhanced_clean as m  # noqa: WPS433
    api = m.create_app(use_legacy=False, enable_all=True)
    # IMPORTANT: No debug, no reloader for stable WebSocket
    api.run(host='127.0.0.1', port=5002, debug=False)

if __name__ == '__main__':
    main()
